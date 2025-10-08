import hashlib
while True:
    mystring = input('Enter String to hash: ')
    salt = '48KEdeiECSMiXh8cBE4uqNwyecogJ1DxnLc8gdDHfwW090jU'
    a = salt + mystring
    b = a.encode('utf-8')
    hash_object = hashlib.sha256(b)
    print(hash_object.hexdigest())
input()