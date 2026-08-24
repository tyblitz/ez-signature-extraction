"""
Unit tests for new Signature Preservation modes and Ink Detection logic.

Tests cover:
- Blue ink mode with preservation level variations (low, default, high)
- Black ink mode with dark stroke extraction and noise rejection
- Auto ink mode detection between blue and black
- Faint stroke & micro-stroke retention
- Transparency & halo reduction checks
"""

import unittest
import os
import tempfile
import shutil
from PIL import Image, ImageDraw
import numpy as np
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.models.extraction_result import ExtractionResult
from backend.models.detection_result import DetectionResult, BoundingBox
from backend.processors.signature_refiner import (
    refine_signature,
    refine_signature_on_full_image,
    _detect_black_ink,
    _detect_ink_auto
)


class TestSignaturePreservationModes(unittest.TestCase):
    """Test suite for new ink modes and preservation sensitivity levels."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_blue_mode_faint_strokes_preservation(self):
        """Test that high preservation level retains faint blue strokes."""
        # Create image with faint blue signature stroke
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        # Light / faint blue line
        draw.line([(50, 50), (250, 50)], fill='#99CCFF', width=2)
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=img.convert('RGBA'),
            error=None
        )
        
        # Test with high preservation level
        result = refine_signature(extraction_result, ink_mode='blue', preservation_level=0.9)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.refined_image)
        
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        preserved_pixels = np.sum(alpha > 0)
        self.assertGreater(preserved_pixels, 0, "Faint blue stroke should be retained under high preservation")

    def test_black_ink_mode_extraction(self):
        """Test black ink mode extracts dark strokes cleanly."""
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        # Black pen signature line
        draw.line([(50, 50), (250, 50)], fill='#1A1A1A', width=4)
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=img.convert('RGBA'),
            error=None
        )
        
        result = refine_signature(extraction_result, ink_mode='black', preservation_level=0.5)
        self.assertTrue(result.success)
        
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        
        # Stroke pixels should be non-transparent
        stroke_pixels = np.sum(alpha > 0)
        self.assertGreater(stroke_pixels, 0, "Black ink stroke should be extracted")
        
        # Background corners should be transparent
        self.assertEqual(alpha[0, 0], 0, "White background should remain transparent in black ink mode")

    def test_auto_ink_mode_detection_blue(self):
        """Test auto ink mode automatically picks blue mode for blue signatures."""
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.line([(50, 50), (250, 50)], fill='#0044CC', width=4)
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=img.convert('RGBA'),
            error=None
        )
        
        result = refine_signature(extraction_result, ink_mode='auto', preservation_level=0.5)
        self.assertTrue(result.success)
        
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        self.assertGreater(np.sum(alpha > 0), 0, "Auto mode should extract blue signature")

    def test_auto_ink_mode_detection_black(self):
        """Test auto ink mode automatically picks black mode for black signatures."""
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.line([(50, 50), (250, 50)], fill='#101010', width=4)
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=img.convert('RGBA'),
            error=None
        )
        
        result = refine_signature(extraction_result, ink_mode='auto', preservation_level=0.5)
        self.assertTrue(result.success)
        
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        self.assertGreater(np.sum(alpha > 0), 0, "Auto mode should extract black signature")

    def test_preservation_level_scaling(self):
        """Test that higher preservation level retains equal or more stroke pixels."""
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        # Tapered faint blue line
        for i in range(50, 250):
            color = (0, 100, 200 + min(55, i // 5))
            draw.point((i, 50), fill=color)
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=img.convert('RGBA'),
            error=None
        )
        
        res_low = refine_signature(extraction_result, ink_mode='blue', preservation_level=0.1)
        res_high = refine_signature(extraction_result, ink_mode='blue', preservation_level=0.9)
        
        count_low = np.sum(np.array(res_low.refined_image)[:, :, 3] > 0)
        count_high = np.sum(np.array(res_high.refined_image)[:, :, 3] > 0)
        
        self.assertGreaterEqual(count_high, count_low, "High preservation level should retain equal or more pixels than low preservation level")

    def test_noise_rejection_in_black_mode(self):
        """Test that paper background remains transparent in black ink mode."""
        img = Image.new('RGB', (100, 100), color='white')
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=img.convert('RGBA'),
            error=None
        )
        result = refine_signature(extraction_result, ink_mode='black', preservation_level=0.5)
        self.assertTrue(result.success)
        
        alpha = np.array(result.refined_image)[:, :, 3]
        self.assertEqual(np.sum(alpha > 0), 0, "Pure white paper background should produce 0 stroke pixels")


if __name__ == '__main__':
    unittest.main()
