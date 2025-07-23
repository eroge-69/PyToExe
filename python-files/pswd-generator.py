import argparse
import secrets
import string
import sys

try:
    import pyperclip
    CLIPBOARD_ENABLED = True
except ImportError:
    CLIPBOARD_ENABLED = False


def generate_password(length=12, use_uppercase=False, use_lowercase=True,
                      use_digits=True, use_symbols=False):
    character_pool = ''
    if use_uppercase:
        character_pool += string.ascii_uppercase
    if use_lowercase:
        character_pool += string.ascii_lowercase
    if use_digits:
        character_pool += string.digits
    if use_symbols:
        character_pool += string.punctuation

    if not character_pool:
        raise ValueError("At least one character set must be selected!")

    return ''.join(secrets.choice(character_pool) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description="🔐 Random Password Generator CLI")
    parser.add_argument('--length', type=int, default=12, help='Length of the password (default: 12)')
    parser.add_argument('--uppercase', action='store_true', help='Include uppercase letters')
    parser.add_argument('--lowercase', action='store_true', default=True, help='Include lowercase letters')
    parser.add_argument('--digits', action='store_true', default=True, help='Include digits')
    parser.add_argument('--symbols', action='store_true', help='Include special characters')
    parser.add_argument('--copy', action='store_true', help='Copy password to clipboard (requires pyperclip)')

    args = parser.parse_args()

    try:
        password = generate_password(
            length=args.length,
            use_uppercase=args.uppercase,
            use_lowercase=args.lowercase,
            use_digits=args.digits,
            use_symbols=args.symbols
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"\n🔑 Generated Password: {password}")

    if args.copy:
        if not CLIPBOARD_ENABLED:
            print("⚠️  Clipboard functionality not available. Install 'pyperclip' to enable it:")
            print("    pip install pyperclip")
        else:
            pyperclip.copy(password)
            print("📋 Password copied to clipboard!")


if __name__ == '__main__':
    main()
