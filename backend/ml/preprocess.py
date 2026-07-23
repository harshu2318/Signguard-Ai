"""
SignGuard AI — Image Preprocessing
====================================
Ported directly from the original Jupyter notebook.
Converts a raw signature image to a clean binary image ready for feature extraction.

Pipeline: RGB → Greyscale → Gaussian Blur → Otsu Threshold → Binary crop
"""
import numpy as np
import matplotlib.image as mpimg
from scipy import ndimage
from skimage.filters import threshold_otsu


def rgbgrey(img: np.ndarray) -> np.ndarray:
    """Convert an RGB image to greyscale by averaging channels."""
    if img.ndim == 2:
        # Already greyscale
        return img.astype(np.float64)
    greyimg = np.zeros((img.shape[0], img.shape[1]), dtype=np.float64)
    for row in range(len(img)):
        for col in range(len(img[row])):
            greyimg[row][col] = np.average(img[row][col][:3])  # ignore alpha if present
    return greyimg


def greybin(img: np.ndarray) -> np.ndarray:
    """
    Apply Gaussian blur then Otsu thresholding to produce a binary image.
    Returns a logical-NOT so that the signature ink is True (foreground).
    """
    blur_radius = 0.8
    img = ndimage.gaussian_filter(img, blur_radius)
    thres = threshold_otsu(img)
    binimg = img > thres
    return np.logical_not(binimg)   # ink pixels are True


def preproc(path: str) -> np.ndarray:
    """
    Full preprocessing pipeline for a signature image file.

    Args:
        path: Absolute path to the image file.

    Returns:
        Binary numpy array cropped tightly around the signature.
    """
    img = mpimg.imread(path)

    # Normalise float images (matplotlib reads PNGs as 0-1 floats)
    if img.dtype in (np.float32, np.float64) and img.max() <= 1.0:
        img = (img * 255).astype(np.uint8)

    grey   = rgbgrey(img)
    binimg = greybin(grey)

    # Crop to bounding box of foreground pixels
    r, c = np.where(binimg == 1)
    if len(r) == 0:
        # Fallback: image has no detected ink — return as-is
        return binimg

    signimg = binimg[r.min():r.max(), c.min():c.max()]
    return signimg
