from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import requests

def get_btc_balance(address):
    url = f"https://blockchain.info/q/addressbalance/{address}?confirmations=6"
    response = requests.get(url)
    if response.status_code == 200:
        # مقدار به ساتوشی است؛ باید به BTC تبدیل کنیم
        satoshi = int(response.text)
        return satoshi / 1e8
    else:
        return None

def get_trx_balance(address):
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for token in data.get("balances", []):
            if token.get("tokenName") == "TRX":
                return int(token.get("amount", 0)) / 1e6
        return 0.0
    else:
        return None

def main():
    print("Enter your 12-word mnemonic phrase:")
    mnemonic = input("> ").strip()

    # تولید seed
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # ---------------- BTC ----------------
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    btc_address = bip44_acc_ctx.PublicKey().ToAddress()
    btc_balance = get_btc_balance(btc_address)

    # ---------------- TRX ----------------
    bip44_trx_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.TRON)
    trx_acc_ctx = bip44_trx_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    trx_address = trx_acc_ctx.PublicKey().ToAddress()
    trx_balance = get_trx_balance(trx_address)

    print("\n===== Wallet Info =====")
    print(f"BTC Address : {btc_address}")
    print(f"BTC Balance : {btc_balance} BTC" if btc_balance is not None else "BTC Balance : Error")

    print(f"\nTRX Address : {trx_address}")
    print(f"TRX Balance : {trx_balance} TRX" if trx_balance is not None else "TRX Balance : Error")

if name == "main":
    main()
