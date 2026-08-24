"""
Extraction result data model for signature extraction module.

Contains strongly-typed dataclasses for representing signature extraction results.
"""

from dataclasses import dataclass
from typing import Optional
from PIL import Image


@dataclass(frozen=True)
class ExtractionResult:
    """
    Immutable result of signature extraction.
    
    Attributes:
        success: Boolean indicating if extraction was successful
        extracted_image: PIL Image object containing the extracted signature with transparent background
        error: Error message if extraction failed, None otherwise
    """
    success: bool
    extracted_image: Optional[Image.Image] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class ExtractionMetadata:
    """
    Metadata about the extraction process.
    
    Attributes:
        original_size: Tuple of (width, height) of the original image
        extracted_size: Tuple of (width, height) of the extracted signature
        bounding_box: The bounding box that was used for extraction
        has_transparency: Whether the extracted image has an alpha channel
    """
    original_size: tuple
    extracted_size: tuple
    bounding_box: object  # BoundingBox type
    has_transparency: bool