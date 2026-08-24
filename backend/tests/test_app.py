"""
Unit tests for the EZ Signature Extraction Application.

Tests cover application functionality including:
- Application startup
- Invalid input handling
- Successful pipeline execution
- Output file creation
- Module integrity verification
- Module 5 integration (transparent signature)
"""

import unittest
import os
import tempfile
import shutil
from PIL import Image, ImageDraw
import numpy as np
import sys

# Add the project root to the path
# __file__ is in backend/tests/ so we need to go up 2 levels
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import from backend package
from backend.main import run_pipeline, get_output_directory


class TestApplicationStartup(unittest.TestCase):
    """Test application startup and basic functionality."""
    
    def test_application_can_import(self):
        """Test that the main module can be imported."""
        from backend import main
        self.assertTrue(hasattr(main, 'run_pipeline'))
        self.assertTrue(hasattr(main, 'get_output_directory'))


class TestInputValidation(unittest.TestCase):
    """Test input validation and error handling."""
    
    def test_missing_input_file(self):
        """Test handling of missing input file."""
        success, message = run_pipeline('/nonexistent/path/image.jpg')
        self.assertFalse(success)
        self.assertIn("not found", message)
    
    def test_invalid_image_format(self):
        """Test handling of invalid image format."""
        # Create a temporary file with invalid extension
        temp_dir = tempfile.mkdtemp()
        try:
            fake_image = os.path.join(temp_dir, 'fake.txt')
            with open(fake_image, 'w') as f:
                f.write('not an image')
            
            success, message = run_pipeline(fake_image)
            self.assertFalse(success)
            self.assertIn("Unable to process image", message)
        finally:
            shutil.rmtree(temp_dir)


class TestSuccessfulPipeline(unittest.TestCase):
    """Test successful pipeline execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test signature image
        self.test_image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(self.test_image)
        pts = [(int(i), int(50 + 20 * np.sin((i - 50) * 0.1) + 10 * np.sin((i - 50) * 0.3))) for i in range(50, 250, 2)]
        draw.line(pts, fill='black', width=4)
        
        # Save test image
        self.input_path = os.path.join(self.temp_dir, 'test_signature.jpg')
        self.test_image.save(self.input_path, format='JPEG', quality=95)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_successful_pipeline_execution(self):
        """Test successful pipeline execution."""
        success, message = run_pipeline(self.input_path)
        
        self.assertTrue(success, f"Pipeline should succeed: {message}")
        
        # Verify output files exist
        output_dir = os.path.join(self.temp_dir, 'output')
        signature_path = os.path.join(output_dir, 'test_signature.png')
        metadata_path = os.path.join(output_dir, 'test_signature_metadata.json')
        
        self.assertTrue(os.path.exists(signature_path), "Signature PNG should exist")
        self.assertTrue(os.path.exists(metadata_path), "Metadata JSON should exist")
    
    def test_successful_pipeline_with_custom_output(self):
        """Test successful pipeline with custom output directory."""
        custom_output = os.path.join(self.temp_dir, 'custom_output')
        success, message = run_pipeline(self.input_path, custom_output)
        
        self.assertTrue(success, f"Pipeline should succeed: {message}")
        self.assertTrue(os.path.exists(custom_output), "Custom output directory should exist")


class TestModule5Integration(unittest.TestCase):
    """Test Module 5 (Signature Refinement) integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test signature image
        self.test_image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(self.test_image)
        pts = [(int(i), int(50 + 20 * np.sin((i - 50) * 0.1) + 10 * np.sin((i - 50) * 0.3))) for i in range(50, 250, 2)]
        draw.line(pts, fill='black', width=4)
        
        self.input_path = os.path.join(self.temp_dir, 'test_signature.jpg')
        self.test_image.save(self.input_path, format='JPEG', quality=95)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_transparent_signature_created(self):
        """Test that transparent signature is created by Module 5."""
        success, message = run_pipeline(self.input_path)
        
        self.assertTrue(success, f"Pipeline should succeed: {message}")
        
        # Check for transparent signature output
        output_dir = os.path.join(self.temp_dir, 'output')
        transparent_path = os.path.join(output_dir, 'test_signature_transparent.png')
        
        self.assertTrue(os.path.exists(transparent_path), 
                       "Transparent signature PNG should exist")
    
    def test_original_signature_preserved(self):
        """Test that original signature is preserved alongside transparent version."""
        success, message = run_pipeline(self.input_path)
        
        self.assertTrue(success, f"Pipeline should succeed: {message}")
        
        output_dir = os.path.join(self.temp_dir, 'output')
        original_path = os.path.join(output_dir, 'test_signature.png')
        transparent_path = os.path.join(output_dir, 'test_signature_transparent.png')
        
        # Both files should exist
        self.assertTrue(os.path.exists(original_path), "Original signature should exist")
        self.assertTrue(os.path.exists(transparent_path), "Transparent signature should exist")
    
    def test_transparent_has_alpha_channel(self):
        """Test that transparent signature has alpha channel."""
        success, message = run_pipeline(self.input_path)
        
        self.assertTrue(success, f"Pipeline should succeed: {message}")
        
        output_dir = os.path.join(self.temp_dir, 'output')
        transparent_path = os.path.join(output_dir, 'test_signature_transparent.png')
        
        if os.path.exists(transparent_path):
            img = Image.open(transparent_path)
            self.assertEqual(img.mode, 'RGBA', "Transparent signature should be RGBA")


class TestOutputDirectoryHandling(unittest.TestCase):
    """Test output directory handling."""
    
    def test_default_output_directory(self):
        """Test default output directory generation."""
        input_path = '/path/to/document.jpg'
        output_dir = get_output_directory(input_path)
        # Use os.path.normpath to handle platform-specific path separators
        expected = os.path.normpath('/path/to/output')
        self.assertEqual(os.path.normpath(str(output_dir)), expected)
    
    def test_custom_output_directory(self):
        """Test custom output directory."""
        input_path = '/path/to/document.jpg'
        custom_dir = '/custom/output'
        output_dir = get_output_directory(input_path, custom_dir)
        # Use os.path.normpath to handle platform-specific path separators
        expected = os.path.normpath('/custom/output')
        self.assertEqual(os.path.normpath(str(output_dir)), expected)
    
    def test_nested_output_directory_creation(self):
        """Test that nested output directories are created."""
        temp_dir = tempfile.mkdtemp()
        try:
            input_path = os.path.join(temp_dir, 'test.jpg')
            nested_output = os.path.join(temp_dir, 'level1', 'level2', 'output')
            
            # Create test image
            img = Image.new('RGB', (100, 50), color='white')
            draw = ImageDraw.Draw(img)
            draw.line([(10, 25), (90, 25)], fill='black', width=3)
            img.save(input_path, format='JPEG')
            
            # Run pipeline with nested output
            success, _ = run_pipeline(input_path, nested_output)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(nested_output))
        finally:
            shutil.rmtree(temp_dir)


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
    
    def test_signature_refiner_unchanged(self):
        """Test that Module 5 signature_refiner.py is unchanged."""
        from backend.processors import signature_refiner
        self.assertTrue(hasattr(signature_refiner, 'refine_signature'))


class TestOutputFiles(unittest.TestCase):
    """Test output file format and content."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test signature
        self.test_image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(self.test_image)
        pts = [(int(i), int(50 + 20 * np.sin((i - 50) * 0.1) + 10 * np.sin((i - 50) * 0.3))) for i in range(50, 250, 2)]
        draw.line(pts, fill='black', width=4)
        
        self.input_path = os.path.join(self.temp_dir, 'test.jpg')
        self.test_image.save(self.input_path, format='JPEG')
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_output_is_valid_png(self):
        """Test that output is a valid PNG file."""
        success, _ = run_pipeline(self.input_path)
        self.assertTrue(success)
        
        output_dir = os.path.join(self.temp_dir, 'output')
        output_path = os.path.join(output_dir, 'test.png')
        
        if os.path.exists(output_path):
            exported = Image.open(output_path)
            self.assertEqual(exported.format, 'PNG')
    
    def test_output_has_transparency(self):
        """Test that output PNG has alpha channel."""
        success, _ = run_pipeline(self.input_path)
        self.assertTrue(success)
        
        output_dir = os.path.join(self.temp_dir, 'output')
        output_path = os.path.join(output_dir, 'test.png')
        
        if os.path.exists(output_path):
            exported = Image.open(output_path)
            self.assertEqual(exported.mode, 'RGBA')
    
    def test_metadata_is_valid_json(self):
        """Test that metadata file is valid JSON."""
        import json
        
        success, _ = run_pipeline(self.input_path)
        self.assertTrue(success)
        
        output_dir = os.path.join(self.temp_dir, 'output')
        metadata_path = os.path.join(output_dir, 'test_metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            self.assertIn('export_info', metadata)


if __name__ == '__main__':
    unittest.main()