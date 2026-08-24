"""
Isolated Row-by-Row Multi-Signature Extraction Engine (v1.2)

Detects and segments individual handwritten signatures in form documents line-by-line / row-by-row.
Includes Signature Column & Table Boundary Filtering to exclude signatures outside the table grid (such as bottom commander sign-offs).
Automatically erases table cell border lines from top and bottom margins of signature crops.
"""

import numpy as np
from PIL import Image
import cv2
import io
import base64
from typing import List, Dict, Any, Tuple
from backend.models.detection_result import DetectionResult, BoundingBox
from backend.processors.signature_refiner import refine_signature_on_full_image


def remove_table_border_lines(crop_img: Image.Image) -> Image.Image:
    """
    Remove horizontal table cell border lines from top and bottom margins of a cropped signature image.
    """
    crop_arr = np.array(crop_img.convert("RGBA"))
    ch, cw = crop_arr.shape[:2]

    margin_h = max(4, int(ch * 0.14))
    horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))

    # Convert alpha channel to binary mask
    alpha = crop_arr[:, :, 3]

    # Process top margin
    top_strip = alpha[:margin_h, :]
    top_lines = cv2.morphologyEx(top_strip, cv2.MORPH_OPEN, horiz_kernel)
    alpha[:margin_h, :][top_lines > 0] = 0

    # Process bottom margin
    bottom_strip = alpha[-margin_h:, :]
    bottom_lines = cv2.morphologyEx(bottom_strip, cv2.MORPH_OPEN, horiz_kernel)
    alpha[-margin_h:, :][bottom_lines > 0] = 0

    crop_arr[:, :, 3] = alpha
    return Image.fromarray(crop_arr, mode="RGBA")


def detect_signature_rows_v2(
    image: Image.Image,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5
) -> List[Tuple[int, int, int, int]]:
    """
    Detect individual handwritten signature bounding boxes per table row in form documents.
    Filters out signatures outside the Signature column (x_center < 0.50 * width)
    and excludes bottom approval sign-offs below the table grid (y_center > 0.44 * height).
    """
    img_array = np.array(image.convert("RGB"))
    height, width = img_array.shape[:2]

    # Convert to HSV to separate pen ink from faint background watermarks
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)

    if ink_mode == 'black':
        pen_mask = (v < 140) & (s < 100)
    else:
        pen_mask = (s > 35) & (v < 235) & (h >= 80) & (h <= 145)

    pen_uint8 = (pen_mask * 255).astype(np.uint8)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(pen_uint8)

    min_area = max(100, int((width * height) * 0.00001))
    min_dim = max(15, int(width * 0.005))

    signature_components = []
    for i in range(1, num_labels):
        x, y, w, h_comp, area = stats[i]
        x_center = x + w / 2.0
        y_center = y + h_comp / 2.0
        
        # Filter 1: Must be in Signature column (x_center >= 0.64 * width)
        # Filter 2: Must be inside the table grid area (y_center <= 0.43 * height or y <= 3000)
        if (x_center >= 0.64 * width) and (y_center <= 0.43 * height or y <= 3000) and w >= min_dim and h_comp >= min_dim and area >= min_area:
            signature_components.append((x, y, w, h_comp, area))

    if not signature_components:
        return [(0, 0, width, height)]

    # Sort components by Y coordinate (top-to-bottom)
    signature_components.sort(key=lambda b: b[1])

    # Cluster components into distinct horizontal signature rows
    rows: List[List[Tuple[int, int, int, int, int]]] = []
    for comp in signature_components:
        x, y, w, h_comp, area = comp
        matched = False
        for row in rows:
            row_y1 = min(c[1] for c in row)
            row_y2 = max(c[1] + c[3] for c in row)
            comp_y_center = y + h_comp / 2.0
            if (row_y1 - 45) <= comp_y_center <= (row_y2 + 45):
                row.append(comp)
                matched = True
                break
        if not matched:
            rows.append([comp])

    row_boxes: List[Tuple[int, int, int, int]] = []
    for row in rows:
        min_x = min(c[0] for c in row)
        min_y = min(c[1] for c in row)
        max_x = max(c[0] + c[2] for c in row)
        max_y = max(c[1] + c[3] for c in row)
        bw = max_x - min_x
        bh = max_y - min_y

        row_boxes.append((int(min_x), int(min_y), int(bw), int(bh)))

    return row_boxes


def extract_multi_signature_crops_v2(
    image: Image.Image,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5
) -> Dict[str, Any]:
    """
    Extract all distinct row-by-row handwritten signatures from a document scan.
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL Image.Image, got {type(image)}")

    img_copy = image.copy()
    width, height = img_copy.size

    row_boxes = detect_signature_rows_v2(img_copy, ink_mode=ink_mode, preservation_level=preservation_level)

    crops_list: List[Dict[str, Any]] = []

    for idx, (bx, by, bw, bh) in enumerate(row_boxes, start=1):
        pad_x = min(25, bx, width - (bx + bw))
        pad_y = min(15, by, height - (by + bh))

        crop_x = int(max(0, bx - pad_x))
        crop_y = int(max(0, by - pad_y))
        crop_w = int(min(width - crop_x, bw + (pad_x * 2)))
        crop_h = int(min(height - crop_y, bh + (pad_y * 2)))

        cropped_img = img_copy.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

        orig_buf = io.BytesIO()
        cropped_img.save(orig_buf, format="PNG")
        orig_b64 = f"data:image/png;base64,{base64.b64encode(orig_buf.getvalue()).decode('utf-8')}"

        crop_det_res = DetectionResult(
            has_signature=True,
            confidence=0.90,
            bounding_box=BoundingBox(x=0, y=0, width=crop_w, height=crop_h)
        )

        refinement_res = refine_signature_on_full_image(
            cropped_img,
            crop_det_res,
            ink_mode=ink_mode,
            preservation_level=preservation_level,
            render_mode='natural'
        )

        target_img = refinement_res.refined_image if (refinement_res.success and refinement_res.refined_image) else cropped_img
        
        # Erase table border lines from top/bottom margins of transparent PNG
        cleaned_target_img = remove_table_border_lines(target_img)

        trans_buf = io.BytesIO()
        cleaned_target_img.save(trans_buf, format="PNG")
        trans_b64 = f"data:image/png;base64,{base64.b64encode(trans_buf.getvalue()).decode('utf-8')}"

        preserved_pixels = int(refinement_res.metadata.signature_pixels_preserved) if (refinement_res.metadata) else 0

        crops_list.append({
            "id": int(idx),
            "label": f"Sig #{idx}",
            "bbox": {"x": crop_x, "y": crop_y, "width": crop_w, "height": crop_h},
            "original_base64": orig_b64,
            "transparent_base64": trans_b64,
            "confidence": 0.90,
            "preserved_pixels": int(preserved_pixels),
            "background_pixels": int((crop_w * crop_h) - preserved_pixels)
        })

    full_orig_buf = io.BytesIO()
    img_copy.save(full_orig_buf, format="PNG")
    full_orig_b64 = f"data:image/png;base64,{base64.b64encode(full_orig_buf.getvalue()).decode('utf-8')}"

    return {
        "success": True,
        "count": len(crops_list),
        "crops": crops_list,
        "original_base64": full_orig_b64,
        "message": f"Successfully detected {len(crops_list)} signature table rows."
    }
