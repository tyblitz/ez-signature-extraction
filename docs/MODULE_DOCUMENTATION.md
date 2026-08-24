# Module Documentation

## Overview

This document provides detailed documentation for each module in the EZ Signature Extraction pipeline.

---

## Module 1: Image Processor

**File:** `backend/processors/image_processor.py`
**Version:** 1.0.0
**Purpose:** Load and validate input images

### Functions

#### `load_image(path: str) -> Image.Image`

Load an image from the given file path.

**Parameters:**
- `path` (str): Path to the image file

**Returns:**
- `Image.Image`: PIL Image object (RGB or RGBA mode)

**Raises:**
- `FileNotFoundError`: If file does not exist
- `ValueError`: If image format is not supported

**Example:**
```python
from backend.processors.image_processor import load_image

image = load_image('document.jpg')
print(image.size)  # (width, height)
print(image.mode)  # 'RGB' or 'RGBA'
```

#### `validate_format(path: str) -> bool`

Validate that the image format is supported.

**Parameters:**
- `path` (str): Path to the image file

**Returns:**
- `bool`: True if format is supported, False otherwise

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)

---

## Module 2: Signature Detector

**File:** `backend/processors/signature_detector.py`
**Version:** 1.0.0
**Purpose:** Detect signature presence and location

### Functions

#### `detect_signature(image: Image.Image) -> DetectionResult`

Detect if a handwritten signature exists in the image.

**Parameters:**
- `image` (Image.Image): PIL Image object (RGB or RGBA)

**Returns:**
- `DetectionResult`: Immutable result containing:
  - `has_signature` (bool): Whether signature was detected
  - `confidence` (float): Detection confidence (0.0 - 1.0)
  - `bounding_box` (Optional[BoundingBox]): Location of signature

**Algorithm:**
1. Convert to grayscale
2. Apply Gaussian blur (3x3 kernel)
3. Apply adaptive thresholding
4. Find external contours
5. Filter by area, aspect ratio, extent, solidity
6. Return largest contour as signature

**Detection Criteria:**
| Property | Threshold | Rationale |
|----------|-----------|-----------|
| Area | 10 - 90% of image | Filter noise and full-image |
| Aspect Ratio | 0.1 - 50 | Handle various shapes |
| Extent | > 0.02 | Filter sparse noise |
| Solidity | > 0.05 | Allow irregular shapes |

**Example:**
```python
from backend.processors.signature_detector import detect_signature
from backend.models.detection_result import DetectionResult

result = detect_signature(image)

if result.has_signature:
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Location: {result.bounding_box}")
```

---

## Module 3: Signature Extractor

**File:** `backend/processors/signature_extractor.py`
**Version:** 1.0.0
**Purpose:** Extract signature region from image

### Functions

#### `extract_signature(image: Image.Image, detection_result: DetectionResult) -> ExtractionResult`

Extract the signature region from the image.

**Parameters:**
- `image` (Image.Image): Original PIL Image
- `detection_result` (DetectionResult): Detection result from Module 2

**Returns:**
- `ExtractionResult`: Immutable result containing:
  - `success` (bool): Whether extraction succeeded
  - `extracted_image` (Optional[Image.Image]): Extracted signature (RGBA)
  - `error` (Optional[str]): Error message if failed

**Process:**
1. Validate inputs
2. Clamp bounding box to image boundaries
3. Crop image to bounding box
4. Convert to RGBA mode
5. Return extracted image

**Example:**
```python
from backend.processors.signature_extractor import extract_signature

result = extract_signature(image, detection_result)

if result.success:
    result.extracted_image.save('signature.png')
```

#### `extract_with_metadata(image: Image.Image, detection_result: DetectionResult) -> Tuple[ExtractionResult, ExtractionMetadata]`

Extract signature with detailed metadata.

**Returns:**
- Tuple of `ExtractionResult` and `ExtractionMetadata`

**Metadata Includes:**
- `original_size` (tuple): Original image dimensions
- `extracted_size` (tuple): Extracted image dimensions
- `bounding_box` (BoundingBox): Crop coordinates
- `has_transparency` (bool): Whether output has alpha

---

## Module 4: Signature Exporter

**File:** `backend/processors/signature_exporter.py`
**Version:** 1.0.0
**Purpose:** Save processed signatures to files

### Functions

#### `export_signature(extraction_result: ExtractionResult, output_dir: str, base_name: str, format: str = 'PNG', export_metadata: bool = True) -> ExportResult`

Export signature to files.

**Parameters:**
- `extraction_result` (ExtractionResult): Image to export
- `output_dir` (str): Output directory path
- `base_name` (str): Base filename (without extension)
- `format` (str): Output format (default: 'PNG')
- `export_metadata` (bool): Whether to generate metadata JSON

**Returns:**
- `ExportResult`: Immutable result containing:
  - `success` (bool): Whether export succeeded
  - `output_path` (Optional[str]): Path to exported file
  - `metadata_path` (Optional[str]): Path to metadata file
  - `error` (Optional[str]): Error message if failed

**Output Files:**
```
output/
├── document.png              # Original image (RGBA)
├── document_transparent.png  # Transparent signature
└── document_metadata.json    # Processing metadata
```

**Example:**
```python
from backend.processors.signature_exporter import export_signature

result = export_signature(
    extraction_result,
    output_dir='output/',
    base_name='document',
    format='PNG'
)

if result.success:
    print(f"Exported to: {result.output_path}")
```

---

## Module 5: Signature Refiner

**File:** `backend/processors/signature_refiner.py`
**Version:** 1.9.10
**Purpose:** Remove background and preserve signature

### Functions

#### `refine_signature(extraction_result: ExtractionResult, background_threshold: int = 240) -> RefinementResult`

Refine the extracted signature by removing background.

**Parameters:**
- `extraction_result` (ExtractionResult): Extracted signature
- `background_threshold` (int): Background detection threshold

**Returns:**
- `RefinementResult`: Immutable result containing:
  - `success` (bool): Whether refinement succeeded
  - `original_image` (Optional[Image.Image]): Original image
  - `refined_image` (Optional[Image.Image]): Refined signature (RGBA)
  - `error` (Optional[str]): Error message if failed
  - `metadata` (Optional[RefinementMetadata]): Processing metadata

**Algorithm:**
1. Convert to LAB color space
2. Detect background (L > 0.80 AND b > 0.05)
3. Convert to HSV color space
4. Detect blue ink (H: 0.47-0.75, S > 0.10)
5. Connect blue ink components
6. Generate alpha channel using distance transform

**Example:**
```python
from backend.processors.signature_refiner import refine_signature

result = refine_signature(extraction_result)

if result.success:
    result.refined_image.save('signature_transparent.png')
```

#### `refine_signature_on_full_image(image: Image.Image, detection_result: DetectionResult) -> RefinementResult`

Refine signature by processing the entire image without cropping.

**Purpose:** Handle multi-character signatures with gaps between characters.

**Parameters:**
- `image` (Image.Image): Original image
- `detection_result` (DetectionResult): Detection result

**Returns:**
- `RefinementResult`: Same as `refine_signature()`

**Example:**
```python
from backend.processors.signature_refiner import refine_signature_on_full_image

result = refine_signature_on_full_image(image, detection_result)

if result.success:
    result.refined_image.save('signature_transparent.png')
```

---

## Data Models

### DetectionResult

```python
@dataclass(frozen=True)
class DetectionResult:
    has_signature: bool
    confidence: float  # 0.0 - 1.0
    bounding_box: Optional[BoundingBox]
```

### BoundingBox

```python
@dataclass(frozen=True)
class BoundingBox:
    x: int      # Left coordinate
    y: int      # Top coordinate
    width: int  # Width in pixels
    height: int # Height in pixels
```

### ExtractionResult

```python
@dataclass(frozen=True)
class ExtractionResult:
    success: bool
    extracted_image: Optional[Image.Image]
    error: Optional[str]
```

### RefinementResult

```python
@dataclass(frozen=True)
class RefinementResult:
    success: bool
    original_image: Optional[Image.Image]
    refined_image: Optional[Image.Image]
    error: Optional[str]
    metadata: Optional[RefinementMetadata]
```

### RefinementMetadata

```python
@dataclass(frozen=True)
class RefinementMetadata:
    original_size: tuple           # (width, height)
    refined_size: tuple            # (width, height)
    background_pixels_removed: int
    signature_pixels_preserved: int
    has_transparency: bool
    processing_method: str
    refinement_successful: bool
```

---

## Color Detection Details

### Blue Ink Detection (HSV)

| Channel | Threshold | Meaning |
|---------|-----------|---------|
| H (Hue) | 0.47-0.75 | 85-135 degrees (blue) |
| S (Saturation) | > 0.10 | Not gray/washed out |

### Background Detection (LAB)

| Channel | Threshold | Meaning |
|---------|-----------|---------|
| L (Lightness) | > 0.80 | Bright paper |
| b (Blue-Yellow) | > 0.05 | Yellowish (not blue) |

---

## Error Handling

All modules use immutable Result objects:

```python
result = process(input)

if result.success:
    # Handle successful result
    use(result.output)
else:
    # Handle error
    log(result.error)
```

Never raise exceptions - always return Result objects with explicit success/failure status.