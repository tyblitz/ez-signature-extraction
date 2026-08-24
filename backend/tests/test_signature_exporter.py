"""
Unit tests for Signature Export Module.

Tests cover signature export functionality including:
- Input validation
- Successful export cases
- Failed export cases
- Edge cases
- Output validation
- File integrity
"""

import unittest
import os
import tempfile
import json
from PIL import Image
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.processors.signature_exporter import export_signature, export_with_details
from backend.models.extraction_result import ExtractionResult
from backend.models.export_result import ExportResult, ExportMetadata
from backend.models.detection_result import DetectionResult, BoundingBox


class TestSignatureExporter(unittest.TestCase):
    """Test cases for the signature export module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test signature image (RGBA with transparency)
        self.test_signature = Image.new('RGBA', (100, 50), color=(255, 255, 255, 0))
        # Draw a simple signature
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.test_signature)
        draw.line([(10, 25), (90, 25)], fill='black', width=3)
        
        # Create a valid extraction result
        self.valid_extraction = ExtractionResult(
            success=True,
            extracted_image=self.test_signature,
            error=None
        )
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_input_validation_invalid_extraction_result(self):
        """Test that invalid extraction result input returns appropriate error."""
        result = export_signature("not an extraction result", self.temp_dir, "test")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNotNone(result.error)
        self.assertIn("ExtractionResult", result.error)
    
    def test_input_validation_failed_extraction(self):
        """Test that failed extraction result returns appropriate error."""
        failed_extraction = ExtractionResult(
            success=False,
            extracted_image=None,
            error="Signature not found"
        )
        
        result = export_signature(failed_extraction, self.temp_dir, "test")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNotNone(result.error)
        self.assertIn("not successful", result.error)
    
    def test_input_validation_missing_image(self):
        """Test that missing extracted image returns appropriate error."""
        no_image_extraction = ExtractionResult(
            success=True,
            extracted_image=None,
            error=None
        )
        
        result = export_signature(no_image_extraction, self.temp_dir, "test")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNotNone(result.error)
    
    def test_input_validation_invalid_output_dir(self):
        """Test that invalid output directory returns appropriate error."""
        result = export_signature(self.valid_extraction, "", "test")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNotNone(result.error)
    
    def test_invalid_format(self):
        """Test that invalid format returns appropriate error."""
        result = export_signature(self.valid_extraction, self.temp_dir, "test", format="GIF")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNotNone(result.error)
        self.assertIn("Unsupported format", result.error)
    
    def test_successful_png_export(self):
        """Test successful PNG export."""
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="PNG"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.output_path)
        self.assertTrue(os.path.exists(result.output_path))
        self.assertEqual(result.output_path.endswith('.png'), True)
        
        # Verify file is valid PNG
        exported = Image.open(result.output_path)
        self.assertEqual(exported.format, 'PNG')
        self.assertEqual(exported.size, (100, 50))
        print(f"  Exported to: {result.output_path}")
    
    def test_successful_jpeg_export(self):
        """Test successful JPEG export."""
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="JPEG"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.output_path)
        self.assertTrue(os.path.exists(result.output_path))
        self.assertEqual(result.output_path.endswith('.jpg'), True)
        
        # Verify file is valid JPEG
        exported = Image.open(result.output_path)
        self.assertEqual(exported.format, 'JPEG')
    
    def test_png_transparency_preserved(self):
        """Test that PNG transparency is preserved in export."""
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="PNG"
        )
        
        self.assertTrue(result.success)
        
        # Verify transparency is preserved
        exported = Image.open(result.output_path)
        self.assertEqual(exported.mode, 'RGBA')
    
    def test_metadata_export(self):
        """Test metadata export functionality."""
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="PNG",
            export_metadata=True
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metadata_path)
        self.assertTrue(os.path.exists(result.metadata_path))
        
        # Verify metadata file content
        with open(result.metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.assertIn('export_info', metadata)
        self.assertEqual(metadata['export_info']['output_format'], 'PNG')
        # JSON serializes tuples as lists
        self.assertEqual(metadata['export_info']['original_size'], [100, 50])
    
    def test_no_metadata_export(self):
        """Test export without metadata."""
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="PNG",
            export_metadata=False
        )
        
        self.assertTrue(result.success)
        self.assertIsNone(result.metadata_path)
    
    def test_compression_parameter(self):
        """Test compression parameter for PNG."""
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="PNG",
            compression=6
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.output_path)
    
    def test_export_with_details(self):
        """Test export_with_details function."""
        result, metadata = export_with_details(
            self.valid_extraction,
            self.temp_dir,
            "test_signature",
            format="PNG"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, ExportMetadata)
        self.assertEqual(metadata.format, 'PNG')
        self.assertEqual(metadata.original_size, (100, 50))
    
    def test_export_with_details_no_signature(self):
        """Test export_with_details with failed extraction."""
        failed_extraction = ExtractionResult(
            success=False,
            extracted_image=None,
            error="No signature found"
        )
        
        result, metadata = export_with_details(
            failed_extraction,
            self.temp_dir,
            "test"
        )
        
        self.assertFalse(result.success)
        self.assertIsNone(metadata)
    
    def test_output_path_predictable(self):
        """Test that output paths are predictable."""
        filename = "my_signature"
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            filename,
            format="PNG"
        )
        
        expected_path = os.path.join(self.temp_dir, f"{filename}.png")
        self.assertEqual(result.output_path, expected_path)
    
    def test_filename_sanitization(self):
        """Test that filenames are properly sanitized."""
        # Filename with path separators
        result = export_signature(
            self.valid_extraction,
            self.temp_dir,
            "test/path/file",
            format="PNG"
        )
        
        self.assertTrue(result.success)
        # Path separators should be replaced
        self.assertNotIn('/', result.output_path.replace(self.temp_dir, ''))
    
    def test_creates_output_directory(self):
        """Test that output directory is created if it doesn't exist."""
        new_dir = os.path.join(self.temp_dir, "new_subdir", "nested")
        
        result = export_signature(
            self.valid_extraction,
            new_dir,
            "test",
            format="PNG"
        )
        
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(new_dir))


class TestExportResultModel(unittest.TestCase):
    """Test the ExportResult and ExportMetadata data models."""
    
    def test_export_result_success(self):
        """Test successful ExportResult creation."""
        result = ExportResult(
            success=True,
            output_path="/path/to/output.png",
            metadata_path="/path/to/metadata.json",
            error=None
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, "/path/to/output.png")
        self.assertEqual(result.metadata_path, "/path/to/metadata.json")
        self.assertIsNone(result.error)
    
    def test_export_result_failure(self):
        """Test failed ExportResult creation."""
        result = ExportResult(
            success=False,
            output_path=None,
            metadata_path=None,
            error="Test error"
        )
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNone(result.metadata_path)
        self.assertEqual(result.error, "Test error")
    
    def test_export_metadata_creation(self):
        """Test ExportMetadata creation."""
        metadata = ExportMetadata(
            format='PNG',
            original_size=(100, 50),
            file_size_bytes=1024,
            compression='compress_level=6',
            export_options={'format': 'PNG', 'compression': 6}
        )
        
        self.assertEqual(metadata.format, 'PNG')
        self.assertEqual(metadata.original_size, (100, 50))
        self.assertEqual(metadata.file_size_bytes, 1024)
        self.assertEqual(metadata.compression, 'compress_level=6')


if __name__ == '__main__':
    unittest.main()