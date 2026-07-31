import os
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import database engine & models
from app.db import engine, Base
import app.models.project
import app.models.milestone
import app.models.epic
import app.models.task
from app.planner.router import router as planner_router

# 1. Load environment variables
load_dotenv()

# 2. Create database tables
Base.metadata.create_all(bind=engine)

# 3. Initialize FastAPI ONCE at the top
app = FastAPI(title="AI Project Management Planner System Engine")

# 4. Add CORS Middleware to the initialized app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Include backend API routers
app.include_router(planner_router)

# 6. Mount static frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 7. Routes for serving frontend & health checks
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health_check():
    return {"status": "operational"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)