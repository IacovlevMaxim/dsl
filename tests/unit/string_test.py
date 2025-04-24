import unittest.mock
import io
import unittest.mock
from utils.get_output import *


class StringMethodsTestCase(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_length(self, mock_stdout):
        code = 'string s = "hello"\nprint(length(s))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "5")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_slice(self, mock_stdout):
        code = 'string s = "hello"\nprint(slice(s, 1, 3))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "ell")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_includes_true(self, mock_stdout):
        code = 'string s = "hello"\nprint(includes(s, "ell"))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_includes_false(self, mock_stdout):
        code = 'string s = "hello"\nprint(includes(s, "world"))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "False")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_starts_with_true(self, mock_stdout):
        code = 'string s = "hello"\nprint(startsWith(s, "he"))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_starts_with_false(self, mock_stdout):
        code = 'string s = "hello"\nprint(startsWith(s, "lo"))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "False")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_ends_with_true(self, mock_stdout):
        code = 'string s = "hello"\nprint(endsWith(s, "lo"))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_ends_with_false(self, mock_stdout):
        code = 'string s = "hello"\nprint(endsWith(s, "he"))'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "False")


if __name__ == '__main__':
    unittest.main()