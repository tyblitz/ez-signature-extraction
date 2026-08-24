"""
Signature detection module for EZ Signature Extraction Application.

This module implements Module 2: Signature Detection.
It receives a - detects the presence and location
of handwritten signatures in images using traditional computer vision techniques.

Responsibilities:
- Receive PIL Image objects from Module 1 (Image Support)
- Detect whether a handwritten signature exists in the image
- Determine the location of the signature via bounding box
- Return a structured DetectionResult
- Preserve the original image completely (no modifications)
- Be fully testable and reusable by future modules

Constraints:
- Never modify the input image
- Never crop, enhance, or save images
- Never perform OCR
- Never implement PDF or batch processing
- Use only Pillow, OpenCV, and NumPy (already approved dependencies)
- Keep implementation simple for Version 1
"""

import numpy as np
from PIL import Image
import cv2
from typing import Optional
from backend.models.detection_result import DetectionResult, BoundingBox


def detect_signature(image: Image.Image) -> DetectionResult:
    """
    Detect handwritten signature in a PIL Image object.
    
    This function analyzes the input image to determine if it contains a 
    handwritten signature and returns the location if found.
    
    Args:
        image: PIL Image object (must not be modified)
               Expected formats: RGB, RGBA, L (grayscale)
               Supported modes from Module 1: RGB, RGBA
    
    Returns:
        DetectionResult: Immutable result containing:
            - has_signature: Boolean indicating signature detection
            - confidence: Float confidence score [0.0, 1.0]
            - bounding_box: BoundingBox if signature found, None otherwise
    
    Guarantees:
        - Input image remains completely unmodified
        - Original image properties (mode, format, size) preserved
        - Function is deterministic and side-effect free
        - Returns valid DetectionResult with confidence in [0.0, 1.0]
    
    Implementation Notes (Version 1 - Simple Approach):
        1. Convert image to grayscale for processing (on copy)
        2. Apply adaptive thresholding to isolate marks
        3. Find contours of connected components
        4. Filter contours by geometric properties typical of signatures:
           - Area constraints (filter out noise and extremely large regions)
           - Aspect ratio constraints (signatures vary in proportion)
           - Basic extent and solidity measures
        5. Calculate confidence based on presence of valid contours
        6. Return bounding box of largest valid contour if any found
    """
    # Input validation
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL Image.Image, got {type(image)}")
    
    # Create a WORKING COPY for processing - NEVER modify original
    # Convert to numpy array for OpenCV processing
    img_array = np.array(image.copy())
    
    # Handle different image modes
    if len(img_array.shape) == 3:
        # Color image (RGB or RGBA) - convert to grayscale
        if img_array.shape[2] == 4:  # RGBA
            # Extract RGB channels, ignore alpha for processing
            gray = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2GRAY)
        else:  # RGB
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    elif len(img_array.shape) == 2:
        # Already grayscale
        gray = img_array
    else:
        raise ValueError(f"Unsupported image shape: {img_array.shape}")
    
    # Apply slight Gaussian blur to reduce noise (on copy)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Adaptive thresholding to isolate dark marks on light background
    # Using parameters that work well for pen-on-paper signatures
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Find contours of connected components
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Filter contours based on signature-like properties
    height, width = gray.shape
    image_area = width * height
    
    valid_contours = []
    
    for contour in contours:
        # Calculate basic properties
        area = cv2.contourArea(contour)
        # Filter out very small noise and extremely large regions
        if area < 10 or area > image_area * 0.9:
            continue
            
        x, y, w, h = cv2.boundingRect(contour)
        
        # Avoid division by zero
        if h == 0:
            continue
            
        # Aspect ratio filter: be inclusive for various signature styles
        aspect_ratio = w / float(h)
        if aspect_ratio < 0.1 or aspect_ratio > 50.0:  # Very permissive
            continue
            
        # Calculate extent (area / bounding box area)
        rect_area = w * h
        if rect_area == 0:
            continue
        extent = area / float(rect_area)
        # Very low threshold to catch various mark types
        if extent < 0.02:
            continue
            
        # Calculate solidity (area / convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            continue
        solidity = area / float(hull_area)
        # Low threshold to allow for irregular signature strokes
        if solidity < 0.05:
            continue
            
        valid_contours.append({
            'contour': contour,
            'area': area,
            'bbox': (x, y, w, h),
            'aspect_ratio': aspect_ratio,
            'extent': extent,
            'solidity': solidity
        })
    
    # Determine detection result
    has_signature = len(valid_contours) > 0

    if has_signature:
        # Sort by area and return largest contour
        largest_contour = max(valid_contours, key=lambda c: c['area'])
        x, y, w, h = largest_contour['bbox']
        
        base_confidence = 0.4
        multi_contour_bonus = min(0.3, len(valid_contours) * 0.05)
        confidence = min(0.8, base_confidence + multi_contour_bonus)
        
        bounding_box = BoundingBox(x=x, y=y, width=w, height=h)
    else:
        confidence = 0.0
        bounding_box = None
    
    return DetectionResult(
        has_signature=has_signature,
        confidence=confidence,
        bounding_box=bounding_box
    )


# Module-level metadata
__version__ = "1.0.0"
__author__ = "EZ Signature Extraction Team"