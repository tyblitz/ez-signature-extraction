#!/usr/bin/env python3
"""
EZ Signature Extraction Application - Main Entry Point

This is the Version 1 command-line application that integrates
Modules 1-5 for signature extraction from document images.

Usage:
    python -m backend.main input/document.jpg
    python -m backend.main input/document.jpg --output output/

Pipeline:
    1. Load input image (Module 1)
    2. Detect signature (Module 2)
    3. Refine signature directly (Module 5) - NO CROPPING
    4. Export signature (Module 4)
"""

import sys
import os
import json
import warnings
from pathlib import Path
from typing import Optional, Tuple

# Ensure workspace root is in sys.path for PyInstaller packaging
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
warnings.filterwarnings('ignore', category=Image.DecompressionBombWarning)
warnings.filterwarnings('ignore')

# Use absolute imports from backend package
from backend.processors.image_processor import load_image, validate_format
from backend.processors.signature_detector import detect_signature
from backend.processors.signature_exporter import export_signature
from backend.processors.signature_refiner import refine_signature_on_full_image
from backend.models.detection_result import DetectionResult
from backend.models.extraction_result import ExtractionResult
from backend.models.export_result import ExportResult
from backend.models.refinement_result import RefinementResult


def get_output_directory(input_path: str, output_dir: Optional[str] = None) -> Path:
    """
    Determine the output directory for extracted signature.
    
    Args:
        input_path: Path to input image
        output_dir: Optional user-specified output directory
    
    Returns:
        Path object for output directory
    """
    if output_dir:
        return Path(output_dir)
    
    # Default: create 'output' directory in the same folder as input
    input_path_obj = Path(input_path)
    return input_path_obj.parent / 'output'


def run_pipeline(
    input_path: str,
    output_directory: Optional[str] = None,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5,
    render_mode: str = 'natural'
) -> Tuple[bool, str]:
    """
    Execute the complete signature extraction pipeline.
    
    For multi-character signatures with gaps, we skip the cropping step
    and process the entire image to preserve all blue ink pixels.
    
    Args:
        input_path: Path to input document image
        output_directory: Optional output directory path
        ink_mode: Ink mode ('blue', 'black', 'auto')
        preservation_level: Sensitivity level (0.0 to 1.0)
        render_mode: Render mode ('natural', 'stamp')
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    input_path_obj = Path(input_path)
    output_dir = get_output_directory(input_path, output_directory)
    
    # Step 1: Validate input file exists
    if not input_path_obj.exists():
        return False, "Input image not found"
    
    # Step 2: Validate image format
    if not validate_format(input_path):
        return False, "Unable to process image"
    
    try:
        # Step 3: Load image (Module 1)
        image = load_image(str(input_path_obj))
        
        # Step 4: Detect signature (Module 2)
        detection_result = detect_signature(image)
        
        if not detection_result.has_signature:
            return False, "No signature detected in document"
        
        # Step 5: Refine signature directly on full image (Module 5)
        refinement_result = refine_signature_on_full_image(
            image, detection_result, ink_mode=ink_mode, preservation_level=preservation_level, render_mode=render_mode
        )
        
        if not refinement_result.success:
            return False, f"Refinement failed: {refinement_result.error}"
        
        # Step 6: Export original (convert to RGBA for transparency support)
        base_name = input_path_obj.stem
        # Convert image to RGBA if needed
        if image.mode != 'RGBA':
            rgba_image = image.convert('RGBA')
        else:
            rgba_image = image.copy()
        
        export_result = export_signature(
            ExtractionResult(
                success=True,
                extracted_image=rgba_image,
                error=None
            ),
            str(output_dir),
            base_name,
            format='PNG',
            export_metadata=True
        )
        
        if not export_result.success:
            return False, f"Export failed: {export_result.error}"
        
        # Step 7: Export transparent version
        transparent_export = export_signature(
            ExtractionResult(
                success=True,
                extracted_image=refinement_result.refined_image,
                error=None
            ),
            str(output_dir),
            f"{base_name}_transparent",
            format='PNG',
            export_metadata=True
        )
        
        if not transparent_export.success:
            return False, f"Transparent export failed: {transparent_export.error}"
        
        # Build success message
        original_size = os.path.getsize(export_result.output_path) if export_result.output_path else 0
        transparent_size = os.path.getsize(transparent_export.output_path) if transparent_export.output_path else 0
        
        message = (
            f"Input:\n"
            f"  {input_path_obj.name}\n\n"
            f"Detection:\n"
            f"  Signature found\n"
            f"  Confidence: {detection_result.confidence:.2f}\n\n"
            f"Refinement:\n"
            f"  Signature pixels preserved: {refinement_result.metadata.signature_pixels_preserved if refinement_result.metadata else 0}\n"
            f"  Background pixels removed: {refinement_result.metadata.background_pixels_removed if refinement_result.metadata else 0}\n\n"
            f"Output:\n"
            f"  {export_result.output_path} (original)\n"
            f"  {transparent_export.output_path} (transparent)\n\n"
            f"File sizes:\n"
            f"  Original: {original_size} bytes\n"
            f"  Transparent: {transparent_size} bytes"
        )
        
        return True, message
        
    except Exception as e:
        return False, f"Processing error: {str(e)}"


import base64
import io


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to data URI base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')


def run_pipeline_json(
    input_path: str,
    output_directory: Optional[str] = None,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5,
    render_mode: str = 'natural'
) -> dict:
    """Execute signature extraction pipeline and return structured JSON result."""
    input_path_obj = Path(input_path)
    output_dir = get_output_directory(input_path, output_directory)
    
    if not input_path_obj.exists():
        return {"success": False, "error": "Input image not found"}
    
    if not validate_format(input_path):
        return {"success": False, "error": "Unable to process image (Unsupported format)"}
    
    try:
        image = load_image(str(input_path_obj))
        detection_result = detect_signature(image)
        
        if not detection_result.has_signature:
            return {"success": False, "error": "No signature detected in document"}
        
        refinement_result = refine_signature_on_full_image(
            image, detection_result, ink_mode=ink_mode, preservation_level=preservation_level, render_mode=render_mode
        )
        
        if not refinement_result.success:
            return {"success": False, "error": f"Refinement failed: {refinement_result.error}"}
        
        base_name = input_path_obj.stem
        rgba_image = image.convert('RGBA') if image.mode != 'RGBA' else image.copy()
        
        transparent_export = export_signature(
            ExtractionResult(success=True, extracted_image=refinement_result.refined_image, error=None),
            str(output_dir),
            f"{base_name}_transparent",
            format='PNG',
            export_metadata=True
        )
        
        original_base64 = image_to_base64(rgba_image)
        transparent_base64 = image_to_base64(refinement_result.refined_image)
        
        bbox_dict = None
        if detection_result.bounding_box:
            bbox_dict = {
                "x": detection_result.bounding_box.x,
                "y": detection_result.bounding_box.y,
                "width": detection_result.bounding_box.width,
                "height": detection_result.bounding_box.height
            }
            
        return {
            "success": True,
            "error": None,
            "input_filename": input_path_obj.name,
            "original_base64": original_base64,
            "transparent_base64": transparent_base64,
            "transparent_output_path": transparent_export.output_path if transparent_export.success else None,
            "confidence": float(detection_result.confidence),
            "bounding_box": bbox_dict,
            "metadata": {
                "signature_pixels_preserved": int(refinement_result.metadata.signature_pixels_preserved) if refinement_result.metadata else 0,
                "background_pixels_removed": int(refinement_result.metadata.background_pixels_removed) if refinement_result.metadata else 0,
                "ink_mode": ink_mode,
                "preservation_level": preservation_level,
                "render_mode": render_mode
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Processing error: {str(e)}"}


def print_banner():
    """Print application banner."""
    print("=" * 50)
    print("EZ Signature Extraction Tool v1.0")
    print("=" * 50)
    print()


def print_result(success: bool, message: str):
    """Print result summary."""
    print(message)
    print()
    
    if success:
        print("-" * 50)
        print("Status: SUCCESS")
        print("-" * 50)
    else:
        print("-" * 50)
        print("Status: FAILED")
        print("-" * 50)


from backend.utils.zip_handler import extract_images_from_zip, create_signatures_zip, SUPPORTED_EXTENSIONS
import tempfile


def unpack_zip_json(zip_path: str) -> dict:
    """Unpacks a ZIP archive into a temp folder and returns image items with base64 previews."""
    zip_obj = Path(zip_path)
    if not zip_obj.exists():
        return {"success": False, "error": f"ZIP file not found: {zip_path}"}
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="ez_zip_")
        extracted_paths = extract_images_from_zip(zip_path, temp_dir)
        items = []
        for p in extracted_paths:
            try:
                img = load_image(p)
                items.append({
                    "path": p,
                    "filename": Path(p).name,
                    "base64": image_to_base64(img)
                })
            except Exception as e:
                print(f"Warning: Failed to load extracted image {p}: {e}", file=sys.stderr)
        
        return {"success": True, "items": items, "temp_dir": temp_dir, "count": len(items)}
    except Exception as e:
        return {"success": False, "error": f"ZIP extraction failed: {str(e)}"}


def create_zip_json(file_paths: list, output_zip_path: str) -> dict:
    """Compresses a list of file paths into an output ZIP file."""
    success, res = create_signatures_zip(file_paths, output_zip_path)
    if success:
        return {"success": True, "zip_path": res}
    else:
        return {"success": False, "error": res}


def main():
    """Main entry point for the application."""
    if len(sys.argv) < 2:
        print("Usage: python -m backend.main <input_image> [--json] [--output <dir>] [--ink-mode <mode>] [--preservation <float>] [--render-mode <mode>] [--unpack-zip <zip_file>] [--create-zip <zip_file>]")
        sys.exit(1)
    
    if '--unpack-zip' in sys.argv:
        idx = sys.argv.index('--unpack-zip')
        if idx + 1 < len(sys.argv):
            res = unpack_zip_json(sys.argv[idx + 1])
            sys.stdout.write(json.dumps(res))
            sys.stdout.flush()
            sys.exit(0 if res.get("success") else 1)

    if '--create-zip' in sys.argv:
        idx = sys.argv.index('--create-zip')
        if idx + 1 < len(sys.argv):
            out_zip = sys.argv[idx + 1]
            # Remaining arguments after --files or from stdin
            file_paths = []
            if '--files' in sys.argv:
                f_idx = sys.argv.index('--files')
                file_paths = sys.argv[f_idx + 1:]
            res = create_zip_json(file_paths, out_zip)
            sys.stdout.write(json.dumps(res))
            sys.stdout.flush()
            sys.exit(0 if res.get("success") else 1)

    is_json = '--json' in sys.argv
    input_path = sys.argv[1]
    output_dir = None
    ink_mode = 'blue'
    preservation_level = 0.5
    render_mode = 'natural'
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
            
    if '--ink-mode' in sys.argv:
        idx = sys.argv.index('--ink-mode')
        if idx + 1 < len(sys.argv):
            ink_mode = sys.argv[idx + 1]
            
    if '--preservation' in sys.argv:
        idx = sys.argv.index('--preservation')
        if idx + 1 < len(sys.argv):
            try:
                preservation_level = float(sys.argv[idx + 1])
            except ValueError:
                preservation_level = 0.5

    if '--render-mode' in sys.argv:
        idx = sys.argv.index('--render-mode')
        if idx + 1 < len(sys.argv):
            render_mode = sys.argv[idx + 1]
    
    if '--multi-v2' in sys.argv:
        try:
            from backend.processors.multi_signature_v2 import extract_multi_signature_crops_v2
            image = load_image(input_path)
            multi_res = extract_multi_signature_crops_v2(image, ink_mode=ink_mode, preservation_level=preservation_level)
            if is_json:
                sys.stdout.write(json.dumps(multi_res))
                sys.stdout.flush()
                sys.exit(0 if multi_res.get("success") else 1)
            else:
                print(f"Multi-Signature V2 Result: Detected {multi_res.get('count', 0)} signatures.")
                sys.exit(0 if multi_res.get("success") else 1)
        except Exception as err:
            err_payload = {"success": False, "error": str(err)}
            if is_json:
                sys.stdout.write(json.dumps(err_payload))
                sys.stdout.flush()
            else:
                print(f"Error: {err}")
            sys.exit(1)

    if is_json:
        result = run_pipeline_json(
            input_path,
            output_directory=output_dir,
            ink_mode=ink_mode,
            preservation_level=preservation_level,
            render_mode=render_mode
        )
        # Output clean JSON exclusively to stdout
        sys.stdout.write(json.dumps(result))
        sys.stdout.flush()
        sys.exit(0 if result.get("success") else 1)
    else:
        print_banner()
        success, message = run_pipeline(
            input_path,
            output_directory=output_dir,
            ink_mode=ink_mode,
            preservation_level=preservation_level,
            render_mode=render_mode
        )
        print_result(success, message)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()