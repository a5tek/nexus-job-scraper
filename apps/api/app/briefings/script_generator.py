from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger


class ScriptGenerator:
    """
    Generates a 60-90 second personalized audio/video briefing script
    synthesizing the user's top 3 matched opportunities.
    """

    @staticmethod
    def generate_script(
        user_name: str,
        top_matches: List[Dict[str, Any]],
    ) -> str:
        """
        Creates a structured, engaging, editorial script.
        """
        first_name = user_name.split()[0] if user_name else "Candidate"
        
        if not top_matches:
            return (
                f"Welcome to your Nexus Executive Briefing, {first_name}. "
                f"Our career intelligence engine is currently indexing new roles matching your profile. "
                f"Be sure to keep your active resume updated so we can highlight your highest fit opportunities next week."
            )

        script_sections = []
        # Intro
        script_sections.append(
            f"Hello {first_name}, welcome to your weekly Nexus Career Briefing. "
            f"Our autonomous matching intelligence analyzed new listings against your resume, and today we have spotlighted your top {len(top_matches)} opportunities."
        )

        # Body items
        for i, match in enumerate(top_matches, start=1):
            title = match.get("title", "Software Engineer")
            company = match.get("company", "leading tech firm")
            score = match.get("match_score") or match.get("display_score")
            score_text = f" boasting a {score}% semantic alignment," if score else ""
            justification = match.get("justification", "Aligns strongly with your core technical competencies.")
            skills = match.get("skills", [])
            skills_text = f" Key technologies in focus are {', '.join(skills[:3])}." if skills else ""
            deadline = match.get("deadline")
            deadline_text = f" Note: applications close on {deadline}." if deadline and deadline != "Not stated" else ""

            ordinal = ["first", "second", "third"][i - 1] if i <= 3 else f"number {i}"
            script_sections.append(
                f"Your {ordinal} standout role is {title} at {company},{score_text} {justification}{skills_text}{deadline_text}"
            )

        # Outro
        script_sections.append(
            f"You can review these roles in depth and explore full requirement breakdowns on your Discover feed. "
            f"Bookmark your favorites to receive deadline alerts. That concludes today's Nexus Briefing. Good luck with your applications!"
        )

        return "\n\n".join(script_sections)
