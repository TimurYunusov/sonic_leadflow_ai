from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from services.playwright_fetcher import fetch_page_html

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

tools = [
    Tool(
        name="fetch_page_html",
        func=fetch_page_html,
        description="Use this tool to fetch the HTML content of a page. Input must be a full URL like https://site.com/contact."
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

def find_email_for_website(domain: str):
    prompt = f"""
You're a web research agent. Your ONLY task is to extract a contact email from {domain}.

You can use the tool `fetch_page_html` to load any subpage like /contact or /about.

Respond ONLY using:
Thought: ...
Action: fetch_page_html
Action Input: "https://..."

Or to finish:
Final Answer: contact@email.com
"""
    return agent.run(prompt)

