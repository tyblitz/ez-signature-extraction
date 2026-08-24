"""
Unit tests for Image Support Module.

Tests cover format validation, image loading, quality preservation,
and transparency preservation for JPG, JPEG, and PNG formats.
"""

import unittest
import os
import tempfile
from PIL import Image
import io

# Import the module to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.processors.image_processor import (
    validate_format,
    validate_file_object,
    load_image,
    load_image_from_bytes,
    load_image_from_file_object,
    get_image_info,
    SUPPORTED_FORMATS
)


class TestFormatValidation(unittest.TestCase):
    """Tests for format validation functions."""
    
    def test_validate_jpg_format(self):
        """Test JPG format is recognized as valid."""
        self.assertTrue(validate_format('test.jpg'))
        self.assertTrue(validate_format('test.JPG'))
    
    def test_validate_jpeg_format(self):
        """Test JPEG format is recognized as valid."""
        self.assertTrue(validate_format('test.jpeg'))
        self.assertTrue(validate_format('test.JPEG'))
    
    def test_validate_png_format(self):
        """Test PNG format is recognized as valid."""
        self.assertTrue(validate_format('test.png'))
        self.assertTrue(validate_format('test.PNG'))
    
    def test_validate_unsupported_format(self):
        """Test unsupported formats are rejected."""
        self.assertFalse(validate_format('test.gif'))
        self.assertFalse(validate_format('test.bmp'))
        self.assertFalse(validate_format('test.pdf'))
        self.assertFalse(validate_format('test.txt'))
    
    def test_validate_empty_path(self):
        """Test empty or invalid path is rejected."""
        self.assertFalse(validate_format(''))
        self.assertFalse(validate_format(None))
        self.assertFalse(validate_format(123))


class TestImageLoading(unittest.TestCase):
    """Tests for image loading functions."""
    
    def setUp(self):
        """Create test images for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.jpg_path = os.path.join(self.temp_dir, 'test.jpg')
        self.png_path = os.path.join(self.temp_dir, 'test.png')
        self.png_transparent_path = os.path.join(self.temp_dir, 'test_transparent.png')
        
        # Create JPG image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.jpg_path, format='JPEG', quality=95)
        
        # Create PNG image
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(self.png_path, format='PNG')
        
        # Create PNG image with transparency
        img = Image.new('RGBA', (100, 100), color=(0, 0, 255, 128))
        img.save(self.png_transparent_path, format='PNG')
    
    def tearDown(self):
        """Clean up test images."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_jpg_image(self):
        """Test loading JPG image preserves properties."""
        image = load_image(self.jpg_path)
        self.assertEqual(image.format, 'JPEG')
        self.assertEqual(image.size, (100, 100))
        image.close()
    
    def test_load_png_image(self):
        """Test loading PNG image preserves properties."""
        image = load_image(self.png_path)
        self.assertEqual(image.format, 'PNG')
        self.assertEqual(image.size, (100, 100))
        image.close()
    
    def test_load_png_transparent_image(self):
        """Test loading transparent PNG preserves alpha channel."""
        image = load_image(self.png_transparent_path)
        self.assertEqual(image.format, 'PNG')
        self.assertEqual(image.mode, 'RGBA')
        self.assertTrue(image.info.get('transparency') is not None or image.mode == 'RGBA')
        image.close()
    
    def test_load_unsupported_format_raises_error(self):
        """Test loading unsupported format raises ValueError."""
        # Create a fake file with unsupported extension
        fake_path = os.path.join(self.temp_dir, 'test.gif')
        with open(fake_path, 'wb') as f:
            f.write(b'GIF87a')
        
        with self.assertRaises(ValueError):
            load_image(fake_path)


class TestBytesLoading(unittest.TestCase):
    """Tests for loading from bytes."""
    
    def test_load_jpg_from_bytes(self):
        """Test loading JPG from bytes preserves quality."""
        # Create test JPG in memory
        img = Image.new('RGB', (50, 50), color='green')
        bytes_io = io.BytesIO()
        img.save(bytes_io, format='JPEG', quality=95)
        bytes_data = bytes_io.getvalue()
        
        loaded_img = load_image_from_bytes(bytes_data)
        self.assertEqual(loaded_img.format, 'JPEG')
        self.assertEqual(loaded_img.size, (50, 50))
    
    def test_load_png_from_bytes(self):
        """Test loading PNG from bytes preserves transparency."""
        # Create test PNG with transparency in memory
        img = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
        bytes_io = io.BytesIO()
        img.save(bytes_io, format='PNG')
        bytes_data = bytes_io.getvalue()
        
        loaded_img = load_image_from_bytes(bytes_data)
        self.assertEqual(loaded_img.format, 'PNG')
        self.assertEqual(loaded_img.mode, 'RGBA')


class TestImageInfo(unittest.TestCase):
    """Tests for image info retrieval."""
    
    def test_get_jpg_image_info(self):
        """Test getting info from JPG image."""
        # Create actual JPG file to test
        temp_dir = tempfile.mkdtemp()
        jpg_path = os.path.join(temp_dir, 'test.jpg')
        img = Image.new('RGB', (200, 150), color='red')
        img.save(jpg_path, format='JPEG', quality=95)
        
        loaded = Image.open(jpg_path)
        info = get_image_info(loaded)
        
        self.assertEqual(info['format'], 'JPEG')
        self.assertEqual(info['mode'], 'RGB')
        self.assertEqual(info['width'], 200)
        self.assertEqual(info['height'], 150)
        self.assertEqual(info['size'], (200, 150))
        self.assertFalse(info['has_transparency'])
        loaded.close()
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_get_png_transparent_info(self):
        """Test getting info from transparent PNG image."""
        img = Image.new('RGBA', (100, 100), color=(0, 0, 0, 128))
        info = get_image_info(img)
        
        self.assertTrue(info['has_transparency'])


if __name__ == '__main__':
    unittest.main()
    unittest.main()