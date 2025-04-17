import io
import unittest
import unittest.mock
from main import parser, InfiniteLoopError


def get_output(code, mock_stdout):
    ast = parser.parse(code, tracking=True)
    ast.eval()
    output = mock_stdout.getvalue().strip('\n')
    return output


class WhileLoopTests(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_simple_while_loop(self, mock_stdout):
        code = """
        number counter = 0
        while (counter < 3) {
            print(counter)
            counter = counter + 1
        }
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "0\n1\n2")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_break_statement(self, mock_stdout):
        code = """
        number i = 0
        while (i < 5) {
            print(i)
            if (i == 2) then break
            i = i + 1
        }
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "0\n1\n2")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_comparison_between_variables(self, mock_stdout):
        code = """
        number counter = 0
        number max = 3
        while (counter < max) {
            print(counter)
            counter = counter + 1
        }
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "0\n1\n2")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_nested_while_loops(self, mock_stdout):
        code = """
        number i = 0
        while (i < 2) {
            number j = 0
            while (j < 2) {
                print(i * 10 + j)
                j = j + 1
            }
            i = i + 1
        }
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "0\n1\n10\n11")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_while_loop_with_complex_condition(self, mock_stdout):
        code = """
        number a = 5
        number b = 10
        while ((a + b) > 10) {
            print(a)
            a = a - 1
        }
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "5\n4\n3\n2\n1")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_while_no_iterations(self, mock_stdout):
        code = """
        number x = 10
        while (x < 5) {
            print(x)
            x = x + 1
        }
        print("Done")
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "Done")


if __name__ == '__main__':
    unittest.main()