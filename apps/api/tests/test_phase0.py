import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_settings_loaded():
    assert settings.APP_NAME == "Nexus"
    assert settings.EXTRACTOR_VERSION == "1.0.0"
    assert settings.JWT_ALGORITHM == "HS256"


def test_password_hashing():
    raw = "MySecurePassword123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_cycle():
    user_id = "test-user-uuid-1234"
    token = create_access_token(subject=user_id)
    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == user_id
    assert payload.get("iss") == "nexus-api"


@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Root health
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "Nexus"

        # API v1 health
        v1_resp = await ac.get("/api/v1/health")
        assert v1_resp.status_code == 200
        v1_data = v1_resp.json()
        assert v1_data["status"] == "ok"
        assert v1_data["service"] == "nexus-api"
