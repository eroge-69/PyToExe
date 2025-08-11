# filepath: /password-generator-app/password-generator-app/src/app.py

from ui import create_ui
from generator import PasswordGenerator

def main():
    password_generator = PasswordGenerator()
    create_ui(password_generator)

if __name__ == "__main__":
    main()