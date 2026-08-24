"""
Signature export module for EZ Signature Extraction Application.

This module implements Module 4: Signature Export & Packaging.
It receives the extracted signature from Module 3 and exports it safely
to disk while preserving the signature data exactly as received.

Responsibilities:
- Receive PIL Image objects from Module 3 (Signature Extraction)
- Export extracted signatures to disk in specified format
- Export extraction metadata alongside the signature
- Provide predictable file output paths
- Maintain traceability between source document and extracted signature
- Preserve extracted signature data without modification

Constraints:
- Never modify the signature image content
- Never enhance, remove noise from, or modify the image
- Never perform OCR, recognition, or matching
- Never perform batch processing
- Use only Pillow (already approved dependency)
- Keep implementation simple for Version 1
"""

import os
import json
from PIL import Image
from typing import Optional, Dict, Any
from backend.models.extraction_result import ExtractionResult
from backend.models.export_result import ExportResult, ExportMetadata


def export_signature(
    extraction_result: ExtractionResult,
    output_dir: str,
    filename: str,
    format: str = "PNG",
    export_metadata: bool = True,
    compression: Optional[int] = None
) -> ExportResult:
    """
    Export extracted signature to disk.
    
    This function takes the extraction result from Module 3 and saves
    the extracted signature image to disk in the specified format.
    
    Args:
        extraction_result: ExtractionResult from Module 3 containing:
            - success: Boolean indicating if extraction was successful
            - extracted_image: PIL Image of the extracted signature (RGBA)
            - error: Error message if extraction failed
        output_dir: Directory path where files should be saved
        filename: Base filename for the output (without extension)
        format: Output image format (default: PNG, supported: PNG, JPEG)
        export_metadata: Whether to export metadata file alongside image
        compression: Compression level for formats that support it (PNG: 0-9)
    
    Returns:
        ExportResult: Immutable result containing:
            - success: Boolean indicating export success
            - output_path: Path to exported image file if successful
            - metadata_path: Path to exported metadata file if successful
            - error: Error message if export failed
    
    Guarantees:
        - Original extracted image remains unchanged
        - Function is deterministic and side-effect free
        - Returns valid ExportResult with proper paths
    """
    # Validate inputs
    if not isinstance(extraction_result, ExtractionResult):
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error=f"Expected ExtractionResult, got {type(extraction_result)}"
        )
    
    if not extraction_result.success:
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error=f"Extraction was not successful: {extraction_result.error}"
        )
    
    if extraction_result.extracted_image is None:
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error="No extracted image available for export"
        )
    
    # Validate output directory
    if not output_dir or not isinstance(output_dir, str):
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error="Invalid output directory"
        )
    
    # Validate format
    format = format.upper()
    if format not in ('PNG', 'JPEG', 'JPG'):
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error=f"Unsupported format: {format}. Supported: PNG, JPEG, JPG"
        )
    
    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error=f"Failed to create output directory: {str(e)}"
        )
    
    # Prepare output paths
    # Sanitize filename (remove path separators and special chars)
    safe_filename = os.path.basename(filename).replace('/', '_').replace('\\', '_')
    
    if format == 'PNG':
        image_path = os.path.join(output_dir, f"{safe_filename}.png")
    else:  # JPEG/JPG
        image_path = os.path.join(output_dir, f"{safe_filename}.jpg")
    
    metadata_path = None
    
    # Export the image
    try:
        extracted = extraction_result.extracted_image
        
        if format == 'PNG':
            # PNG export preserves transparency
            export_kwargs = {}
            if compression is not None:
                export_kwargs['compress_level'] = max(0, min(9, compression))
            extracted.save(image_path, format='PNG', **export_kwargs)
        else:
            # JPEG doesn't support transparency - convert to RGB
            if extracted.mode == 'RGBA':
                # Create white background for transparent areas
                background = Image.new('RGB', extracted.size, (255, 255, 255))
                background.paste(extracted, mask=extracted.split()[-1])  # Use alpha as mask
                rgb_image = background
            else:
                rgb_image = extracted.convert('RGB')
            
            save_kwargs = {}
            if compression is not None:
                save_kwargs['quality'] = max(1, min(95, compression))
            rgb_image.save(image_path, format='JPEG', **save_kwargs)
        
        # Get file size
        file_size = os.path.getsize(image_path)
        
    except Exception as e:
        return ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error=f"Failed to save image: {str(e)}"
        )
    
    # Export metadata if requested
    if export_metadata:
        try:
            # Build metadata dictionary
            metadata = {
                "export_info": {
                    "source_format": extracted.mode,
                    "output_format": format,
                    "original_size": extracted.size,
                    "file_size_bytes": file_size,
                    "compression_used": compression,
                    "export_successful": True
                },
                "traceability": {
                    "output_filename": os.path.basename(image_path),
                    "output_path": image_path
                }
            }
            
            metadata_path = os.path.join(output_dir, f"{safe_filename}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            # Metadata export failure shouldn't fail the main export
            # Just log the error and continue
            print(f"Warning: Failed to export metadata: {str(e)}")
    
    # Return successful export result
    return ExportResult(
        success=True,
        output_path=image_path,
        metadata_path=metadata_path,
        error=None
    )


def export_with_details(
    extraction_result: ExtractionResult,
    output_dir: str,
    filename: str,
    format: str = "PNG",
    export_metadata: bool = True,
    compression: Optional[int] = None
) -> tuple:
    """
    Export signature with detailed metadata about the export process.
    
    This is an extended version that returns both the export result and
    detailed metadata about the export operation.
    
    Args:
        Same as export_signature
    
    Returns:
        Tuple of (ExportResult, ExportMetadata or None)
    """
    # First perform the export
    result = export_signature(
        extraction_result=extraction_result,
        output_dir=output_dir,
        filename=filename,
        format=format,
        export_metadata=export_metadata,
        compression=compression
    )
    
    if not result.success:
        return result, None
    
    # Create detailed metadata
    try:
        file_size = os.path.getsize(result.output_path) if result.output_path else 0
        
        metadata = ExportMetadata(
            format=format,
            original_size=extraction_result.extracted_image.size if extraction_result.extracted_image else (0, 0),
            file_size_bytes=file_size,
            compression="compress_level=" + str(compression) if compression is not None and format == 'PNG' else 
                        ("quality=" + str(compression) if compression is not None and format != 'PNG' else None),
            export_options={
                "format": format,
                "export_metadata": export_metadata,
                "compression": compression
            }
        )
        
        return result, metadata
        
    except Exception as e:
        return result, None


# Module-level metadata
__version__ = "1.0.0"
__author__ = "EZ Signature Extraction Team"