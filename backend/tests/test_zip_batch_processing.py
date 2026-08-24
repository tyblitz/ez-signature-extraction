import os
import tempfile
import zipfile
import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from backend.utils.zip_handler import extract_images_from_zip, create_signatures_zip


class TestZipBatchProcessing(unittest.TestCase):
    """Test suite for ZIP file extraction and packaging functions."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a dummy image
        self.img_path1 = self.temp_path / "test_doc1.png"
        self.img_path2 = self.temp_path / "test_doc2.jpg"

        arr = np.full((100, 100, 3), 255, dtype=np.uint8)
        # Add blue ink line
        arr[40:60, 20:80] = [0, 0, 220]
        
        Image.fromarray(arr).save(self.img_path1)
        Image.fromarray(arr).save(self.img_path2)

        # Create test zip file
        self.zip_input_path = self.temp_path / "documents.zip"
        with zipfile.ZipFile(self.zip_input_path, 'w') as zf:
            zf.write(self.img_path1, arcname="test_doc1.png")
            zf.write(self.img_path2, arcname="test_doc2.jpg")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_images_from_zip(self):
        extract_dir = self.temp_path / "unpacked"
        extracted_files = extract_images_from_zip(str(self.zip_input_path), str(extract_dir))

        self.assertEqual(len(extracted_files), 2)
        basenames = [Path(p).name for p in extracted_files]
        self.assertIn("test_doc1.png", basenames)
        self.assertIn("test_doc2.jpg", basenames)

    def test_create_signatures_zip(self):
        zip_output_path = self.temp_path / "signatures_output.zip"
        success, result_path = create_signatures_zip([str(self.img_path1), str(self.img_path2)], str(zip_output_path))

        self.assertTrue(success)
        self.assertTrue(Path(result_path).exists())

        with zipfile.ZipFile(result_path, 'r') as zf:
            names = zf.namelist()
            self.assertIn("test_doc1.png", names)
            self.assertIn("test_doc2.jpg", names)


if __name__ == '__main__':
    unittest.main()
