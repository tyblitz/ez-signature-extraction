"""
Detection result data models for signature detection module.

Contains strongly-typed dataclasses for representing signature detection results.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BoundingBox:
    """
    Represents a bounding box with integer coordinates.
    
    Attributes:
        x: X-coordinate of top-left corner (pixels from left)
        y: Y-coordinate of top-left corner (pixels from top)
        width: Width of the bounding box (pixels)
        height: Height of the bounding box (pixels)
    """
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class DetectionResult:
    """
    Immutable result of signature detection.
    
    Attributes:
        has_signature: Boolean indicating whether a signature was detected
        confidence: Float between 0.0 and 1.0 indicating detection confidence
        bounding_box: BoundingBox if signature detected, None otherwise
    """
    has_signature: bool
    confidence: float
    bounding_box: Optional[BoundingBox] = None
    
    def __post_init__(self):
        """Validate confidence is in range [0.0, 1.0]."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")