"""
Signature refinement module for EZ Signature Extraction Application.

This module implements Module 5: Signature Refinement & Background Removal.
It receives the image and detection result, removes the paper
background while preserving the signature strokes.

PHILOSOPHY:
- PRESERVE ALL HANDWRITING (absolute priority)
- REMOVE BACKGROUND AGGRESSIVELY
- Handle multi-character signatures by preserving all blue ink
"""

import numpy as np
import cv2
from PIL import Image
from typing import Optional, Tuple

from backend.models.detection_result import DetectionResult
from backend.models.extraction_result import ExtractionResult
from backend.models.refinement_result import RefinementResult, RefinementMetadata


def _detect_background(rgb_array: np.ndarray) -> np.ndarray:
    """
    Detect paper/background pixels that should be removed.
    Returns boolean mask where True = background pixel.
    """
    # Convert to LAB
    lab = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2LAB).astype(np.float32)
    l_channel = lab[:, :, 0] / 255.0  # Lightness: 0-1
    b_channel = (lab[:, :, 2] - 128) / 127.0  # Blue-Yellow: -1 to 1
    
    # Background is: high lightness AND yellowish (positive b)
    is_background = (l_channel > 0.80) & (b_channel > 0.05)
    
    return is_background


def _detect_all_blue_ink(rgb_array: np.ndarray, preservation_level: float = 0.5) -> np.ndarray:
    """
    Detect ALL blue ink pixels in the image.
    This handles multi-character signatures by finding all blue regions.
    """
    # Convert to HSV
    bgr = rgb_array[:, :, ::-1].astype(np.uint8)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    
    h = hsv[:, :, 0] / 179.0  # Hue: 0-1
    s = hsv[:, :, 1] / 255.0  # Saturation: 0-1
    
    # Blue ink criteria:
    # - Hue in blue range (0.47-0.75 = 85-135 degrees)
    blue_hue = (h >= 0.47) & (h <= 0.75)
    
    # Scale saturation cutoff with preservation_level:
    # level = 0.5 -> s > 0.10 (baseline)
    min_sat = max(0.03, 0.10 - 0.10 * (preservation_level - 0.5))
    sufficient_sat = s > min_sat
    
    return blue_hue & sufficient_sat


def _detect_black_ink(rgb_array: np.ndarray, preservation_level: float = 0.5) -> np.ndarray:
    """
    Detect black / dark ink pixels in the image while excluding background paper and shadows.
    """
    lab = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2LAB).astype(np.float32)
    l_channel = lab[:, :, 0] / 255.0
    
    bgr = rgb_array[:, :, ::-1].astype(np.uint8)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    s_channel = hsv[:, :, 1] / 255.0
    
    max_lightness = min(0.65, 0.40 + 0.20 * (preservation_level - 0.5))
    is_dark = l_channel < max_lightness
    is_low_sat = s_channel < 0.30
    
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad = cv2.magnitude(grad_x, grad_y)
    has_gradient = grad > (15.0 - 10.0 * (preservation_level - 0.5))
    
    bg_mask = _detect_background(rgb_array)
    
    return is_dark & is_low_sat & ~bg_mask & (has_gradient | (l_channel < 0.25))


def _detect_ink_auto(rgb_array: np.ndarray, preservation_level: float = 0.5) -> np.ndarray:
    """
    Automated ink detection mode:
    Analyzes blue vs dark ink candidate counts. If significant blue ink exists,
    selects blue mode; otherwise falls back safely to dark/black ink detection.
    """
    blue_mask = _detect_all_blue_ink(rgb_array, preservation_level)
    blue_pixel_count = np.sum(blue_mask)
    
    if blue_pixel_count >= 100:
        return blue_mask
    
    black_mask = _detect_black_ink(rgb_array, preservation_level)
    black_pixel_count = np.sum(black_mask)
    
    if black_pixel_count > 50:
        return black_mask
    
    return blue_mask


def _detect_signature_ink(rgb_array: np.ndarray, ink_mode: str = 'blue', preservation_level: float = 0.5) -> np.ndarray:
    """
    Unified ink detection router supporting 'blue', 'black', and 'auto' modes.
    """
    mode = (ink_mode or 'blue').lower().strip()
    if mode == 'black':
        return _detect_black_ink(rgb_array, preservation_level)
    elif mode == 'auto':
        return _detect_ink_auto(rgb_array, preservation_level)
    else:
        return _detect_all_blue_ink(rgb_array, preservation_level)


def _connect_blue_ink_components(mask: np.ndarray) -> np.ndarray:
    """
    Find all ink components and include them all as part of the signature.
    For multi-character signatures, we include ALL significant components.
    """
    if not np.any(mask):
        return np.zeros_like(mask, dtype=bool)
    
    # Find all connected components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8, ltype=cv2.CV_32S
    )
    
    if num_labels <= 1:
        return mask
    
    # Get all significant components (area > 50 pixels)
    result = np.zeros_like(mask, dtype=bool)
    
    for i in range(1, num_labels):  # Skip background
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 50:
            result = np.logical_or(result, (labels == i))
    
    return result


def _decontaminate_and_refine_signature(
    rgb_array: np.ndarray,
    signature_mask: np.ndarray,
    background_mask: np.ndarray,
    preservation_level: float = 0.5,
    render_mode: str = 'natural'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    1-to-1 Signature Alpha Matting & Paper Subtraction:
    Extracts the exact original scanned ink colors, gradients, and pressure variations
    while mathematically subtracting only the paper background (C_paper).
    
    Render modes:
    - 'natural': Exact 1-to-1 original scanned pen ink colors and natural pressure.
    - 'stamp': Crisp, high-contrast, vibrant digital signature mode optimized for e-signing.
    """
    if not np.any(signature_mask):
        h, w = signature_mask.shape[:2]
        return np.zeros((h, w, 3), dtype=np.uint8), np.zeros((h, w), dtype=np.uint8)

    rgb_float = rgb_array.astype(np.float32)

    # 1. Estimate paper background color C_paper
    if np.any(background_mask):
        paper_color = np.mean(rgb_float[background_mask], axis=0)
    else:
        paper_color = np.array([248.0, 246.0, 240.0], dtype=np.float32)

    paper_lum = 0.299 * paper_color[0] + 0.587 * paper_color[1] + 0.114 * paper_color[2]
    paper_lum = max(1.0, paper_lum)

    # 2. Calculate pixel luminance and relative darkness D
    pixel_lum = 0.299 * rgb_float[:, :, 0] + 0.587 * rgb_float[:, :, 1] + 0.114 * rgb_float[:, :, 2]
    darkness = np.clip(1.0 - (pixel_lum / paper_lum), 0.0, 1.0)

    # 3. Calculate blue chroma delta (for blue ink enhancement)
    b = rgb_float[:, :, 2]
    r = rgb_float[:, :, 0]
    g = rgb_float[:, :, 1]
    blue_chroma = np.clip((b - (r + g) / 2.0) / 255.0, 0.0, 1.0)

    # 4. Combined continuous alpha density
    raw_alpha = darkness + 1.2 * blue_chroma

    # Adjust threshold based on preservation_level
    min_alpha_thresh = max(0.02, 0.08 - 0.06 * (preservation_level - 0.5))
    valid_stroke = signature_mask & (raw_alpha >= min_alpha_thresh)

    # Clean border noise using light morphological closing
    mask_u8 = valid_stroke.astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    smoothed_mask = cv2.morphologyEx(mask_u8, cv2.MORPH_CLOSE, kernel) > 0

    # Scale alpha to 0-255 range
    alpha_matting = np.zeros_like(darkness, dtype=np.float32)
    alpha_matting[smoothed_mask] = np.clip(raw_alpha[smoothed_mask] * 255.0, 0.0, 255.0)

    # Apply light Gaussian smoothing along stroke edges for smooth 1-to-1 anti-aliasing
    alpha_blurred = cv2.GaussianBlur(alpha_matting, (3, 3), 0.7)
    alpha_final = np.where(smoothed_mask, alpha_blurred, 0.0)

    # 5. Extract original unmixed ink color C_ink by paper subtraction
    alpha_norm = np.expand_dims(alpha_final / 255.0, axis=2)
    alpha_safe = np.maximum(alpha_norm, 0.08)

    unmixed_ink = (rgb_float - (1.0 - alpha_norm) * paper_color) / alpha_safe
    unmixed_ink = np.clip(unmixed_ink, 0.0, 255.0)

    # For high alpha pixels (alpha >= 0.7), retain raw scanned RGB in natural mode
    final_rgb = np.where(alpha_norm >= 0.70, rgb_float, unmixed_ink)

    # Clamp highlights on edge pixels to prevent white glare leakage
    max_edge_lightness = paper_color - 15.0
    final_rgb = np.where(alpha_norm < 0.70, np.minimum(final_rgb, max_edge_lightness), final_rgb)

    # If Sharp e-Stamp mode selected, enhance vibrancy and ink contrast
    if (render_mode or 'natural').lower() == 'stamp':
        b_chan = final_rgb[:, :, 2]
        rg_avg = (final_rgb[:, :, 0] + final_rgb[:, :, 1]) / 2.0
        is_blue_pixel = (b_chan > rg_avg)
        
        stamp_rgb = final_rgb.copy()
        stamp_rgb[:, :, 0] = np.clip(stamp_rgb[:, :, 0] * 0.85, 0, 255)
        stamp_rgb[:, :, 1] = np.clip(stamp_rgb[:, :, 1] * 0.85, 0, 255)
        stamp_rgb[:, :, 2] = np.clip(stamp_rgb[:, :, 2] * 1.18, 0, 255)
        
        final_rgb = np.where(np.expand_dims(is_blue_pixel, axis=2), stamp_rgb, final_rgb)

    decontaminated_rgb = np.zeros_like(rgb_float)
    decontaminated_rgb[smoothed_mask] = np.clip(final_rgb[smoothed_mask], 0.0, 255.0)

    return decontaminated_rgb.astype(np.uint8), np.clip(alpha_final, 0, 255).astype(np.uint8)


def refine_signature(
    extraction_result: ExtractionResult,
    background_threshold: int = 240,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5,
    render_mode: str = 'natural'
) -> RefinementResult:
    """Remove paper background and preserve signature strokes."""
    if not isinstance(extraction_result, ExtractionResult):
        return RefinementResult(
            success=False,
            original_image=None,
            refined_image=None,
            error=f"Expected ExtractionResult, got {type(extraction_result)}"
        )
    
    if not extraction_result.success:
        return RefinementResult(
            success=False,
            original_image=None,
            refined_image=None,
            error=f"Extraction was not successful: {extraction_result.error}"
        )
    
    if extraction_result.extracted_image is None:
        return RefinementResult(
            success=False,
            original_image=None,
            refined_image=None,
            error="No extracted image available for refinement"
        )
    
    original_image = extraction_result.extracted_image
    
    try:
        # Ensure we're working with RGBA
        if original_image.mode != 'RGBA':
            working_image = original_image.convert('RGBA')
        else:
            working_image = original_image.copy()
        
        img_width, img_height = working_image.size
        img_array = np.array(working_image)
        
        # Extract RGB channels
        if img_array.shape[2] == 4:
            rgb_array = img_array[:, :, :3]
        else:
            rgb_array = img_array
        
        # STEP 1: Detect background pixels using LAB
        background_mask = _detect_background(rgb_array)
        
        # STEP 2: Detect ink pixels using selected ink_mode and preservation_level
        ink_mask = _detect_signature_ink(rgb_array, ink_mode=ink_mode, preservation_level=preservation_level)
        
        # STEP 3: Find all significant ink components
        signature_mask = _connect_blue_ink_components(ink_mask)
        
        # STEP 4: Remove any remaining background pixels from signature
        signature_mask = signature_mask & ~background_mask
        
        # STEP 5: Color decontamination & continuous alpha matting to eliminate paper halos
        decontaminated_rgb, alpha_channel = _decontaminate_and_refine_signature(
            rgb_array, signature_mask, background_mask, preservation_level=preservation_level, render_mode=render_mode
        )
        
        # Create output image
        result_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        result_array[:, :, :3] = decontaminated_rgb
        result_array[:, :, 3] = alpha_channel
        
        refined_image = Image.fromarray(result_array, mode='RGBA')
        
        # Calculate statistics
        total_pixels = img_width * img_height
        stroke_pixels = np.sum(signature_mask)
        background_pixels = np.sum(background_mask)
        
        proc_method = "background_removal_preservation" if ink_mode == 'blue' else f"background_removal_{ink_mode}"
        
        metadata = RefinementMetadata(
            original_size=(img_width, img_height),
            refined_size=(img_width, img_height),
            background_pixels_removed=int(background_pixels),
            signature_pixels_preserved=int(stroke_pixels),
            has_transparency=True,
            processing_method=proc_method,
            refinement_successful=True
        )
        
        return RefinementResult(
            success=True,
            original_image=original_image,
            refined_image=refined_image,
            error=None,
            metadata=metadata
        )
        
    except Exception as e:
        return RefinementResult(
            success=False,
            original_image=original_image,
            refined_image=None,
            error=f"Refinement failed: {str(e)}"
        )


def refine_signature_on_full_image(
    image: Image.Image,
    detection_result: DetectionResult,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5,
    render_mode: str = 'natural'
) -> RefinementResult:
    """
    Refine the signature by processing the FULL image without cropping.
    
    This is the preferred method for multi-character signatures where
    characters may have gaps between them.
    """
    if not isinstance(image, Image.Image):
        return RefinementResult(
            success=False,
            original_image=None,
            refined_image=None,
            error=f"Expected PIL Image, got {type(image)}"
        )
    
    if not isinstance(detection_result, DetectionResult):
        return RefinementResult(
            success=False,
            original_image=None,
            refined_image=None,
            error=f"Expected DetectionResult, got {type(detection_result)}"
        )
    
    try:
        # Ensure we're working with RGBA
        if image.mode != 'RGBA':
            working_image = image.convert('RGBA')
        else:
            working_image = image.copy()
        
        img_width, img_height = working_image.size
        img_array = np.array(working_image)
        
        # Extract RGB channels
        if img_array.shape[2] == 4:
            rgb_array = img_array[:, :, :3]
        else:
            rgb_array = img_array
        
        # STEP 1: Detect background pixels using LAB
        background_mask = _detect_background(rgb_array)
        
        # STEP 2: Detect ink pixels using selected ink_mode and preservation_level
        ink_mask = _detect_signature_ink(rgb_array, ink_mode=ink_mode, preservation_level=preservation_level)
        
        # STEP 3: Find all significant ink components
        signature_mask = _connect_blue_ink_components(ink_mask)
        
        # STEP 4: Remove any remaining background pixels from signature
        signature_mask = signature_mask & ~background_mask
        
        # STEP 5: Color decontamination & continuous alpha matting to eliminate paper halos
        decontaminated_rgb, alpha_channel = _decontaminate_and_refine_signature(
            rgb_array, signature_mask, background_mask, preservation_level=preservation_level, render_mode=render_mode
        )
        
        # Create output image
        result_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        result_array[:, :, :3] = decontaminated_rgb
        result_array[:, :, 3] = alpha_channel
        
        refined_image = Image.fromarray(result_array, mode='RGBA')
        
        # Calculate statistics
        total_pixels = img_width * img_height
        stroke_pixels = np.sum(signature_mask)
        background_pixels = np.sum(background_mask)
        
        proc_method = "full_image_refinement" if ink_mode == 'blue' else f"full_image_refinement_{ink_mode}"
        
        metadata = RefinementMetadata(
            original_size=(img_width, img_height),
            refined_size=(img_width, img_height),
            background_pixels_removed=int(background_pixels),
            signature_pixels_preserved=int(stroke_pixels),
            has_transparency=True,
            processing_method=proc_method,
            refinement_successful=True
        )
        
        return RefinementResult(
            success=True,
            original_image=working_image,
            refined_image=refined_image,
            error=None,
            metadata=metadata
        )
        
    except Exception as e:
        return RefinementResult(
            success=False,
            original_image=image,
            refined_image=None,
            error=f"Refinement failed: {str(e)}"
        )


def refine_signature_with_padding(
    extraction_result: ExtractionResult,
    background_threshold: int = 240,
    padding: int = 5,
    ink_mode: str = 'blue',
    preservation_level: float = 0.5
) -> RefinementResult:
    """Remove background with automatic cropping and padding."""
    result = refine_signature(extraction_result, background_threshold, ink_mode=ink_mode, preservation_level=preservation_level)
    
    if not result.success or result.refined_image is None:
        return result
    
    refined_array = np.array(result.refined_image)
    alpha = refined_array[:, :, 3]
    
    non_transparent = np.where(alpha > 0)
    
    if len(non_transparent[0]) == 0:
        return RefinementResult(
            success=False,
            original_image=result.original_image,
            refined_image=None,
            error="No signature pixels found for cropping"
        )
    
    min_y, max_y = non_transparent[0].min(), non_transparent[0].max()
    min_x, max_x = non_transparent[1].min(), non_transparent[1].max()
    
    img_width, img_height = result.refined_image.size
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(img_width, max_x + padding)
    max_y = min(img_height, max_y + padding)
    
    cropped = result.refined_image.crop((min_x, min_y, max_x, max_y))
    
    if result.metadata:
        new_metadata = RefinementMetadata(
            original_size=result.metadata.original_size,
            refined_size=cropped.size,
            background_pixels_removed=result.metadata.background_pixels_removed,
            signature_pixels_preserved=result.metadata.signature_pixels_preserved,
            has_transparency=True,
            processing_method="background_removal_with_padding",
            refinement_successful=True
        )
    else:
        new_metadata = None
    
    return RefinementResult(
        success=True,
        original_image=result.original_image,
        refined_image=cropped,
        error=None,
        metadata=new_metadata
    )


__version__ = "1.9.10"
__author__ = "EZ Signature Extraction Team"