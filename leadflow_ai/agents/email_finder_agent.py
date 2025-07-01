from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from leadflow_ai.schemas.lead import AppState
from langchain.tools import tool
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

@tool
async def fetch_page_html(url: str) -> str:
    """Fetch visible text from a webpage and return up to 6000 characters."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
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


def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email)) and "example.com" not in email and "email.com" not in email
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

tools = [
    Tool(
        name="fetch_page_html",
        func=fetch_page_html,
        description="Fetch the HTML content of a webpage. Input must be a full URL like https://site.com/contact."
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

def find_email_for_website_with_llm(website: str, llm: ChatOpenAI) -> str | None:
    prompt = f"""
You're a web research agent. Your ONLY task is to extract a valid business contact email address from the website: {website}

Steps:
1. Use the tool `fetch_page_html` to visit the homepage and common contact pages (like /contact, /about).
2. Read and analyze the HTML/text content to find a real email address.
3. First try to find the email in the footer of the website.
4. If no email is found, say: Final Answer: No valid email found.
5. If you find a real contact email, respond in this format:

Final Answer: contact@realcompany.com

Do NOT make up or guess emails. Only return what you actually see.

IMPORTANT: Do not return placeholder emails like contact@email.com or info@example.com unless you are 100% sure it's in the HTML.
"""

    try:
        result = agent.run(prompt)
    except Exception as e:
        return None

    # Extract email from the agent's final answer
    match = re.search(r"Final Answer:\s*(.+@.+\..+)", result)
    if match:
        email = match.group(1).strip()
        if is_valid_email(email):
            return email

    return None  # fallback if nothing valid was found