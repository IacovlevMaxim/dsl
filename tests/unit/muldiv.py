import io
import unittest.mock
from tests.utils.get_output import *


class MulDivTests(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_simple_multiplication(self, mock_stdout):
        code = "print(2 * 3)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "6")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_simple_division(self, mock_stdout):
        code = "print(6 / 2)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "3.0")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_operator_precedence(self, mock_stdout):
        code = "print(1 + 2 * 3)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "7")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_chained_operations(self, mock_stdout):
        code = "print(2 * 3 * 4 / 2)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "12.0")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_negative_numbers(self, mock_stdout):
        code = "print(-2 * 3 / -1)"
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "6.0")