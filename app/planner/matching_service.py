import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models.project import Employee, Assignment
from app.models.task import Task

# Initialize the lightweight embedding model (caches locally on first run)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Simple in-memory embedding cache to avoid recomputing the same skill strings
_embedding_cache = {}

def get_embedding(text: str):
    clean_text = text.lower().strip()
    if clean_text not in _embedding_cache:
        _embedding_cache[clean_text] = embedding_model.encode(clean_text)
    return _embedding_cache[clean_text]

def cosine_sim(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def skill_match_score(task_skills: list[str], employee_skills: list[str]) -> float:
    if not task_skills or not employee_skills:
        return 0.0
        
    task_vecs = [get_embedding(s) for s in task_skills]
    emp_vecs = [get_embedding(s) for s in employee_skills]
    
    per_skill_scores = []
    for tv in task_vecs:
        # Find the best semantic vector match in the candidate's pool
        best = max((cosine_sim(tv, ev) for ev in emp_vecs), default=0.0)
        
        # Apply a critical threshold filter: 
        # If the skill similarity is below 0.75, it's a weak match—penalize it.
        if best < 0.75:
            best = best * 0.1  # Aggressively drag weak matches down to prevent default winning
            
        per_skill_scores.append(best)
        
    return sum(per_skill_scores) / len(per_skill_scores)

def experience_score(employee_years: float, cap: float = 10.0) -> float:
    years = employee_years if employee_years is not None else 0.0
    return min(years / cap, 1.0)

def availability_score(workload_hours: float, capacity: float = 40.0) -> float:
    # More workload means lower availability score
    if workload_hours >= capacity:
        return 0.0
    return (capacity - workload_hours) / capacity

def calculate_availability_score(db: Session, employee_id: int, capacity: float = 40.0) -> tuple[float, float]:
    """
    Queries the DB for the employee's active assigned task hours,
    calculates their workload, and returns (availability_score, workload_hours).
    """
    # Sum the estimated hours of all active assignments for this employee
    active_assignments = (
        db.query(Assignment)
        .filter(Assignment.employee_id == employee_id)
        .all()
    )
    
    workload_hours = 0.0
    for assignment in active_assignments:
        # Fetch the associated task
        task = db.query(Task).filter(Task.id == assignment.task_id).first()
        if task:
            # Dynamically check for 'duration_hours' or 'estimated_hours'
            hours = getattr(task, "duration_hours", None) or getattr(task, "estimated_hours", None) or 0.0
            workload_hours += float(hours)
            
    # Compute the 0.0 - 1.0 score using your existing availability_score logic
    score = availability_score(workload_hours, capacity)
    
    return score, workload_hours

def past_project_similarity(employee_id: int, task_id: int) -> float:
    return 0.5

def calculate_final_score(skill: float, experience: float, availability: float, past_similarity: float) -> float:
    return (0.50 * skill) + (0.20 * experience) + (0.15 * availability) + (0.15 * past_similarity)