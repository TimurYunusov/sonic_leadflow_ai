from langchain_openai import ChatOpenAI
from leadflow_ai.agents.email_finder_agent import fetch_page_html
from langchain_core.prompts import PromptTemplate
from leadflow_ai.schemas.lead import AppState
from playwright.async_api import async_playwright
import logging
import asyncio
import re

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


async def fetch_page_html_async(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=20000)
            await page.wait_for_timeout(2000)
            html = await page.content()
            return html
        finally:
            await browser.close()

from bs4 import BeautifulSoup
import re

def extract_business_relevant_text(html: str, min_len: int = 40) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove irrelevant tags
    for tag in soup(["script", "style", "noscript", "iframe", "svg", "footer", "nav", "form", "aside"]):
        tag.decompose()

    # 1. Gather main hero and headings
    sections = []

    # Headings
    headings = soup.find_all(["h1", "h2", "h3"])
    sections += [h.get_text(" ", strip=True) for h in headings if h.get_text(strip=True)]

    # 2. Look for 'about', 'services', 'what we do', etc. in ids/classes
    keywords = re.compile(r'(about|service|what[\s\-]?we[\s\-]?do|company|solution)', re.I)
    special_sections = soup.find_all(
        lambda tag: (
            (tag.name in ["section", "div"]) and
            (tag.get("id") and keywords.search(tag.get("id"))) or
            (tag.get("class") and any(keywords.search(c) for c in tag.get("class")))
        )
    )
    for s in special_sections:
        text = s.get_text(" ", strip=True)
        if len(text) > min_len:
            sections.append(text)

    # 3. Main tag/body fallback
    main = soup.find("main")
    if main:
        main_text = main.get_text(" ", strip=True)
        if len(main_text) > min_len:
            sections.append(main_text)
    else:
        # Fallback: get longest text block in body
        candidates = [block.get_text(" ", strip=True) for block in soup.find_all("div") if block.get_text(strip=True)]
        if candidates:
            candidates = sorted(candidates, key=len, reverse=True)
            if len(candidates[0]) > min_len:
                sections.append(candidates[0])

    # 4. Remove duplicates & join
    seen = set()
    final = []
    for s in sections:
        s_norm = s[:100]  # Use a snippet to identify duplicates
        if s_norm not in seen and len(s) > min_len:
            final.append(s)
            seen.add(s_norm)

    # 5. Join, collapse excessive whitespace, and return
    text = "\n\n".join(final)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

summary_prompt = PromptTemplate.from_template("""
You are a senior business analyst with deep expertise in digital strategy and market positioning.

Your task is to analyze the HTML content of a business's website and produce two clear, structured outputs: a **concise summary** of what the business does and a list of **likely challenges or growth opportunities**, based only on observable information (do not speculate).

First, take a step back and follow this reasoning chain:
1. Identify the core product/service offerings.
2. Examine target industries, client types, and any service features.
3. Look for indicators of company positioning, scale, and language tone (e.g., "cutting-edge", "trusted by", "fast-growing").
4. From this context, infer only *observable* challenges or areas for improvement (e.g., complexity of service, competitive pressure, scaling pains, unclear differentiation).

Use this structure in your response:

---
**What the Business Does**  
-Summarize in 3–6 sentences using clear language. Start with "This company…" and refer to key services, audience, and value proposition.

**Potential Pain Points / Challenges**  
• [Write up to 3 bullet points. Focus on marketing, operational, or product-related signals from the content.]  
• [Avoid repeating the summary. Prioritize real-world business frictions hinted at in the content.]  
• [Avoid hallucinating – only use cues visible in the HTML.]  
---

If no reliable business description can be made from the HTML, respond with:
> Unable to extract meaningful business summary from HTML provided.

Now analyze the following HTML:

HTML:
{html}
""")
def parse_summary_and_painpoints(text):
    # Use forgiving patterns that just look for the section headers
    summary_match = re.search(
        r"\*\*What the Business Does\*\*\s*(.*?)\*\*Potential Pain Points", 
        text, re.DOTALL | re.IGNORECASE
    )
    pain_points_match = re.search(
        r"\*\*Potential Pain Points[^\*]*\*\*\s*((?:[•\-].*\n?)+)", 
        text, re.DOTALL | re.IGNORECASE
    )
    summary = summary_match.group(1).strip() if summary_match else ""
    pain_points = []
    if pain_points_match:
        pain_points = [line.strip("-• ").strip() for line in pain_points_match.group(1).splitlines() if line.strip()]
    pain_points_str = "; ".join(pain_points) if pain_points else ""
    return summary, pain_points_str

async def summarize_business(state: AppState) -> dict:
    for business in state.businesses:
        
        try:
            logging.info(f"🧠 Summarizing business: {business.name}")
            html = await fetch_page_html_async(business.website)
            visible_text = extract_business_relevant_text(html)
            prompt = summary_prompt.format(html=visible_text)
            response_msg = await llm.ainvoke(prompt)
            response = response_msg.content if hasattr(response_msg, 'content') else str(response_msg)
            
            summary, pain_points = parse_summary_and_painpoints(response)
            business.summary = summary or ""
            business.pain_points = str(pain_points or "")
            logging.info(f"Pain points: {business.pain_points}")

        except Exception as e:
            logging.warning(f"⚠️ Failed to summarize {business.name}: {e}")

    return {"businesses": state.businesses}
