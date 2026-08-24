# Future Improvements

## Version 1.1+ Roadmap

This document outlines planned improvements for EZ beyond Version 1.

---

## Near-Term Improvements (v1.1)

### Feature: Non-Blue Ink Support

**Priority:** Medium

**Description:** Support for black, red, green, and other colored signatures.

**Requirements:**
- Configurable ink color detection
- Multiple color space support
- User-selectable ink type

**Implementation:**
```python
# Planned API
refine_signature(extraction_result, ink_color='blue')  # Default
refine_signature(extraction_result, ink_color='black')
refine_signature(extraction_result, ink_color='auto')  # Auto-detect
```

**Status:** Planned

---

### Feature: Multi-Signature Support

**Priority:** Low

**Description:** Handle images with multiple signatures (e.g., signatory and witness).

**Requirements:**
- Detect and separate multiple signatures
- Individual export of each signature
- Metadata for each signature

**Implementation:**
```python
# Planned API
results = extract_all_signatures(image)
for result in results:
    result.export()
```

**Status:** Planned

---

### Feature: PDF Processing

**Priority:** Medium

**Description:** Process PDF documents with multiple pages.

**Requirements:**
- PDF batch processing
- Per-page signature extraction
- Output as PDF or individual images

**Dependencies:**
- PyPDF2 or pdf2image
- Page-to-image conversion

**Status:** Planned

---

## Medium-Term Improvements (v1.2+)

### Feature: Configurable Thresholds

**Priority:** Medium

**Description:** Allow users to adjust detection parameters.

**Requirements:**
- Command-line arguments for thresholds
- Configuration file support
- Preset profiles (document, photo, etc.)

**Implementation:**
```bash
# Planned CLI
python -m backend.main document.jpg --ink-color blue
python -m backend.main document.jpg --background-threshold 0.85
```

**Status:** Planned

---

### Feature: Performance Optimization

**Priority:** Medium

**Description:** Improve processing speed for large images.

**Requirements:**
- Process large images (2000x2000+) efficiently
- Memory usage optimization
- Optional downsampling

**Implementation:**
- Image pyramid processing
- Memory-mapped arrays
- Optional multi-threading

**Status:** Planned

---

## Long-Term Improvements (v2.0+)

### Feature: GUI Application

**Priority:** Medium

**Description:** Desktop application with visual interface.

**Requirements:**
- File drag-and-drop
- Preview of extraction
- Batch processing
- Settings panel

**Technology:**
- PyQt5 or Tkinter
- Cross-platform support

**Status:** Planned

---

### Feature: CLI Improvements

**Priority:** Low

**Description:** Enhanced command-line interface.

**Requirements:**
- Help system
- Interactive mode
- Progress indicators
- Multiple input file support

**Status:** Planned

---

## Architecture Evolution

### Planned Changes

| Area | Current | Planned |
|------|---------|---------|
| Color Detection | Fixed HSV/LAB | Configurable color spaces |
| Detection | Single algorithm | Multiple detection methods |
| Output | PNG only | Multiple formats |
| Batch | Single file | Batch processing |

---

## Research Questions

### Investigation Needed

1. **Alternative Color Spaces**
   - YCbCr for skin tone detection
   - L*a*b* for improved paper detection
   - HSV variants for different inks

2. **Machine Learning Integration**
   - Not for Version 1
   - Future consideration for v2+
   - Would require training data collection

3. **Deep Learning Alternatives**
   - U-Net for segmentation
   - Requires GPU acceleration
   - Not planned for Version 1

---

## Limitations to Address

### Current Limitations

| Limitation | Impact | Proposed Solution |
|------------|--------|-------------------|
| Blue ink only | Black signatures lost | Add color detection |
| No PDF support | Cannot process documents | Add PDF library |
| Fixed thresholds | May fail on edge cases | Make configurable |
| No GUI | CLI only | Build desktop app |

---

## Performance Targets

| Metric | Current | Target (v1.1) | Target (v2.0) |
|--------|---------|---------------|---------------|
| 300x300 image | < 1s | < 0.5s | < 0.3s |
| 1000x1000 image | < 5s | < 3s | < 2s |
| Memory usage | < 200MB | < 100MB | < 50MB |
| Test coverage | 100% | 100% | 100% |

---

## Deprecation Policy

Features will be deprecated with:

1. **Warning release** - Mark deprecated, show warning
2. **Transition period** - 3 months minimum
3. **Removal** - In next major version

---

## Breaking Changes

The following changes may be breaking:

- API signature changes
- Default threshold adjustments
- Output format modifications
- Configuration file format changes

All breaking changes will be documented in the release notes.

---

## Feature Request Process

To request a feature:

1. Open an issue on GitHub
2. Use the "Feature Request" template
3. Describe the use case
4. Include examples if possible
5. Label: `feature-request`

---

## Issue Triage

Issues are prioritized as:

| Priority | Definition |
|----------|------------|
| Critical | Crashes, data loss, major bugs |
| High | Affects core functionality |
| Medium | Improves usability or adds features |
| Low | Minor improvements, nice-to-haves |

---

## Version Planning

| Version | Focus | Timeline |
|---------|-------|----------|
| 1.0.0 | Core pipeline | Complete |
| 1.1.0 | Multi-color, PDF | Q1 2026 |
| 1.2.0 | Performance, CLI | Q2 2026 |
| 2.0.0 | GUI, ML options | 2026+