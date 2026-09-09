import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.saved_listing import SavedListing
from app.models.listing import Listing
from app.models.raw_listing import RawListing
from app.repositories.base import enforce_user_scope, MultiTenancyViolationError


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Register a new user
    register_payload = {
        "email": "candidate@example.com",
        "password": "SecurePassword123!",
        "name": "Alex Candidate",
    }
    res = await client.post("/api/v1/auth/register", json=register_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "candidate@example.com"
    assert data["user"]["name"] == "Alex Candidate"
    assert "id" in data["user"]

    token = data["access_token"]

    # 2. Duplicate registration should fail with 400
    res_dup = await client.post("/api/v1/auth/register", json=register_payload)
    assert res_dup.status_code == 400
    assert res_dup.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    # 3. Login with correct credentials
    login_payload = {
        "email": "candidate@example.com",
        "password": "SecurePassword123!",
    }
    res_login = await client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

    # 4. Login with invalid password
    bad_login = {
        "email": "candidate@example.com",
        "password": "WrongPassword123!",
    }
    res_bad = await client.post("/api/v1/auth/login", json=bad_login)
    assert res_bad.status_code == 401
    assert res_bad.json()["error"]["code"] == "INVALID_CREDENTIALS"

    # 5. Access /auth/me with valid token
    headers = {"Authorization": f"Bearer {token}"}
    res_me = await client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "candidate@example.com"

    # 6. Access /auth/me without token -> 401
    res_unauth = await client.get("/api/v1/auth/me")
    assert res_unauth.status_code == 401
    assert res_unauth.json()["error"]["code"] == "NOT_AUTHENTICATED"

    # 7. Access /auth/me with malformed/invalid token -> 401
    res_invalid = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
    assert res_invalid.status_code == 401
    assert res_invalid.json()["error"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_multitenancy_isolation_enforcement(db_session: AsyncSession):
    # Test enforce_user_scope query helper
    user_a_id = "user-uuid-aaa"
    user_b_id = "user-uuid-bbb"

    # Base query on SavedListing
    query = select(SavedListing)
    scoped_a = enforce_user_scope(query, SavedListing, user_a_id)
    scoped_b = enforce_user_scope(query, SavedListing, user_b_id)

    # Scoped queries must contain where clauses binding to user_id
    str_a = str(scoped_a)
    str_b = str(scoped_b)
    assert "saved_listings.user_id =" in str_a
    assert "saved_listings.user_id =" in str_b

    # Verifying exception when model has no user_id
    with pytest.raises(ValueError, match="does not have a user_id attribute"):
        enforce_user_scope(select(Listing), Listing, user_a_id)
