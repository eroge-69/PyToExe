import secrets
import string

# Generate Key (secrets) || range(<int>)
characters = string.ascii_letters + string.digits
password = "".join(secrets.choice(characters) for i in range(20))
print("Key Generate:\t" + password)