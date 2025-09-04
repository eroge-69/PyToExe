
# bip_wallet_app_full.py
# Enhanced Streamlit app:
# - Generates BIP39 mnemonic & seed (downloads wordlist automatically if missing)
# - Derives multiple BTC (P2PKH) & ETH addresses
# - Optionally includes private keys (hex + WIF)
# - Exports CSV and ZIP with QR code PNGs
# - Produces master/account xprv/xpub (simple serialization)
#
# Usage:
# 1) Install dependencies: pip install -r requirements.txt
# 2) Run: streamlit run bip_wallet_app_full.py
#
# SECURITY: This creates REAL wallet secrets. Run offline and securely if you plan to fund addresses.

import os, io, hashlib, hmac, unicodedata, struct, streamlit as st, pandas as pd, zipfile, requests
from ecdsa import SECP256k1, SigningKey
from sha3 import keccak_256
from PIL import Image
import qrcode

# ----------------- Config -----------------
WORDLIST_FILE = "bip39_english_wordlist.txt"
WORDLIST_URL = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt"

# ----------------- Helpers: wordlist -----------------
def ensure_wordlist():
    if os.path.isfile(WORDLIST_FILE):
        with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
            words = [w.strip() for w in f.readlines()]
            if len(words) == 2048:
                return words
            else:
                st.warning(f"Found {WORDLIST_FILE} but it has {len(words)} words.")
    # Attempt to download
    try:
        r = requests.get(WORDLIST_URL, timeout=10)
        r.raise_for_status()
        text = r.text
        words = [w.strip() for w in text.splitlines() if w.strip()]
        if len(words) == 2048:
            with open(WORDLIST_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(words))
            return words
        else:
            st.error("Downloaded wordlist didn't contain 2048 words.")
            st.stop()
    except Exception as e:
        st.error(f"Could not find or download the BIP39 wordlist: {e}")
        st.stop()

WORDLIST = ensure_wordlist()

# ----------------- BIP39 -----------------
def generate_bip39_mnemonic(num_words=12):
    ENTROPY_BITS = {12:128, 15:160, 18:192, 21:224, 24:256}[num_words]
    entropy = os.urandom(ENTROPY_BITS // 8)
    h = hashlib.sha256(entropy).digest()
    checksum_len = ENTROPY_BITS // 32
    ent_bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(ENTROPY_BITS)
    chk_bits = bin(int.from_bytes(h, "big"))[2:].zfill(256)[:checksum_len]
    bits = ent_bits + chk_bits
    return [WORDLIST[int(bits[i:i+11], 2)] for i in range(0, len(bits), 11)]

def mnemonic_to_seed(mnemonic_words, passphrase=""):
    mnemonic = unicodedata.normalize("NFKD", " ".join(mnemonic_words))
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac("sha512", mnemonic.encode(), salt.encode(), 2048)

# ----------------- BIP32 -----------------
CURVE = SECP256k1
N = CURVE.order
BIP32_HARDEN = 0x80000000

def hmac_sha512(key, data): return hmac.new(key, data, hashlib.sha512).digest()

def bip32_master_key_from_seed(seed):
    I = hmac_sha512(b"Bitcoin seed", seed)
    IL, IR = I[:32], I[32:]
    k = int.from_bytes(IL, "big")
    return k, IR

def priv_to_pub_compressed(k_int):
    sk = SigningKey.from_secret_exponent(k_int, curve=CURVE)
    vk = sk.verifying_key
    x = vk.pubkey.point.x().to_bytes(32, "big")
    y = vk.pubkey.point.y()
    return (b"\x02" if (y % 2 == 0) else b"\x03") + x

def pub_to_hash160(pubkey_bytes):
    return hashlib.new("ripemd160", hashlib.sha256(pubkey_bytes).digest()).digest()

def ckd_priv(k_par, c_par, index):
    if index & BIP32_HARDEN:
        data = b"\x00" + k_par.to_bytes(32, "big") + struct.pack(">L", index)
    else:
        P = SigningKey.from_secret_exponent(k_par, curve=CURVE).verifying_key
        x = P.pubkey.point.x()
        y = P.pubkey.point.y()
        prefix = b"\x02" if (y % 2 == 0) else b"\x03"
        data = prefix + x.to_bytes(32, "big") + struct.pack(">L", index)
    I = hmac_sha512(c_par, data)
    IL, IR = I[:32], I[32:]
    child_k = (int.from_bytes(IL, "big") + k_par) % N
    return child_k, IR

def derive_path(seed, path):
    k, c = bip32_master_key_from_seed(seed)
    if path == "m":
        return k, c
    for e in path.split("/"):
        if e == "m" or e == "": continue
        hardened = e.endswith("'")
        idx = int(e[:-1]) if hardened else int(e)
        if hardened: idx |= BIP32_HARDEN
        k, c = ckd_priv(k, c, idx)
    return k, c

# ----------------- Addresses and encodings -----------------
ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def base58_encode(data: bytes) -> str:
    num = int.from_bytes(data, "big")
    enc = bytearray()
    while num > 0:
        num, rem = divmod(num, 58)
        enc.append(ALPHABET[rem])
    n_leading = len(data) - len(data.lstrip(b"\x00"))
    return (b"1"*n_leading + enc[::-1]).decode()

def base58check_encode(payload: bytes) -> str:
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return base58_encode(payload + checksum)

def btc_p2pkh_address(pubkey_compressed: bytes, mainnet=True):
    prefix = b"\x00" if mainnet else b"\x6f"
    return base58check_encode(prefix + pub_to_hash160(pubkey_compressed))

def wif_from_privkey(k_int: int, compressed=True, mainnet=True):
    prefix = b'\x80' if mainnet else b'\xef'
    key_bytes = k_int.to_bytes(32, "big")
    payload = prefix + key_bytes + (b'\x01' if compressed else b'')
    return base58check_encode(payload)

def eth_address_from_priv(k_int: int):
    sk = SigningKey.from_secret_exponent(k_int, curve=CURVE)
    vk = sk.verifying_key
    x = vk.pubkey.point.x().to_bytes(32, "big")
    y = vk.pubkey.point.y().to_bytes(32, "big")
    pub = b"\x04" + x + y
    addr = keccak_256(pub[1:]).digest()[-20:].hex()
    hashed = keccak_256(addr.encode()).hexdigest()
    checksummed = "".join(c.upper() if int(hashed[i],16) >= 8 else c for i,c in enumerate(addr))
    return "0x" + checksummed

# ----------------- xprv/xpub (serialize simple) -----------------
def serialize_xprv(version_bytes: bytes, depth: int, parent_fingerprint: bytes, child_number: int, chain_code: bytes, key_int: int) -> str:
    # key_int is private key integer
    data = version_bytes
    data += bytes([depth])
    data += parent_fingerprint
    data += struct.pack(">L", child_number)
    data += chain_code
    data += b'\x00' + key_int.to_bytes(32, "big")
    return base58check_encode(data)

def serialize_xpub(version_bytes: bytes, depth: int, parent_fingerprint: bytes, child_number: int, chain_code: bytes, pubkey_compressed: bytes) -> str:
    data = version_bytes
    data += bytes([depth])
    data += parent_fingerprint
    data += struct.pack(">L", child_number)
    data += chain_code
    data += pubkey_compressed
    return base58check_encode(data)

def fingerprint_from_pubkey(pubkey_compressed):
    return pub_to_hash160(pubkey_compressed)[:4]

# ----------------- QR & ZIP -----------------
def make_qr_bytes(text: str, box_size=6) -> bytes:
    img = qrcode.make(text, box_size=box_size)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="BIP39 Wallet Generator (Full)", layout="wide")
st.title("🔐 BIP39 HD Wallet Generator — Full")

col1, col2 = st.columns([2,3])

with col1:
    num_words = st.selectbox("Mnemonic length", [12,15,18,21,24], index=0)
    passphrase = st.text_input("Optional passphrase", "")
    num_addresses = st.number_input("Addresses to derive", min_value=1, max_value=200, value=20, step=1)
    include_priv = st.checkbox("Include private keys (hex & WIF) in CSV/ZIP", value=False)
    include_qr = st.checkbox("Include QR PNGs in ZIP", value=True)
    generate_btn = st.button("Generate Wallet")

with col2:
    st.markdown("**Notes:** This app will attempt to download the BIP39 English wordlist if missing. It generates real keys — keep them secret.")

if generate_btn:
    mnemonic = generate_bip39_mnemonic(num_words)
    seed = mnemonic_to_seed(mnemonic, passphrase)
    st.subheader("Mnemonic")
    st.code(" ".join(mnemonic))
    st.subheader("Seed (hex)")
    st.code(seed.hex())

    # master key info
    master_k, master_chain = bip32_master_key_from_seed(seed)
    master_pub = priv_to_pub_compressed(master_k)
    st.write("Master fingerprint:", fingerprint_from_pubkey(master_pub).hex())
    # serialize master xprv/xpub (mainnet standard versions: xprv=0x0488ADE4, xpub=0x0488B21E)
    xprv_master = serialize_xprv(b'\x04\x88\xad\xe4', 0, b'\x00\x00\x00\x00', 0, master_chain, master_k)
    xpub_master = serialize_xpub(b'\x04\x88\xb2\x1e', 0, b'\x00\x00\x00\x00', 0, master_chain, master_pub)
    st.write("Master xprv:", xprv_master)
    st.write("Master xpub:", xpub_master)

    # Also derive account node m/44'/0'/0' and give xprv/xpub for account (depth=3)
    acct_k, acct_chain = derive_path(seed, "m/44'/0'/0'")
    acct_pub = priv_to_pub_compressed(acct_k)
    parent_fp = fingerprint_from_pubkey(priv_to_pub_compressed(bip32_master_key_from_seed(seed)[0])) # master fp
    xprv_acct = serialize_xprv(b'\x04\x88\xad\xe4', 3, parent_fp, 0x80000000*44 + 0x80000000*0 + 0x80000000*0, acct_chain, acct_k)
    xpub_acct = serialize_xpub(b'\x04\x88\xb2\x1e', 3, parent_fp, 0x80000000*44 + 0x80000000*0 + 0x80000000*0, acct_chain, acct_pub)
    st.write("Account xprv (m/44'/0'/0'):", xprv_acct)
    st.write("Account xpub (m/44'/0'/0'):", xpub_acct)

    # Prepare dataframe and files
    rows = []
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for i in range(num_addresses):
            # BTC
            k_btc, chain_b = derive_path(seed, f"m/44'/0'/0'/0/{i}")
            pub_btc = priv_to_pub_compressed(k_btc)
            btc_addr = btc_p2pkh_address(pub_btc)
            # ETH
            k_eth, _ = derive_path(seed, f"m/44'/60'/0'/0/{i}")
            eth_addr = eth_address_from_priv(k_eth)
            row = {"index": i, "btc_address": btc_addr, "eth_address": eth_addr}
            if include_priv:
                row["btc_priv_hex"] = k_btc.to_bytes(32, "big").hex()
                row["btc_wif"] = wif_from_privkey(k_btc)
                row["eth_priv_hex"] = k_eth.to_bytes(32, "big").hex()
            rows.append(row)

            # QR PNGs
            if include_qr:
                qr_btc = make_qr_bytes(btc_addr)
                zf.writestr(f"qr/btc_{i}.png", qr_btc)
                qr_eth = make_qr_bytes(eth_addr)
                zf.writestr(f"qr/eth_{i}.png", qr_eth)

        # Also include mnemonic and a README
        zf.writestr("mnemonic.txt", " ".join(mnemonic) + "\n")
        zf.writestr("README.txt", "Generated by bip_wallet_app_full.py. These are real wallet secrets; keep secure.\n")

    df = pd.DataFrame(rows)
    st.subheader("Derived Addresses")
    st.dataframe(df)

    csv_bytes = df.to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv_bytes, file_name="addresses.csv", mime="text/csv")

    zip_bytes = zip_buffer.getvalue()
    st.download_button("Download ZIP (QR PNGs + mnemonic)", data=zip_bytes, file_name="wallet_export.zip", mime="application/zip")
