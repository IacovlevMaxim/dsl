import ply.lex as lex
import ply.yacc as yacc
import tempfile
# Do not remove these imports, they are used by ply library for generating lexer and parser
from src.lexer.tokens import tokens
from src.lexer.tokens import *
from src.parser.parser import precedence
from src.parser.parser import *


def load_dsl_file(filename="../code.txt"):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: {filename} not found.")


lexer = lex.lex()
parser = yacc.yacc()

if __name__ == '__main__':
    dsl_code = load_dsl_file()
    ast = parser.parse(dsl_code)
    ast.eval()

