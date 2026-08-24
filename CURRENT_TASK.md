# CURRENT PHASE

VERSION 1.1.2 RELEASE COMPLETE — EZ SIGNATURE EXTRACTION ENGINE

--------------------------------------------------

BASELINE TEST & BUILD STATUS

- Unit Test Suite: `backend/tests`
- Total Unit Tests: **111 PASSED (0 failures, 0 errors)**
- Production Build: `npx vite build` (SUCCESS)
- Standalone Portable Build: `exe/EZ_Signature_Extraction_v1.1.2_Portable/` (SUCCESS)
- GitHub Remote Repository: `https://github.com/tyblitz/ez-signature-extraction` (SYNCED)
- Status: **VERSION 1.1.2 RELEASED & VERIFIED**

--------------------------------------------------

RELEASED FEATURES (v1.1.2)

1. **Standalone Portable Distribution**: Portable executable package built at `exe/EZ_Signature_Extraction_v1.1.2_Portable/` requiring zero Python/Node installation on target Windows PCs.
2. **v1.2 Multi-Lab Signature Engine**:
   - Row-by-Row Unified Signature Clustering for disconnected initials (`P.` and `Bencito`).
   - Form Table Boundary Exclusion Filter ($x_{\text{center}} \ge 0.64 \times \text{width}$, $y_{\text{center}} \le 0.43 \times \text{height}$).
   - Automatic Table Cell Border Eraser (`remove_table_border_lines`).
3. **Sidebar Batch Queue & ZIP Export**: Itemized queue for multi-signature crops and one-click `Download All as ZIP` export.
4. **Environment Mode Switcher Reset**: Instant state reset when toggling between `v1.1 Single-Sig` and `v1.2 Multi-Lab`.
5. **Vue 3 + Ionic + Electron Desktop App**: Drag-and-drop workspace, side-by-side comparison, zoom/pan controls, and background toggles.
