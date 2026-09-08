import logging
import sys
from typing import Any, Dict


class ContextFormatter(logging.Formatter):
    """Clean standard formatter with structured timestamps and severity levels."""
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        record_dict: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            record_dict["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            record_dict["user_id"] = record.user_id

        # Format as human-readable string with contextual metadata
        context_parts = []
        if hasattr(record, "request_id"):
            context_parts.append(f"[req:{record.request_id}]")
        if hasattr(record, "user_id"):
            context_parts.append(f"[user:{record.user_id}]")
        
        ctx = " ".join(context_parts)
        if ctx:
            ctx = f" {ctx}"

        return f"[{timestamp}] [{record.levelname:<5}] [{record.name}]{ctx} {record.getMessage()}"


def setup_logging(level: str = "INFO") -> None:
    """Setup root logging with clean formatting."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(ContextFormatter())
    root_logger.addHandler(handler)

    # Quiet overly noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger("nexus")
