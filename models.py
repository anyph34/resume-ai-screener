from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text)
    min_experience_years = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    filename = Column(String(200), nullable=False)
    extracted_text = Column(Text, nullable=False)
    email = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
