from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import datetime

class Lead(BaseModel):
    id: int
    name: constr(min_length=1)
    email: EmailStr
    company: Optional[str]
    domain: Optional[str]
    zip: Optional[constr(min_length=5, max_length=10)]
    interests: Optional[List[str]]
    source: Optional[str]

class Business(BaseModel):
    name: str
    location: str
    website: str
    url: str
    email: Optional[str] = None
    summary: Optional[str] = None
    pain_points: Optional[str] = None
    outreach_email: Optional[str] = None

class AppState(BaseModel):
    search_query: str
    businesses: Optional[List[Business]] = []
    max_links: int

class Interaction(BaseModel):
    lead_id: int
    business_id: int
    status: constr(min_length=1)
    timestamp: datetime 