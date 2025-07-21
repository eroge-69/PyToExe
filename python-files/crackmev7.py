# crackme_v7.py
import hashlib, base64

def confuse(value):
    h = hashlib.sha256((value[::-1] + "XyZ123").encode()).digest()
    return base64.b64encode(h).decode()

def fake_encrypt(val):
    key = "supersecret"
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(val))

def real_encrypt(val):
    salted = val[::2] + "#Key!" + val[1::2]
    hashed = hashlib.md5(salted.encode()).hexdigest()
    return base64.urlsafe_b64encode(hashed.encode()).decode()

def validate(username, key):
    bait = confuse(username)
    fake = fake_encrypt(username)

    if key == bait or key == fake:
        print("🧂 Salted decoy detected.")
        return False

    expected = real_encrypt(username)
    if key == expected:
        return True
    return False

def main():
    print("=== CrackMe v7 ===")
    username = input("Enter your username: ").strip()
    key = input("Enter license key: ").strip()

    if validate(username, key):
        print("✅ Correct key! Access granted.")
    else:
        print("❌ Invalid key or decoy used.")

if __name__ == "__main__":
    main()
