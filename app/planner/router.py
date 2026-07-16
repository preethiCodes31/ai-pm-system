from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os

from app.db import get_db
from app.models.project import Project, Employee, Assignment
from app.models.task import Task
from app.models.milestone import Milestone
from app.models.epic import Epic

from app.planner import service, matching_service
from app.planner.schemas import (
    FullProjectTreeOut,
    TaskMatchResponse,
    AssignmentUpdateIn
)

router = APIRouter(prefix="/projects", tags=["Project Planner"])

# ==========================================
# MODULE 2 — PROJECT PLAN GENERATOR ROUTES
# ==========================================

@router.post("/create-project")
def create_project(description: str, duration_months: int, team_size: int, tech_stack: str, db: Session = Depends(get_db)):
    new_project = Project(
        description=description,
        duration_months=duration_months,
        team_size=team_size,
        tech_stack=tech_stack
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.post("/{project_id}/generate-plan")
def generate_project_plan(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        tech_list = [t.strip() for t in project.tech_stack.split(",")] if project.tech_stack else []
        
        plan = service.generate_plan(
            description=project.description,
            duration_months=project.duration_months,
            team_size=project.team_size,
            tech_stack=tech_list
        )
        
        result = service.save_plan_to_db(db, plan, project_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate structured plan: {str(e)}")

# ==========================================
# MODULE 3 — GRANULAR AI TASK GENERATOR ROUTES
# ==========================================

@router.post("/epics/{epic_id}/generate-tasks")
def generate_epic_tasks(epic_id: int, db: Session = Depends(get_db)):
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic target context not found")
        
    try:
        result = service.generate_tasks_for_epic(db, epic_id=epic_id)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result.get("message"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate granulated epic task tree: {str(e)}")

# ==========================================
# MODULE 4 — RESUME PARSER MULTIPART ROUTES
# ==========================================

@router.post("/create-employee")
def create_employee(name: str, skills: str, db: Session = Depends(get_db)):
    new_employee = Employee(
        name=name,
        skills=skills,
        needs_review=False
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.post("/employees/upload-resume")
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
            
        raw_text = service.extract_text(file_path)
        parsed_profile = service.parse_resume(raw_text)
        
        should_review = len(parsed_profile.skills) == 0
        
        # Format lists into strings for DB storage
        formatted_education = ", ".join(parsed_profile.education) if parsed_profile.education else None
        formatted_certifications = ", ".join(parsed_profile.certifications) if parsed_profile.certifications else None
        formatted_companies = ", ".join(parsed_profile.previous_companies) if parsed_profile.previous_companies else None
        formatted_languages = ", ".join(parsed_profile.languages) if parsed_profile.languages else None
        formatted_skills = ", ".join(parsed_profile.skills) if parsed_profile.skills else None

        # Check if an employee with this email already exists to prevent UNIQUE crashes
        existing_employee = None
        if parsed_profile.email:
            existing_employee = db.query(Employee).filter(Employee.email == parsed_profile.email).first()

        if existing_employee:
            # Upsert: Update fields of the existing candidate profile record
            existing_employee.name = parsed_profile.name
            existing_employee.phone = parsed_profile.phone
            existing_employee.years_experience = parsed_profile.years_experience
            existing_employee.education = formatted_education
            existing_employee.certifications = formatted_certifications
            existing_employee.previous_companies = formatted_companies
            existing_employee.languages = formatted_languages
            existing_employee.skills = formatted_skills
            existing_employee.needs_review = should_review
            
            db.commit()
            db.refresh(existing_employee)
            db_employee = existing_employee
        else:
            # Standard Insert: Build a new candidate row 
            db_employee = Employee(
                name=parsed_profile.name,
                email=parsed_profile.email,
                phone=parsed_profile.phone,
                years_experience=parsed_profile.years_experience,
                education=formatted_education,
                certifications=formatted_certifications,
                previous_companies=formatted_companies,
                languages=formatted_languages,
                skills=formatted_skills,
                needs_review=should_review
            )
            db.add(db_employee)
            db.commit()
            db.refresh(db_employee)
        
        return {
            "status": "success",
            "employee_id": db_employee.id,
            "name": db_employee.name,
            "skills_extracted": parsed_profile.skills,
            "needs_review_flag": db_employee.needs_review
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ==========================================
# MODULE 5 — SEMANTIC MATCHING ENGINE ROUTES
# ==========================================

@router.post("/tasks/{task_id}/match", response_model=TaskMatchResponse)
def match_task_to_employees(task_id: int, top_n: int = 3, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task context target not found")
        
    t_skills = []
    
    # 1. First, try to read explicit skills/tech attributes if they exist on your Task model
    for attr in ["skills", "required_skills", "tech_stack"]:
        if hasattr(task, attr) and getattr(task, attr):
            val = getattr(task, attr)
            if isinstance(val, str):
                t_skills.extend([s.strip() for s in val.split(",") if s.strip()])
            elif isinstance(val, list):
                t_skills.extend(val)

    # 2. If no explicit skill fields exist, break the title & description into individual clean keywords
    if not t_skills:
        raw_text = f"{task.title or ''} {task.description or ''}"
        # Clean common filler words to extract actual tech keywords
        words = raw_text.replace(".", "").replace(",", "").replace(";", "").split()
        stop_words = {"and", "the", "set", "up", "for", "with", "core", "baseline", "structures", "database", "engine", "directory", "project", "layout"}
        t_skills = [w.strip() for w in words if w.lower().strip() not in stop_words and len(w) > 2]

    employees = db.query(Employee).all()
    candidates = []
    
    for emp in employees:
        emp_skills = [s.strip() for s in emp.skills.split(",")] if emp.skills else []
        
        avail_score, workload_hours = matching_service.calculate_availability_score(db, emp.id)
        
        s = matching_service.skill_match_score(t_skills, emp_skills)
        e = matching_service.experience_score(emp.years_experience)
        p = matching_service.past_project_similarity(emp.id, task.id)
        
        final = matching_service.calculate_final_score(s, e, avail_score, p)
        candidates.append({
            "employee_id": emp.id,
            "name": emp.name,
            "workload_hours": workload_hours,
            "final_score": final,
            "score_breakdown": {
                "skill_match": s,
                "experience": e,
                "availability_score": avail_score,
                "past_similarity": p
            }
        })
        
    candidates.sort(key=lambda x: x["final_score"], reverse=True)
    top_picks = candidates[:top_n]
    
    if top_picks:
        best_pick = top_picks[0]
        db.query(Assignment).filter(Assignment.task_id == task_id).delete()
        
        assignment = Assignment(task_id=task_id, employee_id=best_pick["employee_id"], status="suggested")
        db.add(assignment)
        db.commit()
        
    return {"task_id": task_id, "top_candidates": top_picks}

@router.patch("/assignments/{assignment_id}")
def update_assignment_status(assignment_id: int, payload: AssignmentUpdateIn, db: Session = Depends(get_db)):
    if payload.status not in ["confirmed", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid target assignment state action status")
        
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment reference record not found")
        
    assignment.status = payload.status
    db.commit()
    return {"status": "updated", "assignment_id": assignment_id, "new_status": payload.status}

# ==========================================
# MODULE 6 — MASTER TREE ORCHESTRATION ROUTE
# ==========================================

@router.post("/{project_id}/orchestrate", response_model=FullProjectTreeOut)
def trigger_full_project_pipeline(project_id: int, db: Session = Depends(get_db)):
    result = service.orchestrate_full_pipeline(db, project_id=project_id)
    if isinstance(result, dict) and result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result