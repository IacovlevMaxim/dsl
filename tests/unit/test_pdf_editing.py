import io
import os
import unittest
from unittest import mock
import tempfile
import shutil
import textwrap
from pypdf import PdfReader
from src.main import parser, variables


class TestDSLPDFMetadataEditing(unittest.TestCase):
    def setUp(self):
        variables.clear()

        # Resolve path to test.pdf
        self.original_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp/test.pdf"))
        self.temp_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name

        print("Looking for file at:", self.original_path)
        print("Exists?", os.path.exists(self.original_path))

        shutil.copyfile(self.original_path, self.temp_path)

    def tearDown(self):
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def run_dsl_code(self, code: str):
        print("Running DSL code:\n", code)
        ast = parser.parse(code)
        ast.eval()

    def test_dsl_load_and_set_all_metadata_fields(self):
        safe_path = self.temp_path
        code = textwrap.dedent(f'''
            file p = load("{safe_path}")
            set(p, "Author", "Test Author")
            set(p, "Title", "Test Title")
            set(p, "Subject", "Test Subject")
            set(p, "Keywords", "DSL, Test")
            save_file(p)
        ''')
        self.run_dsl_code(code)

        reader = PdfReader(self.temp_path)
        metadata = reader.metadata
        self.assertEqual(str(metadata.get("/Author", "")), "Test Author")
        self.assertEqual(str(metadata.get("/Title", "")), "Test Title")
        self.assertEqual(str(metadata.get("/Subject", "")), "Test Subject")
        self.assertEqual(str(metadata.get("/Keywords", "")), "DSL, Test")

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_dsl_print_metadata(self, mock_stdout):
        safe_path = self.temp_path.replace('\\', '\\\\')
        code = textwrap.dedent(f'''
            file p = load("{safe_path}")
            set(p, "Title", "Printed Title")
            print(p)
        ''')
        self.run_dsl_code(code)

        output = mock_stdout.getvalue()
        print("DSL Output:\n", output)
        self.assertIn("/Title: Printed Title", output)


if __name__ == '__main__':
    unittest.main()
