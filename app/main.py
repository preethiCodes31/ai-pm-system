from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine, Base
from app.planner.router import router as planner_router

import app.models.project
import app.models.milestone
import app.models.epic
import app.models.task
import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Force load the .env file from the current working directory
load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Project Management Planner System Engine")

# Configure CORS Middleware to accept requests from local browser file paths
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows the 'null' origin from file:// paths
    allow_credentials=True,  # Required to be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(planner_router)

@app.get("/")
def health_check():
    return {"status": "operational"}