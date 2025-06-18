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
    id: int
    name: constr(min_length=1)
    domain: Optional[str]
    size: Optional[int]
    location: Optional[str]

class Interaction(BaseModel):
    lead_id: int
    business_id: int
    status: constr(min_length=1)
    timestamp: datetime 