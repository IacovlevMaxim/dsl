import io
import unittest.mock
from main import parser


def get_output(code, mock_stdout):
    ast = parser.parse(code, tracking=True)
    ast.eval()
    output = mock_stdout.getvalue().strip('\n')
    return output


class PrintTestCase(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_number(self, mock_stdout):
        code = "print(1)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_bool_eq(self, mock_stdout):
        code = "print(1 == 1) print(1 == 0)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True\nFalse")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_true(self, mock_stdout):
        code = "print(True)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_not(self, mock_stdout):
        code = "print(!False)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_strexpr(self, mock_stdout):
        code = "print(\"a\")"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "a")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_identifier_num(self, mock_stdout):
        code = "number a = 1 print(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_identifier_num_expr(self, mock_stdout):
        code = "number a = 1 + 1 print(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "2")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_identifier_bool(self, mock_stdout):
        code = "boolean a = True print(a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "True")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_identifier_bool_expr(self, mock_stdout):
        code = "boolean a = True print(!a)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "False")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_identifier_str(self, mock_stdout):
        code = "string s = \"a\" print(s)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "a")

    # TO-DO
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_numexpr_plus(self, mock_stdout):
        code = "print(1 + 1)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "2")

    # TO-DO
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_numexpr_minus(self, mock_stdout):
        code = "print(1 - 1)"
        output = get_output(code, mock_stdout)

        self.assertEqual(output, "0")


if __name__ == '__main__':
    unittest.main()
