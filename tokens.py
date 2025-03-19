tokens = (
    'IDENTIFIER', # variable
    'NUMBER', # numbers (1, 2, 3...)
    'NUMBER_ID', # variable of type number

    'STRING', # string ("hi", "45678",..._
    'STRING_ID', # variable of type string
    'STRCONTENT',

    'FILE_ID', # variable of type file
    'LOADFILE', # " 'load'
    'SETAUTHOR', # set_author
    'SETTITLE', # set_title
    'SAVEFILE', # 'save'
    
    'PLUS', # +
    'LPAREN', # (
    'RPAREN', # )
    'LBRACKET', # [
    'RBRACKET', # ]
    'QUOTE', # "
    'COMMA', # ,
    'EQUALS', # =
    'DOT', # .

    'IS_EQUAL',   # ==
    'GREATER', # >
    'LESS',    # <
    'NOT',     # !

    'PRINT', # print
    
    'BOOLEAN', # True, False
    'BOOLEAN_ID', # variable of type boolean
    'TRUE', # True
    'FALSE', # False
)

t_ignore = ' \t'
t_PLUS = r'\+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_IS_EQUAL = r'=='
t_EQUALS = r'='
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_QUOTE = r'\"'
t_COMMA = r','
t_DOT = r'\.'
t_GREATER = r'>'
t_LESS = r'<'
t_NOT = r'!'
t_TRUE = r'True'
t_FALSE = r'False'
t_STRCONTENT = r'(?<=")[^\n"]+(?=")'


def t_BOOLEAN(t):
    r'True|False'
    t.value = True if t.value == 'True' else False
    return t

def t_BOOLEAN_ID(t):
    r'boolean\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


def t_PRINT(t):
    r'print'
    t.type = 'PRINT'
    return t


def t_LOADFILE(t):
    r'load'
    t.type = 'LOADFILE'
    return t


def t_SETAUTHOR(t):
    r'set_author'
    t.type = 'SETAUTHOR'
    return t


def t_SETTITLE(t):
    r'set_title'
    t.type = 'SETTITLE'
    return t


def t_SAVEFILE(t):
    r'save_file'
    t.type = 'SAVEFILE'
    return t

def t_FILE_ID(t):
    r'file\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t


def t_NUMBER_ID(t):
    r'number\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_STRING_ID(t):
    r'string\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_IDENTIFIER(t):
    r'(?<!"|\/)\b[a-zA-Z_^n][a-zA-Z_0-9]*\b(?!"|\/)'
    t.type = 'IDENTIFIER'
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_error(t):
    t.type = t.value[0]
    t.value = t.value[0]
    t.lexer.skip(1)
    return t


