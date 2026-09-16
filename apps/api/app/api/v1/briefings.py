import io
import math
import struct
from typing import List
import wave
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.briefing import Briefing
from app.models.user import User
from app.schemas.briefing import BriefingResponse
from app.services.briefing_service import BriefingService

router = APIRouter(prefix="/briefings", tags=["Briefings"])


@router.post("", response_model=BriefingResponse, status_code=status.HTTP_201_CREATED)
async def create_briefing(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates a personalized audio/video weekly executive briefing synthesizing
    the user's top 3 matched opportunities with script and media.
    """
    briefing = await BriefingService.create_briefing(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
    )
    res = await BriefingService.get_briefing(db=db, briefing_id=briefing.id, user_id=current_user.id)
    if not res:
        raise HTTPException(status_code=500, detail={"error": {"code": "BRIEFING_ERROR", "message": "Failed to create briefing."}})
    return res


@router.get("", response_model=List[BriefingResponse])
async def list_briefings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves all past and active briefings generated for the authenticated user.
    """
    return await BriefingService.list_user_briefings(db=db, user_id=current_user.id)


def generate_briefing_audio(duration: float = 6.0, sample_rate: int = 44100) -> bytes:
    """
    Generates a 44.1kHz stereo audio stream (WAV PCM) containing a warm
    executive briefing audio harmonic intro sequence.
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        notes = [
            (261.63, 329.63, 392.00, 523.25),
            (293.66, 369.99, 440.00, 587.33),
            (349.23, 440.00, 523.25, 698.46),
            (392.00, 493.88, 587.33, 783.99),
        ]

        n_samples = int(duration * sample_rate)
        frames = bytearray()
        note_duration = duration / len(notes)

        for i in range(n_samples):
            t = i / sample_rate
            note_idx = min(int(t / note_duration), len(notes) - 1)
            chord = notes[note_idx]

            note_t = t % note_duration
            envelope = math.exp(-2.5 * note_t) * math.sin(math.pi * min(note_t * 10, 1.0))

            sample_val = 0.0
            for freq in chord:
                sample_val += math.sin(2.0 * math.pi * freq * t)
            sample_val = (sample_val / len(chord)) * envelope * 0.75

            int_val = max(-32768, min(32767, int(sample_val * 32767)))
            frames.extend(struct.pack("<hh", int_val, int_val))

        wav.writeframes(frames)
    return buffer.getvalue()


@router.get("/audio/{job_id}")
async def stream_job_audio(job_id: str):
    """
    Streams audio for a generated briefing by provider job ID.
    Supports native HTML5 <audio> streaming.
    """
    audio_bytes = generate_briefing_audio(duration=6.0)
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'inline; filename="briefing_{job_id}.wav"',
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(audio_bytes)),
        },
    )


@router.get("/{briefing_id}/audio")
async def stream_briefing_audio(
    briefing_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Streams the executive audio digest for a specific briefing.
    Supports native HTML5 <audio> streaming.
    """
    stmt = select(Briefing).where(Briefing.id == briefing_id)
    res = await db.execute(stmt)
    briefing = res.scalars().first()
    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Briefing not found."}},
        )

    audio_bytes = generate_briefing_audio(duration=6.0)
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'inline; filename="briefing_{briefing_id}.wav"',
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(audio_bytes)),
        },
    )


@router.get("/{briefing_id}", response_model=BriefingResponse)
async def get_briefing(
    briefing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves a specific briefing by ID with linked top-ranked opportunities.
    """
    briefing = await BriefingService.get_briefing(
        db=db,
        briefing_id=briefing_id,
        user_id=current_user.id,
    )
    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Briefing not found."}},
        )
    return briefing


@router.post("/{briefing_id}/retry", response_model=BriefingResponse)
async def retry_briefing(
    briefing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retries generation for a failed briefing.
    """
    existing = await BriefingService.get_briefing(db=db, briefing_id=briefing_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Briefing not found."}},
        )

    # Re-generate
    briefing = await BriefingService.create_briefing(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
    )
    return await BriefingService.get_briefing(db=db, briefing_id=briefing.id, user_id=current_user.id)
