"""
SignGuard Admin — Registration Route
=====================================
POST /register
    Accepts 3 to 5 genuine signature images, extracts features, and stores the profile.
"""
import uuid
import datetime
import numpy as np
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from config import UPLOADS_DIR, PROFILES_DIR, THRESHOLD_MULTIPLIER
from ml.feature_extract import getCSVFeatures

router = APIRouter(tags=["Registration"])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/tiff",
}


@router.post("/register")
async def register_profile(files: List[UploadFile] = File(...)):
    """
    Register a signature profile by uploading 3 to 5 genuine signature images.
    """
    if len(files) < 3:
        raise HTTPException(
            status_code=400,
            detail="Minimum 3 signature samples are required to register a profile."
        )
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 signature samples are allowed."
        )

    features_list = []
    temp_files = []

    try:
        # Save and extract features for each file
        for file in files:
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type '{file.content_type}' for {file.filename}."
                )
            
            suffix = Path(file.filename).suffix or ".png"
            unique_name = f"{uuid.uuid4().hex}{suffix}"
            file_path = UPLOADS_DIR / unique_name
            temp_files.append(file_path)

            contents = await file.read()
            file_path.write_bytes(contents)

            # Extract features
            feats = getCSVFeatures(str(file_path))
            features_list.append(feats)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed during feature extraction: {exc}"
        ) from exc
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)

    # Compute reference profile parameters
    feats_arr = np.array(features_list, dtype=np.float32)
    means = np.mean(feats_arr, axis=0)
    stds = np.std(feats_arr, axis=0)

    # Calculate distance of each sample to the mean profile to set threshold
    epsilon = 1e-6
    distances = []
    for f in feats_arr:
        diff = (f - means) / (stds + epsilon)
        dist = np.sqrt(np.sum(diff ** 2))
        distances.append(dist)

    # Threshold is the max sample distance multiplied by threshold config multiplier
    max_dist = float(np.max(distances))
    threshold = max_dist * THRESHOLD_MULTIPLIER
    
    # Enforce a sensible minimum threshold to prevent division-by-zero sensitivity
    threshold = max(1.0, threshold)

    # Save profile JSON
    profile_data = {
        "means": means.tolist(),
        "stds": stds.tolist(),
        "threshold": threshold,
        "sample_count": len(files),
        "registered_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    profile_path = PROFILES_DIR / "admin_profile.json"
    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=4)

    return JSONResponse(content={
        "status": "success",
        "message": f"Successfully registered profile with {len(files)} samples.",
        "threshold": round(threshold, 4),
    })

# Necessary import helper
from pathlib import Path
import json
