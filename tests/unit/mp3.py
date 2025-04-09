
import unittest
import unittest.mock
import io
import tempfile
import os
import eyed3
from eyed3 import AudioFile
from main import load_dsl_file, parser, variables


class TestMP3Metadata(unittest.TestCase):
    def setUp(self):
        variables.clear()
        self.temp_files = []

    def tearDown(self):
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def create_temp_mp3(self):
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b'ID3\x03\x00\x00\x00\x00\x00\x00')
            tmp.flush()
            self.temp_files.append(tmp.name)

            # Initialize tag so eyed3 won't throw errors
            audiofile = eyed3.load(tmp.name)
            if audiofile.tag is None:
                audiofile.initTag()
                audiofile.tag.artist = "Temp"
                audiofile.tag.save()

            return tmp.name

    def test_load_mp3_file(self):
        mp3_path = self.create_temp_mp3()

        code = f'file f = load("{mp3_path}")'
        ast = parser.parse(code)
        ast.eval()

        self.assertIn('f', variables)
        self.assertEqual(variables['f'].type.name, 'AUDIO_FILE')
        self.assertIsInstance(variables['f'].value, AudioFile)

    def test_set_artist_metadata(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "artist", "Test Artist")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertEqual(audiofile.tag.artist, "Test Artist")

    def test_set_album_metadata(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "album", "Test Album")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertEqual(audiofile.tag.album, "Test Album")

    def test_set_title_metadata(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "title", "Test Title")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertEqual(audiofile.tag.title, "Test Title")

    def test_set_track_num_metadata(self):
        mp3_path = r"C:\Users\user\Desktop\UniFiles\Anul2_Sem2\dsl\test.mp3"

        if not os.path.exists(mp3_path):
            self.skipTest("Real MP3 file not found on this system")

        code = f'''
        file f = load("{mp3_path}")
        set(f, "track_num", 5)
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertEqual(str(audiofile.tag.track_num[0]), "5")

    def test_set_multiple_metadata_fields(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "artist", "Multi Artist")
        set(f, "album", "Multi Album")
        set(f, "title", "Multi Title")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertEqual(audiofile.tag.artist, "Multi Artist")
        self.assertEqual(audiofile.tag.album, "Multi Album")
        self.assertEqual(audiofile.tag.title, "Multi Title")

    def test_save_file_without_changes(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertIsNotNone(audiofile)

    def test_set_invalid_metadata_field(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "nonexistent", "Oops")
        save_file(f)
        '''
        with self.assertRaises(AttributeError):
            ast = parser.parse(code)
            ast.eval()

    def test_full_metadata_edit(self):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        set(f, "artist", "Full Artist")
        set(f, "album", "Full Album")
        set(f, "title", "Full Title")
        set(f, "track_num", 3)
        save_file(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        audiofile = eyed3.load(mp3_path)
        self.assertEqual(audiofile.tag.artist, "Full Artist")
        self.assertEqual(audiofile.tag.album, "Full Album")
        self.assertEqual(audiofile.tag.title, "Full Title")
        self.assertEqual(str(audiofile.tag.track_num[0]), "3")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_file_variable(self, mock_stdout):
        mp3_path = self.create_temp_mp3()

        code = f'''
        file f = load("{mp3_path}")
        print(f)
        '''
        ast = parser.parse(code)
        ast.eval()

        output = mock_stdout.getvalue().strip()
        self.assertIn("AudioFile", output)


if __name__ == '__main__':
    unittest.main()
