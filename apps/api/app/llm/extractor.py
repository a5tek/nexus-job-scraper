from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.models.usage_event import UsageEvent
from app.llm.base import LLMProvider
from app.llm.cache import ExtractionCacheService, compute_extraction_cache_key
from app.llm.cleaner import extract_and_parse_json
from app.llm.gemini import gemini_client
from app.llm.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    build_extraction_prompt,
    build_repair_prompt,
)
from app.llm.schemas import ExtractedListing


class StructuredExtractor:
    """
    High-level extractor orchestrating:
    1. Content-addressed cache lookup
    2. Prompt injection defense
    3. Structured JSON generation
    4. Pydantic validation
    5. Single-retry repair on malformed output
    6. Usage event logging
    """
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or gemini_client

    async def extract(
        self,
        db: AsyncSession,
        raw_content: str,
        raw_content_hash: str,
        raw_title: Optional[str] = None,
        source_url: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[Optional[ExtractedListing], bool]:
        """
        Extracts structured listing details.
        Returns: (extracted_listing, cache_hit)
        """
        cache_key = compute_extraction_cache_key(raw_content_hash)

        # 1. Check Cache
        cached = await ExtractionCacheService.get(db, cache_key)
        if cached:
            logger.info(f"Extraction cache HIT for key {cache_key[:12]}")
            return cached, True

        logger.info(f"Extraction cache MISS for key {cache_key[:12]}. Invoking LLM...")

        # 2. Build extraction prompt
        prompt = build_extraction_prompt(
            raw_content=raw_content,
            raw_title=raw_title,
            source_url=source_url,
        )

        # 3. Call LLM
        json_data, in_tokens, out_tokens = await self.provider.generate_json(
            prompt=prompt,
            system_instruction=EXTRACTION_SYSTEM_PROMPT,
        )

        extracted: Optional[ExtractedListing] = None
        validation_error_str = ""

        if json_data:
            try:
                extracted = ExtractedListing.model_validate(json_data)
            except Exception as exc:
                validation_error_str = str(exc)
                logger.warning(f"Initial JSON validation failed: {exc}. Attempting repair...")

        # 4. Single repair retry if validation failed
        if not extracted and validation_error_str:
            repair_prompt = build_repair_prompt(
                raw_content=raw_content,
                invalid_json_text=str(json_data or ""),
                error_message=validation_error_str,
            )
            repaired_json, r_in, r_out = await self.provider.generate_json(
                prompt=repair_prompt,
                system_instruction=EXTRACTION_SYSTEM_PROMPT,
            )
            in_tokens += r_in
            out_tokens += r_out

            if repaired_json:
                try:
                    extracted = ExtractedListing.model_validate(repaired_json)
                    logger.info("Repair attempt SUCCEEDED.")
                except Exception as exc2:
                    logger.error(f"Repair attempt failed: {exc2}")

        # 5. Log usage event
        try:
            cost_inr = round(((in_tokens * 0.00000015) + (out_tokens * 0.00000060)) * 83.5, 4)
            event = UsageEvent(
                user_id=user_id,
                feature="listing_extraction",
                provider="gemini",
                model=settings.GEMINI_MODEL,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                estimated_cost=cost_inr,
                currency="INR",
            )
            db.add(event)
            await db.commit()
        except Exception as exc:
            logger.warning(f"Failed to log usage event: {exc}")

        # 6. If valid, persist to ExtractionCache
        if extracted:
            await ExtractionCacheService.set(
                db=db,
                cache_key=cache_key,
                raw_content_hash=raw_content_hash,
                payload=extracted.model_dump(mode="json"),
            )
            return extracted, False

        return None, False


structured_extractor = StructuredExtractor()
