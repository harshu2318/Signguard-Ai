"""
SignGuard AI — Model Training Script
======================================
Run this ONCE to train the signature verification model and save it as model.pkl.

Usage
-----
    cd backend
    python ml/train_model.py --genuine <path/to/genuine/> --forged <path/to/forged/>

Dataset Options
---------------
  • CEDAR (public, no login):
    http://www.cedar.buffalo.edu/NIJ/data/signatures.rar
    Place genuine images in one folder, forged in another.

  • Kaggle Signature Verification Dataset:
    https://www.kaggle.com/datasets/robinreni/signature-verification-dataset
    Unzip and point --genuine / --forged to the correct subfolders.

The script:
    1. Walks both folders and extracts 9 features per image
    2. Trains an SVM (RBF kernel) with StandardScaler pipeline
    3. Reports test accuracy
    4. Saves the pipeline to backend/ml/model.pkl
"""

import sys
import argparse
import numpy as np
import joblib
from pathlib import Path

# Ensure the backend root is on sys.path when running as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score

from ml.feature_extract import getCSVFeatures

IMG_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
OUTPUT_PATH = Path(__file__).parent / "model.pkl"


def load_dataset(genuine_dir: str, forged_dir: str):
    """
    Walk genuine and forged directories, extract features, and label them.

    Returns:
        X: np.ndarray of shape (N, 9)
        y: np.ndarray of shape (N,)   — 1=Genuine, 0=Forged
    """
    features, labels = [], []

    def _extract_from_folder(folder: Path, label: int, tag: str):
        images = [f for f in folder.iterdir() if f.suffix.lower() in IMG_EXTENSIONS]
        print(f"  [{tag}] Found {len(images)} images in {folder}")
        ok = 0
        for img_path in images:
            try:
                feat = getCSVFeatures(str(img_path))
                features.append(feat)
                labels.append(label)
                ok += 1
            except Exception as e:
                print(f"    ⚠  Skipping {img_path.name}: {e}")
        print(f"  [{tag}] Extracted features from {ok} images")

    _extract_from_folder(Path(genuine_dir), label=1, tag="Genuine")
    _extract_from_folder(Path(forged_dir),  label=0, tag="Forged")

    return np.array(features, dtype=np.float32), np.array(labels, dtype=np.int32)


def train_and_save(genuine_dir: str, forged_dir: str, output: str = None):
    """Train the SVM pipeline and persist it with joblib."""
    save_path = Path(output) if output else OUTPUT_PATH

    print("\n══════════════════════════════════════")
    print("  SignGuard AI — Model Training")
    print("══════════════════════════════════════\n")

    print("📂 Loading dataset …")
    X, y = load_dataset(genuine_dir, forged_dir)

    if len(X) == 0:
        print("\n[ERROR] No features extracted. Check your folder paths and image formats.")
        sys.exit(1)

    n_genuine = int(np.sum(y == 1))
    n_forged  = int(np.sum(y == 0))
    print(f"\n[INFO] Dataset: {len(X)} samples  ({n_genuine} genuine / {n_forged} forged)")

    # ── Train / Test split ────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # ── Build pipeline ────────────────────────────────────────────────────────
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("svm",    SVC(kernel="rbf", C=10, gamma="scale",
                       probability=True, random_state=42)),
    ])

    print("\n[INFO] Training SVM pipeline …")
    pipeline.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    y_pred   = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n[RESULTS]")
    print(f"   Test Accuracy : {accuracy * 100:.2f}%")
    print("\n" + classification_report(y_test, y_pred,
                                      target_names=["Forged", "Genuine"]))

    # ── Save ──────────────────────────────────────────────────────────────────
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, save_path)
    print(f"[SUCCESS] Model saved -> {save_path}")
    print("\n[INFO] You can now start the FastAPI backend.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train SignGuard AI signature verification model"
    )
    parser.add_argument("--genuine", required=True,
                        help="Path to folder containing genuine signature images")
    parser.add_argument("--forged",  required=True,
                        help="Path to folder containing forged signature images")
    parser.add_argument("--output",  default=None,
                        help="Output path for model.pkl  (default: ml/model.pkl)")
    args = parser.parse_args()

    train_and_save(args.genuine, args.forged, args.output)
