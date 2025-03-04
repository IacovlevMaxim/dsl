# This is a sample Python script.
import eyed3
import ply.lex as lex
import ply.yacc as yacc
from tokens import *
import os

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

variables = {}

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
    'statement : FILE_ID EQUALS LOADFILE LPAREN QUOTE PATHFILE QUOTE RPAREN'
    variable_name = p[1].split()[1]

    file = eyed3.load(p[6])
    variables[variable_name] = file
    p[0] = (variable_name, file)


# -- NUMBER DEFINITION --
def p_statement_number_id_assignment(p):
    'statement : NUMBER_ID EQUALS numexpr'
    variable_name = p[1].split()[1]
    variables[variable_name] = p[3]
    p[0] = (variable_name, p[3])


def p_numexpr_number(p):
    # digit
    'numexpr : NUMBER'
    p[0] = p[1]


# -- STRING DEFINITION --
def p_statement_string_id_assignment(p):
    'statement : STRING_ID EQUALS strexpr'
    variable_name = p[1].split()[1]
    variables[variable_name] = p[3]
    p[0] = (variable_name, p[3])


def p_strexpr(p):
    # TO-DO: use something more flexible than IDENTIFIER
    'strexpr : QUOTE IDENTIFIER QUOTE'
    p[0] = p[2]


def p_statement_id_assignment(p):
    'statement : IDENTIFIER EQUALS expression'
    # TO-DO: be more precise with expression that is passed to assign the variable
    variable_name = p[1]
    if variable_name in variables:
        variables[variable_name] = p[3]
        p[0] = (variable_name, p[3])
    else:
        print(f"Error: variable {variable_name} is not defined")


# ---- FILE METHODS ----
def p_statement_file_setauthor(p):
    'statement : SETAUTHOR LPAREN IDENTIFIER COMMA strexpr RPAREN'
    var = p[3]
    if var in variables:
        audiofile = variables[var]
        audiofile.tag.artist = p[5]

    else:
        print(f"Error: variable {var} is not defined")


def p_statement_file_settitle(p):
    'statement : SETTITLE LPAREN IDENTIFIER COMMA strexpr RPAREN'
    var = p[3]
    if var in variables:
        audiofile = variables[var]
        audiofile.tag.title = p[5]
    else:
        print(f"Error: variable {var} is not defined")


def p_statement_file_savefile(p):
    'statement : SAVEFILE LPAREN IDENTIFIER RPAREN'
    var = p[3]
    if var in variables:
        audiofile = variables[var]
        audiofile.tag.save()
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
        p[0] = variables[variable_name]
    else:
        print(f"Error: Variable '{variable_name}' not in variable table")


def p_expression_add(p):
    'expression : expression PLUS expression'
    p[0] = p[1] + p[3]


# ---- PRINT FUNCTION ----
def p_statement_print(p):
    'statement : PRINT LPAREN IDENTIFIER RPAREN'
    variable_name = p[3]
    if variable_name in variables:
        print(variables[variable_name])
    else:
        print(f"Error: Variable '{variable_name}' not in variable table")


def p_number_print(p):
    'statement : PRINT LPAREN NUMBER RPAREN'
    print(p[3])


lexer = lex.lex()
parser = yacc.yacc()


file_path = os.path.join(os.getcwd(), "test.mp3")

dsl_code = f"""
file f = load("{file_path}")
set_author(f, "Yeehaw")
set_title(f, "powpow2")
save_file(f)
"""

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser.parse(dsl_code)


