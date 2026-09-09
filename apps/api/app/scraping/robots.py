import asyncio
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx
from app.core.logging import logger

USER_AGENT = "NexusCareerBot/1.0 (+https://github.com/a5tek/nexus-job-scraper)"


class RobotsPolicyManager:
    """
    Manages and caches robots.txt policies per domain.
    Respects robots exclusion standard politely.
    """
    def __init__(self, user_agent: str = USER_AGENT):
        self.user_agent = user_agent
        self._parsers: Dict[str, RobotFileParser] = {}
        self._lock = asyncio.Lock()

    def _get_origin(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    async def can_fetch(self, url: str, client: Optional[httpx.AsyncClient] = None) -> bool:
        """
        Determines whether the given URL is allowed to be crawled according to robots.txt.
        """
        parsed = urlparse(url)
        if not parsed.netloc:
            return False

        origin = self._get_origin(url)

        async with self._lock:
            if origin not in self._parsers:
                parser = RobotFileParser()
                robots_url = f"{origin}/robots.txt"
                try:
                    if client:
                        resp = await client.get(robots_url, timeout=5.0)
                    else:
                        async with httpx.AsyncClient(headers={"User-Agent": self.user_agent}) as temp_client:
                            resp = await temp_client.get(robots_url, timeout=5.0)

                    if resp.status_code == 200:
                        parser.parse(resp.text.splitlines())
                    elif resp.status_code in (401, 403):
                        # Blocked completely
                        parser.disallow_all = True
                    else:
                        # 404 or others allow by default
                        parser.allow_all = True
                except Exception as exc:
                    logger.warning(f"Failed to fetch robots.txt from {robots_url}: {exc}. Allowing requests by default.")
                    parser.allow_all = True

                self._parsers[origin] = parser

            parser = self._parsers[origin]

        return parser.can_fetch(self.user_agent, url)


# Shared singleton instance
robots_manager = RobotsPolicyManager()
