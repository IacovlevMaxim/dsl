from src.interpreter.interpreter import *

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
    elif file_extension in ("mp4", "mov"):
        variable_type = VariableType.VIDEO_FILE
    elif file_extension == "pdf":
        variable_type = VariableType.PDF_FILE
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

# ---- WHILE STATEMENTS ----
def p_statement_while(p):
    '''statement : WHILE LPAREN boolexpr RPAREN LCURLY program RCURLY'''
    p[0] = WhileLoop(p[3], p[6])

# ---- FOR OF LOOP ----
def p_statement_for_of(p):
    '''statement : FOR LPAREN FILE_ID OF strexpr RPAREN LCURLY program RCURLY'''
    variable_name = p[3].split()[1]
    p[0] = ForLoop(VariableType.UNKNOWN, variable_name, p[5], p[8])

# ---- BREAK STATEMENT ----
def p_statement_break(p):
    '''statement : BREAK'''
    p[0] = BreakStatement()

# ---- CONTINUE STATEMENT ----
def p_statement_continue(p):
    '''statement : CONTINUE'''
    p[0] = ContinueStatement()

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