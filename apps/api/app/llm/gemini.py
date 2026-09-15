import asyncio
import re
from typing import Any, Dict, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.llm.base import LLMProvider
from app.llm.cleaner import extract_and_parse_json

try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False


class GeminiProvider(LLMProvider):
    """
    Adapter for Google Gemini API.
    Supports structured JSON mode, token counting, and resilient offline fallback.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self._is_configured = False

        if HAS_GEMINI_SDK and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._is_configured = True
            except Exception as exc:
                logger.warning(f"Failed to configure Gemini SDK: {exc}")

    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], int, int]:
        """
        Executes generation requesting JSON MIME type.
        Falls back to local heuristics if API key is not configured or in offline test mode.
        """
        if self._is_configured and HAS_GEMINI_SDK:
            try:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.1,
                    },
                )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt),
                )
                
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else len(prompt.split())
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else len(response.text.split())
                
                parsed = extract_and_parse_json(response.text)
                return parsed, input_tokens, output_tokens
            except Exception as exc:
                logger.error(f"Gemini API call failed: {exc}. Falling back to offline parser.")

        # Offline / Heuristic extraction fallback
        return self._offline_heuristic_json(prompt), len(prompt.split()), 50

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> Tuple[str, int, int]:
        if self._is_configured and HAS_GEMINI_SDK:
            try:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction,
                    generation_config={"temperature": 0.4},
                )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt),
                )
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else len(prompt.split())
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else len(response.text.split())
                return response.text, input_tokens, output_tokens
            except Exception as exc:
                logger.error(f"Gemini generate_text failed: {exc}. Using fallback text.")

        return "Generated response based on provided context.", len(prompt.split()), 15

    def _offline_heuristic_json(self, prompt: str) -> Dict[str, Any]:
        """
        Deterministic offline heuristic extractor.
        Uses rich domain taxonomy, tag normalization, and text sanitization.
        """
        from app.core.sanitizer import (
            clean_company,
            clean_location,
            clean_title,
            extract_tech_skills,
            sanitize_text,
        )

        # 1. Search for company
        company = None
        comp_match = re.search(r"Company:\s*([^\n\r<]+)", prompt, re.IGNORECASE)
        if comp_match:
            company = clean_company(comp_match.group(1).strip())

        # 2. Search for title
        title = None
        title_match = re.search(r"(?:Title|Role|Raw Title Hint):\s*([^\n\r<]+)", prompt, re.IGNORECASE)
        if title_match:
            title = clean_title(title_match.group(1).strip())
        else:
            # Search prompt lines for role keywords
            for line in prompt.splitlines():
                l_lower = line.lower()
                if any(kw in l_lower for kw in ("engineer", "intern", "developer", "architect", "analyst", "designer")) and len(line) < 80:
                    title = clean_title(line.strip(" -*#:;"))
                    break

        title = title or "Software Engineer"
        company = company or "Technology Startup"

        # 3. Search for location
        location = "Remote"
        loc_match = re.search(r"Location:\s*([^\n\r<]+)", prompt, re.IGNORECASE)
        if loc_match:
            location = clean_location(loc_match.group(1).strip())

        remote_ok = True if (location and "remote" in location.lower()) or "remote" in prompt.lower() else False

        # 4. Extract tags if present
        tags: List[str] = []
        tags_match = re.search(r"Tags:\s*([^\n\r<]+)", prompt, re.IGNORECASE)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(",") if t.strip()]

        # 5. Extract rich technical skills
        found_skills = extract_tech_skills(prompt, tags=tags, title=title)

        # 6. Experience level
        exp = "Mid Level"
        p_lower = prompt.lower()
        t_lower = title.lower()
        if "intern" in t_lower or "intern" in p_lower:
            exp = "Intern"
        elif "lead" in t_lower or "principal" in t_lower or "staff" in t_lower:
            exp = "Lead"
        elif "senior" in t_lower or "senior" in p_lower:
            exp = "Senior"
        elif "junior" in t_lower or "entry level" in t_lower or "associate" in t_lower:
            exp = "Entry Level"

        # 7. Stipend
        stipend = None
        stipend_match = re.search(r"(?:₹|\$|USD|INR)\s*[\d,]+(?:\s*(?:k|/mo|/yr|per month|per year|- (?:₹|\$|USD|INR)?\s*[\d,]+(?:\s*(?:k|/mo|/yr|per month|per year))?))?", prompt, re.IGNORECASE)
        if stipend_match:
            stipend = sanitize_text(stipend_match.group(0).strip())

        # 8. Deadline
        deadline = None
        deadline_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", prompt)
        if deadline_match:
            deadline = deadline_match.group(1)

        return {
            "title": title,
            "company": company,
            "location": location,
            "remote_ok": remote_ok,
            "stipend": stipend,
            "required_skills": found_skills,
            "experience_level": exp,
            "deadline": deadline,
        }


# Default singleton instance
gemini_client = GeminiProvider()
