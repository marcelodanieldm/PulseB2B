from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanySchema(BaseModel):
    id: Optional[int]
    name: str
    region: Optional[str]
    country: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    team_size: Optional[int]
    total_funding: Optional[float]
    last_funding_amount: Optional[float]
    last_funding_date: Optional[datetime]
    funding_stage: Optional[str]
    hiring_probability: Optional[float]
    confidence: Optional[str]
    prediction_label: Optional[str]
    status: Optional[str]
    status_reason: Optional[str]
    funding_recency: Optional[int]
    tech_churn: Optional[float]
    job_post_velocity: Optional[float]
    region_factor: Optional[float]
    senior_departures: Optional[int]
    current_month_posts: Optional[int]
    website: Optional[str]
    description: Optional[str]
    predicted_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True
