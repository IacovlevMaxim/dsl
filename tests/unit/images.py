import io
import unittest.mock
<<<<<<< handlePDF
import exiftool
from src.utils.image_metadata import metadata_prefix
from tests.utils.get_output import *
from tests.utils.with_tempfile import *
=======
import eyed3
from eyed3 import AudioFile
from src.main import parser, variables
from tests.utils.get_output import get_output
from tests.utils.with_tempfile import with_tempfile
>>>>>>> dev


class TestMP3MetadataEditing(unittest.TestCase):
    def setUp(self):
        # Clear interpreter variables before each test
        variables.clear()

    def load_audiofile(self, path):
        """Helper to load MP3 file with eyed3."""
        return eyed3.load(path)

    @with_tempfile('mp3')
    def test_load_mp3_file(self, temp_file):
        code = f'file f = load("{temp_file}")'
        ast = parser.parse(code)
        ast.eval()

        self.assertIn('f', variables)
        self.assertEqual(variables['f'].type.name, 'AUDIO_FILE')
        self.assertIsInstance(variables['f'].value, AudioFile)

    @with_tempfile('mp3')
    def test_set_and_save_artist(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "artist", "Test Artist")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertEqual(audiofile.tag.artist, "Test Artist")

    @with_tempfile('mp3')
    def test_set_and_save_album(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "album", "Test Album")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertEqual(audiofile.tag.album, "Test Album")

    @with_tempfile('mp3')
    def test_set_and_save_album_artist(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "album_artist", "Test Album Artist")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertEqual(audiofile.tag.album_artist, "Test Album Artist")

    @with_tempfile('mp3')
    def test_set_and_save_title(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "title", "Test Title")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertEqual(audiofile.tag.title, "Test Title")

    @with_tempfile('mp3')
    def test_set_and_save_track_num(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "track_num", "5")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertEqual(audiofile.tag.track_num[0], 5)

    @with_tempfile('mp3')
    def test_set_multiple_metadata_fields(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "artist", "Multi Artist")
        set(f, "album", "Multi Album")
        set(f, "album_artist", "Multi Album Artist")
        set(f, "title", "Multi Title")
        set(f, "track_num", "7")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertEqual(audiofile.tag.artist, "Multi Artist")
        self.assertEqual(audiofile.tag.album, "Multi Album")
        self.assertEqual(audiofile.tag.album_artist, "Multi Album Artist")
        self.assertEqual(audiofile.tag.title, "Multi Title")
        self.assertEqual(audiofile.tag.track_num[0], 7)

    @with_tempfile('mp3')
    def test_save_file_without_changes(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = self.load_audiofile(temp_file)
        self.assertIsNotNone(audiofile.tag)

    @with_tempfile('mp3')
    def test_set_invalid_metadata_field_raises_error(self, temp_file):
        code = f'''
        file f = load("{temp_file}")
        set(f, "nonexistent_field", "Oops")
        save_file(f)
        '''
        with self.assertRaises(AttributeError):
            ast = parser.parse(code)
            ast.eval()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @with_tempfile('mp3')
    def test_print_mp3_metadata(self, temp_file, mock_stdout):
        code = f'''
        file f = load("{temp_file}")
        print(f)
        '''
        output = get_output(code, mock_stdout)
        self.assertIn("title:", output)
        self.assertIn("artist:", output)


if __name__ == '__main__':
    unittest.main()