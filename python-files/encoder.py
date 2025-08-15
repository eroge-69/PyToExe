import string

chars = " " + string.punctuation + string.digits + string.ascii_letters
chars = list(chars)

key = ['/', '5', '\\', '{', '$', '?', '6', 'f', 'F', '2', '`', 'M', ')', 'C', '+', '<', 'E', 'O', '7', 'e', 'D', 'b', 'w', 'Z', '*', 'i', 'r', '#', ':', ']', 'n', 'g', 's', 'V', 'G', '1', 'K', '8', '}', 'W', 'P', '0', 'm', 'c', 'j', '_', 'v', '4', 'N', 'T', 'h', 'x', 'Q', 'H', '9', 'A', '!', 'z', 'S', '|', '%', 'B', 'u', 't', 'L', 'd', 'Y', ',', '-', ';', 'U', '(', 'I', '3', '"', 'k', 'p', 'R', "'", 'q', '@', 'J', '&', 'a', 'y', '~', '[', 'o', '.', 'X', '=', 'l', '^', ' ', '>']

#ENCRYPT
plain_text = input("Enter a message to encrypt: ")
cipher_text = ""

for letter in plain_text:
    index = chars.index(letter)
    cipher_text += key[index]

print(f"original message : {plain_text}")
print(f"encrypted message: {cipher_text}")

#DECRYPT
cipher_text = input("Enter a message to encrypt: ")
plain_text = ""

for letter in cipher_text:
    index = key.index(letter)
    plain_text += chars[index]

print(f"encrypted message: {cipher_text}")
print(f"original message : {plain_text}")