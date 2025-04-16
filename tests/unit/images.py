import tempfile
import os
import io
import unittest.mock
from functools import wraps

import exiftool

from image_metadata import metadata_prefix
from main import parser


def get_output(code, mock_stdout):
    ast = parser.parse(code, tracking=True)
    ast.eval()
    output = mock_stdout.getvalue().strip('\n')
    return output


def with_tempfile(extension):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(self, *args, **kwargs):
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
                temp_path = tmp.name
                try:
                    if extension in ('png', 'jpg', 'jpeg', 'gif'):
                        tmp.flush()
                        os.system(f"cp ../../test.{extension} {temp_path}")
                    return test_func(self, temp_path, *args, **kwargs)
                finally:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
        return wrapper
    return decorator


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
    def test_image_set_title_no_prefix(self, temp_file):
        field = "Title"
        code = f'file f = load("{temp_file}")\nset(f,"{field}","a")'
        ast = parser.parse(code, tracking=True)
        ast.eval()

        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(temp_file)[0]
            key = f"{metadata_prefix(field)}:{field}"
            self.assertEqual(metadata[key], "a")

    @with_tempfile('png')
    def test_image_set_title_with_prefix(self, temp_file):
        field = "Title"
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