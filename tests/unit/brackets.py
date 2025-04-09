import io
import unittest.mock
from main import parser

def get_output(code, mock_stdout):
    ast = parser.parse(code, tracking=True)
    ast.eval()
    output = mock_stdout.getvalue().strip('\n')
    return output

class MulDivTests(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_simple_multiplication(self, mock_stdout):
        code = "print((1 + 2) * 3)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "9")


    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_simple_division(self, mock_stdout):
        code = "print(1 + 2 * 3)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "7")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_operator_precedence(self, mock_stdout):
        code = "print((((1+2))))"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "3")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_operator_precedence(self, mock_stdout):
        code = "print(-(((1))))"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "-1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_chained_operations(self, mock_stdout):
        code = "print(2 * (3 + (4 / 2)))"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "10.0")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_negative_numbers(self, mock_stdout):
        code = "print((1 + 2) * (3 + 4))"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "21")