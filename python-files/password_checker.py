import re
import random
import string

# Function to generate a strong password suggestion
def suggest_password(password):
    # Start with the original password or pad it
    suggestion = password

    # Ensure it's at least 8 characters long
    if len(suggestion) < 8:
        suggestion += ''.join(random.choices(string.ascii_letters + string.digits, k=8 - len(suggestion)))

    # Add missing character types
    if not re.search("[A-Z]", suggestion):
        suggestion += random.choice(string.ascii_uppercase)
    if not re.search("[a-z]", suggestion):
        suggestion += random.choice(string.ascii_lowercase)
    if not re.search("[0-9]", suggestion):
        suggestion += random.choice(string.digits)
    if not re.search("[@#$%^&*]", suggestion):
        suggestion += random.choice("@#$%^&*")

    # Shuffle to avoid predictable patterns
    suggestion = ''.join(random.sample(suggestion, len(suggestion)))
    return suggestion

# Function to check password strength
def password_strength(password):
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long.")
    if not re.search("[A-Z]", password):
        issues.append("Add at least one uppercase letter.")
    if not re.search("[a-z]", password):
        issues.append("Add at least one lowercase letter.")
    if not re.search("[0-9]", password):
        issues.append("Add at least one number.")
    if not re.search("[@#$%^&*]", password):
        issues.append("Include at least one special character (@#$%^&*).")

    if issues:
        print("Weak Password:")
        for issue in issues:
            print(f"- {issue}")
        print("\nSuggested Strong Password:")
        print(f"=> {suggest_password(password)}")
    else:
        print("Strong Password!")

# Take user input
user_password = input("Enter a password to check its strength: ")
# Call the function
password_strength(user_password)