
import getpass
import time

# بياناتك إنت بس
my_name = "ahmed"
my_password = "123456"
access_code = "X9A7-CODE-2025"

# عدد المحاولات المسموح بها
max_attempts = 3
attempts = 0

print("🔐 Welcome to Secure Access System")

while attempts < max_attempts:
    name = input("👤 Enter your name: ").strip()
    password = getpass.getpass("🔑 Enter your password: ").strip()

    if name == my_name and password == my_password:
        print("\n✅ Access Granted!")
        print(f"🎁 Your Code: {access_code}")
        break
    else:
        attempts += 1
        print(f"❌ Access Denied! Attempts left: {max_attempts - attempts}\n")
        time.sleep(1)

if attempts >= max_attempts:
    print("⛔ Too many failed attempts. Exiting...")
