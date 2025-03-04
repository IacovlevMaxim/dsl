tokens = (
    'IDENTIFIER',
    'NUMBER',
    'NUMBER_ID',

    'STRING',
    'STRING_ID',

    'FILE_ID',
    'PATHFILE',
    'LOADFILE',
    'SETAUTHOR',
    'SETTITLE',
    'SAVEFILE',
    
    'PLUS',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'QUOTE',
    'COMMA',
    'EQUALS',
    'DOT',

    'PRINT'
)

t_ignore = ' \t'
t_PLUS = r'\+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_QUOTE= r'\"'
t_COMMA = r','
t_DOT = r'\.'
# t_PATHFILE = r'^\w+.(jpg|png|gif|mp4|mp3)$'
# t_PATHFILE = r'^([a-zA-Z]:[\\\/]|[\\\/])?([^<>:"|?*\r\n]+[\\\/]*)+$'
# t_PATHFILE = r'[^"]+'
# t_LOAD_FILE = r'load'

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


def t_MATRIX_ID(t):
    r'matrix\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_NUMBER_ID(t):
    r'number\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_STRING_ID(t):
    r'string\s+[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = 'IDENTIFIER'
    return t

def t_PATHFILE(t):
    # r'[a-zA-Z_][a-zA-Z_0-9]*'
    # r'^([a-zA-Z]:[\\\/]|[\\\/])?([^<>:"|?*\r\n]+[\\\/]*)+$'
    # r'[^"]+'
    # r'^\w+.(jpg|png|gif|mp4|mp3)$'
    r'[\w/.-]+'
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


