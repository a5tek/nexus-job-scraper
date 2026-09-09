from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agent.tools.definitions import AGENT_TOOLS
from app.core.config import settings
from app.core.logging import logger
from app.schemas.agent import AgentChatResponse, ChatMessage, ToolCallRecord


class AgentOrchestrator:
    """
    Coordinates tool-calling AI agent interactions for the user's workspace.
    Enforces server-side user scoping and prompt injection defense.
    """
    @staticmethod
    async def process_chat(
        db: AsyncSession,
        user_id: str,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> AgentChatResponse:
        lower_msg = message.lower()
        tools_called: List[ToolCallRecord] = []

        # Intent detection & tool selection
        tool_to_run = None
        tool_args: Dict[str, Any] = {}

        if any(w in lower_msg for w in ("deadline", "closing", "due", "close", "date")):
            tool_to_run = "get_listings_by_deadline"
            saved_only = "saved" in lower_msg or "shortlist" in lower_msg
            tool_args = {"days_ahead": 30, "saved_only": saved_only}

        elif any(w in lower_msg for w in ("saved", "shortlist", "shortlisted", "my roles", "my jobs")):
            tool_to_run = "get_saved_listings"
            tool_args = {"limit": 10}

        elif any(w in lower_msg for w in ("skills", "common tech", "stack", "frequency", "technologies")):
            tool_to_run = "get_skill_frequency"
            tool_args = {"saved_only": "saved" in lower_msg, "top_n": 8}

        elif any(w in lower_msg for w in ("best fit", "top match", "highest match", "strongest", "matches")):
            tool_to_run = "get_top_matches"
            tool_args = {"limit": 5, "min_score": 50}

        else:
            tool_to_run = "search_listings"
            tool_args = {"query": message, "limit": 5}

        # Execute chosen tool with server-injected user_id
        tool_meta = AGENT_TOOLS[tool_to_run]
        func = tool_meta["func"]
        
        try:
            result = await func(db=db, user_id=user_id, **tool_args)
            summary = f"Retrieved {result.get('count', len(result.get('top_skills', [])))} items from database."
            tools_called.append(
                ToolCallRecord(
                    tool_name=tool_to_run,
                    arguments=tool_args,
                    result_summary=summary,
                )
            )
        except Exception as exc:
            logger.error(f"Error executing agent tool {tool_to_run}: {exc}")
            result = {"error": str(exc)}
            tools_called.append(
                ToolCallRecord(
                    tool_name=tool_to_run,
                    arguments=tool_args,
                    result_summary=f"Execution error: {exc}",
                )
            )

        # Synthesize clear, user-facing editorial answer
        response_text = AgentOrchestrator._synthesize_response(tool_to_run, result, message)

        follow_ups = [
            "Which of my saved roles have upcoming deadlines?",
            "What technical skills appear most often in my matches?",
            "Show my top 3 resume matches.",
        ]

        return AgentChatResponse(
            response=response_text,
            tools_called=tools_called,
            suggested_follow_ups=follow_ups,
        )

    @staticmethod
    def _synthesize_response(tool_name: str, result: Dict[str, Any], query: str) -> str:
        if tool_name == "get_listings_by_deadline":
            listings = result.get("listings", [])
            if not listings:
                scope = "your saved shortlist" if result.get("saved_only") else "available roles"
                return f"I checked your database, and there are currently no roles in {scope} closing in the next {result.get('days_ahead', 14)} days."

            lines = [f"Here are the upcoming deadlines I found for you:"]
            for l in listings[:5]:
                days = l.get("days_remaining", 0)
                time_str = f"in {days} days" if days > 0 else "today!"
                lines.append(f"• **{l['title']}** at **{l['company']}** — Deadline: {l['deadline']} ({time_str})")
            return "\n".join(lines)

        elif tool_name == "get_saved_listings":
            saved = result.get("saved_listings", [])
            if not saved:
                return "Your shortlist is currently empty. You can save interesting roles from the Discover feed with the bookmark action."

            lines = [f"You currently have {len(saved)} saved opportunities in your shortlist:"]
            for s in saved:
                score_str = f" ({s['match_score']}% Match)" if s.get("match_score") else ""
                lines.append(f"• **{s['title']}** at **{s['company']}**{score_str} — {s['location'] or 'Remote'}")
            return "\n".join(lines)

        elif tool_name == "get_top_matches":
            matches = result.get("matches", [])
            if not matches:
                return "I couldn't find matches above your score threshold yet. Make sure your active resume is uploaded so Nexus can calculate personalized semantic fits."

            lines = [f"Based on your resume semantic profile, here are your top matches:"]
            for m in matches:
                lines.append(f"• **{m['title']}** at **{m['company']}** (**{m['match_score']}% match**)\n  _{m['justification']}_")
            return "\n\n".join(lines)

        elif tool_name == "get_skill_frequency":
            top_skills = result.get("top_skills", [])
            if not top_skills:
                return "No skill frequency metrics available yet. As more matching listings are processed, this data will populate."

            lines = ["Here are the most frequently requested technical skills across your opportunities:"]
            for s in top_skills:
                lines.append(f"• **{s['skill']}**: mentioned in {s['count']} matching roles")
            return "\n".join(lines)

        else:  # search_listings
            listings = result.get("listings", [])
            if not listings:
                return f"I searched the opportunity database for '{query}', but didn't find any close matches. Try broadening your keywords or checking remote filters."

            lines = [f"I found {len(listings)} opportunities relevant to your query:"]
            for l in listings:
                skills = ", ".join(l.get("skills", [])[:4])
                skills_text = f" | Skills: {skills}" if skills else ""
                lines.append(f"• **{l['title']}** at **{l['company']}** ({l['location'] or 'Remote'}){skills_text}")
            return "\n".join(lines)
