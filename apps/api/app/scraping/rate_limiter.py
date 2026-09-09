import asyncio
import random
import time
from typing import Dict
from urllib.parse import urlparse


class PerHostRateLimiter:
    """
    Polite per-host asynchronous rate limiter.
    Ensures a minimum delay with random jitter between requests to the same domain.
    """
    def __init__(self, base_delay: float = 1.0, jitter: float = 0.5):
        self.base_delay = base_delay
        self.jitter = jitter
        self._last_request_time: Dict[str, float] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def _get_host_lock(self, host: str) -> asyncio.Lock:
        async with self._global_lock:
            if host not in self._locks:
                self._locks[host] = asyncio.Lock()
            return self._locks[host]

    async def throttle(self, url: str) -> None:
        host = urlparse(url).netloc.lower()
        if not host:
            return

        lock = await self._get_host_lock(host)
        async with lock:
            last_time = self._last_request_time.get(host, 0.0)
            elapsed = time.time() - last_time
            required_delay = self.base_delay + random.uniform(0, self.jitter)

            if elapsed < required_delay:
                await asyncio.sleep(required_delay - elapsed)

            self._last_request_time[host] = time.time()


# Default singleton instance
rate_limiter = PerHostRateLimiter(base_delay=1.0, jitter=0.5)
