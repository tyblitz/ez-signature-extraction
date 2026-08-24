"""
Signature extraction module for EZ Signature Extraction Application.

This module implements Module 3: Signature Extraction.
It receives a PIL Image and DetectionResult from Module 2, extracts the detected 
signature region from the original image, and returns a clean extracted signature.

Responsibilities:
- Receive PIL Image objects from Module 1
- Receive DetectionResult from Module 2
- Extract the signature region using the bounding box
- Apply basic normalization for clean extraction
- Return a clean extracted signature image
- Preserve the original image completely (no modifications)

Constraints:
- Never modify the input image
- Never perform signature detection (relies on Module 2 output)
- Never perform signature recognition or matching
- Never perform OCR
- Never implement PDF or batch processing
- Use only Pillow, OpenCV, and NumPy (already approved dependencies)
- Keep implementation simple for Version 1
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional
from backend.models.detection_result import DetectionResult, BoundingBox
from backend.models.extraction_result import ExtractionResult, ExtractionMetadata


def extract_signature(
    image: Image.Image, 
    detection_result: DetectionResult
) -> ExtractionResult:
    """
    Extract signature from image using detection result coordinates.
    
    This function takes the original image and the detection result from Module 2,
    extracts the signature region, and returns a clean extracted signature image.
    
    Args:
        image: Original PIL Image object (MUST NOT BE MODIFIED)
               Expected formats: RGB, RGBA, L (grayscale)
        detection_result: DetectionResult from Module 2 containing:
            - has_signature: Boolean indicating if signature was detected
            - confidence: Detection confidence score
            - bounding_box: BoundingBox coordinates if signature found
    
    Returns:
        ExtractionResult: Immutable result containing:
            - success: Boolean indicating extraction success
            - extracted_image: PIL Image of extracted signature (RGBA with transparency)
            - error: Error message if extraction failed, None otherwise
    
    Guarantees:
        - Input image remains completely unmodified
        - Original image properties (mode, format, size) preserved
        - Function is deterministic and side-effect free
        - If signature detected, returns extracted region in RGBA format
    """
    # Input validation
    if not isinstance(image, Image.Image):
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Expected PIL Image.Image, got {type(image)}"
        )
    
    if not isinstance(detection_result, DetectionResult):
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Expected DetectionResult, got {type(detection_result)}"
        )
    
    # Check if signature was detected
    if not detection_result.has_signature:
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error="No signature detected in image"
        )
    
    # Check if bounding box is available
    if detection_result.bounding_box is None:
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error="No bounding box available for extraction"
        )
    
    bbox: BoundingBox = detection_result.bounding_box
    
    # Get image dimensions
    img_width, img_height = image.size
    
    # Validate bounding box coordinates
    if bbox.x < 0 or bbox.y < 0 or bbox.width <= 0 or bbox.height <= 0:
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Invalid bounding box: x={bbox.x}, y={bbox.y}, w={bbox.width}, h={bbox.height}"
        )
    
    # Clamp bounding box to image boundaries
    x1 = max(0, bbox.x)
    y1 = max(0, bbox.y)
    x2 = min(img_width, bbox.x + bbox.width)
    y2 = min(img_height, bbox.y + bbox.height)
    
    # Adjust for out-of-bounds boxes
    if x2 <= x1 or y2 <= y1:
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error="Bounding box is completely outside image boundaries"
        )
    
    # Create a working copy of the image for processing
    # IMPORTANT: We never modify the original image
    try:
        # Crop the signature region from the original image
        # This creates a new image object - original is unchanged
        cropped = image.crop((x1, y1, x2, y2))
        
        # Convert to RGBA for transparency support
        if cropped.mode != 'RGBA':
            # Convert to RGBA, preserving existing alpha if present
            extracted = cropped.convert('RGBA')
        else:
            extracted = cropped.copy()
        
        # Return successful extraction result
        return ExtractionResult(
            success=True,
            extracted_image=extracted,
            error=None
        )
        
    except Exception as e:
        return ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Extraction failed: {str(e)}"
        )


def extract_with_metadata(
    image: Image.Image,
    detection_result: DetectionResult
) -> Tuple[Optional[ExtractionResult], Optional[ExtractionMetadata]]:
    """
    Extract signature with detailed metadata about the extraction process.
    
    This is an extended version that returns both the extraction result and
    metadata about the extraction process.
    
    Args:
        image: Original PIL Image object
        detection_result: DetectionResult from Module 2
    
    Returns:
        Tuple of (ExtractionResult, ExtractionMetadata or None)
    """
    # Input validation
    if not isinstance(image, Image.Image):
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Expected PIL Image.Image, got {type(image)}"
        )
        return result, None
    
    if not isinstance(detection_result, DetectionResult):
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Expected DetectionResult, got {type(detection_result)}"
        )
        return result, None
    
    # Check if signature was detected
    if not detection_result.has_signature:
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error="No signature detected in image"
        )
        return result, None
    
    if detection_result.bounding_box is None:
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error="No bounding box available for extraction"
        )
        return result, None
    
    bbox = detection_result.bounding_box
    img_width, img_height = image.size
    
    # Validate bounding box
    if bbox.x < 0 or bbox.y < 0 or bbox.width <= 0 or bbox.height <= 0:
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Invalid bounding box: x={bbox.x}, y={bbox.y}, w={bbox.width}, h={bbox.height}"
        )
        return result, None
    
    # Clamp bounding box to image boundaries
    x1 = max(0, bbox.x)
    y1 = max(0, bbox.y)
    x2 = min(img_width, bbox.x + bbox.width)
    y2 = min(img_height, bbox.y + bbox.height)
    
    if x2 <= x1 or y2 <= y1:
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error="Bounding box is completely outside image boundaries"
        )
        return result, None
    
    try:
        # Crop and prepare extracted image
        cropped = image.crop((x1, y1, x2, y2))
        
        if cropped.mode != 'RGBA':
            extracted = cropped.convert('RGBA')
        else:
            extracted = cropped.copy()
        
        # Create metadata
        metadata = ExtractionMetadata(
            original_size=(img_width, img_height),
            extracted_size=extracted.size,
            bounding_box=bbox,
            has_transparency=True
        )
        
        result = ExtractionResult(
            success=True,
            extracted_image=extracted,
            error=None
        )
        
        return result, metadata
        
    except Exception as e:
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error=f"Extraction failed: {str(e)}"
        )
        return result, None


# Module-level metadata
__version__ = "1.0.0"
__author__ = "EZ Signature Extraction Team"