#!/usr/bin/env python3
"""
Reverse Engineering Challenge 1 - Python Version
Simple Binary Analysis
"""

import sys

def decrypt_flag():
    """Decrypt the hidden flag"""
    # XOR encrypted flag
    encrypted_flag = [
        0x54, 0x54, 0x43, 0x7b, 0x72, 0x65, 0x76, 0x65, 0x72, 0x73, 0x65, 0x64, 
        0x5f, 0x62, 0x69, 0x6e, 0x61, 0x72, 0x79, 0x5f, 0x73, 0x75, 0x63, 0x63, 
        0x65, 0x73, 0x73, 0x7d
    ]
    xor_key = 0x42
    
    print("Decrypting flag...")
    flag = ""
    for byte in encrypted_flag:
        flag += chr(byte ^ xor_key)
    print(f"Flag: {flag}")

def check_password(password):
    """Check if the password is correct"""
    # Simple algorithm - reverse the input and check against hardcoded value
    if len(password) != 8:
        return False
    
    # Reverse the password
    reversed_pass = password[::-1]
    
    # Check against hardcoded value
    expected = "ctf_2024"
    return reversed_pass == expected

def print_banner():
    """Print the challenge banner"""
    print("=" * 40)
    print("    TTC Reverse Engineering Challenge 1")
    print("=" * 40)
    print("Enter the correct password to get the flag!")
    print("Hint: The password is 8 characters long")
    print("Hint: Think about reversing...")
    print()

def main():
    """Main function"""
    print_banner()
    
    try:
        password = input("Password: ")
        
        if check_password(password):
            print("Correct password! ", end="")
            decrypt_flag()
        else:
            print("Incorrect password. Try again!")
            print("Hint: The password should be 8 characters long")
            print("Hint: When reversed, it should equal 'ctf_2024'")
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()