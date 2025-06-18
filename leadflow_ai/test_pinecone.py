import asyncio
from db.pinecone import embed_interests, upsert_lead, search_businesses

async def test_pinecone():
    # Test embedding and upserting a lead
    lead_id = "lead_123"
    interests = ["AI", "Machine Learning", "Data Science"]
    await upsert_lead(lead_id, interests)
    print(f"Upserted lead {lead_id} with interests: {interests}")

    # Test searching for businesses
    query_interests = ["AI", "Data Analysis"]
    results = await search_businesses(query_interests)
    print("Search results for businesses:", results)

# Run the test
asyncio.run(test_pinecone())
