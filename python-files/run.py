import streamlit.web.cli as stcli
import os
import sys
import multiprocessing

def main():
    app_path = os.path.join(os.path.dirname(__file__), 'main.py')
    args = [
        "run",
        app_path,
        "--server.headless=true",
        "--global.developmentMode=false"
    ]
    sys.exit(stcli.main(args))

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    main()