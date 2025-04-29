import os
import unittest
from pypdf import PdfReader, PdfWriter


class TestPDFMetadataEditing(unittest.TestCase):

    def setUp(self):
        self.test_pdf_path = "test_temp.pdf"
        self.create_dummy_pdf(self.test_pdf_path)

    def tearDown(self):
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)

    def create_dummy_pdf(self, path):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_metadata({
            "/Title": "Initial Title",
            "/Author": "Initial Author"
        })
        with open(path, "wb") as f:
            writer.write(f)

    def test_load_pdf_file(self):
        """Test loading a PDF file."""
        reader = PdfReader(self.test_pdf_path)
        self.assertIsNotNone(reader)
        self.assertIsInstance(reader, PdfReader)

    def test_edit_and_verify_metadata(self):
        """Test changing and verifying metadata fields."""
        reader = PdfReader(self.test_pdf_path)
        writer = PdfWriter()
        writer.append(reader)
        writer.add_metadata({
            "/Title": "Updated Title",
            "/Author": "Updated Author",
            "/Subject": "Updated Subject",
            "/Keywords": "Test,PDF,Metadata"
        })

        with open(self.test_pdf_path, "wb") as f:
            writer.write(f)

        # Reload and verify
        reloaded_reader = PdfReader(self.test_pdf_path)
        metadata = reloaded_reader.metadata

        self.assertEqual(metadata.get("/Title"), "Updated Title")
        self.assertEqual(metadata.get("/Author"), "Updated Author")
        self.assertEqual(metadata.get("/Subject"), "Updated Subject")
        self.assertEqual(metadata.get("/Keywords"), "Test,PDF,Metadata")

    def test_save_without_changes(self):
        """Test saving without changing metadata."""
        reader = PdfReader(self.test_pdf_path)
        writer = PdfWriter()
        writer.append(reader)
        writer.add_metadata(reader.metadata)

        with open(self.test_pdf_path, "wb") as f:
            writer.write(f)

        # Reload and verify metadata still exists
        reloaded_reader = PdfReader(self.test_pdf_path)
        metadata = reloaded_reader.metadata
        self.assertIn("/Title", metadata)
        self.assertIn("/Author", metadata)


if __name__ == "__main__":
    unittest.main()
