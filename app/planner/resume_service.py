import pdfplumber
from docx import Document
import json
from sqlalchemy.orm import Session
from app.planner.schemas import ResumeOut
from app.models.project import Employee
from app.llm_client import call_llm_json_with_retry

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type")

def parse_resume(raw_text: str) -> ResumeOut:
    truncated_text = raw_text[:4000] 
    system_prompt = f"Extract structured data from this resume. Return ONLY JSON matching: {json.dumps(ResumeOut.model_json_schema())}"
    return call_llm_json_with_retry(system_prompt, truncated_text, ResumeOut)

def save_employee_to_db(db: Session, profile: ResumeOut) -> Employee:
    review_flag = len(profile.skills) == 0
    db_employee = Employee(
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        years_experience=profile.years_experience,
        education=", ".join(profile.education),
        certifications=", ".join(profile.certifications),
        previous_companies=", ".join(profile.previous_companies),
        languages=", ".join(profile.languages),
        skills=", ".join(profile.skills),
        needs_review=review_flag
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee