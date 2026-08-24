"""
Image Support Module for EZ Signature Extraction Application.

This module handles loading, validation, and preservation of image quality/transparency
for JPG, JPEG, and PNG formats. No modifications are performed in this phase.
"""

from PIL import Image
import os
import warnings
import io
from typing import Union, Tuple, Optional

# Suppress Pillow decompression warnings and disable max pixel cap for large scans
Image.MAX_IMAGE_PIXELS = None
warnings.filterwarnings('ignore', category=Image.DecompressionBombWarning)
warnings.filterwarnings('ignore')

# Supported image formats
SUPPORTED_FORMATS = ('JPG', 'JPEG', 'PNG')
MAX_PROCESS_DIMENSION = 2500

# Format extensions mapping
FORMAT_EXTENSIONS = {
    'JPG': '.jpg',
    'JPEG': '.jpg',
    'PNG': '.png'
}


def validate_format(file_path: str) -> bool:
    """
    Validate if the file path has a supported image extension.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        bool: True if format is supported, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False
    ext = file_path.lower().split('.')[-1]
    return ext in ('jpg', 'jpeg', 'png')


def validate_file_object(file_obj) -> bool:
    """
    Validate if a file-like object contains a supported image format.
    
    Args:
        file_obj: File-like object (e.g., BytesIO or opened file)
        
    Returns:
        bool: True if format is supported, False otherwise
    """
    try:
        if hasattr(file_obj, 'read'):
            file_obj.seek(0)
            with Image.open(file_obj) as img:
                return img.format in SUPPORTED_FORMATS
        return False
    except Exception:
        return False


def load_image(file_path: str) -> Image.Image:
    """
    Load an image from file path while preserving quality and transparency.
    Downscales giant scanned images (>2500px) for high performance.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        PIL Image object
    """
    if not validate_format(file_path):
        raise ValueError(f"Unsupported format. Supported formats: {SUPPORTED_FORMATS}")
    
    image = Image.open(file_path)
    
    # Auto-scale giant scanned documents to MAX_PROCESS_DIMENSION for high performance
    w, h = image.size
    if max(w, h) > MAX_PROCESS_DIMENSION:
        ratio = MAX_PROCESS_DIMENSION / float(max(w, h))
        new_w, new_h = max(1, int(w * ratio)), max(1, int(h * ratio))
        resample = getattr(Image, 'Resampling', Image).LANCZOS
        image = image.resize((new_w, new_h), resample)
        
    return image


def load_image_from_bytes(file_bytes: bytes) -> Image.Image:
    """
    Load an image from bytes while preserving quality and transparency.
    
    Args:
        file_bytes: Raw bytes of an image file
        
    Returns:
        PIL Image object with preserved properties
        
    Raises:
        ValueError: If file format is not supported
    """
    try:
        file_obj = io.BytesIO(file_bytes)
        if not validate_file_object(file_obj):
            raise ValueError(f"Unsupported format. Supported formats: {SUPPORTED_FORMATS}")
        
        file_obj.seek(0)
        image = Image.open(file_obj)
        return image
    except Exception as e:
        if "Unsupported format" in str(e):
            raise
        raise ValueError(f"Invalid image file: {str(e)}")


def load_image_from_file_object(file_obj, file_name: str = None) -> Image.Image:
    """
    Load an image from a file-like object while preserving quality and transparency.
    
    Args:
        file_obj: File-like object (e.g., from Flask request.files)
        file_name: Optional filename for format validation
        
    Returns:
        PIL Image object with preserved properties
        
    Raises:
        ValueError: If file format is not supported
    """
    # Validate format if filename provided
    if file_name and not validate_format(file_name):
        raise ValueError(f"Unsupported format. Supported formats: {SUPPORTED_FORMATS}")
    
    # Validate file object
    if not validate_file_object(file_obj):
        raise ValueError(f"Unsupported format. Supported formats: {SUPPORTED_FORMATS}")
    
    file_obj.seek(0)
    image = Image.open(file_obj)
    
    # Ensure we have the image data loaded
    image.load()
    
    return image


def get_image_info(image: Image.Image) -> dict:
    """
    Get information about an image without modification.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary with image properties
    """
    return {
        'format': image.format,
        'mode': image.mode,
        'size': image.size,
        'width': image.width,
        'height': image.height,
        'has_transparency': image.mode == 'RGBA' or image.mode == 'LA',
        'is_png': image.format == 'PNG'
    }

def get_supported_formats() -> tuple:
    """
    Return list of supported image formats.
    
    Returns:
        Tuple of supported format strings
    """
    return SUPPORTED_FORMATS