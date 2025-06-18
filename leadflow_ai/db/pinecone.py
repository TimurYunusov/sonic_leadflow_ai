import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from typing import List, Dict

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Create an instance of the Pinecone class
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = 'leads'

# Ensure the index exists
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Correct dimension for text-embedding-3-small
        metric='cosine',  # or 'euclidean', depending on your use case
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'  # Change to a valid AWS region
        )
    )

# Use the Index method from the Pinecone instance
index = pc.Index(index_name)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

async def embed_interests(interests: List[str]) -> List[float]:
    # Combine interests into a single string
    combined_text = ' '.join(interests)
    return get_embedding(combined_text)

async def upsert_lead(lead_id: str, interests: List[str]):
    embedding = await embed_interests(interests)
    index.upsert([(lead_id, embedding)])

async def search_businesses(query_interests: List[str], top_k: int = 5) -> List[Dict]:
    query_embedding = await embed_interests(query_interests)
    results = index.query(vector=query_embedding, top_k=top_k, include_values=True)
    return results