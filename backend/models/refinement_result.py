"""
Refinement result data model for signature refinement module.

Contains strongly-typed dataclasses for representing signature refinement results.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Any


@dataclass(frozen=True)
class RefinementMetadata:
    """
    Metadata about the refinement process.
    
    Attributes:
        original_size: Size of the original extracted image (width, height)
        refined_size: Size of the refined image (width, height)
        background_pixels_removed: Approximate count of background pixels removed
        signature_pixels_preserved: Approximate count of signature pixels preserved
        has_transparency: Whether the output image has transparency
        processing_method: Method used for background removal
        refinement_successful: Whether refinement completed successfully
    """
    original_size: Tuple[int, int]
    refined_size: Tuple[int, int]
    background_pixels_removed: int
    signature_pixels_preserved: int
    has_transparency: bool
    processing_method: str
    refinement_successful: bool


@dataclass(frozen=True)
class RefinementResult:
    """
    Immutable result containing the refined signature.
    
    This result contains both the original extracted image (preserved)
    and a refined version with transparent background.
    
    Attributes:
        success: Boolean indicating if refinement was successful
        original_image: The original extracted image (preserved, never modified)
        refined_image: The refined image with transparent background (None if failed)
        error: Error message if refinement failed, None otherwise
        metadata: Metadata about the refinement process
    """
    success: bool
    original_image: Optional[Any]  # PIL Image
    refined_image: Optional[Any]  # PIL Image
    error: Optional[str]
    metadata: Optional[RefinementMetadata] = None