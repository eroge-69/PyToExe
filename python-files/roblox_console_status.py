import os
import sys
import msvcrt

def clear():
    os.system('cls')

def yellow(text):
    return f'\033[33m{text}\033[0m'

def green(text):
    return f'\033[32m{text}\033[0m'

def gray(text):
    return f'\033[90m{text}\033[0m'

def wait_key():
    msvcrt.getch()

def main():
    os.system('')
    clear()
    print(f"{yellow('[/]')} {gray('Waiting for Roblox..')}")
    wait_key()
    clear()
    print(f"{green('[+]')} {gray('Found Roblox process - version-2a06298afe3947ab')}")
    print(f"{yellow('[/]')} {gray('Injecting..')}")
    wait_key()
    clear()
    print(f"{green('[+]')} {gray('Found Roblox process - version-2a06298afe3947ab')}")
    print(f"{green('[+]')} {gray('Injected BeefronRapist.dll, have fun! Do not close this application!')}")

if __name__ == '__main__':
    main() 