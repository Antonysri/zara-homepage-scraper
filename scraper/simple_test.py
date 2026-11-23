"""
Simple Test - Basic Zara Access Test
==================================

Testing basic access to see what's happening.
"""

import asyncio
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()


async def simple_test():
    """Simple test to see what happens"""
    try:
        console.print("[blue]🚀 Starting simple test...[/blue]")
        
        async with async_playwright() as p:
            # Launch browser (visible)
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            console.print("[blue]🌐 Navigating to Zara...[/blue]")
            
            # Try to navigate
            try:
                await page.goto("https://www.zara.com/", timeout=30000)
                title = await page.title()
                console.print(f"[green]✅ Success: {title}[/green]")
                
                # Take screenshot
                await page.screenshot(path="simple_test_success.png")
                console.print("[green]✅ Screenshot saved[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Navigation failed: {str(e)}[/red]")
                
                # Try to get current page info
                try:
                    title = await page.title()
                    console.print(f"[yellow]Current title: {title}[/yellow]")
                    
                    # Take screenshot of error page
                    await page.screenshot(path="simple_test_error.png")
                    console.print("[yellow]⚠️ Error screenshot saved[/yellow]")
                    
                except Exception as e2:
                    console.print(f"[red]❌ Couldn't get page info: {str(e2)}[/red]")
            
            await browser.close()
            
    except Exception as e:
        console.print(f"[red]❌ Test failed: {str(e)}[/red]")


if __name__ == "__main__":
    asyncio.run(simple_test())

