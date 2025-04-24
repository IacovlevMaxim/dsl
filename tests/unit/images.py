import io
import unittest.mock
import exiftool
from src.utils.image_metadata import metadata_prefix
from utils.get_output import *
from utils.with_tempfile import *


class ImagesTestCase(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @with_tempfile('png')
    def test_image_load_print(self, temp_file, mock_stdout):
        code = f'file f = load("{temp_file}")\nprint(f)'
        output = get_output(code, mock_stdout)

        print(output)

        contents = [temp_file, "File:FileType: PNG"]
        for content in contents:
            self.assertEqual(content in output, True)

    @with_tempfile('png')
    def test_image_set_comment_no_prefix(self, temp_file):
        field = "Comment"
        code = f'file f = load("{temp_file}")\nset(f,"{field}","a")'
        ast = parser.parse(code, tracking=True)
        ast.eval()

        os.system(f"echo {temp_file}")

        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(temp_file)[0]
            key = f"{metadata_prefix(field)}:{field}"
            self.assertEqual(metadata[key], "a")

    @with_tempfile('png')
    def test_image_set_comment_with_prefix(self, temp_file):
        field = "Comment"
        key = f"{metadata_prefix(field)}:{field}"
        code = f'file f = load("{temp_file}")\nset(f,"{key}","a")'
        print(code)
        ast = parser.parse(code, tracking=True)
        ast.eval()

        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(temp_file)[0]
            print(metadata)
            self.assertEqual(metadata[key], "a")


if __name__ == '__main__':
    unittest.main()