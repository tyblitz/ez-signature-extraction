# System Architecture

## Overview

EZ follows a modular 5-stage pipeline architecture. Each module has a single responsibility and communicates through immutable data structures.

```
┌─────────────────────────────────────────────────────────────────┐
│                        EZ Pipeline Flow                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Module 1   │────▶│   Module 2   │────▶│   Module 3   │
│ Image Loader │     │ Signature    │     │ Signature    │
│   (v1.0.0)   │     │ Detector     │     │ Extractor    │
│              │     │ (v1.0.0)     │     │ (v1.0.0)     │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Module 4   │◀────│   Module 5   │◀────│   Module 6   │
│ Signature    │     │ Signature    │     │ (Optional)   │
│ Exporter     │     │ Refiner      │     │              │
│ (v1.0.0)     │     │ (v1.9.10)    │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Module Details

### Module 1: Image Processor (image_processor.py)

**Purpose:** Load and validate input images

**Responsibilities:**
- Load images from file paths
- Validate supported formats
- Convert to consistent internal representation
- Preserve original image integrity

**Key Functions:**
```python
load_image(path: str) -> Image.Image
validate_format(path: str) -> bool
```

**Data Flow:**
```
File Path → PIL Image (RGB/RGBA)
```

---

### Module 2: Signature Detector (signature_detector.py)

**Purpose:** Detect if a signature exists and locate it

**Responsibilities:**
- Convert image to grayscale
- Apply adaptive thresholding
- Find contours of connected components
- Filter contours by geometric properties
- Return DetectionResult with confidence and bounding box

**Key Functions:**
```python
detect_signature(image: Image.Image) -> DetectionResult
```

**Detection Criteria:**
- Area: 10 - 90% of image area
- Aspect ratio: 0.1 - 50 (permissive)
- Extent: > 0.02
- Solidity: > 0.05

**Output Model:**
```python
@dataclass(frozen=True)
class DetectionResult:
    has_signature: bool
    confidence: float  # 0.0 - 1.0
    bounding_box: Optional[BoundingBox]  # May be None if no signature
```

---

### Module 3: Signature Extractor (signature_extractor.py)

**Purpose:** Extract the signature region from the image

**Responsibilities:**
- Crop image to bounding box
- Convert to RGBA format
- Preserve original image (never modify)
- Return clean extracted signature

**Key Functions:**
```python
extract_signature(image: Image.Image, detection: DetectionResult) -> ExtractionResult
```

**Important Note (Version 1.9+):**
For multi-character signatures with gaps, the pipeline now processes the entire image without aggressive cropping to preserve all blue ink pixels.

**Output Model:**
```python
@dataclass(frozen=True)
class ExtractionResult:
    success: bool
    extracted_image: Optional[Image.Image]  # RGBA image
    error: Optional[str]
```

---

### Module 4: Signature Exporter (signature_exporter.py)

**Purpose:** Save processed signatures to files

**Responsibilities:**
- Save PNG files with transparency
- Generate metadata JSON files
- Calculate file sizes
- Handle export errors gracefully

**Key Functions:**
```python
export_signature(
    extraction_result: ExtractionResult,
    output_dir: str,
    base_name: str,
    format: str = 'PNG',
    export_metadata: bool = True
) -> ExportResult
```

**Output Files:**
- `{base_name}.png` - Original image (RGBA)
- `{base_name}_transparent.png` - Transparent signature
- `{base_name}_metadata.json` - Processing metadata

---

### Module 5: Signature Refiner (signature_refiner.py)

**Purpose:** Remove background and preserve signature opacity

**Responsibilities:**
- Detect paper background using LAB color space
- Detect blue ink using HSV color space
- Connect multi-character signature components
- Generate alpha channel with proper opacity
- Validate output quality

**Key Functions:**
```python
refine_signature(extraction_result: ExtractionResult) -> RefinementResult
refine_signature_on_full_image(image: Image.Image, detection: DetectionResult) -> RefinementResult
```

**Color Detection:**

| Color Space | Purpose | Threshold |
|-------------|---------|-----------|
| LAB | Background detection | L > 0.80 AND b > 0.05 |
| HSV | Blue ink detection | H: 0.47-0.75, S > 0.10 |

**Alpha Channel Strategy:**
- Core signature: alpha 240-255 (nearly opaque)
- Edge pixels: alpha 200-240 (naturally blended)
- Background: alpha 0 (fully transparent)

**Output Model:**
```python
@dataclass(frozen=True)
class RefinementResult:
    success: bool
    original_image: Optional[Image.Image]
    refined_image: Optional[Image.Image]  # RGBA
    error: Optional[str]
    metadata: Optional[RefinementMetadata]
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INPUT: document.jpg                             │
│                                                                             │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌──────────────────────────────┐                        │
│                    │  Module 1: Image Processor     │                        │
│                    │  - Load image                  │                        │
│                    │  - Validate format             │                        │
│                    └──────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌──────────────────────────────┐                        │
│                    │  Module 2: Signature Detector│                        │
│                    │  - Detect signature presence  │                        │
│                    │  - Calculate confidence      │                        │
│                    │  - Find bounding box         │                        │
│                    └──────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌──────────────────────────────┐                        │
│                    │  Module 3: Signature Extractor│                        │
│                    │  - Crop to bounding box      │                        │
│                    │  - Convert to RGBA           │                        │
│                    │  - Preserve original         │                        │
│                    └──────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌──────────────────────────────┐                        │
│                    │  Module 5: Signature Refiner │                        │
│                    │  - LAB background detection  │                        │
│                    │  - HSV blue ink detection    │                        │
│                    │  - Connect components        │                        │
│                    │  - Generate alpha channel    │                        │
│                    └──────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌──────────────────────────────┐                        │
│                    │  Module 4: Signature Exporter  │                        │
│                    │  - Save PNG files            │                        │
│                    │  - Generate metadata         │                        │
│                    │  - Calculate file sizes      │                        │
│                    └──────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│              document.png   document_transparent.png   document_metadata.json │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Principles

### Immutability

All input images are treated as immutable. Processing is done on copies:

```python
# NEVER modify input
image = load_image(path)  # Original preserved
working_copy = image.copy()  # Work on copy
```

### Single Responsibility

Each module has exactly one job:

| Module | Single Responsibility |
|--------|----------------------|
| Image Processor | Load and validate images |
| Signature Detector | Find signatures |
| Signature Extractor | Extract signature regions |
| Signature Refiner | Remove background, preserve signature |
| Signature Exporter | Save files |

### Testability

Every module is designed to be testable in isolation:

```python
# Unit test example
def test_background_removal():
    # Arrange
    image = create_test_image_with_blue_signature()
    
    # Act
    result = refine_signature(extraction_result)
    
    # Assert
    assert result.success
    assert no_white_pixels(result.refined_image)
```

---

## Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Language |
| Pillow | 9.0+ | Image loading/saving |
| OpenCV | 4.5+ | Computer vision operations |
| NumPy | 1.20+ | Array operations |

### Why These Technologies?

**Pillow:**
- ✅ Mature, well-documented
- ✅ Native PNG transparency support
- ✅ No external dependencies

**OpenCV:**
- ✅ Connected component analysis
- ✅ Color space conversions (RGB→HSV, RGB→LAB)
- ✅ Morphological operations

**NumPy:**
- ✅ Efficient array operations
- ✅ Required by OpenCV
- ✅ Easy pixel manipulation

### Rejected Technologies

| Technology | Reason Rejected |
|------------|-----------------|
| TensorFlow | Not needed for Version 1 |
| PyTorch | Not needed for Version 1 |
| Tesseract OCR | Signature preservation, not text recognition |
| Cloud APIs | No network dependencies allowed |
| Machine Learning | Traditional CV sufficient for blue ink detection |

---

## Module Dependencies

```
backend/
├── main.py                    # Entry point (depends on all modules)
├── models/
│   ├── detection_result.py     # DetectionResult, BoundingBox
│   ├── extraction_result.py    # ExtractionResult
│   └── refinement_result.py    # RefinementResult, RefinementMetadata
└── processors/
    ├── image_processor.py      # Module 1
    ├── signature_detector.py   # Module 2
    ├── signature_extractor.py  # Module 3
    ├── signature_exporter.py   # Module 4
    └── signature_refiner.py    # Module 5
```

---

## Configuration

Current configuration is hardcoded in modules. Future versions may support:

- Configurable color thresholds
- Adjustable confidence thresholds
- Custom output formats

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Image loading | O(n) | n = pixels |
| Grayscale conversion | O(n) | Linear scan |
| Contour detection | O(n) | Connected components |
| Color detection | O(n) | Per-pixel analysis |
| Background removal | O(n) | LAB conversion |
| Alpha generation | O(n) | Distance transform |

**Typical processing time:** 0.5-2 seconds for 300x300 images

---

## Error Handling

The pipeline uses immutable result objects that indicate success/failure:

```python
result = process_image(path)

if result.success:
    # Process successful result
    save(result.output)
else:
    # Handle error
    log(result.error)
```

Never raise exceptions - always return Result objects.

---

## Future Architecture Considerations

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for planned architectural changes.