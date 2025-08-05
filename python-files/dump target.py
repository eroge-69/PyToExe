import random
import csv
from faker import Faker

fake = Faker()

# Crypto domains and wallets
crypto_domains = [
    "binance.com", "trustwallet.com", "okx.com",
    "metamask.io", "bybit.com", "kraken.com",
    "coinbase.com", "crypto.com"
]

wallets = [
    "Binance", "Trust Wallet", "OKX", "MetaMask", "Bybit", "Kraken", "Coinbase", "Crypto.com"
]

# Generate fake users
def generate_fake_users(n):
    users = []
    for _ in range(n):
        name = fake.name()
        country = fake.country()
        domain = random.choice(crypto_domains)
        username = fake.user_name()
        email = f"{username}@{domain}"
        wallet = random.choice(wallets)
        users.append({
            "name": name,
            "country": country,
            "email": email,
            "wallet": wallet
        })
    return users

# Save to CSV
def save_to_csv(users, filename="from server_crypto_users.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "country", "email", "wallet"])
        writer.writeheader()
        writer.writerows(users)
    print(f"✅ Saved {len(users)} users to '{filename}'.")

# Run
if __name__ == "__main__":
    fake_users = generate_fake_users(100000)  # change to 1000 or more if needed
    save_to_csv(fake_users)
