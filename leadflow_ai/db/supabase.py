import os
from supabase._async.client import AsyncClient as Client, create_client
from dotenv import load_dotenv
from typing import List

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

async def create_supabase() -> Client:
    return await create_client(SUPABASE_URL, SUPABASE_KEY)

async def insert_lead(supabase: Client, lead_data: dict) -> dict:
    response = await supabase.table('leads').insert(lead_data).execute()
    return response.data

async def fetch_all_businesses(supabase: Client) -> List[dict]:
    response = await supabase.table('businesses').select('*').execute()
    return response.data

async def update_interaction_status(supabase: Client, interaction_id: int, new_status: str) -> dict:
    response = await supabase.table('interactions').update({'status': new_status}).eq('id', interaction_id).execute()
    return response.data 