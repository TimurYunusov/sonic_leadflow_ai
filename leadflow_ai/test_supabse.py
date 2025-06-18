import asyncio
from db.supabase import create_supabase, insert_lead, fetch_all_businesses, update_interaction_status

async def test_supabase():
    supabase = await create_supabase()

    # Test inserting a new lead
    lead_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "company": "Example Corp",
        "domain": "example.com",
        "zip": "12345",
        "interests": ["AI", "ML"],
        "source": "website"
    }
    new_lead = await insert_lead(supabase, lead_data)
    print("Inserted Lead:", new_lead)

    # Test fetching all businesses
    businesses = await fetch_all_businesses(supabase)
    print("Businesses:", businesses)

    # Test updating interaction status
    if businesses:
        interaction_id = 1  # Assuming an interaction with this ID exists
        new_status = "Contacted"
        updated_interaction = await update_interaction_status(supabase, interaction_id, new_status)
        print("Updated Interaction:", updated_interaction)

# Run the test
asyncio.run(test_supabase())
