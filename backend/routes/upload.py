"""
SignGuard AI — Upload Route
=============================
POST /upload
    Accepts a signature image, runs the ML pipeline, returns prediction JSON.
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from config import UPLOADS_DIR
from ml.predict import predict_signature

router = APIRouter(tags=["Prediction"])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/tiff",
    "image/tif",
}


@router.post("/upload")
async def upload_signature(file: UploadFile = File(...)):
    """
    Upload a signature image and receive a Genuine / Forged prediction.

    - **file**: image file (PNG, JPG, BMP, TIFF)

    Returns:
    ```json
    {
      "prediction": "Genuine",
      "confidence": 94,
      "filename": "my_signature.png"
    }
    ```
    """
    # ── Validate MIME type ─────────────────────────────────────────────────────
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                "Please upload a PNG, JPG, BMP, or TIFF image."
            ),
        )

    # ── Save to uploads/ with a unique name ───────────────────────────────────
    suffix      = Path(file.filename).suffix or ".png"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path   = UPLOADS_DIR / unique_name

    try:
        contents = await file.read()
        file_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=500,
                            detail=f"Failed to save file: {exc}") from exc

    # ── Run prediction ─────────────────────────────────────────────────────────
    try:
        result = predict_signature(str(file_path))
        return JSONResponse(content={
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "filename":   file.filename,
        })

    except FileNotFoundError as exc:
        # model.pkl has not been trained yet
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(status_code=500,
                            detail=f"Prediction failed: {exc}") from exc

    finally:
        # Always clean up the temporary upload after prediction
        if file_path.exists():
            file_path.unlink(missing_ok=True)
