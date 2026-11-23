"""
Enhanced Scraper with Database Integration
=========================================

This scraper combines stealth techniques with database storage.
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

# Import database functions
from database import save_scrape_results, get_scrape_history, get_scrape_details

# Configuration
ZARA_URLS = [
    "https://www.zara.com/",
    "https://www.zara.com/us/",
    "https://www.zara.com/uk/"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Output directories
OUTPUT_DIR = Path("data/enhanced_scrapes")
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
HTML_DIR = OUTPUT_DIR / "html"
LOGS_DIR = OUTPUT_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger.add(
    LOGS_DIR / "enhanced_scraper_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

console = Console()


class EnhancedScraper:
    """Enhanced scraper with database integration"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.retry_count = 0
        self.max_retries = 3
        self.session_id = None
        
        self.scrape_data = {
            "timestamp": self.timestamp,
            "url": "",
            "success": False,
            "html_file": None,
            "screenshot_file": None,
            "title": None,
            "banners": [],
            "errors": [],
            "retries": 0
        }
        
        logger.info(f"Initialized EnhancedScraper: {self.timestamp}")
    
    async def __aenter__(self):
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def start_browser(self) -> None:
        """Start browser with stealth options"""
        try:
            console.print("[blue]🚀 Starting enhanced browser...[/blue]")
            
            self.browser = await async_playwright().start()
            browser_instance = await self.browser.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-web-security"
                ]
            )
            
            user_agent = random.choice(USER_AGENTS)
            
            self.context = await browser_instance.new_context(
                locale="en-US",
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080}
            )
            
            self.page = await self.context.new_page()
            
            # Inject stealth scripts
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            console.print("[green]✅ Enhanced browser started[/green]")
            
        except Exception as e:
            error_msg = f"Failed to start browser: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            raise
    
    async def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """Add random delay"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def navigate_with_retry(self, url: str) -> bool:
        """Navigate with retry mechanism"""
        self.scrape_data["url"] = url
        
        for attempt in range(self.max_retries):
            self.retry_count = attempt + 1
            self.scrape_data["retries"] = self.retry_count
            
            try:
                console.print(f"[blue]🌐 Attempt {attempt + 1}/{self.max_retries}: {url}[/blue]")
                
                await self._random_delay(2.0, 5.0)
                
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
                await self.page.wait_for_load_state("domcontentloaded")
                
                await self._random_delay(1.0, 2.0)
                
                title = await self.page.title()
                if "access denied" in title.lower():
                    console.print(f"[yellow]⚠️ Blocked on attempt {attempt + 1}[/yellow]")
                    
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(random.uniform(5.0, 10.0))
                        continue
                    else:
                        return False
                
                self.scrape_data["title"] = title
                console.print(f"[green]✅ Success: {title}[/green]")
                return True
                
            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                console.print(f"[red]❌ {error_msg}[/red]")
                self.scrape_data["errors"].append(error_msg)
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(random.uniform(3.0, 8.0))
                    continue
                else:
                    return False
        
        return False
    
    async def extract_banners(self) -> List[Dict]:
        """Extract banner data from page"""
        try:
            console.print("[blue]🔍 Extracting banners...[/blue]")
            
            await self.page.wait_for_load_state("networkidle")
            
            # Look for banner elements
            selectors = [
                "a:has-text('SHOP')",
                "a[href*='shop']",
                "a[href*='product']",
                ".hero-banner a",
                ".banner a"
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
            html_filename = f"enhanced_zara_{self.timestamp}.html"
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
            
            screenshot_filename = f"enhanced_zara_{self.timestamp}.png"
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
    
    async def save_to_database(self) -> Optional[int]:
        """Save scrape results to database"""
        try:
            console.print("[blue]💾 Saving to database...[/blue]")
            
            session_id = save_scrape_results(self.scrape_data)
            
            if session_id:
                self.session_id = session_id
                console.print(f"[green]✅ Saved to database with session ID: {session_id}[/green]")
                return session_id
            else:
                console.print("[red]❌ Failed to save to database[/red]")
                return None
                
        except Exception as e:
            error_msg = f"Database save failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            return None
    
    async def run_scrape(self, url: str) -> Dict:
        """Main scraping method"""
        try:
            console.print(Panel.fit(
                f"[bold blue]Enhanced Scraper with Database[/bold blue]\n"
                f"URL: {url}\n"
                f"Timestamp: {self.timestamp}",
                title="🚀 Starting Enhanced Scrape"
            ))
            
            if not await self.navigate_with_retry(url):
                self.scrape_data["success"] = False
                await self.save_to_database()
                return self.scrape_data
            
            await self.extract_banners()
            await self.save_html()
            await self.save_screenshot()
            
            self.scrape_data["success"] = True
            await self.save_to_database()
            
            self._display_results()
            
            console.print(Panel.fit(
                "[bold green]✅ Enhanced Scraping Completed![/bold green]",
                title="🎉 Success"
            ))
            
            return self.scrape_data
            
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            self.scrape_data["errors"].append(error_msg)
            self.scrape_data["success"] = False
            await self.save_to_database()
            return self.scrape_data
    
    def _display_results(self) -> None:
        """Display results"""
        table = Table(title="📊 Enhanced Scraping Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", "✅ Success" if self.scrape_data["success"] else "❌ Failed")
        table.add_row("Session ID", str(self.session_id) if self.session_id else "N/A")
        table.add_row("URL", self.scrape_data["url"])
        table.add_row("Title", self.scrape_data["title"] or "N/A")
        table.add_row("Retries", str(self.scrape_data["retries"]))
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


async def test_enhanced_scraper():
    """Test enhanced scraper with database"""
    results = []
    
    for url in ZARA_URLS:
        console.print(f"\n[bold blue]Testing Enhanced: {url}[/bold blue]")
        
        try:
            async with EnhancedScraper(headless=True) as scraper:
                result = await scraper.run_scrape(url)
                results.append(result)
                await asyncio.sleep(random.uniform(5.0, 10.0))
                
        except Exception as e:
            console.print(f"[red]❌ Failed: {str(e)}[/red]")
            results.append({"url": url, "success": False, "error": str(e)})
    
    return results


def show_database_history():
    """Show database history"""
    console.print("\n[bold blue]📊 Database History[/bold blue]")
    
    history = get_scrape_history(10)
    
    if history:
        table = Table(title="Recent Scrape Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Timestamp", style="blue")
        table.add_column("URL", style="green")
        table.add_column("Success", style="yellow")
        table.add_column("Title", style="white")
        table.add_column("Errors", style="red")
        
        for session in history:
            table.add_row(
                str(session["id"]),
                session["timestamp"][:19],
                session["url"][:30] + "..." if len(session["url"]) > 30 else session["url"],
                "✅" if session["success"] else "❌",
                session["title"][:20] + "..." if session["title"] and len(session["title"]) > 20 else session["title"] or "N/A",
                str(session["error_count"])
            )
        
        console.print(table)
    else:
        console.print("[yellow]No scrape history found[/yellow]")


async def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold blue]Enhanced Scraper with Database Integration[/bold blue]\n"
        "Testing stealth techniques + database storage",
        title="🚀 Starting Enhanced Scraper"
    ))
    
    # Show existing history
    show_database_history()
    
    # Run enhanced scraper
    results = await test_enhanced_scraper()
    
    # Show updated history
    console.print("\n[bold blue]📊 Updated Database History[/bold blue]")
    show_database_history()
    
    # Summary
    successful = sum(1 for r in results if r.get("success"))
    total = len(results)
    
    console.print(Panel.fit(
        f"[bold]Enhanced Scraping Summary[/bold]\n"
        f"Successful: {successful}/{total}\n"
        f"Rate: {(successful/total)*100:.1f}%\n"
        f"All results saved to database",
        title="📊 Final Results"
    ))
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

