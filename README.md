# AI-PM-SYSTEM — AI Project Management Planner System Engine

AI-PM-SYSTEM is an intelligent, automated project planning, task decomposition, and team assignment system built. 

The system maps out structural software roadmaps from raw descriptions, extracts developer skills from professional documents, and relies on an algorithmic optimization matrix to balance workloads and automatically assign the right engineers to the right tasks.

---

## 📂 System Architecture

```text
AI-PM-SYSTEM/
│
├── app/
│   ├── models/                # Relational Database Schema Layers
│   │   ├── epic.py
│   │   ├── milestone.py
│   │   ├── project.py         # Main project, employee, and assignment structural models
│   │   └── task.py
│   │
│   ├── planner/               # Core business logic and routing paths
│   │   ├── matching_service.py# Algorithmic scoring matrices for talent mapping
│   │   ├── resume_service.py  # Resume text extraction and analysis pipelines
│   │   ├── router.py          # API Endpoints & Request-Response mappings
│   │   ├── schemas.py         # Pydantic data modeling contracts & JSON schemas
│   │   └── service.py         # Main structural planning orchestration engine
│   │
│   ├── db.py                  # Core SQLAlchemy engines & database session setup
│   ├── llm_client.py          # Unified network execution layer with retry logic
│   └── main.py                # Server initialization, CORS validation, & entry point
│
├── frontend/                  # Presentation layer
│   └── index.html             # Client-side user interface view
│
├── temp_uploads/              # Temporary file cache directory for uploaded resumes
└── .env                       # Local secrets management (Active API Keys)