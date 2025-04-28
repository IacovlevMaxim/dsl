from src.main import parser


def get_output(code, mock_stdout):
    ast = parser.parse(code, tracking=True)
    ast.eval()
    output = mock_stdout.getvalue().strip('\n')
    return output
