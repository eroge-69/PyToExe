import os

def load_keys():
    if not os.path.exists("keys.txt"):
        print("Fajl sa ključevima ne postoji.")
        return []
    with open("keys.txt", "r") as f:
        return [line.strip() for line in f.readlines()]

def check_key(user_key, valid_keys):
    return user_key in valid_keys

def show_menu():
    print("\n--- Multitool Menu ---")
    print("1. IP Geolokacija")
    print("2. Base64 Encode")
    print("3. Base64 Decode")
    print("4. Izlaz")

def ip_lookup():
    import requests
    ip = input("Unesi IP adresu: ")
    response = requests.get(f"http://ip-api.com/json/{ip}")
    data = response.json()
    for key, value in data.items():
        print(f"{key}: {value}")

def base64_encode():
    import base64
    text = input("Unesi tekst: ")
    encoded = base64.b64encode(text.encode()).decode()
    print(f"Encoded: {encoded}")

def base64_decode():
    import base64
    text = input("Unesi Base64 string: ")
    try:
        decoded = base64.b64decode(text).decode()
        print(f"Decoded: {decoded}")
    except Exception as e:
        print(f"Greška: {e}")

def main():
    print("=== Dobrodošao u Multitool ===")
    user_key = input("Unesi ključ: ").strip()
    valid_keys = load_keys()

    if not check_key(user_key, valid_keys):
        print("❌ Pogrešan ključ. Pristup odbijen.")
        return

    print("✅ Pristup dozvoljen!")

    while True:
        show_menu()
        choice = input("Izbor: ")

        if choice == "1":
            ip_lookup()
        elif choice == "2":
            base64_encode()
        elif choice == "3":
            base64_decode()
        elif choice == "4":
            print("Izlaz...")
            break
        else:
            print("Nepoznata opcija.")

if __name__ == "__main__":
    main()
