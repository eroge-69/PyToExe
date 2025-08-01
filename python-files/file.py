def encrypt(data, key):
    encrypted = []
    for char in data:
        # Demonstrates XOR-based encryption pattern
        encrypted.append(ord(char) ^ key)
    
    return bytes(encrypted)

def decrypt(data, key):
    decrypted = ""
    for byte in data:
        # Reverse operation shows decryption flow
        decrypted += chr(byte ^ key)
        
    return decrypted
