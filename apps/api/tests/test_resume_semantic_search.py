from io import BytesIO
import pytest
import pymupdf
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.embeddings.base import EmbeddingProvider
from app.embeddings.provider import embedding_provider
from app.models.listing import Listing
from app.models.raw_listing import RawListing
from app.models.source import Source
from app.services.matching_service import calculate_display_score
from app.services.pdf_service import PDFProcessingError, PDFService


def create_sample_pdf_bytes(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pdf_extraction_success_and_failures():
    sample_text = (
        "Alex Candidate\n"
        "Software Engineer with 2 years of experience in backend development.\n"
        "Skills: Python, FastAPI, PostgreSQL, Docker, Redis, Kubernetes, Go.\n"
        "Experience: Built distributed event processing architectures."
    )
    pdf_bytes = create_sample_pdf_bytes(sample_text)
    extracted, content_hash = PDFService.extract_text_from_pdf_bytes(pdf_bytes)
    assert "Alex Candidate" in extracted
    assert "FastAPI" in extracted
    assert len(content_hash) == 64

    # Non-PDF failure
    with pytest.raises(PDFProcessingError) as exc_info:
        PDFService.extract_text_from_pdf_bytes(b"Not a PDF file content")
    assert exc_info.value.status_code == 400

    # PDF with insufficient text
    empty_pdf = create_sample_pdf_bytes("Hi")
    with pytest.raises(PDFProcessingError) as exc_info2:
        PDFService.extract_text_from_pdf_bytes(empty_pdf)
    assert exc_info2.value.status_code == 400


def test_embedding_and_cosine_similarity():
    vec_a = embedding_provider.embed_text("FastAPI backend development with Python and PostgreSQL")
    vec_b = embedding_provider.embed_text("Senior Backend Engineer specializing in Python and relational databases")
    vec_c = embedding_provider.embed_text("Fashion model and graphic visual branding director")

    assert len(vec_a) == 384
    assert len(vec_b) == 384
    assert len(vec_c) == 384

    sim_related = EmbeddingProvider.cosine_similarity(vec_a, vec_b)
    sim_unrelated = EmbeddingProvider.cosine_similarity(vec_a, vec_c)

    assert sim_related > sim_unrelated
    score_related = calculate_display_score(sim_related)
    score_unrelated = calculate_display_score(sim_unrelated)
    assert score_related > score_unrelated
    assert 0 <= score_related <= 100


@pytest.mark.asyncio
async def test_resume_upload_and_opportunity_feed(client: AsyncClient, db_session: AsyncSession):
    # 1. Register candidate
    reg = await client.post("/api/v1/auth/register", json={
        "email": "sarah.dev@example.com",
        "password": "SecurePassword123!",
        "name": "Sarah Dev",
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed listings into DB
    source = Source(
        name="Job Source Alpha",
        base_url="https://alpha.com",
        scraper_key="alpha_jobs",
        is_enabled=True,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)

    raw1 = RawListing(
        source_id=source.id,
        source_url="https://alpha.com/job/1",
        canonical_url="https://alpha.com/job/1",
        raw_title="Backend API Engineer",
        raw_content="Acme is hiring a backend API engineer with FastAPI, Python, and PostgreSQL.",
        dedupe_key="alpha:id:1",
        content_hash="h1",
        extraction_status="extracted",
    )
    raw2 = RawListing(
        source_id=source.id,
        source_url="https://alpha.com/job/2",
        canonical_url="https://alpha.com/job/2",
        raw_title="iOS Swift Developer",
        raw_content="Mobile team hiring iOS engineer with Swift, SwiftUI, and Xcode experience.",
        dedupe_key="alpha:id:2",
        content_hash="h2",
        extraction_status="extracted",
    )
    db_session.add_all([raw1, raw2])
    await db_session.commit()
    await db_session.refresh(raw1)
    await db_session.refresh(raw2)

    vec1 = embedding_provider.embed_text("Backend API Engineer at Acme. Skills: Python, FastAPI, PostgreSQL.")
    vec2 = embedding_provider.embed_text("iOS Swift Developer at MobileCo. Skills: Swift, SwiftUI, Xcode.")

    listing1 = Listing(
        raw_listing_id=raw1.id,
        title="Backend API Engineer",
        company="Acme",
        location="Remote",
        remote_ok=True,
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        experience_level="Intern",
        embedding=vec1,
        extractor_version="1.0.0",
    )
    listing2 = Listing(
        raw_listing_id=raw2.id,
        title="iOS Swift Developer",
        company="MobileCo",
        location="New York, NY",
        remote_ok=False,
        required_skills=["Swift", "SwiftUI", "Xcode"],
        experience_level="Mid",
        embedding=vec2,
        extractor_version="1.0.0",
    )
    db_session.add_all([listing1, listing2])
    await db_session.commit()
    await db_session.refresh(listing1)
    await db_session.refresh(listing2)

    # 3. Upload Python backend resume
    resume_text = (
        "Sarah Dev - Software Engineer\n"
        "Experienced in backend web APIs using Python, FastAPI, and PostgreSQL databases.\n"
        "Built microservices with Docker, Redis, and high-performance SQL architectures."
    )
    pdf_bytes = create_sample_pdf_bytes(resume_text)

    files = {"file": ("sarah_resume.pdf", BytesIO(pdf_bytes), "application/pdf")}
    upload_res = await client.post("/api/v1/resume", files=files, headers=headers)
    assert upload_res.status_code == 201
    resume_data = upload_res.json()
    assert resume_data["file_name"] == "sarah_resume.pdf"
    assert resume_data["is_active"] is True

    # 4. Check active resume & status
    res_get = await client.get("/api/v1/resume", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == resume_data["id"]

    status_get = await client.get("/api/v1/resume/status", headers=headers)
    assert status_get.status_code == 200
    assert status_get.json()["matches_calculated"] >= 2

    # 5. Check Opportunity Feed (GET /listings)
    feed_res = await client.get("/api/v1/listings", headers=headers)
    assert feed_res.status_code == 200
    feed = feed_res.json()
    assert len(feed) >= 2

    # Backend role should be ranked FIRST because match score is higher
    top_role = feed[0]
    assert top_role["title"] == "Backend API Engineer"
    assert top_role["match_score"] is not None
    assert top_role["match_explanation"] is not None
    assert "FastAPI" in top_role["match_explanation"] or "Python" in top_role["match_explanation"]
    assert top_role["match_score"] > feed[1]["match_score"]

    # 6. Semantic Search: query "cloud database backend"
    search_res = await client.post(
        "/api/v1/listings/search",
        json={"query": "cloud database backend services"},
        headers=headers,
    )
    assert search_res.status_code == 200
    search_results = search_res.json()
    assert len(search_results) >= 1
    assert search_results[0]["title"] == "Backend API Engineer"

    # 7. Shortlist lifecycle
    listing_id = top_role["id"]
    save_res = await client.post(f"/api/v1/shortlist/{listing_id}", headers=headers)
    assert save_res.status_code == 201

    # Idempotent save
    save_res_dup = await client.post(f"/api/v1/shortlist/{listing_id}", headers=headers)
    assert save_res_dup.status_code == 201

    # View shortlist
    shortlist_res = await client.get("/api/v1/shortlist", headers=headers)
    assert shortlist_res.status_code == 200
    shortlist_items = shortlist_res.json()
    assert len(shortlist_items) == 1
    assert shortlist_items[0]["listing_id"] == listing_id
    assert shortlist_items[0]["listing"]["title"] == "Backend API Engineer"
    assert shortlist_items[0]["listing"]["is_saved"] is True

    # Unsave
    unsave_res = await client.delete(f"/api/v1/shortlist/{listing_id}", headers=headers)
    assert unsave_res.status_code == 200

    # Verify shortlist now empty
    shortlist_empty = await client.get("/api/v1/shortlist", headers=headers)
    assert len(shortlist_empty.json()) == 0
