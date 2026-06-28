import asyncio
import httpx
from bs4 import BeautifulSoup

async def perform_search(query: str, api_key: str = None, provider: str = "tavily") -> str:
    """
    Searches the web and returns the top URL.
    Tries Tavily first (if key provided), then falls back to DuckDuckGo.
    """
    # 1. Try Tavily if key is available
    if provider == "tavily" and api_key:
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        data = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": 1
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                results = response.json()
                if "results" in results and len(results["results"]) > 0:
                    return results["results"][0]["url"]
        except Exception as e:
            print(f"[Search] Tavily failed: {e}")
            
    # 2. Fallback: DuckDuckGo via simple HTTP (no external library needed)
    try:
        search_url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.post(search_url, data=params, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # DuckDuckGo HTML results have class "result__url"
                result_links = soup.select("a.result__a")
                if result_links:
                    href = result_links[0].get("href", "")
                    if href.startswith("//"):
                        href = "https:" + href
                    return href
    except Exception as e:
        print(f"[Search] DuckDuckGo HTML fallback failed: {e}")
        
    return ""

async def scrape_url(url: str) -> str:
    """
    Scrapes text content from a URL using httpx + BeautifulSoup.
    Falls back from Playwright to simple HTTP if needed.
    """
    if not url:
        return ""
    
    # Try simple HTTP first (faster, no browser needed)
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts, styles, etc.
                for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                    element.decompose()
                    
                text = soup.get_text(separator=' ', strip=True)
                
                # Basic cleanup
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = ' '.join(lines)
                
                # Only return if we got meaningful content
                if len(text) > 100:
                    return text[:5000]
    except Exception as e:
        print(f"[Scraper] HTTP scrape failed for {url}: {e}")
    
    # Fallback to Playwright for JS-heavy pages
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            
            html = await page.content()
            await browser.close()
            
            soup = BeautifulSoup(html, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                element.decompose()
                
            text = soup.get_text(separator=' ', strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = ' '.join(lines)
            
            return text[:5000]
            
    except Exception as e:
        print(f"[Scraper] Playwright fallback failed for {url}: {e}")
        return ""
