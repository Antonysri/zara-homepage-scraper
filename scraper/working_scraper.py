"""
Working Scraper - Handles Zara's Slow Loading
===========================================

This scraper works around Zara's timeout issues.
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
OUTPUT_DIR = Path("data/working_scrapes")
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
HTML_DIR = OUTPUT_DIR / "html"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)

console = Console()


class WorkingScraper:
    """Working scraper that handles Zara's loading issues"""
    
    def __init__(self, headless: bool = False):
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
            "html_file": None,
            "screenshot_file": None,
            "banners": [],
            "errors": []
        }
        
        logger.info(f"Initialized WorkingScraper: {self.timestamp}")
    
    async def __aenter__(self):
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def start_browser(self) -> None:
        """Start browser with optimized settings"""
        try:
            console.print("[blue]🚀 Starting working browser...[/blue]")
            
            self.browser = await async_playwright().start()
            browser_instance = await self.browser.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding"
                ]
            )
            
            user_agent = random.choice(USER_AGENTS)
            
            self.context = await browser_instance.new_context(
                locale="en-US",
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                timezone_id="Asia/Kolkata"
            )
            
            self.page = await self.context.new_page()
            
            # Basic stealth
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            console.print("[green]✅ Working browser started[/green]")
            
        except Exception as e:
            error_msg = f"Failed to start browser: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            raise
    
    async def navigate_with_patience(self, url: str) -> bool:
        """Navigate with patience for slow loading"""
        self.scrape_data["url"] = url
        
        try:
            console.print(f"[blue]🌐 Navigating with patience: {url}[/blue]")
            
            # Navigate without waiting for networkidle
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait a bit for content to load
            await asyncio.sleep(5)
            
            # Check if we got a title
            title = await self.page.title()
            
            if "access denied" in title.lower() or "blocked" in title.lower():
                console.print(f"[yellow]⚠️ Blocked: {title}[/yellow]")
                return False
            
            if "zara" in title.lower():
                self.scrape_data["title"] = title
                console.print(f"[green]✅ Success: {title}[/green]")
                return True
            else:
                console.print(f"[yellow]⚠️ Unexpected title: {title}[/yellow]")
                return False
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            return False
    
    async def extract_banners(self) -> List[Dict]:
        """Extract banner data"""
        try:
            console.print("[blue]🔍 Extracting banners...[/blue]")
            
            # Wait for page to be more stable
            await asyncio.sleep(3)
            
            # Look for banner elements
            selectors = [
                "a:has-text('SHOP')",
                "a[href*='shop']",
                "a[href*='product']",
                ".hero-banner a",
                ".banner a",
                "[data-testid*='banner'] a"
            ]
            
            banners = []
            
            for selector in selectors:
                try:
                    elements = self.page.locator(selector)
                    count = await elements.count()
                    
                    for i in range(min(count, 10)):
                        try:
                            element = elements.nth(i)
                            href = await element.get_attribute("href")
                            text = await element.inner_text()
                            
                            if href and text.strip():
                                banner_data = {
                                    "type": "banner",
                                    "text": text.strip(),
                                    "href": href,
                                    "index": i
                                }
                                banners.append(banner_data)
                                
                        except Exception as e:
                            logger.debug(f"Error extracting element {i}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            console.print(f"[green]✅ Extracted {len(banners)} banners[/green]")
            self.scrape_data["banners"] = banners
            return banners
            
        except Exception as e:
            error_msg = f"Failed to extract banners: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            return []
    
    async def save_html(self) -> Optional[str]:
        """Save HTML content"""
        try:
            console.print("[blue]💾 Saving HTML...[/blue]")
            
            html_content = await self.page.content()
            html_filename = f"working_zara_{self.timestamp}.html"
            html_filepath = HTML_DIR / html_filename
            
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            console.print(f"[green]✅ HTML saved: {html_filepath}[/green]")
            self.scrape_data["html_file"] = str(html_filepath)
            return str(html_filepath)
            
        except Exception as e:
            error_msg = f"Failed to save HTML: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            return None
    
    async def save_screenshot(self) -> Optional[str]:
        """Save screenshot"""
        try:
            console.print("[blue]📸 Taking screenshot...[/blue]")
            
            screenshot_filename = f"working_zara_{self.timestamp}.png"
            screenshot_filepath = SCREENSHOTS_DIR / screenshot_filename
            
            await self.page.screenshot(path=str(screenshot_filepath), full_page=True)
            
            console.print(f"[green]✅ Screenshot saved: {screenshot_filepath}[/green]")
            self.scrape_data["screenshot_file"] = str(screenshot_filepath)
            return str(screenshot_filepath)
            
        except Exception as e:
            error_msg = f"Failed to save screenshot: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            return None
    
    async def run_scrape(self, url: str) -> Dict:
        """Main scraping method"""
        try:
            console.print(Panel.fit(
                f"[bold blue]Working Scraper[/bold blue]\n"
                f"URL: {url}\n"
                f"Headless: {self.headless}\n"
                f"Timestamp: {self.timestamp}",
                title="🚀 Starting Working Scrape"
            ))
            
            if await self.navigate_with_patience(url):
                self.scrape_data["success"] = True
                await self.extract_banners()
                await self.save_html()
                await self.save_screenshot()
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
        table = Table(title="📊 Working Scraper Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", "✅ Success" if self.scrape_data["success"] else "❌ Failed")
        table.add_row("URL", self.scrape_data["url"])
        table.add_row("Title", self.scrape_data["title"] or "N/A")
        table.add_row("HTML File", self.scrape_data["html_file"] or "❌ Not saved")
        table.add_row("Screenshot", self.scrape_data["screenshot_file"] or "❌ Not saved")
        table.add_row("Banners Found", str(len(self.scrape_data["banners"])))
        table.add_row("Errors", str(len(self.scrape_data["errors"])))
        
        console.print(table)
        
        if self.scrape_data["banners"]:
            banner_table = Table(title="🎯 Extracted Banners")
            banner_table.add_column("Index", style="cyan")
            banner_table.add_column("Text", style="green")
            banner_table.add_column("Link", style="blue")
            
            for banner in self.scrape_data["banners"][:5]:
                banner_table.add_row(
                    str(banner["index"]),
                    banner["text"][:50] + "..." if len(banner["text"]) > 50 else banner["text"],
                    banner["href"][:50] + "..." if len(banner["href"]) > 50 else banner["href"]
                )
            
            if len(self.scrape_data["banners"]) > 5:
                banner_table.add_row("...", f"... and {len(self.scrape_data['banners']) - 5} more", "...")
            
            console.print(banner_table)


async def test_working_scraper():
    """Test working scraper"""
    results = []
    
    for url in ZARA_URLS:
        console.print(f"\n[bold blue]Testing Working Scraper: {url}[/bold blue]")
        
        try:
            async with WorkingScraper(headless=False) as scraper:
                result = await scraper.run_scrape(url)
                results.append(result)
                await asyncio.sleep(random.uniform(5.0, 10.0))
                
        except Exception as e:
            console.print(f"[red]❌ Failed: {str(e)}[/red]")
            results.append({"url": url, "success": False, "error": str(e)})
    
    return results


async def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold blue]Working Scraper Test[/bold blue]\n"
        "Testing with patience for slow loading\n"
        "Browser window will be visible",
        title="🚀 Starting Working Test"
    ))
    
    results = await test_working_scraper()
    
    successful = sum(1 for r in results if r.get("success"))
    total = len(results)
    
    console.print(Panel.fit(
        f"[bold]Working Scraper Summary[/bold]\n"
        f"Successful: {successful}/{total}\n"
        f"Rate: {(successful/total)*100:.1f}%\n"
        f"Check browser window and saved files",
        title="📊 Final Results"
    ))
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

