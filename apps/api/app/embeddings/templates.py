from typing import List, Optional
import re


def build_listing_embedding_text(
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    remote_ok: Optional[bool] = None,
    experience_level: Optional[str] = None,
    required_skills: Optional[List[str]] = None,
    description_snippet: Optional[str] = None,
) -> str:
    """
    Deterministic template builder for listing semantic embeddings.
    Conforms to PRD.md Section 6.5 & TECH_STACK.md Section 13.3.
    """
    remote_str = "Remote" if remote_ok is True else ("Onsite" if remote_ok is False else "Not specified")
    skills_str = ", ".join(required_skills) if required_skills else "General software engineering"
    
    clean_desc = ""
    if description_snippet:
        # Collapse whitespace and truncate snippet to avoid context bloat
        clean_desc = re.sub(r"\s+", " ", description_snippet).strip()[:400]

    lines = [
        f"Title: {title or 'Software Engineer'}",
        f"Company: {company or 'Technology Company'}",
        f"Experience: {experience_level or 'Intern / Early Career'}",
        f"Location: {location or 'Flexible'}",
        f"Remote Status: {remote_str}",
        f"Required Skills: {skills_str}",
    ]
    if clean_desc:
        lines.append(f"Description: {clean_desc}")

    return "\n".join(lines)


def build_resume_embedding_text(extracted_text: str) -> str:
    """
    Deterministic template builder for candidate resume embeddings.
    Normalizes whitespace and extracts the dense semantic profile.
    """
    if not extracted_text:
        return "Software engineering candidate profile."

    cleaned = re.sub(r"\s+", " ", extracted_text).strip()
    return f"Candidate Technical Profile:\n{cleaned[:2500]}"
