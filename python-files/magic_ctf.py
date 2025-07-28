# random_flag_generator.py
import random
import string

def generate_flag():
    prefix = "CTF{"
    suffix = "}"
    body = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return prefix + body + suffix

def main():
    flag = generate_flag()
    print(f"Your flag is: {flag}")

if __name__ == "__main__":
    main()
