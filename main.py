import eyed3
import ply.lex as lex
import ply.yacc as yacc
from tokens import *
from typing import Union
from enum import Enum
from eyed3 import AudioFile
import os


variables = {}

class VariableType(Enum):
    UNKNOWN = 0
    NUMBER = 1
    STRING = 2
    AUDIO_FILE = 3
    BOOLEAN = 4
    type_names = {
        UNKNOWN: "unknown",
        NUMBER: "number",
        STRING: "string",
        AUDIO_FILE: "audio file",
        BOOLEAN: "boolean"
    }


class Variable:
    def __init__(self, name: str, var_type: VariableType, value: Union[int, float, str, AudioFile] = None):
        self.name = name
        self.type = var_type
        self.value = value


class ASTNode:
    """Base class for all AST nodes"""

    def eval(self):
        raise NotImplementedError("Subclasses must implement eval()")


class Program(ASTNode):
    """Represents a program (sequence of statements)"""

    def __init__(self, statements):
        self.statements = statements

    def eval(self):
        for stmt in self.statements:
            stmt.eval()


class VariableDeclaration(ASTNode):
    """Represents variable declaration"""

    def __init__(self, var_type, name, value_expr):
        self.var_type = var_type
        self.name = name
        self.value_expr = value_expr

    def eval(self):
        value = self.value_expr.eval()
        variables[self.name] = Variable(self.name, self.var_type, value)
        return variables[self.name]


class Assignment(ASTNode):
    """Represents variable assignment"""

    def __init__(self, name, value_expr, expr_type):
        self.name = name
        self.value_expr = value_expr
        self.expr_type = expr_type

    def eval(self):
        if self.name not in variables:
            raise NameError(f"Cannot assign to '{self.name}' (not defined)")

        value = self.value_expr.eval()
        if variables[self.name].type != self.expr_type:
            raise TypeError(f"Value '{value}' is not of variable type '{self.name}'")

        variables[self.name].value = value
        return value


class BinaryOperation(ASTNode):
    """Represents binary operations like +, ==, >, etc."""

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def eval(self):
        left_val = self.left.eval()
        right_val = self.right.eval()

        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return left_val / right_val
        elif self.op == '==':
            return left_val == right_val
        elif self.op == '>':
            return left_val > right_val
        elif self.op == '<':
            return left_val < right_val


class UnaryOperation(ASTNode):
    """Represents unary operations like NOT"""

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def eval(self):
        val = self.expr.eval()
        if self.op == 'NOT':
            return not val
        elif self.op == '-':  # Handle negative numbers
            return -val
        # Add more unary operations as needed


class Literal(ASTNode):
    """Represents literal values (numbers, strings, booleans)"""

    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value


class Identifier(ASTNode):
    """Represents variable references"""

    def __init__(self, name):
        self.name = name

    def eval(self):
        if self.name not in variables:
            raise NameError(f"Variable '{self.name}' not defined")
        return variables[self.name].value


class IfStatement(ASTNode):
    """Represents if conditional statements"""

    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def eval(self):
        if self.condition.eval():
            return self.then_branch.eval()
        elif self.else_branch:
            return self.else_branch.eval()
        return None


class FunctionCall(ASTNode):
    """Represents function calls like print, set_author, etc."""

    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def eval(self):
        args = [arg.eval() for arg in self.args]

        if self.func_name == 'print':
            for arg in self.args:
                value = arg.eval()

                # Print metadata if AUDIO_FILE
                if isinstance(arg, Identifier) and arg.name in variables:
                    var = variables[arg.name]
                    if var.type == VariableType.AUDIO_FILE:
                        tag = var.value.tag
                        print(f"title: {tag.title or 'None'}")
                        print(f"artist: {tag.artist or 'None'}")
                        print(f"album: {tag.album or 'None'}")
                        print(f"album artist: {tag.album_artist or 'None'}")
                        print(f"track: {tag.track_num[0] if tag.track_num else 'None'}")
                    else:
                        print(value)
                else:
                    print(value)
        elif self.func_name == 'set':
            var_name = self.args[0].name

            if variables[var_name].type == VariableType.AUDIO_FILE:
                setattr(variables[var_name].value.tag, args[1], args[2])
        elif self.func_name == 'save_file':
            var_name = self.args[0].name
            if variables[var_name].type == VariableType.AUDIO_FILE:
                variables[var_name].value.tag.save()
        elif self.func_name == 'loadfile':
            path = args[0]
            file = eyed3.load(path)
            return file

        elif self.func_name == 'length':
            if not isinstance(args[0], str):
                raise TypeError(f"Argument to 'length' must be a string, got {type(args[0])}")
            return len(args[0])

        elif self.func_name == 'slice':
            if not isinstance(args[0], str):
                raise TypeError(f"First argument to 'slice' must be a string, got {type(args[0])}")
            start = args[1]
            if len(args) == 3:
                length = args[2]
                return args[0][start:start + length]
            return args[0][start:]  # Slice until the end if length is not provided

        elif self.func_name == 'includes':
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise TypeError(f"Arguments to 'includes' must be strings")
            return args[1] in args[0]

        elif self.func_name == 'startsWith':
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise TypeError(f"Arguments to 'startsWith' must be strings")
            return args[0].startswith(args[1])

        elif self.func_name == 'endsWith':
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise TypeError(f"Arguments to 'endsWith' must be strings")
            return args[0].endswith(args[1])
        # Add more function calls as needed

# ---- PROGRAM ----
def p_program(p):
    '''program : program statement
               | statement'''
    if len(p) == 2:
        p[0] = Program([p[1]])
    else:
        p[1].statements.append(p[2])
        p[0] = p[1]

# ---- VARIABLE DEFINITION ----
def p_statement_file_id_assignment(p):
    'statement : FILE_ID EQUALS LOADFILE LPAREN strexpr RPAREN'
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.AUDIO_FILE, variable_name,
                              FunctionCall('loadfile', [p[5]]))

def p_statement_number_id_assignment(p):
    'statement : NUMBER_ID EQUALS numexpr'
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.NUMBER, variable_name, p[3])

def p_numexpr_number(p):
    'numexpr : NUMBER'
    p[0] = Literal(p[1])

def p_numexpr_negative(p):
    'numexpr : MINUS numexpr %prec UMINUS'
    p[0] = UnaryOperation('-', p[2])

def p_numexpr_number_multiply(p):
    'numexpr : numexpr MULTIPLY numexpr'
    p[0] = BinaryOperation(p[1], '*', p[3])

def p_numexpr_number_divide(p):
    'numexpr : numexpr DIVIDE numexpr'
    p[0] = BinaryOperation(p[1], '/', p[3])

def p_numexpr_number_plus(p):
    'numexpr : numexpr PLUS numexpr'
    p[0] = BinaryOperation(p[1], '+', p[3])

def p_numexpr_number_minus(p):
    'numexpr : numexpr MINUS numexpr'
    p[0] = BinaryOperation(p[1], '-', p[3])

def p_numexpr_brackets(p):
    'numexpr : LPAREN numexpr RPAREN'
    p[0] = p[2]  # Pass the inner expression directly

def p_statement_string_id_assignment(p):
    'statement : STRING_ID EQUALS strexpr'
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.STRING, variable_name, p[3])

def p_strexpr(p):
    'strexpr : QUOTE STRCONTENT QUOTE'
    p[0] = Literal(p[2])

def p_strexpr_identifier(p):
    '''strexpr : IDENTIFIER'''
    p[0] = Identifier(p[1])  # Wrap the identifier for evaluation
def p_id_eq_numexpr(p):
    'statement : IDENTIFIER EQUALS numexpr'
    p[0] = Assignment(p[1], p[3], VariableType.NUMBER)

def p_id_eq_boolexpr(p):
    'statement : IDENTIFIER EQUALS boolexpr'
    p[0] = Assignment(p[1], p[3], VariableType.BOOLEAN)

def p_id_eq_strexpr(p):
    'statement : IDENTIFIER EQUALS strexpr'
    p[0] = Assignment(p[1], p[3], VariableType.STRING)

def p_id_eq_loadfile(p):
    'statement : IDENTIFIER EQUALS LOADFILE LPAREN strexpr RPAREN'
    p[0] = Assignment(p[1], FunctionCall('loadfile', [p[5]]), VariableType.AUDIO_FILE)

# ---- BOOLEAN EXPRESSIONS ----
def p_expression_boolean_equal_num(p):
    'boolexpr : numexpr IS_EQUAL numexpr'
    p[0] = BinaryOperation(p[1], '==', p[3])

def p_expression_boolean_equal_bool(p):
    'boolexpr : boolexpr IS_EQUAL boolexpr'
    p[0] = BinaryOperation(p[1], '==', p[3])

def p_expression_boolean_greater(p):
    'boolexpr : numexpr GREATER numexpr'
    p[0] = BinaryOperation(p[1], '>', p[3])

def p_expression_boolean_less(p):
    'boolexpr : numexpr LESS numexpr'
    p[0] = BinaryOperation(p[1], '<', p[3])

def p_expression_boolean_not(p):
    'boolexpr : NOT boolexpr'
    p[0] = UnaryOperation('NOT', p[2])

def p_expression_boolean_vals(p):
    'boolexpr : BOOLEAN'
    p[0] = Literal(bool(p[1]))

def p_expression_boolean_id(p):
    'boolexpr : IDENTIFIER'
    p[0] = Identifier(p[1])

# ---- PRINT FUNCTION ----
def p_statement_print(p):
    'statement : PRINT LPAREN IDENTIFIER RPAREN'
    p[0] = FunctionCall('print', [Identifier(p[3])])

def p_number_print(p):
    'statement : PRINT LPAREN numexpr RPAREN'
    p[0] = FunctionCall('print', [p[3]])

def p_string_print(p):
    'statement : PRINT LPAREN strexpr RPAREN'
    p[0] = FunctionCall('print', [p[3]])

def p_boolean_print(p):
    'statement : PRINT LPAREN boolexpr RPAREN'
    p[0] = FunctionCall('print', [p[3]])

# ---- BOOLEAN DEFINITION ----

def p_statement_boolean_id_assignment_boolexpr(p):
    '''statement : BOOLEAN_ID EQUALS boolexpr'''
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.BOOLEAN, variable_name, p[3])

# ---- IF STATEMENTS ----
def p_statement_if_short(p):
    '''statement : IF LPAREN boolexpr RPAREN THEN statement'''
    p[0] = IfStatement(p[3], p[6])

def p_statement_if_extended(p):
    '''statement : IF LPAREN boolexpr RPAREN THEN LCURLY program RCURLY'''
    p[0] = IfStatement(p[3], p[7])

# ---- FILE METHODS ----
def p_statement_file_set(p):
    'statement : SET LPAREN IDENTIFIER COMMA strexpr COMMA strexpr RPAREN'
    p[0] = FunctionCall('set', [Identifier(p[3]), p[5], p[7]])


def p_statement_file_savefile(p):
    'statement : SAVEFILE LPAREN IDENTIFIER RPAREN'
    p[0] = FunctionCall('save_file', [Identifier(p[3])])

# ---- STRING METHODS ----
def p_function_length(p):
    '''strexpr : LENGTH LPAREN strexpr RPAREN'''
    p[0] = FunctionCall('length', [p[3]])
def p_function_slice(p):
    '''strexpr : SLICE LPAREN strexpr COMMA numexpr COMMA numexpr RPAREN
               | SLICE LPAREN strexpr COMMA numexpr RPAREN'''
    if len(p) == 9:
        p[0] = FunctionCall('slice', [p[3], p[5], p[7]])
    else:
        p[0] = FunctionCall('slice', [p[3], p[5]])

def p_function_includes(p):
    'boolexpr : INCLUDES LPAREN strexpr COMMA strexpr RPAREN'
    p[0] = FunctionCall('includes', [p[3], p[5]])

def p_function_startsWith(p):
    'boolexpr : STARTSWITH LPAREN strexpr COMMA strexpr RPAREN'
    p[0] = FunctionCall('startsWith', [p[3], p[5]])

def p_function_endsWith(p):
    'boolexpr : ENDSWITH LPAREN strexpr COMMA strexpr RPAREN'
    p[0] = FunctionCall('endsWith', [p[3], p[5]])


# ---- STRING CONCATENATION ----
def p_strexpr_concat(p):
    '''strexpr : strexpr PLUS strexpr
               | strexpr PLUS numexpr'''
    if isinstance(p[3], Literal) and isinstance(p[3].value, (int, float)):
        p[0] = Literal(p[1].eval() + str(p[3].eval()))
    elif isinstance(p[3], Literal):
        p[0] = Literal(p[1].eval() + p[3].eval())
    else:
        raise TypeError(f"Cannot concatenate {type(p[1])} and {type(p[3])}")


# Rules to handle negative numbers and operator precedence
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'UMINUS'),  # Unary minus operator
)

def p_error(token):
    if token is not None:
        print("Line %s, illegal token %s" % (token.lineno, token.value))
    else:
        print('Unexpected end of input')


def load_dsl_file(filename="code.txt"):
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
