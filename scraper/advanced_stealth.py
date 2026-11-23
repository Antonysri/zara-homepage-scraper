"""
Advanced Stealth Scraper - Enhanced Anti-Detection
=================================================

Testing improved stealth techniques for Zara access.
"""

import asyncio
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

# Configuration
ZARA_URLS = ["https://www.zara.com/", "https://www.zara.com/us/"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Output directories
OUTPUT_DIR = Path("data/advanced_stealth")
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
HTML_DIR = OUTPUT_DIR / "html"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)

console = Console()


class AdvancedStealthScraper:
    """Advanced stealth scraper with enhanced anti-detection"""
    
    def __init__(self, headless: bool = False):  # Changed to False for testing
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.scrape_data = {
            "timestamp": self.timestamp,
            "url": "",
            "success": False,
            "title": None,
            "errors": [],
            "stealth_methods": []
        }
        
        logger.info(f"Initialized AdvancedStealthScraper: {self.timestamp}")
    
    async def __aenter__(self):
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def start_browser(self) -> None:
        """Start browser with advanced stealth"""
        try:
            console.print("[blue]🚀 Starting advanced stealth browser...[/blue]")
            
            self.browser = await async_playwright().start()
            browser_instance = await self.browser.chromium.launch(
                headless=self.headless,  # Show browser window
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-default-apps",
                    "--disable-sync",
                    "--disable-translate"
                ]
            )
            
            user_agent = random.choice(USER_AGENTS)
            
            self.context = await browser_instance.new_context(
                locale="en-US",
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                timezone_id="Asia/Kolkata",  # Indian timezone
                geolocation={"latitude": 20.5937, "longitude": 78.9629},  # India coordinates
                permissions=["geolocation"]
            )
            
            self.page = await self.context.new_page()
            
            # Enhanced stealth scripts
            await self._inject_advanced_stealth()
            
            console.print("[green]✅ Advanced stealth browser started[/green]")
            
        except Exception as e:
            error_msg = f"Failed to start browser: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            raise
    
    async def _inject_advanced_stealth(self) -> None:
        """Inject advanced stealth scripts"""
        try:
            # Comprehensive stealth injection
            await self.page.add_init_script("""
                // Remove automation properties
                delete navigator.__proto__.webdriver;
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Add human-like properties
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Modify screen properties
                Object.defineProperty(screen, 'width', {
                    get: () => 1920,
                });
                
                Object.defineProperty(screen, 'height', {
                    get: () => 1080,
                });
                
                // Add chrome object
                Object.defineProperty(window, 'chrome', {
                    writable: true,
                    enumerable: true,
                    configurable: true,
                    value: {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    },
                });
                
                // Modify permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Add human-like behavior
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
            """)
            
            self.scrape_data["stealth_methods"].extend([
                "webdriver_removal",
                "human_properties",
                "screen_modification",
                "chrome_object",
                "permissions_modification"
            ])
            
            console.print("[green]✅ Advanced stealth scripts injected[/green]")
            
        except Exception as e:
            logger.error(f"Failed to inject stealth scripts: {str(e)}")
    
    async def _human_like_behavior(self) -> None:
        """Simulate human-like behavior"""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                await self.page.mouse.move(
                    random.randint(100, 800),
                    random.randint(100, 600)
                )
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Random scrolling
            await self.page.mouse.wheel(0, random.randint(100, 300))
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Random clicks (empty areas)
            await self.page.mouse.click(
                random.randint(50, 200),
                random.randint(50, 150)
            )
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            self.scrape_data["stealth_methods"].append("human_behavior")
            
        except Exception as e:
            logger.debug(f"Human behavior simulation failed: {str(e)}")
    
    async def _random_delay(self, min_seconds: float = 2.0, max_seconds: float = 8.0) -> None:
        """Add longer random delays"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def navigate_with_stealth(self, url: str) -> bool:
        """Navigate with advanced stealth"""
        self.scrape_data["url"] = url
        
        try:
            console.print(f"[blue]🌐 Navigating with stealth: {url}[/blue]")
            
            # Pre-navigation delay
            await self._random_delay(3.0, 7.0)
            
            # Navigate to page
            await self.page.goto(url, wait_until="networkidle", timeout=45000)
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Post-navigation delay
            await self._random_delay(2.0, 5.0)
            
            # Human-like behavior
            await self._human_like_behavior()
            
            # Check if blocked
            title = await self.page.title()
            if "access denied" in title.lower() or "blocked" in title.lower():
                console.print(f"[yellow]⚠️ Still blocked: {title}[/yellow]")
                return False
            
            self.scrape_data["title"] = title
            console.print(f"[green]✅ Success: {title}[/green]")
            return True
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            return False
    
    async def save_results(self) -> None:
        """Save HTML and screenshot"""
        try:
            # Save HTML
            html_content = await self.page.content()
            html_filename = f"advanced_stealth_{self.timestamp}.html"
            html_filepath = HTML_DIR / html_filename
            
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            console.print(f"[green]✅ HTML saved: {html_filepath}[/green]")
            
            # Save screenshot
            screenshot_filename = f"advanced_stealth_{self.timestamp}.png"
            screenshot_filepath = SCREENSHOTS_DIR / screenshot_filename
            
            await self.page.screenshot(path=str(screenshot_filepath), full_page=True)
            console.print(f"[green]✅ Screenshot saved: {screenshot_filepath}[/green]")
            
        except Exception as e:
            error_msg = f"Failed to save results: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
    
    async def run_scrape(self, url: str) -> Dict:
        """Main scraping method"""
        try:
            console.print(Panel.fit(
                f"[bold blue]Advanced Stealth Scraper[/bold blue]\n"
                f"URL: {url}\n"
                f"Headless: {self.headless}\n"
                f"Stealth Methods: {len(self.scrape_data['stealth_methods'])}",
                title="🚀 Starting Advanced Stealth Test"
            ))
            
            if await self.navigate_with_stealth(url):
                self.scrape_data["success"] = True
                await self.save_results()
            else:
                self.scrape_data["success"] = False
            
            self._display_results()
            return self.scrape_data
            
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            self.scrape_data["success"] = False
            return self.scrape_data
    
    def _display_results(self) -> None:
        """Display results"""
        table = Table(title="📊 Advanced Stealth Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", "✅ Success" if self.scrape_data["success"] else "❌ Failed")
        table.add_row("URL", self.scrape_data["url"])
        table.add_row("Title", self.scrape_data["title"] or "N/A")
        table.add_row("Headless", str(self.headless))
        table.add_row("Stealth Methods", ", ".join(self.scrape_data["stealth_methods"]))
        table.add_row("Errors", str(len(self.scrape_data["errors"])))
        
        console.print(table)


async def test_advanced_stealth():
    """Test advanced stealth scraper"""
    results = []
    
    for url in ZARA_URLS:
        console.print(f"\n[bold blue]Testing Advanced Stealth: {url}[/bold blue]")
        
        try:
            async with AdvancedStealthScraper(headless=False) as scraper:
                result = await scraper.run_scrape(url)
                results.append(result)
                await asyncio.sleep(random.uniform(10.0, 15.0))
                
        except Exception as e:
            console.print(f"[red]❌ Failed: {str(e)}[/red]")
            results.append({"url": url, "success": False, "error": str(e)})
    
    return results


async def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold blue]Advanced Stealth Scraper Test[/bold blue]\n"
        "Testing enhanced anti-detection techniques\n"
        "Browser window will be visible for testing",
        title="🚀 Starting Advanced Test"
    ))
    
    results = await test_advanced_stealth()
    
    successful = sum(1 for r in results if r.get("success"))
    total = len(results)
    
    console.print(Panel.fit(
        f"[bold]Advanced Stealth Summary[/bold]\n"
        f"Successful: {successful}/{total}\n"
        f"Rate: {(successful/total)*100:.1f}%\n"
        f"Check browser window for visual feedback",
        title="📊 Final Results"
    ))
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

