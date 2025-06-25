from langchain.tools import tool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

@tool
def fetch_page_html(url: str) -> str:
    """Fetch visible text from a webpage and return up to 6000 characters."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(2000)
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            trimmed_text = text[:6000]  # Keep it safe for GPT-4 input
        except Exception as e:
            trimmed_text = f"ERROR: {e}"
        finally:
            browser.close()
    return trimmed_text
