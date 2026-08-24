# Project Overview

## What is EZ?

**EZ** stands for **E**Z Signature **Z**one. It is a **Signature Preservation and Isolation Engine** built for extracting handwritten signatures from document images.

## Core Purpose

EZ exists for one primary purpose: **preserve the signature**.

Not to improve it. Not to enhance it. Not to make it look better. Just preserve it exactly as written.

## Project Philosophy

### The Fundamental Principle

> **Signature preservation must always take priority over:**
> - Prettier outputs
> - Aggressive cropping
> - Perfect transparency
> - Unnecessary architectural complexity

### Evolution of Philosophy

During Version 1 development, the project philosophy evolved significantly:

| Phase | Philosophy | Problem | Solution |
|-------|------------|---------|----------|
| Early | "Preserve more pixels" | Too conservative, kept background artifacts | "Preserve all handwriting, destroy everything else" |
| Mid | "Preserve more pixels" | Still preserving non-signature content | "Signature preservation > transparency beauty" |
| Final | "Preserve all handwriting" | Multi-character signatures being cropped | "Process entire image, preserve all blue ink" |

### Stop Thinking of EZ As...

❌ **A Signature Detector**
- Traditional detectors ask: "Where is the signature?"
- EZ knows: "There is only one signature"

✅ **A Signature Preservation Engine**
- EZ asks: "Which pixels are NOT part of the blue handwritten signature?"
- Everything else gets removed

## What EZ Does

### 1. Preserves All Blue Handwritten Signature

This includes:
- Dark blue ink
- Medium blue ink
- Faded blue ink
- Loops and curves
- Thin strokes
- Anti-aliased edges
- Disconnected handwriting components
- Intersections and crossings

### 2. Removes Everything Non-Signature

Aggressively removes:
- Yellow paper backgrounds
- White edge artifacts
- Document borders
- Document lines
- Scanner noise
- Gray artifacts
- Compression artifacts
- Transparency artifacts

### 3. Generates Faithful Transparent PNG

Creates a transparent PNG where:
- Signature pixels: alpha 240-255 (nearly opaque)
- Edge pixels: alpha 200-240 (naturally blended)
- Background: alpha 0 (fully transparent)

## What EZ Does NOT Do

- ✗ Detect multiple signatures (only one per image)
- ✗ Recognize or match signatures
- ✗ Generate or create signatures
- ✗ Use AI/ML models
- ✗ Implement OCR
- ✗ Process multi-page documents
- ✗ Handle video input

## Target Use Cases

1. **Legal Document Processing**
   - Extract signatures from contracts
   - Preserve signature authenticity for archival

2. **Digital Signing Workflows**
   - Convert wet signatures to digital format
   - Maintain signature integrity for verification

3. **Document Management**
   - Isolate signatures in automated workflows
   - Prepare signatures for electronic systems

4. **Forensic Analysis**
   - Preserve signature evidence faithfully
   - Maintain original characteristics

## Assumptions

The following assumptions are critical to EZ's operation:

| Assumption | Rationale | Impact if Wrong |
|--------------|-----------|-----------------|
| Single signature per image | Simplifies processing | Multiple signatures would need separate handling |
| Blue ink signature | Primary detection mechanism | Non-blue ink would be removed |
| Signature is handwritten | Distinguishes from typed text | Printed signatures may not be recognized |
| Paper-based document | Background is paper-colored | Non-paper backgrounds may be misidentified |

## Limitations

### Current Limitations (Version 1)

1. **Single signature only** - Images with multiple signatures will only extract the first one detected
2. **Blue ink required** - Non-blue signatures (black, red, green) will be partially or fully removed
3. **RGB images only** - Grayscale support is limited
4. **No multi-page support** - Each image must be processed separately
5. **Fixed color thresholds** - May not work well on unusual paper colors or extreme lighting

### Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| Very light signature ink may be lost | Under investigation | Ensure signature has sufficient contrast |
| Very dark background may be misidentified | Under investigation | Use documents with standard cream/white backgrounds |
| Compression artifacts in JPEG | Handled | Use high-quality JPEG or PNG |

## Version Status

⚠️ **Version 1 is Under Active Development**

- Architecture may evolve based on testing
- Design decisions may change when justified
- Correctness always takes priority over preserving assumptions
- New features are being evaluated for v1.1+

---

## Quick Reference

```
EZ = Signature Preservation + Background Removal + Transparency Generation
```

**Remember:** If there's ever a conflict between a perfectly clean PNG and a perfectly preserved signature, always choose **perfectly preserved signature**.