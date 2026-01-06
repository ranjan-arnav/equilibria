from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add src to python path to import existing agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import AppConfig

# Import API routers
from backend.api import negotiator, council, burnout, chat, decision, planning, state

app = FastAPI(
    title="Equilibria API",
    description="Backend API for Equilibria",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(negotiator.router, prefix="/api/negotiator", tags=["Negotiator"])
app.include_router(council.router, prefix="/api/council", tags=["Council"])
app.include_router(burnout.router, prefix="/api/burnout", tags=["Burnout"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(decision.router, prefix="/api/decision", tags=["Decision"])
app.include_router(planning.router, prefix="/api/planning", tags=["Planning"])
app.include_router(state.router, prefix="/api/state", tags=["State"])

@app.get("/")
def read_root():
    return {"message": "Equilibria API is running"}