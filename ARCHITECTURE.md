# ARCHITECTURE OVERVIEW — EZ SIGNATURE EXTRACTION ENGINE (v1.1.2)

## 1. System Topology

```
+-----------------------------------------------------------------------+
|                        Electron Main Process                          |
|                       (electron/main.ts v1.1.2)                       |
+-----------------------------------+-----------------------------------+
                                    | IPC Subprocess Spawn
                                    v
+-----------------------------------------------------------------------+
|                       Backend PyInstaller Engine                      |
|                  (resources/backend/ez_backend.exe)                   |
|                   OR Python (backend/main.py)                        |
|                                                                       |
|  +---------------------------+     +-------------------------------+  |
|  | v1.1 Single-Sig Processor |     | v1.2 Multi-Lab Engine         |  |
|  | (signature_detector.py)   |     | (multi_signature_v2.py)       |  |
|  +-------------+-------------+     +---------------+---------------+  |
|                |                                   |                  |
|                +-----------------+-----------------+                  |
|                                  |                                    |
|                                  v                                    |
|                   Signature Refiner & Alpha Matting                   |
|                      (signature_refiner.py)                           |
+-----------------------------------+-----------------------------------+
                                    | JSON Payload Return
                                    v
+-----------------------------------------------------------------------+
|                      Vue 3 + Ionic Frontend UI                        |
|             (ExtractionView.vue & MultiExtractionView.vue)            |
+-----------------------------------------------------------------------+
```

---

## 2. Key Architecture Components

### Backend Modules (`backend/`)
- **`backend/main.py`**: CLI entry point supporting `--json`, `--multi-v2`, `--ink-mode`, and `--preservation`.
- **`backend/processors/multi_signature_v2.py`**:
  - `detect_signature_rows_v2`: HSV pen ink isolation + row-by-row Y-clustering + column/grid boundary filtering.
  - `remove_table_border_lines`: Morphological open operation erases horizontal table border lines at top/bottom margins of signature crops.
- **`backend/processors/signature_refiner.py`**:
  - 1-to-1 paper subtraction color matting ($C_{\text{ink}} = \frac{C_{\text{scan}} - (1-\alpha)C_{\text{paper}}}{\alpha}$).

### IPC Bridge (`electron/main.ts`)
- **`getBackendCommand()`**: Checks for packaged standalone executable (`resources/backend/ez_backend/ez_backend.exe`), local build (`backend_dist/ez_backend/ez_backend.exe`), or virtual environment Python (`venv/Scripts/python.exe`).
- **`extract-signature`**: Handles v1.1 single signature extractions.
- **`extract-multi-signature-v2`**: Handles v1.2 multi-signature extractions.

### Frontend Components (`frontend/src/`)
- **`ExtractionView.vue`**: Primary workspace manager, environment mode switcher (`v1.1` vs `v1.2`), sidebar batch queue manager, ZIP exporter.
- **`MultiExtractionView.vue`**: Multi-signature workspace canvas, document bounding box map viewer, background toggles (`checkerboard`, `light`, `dark`).

---

## 3. Packaging & Distribution
- Built with PyInstaller (`--onedir`) and Electron Builder (`--dir`).
- Standalone portable bundle located at `exe/EZ_Signature_Extraction_v1.1.2_Portable/`.