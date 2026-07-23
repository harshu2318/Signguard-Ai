"""
SignGuard Admin — Verification Engine
=====================================
Uses standardized Euclidean distance to verify signatures against a stored reference profile.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any

from config import PROFILES_DIR

PROFILE_PATH = PROFILES_DIR / "admin_profile.json"


def load_profile() -> Dict[str, Any]:
    """Load the registered admin signature profile from disk."""
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            "No admin signature profile registered yet. "
            "Please register your signature first."
        )
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


def verify_signature(features: list) -> Dict[str, Any]:
    """
    Verify an uploaded signature's features against the registered profile.

    Args:
        features: List of 9 floats representing the uploaded signature's features.

    Returns:
        dict:
            verdict (str)    — "Genuine" or "Forged"
            confidence (int) — confidence percentage (0-100)
            distance (float) — normalized Euclidean distance
            threshold (float)— distance threshold
    """
    profile = load_profile()
    
    means = np.array(profile["means"])
    stds = np.array(profile["stds"])
    threshold = profile["threshold"]
    
    u = np.array(features)
    
    # Standardized Euclidean Distance (avoid division by zero with small epsilon)
    epsilon = 1e-6
    diff = (u - means) / (stds + epsilon)
    distance = float(np.sqrt(np.sum(diff ** 2)))
    
    # Calculate verdict and confidence
    if distance <= threshold:
        verdict = "Genuine"
        # Maps distance=0 -> 100% and distance=threshold -> 50%
        confidence = int(round(50 + (1.0 - (distance / threshold)) * 50))
    else:
        verdict = "Forged"
        # Maps distance=threshold -> 50% and distance >= 2*threshold -> 0%
        confidence = int(round(max(0.0, 50.0 - ((distance - threshold) / threshold) * 50.0)))
        
    return {
        "verdict": verdict,
        "confidence": confidence,
        "distance": round(distance, 4),
        "threshold": round(threshold, 4),
    }
