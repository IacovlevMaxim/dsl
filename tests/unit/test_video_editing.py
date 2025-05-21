import io
import os
import unittest
import unittest.mock
import tempfile
import shutil
from mutagen.mp4 import MP4
from src.main import parser, variables


class TestDSLVideoMetadataEditing(unittest.TestCase):
    def setUp(self):
        variables.clear()
        self.original_path = "C:/Users/user/Desktop/UniFiles/Anul2_Sem2/dsl/tests/temp/test.mp4"
        self.temp_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        shutil.copyfile(self.original_path, self.temp_path)

    def tearDown(self):
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def run_dsl_code(self, code):
        ast = parser.parse(code)
        ast.eval()

    def test_dsl_load_and_set_all_metadata_fields(self):
        code = f'''
        file v = load("{self.temp_path}")
        set(v, "title", "Test Title")
        set(v, "artist", "Test Artist")
        set(v, "album", "Test Album")
        set(v, "genre", "Test Genre")
        set(v, "description", "Test Description")
        save_file(v)
        '''
        self.run_dsl_code(code)

        mp4 = MP4(self.temp_path)
        self.assertEqual(mp4.get("\xa9nam", [""])[0], "Test Title")
        self.assertEqual(mp4.get("\xa9ART", [""])[0], "Test Artist")
        self.assertEqual(mp4.get("\xa9alb", [""])[0], "Test Album")
        self.assertEqual(mp4.get("\xa9gen", [""])[0], "Test Genre")
        self.assertEqual(mp4.get("desc", [""])[0], "Test Description")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_dsl_print_metadata(self, mock_stdout):
        code = f'''
        file v = load("{self.temp_path}")
        set(v, "title", "Printed Title")
        set(v, "artist", "Printed Artist")
        print(v)
        '''
        self.run_dsl_code(code)
        output = mock_stdout.getvalue()
        self.assertIn("title: Printed Title", output)
        self.assertIn("artist: Printed Artist", output)


if __name__ == '__main__':
    unittest.main()
