from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import datetime
from pydantic import field_validator, model_validator

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
    pain_points: Optional[str] = ""
    @field_validator("pain_points", mode="before")
    @classmethod
    def ensure_string(cls, v):
        if isinstance(v, list):
            return "; ".join(v)
        return str(v) if v is not None else ""
    @model_validator(mode="after")
    def ensure_pain_points_is_string(self):
        # Ensures final output is always a string even if field got bypassed
        if isinstance(self.pain_points, list):
            self.pain_points = "; ".join(self.pain_points)
        return self
    outreach_email: Optional[str] = "None"

class AppState(BaseModel):
    search_query: str
    businesses: Optional[List[Business]] = []
    max_links: int

class Interaction(BaseModel):
    lead_id: int
    business_id: int
    status: constr(min_length=1)
    timestamp: datetime 