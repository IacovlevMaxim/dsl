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

    def __init__(self, name, value_expr):
        self.name = name
        self.value_expr = value_expr

    def eval(self):
        if self.name not in variables:
            raise NameError(f"Variable '{self.name}' not defined")
        value = self.value_expr.eval()
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
        elif self.op == '==':
            return left_val == right_val
        elif self.op == '>':
            return left_val > right_val
        elif self.op == '<':
            return left_val < right_val
        # Add more operations as needed


class UnaryOperation(ASTNode):
    """Represents unary operations like NOT"""

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def eval(self):
        val = self.expr.eval()
        if self.op == 'NOT':
            return not val
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
            print(*args)
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

def p_statement_string_id_assignment(p):
    'statement : STRING_ID EQUALS strexpr'
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.STRING, variable_name, p[3])

def p_strexpr(p):
    'strexpr : QUOTE STRCONTENT QUOTE'
    p[0] = Literal(p[2])

def p_statement_id_assignment(p):
    'statement : IDENTIFIER EQUALS expression'
    p[0] = Assignment(p[1], p[3])

# ---- EXPRESSIONS ----
def p_expression_number(p):
    'expression : numexpr'
    p[0] = p[1]

def p_expression_string(p):
    'expression : strexpr'
    p[0] = p[1]

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    p[0] = Identifier(p[1])

def p_expression_add(p):
    'expression : expression PLUS expression'
    p[0] = BinaryOperation(p[1], '+', p[3])

# ---- BOOLEAN EXPRESSIONS ----
def p_expression_boolean_equal(p):
    'boolexpr : NUMBER IS_EQUAL NUMBER'
    p[0] = BinaryOperation(Literal(p[1]), '==', Literal(p[3]))

def p_expression_boolean_greater(p):
    'boolexpr : expression GREATER expression'
    p[0] = BinaryOperation(p[1], '>', p[3])

def p_expression_boolean_less(p):
    'boolexpr : expression LESS expression'
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
    'statement : PRINT LPAREN NUMBER RPAREN'
    p[0] = FunctionCall('print', [Literal(p[3])])

def p_string_print(p):
    'statement : PRINT LPAREN strexpr RPAREN'
    p[0] = FunctionCall('print', [p[3]])

def p_boolean_print(p):
    'statement : PRINT LPAREN boolexpr RPAREN'
    p[0] = FunctionCall('print', [p[3]])

# ---- BOOLEAN DEFINITION ----
def p_statement_boolean_id_assignment(p):
    '''statement : BOOLEAN_ID EQUALS BOOLEAN'''
    variable_name = p[1].split()[1]
    p[0] = VariableDeclaration(VariableType.BOOLEAN, variable_name, Literal(bool(p[3])))

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

def p_error(token):
    if token is not None:
        print("Line %s, illegal token %s" % (token.lineno, token.value))
    else:
        print('Unexpected end of input')


lexer = lex.lex()
parser = yacc.yacc()

file_path = os.path.join(os.getcwd(), "test.mp3")

dsl_code = f"""
file f1 = load("{file_path}")
set(f2, "artist", "Yeet")
set(f1, "title", "Cookie Crisp")
save_file(f1)
"""

if __name__ == '__main__':
    ast = parser.parse(dsl_code)
    ast.eval()




