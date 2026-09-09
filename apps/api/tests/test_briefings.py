import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.briefings.script_generator import ScriptGenerator
from app.models.listing import Listing
from app.models.match import Match
from app.models.raw_listing import RawListing
from app.models.resume import Resume
from app.models.user import User
from app.services.briefing_service import BriefingService


def test_script_generator_output():
    # Empty matches fallback
    empty_script = ScriptGenerator.generate_script(user_name="Alex Candidate", top_matches=[])
    assert "Alex" in empty_script
    assert "Nexus Executive Briefing" in empty_script

    # With 3 matches
    matches = [
        {
            "title": "Lead AI Architect",
            "company": "Anthropic",
            "display_score": 95,
            "justification": "Extensive experience in large language model architecture.",
            "skills": ["Python", "PyTorch", "Transformers"],
            "deadline": "2026-10-15",
        },
        {
            "title": "Founding Engineer",
            "company": "Nexus Labs",
            "display_score": 91,
            "justification": "Full-stack systems experience with autonomous agents.",
            "skills": ["FastAPI", "React", "Docker"],
            "deadline": "Not stated",
        },
    ]
    script = ScriptGenerator.generate_script(user_name="Jordan Bell", top_matches=matches)
    assert "Jordan" in script
    assert "Lead AI Architect" in script
    assert "Anthropic" in script
    assert "95%" in script
    assert "Founding Engineer" in script
    assert "Nexus Labs" in script


@pytest.mark.asyncio
async def test_briefing_service_and_isolation(db_session: AsyncSession):
    # Create two users
    user_a = User(email="brief_a@example.com", password_hash="pw", name="Briefing User A", is_active=True)
    user_b = User(email="brief_b@example.com", password_hash="pw", name="Briefing User B", is_active=True)
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    # Create raw listing and listing
    raw = RawListing(
        source_url="https://workatastartup.com/jobs/brief-1",
        canonical_url="https://workatastartup.com/jobs/brief-1",
        raw_title="Principal AI Scientist",
        raw_content="Looking for Principal AI Scientist",
        dedupe_key="yc:brief-1",
        content_hash="hash-brief-1",
        extraction_status="extracted",
    )
    db_session.add(raw)
    await db_session.flush()

    listing = Listing(
        raw_listing_id=raw.id,
        title="Principal AI Scientist",
        company="Cognitive Corp",
        location="Remote",
        remote_ok=True,
        required_skills=["Python", "Deep Learning"],
        deadline=date.today() + timedelta(days=7),
        extractor_version="1.0",
    )
    db_session.add(listing)
    await db_session.flush()

    # Create resume and match for User A
    resume_a = Resume(
        user_id=user_a.id,
        file_url="/resumes/brief_a.pdf",
        file_name="brief_a.pdf",
        extracted_text="Experienced AI scientist and researcher.",
        is_active=True,
    )
    db_session.add(resume_a)
    await db_session.flush()

    match_a = Match(
        user_id=user_a.id,
        resume_id=resume_a.id,
        listing_id=listing.id,
        similarity=0.96,
        display_score=96,
        justification="World class match in deep learning and research.",
        match_version="1.0",
    )
    db_session.add(match_a)
    await db_session.commit()

    # Generate briefing for user A
    briefing_a = await BriefingService.create_briefing(
        db=db_session,
        user_id=user_a.id,
        user_name=user_a.name,
    )
    assert briefing_a.status == "done"
    assert briefing_a.media_url is not None
    assert "Cognitive Corp" in (briefing_a.script or "")

    # Retrieve briefing for user A
    res_a = await BriefingService.get_briefing(db=db_session, briefing_id=briefing_a.id, user_id=user_a.id)
    assert res_a is not None
    assert len(res_a.listings) == 1
    assert res_a.listings[0].title == "Principal AI Scientist"
    assert res_a.listings[0].match_score == 96

    # User B should NOT be able to access User A's briefing
    res_b = await BriefingService.get_briefing(db=db_session, briefing_id=briefing_a.id, user_id=user_b.id)
    assert res_b is None


@pytest.mark.asyncio
async def test_briefings_api_endpoints(client: AsyncClient):
    # 1. Register candidate user
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "briefing_candidate@example.com",
            "password": "Password123!",
            "name": "Briefing Candidate",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Unauthenticated check
    unauth = await client.get("/api/v1/briefings")
    assert unauth.status_code == 401

    # 3. Create a briefing via API
    create_res = await client.post("/api/v1/briefings", headers=headers)
    assert create_res.status_code == 201
    b_data = create_res.json()
    assert "id" in b_data
    assert b_data["status"] == "done"
    assert b_data["media_url"] is not None
    briefing_id = b_data["id"]

    # 4. List briefings
    list_res = await client.get("/api/v1/briefings", headers=headers)
    assert list_res.status_code == 200
    briefings_list = list_res.json()
    assert len(briefings_list) >= 1
    assert briefings_list[0]["id"] == briefing_id

    # 5. Get briefing by id
    get_res = await client.get(f"/api/v1/briefings/{briefing_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == briefing_id

    # 6. Retry briefing
    retry_res = await client.post(f"/api/v1/briefings/{briefing_id}/retry", headers=headers)
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "done"

    # 7. Non-existent briefing returns 404
    bad_res = await client.get("/api/v1/briefings/non-existent-id", headers=headers)
    assert bad_res.status_code == 404
