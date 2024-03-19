import sys

def error(msg: str) -> None:
    print(msg, file=sys.stderr)
    exit(1)