from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    order = Column(Integer)

    project = relationship("Project", back_populates="milestones")
    epics = relationship("Epic", back_populates="milestone", cascade="all, delete-orphan")