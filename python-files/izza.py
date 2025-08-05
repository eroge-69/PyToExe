import os
import hashlib
import ecdsa
import base58

# Puzzle #135 public key (compressed)
TARGET_PUBKEY = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"

# Range: 0x4000... to 0x7fff...
START_KEY = int("4000000000000000000000000000000000", 16)
END_KEY   = int("7fffffffffffffffffffffffffffffffff", 16)

# Keys per chunk
CHUNK_SIZE = 10000
PROGRESS_FILE = "progress.txt"
RESULT_FILE = "match_found.txt"

def save_progress(chunk_index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(chunk_index))

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read())
    return 0

def private_key_to_wif(priv_hex: str) -> str:
    extended_key = b'\x80' + bytes.fromhex(priv_hex) + b'\x01'
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    final_key = extended_key + checksum
    return base58.b58encode(final_key).decode()

def private_key_to_pubkey(priv_hex: str) -> str:
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(priv_hex), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    pk = b'\x02' + vk.to_string()[:32] if vk.to_string()[32] < 128 else b'\x03' + vk.to_string()[:32]
    return pk.hex()

def scan_chunk(start):
    for i in range(CHUNK_SIZE):
        key_int = start + i
        priv_hex = hex(key_int)[2:].zfill(64)
        pubkey = private_key_to_pubkey(priv_hex)
        if pubkey.lower() == TARGET_PUBKEY.lower():
            print(f"🎯 MATCH FOUND!\nPrivate Key: {priv_hex}")
            with open(RESULT_FILE, "w") as f:
                f.write(f"Private Key: {priv_hex}\nWIF: {private_key_to_wif(priv_hex)}")
            return True
    return False

def main():
    print("🚀 Starting Izza Rani v2 - Puzzle #135 Scanner")
    chunk_index = load_progress()
    total_chunks = (END_KEY - START_KEY) // CHUNK_SIZE

    while chunk_index < total_chunks:
        start = START_KEY + chunk_index * CHUNK_SIZE
        print(f"🧩 Scanning Chunk {chunk_index} starting at {hex(start)}")
        if scan_chunk(start):
            break
        chunk_index += 1
        save_progress(chunk_index)

    print("✅ Done scanning.")

if __name__ == "__main__":
    main()
