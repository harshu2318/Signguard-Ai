"""
SignGuard Admin — Verification Route
====================================
POST /verify
    Accepts a signature image, checks it against the registered profile, and returns the results.
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from config import UPLOADS_DIR
from ml.feature_extract import getCSVFeatures
from ml.verifier import verify_signature

router = APIRouter(tags=["Verification"])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/tiff",
}


@router.post("/verify")
async def verify_uploaded_signature(file: UploadFile = File(...)):
    """
    Verify an uploaded signature image against the registered admin profile.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                "Please upload a PNG, JPG, BMP, or TIFF image."
            ),
        )

    suffix      = Path(file.filename).suffix or ".png"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path   = UPLOADS_DIR / unique_name

    try:
        contents = await file.read()
        file_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}") from exc

    try:
        # Extract features from uploaded file
        features = getCSVFeatures(str(file_path))
        
        # Verify against registered profile
        result = verify_signature(features)
        
        return JSONResponse(content={
            "verdict":    result["verdict"],
            "confidence": result["confidence"],
            "distance":   result["distance"],
            "threshold":  result["threshold"],
            "filename":   file.filename,
        })

    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}") from exc
    finally:
        # Cleanup temporary uploaded file
        if file_path.exists():
            file_path.unlink(missing_ok=True)
