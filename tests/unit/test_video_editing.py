import io
import os
import shutil
import tempfile
import unittest
import unittest.mock
from src.main import parser, variables
from mutagen.mp4 import MP4

class TestVideoMetadataEditing(unittest.TestCase):
    def setUp(self):
        variables.clear()
        self.temp_files = []

    def tearDown(self):
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def create_temp_mp4(self):
        """Copies a real MP4 file and returns its filename."""
        src_mp4 = r"C:\Users\user\Desktop\UniFiles\Anul2_Sem2\dsl\tests\temp\test.mp4"
        dst_dir = os.getcwd()
        dst_path = os.path.join(dst_dir, "test.mp4")
        shutil.copyfile(src_mp4, dst_path)
        self.temp_files.append(dst_path)
        return "test.mp4"  # Return only filename

    def run_dsl_code(self, code):
        """Helper to parse and run DSL code."""
        ast = parser.parse(code)
        if ast is None:
            raise ValueError("Parser returned None. DSL code might be invalid.")
        ast.eval()

    def load_video(self, path):
        """Helper to reload the MP4 file for verification."""
        return MP4(path)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_load_video_file(self, mock_stdout):
        mp4_filename = self.create_temp_mp4()

        code = f"""
f = load("{mp4_filename}")
print(f)
"""
        try:
            self.run_dsl_code(code)
            output = mock_stdout.getvalue()
            self.assertIn("title:", output)
            self.assertIn("artist:", output)
        except Exception as e:
            self.fail(f"Test failed during file load or print: {e}")

    def test_edit_and_save_metadata_fields(self):
        mp4_filename = self.create_temp_mp4()

        code = f"""
f = load("{mp4_filename}")
set(f, "title", "Test Video Title")
set(f, "artist", "Test Video Artist")
set(f, "album", "Test Video Album")
set(f, "genre", "Action")
set(f, "description", "Test description for video")
save_file(f)
"""
        try:
            self.run_dsl_code(code)
        except Exception as e:
            self.fail(f"Test failed during metadata edit/save: {e}")

        video = self.load_video(mp4_filename)

        self.assertEqual(video.get('\xa9nam', [""])[0], "Test Video Title")
        self.assertEqual(video.get('\xa9ART', [""])[0], "Test Video Artist")
        self.assertEqual(video.get('\xa9alb', [""])[0], "Test Video Album")
        self.assertEqual(video.get('\xa9gen', [""])[0], "Action")
        self.assertEqual(video.get('desc', [""])[0], "Test description for video")

    def test_save_file_without_changes(self):
        mp4_filename = self.create_temp_mp4()

        code = f"""
f = load("{mp4_filename}")
save_file(f)
"""
        try:
            self.run_dsl_code(code)
        except Exception as e:
            self.fail(f"Test failed during save without changes: {e}")

        video = self.load_video(mp4_filename)
        self.assertIsNotNone(video.tags)

if __name__ == '__main__':
    unittest.main()
