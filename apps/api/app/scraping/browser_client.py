import asyncio
from typing import Optional
from app.core.logging import logger
from app.scraping.client import PoliteScraperClient

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PlaywrightScraperClient:
    """
    Headless browser scraper client for JavaScript-rendered SPAs.
    Gracefully falls back to polite HTTP client if Playwright is unavailable.
    """
    def __init__(self, headless: bool = True, timeout_ms: int = 15000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._fallback_client = PoliteScraperClient()
        self._playwright = None
        self._browser = None

    async def get_browser(self):
        if not PLAYWRIGHT_AVAILABLE:
            return None
        if self._browser is None:
            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
                )
            except Exception as exc:
                logger.warning(f"Could not initialize Playwright browser ({exc}). Falling back to HTTP client.")
                self._browser = None
        return self._browser

    async def get_rendered_content(self, url: str, wait_selector: Optional[str] = None) -> Optional[str]:
        """
        Loads page in headless browser, waits for network idle or selector, and returns rendered HTML.
        """
        browser = await self.get_browser()
        if browser:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NexusCareerBot/1.0"
                )
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
                if wait_selector:
                    try:
                        await page.wait_for_selector(wait_selector, timeout=5000)
                    except Exception:
                        pass
                content = await page.content()
                await context.close()
                return content
            except Exception as exc:
                logger.warning(f"Playwright failed to fetch {url}: {exc}. Falling back to HTTP client.")

        # Fallback to standard polite HTTP client
        resp = await self._fallback_client.get(url)
        return resp.text if resp and resp.status_code == 200 else None

    async def close(self) -> None:
        """Closes browser and subprocess."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        await self._fallback_client.close()
