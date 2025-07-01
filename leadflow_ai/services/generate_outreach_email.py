import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from leadflow_ai.schemas.lead import AppState
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def generate_outreach_email_node(state: AppState) -> dict:
    for business in state.businesses:
        if business.summary and business.pain_points:
            
            business.outreach_email = await generate_outreach_email(
                business.summary,
                business.pain_points,
                business.name
            )
            logging.info(f"Outreach email generated for {business.name}: {business.outreach_email}")
    return {"businesses": state.businesses}

outreach_prompt = PromptTemplate.from_template("""
You are a top-tier sales copywriter for **Sonic Wave Lounge**, a premium wellness studio in South Loop, Chicago.  
Your goal is to **craft a short, persuasive cold outreach email** to the business **{biz_name}**, based on their summary and challenges.

---  
 **Context for Personalization**  
Here is what we know about the business:  
Business Summary:  
{summary}  

Pain Points:  
{pain_points}  

---  
 **Sonic Wave Lounge Offering**  
We help busy teams reduce stress, prevent burnout, and increase clarity in just minutes using **Shiftwave Therapy** — a zero-gravity chair experience that combines guided breathwork, biofeedback, and vibrational stimulation to reset the nervous system.  

- Fast, drug-free relief from stress and screen fatigue  
- Enhances recovery, focus, and emotional regulation  
- Used by high-stress professionals and wellness-forward companies  
- On-site or in-studio — with a **free 10-minute trial** for new partners  

---  
 **Email Writing Instructions**  
- Start with a **hook** that acknowledges the business or team's likely challenge  
- Tie one or two pain points to **Shiftwave's specific benefits**  
- Clearly explain the **offer** and how it helps *them*  
- Include **light social proof** (e.g., "used by teams like yours" or "already helping local businesses")  
- End with a **concise CTA** (e.g., book a call, try a demo)  
- Keep tone friendly, clear, and confident (not too salesy)  
- Length: 4 short paragraphs max  
- Respond only with the email body (no greeting or signature)  
""")


async def generate_outreach_email(summary: str, pain_points: str, biz_name: str) -> str:
    prompt = outreach_prompt.format(
        summary=summary,
        pain_points=pain_points,
        biz_name=biz_name
    )
    response = await llm.ainvoke(prompt)
    return response.content if hasattr(response, "content") else str(response)
