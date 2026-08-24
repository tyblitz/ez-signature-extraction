# EZ Signature Extraction Engine — Version 1.1.2

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.1.2-stable.svg)](package.json)
[![Build](https://img.shields.io/badge/build-Electron%20%2B%20Vue%203-brightgreen.svg)](electron/main.ts)

## Overview

**EZ Signature Extraction Engine** is a high-fidelity Signature Preservation, Isolation, and Extraction Desktop Application designed to extract handwritten signatures from single-page scanned forms, documents, and document batches while preserving authentic scanned pen ink pressure gradients.

---

## What's New in Release v1.1.2

1. **Standalone Portable Executable (`exe/EZ_Signature_Extraction_v1.1.2_Portable/`)**:
   - Includes a standalone compiled Python backend executable (`ez_backend.exe`) with pre-packaged OpenCV and Pillow.
   - Run the app on any Windows PC **without installing Python or Node.js**.
2. **Isolated Multi-Signature Lab Engine (`v1.2 Multi-Lab`)**:
   - **Row-by-Row Unified Clustering**: Treats all pen strokes inside a single table row of the Signature column as one unified signature (capturing disconnected initials like `P.` and surnames `Bencito` cleanly together).
   - **Form Table & Column Boundary Filtering**: Excludes Designation text columns ($x < 0.64 \times \text{width}$) and bottom Commander Approval Sign-Off blocks ($y > 0.43 \times \text{height}$).
   - **Automatic Cell Border Eraser**: Erases horizontal table box border lines running across top and bottom margins of signature crops.
3. **Sidebar Batch Queue & ZIP Export**:
   - Auto-unpacks extracted signature crops directly into individual sidebar Batch Queue items.
   - Enables one-click bulk export via **`Download All as ZIP`**.
4. **Environment Mode Switcher State Reset**:
   - Switching between `v1.1 Single-Sig` and `v1.2 Multi-Lab` instantly resets the workspace and cancels active tasks without auto-triggering unwanted extractions.

---

## Installation & Portable Usage

### Option 1: Standalone Portable Desktop Run (No Installation Required)
1. Copy the folder `exe/EZ_Signature_Extraction_v1.1.2_Portable` to any Windows computer.
2. Double click **`EZ Signature Extraction Engine.exe`** to launch immediately.

### Option 2: Development Installation from Source

```bash
# Clone the repository
git clone https://github.com/tyblitz/ez-signature-extraction.git
cd ez-signature-extraction

# Create Python virtual environment
python -m venv venv
venv\Scripts\activate

# Install Python backend dependencies
pip install Pillow opencv-python numpy pyinstaller

# Install Frontend dependencies
npm install

# Run Desktop Application in Dev Mode
npm run dev
```

---

## Workspace Operating Modes

### 🎯 v1.1 Single-Sig Mode
- Designed for single document scans or fast single-signature extractions.
- Produces full-resolution transparent PNG outputs with side-by-side original vs extracted comparison.

### 👥 v1.2 Multi-Lab Mode
- Designed for multi-signature table forms and specs sheets.
- Automatically segments signature rows, filters out non-signature table areas, populates the sidebar Batch Queue, and exports as a `.ZIP` bundle.

---

## Verification & Unit Testing

```bash
# Run unit test suite (111/111 passing tests)
venv\Scripts\python.exe -m unittest discover backend/tests

# Build production bundle
npx vite build
```

---

## License

MIT License. Copyright (c) 2026.