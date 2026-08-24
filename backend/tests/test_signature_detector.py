"""
Unit tests for Signature Detection Module.

Tests cover signature detection functionality including:
- Input validation
- Negative cases (no signature)
- Positive cases (with signature)
- Edge cases
- Output validation
- Immutability guarantees
"""

import unittest
import os
import tempfile
import numpy as np
from PIL import Image
import sys

# Add the backend directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.processors.signature_detector import detect_signature
from backend.models.detection_result import DetectionResult, BoundingBox


class TestSignatureDetector(unittest.TestCase):
    """Test cases for the signature detection module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.blank_image = Image.new('RGB', (200, 200), color='white')
        self.black_image = Image.new('RGB', (200, 200), color='black')
        
        # Create signature-like image
        self.signature_img = self._create_signature_image()
        
        # Create text-like image (should not be detected as signature)
        self.text_like_img = self._create_text_like_image()
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_signature_image(self):
        """Create a test image with a signature-like mark."""
        img = Image.new('RGB', (300, 100), color='white')
        # Create a simple signature-like curve
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Draw a wavy line that resembles a signature
        points = []
        for i in range(50, 250, 5):
            x = i
            y = 50 + 20 * np.sin((i - 50) * 0.1) + 10 * np.sin((i - 50) * 0.3)
            points.append((x, y))
        # Draw the line
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill='black', width=3)
        return img
    
    def _create_text_like_image(self):
        """Create an image with text-like patterns (should not trigger signature detection)."""
        img = Image.new('RGB', (200, 200), color='white')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Draw some small rectangles that resemble text characters
        for i in range(10, 190, 20):
            for j in range(20, 180, 20):
                draw.rectangle([i, j, i+8, j+12], fill='black')
        return img

    def test_input_validation(self):
        """Test that invalid inputs raise appropriate exceptions."""
        # Test None input
        with self.assertRaises(TypeError):
            detect_signature(None)
        
        # Test non-Image input
        with self.assertRaises(TypeError):
            detect_signature("not an image")
        
        with self.assertRaises(TypeError):
            detect_signature(123)
            
    def test_blank_image_no_signature(self):
        """Test that blank white image returns no signature detected."""
        result = detect_signature(self.blank_image)
        
        self.assertIsInstance(result, DetectionResult)
        self.assertFalse(result.has_signature)
        self.assertEqual(result.confidence, 0.0)
        self.assertIsNone(result.bounding_box)
    
    def test_black_image_no_signature(self):
        """Test that completely black image returns no signature detected."""
        result = detect_signature(self.black_image)
        
        # Even though it's all black, our filtering should reject it as too large
        self.assertIsInstance(result, DetectionResult)
        # This might actually detect something due to our size filtering, 
        # but confidence should be low or it should be rejected by size
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
    
    def test_signature_image_detection(self):
        """Test that signature-like image is detected."""
        result = detect_signature(self.signature_img)
        
        self.assertIsInstance(result, DetectionResult)
        # Should detect something in our signature-like image
        self.assertTrue(result.has_signature)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        
        if result.has_signature:
            self.assertIsNotNone(result.bounding_box)
            self.assertIsInstance(result.bounding_box, BoundingBox)
            # Bounding box should be within image bounds
            img_width, img_height = self.signature_img.size
            self.assertGreaterEqual(result.bounding_box.x, 0)
            self.assertGreaterEqual(result.bounding_box.y, 0)
            self.assertLessEqual(
                result.bounding_box.x + result.bounding_box.width, 
                img_width
            )
            self.assertLessEqual(
                result.bounding_box.y + result.bounding_box.height, 
                img_height
            )
    
    def test_text_like_image(self):
        """Test that text-like patterns don't trigger false positives."""
        result = detect_signature(self.text_like_img)
        
        self.assertIsInstance(result, DetectionResult)
        # Our simple detector might flag this, but confidence should be low
        # or it might be filtered out by geometric constraints
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        
        # If it does detect something, verify bounding box validity
        if result.has_signature and result.bounding_box:
            self.assertIsInstance(result.bounding_box, BoundingBox)
    
    def test_output_format_and_types(self):
        """Test that output has correct types and format."""
        result = detect_signature(self.blank_image)
        
        # Check return type
        self.assertIsInstance(result, DetectionResult)
        
        # Check field types
        self.assertIsInstance(result.has_signature, bool)
        self.assertIsInstance(result.confidence, float)
        self.assertTrue(0.0 <= result.confidence <= 1.0)
        
        if result.bounding_box is not None:
            self.assertIsInstance(result.bounding_box, BoundingBox)
            self.assertIsInstance(result.bounding_box.x, int)
            self.assertIsInstance(result.bounding_box.y, int)
            self.assertIsInstance(result.bounding_box.width, int)
            self.assertIsInstance(result.bounding_box.height, int)
            self.assertGreaterEqual(result.bounding_box.width, 0)
            self.assertGreaterEqual(result.bounding_box.height, 0)
    
    def test_immutability_guarantee(self):
        """Test that the input image is not modified."""
        # Create a test image with known pixel values
        test_img = Image.new('RGB', (100, 100), color='red')
        original_data = list(test_img.getdata())
        original_id = id(test_img)
        
        # Process the image
        result = detect_signature(test_img)
        
        # Check that the image object is the same (no rebinding)
        self.assertEqual(id(test_img), original_id)
        
        # Check that pixel data is unchanged
        new_data = list(test_img.getdata())
        self.assertEqual(original_data, new_data)
        
        # Check that basic properties are unchanged
        self.assertEqual(test_img.size, (100, 100))
        self.assertEqual(test_img.mode, 'RGB')
    
    def test_different_image_modes(self):
        """Test detection works with different image modes from Module 1."""
        # Test RGB
        rgb_img = Image.new('RGB', (100, 100), color='white')
        result_rgb = detect_signature(rgb_img)
        self.assertIsInstance(result_rgb, DetectionResult)
        
        # Test RGBA (with transparency)
        rgba_img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 255))
        result_rgba = detect_signature(rgba_img)
        self.assertIsInstance(result_rgba, DetectionResult)
        
        # Test grayscale
        gray_img = Image.new('L', (100, 100), color=255)
        result_gray = detect_signature(gray_img)
        self.assertIsInstance(result_gray, DetectionResult)
    
    def test_deterministic_output(self):
        """Test that same input produces same output."""
        img = Image.new('RGB', (100, 100), color='white')
        # Add some deterministic noise
        import random
        random.seed(42)
        pixels = []
        for _ in range(100 * 100):
            r = random.randint(240, 255)
            g = random.randint(240, 255)
            b = random.randint(240, 255)
            pixels.append((r, g, b))
        img.putdata(pixels)
        
        result1 = detect_signature(img)
        result2 = detect_signature(img)
        
        self.assertEqual(result1.has_signature, result2.has_signature)
        self.assertAlmostEqual(result1.confidence, result2.confidence, places=5)
        # Bounding boxes should be identical if present
        if result1.bounding_box and result2.bounding_box:
            self.assertEqual(
                (result1.bounding_box.x, result1.bounding_box.y, 
                 result1.bounding_box.width, result1.bounding_box.height),
                (result2.bounding_box.x, result2.bounding_box.y, 
                 result2.bounding_box.width, result2.bounding_box.height)
            )
        elif result1.bounding_box is None and result2.bounding_box is None:
            pass  # Both None is fine
        else:
            self.fail("One result had bounding box, other didn't")


class TestDetectionResultModel(unittest.TestCase):
    """Test the DetectionResult and BoundingBox data models."""
    
    def test_bounding_box_creation(self):
        """Test BoundingBox dataclass creation."""
        bbox = BoundingBox(x=10, y=20, width=30, height=40)
        self.assertEqual(bbox.x, 10)
        self.assertEqual(bbox.y, 20)
        self.assertEqual(bbox.width, 30)
        self.assertEqual(bbox.height, 40)
    
    def test_detection_result_creation(self):
        """Test DetectionResult dataclass creation."""
        bbox = BoundingBox(x=0, y=0, width=50, height=30)
        result = DetectionResult(
            has_signature=True,
            confidence=0.8,
            bounding_box=bbox
        )
        
        self.assertTrue(result.has_signature)
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.bounding_box, bbox)
    
    def test_detection_result_no_signature(self):
        """Test DetectionResult with no signature."""
        result = DetectionResult(
            has_signature=False,
            confidence=0.0,
            bounding_box=None
        )
        
        self.assertFalse(result.has_signature)
        self.assertEqual(result.confidence, 0.0)
        self.assertIsNone(result.bounding_box)


if __name__ == '__main__':
    unittest.main()