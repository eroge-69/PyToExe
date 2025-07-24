import hashlib
import sys
import json

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        text = sys.argv[2]
        
        if action == "hash":
            print(hash_text(text))
        elif action == "verify":
            stored_hash = sys.argv[3]
            print("true" if hash_text(text) == stored_hash else "false")
