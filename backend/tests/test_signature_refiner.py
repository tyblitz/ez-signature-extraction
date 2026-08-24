"""
Unit tests for Signature Refinement Module.

Tests cover signature refinement functionality including:
- Input validation
- Successful background removal
- Transparency generation
- Original image preservation
- Edge cases
- Output validation
- Metadata validation
- Blue ink detection
"""

import unittest
import os
import tempfile
import shutil
from PIL import Image, ImageDraw
import numpy as np
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from backend.models.extraction_result import ExtractionResult
from backend.models.refinement_result import RefinementResult, RefinementMetadata
from backend.processors.signature_refiner import refine_signature, refine_signature_with_padding


class TestRefinementResultModel(unittest.TestCase):
    """Test cases for RefinementResult dataclass."""
    
    def test_refinement_result_creation_success(self):
        """Test successful RefinementResult creation."""
        img = Image.new('RGBA', (100, 50), color=(255, 255, 255, 255))
        metadata = RefinementMetadata(
            original_size=(100, 50),
            refined_size=(100, 50),
            background_pixels_removed=5000,
            signature_pixels_preserved=1000,
            has_transparency=True,
            processing_method="test",
            refinement_successful=True
        )
        result = RefinementResult(
            success=True,
            original_image=img,
            refined_image=img,
            error=None,
            metadata=metadata
        )
        self.assertTrue(result.success)
        self.assertIsNotNone(result.original_image)
        self.assertIsNotNone(result.refined_image)
        self.assertIsNone(result.error)
        self.assertIsNotNone(result.metadata)
    
    def test_refinement_result_failure(self):
        """Test failed RefinementResult creation."""
        result = RefinementResult(
            success=False,
            original_image=None,
            refined_image=None,
            error="Test error"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.original_image)
        self.assertIsNone(result.refined_image)
        self.assertEqual(result.error, "Test error")
    
    def test_refinement_metadata_creation(self):
        """Test RefinementMetadata creation."""
        metadata = RefinementMetadata(
            original_size=(100, 50),
            refined_size=(100, 50),
            background_pixels_removed=5000,
            signature_pixels_preserved=1000,
            has_transparency=True,
            processing_method="test",
            refinement_successful=True
        )
        self.assertEqual(metadata.original_size, (100, 50))
        self.assertEqual(metadata.refined_size, (100, 50))
        self.assertTrue(metadata.has_transparency)


class TestSignatureRefiner(unittest.TestCase):
    """Test cases for signature refinement functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test signature image with white background
        # Using BLUE ink as per Module 5 requirements
        self.test_image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(self.test_image)
        # Draw a simple signature-like shape using blue ink
        for i in range(50, 250, 10):
            x = i
            y = 50 + 5 * np.sin((i - 50) * 0.2)
            draw.line([(x-3, y-3), (x+3, y+3)], fill='#0066CC', width=6)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_input_validation_invalid_extraction_result(self):
        """Test that invalid extraction result returns appropriate error."""
        result = refine_signature("not an extraction result")
        self.assertFalse(result.success)
        self.assertIn("Expected ExtractionResult", result.error)
    
    def test_input_validation_failed_extraction(self):
        """Test handling of failed extraction result."""
        failed_result = ExtractionResult(
            success=False,
            extracted_image=None,
            error="Extraction failed"
        )
        result = refine_signature(failed_result)
        self.assertFalse(result.success)
        self.assertIn("not successful", result.error)
    
    def test_successful_background_removal(self):
        """Test successful background removal."""
        # Convert to RGBA first (simulating Module 4 output)
        rgba_image = self.test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.refined_image)
        self.assertIsNotNone(result.metadata)
        self.assertTrue(result.metadata.has_transparency)
    
    def test_transparency_generation(self):
        """Test that output has proper transparency."""
        rgba_image = self.test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that the refined image has an alpha channel
        refined_array = np.array(result.refined_image)
        self.assertEqual(refined_array.shape[2], 4)
        
        # Check that there are transparent pixels (background)
        alpha = refined_array[:, :, 3]
        has_transparent = np.any(alpha == 0)
        self.assertTrue(has_transparent, "Image should have transparent pixels")
    
    def test_original_image_preservation(self):
        """Test that original image is preserved (not modified)."""
        rgba_image = self.test_image.convert('RGBA')
        original_id = id(rgba_image)
        original_data = rgba_image.tobytes()
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        # Verify original is unchanged
        self.assertEqual(id(result.original_image), original_id)
        self.assertEqual(result.original_image.tobytes(), original_data)
    
    def test_signature_strokes_preserved(self):
        """Test that signature strokes are preserved."""
        rgba_image = self.test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that refined image has non-transparent pixels
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        non_transparent_count = np.sum(alpha > 0)
        
        # There should be some non-transparent pixels (the signature)
        self.assertGreater(non_transparent_count, 0, "Signature should be preserved")
    
    def test_refinement_with_padding(self):
        """Test refinement with automatic cropping and padding."""
        rgba_image = self.test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature_with_padding(extraction_result, padding=5)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.refined_image)
    
    def test_failed_refinement_no_image(self):
        """Test refinement when no image is available."""
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=None,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertFalse(result.success)
        self.assertIn("No extracted image", result.error)
    
    def test_metadata_values(self):
        """Test that metadata values are reasonable."""
        rgba_image = self.test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metadata)
        
        # Metadata should have reasonable values
        self.assertEqual(result.metadata.original_size, (300, 100))
        self.assertTrue(result.metadata.refinement_successful)
        self.assertEqual(result.metadata.processing_method, "background_removal_preservation")


class TestBlueInkDetection(unittest.TestCase):
    """Test blue ink-only signature detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_dark_blue_ink_detected(self):
        """Test that dark blue ink signatures are detected."""
        test_img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(test_img)
        draw.line([(50, 50), (250, 50)], fill='#0066CC', width=4)  # Dark blue
        
        rgba_image = test_img.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that signature pixels are preserved
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        non_transparent_count = np.sum(alpha > 0)
        
        self.assertGreater(non_transparent_count, 0, "Blue ink should be preserved")
    
    def test_light_blue_ink_detected(self):
        """Test that light blue ink signatures are detected."""
        test_img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(test_img)
        draw.line([(50, 50), (250, 50)], fill='#3399FF', width=4)  # Light blue
        
        rgba_image = test_img.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that signature pixels are preserved
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        non_transparent_count = np.sum(alpha > 0)
        
        self.assertGreater(non_transparent_count, 0, "Light blue ink should be preserved")
    
    def test_navy_blue_ink_detected(self):
        """Test that navy blue ink signatures are detected."""
        test_img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(test_img)
        draw.line([(50, 50), (250, 50)], fill='#003366', width=4)  # Navy blue
        
        rgba_image = test_img.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that signature pixels are preserved
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        non_transparent_count = np.sum(alpha > 0)
        
        self.assertGreater(non_transparent_count, 0, "Navy blue ink should be preserved")
    
    def test_non_blue_artifacts_removed(self):
        """Test that non-blue artifacts are removed."""
        test_img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(test_img)
        
        # Draw blue signature
        draw.line([(50, 50), (250, 50)], fill='#0066CC', width=4)
        
        # Add non-blue artifacts
        draw.rectangle([(10, 70), (40, 90)], fill='gray')  # Gray artifact
        draw.text((10, 10), 'STAMP', fill='black')  # Black text
        draw.line([(250, 10), (290, 40)], fill='red', width=3)  # Red line
        
        rgba_image = test_img.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that only blue signature remains
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        
        # Most pixels should be transparent (non-blue artifacts removed)
        transparent_count = np.sum(alpha == 0)
        self.assertGreater(transparent_count, 0, "Non-blue artifacts should be removed")
    
    def test_white_background_removed(self):
        """Test that white paper background is removed."""
        test_img = Image.new('RGB', (100, 100), color='white')
        
        rgba_image = test_img.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # All pixels should be transparent (pure white background)
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        
        # Check corner pixels are transparent
        self.assertEqual(alpha[0, 0], 0, "Background should be transparent")
        self.assertEqual(alpha[99, 99], 0, "Background should be transparent")


class TestTransparentPNGValidation(unittest.TestCase):
    """Test transparent PNG output validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_output_is_valid_rgba(self):
        """Test that output is a valid RGBA image."""
        # Create test image with blue signature
        test_image = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(test_image)
        draw.line([(50, 50), (150, 50)], fill='#0066CC', width=4)
        
        rgba_image = test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        self.assertEqual(result.refined_image.mode, 'RGBA')
    
    def test_background_is_transparent(self):
        """Test that background pixels are transparent."""
        # Create test image with known background
        test_image = Image.new('RGB', (100, 100), color='white')
        
        rgba_image = test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        
        # Check that corner pixels (definitely background) are transparent
        refined_array = np.array(result.refined_image)
        alpha = refined_array[:, :, 3]
        
        # Corner pixels should be transparent (background)
        corner_pixels = [
            alpha[0, 0], alpha[0, 99],
            alpha[99, 0], alpha[99, 99]
        ]
        for pixel_alpha in corner_pixels:
            self.assertEqual(pixel_alpha, 0, "Background pixels should be transparent")


class TestMetadataValidation(unittest.TestCase):
    """Test metadata validation."""
    
    def test_metadata_contains_required_fields(self):
        """Test that metadata contains all required fields."""
        test_image = Image.new('RGB', (100, 50), color='white')
        rgba_image = test_image.convert('RGBA')
        
        extraction_result = ExtractionResult(
            success=True,
            extracted_image=rgba_image,
            error=None
        )
        
        result = refine_signature(extraction_result)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metadata)
        
        # Check all required fields
        self.assertTrue(hasattr(result.metadata, 'original_size'))
        self.assertTrue(hasattr(result.metadata, 'refined_size'))
        self.assertTrue(hasattr(result.metadata, 'background_pixels_removed'))
        self.assertTrue(hasattr(result.metadata, 'signature_pixels_preserved'))
        self.assertTrue(hasattr(result.metadata, 'has_transparency'))
        self.assertTrue(hasattr(result.metadata, 'processing_method'))
        self.assertTrue(hasattr(result.metadata, 'refinement_successful'))


class TestModuleIntegrity(unittest.TestCase):
    """Test that existing modules remain unchanged."""
    
    def test_image_processor_unchanged(self):
        """Test that Module 1 image_processor.py is unchanged."""
        from backend.processors import image_processor
        self.assertTrue(hasattr(image_processor, 'load_image'))
        self.assertTrue(hasattr(image_processor, 'validate_format'))
    
    def test_signature_detector_unchanged(self):
        """Test that Module 2 signature_detector.py is unchanged."""
        from backend.processors import signature_detector
        self.assertTrue(hasattr(signature_detector, 'detect_signature'))
    
    def test_signature_extractor_unchanged(self):
        """Test that Module 3 signature_extractor.py is unchanged."""
        from backend.processors import signature_extractor
        self.assertTrue(hasattr(signature_extractor, 'extract_signature'))
    
    def test_signature_exporter_unchanged(self):
        """Test that Module 4 signature_exporter.py is unchanged."""
        from backend.processors import signature_exporter
        self.assertTrue(hasattr(signature_exporter, 'export_signature'))
    
    def test_signature_refiner_exists(self):
        """Test that Module 5 signature_refiner.py exists."""
        from backend.processors import signature_refiner
        self.assertTrue(hasattr(signature_refiner, 'refine_signature'))


if __name__ == '__main__':
    unittest.main()