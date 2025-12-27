from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    region = Column(String)
    country = Column(String)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    team_size = Column(Integer)
    total_funding = Column(Float)
    last_funding_amount = Column(Float)
    last_funding_date = Column(DateTime)
    funding_stage = Column(String)
    hiring_probability = Column(Float)
    confidence = Column(String)
    prediction_label = Column(String)
    status = Column(String)
    status_reason = Column(String)
    funding_recency = Column(Integer)
    tech_churn = Column(Float)
    job_post_velocity = Column(Float)
    region_factor = Column(Float)
    senior_departures = Column(Integer)
    current_month_posts = Column(Integer)
    website = Column(String)
    description = Column(String)
    predicted_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
