import re
import logging
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from leadflow_ai.agents.email_finder_agent import find_email_for_website_with_llm
from langchain_openai import ChatOpenAI
from leadflow_ai.schemas.lead import AppState

def extract_emails_from_html(html: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)

FORBIDDEN_EMAIL_PATTERNS = [
    "bootstrap", "fontawesome", "googleapis", "cloudflare", "cdn",
    "localhost", "example.com", "fancybox", "admin@", "test@", "noreply@"
]

def is_valid_email(email: str, domain: str = None) -> bool:
    if not email or "@" not in email:
        return False
    email_l = email.lower()
    if any(bad in email_l for bad in FORBIDDEN_EMAIL_PATTERNS):
        return False
    if domain and domain not in email_l:
        # Optionally require the email to match business domain
        return False
    # Very basic check
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def smart_score_email(email, visible_text, footer_text):
    s = 0
    if "info@" in email or "contact@" in email or "support@" in email:
        s += 10
    if email.lower() in visible_text:
        s += 5
    if footer_text and email.lower() in footer_text:
        s += 5
    idx = visible_text.find(email.lower())
    if idx != -1:
        window = visible_text[max(0, idx-40):idx+40]
        if any(w in window for w in ["contact", "inquir", "media", "reach us", "email us"]):
            s += 5
    if "dev@" in email or "agency" in email or "webmaster@" in email:
        s -= 5
    return s

async def find_email_for_website(url: str, llm=None) -> dict:
    logging.info(f"Finding email for {url}")
    pages_to_try = ["", "/contact", "/about"]
    best_email = None
    best_score = float('-inf')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for path in pages_to_try:
            try:
                full_url = urljoin(url, path)
                await page.goto(full_url, timeout=10000)
                await page.wait_for_timeout(2000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                visible_text = soup.get_text(separator=" ").lower()
                footer = soup.find("footer")
                footer_text = footer.get_text(separator=" ").lower() if footer else ""

                # Look for visible, user-facing mailto emails in the footer/contact
                for a in soup.find_all("a", href=True):
                    if a["href"].startswith("mailto:"):
                        mailto_email = a["href"].replace("mailto:", "").strip()
                        score = smart_score_email(mailto_email, visible_text, footer_text)
                        if score > best_score:
                            best_email, best_score = mailto_email, score

                # Collect all emails and rank them
                emails = set(extract_emails_from_html(content))
                for email in emails:
                    if is_valid_email(email):
                        score = smart_score_email(email, visible_text, footer_text)
                        if score > best_score:
                            best_email, best_score = email, score

            except Exception as e:
                logging.warning(f"Failed to process {url + path}: {e}")
                continue

        await browser.close()

    if best_email:
        return {"email": best_email, "source": "smart_extractor"}

    # Priority 3: fallback to LLM (if still no good email found)
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    try:
        email = await find_email_for_website_with_llm(url, llm)
        if email:
            return {"email": email, "source": "llm"}
    except Exception as e:
        logging.error(f"LLM fallback failed for {url}: {e}")

    return {"email": None, "source": "not_found"}

async def update_business_emails(state: AppState) -> AppState:
    filtered_businesses = []
    for business in state.businesses:
        if not business.email:
            result = await find_email_for_website(business.website)
            business.email = result.get("email")

        if business.email:  # Keep only businesses with emails
            filtered_businesses.append(business)
        else:
            logging.info(f"🚫 Skipping {business.name} — No valid email found.")

    state.businesses = filtered_businesses
    return state
