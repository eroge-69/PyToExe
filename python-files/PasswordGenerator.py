import random
import string

def generate_password(length):
    # Define the character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation
    
    # Combine all characters into one pool
    all_characters = uppercase + lowercase + digits + symbols
    
    # Ensure that the password contains at least one of each character type
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(symbols)
    ]
    
    # Fill the rest of the password length with random characters from the pool
    password += random.choices(all_characters, k=length - 4)
    
    # Shuffle the password list to ensure randomness
    random.shuffle(password)
    
    # Join the list into a string and return it
    return ''.join(password)

# Example usage:
password_length = int(input("Enter password length: "))
print("Generated password:", generate_password(password_length))
