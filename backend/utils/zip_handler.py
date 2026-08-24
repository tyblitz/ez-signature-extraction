import os
import zipfile
import tempfile
from pathlib import Path
from typing import List, Tuple

SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp'}


def extract_images_from_zip(zip_path: str, extract_to_dir: str) -> List[str]:
    """
    Extracts all supported image files from a ZIP archive into extract_to_dir.
    
    Returns:
        List of absolute file paths to the extracted image files.
    """
    extracted_image_paths: List[str] = []
    zip_path_obj = Path(zip_path)
    
    if not zip_path_obj.exists():
        return []
    
    os.makedirs(extract_to_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            # Skip directories and hidden files
            if file_info.is_dir() or file_info.filename.startswith('__MACOSX'):
                continue
            
            ext = Path(file_info.filename).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                extracted_path = zip_ref.extract(file_info, extract_to_dir)
                extracted_image_paths.append(str(Path(extracted_path).resolve()))
                
    return sorted(extracted_image_paths)


def create_signatures_zip(transparent_png_paths: List[str], output_zip_path: str) -> Tuple[bool, str]:
    """
    Packs a list of transparent PNG signature files into a target ZIP archive.
    
    Returns:
        Tuple of (success: bool, output_path_or_error: str)
    """
    try:
        output_path_obj = Path(output_zip_path)
        os.makedirs(output_path_obj.parent, exist_ok=True)
        
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in transparent_png_paths:
                p = Path(file_path)
                if p.exists():
                    zip_out.write(str(p), arcname=p.name)
                    
        return True, str(output_path_obj.resolve())
    except Exception as e:
        return False, f"Failed to create ZIP archive: {str(e)}"
