import exiftool
import eyed3
import ply.lex as lex
import ply.yacc as yacc
from tokens import *
from typing import Union
from enum import Enum
from eyed3 import AudioFile
from image_metadata import metadata_prefix

variables = {}

class VariableType(Enum):
    UNKNOWN = 0
    NUMBER = 1
    STRING = 2
    AUDIO_FILE = 3
    BOOLEAN = 4
    IMAGE_FILE = 5
    type_names = {
        UNKNOWN: "unknown",
        NUMBER: "number",
        STRING: "string",
        AUDIO_FILE: "audio file",
        BOOLEAN: "boolean",
        IMAGE_FILE: "image file"
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

class BreakException(Exception):
    """Exception raised when a break statement is encountered"""
    pass

class InfiniteLoopError(Exception):
    """Exception raised when an infinite loop is detected"""
    pass

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
        if var_type == VariableType.UNKNOWN:
            raise SyntaxError(f"Unknown variable type for variable '{name}'. Invalid or unsupported extension?")

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


class WhileLoop(ASTNode):
    """Represents while loop statements"""

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.max_iterations = 10000

    def eval(self):
        if not self.condition.eval():
            return None
        iterations = 0
        initial_vars = {}
        for var_name, var_obj in variables.items():
            if isinstance(var_obj.value, (int, float, bool, str)):
                initial_vars[var_name] = var_obj.value
        try:
            while self.condition.eval():
                try:
                    self.body.eval()
                except BreakException:
                    break
                iterations += 1
                if iterations >= self.max_iterations:
                    changed = False
                    for var_name, initial_value in initial_vars.items():
                        if var_name in variables and variables[var_name].value != initial_value:
                            changed = True
                            break
                    if not changed:
                        raise InfiniteLoopError("Potential infinite loop detected")
                    print(f"Warning: Loop has run {self.max_iterations} iterations")

        except InfiniteLoopError as e:
            raise InfiniteLoopError(f"Infinite loop detected: {str(e)}")
        return None

class BreakStatement(ASTNode):
    """Represents a break statement"""
    def eval(self):
        raise BreakException()

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
                    elif var.type == VariableType.IMAGE_FILE:
                        metadata = var.value
                        for key, value in metadata.items():
                            print(f"{key}: {value}")
                    else:
                        print(value)
                else:
                    print(value)
        elif self.func_name == 'set':
            var_name = self.args[0].name
            var_type = variables[var_name].type

            if var_type == VariableType.AUDIO_FILE:
                setattr(variables[var_name].value.tag, args[1], args[2])
            elif var_type == VariableType.IMAGE_FILE:
                metadata = variables[var_name].value
                file_path = metadata["File:Directory"] + "/" + metadata["SourceFile"]
                key = args[1] if ":" in args[1] else f"{metadata_prefix(args[1])}:{args[1]}"
                print("key", key)
                value = args[2]
                with exiftool.ExifTool() as et:
                    et.execute(f"-{key}={value}", file_path)

                variables[var_name].value[key] = value

        elif self.func_name == 'save_file':
            var_name = self.args[0].name
            if variables[var_name].type == VariableType.AUDIO_FILE:
                variables[var_name].value.tag.save()
        elif self.func_name == 'loadfile':
            path = args[0]
            if len(path.split('.')) < 2:
                raise SyntaxError(f"No file extension provided for path '{path}'")
            file_extension = path.split('.')[1]
            if file_extension == "mp3":
                file = eyed3.load(path)
            elif file_extension == "png" or file_extension == "jpg":
                with exiftool.ExifToolHelper() as et:
                    file = et.get_metadata(path)[0]
            else:
                raise SyntaxError(f"Unsupported file extension '{file_extension}'")
            return file


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
    file_extension = p[5].value.split('.')[1]
    if file_extension == "mp3":
        variable_type = VariableType.AUDIO_FILE
    elif file_extension == "png" or file_extension == "jpg":
        variable_type = VariableType.IMAGE_FILE
    else:
        variable_type = VariableType.UNKNOWN

    p[0] = VariableDeclaration(variable_type, variable_name,
                              FunctionCall('loadfile', [p[5]]))

def p_statement_number_id_assignment(p):
    'statement : NUMBER_ID EQUALS numexpr'
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.NUMBER, variable_name, p[3])

def p_numexpr_number(p):
    'numexpr : NUMBER'
    p[0] = Literal(p[1])

def p_numexpr_identifier(p):
    'numexpr : IDENTIFIER'
    p[0] = Identifier(p[1])

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

# ---- WHILE STATEMENTS ----
def p_statement_while(p):
    '''statement : WHILE LPAREN boolexpr RPAREN LCURLY program RCURLY'''
    p[0] = WhileLoop(p[3], p[6])

# ---- BREAK STATEMENT ----
def p_statement_break(p):
    '''statement : BREAK'''
    p[0] = BreakStatement()

# ---- FILE METHODS ----
def p_statement_file_set(p):
    'statement : SET LPAREN IDENTIFIER COMMA strexpr COMMA strexpr RPAREN'
    p[0] = FunctionCall('set', [Identifier(p[3]), p[5], p[7]])


def p_statement_file_savefile(p):
    'statement : SAVEFILE LPAREN IDENTIFIER RPAREN'
    p[0] = FunctionCall('save_file', [Identifier(p[3])])

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