
import secrets ## For Secure Cryptographic Pseudo Random Number Generation

# Character sets
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']

# Leetspeak map
leet_map = {
    'a': '@', 'A': '@',
    'e': '3', 'E': '3',
    'i': '1', 'I': '1',
    'o': '0', 'O': '0',
    's': '$', 'S': '$',
    'l': '1', 'L': '1'
}
# Leetspeak function 
def leetspeak(phrase):
    return ''.join(leet_map.get(c, c) for c in phrase)

# Validate: max 5 words, each word has both upper & lower case
def is_valid_phrase(phrase):
    words = phrase.strip().split()
    
    if len(words) > 5:
        print(f"❌ Error: Please enter no more than 5 words. \nThis Phrase contains {len(words)}.")
        return False

    for word in words:
        has_upper = any(c.isupper() for c in word)
        has_lower = any(c.islower() for c in word)
        
        if not has_upper or not has_lower:
            print(f"❌ Error: Each word must contain at least one uppercase and one lowercase letter. \nProblem word: {word}.")
            return False

    return True

# Constructing our unique password
def generate_password(phrase):
    phrase_clean = ''.join(phrase.strip().split())  # Remove spaces
    phrase_leet = leetspeak(phrase_clean)

    base_max_len = 14  # Reserve space for 2 symbols and 2 numbers
    base = phrase_leet[:base_max_len]

    # Add exactly 2 symbols and 2 numbers
    extra_symbols = ''.join(secrets.choice(symbols) for _ in range(2))
    extra_numbers = ''.join(secrets.choice(numbers) for _ in range(2))

    # Creating our Custom Password
    password = base + extra_symbols + extra_numbers
    
    # Applying the validation of password lengths being between 14 - 18 chars long
    if 14 <= len(password) <= 18:
        return password
    else:
        return f" Password length is not within the approved password length boundaries (14-18 Chars long)\n Your Password length was {len(password)}.\n Enter a password that is within the approved length."

# Main Flow
print("🔐 Memorable Password Generator (14–18 chars, max 5 words, 2 symbols, 2 numbers)")

phrase = input("Enter a phrase (max 5 words):\n")

# Phrase validation and password generation
if is_valid_phrase(phrase):
    password = generate_password(phrase)
    if password:
        print(f"✅ Your secure, memorable password:\n{password}")
    else:
        print("❌ Error: Unable to generate password within 14–18 character limit.")