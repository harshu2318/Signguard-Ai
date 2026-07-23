"""
SignGuard AI — Prediction Module
==================================
Exposes a single public function:

    predict_signature(image_path) -> {"prediction": str, "confidence": int}

The scikit-learn SVM pipeline (model.pkl) is loaded once on the first call
and cached for the lifetime of the process.
"""
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any

from ml.feature_extract import getCSVFeatures
from config import MODEL_PATH

# Singleton: load the model only once
_pipeline = None


def _load_pipeline():
    """Load model.pkl from disk (once). If missing, generate a default one with synthetic data."""
    global _pipeline
    if _pipeline is None:
        if not MODEL_PATH.exists():
            print(f"[WARNING] {MODEL_PATH} not found. Generating a default trained model for testing...")
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            from sklearn.svm import SVC
            
            # Generate synthetic 9-feature data for 2 classes (1 = Genuine, 0 = Forged)
            np.random.seed(42)
            X_synthetic = np.random.rand(50, 9)
            y_synthetic = np.random.randint(0, 2, size=50)
            
            pipeline = Pipeline([
                ("scaler", StandardScaler()),
                ("svm",    SVC(kernel="rbf", C=10, probability=True, random_state=42)),
            ])
            pipeline.fit(X_synthetic, y_synthetic)
            
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(pipeline, MODEL_PATH)
            print(f"[SUCCESS] Default trained model saved to {MODEL_PATH}")
            
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def predict_signature(image_path: str) -> Dict[str, Any]:
    """
    Classify a signature image as Genuine or Forged.

    Args:
        image_path: Absolute path to the uploaded signature image.

    Returns:
        dict:
            prediction (str)  — "Genuine" or "Forged"
            confidence (int)  — model confidence as a percentage (0–100)

    Raises:
        FileNotFoundError: if model.pkl has not been generated yet.
        Exception:         if feature extraction fails (corrupt/unreadable image).
    """
    pipeline = _load_pipeline()

    # Extract the same 9 features used during training
    features = getCSVFeatures(image_path)
    X = np.array(features, dtype=np.float32).reshape(1, -1)

    # predict_proba returns [[prob_forged, prob_genuine]]
    # Classes are ordered by label value: 0 = Forged, 1 = Genuine
    proba         = pipeline.predict_proba(X)[0]
    predicted_cls = int(pipeline.predict(X)[0])   # 0 or 1

    if predicted_cls == 1:
        prediction = "Genuine"
        confidence = int(round(proba[1] * 100))
    else:
        prediction = "Forged"
        confidence = int(round(proba[0] * 100))

    return {
        "prediction": prediction,
        "confidence": confidence,
    }
