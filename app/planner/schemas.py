from pydantic import BaseModel
from typing import List
from typing import Optional, List
from typing import List, Dict, Any, Optional




class TaskOut(BaseModel):
    title: str
    description: str

class EpicOut(BaseModel):
    title: str
    tasks: List[TaskOut]

class MilestoneOut(BaseModel):
    title: str
    epics: List[EpicOut]

class ProjectPlanOut(BaseModel):
    milestones: List[MilestoneOut]

# Keep your existing TaskOut, EpicOut, MilestoneOut, ProjectPlanOut here...

class DetailedTaskOut(BaseModel):
    title: str
    description: str
    priority: str  # "Low" | "Medium" | "High"
    estimated_hours: float
    story_points: int
    required_skills: List[str]
    dependencies: List[str]  # Titles of other tasks in this epic it depends on

class TaskListOut(BaseModel):
    tasks: List[DetailedTaskOut]

class ResumeOut(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    years_experience: Optional[float] = None
    education: List[str]
    certifications: List[str]
    previous_companies: List[str]
    languages: List[str]



class DetailedTaskOut(BaseModel):
    title: str
    description: str
    priority: str  # "Low" | "Medium" | "High"
    estimated_hours: float
    story_points: int
    required_skills: List[str]
    dependencies: List[str]

class TaskListOut(BaseModel):
    tasks: List[DetailedTaskOut]


class ResumeOut(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    years_experience: Optional[float] = None
    education: List[str]
    certifications: List[str]
    previous_companies: List[str]
    languages: List[str]



class MatchScoreBreakdown(BaseModel):
    skill_match: float
    experience: float
    availability_score: float
    past_similarity: float

class CandidateMatchOut(BaseModel):
    employee_id: int
    name: str
    workload_hours: float
    final_score: float
    score_breakdown: MatchScoreBreakdown

class TaskMatchResponse(BaseModel):
    task_id: int
    top_candidates: List[CandidateMatchOut]

class AssignmentUpdateIn(BaseModel):
    status: str  # "confirmed" | "rejected"



class OrchestratedTaskOut(BaseModel):
    id: int
    title: str
    description: str
    order: int
    suggested_assignee: Optional[CandidateMatchOut] = None

class OrchestratedEpicOut(BaseModel):
    id: int
    title: str
    order: int
    tasks: List[OrchestratedTaskOut]

class OrchestratedMilestoneOut(BaseModel):
    id: int
    title: str
    order: int
    epics: List[OrchestratedEpicOut]

class FullProjectTreeOut(BaseModel):
    project_id: int
    title: str
    milestones: List[OrchestratedMilestoneOut]