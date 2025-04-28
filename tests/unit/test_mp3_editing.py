import io
import os
import tempfile
import unittest
import unittest.mock
import eyed3
from eyed3 import AudioFile
from src.main import parser, variables


class TestMP3MetadataEditing(unittest.TestCase):
    def setUp(self):
        # Clear interpreter variables before each test
        variables.clear()
        self.temp_files = []

    def tearDown(self):
        # Clean up temporary files
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def create_temp_mp3(self):
        """Create a valid minimal MP3 file with ID3 tag."""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b'ID3\x03\x00\x00\x00\x00\x00\x00')  # Minimal MP3 header
            tmp.flush()
            self.temp_files.append(tmp.name)

            # Ensure the MP3 file has a tag
            audiofile = eyed3.load(tmp.name)
            if audiofile.tag is None:
                audiofile.initTag()
                audiofile.tag.artist = "Temp Artist"
                audiofile.tag.save()

            return tmp.name

    def run_dsl_code(self, code):
        """Helper to parse and evaluate DSL code."""
        ast = parser.parse(code)
        ast.eval()

    def load_audiofile(self, path):
        """Helper to load MP3 file with eyed3."""
        return eyed3.load(path)

    def test_load_mp3_file(self):
        mp3_path = self.create_temp_mp3()

        code = f'file f = load("{mp3_path}")'
        self.run_dsl_code(code)

        self.assertIn('f', variables)
        self.assertEqual(variables['f'].type.name, 'AUDIO_FILE')
        self.assertIsInstance(variables['f'].value, AudioFile)

    def test_set_and_save_artist(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "artist", "Test Artist")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertEqual(audiofile.tag.artist, "Test Artist")

    def test_set_and_save_album(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "album", "Test Album")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertEqual(audiofile.tag.album, "Test Album")

    def test_set_and_save_album_artist(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "album_artist", "Test Album Artist")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertEqual(audiofile.tag.album_artist, "Test Album Artist")

    def test_set_and_save_title(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "title", "Test Title")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertEqual(audiofile.tag.title, "Test Title")

    def test_set_and_save_track_num(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "track_num", "5")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertEqual(audiofile.tag.track_num[0], 5)

    def test_set_multiple_metadata_fields(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "artist", "Multi Artist")
        set(f, "album", "Multi Album")
        set(f, "album_artist", "Multi Album Artist")
        set(f, "title", "Multi Title")
        set(f, "track_num", "7")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertEqual(audiofile.tag.artist, "Multi Artist")
        self.assertEqual(audiofile.tag.album, "Multi Album")
        self.assertEqual(audiofile.tag.album_artist, "Multi Album Artist")
        self.assertEqual(audiofile.tag.title, "Multi Title")
        self.assertEqual(audiofile.tag.track_num[0], 7)

    def test_save_file_without_changes(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        save_file(f)
        '''
        self.run_dsl_code(code)

        audiofile = self.load_audiofile(mp3_path)
        self.assertIsNotNone(audiofile.tag)

    def test_set_invalid_metadata_field_raises_error(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "nonexistent_field", "Oops")
        save_file(f)
        '''
        with self.assertRaises(AttributeError):
            self.run_dsl_code(code)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_mp3_metadata(self, mock_stdout):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        print(f)
        '''
        self.run_dsl_code(code)


        output = mock_stdout.getvalue()
        self.assertIn("title:", output)
        self.assertIn("artist:", output)


if __name__ == '__main__':
    unittest.main()
