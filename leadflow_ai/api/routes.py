from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.hunter import get_contacts
from ..db.supabase import create_supabase, insert_lead, insert_local_target
from ..services.enrichment import enrich_target
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Set the logging level for httpx and httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("hpack").setLevel(logging.WARNING)  # For hpack logs

# Optionally, set the logging level for your entire application
logging.basicConfig(level=logging.WARNING)

# Define the data model for the discover request
class DiscoverRequest(BaseModel):
    location: str
    radius: float

# Define the data model for the lead
class Lead(BaseModel):
    name: str
    domain: str
    zip: str
    interests: list[str]

# Initialize the router
router = APIRouter()

# Define the POST endpoint
@router.post("/discover")
async def discover_location(request: DiscoverRequest):
    # Step 1: Geocode using Nominatim
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={request.location}&format=json"
    headers = {"User-Agent": os.getenv("USER_AGENT", "my-app")}
    async with aiohttp.ClientSession() as session:
        async with session.get(nominatim_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Error accessing Nominatim API")
            geocode_data = await response.json()
            if not geocode_data:
                raise HTTPException(status_code=404, detail="Location not found")
            lat = geocode_data[0]['lat']
            lon = geocode_data[0]['lon']
            logging.debug(f'Geocoded lat/lon: {lat}, {lon}')

    # Step 2: Query Overpass API
    radius_m = request.radius * 1609.34
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node[\"office\"](around:{radius_m},{lat},{lon});
      node[\"amenity\"=\"coworking_space\"](around:{radius_m},{lat},{lon});
      way[\"building\"=\"apartments\"](around:{radius_m},{lat},{lon});
      way[\"amenity\"=\"coworking_space\"](around:{radius_m},{lat},{lon});
      way[\"hotel\"=\"hotel\"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    async with aiohttp.ClientSession() as session:
        async with session.post(overpass_url, data=overpass_query, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Error accessing Overpass API")
            overpass_data = await response.json()

    # Step 3: Normalize the response
    results = []
    for element in overpass_data['elements']:
        name = element.get('tags', {}).get('name', 'Unknown')
        address = element.get('tags', {}).get('addr:full', 'Unknown')
        lat = element.get('lat', element.get('center', {}).get('lat', 0))
        lon = element.get('lon', element.get('center', {}).get('lon', 0))
        if lat and lon:
            target = {
                "name": name,
                "type": element.get('tags', {}).get('amenity', 'office'),
                "address": address,
                "lat": lat,
                "lng": lon,
                "source": "overpass"
            }
            # Log the target before enrichment
            logging.info(f"Enriching target: {target}")
            try:
                # Enrich target and get enriched data
                enriched_target = await enrich_target(target)
            except Exception as e:
                logging.warning(f"Enrichment failed, using fallback address: {e}")
                enriched_target = target  # fallback to original

            # Log enriched data before insert
            logging.info(f"Inserting enriched target: {enriched_target}")

            # Insert enriched data into Supabase
            supabase = await create_supabase()
            await insert_local_target(supabase, {
                "name": enriched_target['name'],
                "address": enriched_target['address'],
                "lat": enriched_target['lat'],
                "lng": enriched_target['lng'],
                "type": enriched_target['type'],
                "source": enriched_target['source'],
                "unique_hash": hash((enriched_target['name'], enriched_target['lat'], enriched_target['lng']))
            })

            results.append(enriched_target)

    # Step 5: Return the results as JSON
    return results

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