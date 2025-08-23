from hashlib import sha256
from base64 import urlsafe_b64encode
from getpass import getpass
from time import sleep
from cryptography.fernet import Fernet

def clear():
    print("\n" * 100)

class PassGen:
    def __init__(self, password : str, key : str):
        self.key = self.__gen_key__(key)
        self.fernet = Fernet(self.key)
        self.password = password
    def encrypt(self):
        return self.fernet.encrypt(self.password.encode())
    def decrypt(self):
        return self.fernet.decrypt(self.password)
    def __gen_key__(self, key : str):
        return urlsafe_b64encode(sha256(key.encode()).digest())

# Auth

print("""
=================================
      
      Authentification

=================================
""")
key = getpass("Input your key: ")
clear()

# Mode

print("""
=================================
      
      Available modes:
      1 - encrypt
      2 - decrypt

=================================
""")
mode = int(input("Choose the mode (1|2): "))
clear()

# Password
print("""
=================================
      
      Provide the data

=================================
""")
password = getpass("Input the password to encrypt/decrypt: ")
clear()

job = PassGen(password, key)
if mode == 1:
    response = job.encrypt().decode()
else:
    response = job.decrypt().decode()

print(f"""

Response to your request:
{response}
   
""")

sleep(3)