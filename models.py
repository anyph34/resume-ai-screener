from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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
    matches = relationship("Match", back_populates="job")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    filename = Column(String(200), nullable=False)
    extracted_text = Column(Text, nullable=False)
    email = Column(String(100))
    word_count = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    matches = relationship("Match", back_populates="resume")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    similarity_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("Job", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
