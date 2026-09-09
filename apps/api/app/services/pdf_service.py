import hashlib
import io
import re
from typing import Tuple
from fastapi import HTTPException, status
import pymupdf
from app.core.logging import logger


class PDFProcessingError(HTTPException):
    def __init__(self, message: str, code: str = "PDF_PROCESSING_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": code, "message": message}},
        )


class PDFService:
    """
    Extracts text content and metadata from PDF files using PyMuPDF.
    Conforms to PRD.md Section 6.2 & TECH_STACK.md Section 15.1.
    """
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, str]:
        """
        Extracts textual content and computes SHA-256 hash.
        Returns: (extracted_text, content_hash)
        Raises: PDFProcessingError on corrupted file or unextractable text.
        """
        if not pdf_bytes:
            raise PDFProcessingError("Uploaded file is empty.", code="EMPTY_FILE")

        # Basic PDF magic bytes check (%PDF-)
        if not pdf_bytes.startswith(b"%PDF"):
            raise PDFProcessingError("File is not a valid PDF document.", code="INVALID_PDF_FORMAT")

        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            logger.error(f"PyMuPDF failed to open document: {exc}")
            raise PDFProcessingError("Could not read or parse the PDF document.", code="CORRUPTED_PDF")

        text_parts = []
        try:
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_text = page.get_text("text")
                if page_text:
                    text_parts.append(page_text.strip())
        finally:
            doc.close()

        full_text = "\n\n".join(text_parts).strip()

        # Check for usable textual content (detect scanned / raster images)
        clean_check = re.sub(r"\s+", "", full_text)
        if len(clean_check) < 30:
            raise PDFProcessingError(
                "The uploaded PDF does not contain sufficient extractable text. "
                "Please upload a standard text-based PDF rather than a scanned image.",
                code="NO_EXTRACTABLE_TEXT",
            )

        content_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        return full_text, content_hash
