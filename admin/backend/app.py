"""
SignGuard Admin — FastAPI Application Entry Point
==================================================
Writer-Dependent Signature Verification System.
Runs independently on port 8001. Does NOT modify the main SignguardRag project.
"""
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.register import router as register_router
from routes.verify import router as verify_router

app = FastAPI(
    title="SignGuard Admin API",
    description="Writer-Dependent Signature Verification — Admin Panel",
    version="1.0.0",
)

# Allow all origins — this is a local-only admin tool
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(register_router)
app.include_router(verify_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "SignGuard Admin API is running"}


@app.get("/profile-status", tags=["Health"])
def profile_status():
    """Check whether a reference profile has been registered."""
    from config import PROFILES_DIR
    profile_path = PROFILES_DIR / "admin_profile.json"
    if profile_path.exists():
        with open(profile_path) as f:
            data = json.load(f)
        return {
            "registered": True,
            "sample_count": data.get("sample_count", 0),
            "registered_at": data.get("registered_at", "unknown"),
            "threshold": round(data.get("threshold", 0), 4),
        }
    return {"registered": False}
