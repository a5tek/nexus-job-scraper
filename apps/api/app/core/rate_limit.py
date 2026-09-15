from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Rate limiter with remote address keying
# Disabled in test environment to prevent false positives in rapid test suites
limiter = Limiter(
    key_func=get_remote_address,
    enabled=(settings.APP_ENV != "test"),
)
