from datetime import date, datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class ExtractedListing(BaseModel):
    """
    Normalized logical schema for a scraped job listing according to PRD.md Section 6.4.
    """
    title: Optional[str] = Field(default=None, description="Job title, e.g. 'Software Engineer Intern'")
    company: Optional[str] = Field(default=None, description="Company or organization name")
    location: Optional[str] = Field(default=None, description="Physical location or city/state/country")
    remote_ok: Optional[bool] = Field(default=None, description="Whether the role supports remote work")
    stipend: Optional[str] = Field(default=None, description="Compensation, salary, or stipend string")
    required_skills: List[str] = Field(default_factory=list, description="List of technical skills or tools")
    experience_level: Optional[str] = Field(
        default=None,
        description="Experience level: e.g. 'Intern', 'Entry Level', 'Junior', 'Mid', 'Senior'",
    )
    deadline: Optional[date] = Field(default=None, description="Application deadline as ISO date")

    @field_validator("title", "company", "location", "stipend", "experience_level", mode="before")
    @classmethod
    def clean_strings(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        text = str(v).strip()
        if not text or text.lower() in ("null", "none", "n/a", "unknown", "undefined"):
            return None
        return text

    @field_validator("remote_ok", mode="before")
    @classmethod
    def parse_remote(cls, v: Any) -> Optional[bool]:
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        text = str(v).strip().lower()
        if text in ("true", "1", "yes", "remote", "hybrid"):
            return True
        elif text in ("false", "0", "no", "onsite", "in-person", "in person"):
            return False
        return None

    @field_validator("required_skills", mode="before")
    @classmethod
    def clean_skills(cls, v: Any) -> List[str]:
        if not v:
            return []
        if isinstance(v, str):
            # Split comma-separated skills if model returned a string
            v = [s.strip() for s in v.split(",") if s.strip()]
        
        cleaned = []
        seen = set()
        for item in v:
            if not item:
                continue
            skill = str(item).strip()
            # Remove bullets or extra quotes
            skill = skill.lstrip("•-* ").strip("\"' ")
            if skill and skill.lower() not in seen and len(skill) <= 50:
                seen.add(skill.lower())
                cleaned.append(skill)
        return cleaned

    @field_validator("deadline", mode="before")
    @classmethod
    def parse_deadline(cls, v: Any) -> Optional[date]:
        if not v:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, datetime):
            return v.date()
        
        text = str(v).strip()
        if text.lower() in ("null", "none", "n/a", "rolling", "asap", "open", "ongoing"):
            return None

        # Try ISO format
        try:
            return date.fromisoformat(text.split("T")[0])
        except ValueError:
            pass

        # Try standard date formats
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue

        # If date could not be parsed safely, avoid crashing or hallucinating
        return None
