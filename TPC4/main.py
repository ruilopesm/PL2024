from io import TextIOWrapper
import sys

import ply.lex as ply

reserved = {
    'select': 'SELECT',
    'from': 'FROM',
    'where': 'WHERE',
    'and': 'AND',
    'or': 'OR',
    'like': 'LIKE',
    'inner': 'INNER',
    'outer': 'OUTER',
    'left': 'LEFT',
    'right': 'RIGHT',
    'full': 'FULL',
    'on': 'ON',
    # ...
}

tokens = [
    "FIELD",
    "COMMAND",
    "DELIMITER",
    "FINAL_DELIMITER",
    "NUMBER",
    "MATH_OPERATOR",
] + list(reserved.values())

def t_COMMAND(t):
    r"\b[a-zA-Z]+\b"
    to_lower = t.value.lower()
    t.type = reserved.get(to_lower, "COMMAND") if to_lower in reserved else "FIELD"
    return t

t_DELIMITER = r","

t_FINAL_DELIMITER = r";"

def t_NUMBER(t): 
    r"[0-9]+(\.[0-9]+)?"
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_MATH_OPERATOR(t):
    r">=|<=|\+|-|\*|>|<|="
    return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

t_ignore = " \t"

def t_error(t):
    sys.stderr.write(f"Error: Unexpected character {t.value[0]}\n")
    t.lexer.skip(1) # Skip the character

def main(stdin: TextIOWrapper) -> None:
    lexer: ply.Lexer = ply.lex()
    
    for line in stdin:
        lexer.input(line)
        for token in lexer:
            if not token: break
            print(token)

if __name__ == "__main__":
    main(sys.stdin)
