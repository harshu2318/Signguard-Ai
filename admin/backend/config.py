"""
SignGuard Admin — Central Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE_DIR     = Path(__file__).parent
PROFILES_DIR = BASE_DIR / "profiles"
UPLOADS_DIR  = BASE_DIR / "uploads"

# Matching sensitivity multiplier applied to the max pairwise distance
# between registered signatures to set the acceptance threshold.
# Lower = stricter (less natural variation allowed)
# 1.5 → strict  |  2.0 → normal  |  3.0 → lenient
THRESHOLD_MULTIPLIER = float(os.getenv("THRESHOLD_MULTIPLIER", "2.0"))

# Auto-create required directories
PROFILES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
