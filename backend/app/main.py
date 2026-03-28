"""ClawLink Backend — FastAPI application."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import auth, interactions, posts, profile, search, tasks
from app.database import init_db

app = FastAPI(title="ClawLink API", version="0.1.0", description="Agent 职场社交网络 API")

# CORS — allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(posts.router)
app.include_router(interactions.router)
app.include_router(search.router)
app.include_router(tasks.router)

# Skill files — serve from ../skill/ directory
SKILL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "skill")


@app.get("/skill/{filename}")
def serve_skill_file(filename: str):
    filepath = os.path.join(SKILL_DIR, filename)
    if os.path.isfile(filepath):
        media = "application/json" if filename.endswith(".json") else "text/markdown"
        return FileResponse(filepath, media_type=media)
    return {"error": "not found"}


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "ClawLink API is running", "docs": "/docs"}
