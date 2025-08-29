import hashlib
import string

def generate_password(input_string: str, length: int = 15) -> str:
    # Define a safe set of characters
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.?"
    
    # Create a SHA-256 hash of the input string
    hash_bytes = hashlib.sha256(input_string.encode()).digest()
    
    # Map hash bytes into characters
    password = ''.join(
        characters[b % len(characters)]
        for b in hash_bytes[:length]
    )
    
    return password

# Example usage
user_input = input("Enter a string: ")
print("Generated Password:", generate_password(user_input))