from langgraph import Graph, Node
from services.hunter import get_contacts
from db.pinecone import embed_interests, upsert_lead, search_businesses
from db.supabase import fetch_all_businesses
from langchain import OpenAI
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define nodes
class ReceiveLead(Node):
    def run(self, domain: str, basic_info: dict):
        return {'domain': domain, 'basic_info': basic_info}

class EnrichLead(Node):
    def run(self, domain: str):
        contacts = get_contacts(domain)
        return {'contacts': contacts}

class EmbedAndScore(Node):
    def run(self, interests: list):
        embedding = embed_interests(interests)
        upsert_lead('lead_id', interests)
        return {'embedding': embedding}

class QuerySupabase(Node):
    def run(self):
        businesses = fetch_all_businesses()
        return {'businesses': businesses}

class GenerateMessage(Node):
    def run(self, lead_info: dict, businesses: list):
        # Use LangChain and OpenAI to generate a personalized message
        prompt = f"Generate a personalized message for {lead_info['name']}"
        response = client.responses.create(
            model="gpt-4o",
            input=prompt
        )
        return {'message': response.output_text}

# Create the graph
leadflow_graph = Graph([
    ReceiveLead(),
    EnrichLead(),
    EmbedAndScore(),
    QuerySupabase(),
    GenerateMessage()
]) 