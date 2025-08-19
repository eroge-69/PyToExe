import random
import time
import os

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_code():
    return '-'.join(''.join(random.choice(chars) for _ in range(4)) for _ in range(4))

def main():
    clear()
    print("==================================================")
    print("      Welcome to the GTA V Activation Generator")
    print("==================================================\n")
    
    access_key = input("Enter your access key: ").strip()
    # ระบบตรวจสอบ Access Key ปลอม
    if access_key:
        print("✔ Access key is valid.\n")
    else:
        print("❌ Invalid access key!")
        return
    
    try:
        num = int(input("How many keys would you like to generate (1-5): "))
        if num < 1 or num > 5:
            num = 1
    except:
        num = 1

    print("\n[GENERATING KEYS...]")
    time.sleep(1)
    
    for _ in range(num):
        code = generate_code()
        print(f"[VALID KEY] {code}")
        time.sleep(0.5)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
