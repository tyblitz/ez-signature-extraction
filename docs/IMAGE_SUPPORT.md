# Image Support Module - Phase 1 Documentation

## Overview

The Image Support module (Phase 1) provides basic image format handling for the EZ Signature Extraction application. This module focuses on loading and validating JPG, JPEG, and PNG images while preserving their original quality and transparency properties.

## Requirements Implemented

- ✅ JPG format support
- ✅ JPEG format support  
- ✅ PNG format support (including transparency)
- ✅ Image quality preservation
- ✅ Transparency preservation (for PNG)
- ✅ Large image file support (handled by Pillow)

## Architecture

```
Input Image → validate_format() → load_image/load_image_from_bytes/load_image_from_file_object() → Image Object (preserved)
```

The module acts as a passthrough - it does NOT modify images. It only:
1. Validates the file format
2. Loads the image into memory
3. Returns the image object with all original properties intact

## Functions

### `validate_format(file_path: str) -> bool`
Validates if a file path has a supported image extension (.jpg, .jpeg, .png).

### `validate_file_object(file_obj) -> bool`
Validates a file-like object contains a supported image format.

### `load_image(file_path: str) -> Image.Image`
Loads an image from file path with preserved quality and transparency.
- Raises `ValueError` for unsupported formats
- Raises `FileNotFoundError` if file doesn't exist
- Returns PIL Image object in original mode

### `load_image_from_bytes(file_bytes: bytes) -> Image.Image`
Loads an image from raw bytes with preserved properties.
- Useful for API uploads and in-memory processing

### `load_image_from_file_object(file_obj, file_name: str = None) -> Image.Image`
Loads an image from a file-like object (e.g., Flask request.files).
- Optional filename for additional format validation

### `get_image_info(image: Image.Image) -> dict`
Returns image properties without modification:
- Format, mode, size, dimensions
- Transparency status

- PNG images in RGBA or LA mode retain alpha channel
- No conversion to RGB unless absolutely necessary for JPEG output
- Transparency property passed through to next module unchanged

## Large Image Support

- Pillow handles large images efficiently
- Images loaded completely into memory for processing
- No specific size limits imposed by this module

## Usage Example

```python
from backend.processors.image_processor import load_image

# Load image
image = load_image('signature.png')

# Image is preserved - no modifications made
# Pass to next module for signature detection
# ...
```

## Testing

Run tests with:
```bash
python -m pytest backend/tests/test_image_processor.py -v
```

Or with unittest:
```bash
python backend/tests/test_image_processor.py
```

## Limitations

1. **No image validation beyond format** - Malformed image files may cause errors
2. **No size validation** - Very large images could consume memory
3. **No EXIF handling** - Metadata not processed or preserved
4. **Requires Pillow/OpenCV** - Dependencies must be installed

## Next Phase

Phase 2 will implement signature detection on the loaded images.