# 🚀 ai-pm-system
  
> Decomposing high-level project scopes into clear implementation tasks and matching them with verified candidate skill profiles in real time.

---

## 📌 Overview

**ai-pm-system** is an end-to-end, AI-powered project management engine designed to streamline project planning and team allocation. By leveraging **Meta Llama 3.3 70B via Groq**, the platform converts high-level project descriptions into structured, actionable implementation trees (Milestones ➔ Epics ➔ Sub-tasks) and automatically evaluates candidate suitability using an algorithmic matching engine.

---

## ✨ Key Features

* **🤖 Autonomous Project Decomposition:** Dynamically breaks down broad project goals into milestones, epics, estimated hourly workloads, and required skills using Groq Llama 3.3 70B.
* **📄 Smart Resume Parsing:** Ingests candidate resumes (`.pdf`, `.docx`) using `pdfplumber` to extract skills, experience levels, and domain expertise.
* **🎯 Algorithmic Candidate Matching:** Evaluates talent suitability per task based on skill overlap, capacity, and historical experience scores.
* **🖥️ Interactive Dark SaaS Dashboard:** Modern glassmorphism UI built with React and Tailwind CSS for real-time visualization of task breakdown and candidate assignments.
* **🔒 Privacy & Security:** Built-in safeguards ensuring API keys (`.env`) and local runtime databases (`sql_app.db`) remain protected and excluded from version control.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **LLM Engine** | Meta Llama 3.3 70B (via Groq API) | Dynamic JSON task generation & skill breakdown |
| **Backend API** | Python 3.10+ / FastAPI / SQLAlchemy | REST API, database persistence, and service orchestration |
| **Resume Ingestion** | `pdfplumber` / `python-docx` | Structured document parsing & skill extraction |
| **Frontend UI** | React (CDN) + Tailwind CSS | Responsive, interactive dark-mode dashboard |
| **Database** | SQLite (Dev) / PostgreSQL-ready | Local persistence for projects, tasks, and talent pool |

---

## 📂 Project Structure

```text
AI-PM-SYSTEM/
├── .venv/                 # Python virtual environment
├── app/
│   ├── models/            # SQLAlchemy Database Models
│   │   ├── epic.py
│   │   ├── milestone.py
│   │   ├── project.py
│   │   └── task.py
│   ├── planner/           # Core Orchestration & Matching Services
│   │   ├── matching_service.py
│   │   ├── resume_service.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── db.py              # Database configuration & session initialization
│   ├── llm_client.py     # Groq API client with JSON schema validation
│   └── main.py            # FastAPI entry point & middleware setup
├── frontend/
│   ├── index.html         # React + Tailwind SaaS dashboard UI
│   └── temp_uploads/      # Temporary candidate resume storage
├── .env                   # Environment variables & API keys (Git ignored)
├── .gitignore             # Version control exclusion rules
├── requirements.txt       # Python dependencies list
└── README.md              # Project documentation
```
