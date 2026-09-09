import json
import re
from typing import Any, Dict, Optional


def extract_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts and parses a JSON object from raw LLM output.
    Handles markdown fences, leading/trailing conversational text, and whitespace.
    """
    if not text:
        return None

    cleaned = text.strip()

    # 1. Direct parse attempt
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # 2. Extract content from ```json ... ``` or ``` ... ``` code fence
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    fence_match = re.search(fence_pattern, cleaned, re.IGNORECASE)
    if fence_match:
        fenced_text = fence_match.group(1).strip()
        try:
            data = json.loads(fenced_text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    # 3. Find outermost curly braces { ... }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate_json = cleaned[first_brace : last_brace + 1].strip()
        try:
            data = json.loads(candidate_json)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    return None
