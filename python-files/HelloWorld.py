import time
import sys
import os  # <-- needed for clearing terminal

# Fake BTC address and unlock code
btc_address = "1FfmbHfnpaZjKFvyi1okTjJJusN455paPH"
unlock_code = "PAID1234"

# Clear terminal function
def clear_screen():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

# Display ransom message
def display_ransom():
    clear_screen()
    print("\n" + "="*50)
    print("💀 YOUR SYSTEM IS LOCKED 💀".center(50))
    print("="*50 + "\n")
    print(f"Send $100 BTC to the following address:\n{btc_address}\n")
    print("After payment, enter your payment code to unlock.\n")
    print("="*50 + "\n")

# Main loop
while True:
    display_ransom()
    code = input("Enter payment code: ")
    if code == unlock_code:
        print("\n✅ Payment verified! System unlocked.")
        break
    else:
        print("\n❌ Invalid code. System remains locked.")
        time.sleep(2)
