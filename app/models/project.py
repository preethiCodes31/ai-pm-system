from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from app.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    duration_months = Column(Integer)
    team_size = Column(Integer)
    tech_stack = Column(String)  # Stored as a comma-separated string locally

    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    years_experience = Column(Float, nullable=True)
    education = Column(String, nullable=True)          
    certifications = Column(String, nullable=True)     
    previous_companies = Column(String, nullable=True) 
    languages = Column(String, nullable=True)          
    skills = Column(String, nullable=True)             
    needs_review = Column(Boolean, default=False)      

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, index=True)
    employee_id = Column(Integer, index=True)
    status = Column(String, default="suggested") # "suggested" | "confirmed" | "rejected"