import time
from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic

Account.enable_unaudited_hdwallet_features()

# === SETUP ===

def load_api_keys(filename="api.txt"):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_wordlist(filename="english.txt"):
    with open(filename, "r") as f:
        words = [line.strip() for line in f if line.strip()]
    if len(words) != 2048:
        raise ValueError("english.txt harus berisi 2048 kata.")
    return words

def load_scanned_seeds(filename="scanned_seeds.txt"):
    try:
        with open(filename, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_scanned_seed(seed, filename="scanned_seeds.txt"):
    with open(filename, "a") as f:
        f.write(seed + "\n")

def save_result(mnemonic, balance):
    # Simpan hanya jika saldo lebih dari nol
    if balance > 0:
        with open("saldo.txt", "a") as f:
            f.write(f"{mnemonic} | {balance:.5f} ETH\n")

# === GENERATE MNEMONIC ===

def generate_valid_mnemonic(custom_wordlist):
    mnemo = Mnemonic("english")
    mnemo.wordlist = custom_wordlist
    return mnemo.generate(strength=128)  # 12 kata

# === DERIVE ADDRESS ===

def derive_address(mnemonic):
    acct = Account.from_mnemonic(mnemonic)
    return acct.address

# === CHECK BALANCE ===

def check_balance(address, infura_url):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    balance_wei = w3.eth.get_balance(address)
    return w3.from_wei(balance_wei, 'ether')

# === MAIN LOOP ===

def main():
    api_keys = load_api_keys("api.txt")
    wordlist = load_wordlist("english.txt")
    scanned_seeds = load_scanned_seeds("scanned_seeds.txt")
    api_index = 0

    print(f"[INFO] Mulai scan, total seed sudah discan: {len(scanned_seeds)}")

    while True:
        mnemonic = generate_valid_mnemonic(wordlist)

        if mnemonic in scanned_seeds:
            continue

        scanned_seeds.add(mnemonic)
        save_scanned_seed(mnemonic)

        try:
            address = derive_address(mnemonic)
        except Exception as e:
            print(f"[ERROR] Derive address gagal: {e}")
            continue

        infura_url = f"https://mainnet.infura.io/v3/{api_keys[api_index]}"
        api_index = (api_index + 1) % len(api_keys)

        print(f"[SCAN] Seed: {mnemonic}")

        try:
            balance = check_balance(address, infura_url)
            print(f"→ Balance: {balance:.5f} ETH\n")

            # Simpan hanya jika saldo > 0
            save_result(mnemonic, balance)

        except Exception as e:
            print(f"[ERROR] Gagal cek saldo: {e}")
            time.sleep(1)

        # Delay antara scan
        time.sleep(0.5)

if __name__ == "__main__":
    main()
