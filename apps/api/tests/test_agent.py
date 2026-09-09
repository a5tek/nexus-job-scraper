import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import AgentOrchestrator
from app.agent.tools.definitions import (
    tool_search_listings,
    tool_get_saved_listings,
    tool_get_listings_by_deadline,
    tool_get_skill_frequency,
    tool_get_top_matches,
)
from app.models.listing import Listing
from app.models.match import Match
from app.models.raw_listing import RawListing
from app.models.saved_listing import SavedListing
from app.models.user import User


@pytest.mark.asyncio
async def test_agent_tools_and_scoping(db_session: AsyncSession):
    # Setup two users
    user_a = User(
        email="agent_a@example.com",
        password_hash="pw",
        name="Agent User A",
        is_active=True,
    )
    user_b = User(
        email="agent_b@example.com",
        password_hash="pw",
        name="Agent User B",
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    # Create raw listing & listing with deadline and skills
    today = date.today()
    raw = RawListing(
        source_url="https://workatastartup.com/jobs/agent-test-1",
        canonical_url="https://workatastartup.com/jobs/agent-test-1",
        raw_title="Senior AI Engineer",
        raw_content="Looking for Senior AI Engineer with Python and PyTorch",
        dedupe_key="yc:agent-test-1",
        content_hash="hash-agent-test-1",
        extraction_status="extracted",
    )
    db_session.add(raw)
    await db_session.flush()

    listing = Listing(
        raw_listing_id=raw.id,
        title="Senior AI Engineer",
        company="Nexus AI",
        location="Remote",
        remote_ok=True,
        required_skills=["Python", "PyTorch", "FastAPI"],
        deadline=today + timedelta(days=5),
        extractor_version="1.0",
    )
    db_session.add(listing)
    await db_session.flush()

    # Create resume for user A
    from app.models.resume import Resume
    resume_a = Resume(
        user_id=user_a.id,
        file_url="/dummy/resume.pdf",
        file_name="resume.pdf",
        extracted_text="Senior Python and PyTorch engineer",
        is_active=True,
    )
    db_session.add(resume_a)
    await db_session.flush()

    # User A saves the listing, User B does not
    saved_a = SavedListing(user_id=user_a.id, listing_id=listing.id)
    match_a = Match(
        user_id=user_a.id,
        resume_id=resume_a.id,
        listing_id=listing.id,
        similarity=0.92,
        display_score=92,
        justification="Strong match on Python and AI systems experience.",
        match_version="1.0",
    )
    db_session.add_all([saved_a, match_a])
    await db_session.commit()

    # 1. Test tool_get_saved_listings with user scoping
    res_a = await tool_get_saved_listings(db_session, user_id=user_a.id)
    assert res_a["count"] == 1
    assert res_a["saved_listings"][0]["title"] == "Senior AI Engineer"
    assert res_a["saved_listings"][0]["match_score"] == 92

    res_b = await tool_get_saved_listings(db_session, user_id=user_b.id)
    assert res_b["count"] == 0
    assert len(res_b["saved_listings"]) == 0

    # 2. Test tool_get_listings_by_deadline
    res_deadline_all = await tool_get_listings_by_deadline(
        db_session, user_id=user_a.id, days_ahead=10, saved_only=False
    )
    assert res_deadline_all["count"] >= 1
    assert res_deadline_all["listings"][0]["company"] == "Nexus AI"

    res_deadline_saved_b = await tool_get_listings_by_deadline(
        db_session, user_id=user_b.id, days_ahead=10, saved_only=True
    )
    assert res_deadline_saved_b["count"] == 0

    # 3. Test tool_get_skill_frequency
    skills_a = await tool_get_skill_frequency(
        db_session, user_id=user_a.id, saved_only=True
    )
    skill_names = [s["skill"] for s in skills_a["top_skills"]]
    assert "Python" in skill_names
    assert "PyTorch" in skill_names

    # 4. Test tool_get_top_matches
    top_matches = await tool_get_top_matches(
        db_session, user_id=user_a.id, min_score=80
    )
    assert top_matches["count"] == 1
    assert top_matches["matches"][0]["match_score"] == 92

    # 5. Test tool_search_listings
    search_res = await tool_search_listings(
        db_session, user_id=user_a.id, query="Python", limit=5
    )
    assert "listings" in search_res


@pytest.mark.asyncio
async def test_agent_orchestrator_routing(db_session: AsyncSession):
    user = User(
        email="orchestrator_user@example.com",
        password_hash="pw",
        name="Orchestrator User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Deadline query routing
    res_deadline = await AgentOrchestrator.process_chat(
        db=db_session,
        user_id=user.id,
        message="What are the upcoming deadlines for my applications?",
    )
    assert len(res_deadline.tools_called) == 1
    assert res_deadline.tools_called[0].tool_name == "get_listings_by_deadline"
    assert len(res_deadline.suggested_follow_ups) > 0

    # Saved listings query routing
    res_saved = await AgentOrchestrator.process_chat(
        db=db_session,
        user_id=user.id,
        message="Show me my saved shortlist",
    )
    assert len(res_saved.tools_called) == 1
    assert res_saved.tools_called[0].tool_name == "get_saved_listings"

    # Skills query routing
    res_skills = await AgentOrchestrator.process_chat(
        db=db_session,
        user_id=user.id,
        message="What common technologies and skills are in demand?",
    )
    assert len(res_skills.tools_called) == 1
    assert res_skills.tools_called[0].tool_name == "get_skill_frequency"

    # Top matches query routing
    res_matches = await AgentOrchestrator.process_chat(
        db=db_session,
        user_id=user.id,
        message="What are my best fit roles and top matches?",
    )
    assert len(res_matches.tools_called) == 1
    assert res_matches.tools_called[0].tool_name == "get_top_matches"


@pytest.mark.asyncio
async def test_agent_api_endpoint(client: AsyncClient):
    # Register via client
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "agent_api_user@example.com",
            "password": "Password123!",
            "name": "Agent API Tester",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]

    # Unauthenticated request rejected
    res_unauth = await client.post("/api/v1/agent/chat", json={"message": "Hello"})
    assert res_unauth.status_code == 401

    # Authenticated chat
    res = await client.post(
        "/api/v1/agent/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show my top match opportunities"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "tools_called" in data
    assert "suggested_follow_ups" in data
