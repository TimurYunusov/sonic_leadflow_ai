import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# Create an instance of the Pinecone class
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = 'leads'

# Delete the existing index if it exists
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

# Create the index with the correct dimension
pc.create_index(
    name=index_name,
    dimension=1536,  # Correct dimension for text-embedding-ada-002
    metric='cosine',  # or 'euclidean', depending on your use case
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'  # Change to a valid AWS region
    )
)

print("Available indexes:", pc.list_indexes().names()) 