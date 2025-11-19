"""Image processing utilities"""

import cv2
import numpy as np
from PIL import Image
import imagehash


def preprocess_image(frame: np.ndarray) -> np.ndarray:
    """
    Preprocess frame for better OCR results
    
    Args:
        frame: Input frame (BGR format from OpenCV)
        
    Returns:
        Preprocessed grayscale image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply slight Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply adaptive thresholding for better text contrast
    # This works well for slides with varying lighting
    processed = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    return processed


def compute_image_hash(frame: np.ndarray, hash_size: int = 8) -> str:
    """
    Compute perceptual hash of an image for quick comparison
    
    Args:
        frame: Input frame (BGR format from OpenCV)
        hash_size: Size of the hash (default 8)
        
    Returns:
        Perceptual hash as hexadecimal string
    """
    # Convert BGR to RGB for PIL
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(rgb_frame)
    
    # Compute perceptual hash (robust to minor changes)
    phash = imagehash.phash(pil_image, hash_size=hash_size)
    
    return str(phash)


def resize_for_display(frame: np.ndarray, max_width: int = 1920, max_height: int = 1080) -> np.ndarray:
    """
    Resize frame while maintaining aspect ratio
    
    Args:
        frame: Input frame
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Resized frame
    """
    height, width = frame.shape[:2]
    
    # Calculate scaling factor
    scale = min(max_width / width, max_height / height, 1.0)
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return frame


def enhance_contrast(frame: np.ndarray) -> np.ndarray:
    """
    Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    
    Args:
        frame: Input grayscale frame
        
    Returns:
        Contrast-enhanced frame
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(frame)
