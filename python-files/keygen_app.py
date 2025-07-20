import hashlib, base64
import getpass

USERNAME = "vZey"
PASSWORD = "vZey1506;"

SECRET_KEY = "vZey1506;"

def generate_key(input_str):
    hashed = hashlib.sha256((input_str + SECRET_KEY).encode()).digest()
    return base64.urlsafe_b64encode(hashed).decode()

def main():
    print("=== License Key Generator ===")
    user = input("Username: ")
    pw = getpass.getpass("Password: ")

    if user != USERNAME or pw != PASSWORD:
        print("❌ Access denied.")
        return

    raw_code = input("Enter a base code (like user's name or ID): ").strip()
    license_key = generate_key(raw_code)

    print("\n✅ License key to send to user:\n" + license_key)

    # Optional: Save to file so the main.exe knows this key is legit
    with open("valid_keys.txt", "a") as f:
        f.write(license_key + "\n")

if __name__ == "__main__":
    main()
