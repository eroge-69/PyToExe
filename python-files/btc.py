from mnemonic import Mnemonic
from bitcoinlib.keys import HDKey
import requests
import concurrent.futures

def generate_btc_address(seed_phrase):
    mnemo = Mnemonic("english")
    if not mnemo.check(seed_phrase):
        raise ValueError("Seed phrase tidak valid")
    seed_bytes = mnemo.to_seed(seed_phrase)
    hdkey = HDKey.from_seed(seed_bytes, network='bitcoin')
    address = hdkey.address()
    return address

def cek_saldo_btc(address):
    url = f"https://blockstream.info/api/address/{address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        funded = data['chain_stats']['funded_txo_sum']
        spent = data['chain_stats']['spent_txo_sum']
        balance_satoshi = funded - spent
        balance_btc = balance_satoshi / 1e8
        return balance_btc
    except requests.exceptions.RequestException as e:
        return f"Error cek saldo Blockstream: {e}"

def process_seed(seed):
    try:
        btc_address = generate_btc_address(seed)
        saldo = cek_saldo_btc(btc_address)
        return seed, btc_address, saldo
    except Exception as e:
        return seed, None, f"Error: {e}"

def simpan_hasil_ke_txt(data, filename="saldo.txt"):
    with open(filename, 'w', encoding='utf-8') as f:
        for seed, saldo in data:
            f.write(f"Seed Phrase: {seed}\n")
            f.write(f"Saldo BTC: {saldo}\n")
            f.write("-" * 30 + "\n")

def main():
    filename = "seed_phrases.txt"
    try:
        with open(filename, 'r') as f:
            seed_phrases = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File '{filename}' tidak ditemukan!")
        return

    max_workers = 5
    hasil = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_seed, seed) for seed in seed_phrases]

        for future in concurrent.futures.as_completed(futures):
            seed, address, saldo = future.result()
            print(f"Seed Phrase: {seed}")
            if address is not None and isinstance(saldo, float):
                print(f"   Bitcoin Address: {address}")
                print(f"   Saldo BTC      : {saldo:.6f} BTC\n")
                if saldo > 0:
                    hasil.append((seed, f"{saldo:.6f} BTC"))
            else:
                print(f"   Gagal: {saldo}\n")

    if hasil:
        simpan_hasil_ke_txt(hasil)
        print(f"Hasil saldo > 0 disimpan ke file 'saldo.txt'")
    else:
        print("Tidak ada saldo > 0 untuk disimpan.")

if __name__ == "__main__":
    main()
