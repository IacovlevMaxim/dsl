import io
import unittest.mock
from mutagen.mp4 import MP4
from tests.utils.with_tempfile import *
from tests.utils.get_output import *


class TestDSLVideoMetadataEditing(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @with_tempfile('mp4')
    def test_dsl_load_and_set_all_metadata_fields(self, temp_file, mock_stdout):
        code = f'''
        file v = load("{temp_file}")
        set(v, "title", "Test Title")
        set(v, "artist", "Test Artist")
        set(v, "album", "Test Album")
        set(v, "genre", "Test Genre")
        set(v, "description", "Test Description")
        save_file(v)
        '''
        get_output(code, mock_stdout)

        mp4 = MP4(temp_file)
        self.assertEqual(mp4.get("©nam", [""])[0], "Test Title")
        self.assertEqual(mp4.get("©ART", [""])[0], "Test Artist")
        self.assertEqual(mp4.get("©alb", [""])[0], "Test Album")
        self.assertEqual(mp4.get("©gen", [""])[0], "Test Genre")
        self.assertEqual(mp4.get("desc", [""])[0], "Test Description")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @with_tempfile('mp4')
    def test_dsl_print_metadata(self, temp_file, mock_stdout):
        code = f'''
        file v = load("{temp_file}")
        set(v, "title", "Printed Title")
        set(v, "artist", "Printed Artist")
        print(v)
        '''

        output = get_output(code, mock_stdout)
        self.assertIn("title: Printed Title", output)
        self.assertIn("artist: Printed Artist", output)


if __name__ == '__main__':
    unittest.main()
