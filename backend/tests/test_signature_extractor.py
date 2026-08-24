"""
Unit tests for Signature Extraction Module.

Tests cover signature extraction functionality including:
- Input validation
- Successful extraction cases
- Failed extraction cases
- Edge cases
- Output validation
- Immutability guarantees
"""

import unittest
import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.processors.signature_extractor import extract_signature, extract_with_metadata
from backend.processors.signature_detector import detect_signature
from backend.models.detection_result import DetectionResult, BoundingBox
from backend.models.extraction_result import ExtractionResult, ExtractionMetadata


class TestSignatureExtractor(unittest.TestCase):
    """Test cases for the signature extraction module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.blank_image = Image.new('RGB', (200, 200), color='white')
        
        # Create signature image
        self.signature_img = self._create_signature_image()
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_signature_image(self):
        """Create a test image with a signature-like mark."""
        img = Image.new('RGB', (300, 100), color='white')
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

    def test_input_validation_invalid_image(self):
        """Test that invalid image input returns appropriate error."""
        # Create a valid detection result
        bbox = BoundingBox(x=10, y=10, width=50, height=30)
        detection = DetectionResult(has_signature=True, confidence=0.8, bounding_box=bbox)
        
        # Test with invalid image
        result = extract_signature("not an image", detection)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)
        self.assertIsNotNone(result.error)
        self.assertIn("PIL Image.Image", result.error)

    def test_input_validation_invalid_detection_result(self):
        """Test that invalid detection result input returns appropriate error."""
        result = extract_signature(self.blank_image, "not a detection result")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)
        self.assertIsNotNone(result.error)
        self.assertIn("DetectionResult", result.error)

    def test_no_signature_detected(self):
        """Test extraction when no signature was detected."""
        # Create detection result with no signature
        detection = DetectionResult(has_signature=False, confidence=0.0, bounding_box=None)
        
        result = extract_signature(self.blank_image, detection)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)
        self.assertIsNotNone(result.error)
        self.assertIn("No signature detected", result.error)

    def test_missing_bounding_box(self):
        """Test extraction when detection result has no bounding box."""
        # Create detection result with signature but no bounding box
        detection = DetectionResult(has_signature=True, confidence=0.8, bounding_box=None)
        
        result = extract_signature(self.blank_image, detection)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)
        self.assertIsNotNone(result.error)
        self.assertIn("No bounding box", result.error)

    def test_successful_extraction(self):
        """Test successful signature extraction."""
        # First detect signature
        detection = detect_signature(self.signature_img)
        
        # Then extract
        result = extract_signature(self.signature_img, detection)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.extracted_image)
        self.assertIsNone(result.error)
        
        # Verify extracted image properties
        extracted = result.extracted_image
        self.assertEqual(extracted.mode, 'RGBA')
        self.assertGreater(extracted.width, 0)
        self.assertGreater(extracted.height, 0)

    def test_extraction_with_rgba_image(self):
        """Test extraction with RGBA image (transparency preserved)."""
        # Create RGBA image with signature
        img = Image.new('RGBA', (300, 100), color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        for i in range(50, 250, 5):
            x = i
            y = 50 + 20 * np.sin((i - 50) * 0.1) + 10 * np.sin((i - 50) * 0.3)
            draw.line([(x-2, y-2), (x+2, y+2)], fill='black', width=3)
        
        # Detect and extract
        detection = detect_signature(img)
        result = extract_signature(img, detection)
        
        self.assertTrue(result.success)
        self.assertEqual(result.extracted_image.mode, 'RGBA')

    def test_extraction_immutability(self):
        """Test that extraction doesn't modify the original image."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        original_data = list(img.getdata())
        original_id = id(img)
        original_size = img.size
        original_mode = img.mode
        
        # Create a valid detection result
        bbox = BoundingBox(x=10, y=10, width=50, height=50)
        detection = DetectionResult(has_signature=True, confidence=0.8, bounding_box=bbox)
        
        # Extract signature
        result = extract_signature(img, detection)
        
        # Verify original image unchanged
        self.assertEqual(id(img), original_id)
        self.assertEqual(list(img.getdata()), original_data)
        self.assertEqual(img.size, original_size)
        self.assertEqual(img.mode, original_mode)

    def test_invalid_bounding_box_coordinates(self):
        """Test extraction with invalid bounding box coordinates."""
        # Negative coordinates
        bbox = BoundingBox(x=-10, y=-10, width=50, height=50)
        detection = DetectionResult(has_signature=True, confidence=0.8, bounding_box=bbox)
        
        result = extract_signature(self.blank_image, detection)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)

    def test_out_of_bounds_bounding_box(self):
        """Test extraction when bounding box extends outside image."""
        # Bounding box that extends outside image
        bbox = BoundingBox(x=150, y=150, width=100, height=100)
        detection = DetectionResult(has_signature=True, confidence=0.8, bounding_box=bbox)
        
        result = extract_signature(self.blank_image, detection)
        
        # Should succeed with clamped bounding box
        self.assertTrue(result.success)
        self.assertIsNotNone(result.extracted_image)

    def test_empty_bounding_box(self):
        """Test extraction with zero-size bounding box."""
        bbox = BoundingBox(x=10, y=10, width=0, height=0)
        detection = DetectionResult(has_signature=True, confidence=0.8, bounding_box=bbox)
        
        result = extract_signature(self.blank_image, detection)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)

    def test_extract_with_metadata_success(self):
        """Test extraction with metadata."""
        # Create a signature image
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        for i in range(50, 250, 5):
            x = i
            y = 50 + 20 * np.sin((i - 50) * 0.1) + 10 * np.sin((i - 50) * 0.3)
            draw.line([(x-2, y-2), (x+2, y+2)], fill='black', width=3)
        
        # Detect and extract with metadata
        detection = detect_signature(img)
        result, metadata = extract_with_metadata(img, detection)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, ExtractionMetadata)
        self.assertEqual(metadata.original_size, (300, 100))
        self.assertEqual(metadata.extracted_size, result.extracted_image.size)
        self.assertTrue(metadata.has_transparency)

    def test_extract_with_metadata_no_signature(self):
        """Test extraction with metadata when no signature detected."""
        detection = DetectionResult(has_signature=False, confidence=0.0, bounding_box=None)
        
        result, metadata = extract_with_metadata(self.blank_image, detection)
        
        self.assertFalse(result.success)
        self.assertIsNone(metadata)


class TestExtractionResultModel(unittest.TestCase):
    """Test the ExtractionResult and ExtractionMetadata data models."""
    
    def test_extraction_result_success(self):
        """Test successful ExtractionResult creation."""
        img = Image.new('RGBA', (100, 50), color=(255, 0, 0, 128))
        result = ExtractionResult(
            success=True,
            extracted_image=img,
            error=None
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.extracted_image, img)
        self.assertIsNone(result.error)
    
    def test_extraction_result_failure(self):
        """Test failed ExtractionResult creation."""
        result = ExtractionResult(
            success=False,
            extracted_image=None,
            error="Test error message"
        )
        
        self.assertFalse(result.success)
        self.assertIsNone(result.extracted_image)
        self.assertEqual(result.error, "Test error message")
    
    def test_extraction_metadata(self):
        """Test ExtractionMetadata creation."""
        bbox = BoundingBox(x=10, y=20, width=30, height=40)
        metadata = ExtractionMetadata(
            original_size=(100, 200),
            extracted_size=(30, 40),
            bounding_box=bbox,
            has_transparency=True
        )
        
        self.assertEqual(metadata.original_size, (100, 200))
        self.assertEqual(metadata.extracted_size, (30, 40))
        self.assertEqual(metadata.bounding_box, bbox)
        self.assertTrue(metadata.has_transparency)


if __name__ == '__main__':
    unittest.main()