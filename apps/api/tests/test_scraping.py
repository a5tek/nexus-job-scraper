import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.raw_listing import RawListing
from app.repositories.raw_listing_repo import RawListingRepository
from app.scraping.dedupe import (
    compute_content_hash,
    compute_dedupe_key,
    normalize_canonical_url,
)
from app.scraping.rate_limiter import PerHostRateLimiter
from app.scraping.robots import RobotsPolicyManager
from app.scraping.schemas import ListingCandidate
from app.scraping.sources.github_jobs import GitHubInternshipsScraper
from app.scraping.sources.yc_jobs import YCJobsScraper


def test_url_canonicalization():
    url1 = "https://WWW.Example.com/jobs/123/?utm_source=twitter&utm_medium=cpc&id=456#details"
    canon1 = normalize_canonical_url(url1)
    # Host lowercased, utm params removed, fragment removed, id preserved
    assert canon1 == "https://www.example.com/jobs/123?id=456"

    url2 = "http://example.com/roles//"
    canon2 = normalize_canonical_url(url2)
    assert canon2 == "http://example.com/roles"

    url3 = "https://company.com/career?b=2&a=1&utm_campaign=winter"
    canon3 = normalize_canonical_url(url3)
    assert canon3 == "https://company.com/career?a=1&b=2"


def test_content_hashing_and_dedupe():
    text1 = "  Backend Engineer \n at Acme Corp.   Remote. "
    text2 = "Backend Engineer at Acme Corp. Remote."
    hash1 = compute_content_hash(text1)
    hash2 = compute_content_hash(text2)
    assert hash1 == hash2

    key_id = compute_dedupe_key("yc_jobs", source_listing_id="job_9988")
    assert key_id == "yc_jobs:id:job_9988"

    key_url = compute_dedupe_key("github_internships", canonical_url="https://acme.com/jobs/1")
    assert key_url.startswith("github_internships:url:")


@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = PerHostRateLimiter(base_delay=0.05, jitter=0.01)
    # Consecutive throttles should not crash and should enforce delay
    await limiter.throttle("https://example.com/page1")
    await limiter.throttle("https://example.com/page2")


@pytest.mark.asyncio
async def test_robots_parser_mock():
    manager = RobotsPolicyManager()
    # Mocking parser directly for deterministic testing
    from urllib.robotparser import RobotFileParser
    parser = RobotFileParser()
    parser.parse([
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /jobs/",
    ])
    manager._parsers["https://jobs.example.com"] = parser

    assert await manager.can_fetch("https://jobs.example.com/jobs/1") is True
    assert await manager.can_fetch("https://jobs.example.com/admin/settings") is False


def test_yc_jobs_card_parser():
    scraper = YCJobsScraper()
    sample_html = """
    <div class="jobs-container">
        <div class="job-card" data-job-id="yc_101">
            <h3 class="job-title">Distributed Systems Engineer</h3>
            <span class="company-name">Resilience AI</span>
            <span class="location">San Francisco, CA / Remote</span>
            <div class="job-details">
                Build high-throughput event processing pipelines using Go, Kafka, and PostgreSQL.
            </div>
            <a href="/jobs/yc_101">Apply on YC</a>
        </div>
        <div class="job-card" data-job-id="yc_102">
            <h3 class="job-title">Fullstack AI Intern</h3>
            <span class="company-name">Nexus Labs</span>
            <span class="location">Remote</span>
            <div class="job-details">
                Work with Next.js, FastAPI, and Gemini structured output.
            </div>
            <a href="https://nexuslabs.com/careers/intern">Apply</a>
        </div>
    </div>
    """
    candidates = scraper.parse_html_content(sample_html, "https://www.workatastartup.com/jobs")
    assert len(candidates) == 2

    c1 = candidates[0]
    assert c1.raw_title == "Distributed Systems Engineer"
    assert c1.company_hint == "Resilience AI"
    assert c1.source_listing_id == "yc_101"
    assert "San Francisco" in c1.raw_content
    assert "Go, Kafka, and PostgreSQL" in c1.raw_content

    c2 = candidates[1]
    assert c2.raw_title == "Fullstack AI Intern"
    assert c2.company_hint == "Nexus Labs"
    assert c2.source_url == "https://nexuslabs.com/careers/intern"

    # Test malformed card rejection (no fabricated data)
    malformed_html = """
    <div class="job-card">
        <div>Missing all mandatory headers</div>
    </div>
    """
    assert len(scraper.parse_html_content(malformed_html, "https://example.com")) == 0


def test_github_internships_markdown_and_html_table_parser():
    scraper = GitHubInternshipsScraper()
    
    # 1. Test Markdown table with active and closed (🔒) rows
    sample_md = """
# Tech Internships 2026

| Company | Role | Location | Application Link | Date Posted |
|---|---|---|---|---|
| **[Anthropic](https://anthropic.com)** | [Research Intern](https://anthropic.com/jobs/123?utm_source=tracker) | San Francisco, CA | [Apply](https://anthropic.com/jobs/123?utm_source=tracker) | Sep 01 |
| Datadog | Software Engineer Intern | Remote, US | [Apply](https://datadog.com/jobs/456) | Sep 05 |
| ClosedCorp | Closed Intern Role | New York, NY | 🔒 Closed | Sep 06 |
    """
    md_candidates = scraper.parse_markdown_table(sample_md, "https://github.com/repo/README.md")
    assert len(md_candidates) == 2
    assert md_candidates[0].company_hint == "Anthropic"
    assert md_candidates[0].raw_title == "Research Intern"
    assert md_candidates[0].source_url == "https://anthropic.com/jobs/123"
    assert md_candidates[1].company_hint == "Datadog"
    assert md_candidates[1].raw_title == "Software Engineer Intern"

    # 2. Test HTML table with closed row filtering
    sample_html = """
    <table>
        <thead>
            <tr><th>Company</th><th>Role</th><th>Location</th><th>Application</th></tr>
        </thead>
        <tbody>
            <tr>
                <td>Stripe</td>
                <td>Infrastructure Intern</td>
                <td>Seattle, WA</td>
                <td><a href="https://stripe.com/jobs/789">Apply Here</a></td>
            </tr>
            <tr>
                <td>OldCo</td>
                <td>Closed Role</td>
                <td>Remote</td>
                <td>🔒 Closed</td>
            </tr>
        </tbody>
    </table>
    """
    html_candidates = scraper.parse_html_table(sample_html, "https://github.com/repo/page.html")
    assert len(html_candidates) == 1
    assert html_candidates[0].company_hint == "Stripe"
    assert html_candidates[0].raw_title == "Infrastructure Intern"
    assert html_candidates[0].source_url == "https://stripe.com/jobs/789"


@pytest.mark.asyncio
async def test_remoteok_scraper_parser():
    from app.scraping.sources.remoteok_jobs import RemoteOKScraper
    scraper = RemoteOKScraper()
    assert scraper.source_key == "remoteok"
    assert scraper.source_name == "RemoteOK"

    # Mock response format of RemoteOK JSON API
    mock_payload = [
        {"legal": "RemoteOK API disclaimer and terms of service"},
        {
            "id": "12345",
            "company": "Acme Remote Cloud",
            "position": "Senior Backend Python Engineer",
            "location": "Worldwide / Remote",
            "tags": ["python", "fastapi", "postgres"],
            "description": "<p>We are seeking a <b>talented</b> senior backend developer.</p>",
            "apply_url": "https://acme.com/careers/python-engineer",
            "salary_min": 130000,
            "salary_max": 160000,
        },
        {
            "id": "12346",
            # Missing company and title - should be discarded
            "company": "",
            "position": "",
        },
    ]

    class MockResponse:
        status_code = 200
        def json(self):
            return mock_payload

    class MockClient:
        async def get(self, url, headers=None, check_robots=True):
            return MockResponse()

    scraper.client = MockClient()
    candidates = await scraper.scrape_page("https://remoteok.com/api")
    assert len(candidates) == 1
    c = candidates[0]
    assert c.source_name == "RemoteOK"
    assert c.company_hint == "Acme Remote Cloud"
    assert c.raw_title == "Senior Backend Python Engineer"
    assert c.source_listing_id == "12345"
    assert c.source_url == "https://acme.com/careers/python-engineer"
    assert "Salary: $130,000 - $160,000" in c.raw_content
    assert "fastapi" in c.raw_content


@pytest.mark.asyncio
async def test_raw_listing_upsert_lifecycle(db_session: AsyncSession):
    source = await RawListingRepository.get_or_create_source(
        db=db_session,
        name="Test Ingestion Source",
        base_url="https://example.com",
        scraper_key="test_source",
    )
    assert source.id is not None

    candidate = ListingCandidate(
        source_name="Test Ingestion Source",
        source_url="https://example.com/job/100?utm_source=test",
        source_listing_id="job_100",
        raw_title="Platform Engineer",
        raw_content="Acme Corp is hiring a platform engineer with Kubernetes and Go experience.",
        company_hint="Acme Corp",
        location_hint="Remote",
    )

    # 1. First run -> inserted
    record, status1 = await RawListingRepository.upsert_candidate(db_session, source.id, candidate)
    assert status1 == "inserted"
    assert record.extraction_status == "pending"
    assert record.is_active is True
    first_seen = record.first_seen_at

    # 2. Re-scrape identical -> unchanged, last_seen_at refreshed
    record2, status2 = await RawListingRepository.upsert_candidate(db_session, source.id, candidate)
    assert status2 == "unchanged"
    assert record2.id == record.id
    assert record2.first_seen_at == first_seen

    # 3. Content changed -> updated, extraction_status reset to pending
    candidate_updated = ListingCandidate(
        source_name="Test Ingestion Source",
        source_url="https://example.com/job/100?utm_source=test",
        source_listing_id="job_100",
        raw_title="Senior Platform Engineer",
        raw_content="Acme Corp is NOW hiring a SENIOR platform engineer with Rust, Kubernetes and Go experience.",
        company_hint="Acme Corp",
        location_hint="Remote",
    )
    record3, status3 = await RawListingRepository.upsert_candidate(db_session, source.id, candidate_updated)
    assert status3 == "updated"
    assert record3.id == record.id
    assert record3.extraction_status == "pending"
    assert record3.raw_title == "Senior Platform Engineer"


@pytest.mark.asyncio
async def test_internal_sources_endpoint(client: AsyncClient):
    res = await client.get("/api/v1/internal/sources")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    keys = [item["source_key"] for item in data]
    assert "yc_jobs" in keys
    assert "github_internships" in keys
    assert "remoteok" in keys
