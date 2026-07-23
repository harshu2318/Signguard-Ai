"""
SignGuard AI — Feature Extraction
====================================
Ported directly from the original Jupyter notebook.
Computes 9 hand-crafted statistical features from a preprocessed binary signature image.

Features:
    1. Ratio          — ink pixel density
    2. Centroid Y     — vertical centre of mass (normalised)
    3. Centroid X     — horizontal centre of mass (normalised)
    4. Eccentricity   — how elongated the shape is
    5. Solidity       — convex hull fill ratio
    6. Skewness X     — horizontal skewness of pixel distribution
    7. Skewness Y     — vertical skewness
    8. Kurtosis X     — horizontal kurtosis
    9. Kurtosis Y     — vertical kurtosis
"""
import numpy as np
from typing import List
from skimage.measure import regionprops

from ml.preprocess import preproc


# ─── Individual Feature Functions (unchanged from notebook) ───────────────────

def Ratio(img: np.ndarray) -> float:
    """Ratio of ink pixels to total pixels."""
    a = np.sum(img == True)
    total = img.shape[0] * img.shape[1]
    return a / total if total > 0 else 0.0


def Centroid(img: np.ndarray):
    """Normalised (y, x) centroid of ink pixels."""
    coords = np.argwhere(img)
    if len(coords) == 0:
        return 0.5, 0.5
    centroid = np.mean(coords, axis=0) / np.array(img.shape)
    return float(centroid[0]), float(centroid[1])


def EccentricitySolidity(img: np.ndarray):
    """Eccentricity and solidity from region properties."""
    try:
        r = regionprops(img.astype("int8"))
        if not r:
            return 0.0, 0.0
        return float(r[0].eccentricity), float(r[0].solidity)
    except Exception:
        return 0.0, 0.0


def SkewKurtosis(img: np.ndarray):
    """
    Compute skewness and kurtosis along both axes.
    Returns:
        (skewx, skewy), (kurtx, kurty)
    """
    h, w = img.shape
    x = np.arange(w)
    y = np.arange(h)

    xp = np.sum(img, axis=0).astype(np.float64)
    yp = np.sum(img, axis=1).astype(np.float64)

    total = np.sum(img)
    if total == 0:
        return (0.0, 0.0), (0.0, 0.0)

    cx = np.sum(x * xp) / np.sum(xp) if np.sum(xp) > 0 else 0
    cy = np.sum(y * yp) / np.sum(yp) if np.sum(yp) > 0 else 0

    sx = np.sqrt(np.sum((x - cx) ** 2 * xp) / total)
    sy = np.sqrt(np.sum((y - cy) ** 2 * yp) / total)

    if sx == 0 or sy == 0:
        return (0.0, 0.0), (0.0, 0.0)

    skewx  = np.sum(xp * (x - cx) ** 3) / (total * sx ** 3)
    skewy  = np.sum(yp * (y - cy) ** 3) / (total * sy ** 3)
    kurtx  = np.sum(xp * (x - cx) ** 4) / (total * sx ** 4) - 3
    kurty  = np.sum(yp * (y - cy) ** 4) / (total * sy ** 4) - 3

    return (float(skewx), float(skewy)), (float(kurtx), float(kurty))


# ─── Combined Feature Vector ───────────────────────────────────────────────────

def getCSVFeatures(path: str) -> List[float]:
    """
    Extract the 9-dimensional feature vector from a signature image file.

    Args:
        path: Absolute path to the signature image.

    Returns:
        List of 9 floats: [ratio, cent_y, cent_x, eccentricity,
                           solidity, skew_x, skew_y, kurt_x, kurt_y]
    """
    img    = preproc(path)
    ratio  = Ratio(img)
    cy, cx = Centroid(img)
    ecc, sol = EccentricitySolidity(img)
    (skew_x, skew_y), (kurt_x, kurt_y) = SkewKurtosis(img)

    return [ratio, cy, cx, ecc, sol, skew_x, skew_y, kurt_x, kurt_y]
