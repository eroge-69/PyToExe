import os
import sys
import time
import re

RED = '\033[31m'
RESET = '\033[0m'

def color_braces(text: str) -> str:
    return re.sub(r'\{([^}]*)\}', lambda m: f"{RED}{m.group(1)}{RESET}", text)

def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header() -> None:
    header = r"""                                                 
    _|      _|    _|_|      _|_|    _|_|_|_|_|  _|_|_|_|  
    _|_|  _|_|  _|    _|  _|    _|        _|    _|        
    _|  _|  _|  _|    _|  _|    _|      _|      _|_|_|    
    _|      _|  _|    _|  _|    _|    _|        _|        
    _|      _|    _|_|      _|_|    _|_|_|_|_|  _|_|_|_|  
"""
    print(header)

def main() -> None:
    if os.name == 'nt':
        os.system('mode con: cols=70 lines=15')

    while True:
        clear_screen()
        print_header()
        key = input(color_braces("    [{-}] Key: "))
        if key == "@lugk":
            break

    clear_screen()
    print_header()
    print(color_braces("    [{-}] Authenticating..."))
    time.sleep(2)

    clear_screen()
    print_header()
    print(color_braces("    [{-}] Hiding console in {5.00} seconds!"))
    time.sleep(5)
    sys.exit()

if __name__ == "__main__":
    main()
