# EZ Signature Extraction - Version 1

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-stable.svg)](CHANGELOG.md)

## Overview

**EZ** is a Signature Preservation and Isolation Engine designed to extract handwritten signatures from document images while preserving every aspect of the original handwriting.

### What EZ Does

1. **Preserves all blue handwritten signature ink** - Every stroke, loop, thin line, and faded mark
2. **Removes paper background aggressively** - Yellow paper, white artifacts, document borders
3. **Generates transparent PNG output** - Most faithful representation possible

### Key Philosophy

> **Signature preservation always takes priority over:**
> - Prettier outputs
> - Aggressive cropping
> - Perfect transparency
> - Unnecessary architectural complexity

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Pillow, OpenCV, NumPy (automatically installed)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/nousresearch/ez-signature-extraction.git
cd ez-signature-extraction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install Pillow opencv-python numpy

# Install the package
pip install -e .
```

### Requirements

```bash
# Required packages (see requirements.txt)
Pillow>=9.0.0
opencv-python>=4.5.0
numpy>=1.20.0
```

---

## Usage

### Command Line

```bash
# Basic usage
python -m backend.main input/document.jpg

# With custom output directory
python -m backend.main input/document.jpg --output results/
```

### As a Python Module

```python
from backend.main import run_pipeline

# Run the complete pipeline
success, message = run_pipeline('path/to/document.jpg')

if success:
    print("Extraction successful!")
    print(message)
else:
    print(f"Extraction failed: {message}")
```

### Programmatic Usage

```python
from PIL import Image
from backend.processors.signature_detector import detect_signature
from backend.processors.signature_refiner import refine_signature_on_full_image
from backend.models.extraction_result import ExtractionResult

# Load image
image = Image.open('document.jpg')

# Detect signature
detection = detect_signature(image)

if detection.has_signature:
    # Refine and extract
    result = refine_signature_on_full_image(image, detection)
    
    if result.success:
        # Save transparent signature
        result.refined_image.save('output_transparent.png')
```

---

## Supported Input Formats

| Format | Mode | Notes |
|--------|------|-------|
| JPEG | RGB | Most common format |
| PNG | RGB/RGBA | Preserves transparency |
| BMP | RGB | Supported |
| TIFF | RGB/RGBA | Multi-page not supported |

---

## Output Format

| File | Description |
|------|-------------|
| `{name}.png` | Original image with RGBA mode |
| `{name}_transparent.png` | Signature with transparent background |
| `{name}_metadata.json` | Processing metadata |

---

## Documentation

- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - What EZ is and its core philosophy
- **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** - Module structure and data flow
- **[Design Decisions](docs/DESIGN_DECISIONS.md)** - Why certain choices were made
- **[Version 1 Requirements](docs/VERSION1_REQUIREMENTS.md)** - Functional and non-functional requirements
- **[Module Documentation](docs/MODULE_DOCUMENTATION.md)** - Detailed module reference
- **[Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md)** - Coding standards and practices
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](docs/CHANGELOG.md)** - Version history and changes
- **[Future Improvements](docs/FUTURE_IMPROVEMENTS.md)** - Roadmap and planned features

---

## Project Philosophy

**EZ is NOT:**
- A signature detector
- A signature recognition system
- An e-signature generator

**EZ IS:**
- A Signature Preservation and Isolation Engine

**Its purpose is to:**
1. Preserve all of the blue handwritten signature
2. Remove everything that is not part of that signature
3. Generate the most faithful transparent representation possible

---

## Examples

### Input: Document with signature
![Input Example](docs/images/example_input.png)

### Output: Transparent signature
![Output Example](docs/images/example_output.png)

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Contributing

Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) before submitting pull requests.

---

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/nousresearch/ez-signature-extraction/issues) page.