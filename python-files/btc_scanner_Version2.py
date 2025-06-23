import requests
from mnemonic import Mnemonic
import bip32utils

def generate_wallet():
    mnemo = Mnemonic("english")
    seed_words = mnemo.generate(strength=128)
    seed_bytes = mnemo.to_seed(seed_words, passphrase="")
    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed_bytes)
    bip32_child_key_obj = (
        bip32_root_key_obj
        .ChildKey(44 + bip32utils.BIP32_HARDEN)
        .ChildKey(0 + bip32utils.BIP32_HARDEN)
        .ChildKey(0 + bip32utils.BIP32_HARDEN)
        .ChildKey(0)
        .ChildKey(0)
    )
    address = bip32_child_key_obj.Address()
    privkey = bip32_child_key_obj.WalletImportFormat()
    return seed_words, address, privkey

def check_btc_balance(address):
    try:
        url = f"https://blockstream.info/api/address/{address}"
        res = requests.get(url, timeout=1)
        if res.status_code == 200:
            data = res.json()
            balance = int(data.get("chain_stats", {}).get("funded_txo_sum", 0))
            return balance / 1e8
    except:
        pass
    return 0.0

def main():
    counter = 1
    total_checks = 0
    while True:
        seed, addr, priv = generate_wallet()
        balance = check_btc_balance(addr)
        print(f"{addr} | Mnemonic phrase: {seed} | Balance: [{balance} $]")
        total_checks += 1
        if counter % 100 == 0 or balance > 0:
            print("-" * 70)
        if balance > 0:
            print(f"🎉 Wallet with balance found! Seed: {seed}\nAddress: {addr}\nPrivate Key: {priv}\nBalance: {balance} BTC")
            break
        counter += 1

if __name__ == "__main__":
    main()