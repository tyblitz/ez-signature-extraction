"""
Export result data model for signature export module.

Contains strongly-typed dataclasses for representing signature export results.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from PIL import Image


@dataclass(frozen=True)
class ExportResult:
    """
    Immutable result of signature export operation.
    
    Attributes:
        success: Boolean indicating if export was successful
        output_path: Path to the exported file if successful, None otherwise
        metadata_path: Path to the exported metadata file if successful, None otherwise
        error: Error message if export failed, None otherwise
    """
    success: bool
    output_path: Optional[str] = None
    metadata_path: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class ExportMetadata:
    """
    Metadata about the export operation.
    
    Attributes:
        format: Output image format (e.g., 'PNG')
        original_size: Tuple of (width, height) of the extracted signature
        file_size_bytes: Size of the exported file in bytes
        compression: Compression level used (if applicable)
        export_options: Dictionary of options used for export
    """
    format: str
    original_size: tuple
    file_size_bytes: int
    compression: Optional[str] = None
    export_options: Optional[Dict[str, Any]] = None