import asyncio
from typing import Dict, Optional
import httpx
from app.core.logging import logger
from app.scraping.rate_limiter import PerHostRateLimiter, rate_limiter
from app.scraping.robots import RobotsPolicyManager, USER_AGENT, robots_manager


class PoliteScraperClient:
    """
    Polite HTTP scraping client with robots.txt adherence,
    per-host rate limiting, and bounded exponential backoff retries.
    """
    def __init__(
        self,
        user_agent: str = USER_AGENT,
        timeout: float = 10.0,
        max_retries: int = 3,
        limiter: Optional[PerHostRateLimiter] = None,
        robots: Optional[RobotsPolicyManager] = None,
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = limiter or rate_limiter
        self.robots_manager = robots or robots_manager

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        check_robots: bool = True,
    ) -> Optional[httpx.Response]:
        """
        Executes an HTTP GET request politely.
        Returns None if robots.txt disallows or all retries are exhausted.
        """
        request_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if headers:
            request_headers.update(headers)

        if check_robots:
            allowed = await self.robots_manager.can_fetch(url)
            if not allowed:
                logger.warning(f"Robots.txt disallows fetching URL: {url}")
                return None

        # Apply per-host rate limiting
        await self.rate_limiter.throttle(url)

        async with httpx.AsyncClient(headers=request_headers, timeout=self.timeout, follow_redirects=True) as client:
            attempt = 0
            backoff = 1.0

            while attempt < self.max_retries:
                attempt += 1
                try:
                    resp = await client.get(url)

                    # Handle 429 Too Many Requests or 5xx server errors with backoff
                    if resp.status_code in (429, 502, 503, 504):
                        retry_after = resp.headers.get("Retry-After")
                        delay = float(retry_after) if retry_after and retry_after.isdigit() else backoff
                        logger.warning(
                            f"HTTP {resp.status_code} for {url}. Backing off {delay:.1f}s (Attempt {attempt}/{self.max_retries})"
                        )
                        await asyncio.sleep(delay)
                        backoff *= 2.0
                        continue

                    # Successful or client error (4xx other than 429 should not retry)
                    return resp

                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    logger.warning(
                        f"Network error requesting {url}: {exc}. Backoff {backoff:.1f}s (Attempt {attempt}/{self.max_retries})"
                    )
                    if attempt >= self.max_retries:
                        logger.error(f"Exhausted retries for {url}: {exc}")
                        return None
                    await asyncio.sleep(backoff)
                    backoff *= 2.0

        return None
