from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Epic(Base):
    __tablename__ = "epics"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"))
    title = Column(String)
    order = Column(Integer)

    milestone = relationship("Milestone", back_populates="epics")
    tasks = relationship("Task", back_populates="epic", cascade="all, delete-orphan")