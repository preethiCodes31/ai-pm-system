from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    epic_id = Column(Integer, ForeignKey("epics.id"))
    title = Column(String)
    description = Column(String)
    order = Column(Integer)

    epic = relationship("Epic", back_populates="tasks")