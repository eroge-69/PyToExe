import os
import sys
import subprocess

def main():
    steam_url = "steam://rungameid/230410"
    subprocess.Popen(["start", "", steam_url], shell=True)

if __name__ == "__main__":
    main()