import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from leadflow_ai.api.routes import router as lead_router
from leadflow_ai.schemas.lead import AppState
from langgraph.graph import StateGraph, START, END
from leadflow_ai.agents.email_finder_agent import find_email_for_website_with_llm
from leadflow_ai.services.scrape_gogglemaps import scrape_google_maps_node
from leadflow_ai.services.email_finder_tool import update_business_emails
from leadflow_ai.services.summirize_business_and_pain_points import summarize_business
from leadflow_ai.services.generate_outreach_email import generate_outreach_email_node
import logging
import os
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# Initialize the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Your Next.js dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
# Include the router
app.include_router(lead_router)

# Define a root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to the LeadFlow API"} 
class PipelineRequest(BaseModel):
    search_query: str
    max_links: int = 10

@app.post("/run-leadflow-pipeline")
async def run_leadflow_pipeline(request: PipelineRequest):
    state = AppState(search_query=request.search_query, max_links=request.max_links)
    builder = StateGraph(AppState)
    builder.add_node("scrape_google_maps_node", scrape_google_maps_node)
    builder.add_node("update_business_emails", update_business_emails)
    builder.set_entry_point("scrape_google_maps_node")
    builder.add_edge("scrape_google_maps_node", "update_business_emails")
    builder.add_node("summarize_business", summarize_business)
    builder.add_edge("update_business_emails", "summarize_business")
    builder.add_node("generate_outreach_email", generate_outreach_email_node)
    builder.add_edge("summarize_business", "generate_outreach_email")
    builder.add_edge("generate_outreach_email", END)
    graph = builder.compile()
    results = await graph.ainvoke(state)
    # For serialization, convert businesses to dict
    results["businesses"] = [b.model_dump() if hasattr(b, "model_dump") else b.__dict__ for b in results["businesses"]]
    return results



#   uvicorn leadflow_ai.api.main:app --reload

    

if __name__ == "__main__":
    state = AppState(search_query="technology companies in South Loop Chicago", max_links=10)
    builder = StateGraph(AppState)
    builder.add_node("scrape_google_maps_node", scrape_google_maps_node)
    builder.add_node("update_business_emails", update_business_emails)
    builder.set_entry_point("scrape_google_maps_node")
    builder.add_edge("scrape_google_maps_node", "update_business_emails")
    builder.add_node("summarize_business", summarize_business)
    builder.add_edge("update_business_emails", "summarize_business")
    builder.add_node("generate_outreach_email", generate_outreach_email_node)
    builder.add_edge("summarize_business", "generate_outreach_email")
    builder.add_edge("generate_outreach_email", END)

    # builder.add_edge("update_business_emails", END)
    graph = builder.compile()

    # Run the graph
    results = asyncio.run(graph.ainvoke(state))
    
    logging.info(f"Results: {results}")
   
    logging.info("Results saved to state memory")