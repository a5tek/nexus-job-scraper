import abc
import hashlib
from typing import NamedTuple, Optional


class JobSubmissionResult(NamedTuple):
    job_id: str
    status: str  # queued, processing, done, failed


class JobStatusResult(NamedTuple):
    status: str  # queued, processing, done, failed
    media_url: Optional[str] = None
    error: Optional[str] = None


class BaseMediaProvider(abc.ABC):
    """
    Abstract interface for media (audio/video) generation services.
    Supports asynchronous polling or immediate generation patterns.
    """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        pass

    @abc.abstractmethod
    async def submit_job(self, script: str, user_id: str) -> JobSubmissionResult:
        """Submits text script for media rendering."""
        pass

    @abc.abstractmethod
    async def poll_job(self, job_id: str) -> JobStatusResult:
        """Checks generation status of an in-flight job."""
        pass


class MockMediaProvider(BaseMediaProvider):
    """
    High-fidelity mock provider producing synthetic podcast/audio briefings.
    Produces deterministic media URLs and immediate completion for local/dev use.
    """

    @property
    def provider_name(self) -> str:
        return "mock_studio"

    async def submit_job(self, script: str, user_id: str) -> JobSubmissionResult:
        script_hash = hashlib.sha256(script.encode("utf-8")).hexdigest()[:16]
        job_id = f"job_mock_{script_hash}"
        return JobSubmissionResult(job_id=job_id, status="done")

    async def poll_job(self, job_id: str) -> JobStatusResult:
        media_url = f"https://cdn.nexus.internal/briefings/{job_id}.mp3"
        return JobStatusResult(
            status="done",
            media_url=media_url,
            error=None,
        )


def get_media_provider() -> BaseMediaProvider:
    return MockMediaProvider()
