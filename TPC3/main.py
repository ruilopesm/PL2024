from io import TextIOWrapper
from typing import Final, List
import re
import sys

token_specification: Final[List] = [
    ("INT", r"(\+|-)?\d+"),
    ("ON", r"(?i:on)"),
    ("OFF", r"(?i:off)"),
    ("EQ", r"="),
    ("SKIP", r"\s+"),
    ("UNKNOWN", r".")
]

def build_regex_pattern() -> str:
    return "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specification)

def main(stdin: TextIOWrapper) -> None:
    pattern: str = build_regex_pattern()
    
    total: int = 0
    on: bool = True

    content: str = stdin.read()
    ptr: int = 0

    while ptr < len(content):
        match = re.match(pattern, content[ptr:])
        token = match.groupdict()
        ptr = ptr + match.end()

        if token["INT"] and on:
            total += int(token["INT"])
        elif token["ON"]:
            on = True
        elif token["OFF"]:
            on = False
        elif token["EQ"]:
            sys.stdout.write(f"{total}\n")
        elif token["SKIP"] or token["UNKNOWN"]:
            pass

if __name__ == "__main__":
    main(sys.stdin)
