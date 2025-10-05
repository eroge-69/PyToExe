import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def GenerateButton_Click(UserIdTextBox):
    return BinGen(UserIdTextBox)

def BinGen(id):
    iddParts = id.split("_")
    
    combinedString = iddParts[1] + iddParts[1] + "3losh"

    md5Hash = ComputeMD5Hash(combinedString)

    key = bytearray(32)
    key[0:5] = md5Hash[0:5]
    key[10:15] = md5Hash[0:5]

    key = bytes(key)
    
    cipher = AES.new(key, AES.MODE_ECB)
    
    iddBytes = SBxx(id)
    padded_data = pad(iddBytes, AES.block_size)
    encryptedBytes = cipher.encrypt(padded_data)

    return base64.b64encode(encryptedBytes).decode('utf-8')

def ComputeMD5Hash(input):
    return hashlib.md5(input.encode('utf-8')).digest()

def SBxx(input):
    return input.encode('utf-8')
print("BinGen By @Drcrypt0r !\n")
print(" ")
user_id = input("Enter User ID: ")
license_key = GenerateButton_Click(user_id)
print("License Key:", license_key)