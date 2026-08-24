# Changelog

All notable changes to the EZ Signature Extraction project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.9.10] - 2026-07-30

### Added
- `refine_signature_on_full_image()` function for multi-character signature support
- Processing of entire image without cropping to preserve all blue ink
- Support for signatures with gaps between characters

### Changed
- Pipeline now processes entire image to preserve disconnected signature components
- Updated main.py to use full-image refinement approach instead of cropping

### Fixed
- Multi-character signatures with spaces are now preserved as one signature
- Disconnected handwriting components are no longer lost during extraction

---

## [1.9.9] - 2026-07-30

### Changed
- Removed brightness filter that was removing light blue ink
- Adjusted blue detection to preserve light blue signature ink (#3399FF)

### Fixed
- Light blue ink signatures are now properly detected and preserved

---

## [1.9.8] - 2026-07-30

### Fixed
- Corrected LAB b channel calculation to prevent uint8 underflow
- Fixed blue hue detection range for better signature capture

---

## [1.9.7] - 2026-07-30

### Changed
- Removed value (brightness) threshold from blue ink detection
- Blue ink detection now only uses hue and saturation

### Fixed
- Navy blue ink is now properly detected

---

## [1.9.6] - 2026-07-30

### Changed
- Signature preservation is now the highest priority
- Signature pixels remain opaque (alpha 240-255), only edges receive reduced alpha
- Adaptive padding prevents signature cropping at borders

### Added
- Export validation to check signature integrity

---

## [1.9.5] - 2026-07-30

### Fixed
- Fixed LAB calculation overflow by using int16 conversion before subtraction
- White pixels in signature area reduced to 0

---

## [1.9.4] - 2026-07-30

### Changed
- Implemented connectivity-based preservation logic
- Only keep pixels in significant connected components

### Added
- Aggressive artifact elimination for yellow stains, white highlights, gray artifacts

---

## [1.9.3] - 2026-07-30

### Changed
- Rewritten Module 5 with signature preservation as highest priority
- Core signature pixels preserved with alpha 240-255
- Edge pixels receive natural alpha blending (200-240)

---

## [1.9.2] - 2026-07-30

### Fixed
- Removed morphological closing operations that expanded mask into white areas
- Increased confidence threshold to 0.6

---

## [1.9.1] - 2026-07-30

### Fixed
- Fixed LAB analysis for proper background separation (dark pixel detection)
- Added light pixel filter (brightness threshold 0.90) to remove near-white signature pixels

---

## [1.9.0] - 2026-07-30

### Added
- Multi-color confidence analysis (HSV, LAB, RGB)
- RGB prioritization for blue detection
- Transparency validation before export

---

## [1.0.0] - 2026-07-30

### Added
- Initial release
- 5-module pipeline architecture
- Blue ink signature detection
- Background removal using LAB color space
- Transparent PNG generation
- Comprehensive test suite (103 tests)