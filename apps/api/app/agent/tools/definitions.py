from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.embeddings.provider import embedding_provider
from app.models.listing import Listing
from app.models.match import Match
from app.models.saved_listing import SavedListing
from app.repositories.listing_repo import ListingRepository
from app.repositories.saved_listing_repo import SavedListingRepository


async def tool_search_listings(
    db: AsyncSession,
    user_id: str,
    query: str,
    limit: int = 5,
    remote_only: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Search opportunities semantically by concept, skill, or role description.
    """
    query_vec = embedding_provider.embed_text(query)
    results = await ListingRepository.semantic_search(
        db=db,
        query_vector=query_vec,
        limit=min(limit, 10),
        remote_only=remote_only,
    )

    listings_data = []
    for listing, sim in results:
        listings_data.append({
            "id": listing.id,
            "title": listing.title,
            "company": listing.company,
            "location": listing.location,
            "remote_ok": listing.remote_ok,
            "skills": (listing.required_skills or [])[:6],
            "deadline": str(listing.deadline) if listing.deadline else "Not stated",
        })

    return {
        "query": query,
        "count": len(listings_data),
        "listings": listings_data,
    }


async def tool_get_saved_listings(
    db: AsyncSession,
    user_id: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Retrieves the current user's shortlisted (saved) opportunities with match scores.
    """
    saved_records = await SavedListingRepository.list_for_user(db, user_id, limit=min(limit, 20))
    items = []
    for saved, listing, match in saved_records:
        items.append({
            "id": listing.id,
            "title": listing.title,
            "company": listing.company,
            "location": listing.location,
            "remote_ok": listing.remote_ok,
            "match_score": match.display_score if match else None,
            "justification": match.justification if match else None,
            "deadline": str(listing.deadline) if listing.deadline else "Not stated",
        })

    return {
        "user_id": user_id,
        "count": len(items),
        "saved_listings": items,
    }


async def tool_get_listings_by_deadline(
    db: AsyncSession,
    user_id: str,
    days_ahead: int = 14,
    saved_only: bool = False,
) -> Dict[str, Any]:
    """
    Finds job opportunities with application deadlines approaching in the next N days.
    """
    today = date.today()
    target_date = today + timedelta(days=days_ahead)

    if saved_only:
        saved_records = await SavedListingRepository.list_for_user(db, user_id, limit=50)
        items = []
        for _, listing, match in saved_records:
            if listing.deadline and today <= listing.deadline <= target_date:
                items.append({
                    "id": listing.id,
                    "title": listing.title,
                    "company": listing.company,
                    "deadline": str(listing.deadline),
                    "days_remaining": (listing.deadline - today).days,
                    "match_score": match.display_score if match else None,
                })
        items.sort(key=lambda x: x["deadline"])
        return {"days_ahead": days_ahead, "saved_only": True, "count": len(items), "listings": items}

    # All listings
    stmt = (
        select(Listing)
        .where(
            Listing.deadline.isnot(None),
            Listing.deadline >= today,
            Listing.deadline <= target_date,
        )
        .order_by(Listing.deadline.asc())
        .limit(10)
    )
    res = await db.execute(stmt)
    listings = res.scalars().all()

    items = [
        {
            "id": l.id,
            "title": l.title,
            "company": l.company,
            "deadline": str(l.deadline),
            "days_remaining": (l.deadline - today).days,
        }
        for l in listings
    ]
    return {"days_ahead": days_ahead, "saved_only": False, "count": len(items), "listings": items}


async def tool_get_skill_frequency(
    db: AsyncSession,
    user_id: str,
    saved_only: bool = False,
    top_n: int = 10,
) -> Dict[str, Any]:
    """
    Aggregates the most frequently required technical skills across matching or saved listings.
    """
    skill_counter = Counter()

    if saved_only:
        saved_records = await SavedListingRepository.list_for_user(db, user_id, limit=50)
        for _, listing, _ in saved_records:
            if listing.required_skills:
                for s in listing.required_skills:
                    skill_counter[s] += 1
    else:
        stmt = (
            select(Match, Listing)
            .join(Listing, Match.listing_id == Listing.id)
            .where(Match.user_id == user_id, Match.display_score >= 50)
            .limit(30)
        )
        res = await db.execute(stmt)
        for _, listing in res.all():
            if listing.required_skills:
                for s in listing.required_skills:
                    skill_counter[s] += 1

    top_skills = [
        {"skill": skill, "count": count}
        for skill, count in skill_counter.most_common(top_n)
    ]
    return {
        "scope": "saved_listings" if saved_only else "top_matching_listings",
        "top_skills": top_skills,
    }


async def tool_get_top_matches(
    db: AsyncSession,
    user_id: str,
    limit: int = 5,
    min_score: int = 60,
) -> Dict[str, Any]:
    """
    Retrieves the user's highest scoring role matches based on resume semantic similarity.
    """
    stmt = (
        select(Match, Listing)
        .join(Listing, Match.listing_id == Listing.id)
        .where(Match.user_id == user_id, Match.display_score >= min_score)
        .order_by(desc(Match.display_score))
        .limit(min(limit, 10))
    )
    res = await db.execute(stmt)
    records = res.all()

    matches_data = []
    for match, listing in records:
        matches_data.append({
            "id": listing.id,
            "title": listing.title,
            "company": listing.company,
            "location": listing.location,
            "remote_ok": listing.remote_ok,
            "match_score": match.display_score,
            "justification": match.justification,
            "skills": (listing.required_skills or [])[:5],
        })

    return {
        "min_score": min_score,
        "count": len(matches_data),
        "matches": matches_data,
    }


# Tool Registry mapping name -> function & doc
AGENT_TOOLS = {
    "search_listings": {
        "func": tool_search_listings,
        "description": "Search job opportunities semantically by concept, skill, or role description.",
        "parameters": {
            "query": {"type": "string", "description": "The search term, concept, or required technologies"},
            "limit": {"type": "integer", "description": "Maximum number of results to return (default 5)"},
            "remote_only": {"type": "boolean", "description": "Filter for remote-friendly roles"},
        },
    },
    "get_saved_listings": {
        "func": tool_get_saved_listings,
        "description": "Retrieve the current user's shortlisted (saved) opportunities with match scores.",
        "parameters": {
            "limit": {"type": "integer", "description": "Maximum number of saved items to retrieve (default 10)"},
        },
    },
    "get_listings_by_deadline": {
        "func": tool_get_listings_by_deadline,
        "description": "Find job opportunities with application deadlines approaching in the next N days.",
        "parameters": {
            "days_ahead": {"type": "integer", "description": "Number of days ahead to check (default 14)"},
            "saved_only": {"type": "boolean", "description": "Whether to check only user's saved listings"},
        },
    },
    "get_skill_frequency": {
        "func": tool_get_skill_frequency,
        "description": "Aggregate the most frequently required technical skills across matching or saved listings.",
        "parameters": {
            "saved_only": {"type": "boolean", "description": "Aggregate from saved listings only (default False)"},
            "top_n": {"type": "integer", "description": "Number of top skills to return (default 10)"},
        },
    },
    "get_top_matches": {
        "func": tool_get_top_matches,
        "description": "Retrieve the user's highest scoring role matches based on resume semantic similarity.",
        "parameters": {
            "limit": {"type": "integer", "description": "Number of top roles to return (default 5)"},
            "min_score": {"type": "integer", "description": "Minimum match score threshold (default 60)"},
        },
    },
}
