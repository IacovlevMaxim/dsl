import io
import unittest.mock
from tests.utils.get_output import *
from tests.utils.with_tempfile import *


class AssignmentTestCase(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_strid_name_error(self, mock_stdout):
        code = "string s = \"a\"\nb = 1"
        with self.assertRaises(NameError):
            get_output(code, mock_stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_numid_num(self, mock_stdout):
        code = "number a = 1\na = 2\nprint(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "2")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_numid_uminus(self, mock_stdout):
        code = "number a = 1\na = -1\nprint(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "-1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_numid_numexpr(self, mock_stdout):
        code = "number a = 1\na = 1+1\nprint(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "2")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_numid_bool(self, mock_stdout):
        code = "number a = 1\na = True\nprint(a)"

        with self.assertRaises(TypeError):
            get_output(code, mock_stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_strid_str(self, mock_stdout):
        code = 'string s = "a"\ns = "b"\nprint(s)'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "b")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_strid_strnum(self, mock_stdout):
        code = 'string s = "1"\nprint(s)'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_strid_strnum_neg(self, mock_stdout):
        code = 'string s = "-1"\nprint(s)'
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "-1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_strid_num(self, mock_stdout):
        code = "string s = \"a\"\ns = 1\nprint(s)"
        with self.assertRaises(TypeError):
            get_output(code, mock_stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_boolid_bool(self, mock_stdout):
        code = "boolean a = True\na = False\nprint(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "False")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_boolid_boolexpr(self, mock_stdout):
        code = "boolean a = True\na = !False\nprint(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_boolid_num(self, mock_stdout):
        code = "boolean a = True\na = 1\nprint(a)"
        with self.assertRaises(TypeError):
            get_output(code, mock_stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @with_tempfile('mp3')
    def test_fileid_file(self, file1, mock_stdout):
        os.system(f"echo {file1}")
        code = f'file f = load("{file1}")\nprint(f)'
        output = get_output(code, mock_stdout)

        print(output)


if __name__ == '__main__':
    unittest.main()
