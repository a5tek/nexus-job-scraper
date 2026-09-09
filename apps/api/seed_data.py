import os
os.environ["OFFLINE_EMBEDDINGS"] = "1"
import asyncio
from datetime import date, timedelta
from app.db.session import AsyncSessionLocal
from app.models.source import Source
from app.models.raw_listing import RawListing
from app.models.listing import Listing
from app.embeddings.provider import embedding_provider
from app.embeddings.templates import build_listing_embedding_text


SAMPLE_ROLES = [
    {
        "title": "Senior AI Systems Engineer",
        "company": "Nexus Research",
        "location": "San Francisco, CA",
        "remote_ok": True,
        "stipend": "$160,000 - $210,000",
        "required_skills": ["Python", "PyTorch", "FastAPI", "Vector Databases", "Distributed Systems"],
        "days": 12,
        "description": "Architect high-throughput AI agent workflows, implement pgvector similarity retrieval, and manage model inference pipelines.",
    },
    {
        "title": "Full Stack Engineer (Founding Team)",
        "company": "Cognitive Cloud",
        "location": "New York, NY",
        "remote_ok": True,
        "stipend": "$130,000 - $175,000",
        "required_skills": ["TypeScript", "Next.js", "React", "Node.js", "Tailwind CSS", "PostgreSQL"],
        "days": 4,
        "description": "Lead development of candidate-facing workspace surfaces, real-time collaboration widgets, and performant state orchestration.",
    },
    {
        "title": "Machine Learning Platform Engineer",
        "company": "HyperScale AI",
        "location": "Seattle, WA",
        "remote_ok": False,
        "stipend": "$175,000 - $230,000",
        "required_skills": ["Python", "Kubernetes", "Docker", "Go", "Ray", "CI/CD"],
        "days": 21,
        "description": "Design and scale GPU compute clusters for model fine-tuning, training distributed checkpoints, and automated serving infrastructure.",
    },
    {
        "title": "Distributed Systems Intern",
        "company": "CloudScale Labs",
        "location": "Remote",
        "remote_ok": True,
        "stipend": "₹45,000 / month",
        "required_skills": ["Go", "Kafka", "PostgreSQL", "Linux", "gRPC"],
        "days": 5,
        "description": "Build high-throughput event streaming pipelines, consensus protocol benchmarking, and partitioned key-value storage replicas.",
    },
    {
        "title": "Backend Infrastructure Architect",
        "company": "Apex Protocol",
        "location": "Austin, TX",
        "remote_ok": True,
        "stipend": "$150,000 - $190,000",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Microservices"],
        "days": 18,
        "description": "Develop resilient asynchronous microservices, rate-limiting layers, and database partitioning strategies for fintech applications.",
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select
        res = await db.execute(select(Listing))
        if res.scalars().first():
            print("Database already contains listings.")
            return

        # Create default sources
        source = Source(
            name="YC Work at a Startup",
            base_url="https://www.workatastartup.com",
            scraper_key="yc",
            is_enabled=True,
        )
        db.add(source)
        await db.flush()

        today = date.today()
        for idx, role in enumerate(SAMPLE_ROLES, start=1):
            raw = RawListing(
                source_id=source.id,
                source_url=f"https://www.workatastartup.com/jobs/role-{idx}",
                canonical_url=f"https://www.workatastartup.com/jobs/role-{idx}",
                raw_title=role["title"],
                raw_content=role["description"],
                dedupe_key=f"yc:role-{idx}",
                content_hash=f"hash_role_{idx}",
                extraction_status="extracted",
                is_active=True,
            )
            db.add(raw)
            await db.flush()

            # Precalculate embedding
            text_to_embed = build_listing_embedding_text(
                title=role["title"],
                company=role["company"],
                location=role["location"],
                remote_ok=role["remote_ok"],
                required_skills=role["required_skills"],
                description_snippet=role["description"],
            )
            vector = embedding_provider.embed_text(text_to_embed)

            listing = Listing(
                raw_listing_id=raw.id,
                title=role["title"],
                company=role["company"],
                location=role["location"],
                remote_ok=role["remote_ok"],
                stipend=role["stipend"],
                required_skills=role["required_skills"],
                deadline=today + timedelta(days=role["days"]),
                embedding=vector,
                extractor_version="1.0",
            )
            db.add(listing)

        await db.commit()
        print(f"Successfully seeded {len(SAMPLE_ROLES)} initial opportunities.")


if __name__ == "__main__":
    asyncio.run(seed())
