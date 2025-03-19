# This is a sample Python script.
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


# TO-DO:
# 1) Define variable types in the dictionary
# 2) Try to implement if

# ---- PROGRAM ----
def p_program(p):
    '''program : program statement
               | statement'''
    pass


# ---- VARIABLE DEFINITION ---

# -- FIlE DEFINITION --
def p_statement_file_id_assignment(p):
    'statement : FILE_ID EQUALS LOADFILE LPAREN strexpr RPAREN'
    # file file123 = load("local/usr/bin/t.mp3")
    # statement, file_id, equals, loadfile, lparen, pathfile, rparen = p
    variable_name = p[1].split()[1]
    file = eyed3.load(p[5])

    new_var = Variable(variable_name, VariableType.AUDIO_FILE, file)
    variables[variable_name] = new_var
    p[0] = (variable_name, new_var)


# -- NUMBER DEFINITION --
def p_statement_number_id_assignment(p):
    'statement : NUMBER_ID EQUALS numexpr'
    # statement, number_id, equals, numexpr = p
    # number num123 = 123
    variable_name = p[1].split()[1]

    new_var = Variable(variable_name, VariableType.NUMBER, p[3])
    variables[variable_name] = new_var
    p[0] = (variable_name, new_var)


def p_numexpr_number(p):
    # digit
    'numexpr : NUMBER'
    p[0] = p[1]


# -- STRING DEFINITION --
def p_statement_string_id_assignment(p):
    'statement : STRING_ID EQUALS strexpr'
    # string str123 = "akjshdfkl"
    variable_name = p[1].split()[1]
    new_var = Variable(variable_name, VariableType.STRING, p[3])
    variables[variable_name] = new_var
    p[0] = (variable_name, new_var)


def p_strexpr(p):
    # TO-DO: use something more flexible than IDENTIFIER
    # 'strexpr : QUOTE IDENTIFIER QUOTE'
    'strexpr : QUOTE STRCONTENT QUOTE'
    # "akjshdfkl"
    p[0] = p[2]


def p_statement_id_assignment(p):
    'statement : IDENTIFIER EQUALS expression'
    # TO-DO: be more precise with expression that is passed to assign the variable
    variable_name = p[1]
    if variable_name in variables:
        variables[variable_name] = Variable(variable_name, variables[variable_name].type, p[3])
        p[0] = (variable_name, variables[variable_name])
    else:
        print(f"Error: variable {variable_name} is not defined")


# ---- FILE METHODS ----
def p_statement_file_setauthor(p):
    'statement : SETAUTHOR LPAREN IDENTIFIER COMMA strexpr RPAREN'
    # set_author(file1, "author")
    var = p[3]
    if var in variables:
        audiofile = variables[var]
        if audiofile.type is VariableType.AUDIO_FILE:
            audiofile.value.tag.artist = p[5]
        else:
            print(f"Error: variable {var} is not of type '{VariableType.AUDIO_FILE}'")

    else:
        print(f"Error: variable {var} is not defined")


def p_statement_file_settitle(p):
    'statement : SETTITLE LPAREN IDENTIFIER COMMA strexpr RPAREN'
    # set_title(file1, "title")
    var = p[3]
    if var in variables:
        audiofile = variables[var]
        if audiofile.type is VariableType.AUDIO_FILE:
            audiofile.value.tag.title = p[5]
        else:
            print(f"Error: variable {var} is not of type '{VariableType.AUDIO_FILE}'")
    else:
        print(f"Error: variable {var} is not defined")


def p_statement_file_savefile(p):
    'statement : SAVEFILE LPAREN IDENTIFIER RPAREN'
    var = p[3]
    if var in variables:
        audiofile = variables[var]
        if audiofile.type is VariableType.AUDIO_FILE:
            audiofile.value.tag.save()
        else:
            print(f"Error: variable {var} is not of type '{VariableType.AUDIO_FILE}'")
    else:
        print(f"Error: variable {var} is not defined")


# ---- GENERAL EXPRESSION ---
def p_expression_number(p):
    'expression : numexpr'
    p[0] = p[1]


def p_expression_string(p):
    'expression : strexpr'
    p[0] = p[1]


def p_expression_identifier(p):
    'expression : IDENTIFIER'
    variable_name = p[1]
    if variable_name in variables:
        p[0] = variables[variable_name].value
    else:
        print(f"Error: Variable '{variable_name}' not in variable table")


def p_expression_add(p):
    'expression : expression PLUS expression'
    p[0] = p[1] + p[3]

# ---- BOOLEAN EXPRESSIONS ----
def p_expression_boolean_equal(p):
    'boolexpr : NUMBER IS_EQUAL NUMBER'
    p[0] = p[1] == p[3]

def p_expression_boolean_greater(p):
    'boolexpr : expression GREATER expression'
    p[0] = p[1] > p[3]

def p_expression_boolean_less(p):
    'boolexpr : expression LESS expression'
    p[0] = p[1] < p[3]

def p_expression_boolean_not(p):
    'boolexpr : NOT boolexpr'
    p[0] = not p[2]

def p_expression_boolean_vals(p):
    'boolexpr : BOOLEAN'
    p[0] = bool(p[1])


def p_expression_boolean_id(p):
    'boolexpr : IDENTIFIER'
    p[0] = bool(p[1])


# ---- PRINT FUNCTION ----
def p_statement_print(p):
    'statement : PRINT LPAREN IDENTIFIER RPAREN'
    if p[3] in variables:
        variable = variables[p[3]]
        if variable.type == VariableType.AUDIO_FILE:
            audiofile = variable.value
            print(f"Artist: {audiofile.tag.artist}")
            print(f"Album: {audiofile.tag.album}")
            print(f"Album artist: {audiofile.tag.album_artist}")
            print(f"Title: {audiofile.tag.title}")
            print(f"Track number: {audiofile.tag.track_num}")
        elif variable.type == VariableType.NUMBER:
            print(variable.value)
        elif variable.type == VariableType.BOOLEAN:
            print(variable.value)
    else:
        print(f"Error: Variable '{p[3]}' not in variable table")


def p_number_print(p):
    'statement : PRINT LPAREN NUMBER RPAREN'
    print(p[3])

def p_string_print(p):
    'statement : PRINT LPAREN strexpr RPAREN'
    print(p[3])


def p_boolean_print(p):
    'statement : PRINT LPAREN boolexpr RPAREN'
    print(p[3])

# ---- BOOLEAN DEFINITION ----
def p_statement_boolean_id_assignment(p):
    '''statement : BOOLEAN_ID EQUALS BOOLEAN'''
    # boolean var123 = True
    variable_name = p[1].split()[1]
    new_var = Variable(variable_name, VariableType.BOOLEAN, bool(p[3]))
    variables[variable_name] = new_var
    p[0] = (variable_name, new_var)


def p_statement_boolean_id_assignment_boolexpr(p):
    '''statement : BOOLEAN_ID EQUALS boolexpr'''
    # boolean var123 = True
    variable_name = p[1].split()[1]
    new_var = Variable(variable_name, VariableType.BOOLEAN, bool(p[3]))
    variables[variable_name] = new_var
    p[0] = (variable_name, new_var)

def p_statement_if_short(p):
    '''statement : IF LPAREN boolexpr RPAREN THEN statement'''
    bool_val = p[3]
    if not bool_val:
        # skip implementation of statement if false
        p[6] = None
        pass

def p_statement_if_extended(p):
    '''statement : IF LPAREN boolexpr RPAREN THEN LCURLY program RCURLY'''
    bool_val = p[3]
    if not bool_val:
        # skip implementation of statement if false
        p[7] = None
        pass

def p_error(token):
    if token is not None:
        print ("Line %s, illegal token %s" % (token.lineno, token.value))
    else:
        print('Unexpected end of input')


lexer = lex.lex()
parser = yacc.yacc()


file_path = os.path.join(os.getcwd(), "test.mp3")

dsl_code = """
if(1 == 1) then print("wow")
if(1 == 0) then {
    print("hi")
    print("hi2")
}
"""

"""
Print function:
* Boolean works
* False works
* Number from variable works
* Number works
* String from variable works
* String - prints "

"""

# test print
# dsl_code = f"""
# boolean flag = True
# number num123 = 42
# string text = "hello"
# print(flag)
# print(num123)
# print(text)
# print(100)
# print("test")
# print(False)
# """

# test boolean operations
# note: fails
# dsl_code = f"""
# boolean a = True
# boolean b = !a
# print(a)
# print(b)
# """

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser.parse(dsl_code, debug=True, tracking=True)





