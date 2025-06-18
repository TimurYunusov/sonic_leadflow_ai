from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.hunter import get_contacts
from ..db.supabase import create_supabase, insert_lead
import asyncio

# Define the data model for the lead
class Lead(BaseModel):
    name: str
    domain: str
    zip: str
    interests: list[str]

# Initialize the router
router = APIRouter()

# Define the POST endpoint
@router.post("/ingest-lead")
async def ingest_lead(lead: Lead):
    # Use Hunter.io to find contacts
    contacts = get_contacts(lead.domain)
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")

    # Connect to Supabase
    supabase = await create_supabase()

    # Insert contacts into Supabase
    for contact in contacts:
        lead_data = {
            "name": contact['full_name'],
            "email": contact['email'],
            "position": contact['position'],
            "confidence": contact['confidence'],
            "domain": lead.domain,
            "zip": lead.zip,
            "interests": lead.interests
        }
        await insert_lead(supabase, lead_data)

    # Return a success message
    return {"message": "Leads ingested successfully", "matched_business": lead.domain} 