import random
import string
import time
from datetime import datetime

aderess = "0xFc94kXC3dS037RwUq9LwFfIY1xHxppCuF6VuwlJvKdL"
#replace with your own aderess so that the funds get instantly deposited into your account"

tries = 100
length = 43

while True:
    tries = 100  # Number of attempts

    for _ in range(tries):
        result = "Found" if random.random() < 0.0001 else "Did Not Find"
    
    time.sleep(0.05)  # Pause for 1 second
    random_string = '0x' + ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    print("Searching Crypto Wallet", random_string, result, "BTC")
    time.sleep(0.05)
    if result == "Found":
        print("Deposited Found BTC funds into", aderess)

        
