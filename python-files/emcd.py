# CapsuleMiner432 Pro - CONFIGURED for EMCD Pool

import socket, json, hashlib, struct, threading, time, pygame, random, sys

# === CONFIG ===
USERNAME = "abrahamarshad17.worker"   # ← Your EMCD account.worker name
PASSWORD = "x"                        # ← Can be anything
POOL = "cn.emcd.network"              # ← EMCD pool server
PORT = 3333

# === CAPSULE CONSTANTS ===
CAPSULE_FREQUENCY = 432
CAPSULE_Q = 0.8
CAPSULE_T = 1.4
CAPSULE_SV = 0.65
CAPSULE_O = 0.80

# === AI Parameters ===
BASE_NONCE_STEP = 1
TARGET_TEMP = 45
MAX_THREADS = 4

# === INIT ===
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("CapsuleMiner432 Pro")
font = pygame.font.SysFont("Courier", 20)
clock = pygame.time.Clock()

hashrate_avg = []
found_hashes = []

def sha256d(header):
    return hashlib.sha256(hashlib.sha256(header).digest()).digest()

def capsule_energy():
    t = time.time() % 3600
    return CAPSULE_Q * CAPSULE_FREQUENCY * (CAPSULE_SV * CAPSULE_O) * CAPSULE_T * (t ** 3)

def adaptive_nonce_step(temp, energy):
    if temp > TARGET_TEMP:
        return max(1, int(BASE_NONCE_STEP * 0.5))
    elif energy > 1e19:
        return int(BASE_NONCE_STEP * 2)
    else:
        return BASE_NONCE_STEP

def draw_stats(stats):
    screen.fill((10, 10, 30))
    for i, (key, val) in enumerate(stats.items()):
        val_str = str(val)
        color = (255, 215, 0) if "FOUND" in val_str else (0, 255, 100)
        text = font.render(f"{key}: {val_str}", True, color)
        screen.blit(text, (20, 30 * i + 20))
    pygame.display.flip()

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((POOL, PORT))
    return s

def send_msg(sock, data):
    msg = json.dumps(data) + "\n"
    sock.sendall(msg.encode())

def recv_msg(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed.")
        data += chunk
        lines = data.decode(errors="ignore").split("\n")
        for line in lines:
            if line.strip():
                try:
                    return json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

def submit_share(sock, job_id, extranonce2, nonce, ntime, nbits):
    submit_data = {
        "id": 4,
        "method": "mining.submit",
        "params": [USERNAME, job_id, extranonce2, ntime, nonce, nbits]
    }
    print("[>] Submitting share:", submit_data)
    send_msg(sock, submit_data)

def miner_thread(job_id, data, target, extranonce2, nonce_start, nonce_end, result_list):
    start_time = time.time()
    for nonce in range(nonce_start, nonce_end):
        header = data[:76] + struct.pack("<I", nonce)
        hash_bin = sha256d(header)
        hash_hex = hash_bin[::-1].hex()
        if hash_hex < target:
            result_list.append((job_id, extranonce2, nonce, hash_hex))
            found_hashes.append((time.strftime("%H:%M:%S"), hash_hex))
            break
    end_time = time.time()
    hashrate_avg.append((nonce_end - nonce_start) / (end_time - start_time + 0.001))

def main():
    temp = 38.0
    energy = capsule_energy()
    nonce_step = BASE_NONCE_STEP
    stats = {
        "Status": "Connecting...",
        "Temp": f"{temp:.1f} °C",
        "Capsule Energy": f"{energy:.2e} J",
        "Nonce Step": nonce_step,
        "Hashrate": "0 H/s",
        "Shares Found": "0"
    }

    try:
        s = connect()
    except Exception as e:
        print(f"[X] Connection failed: {e}")
        stats["Status"] = "Connection failed"
        draw_stats(stats)
        time.sleep(3)
        return

    send_msg(s, {"id": 1, "method": "mining.subscribe", "params": []})
    sub_reply = recv_msg(s)
    extranonce1 = sub_reply["result"][1]
    extranonce2_size = sub_reply["result"][2]

    send_msg(s, {"id": 2, "method": "mining.authorize", "params": [USERNAME, PASSWORD]})
    recv_msg(s)

    stats["Status"] = "Subscribed"
    draw_stats(stats)

    target = "00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

    while True:
        try:
            msg = recv_msg(s)
        except Exception as e:
            print(f"[X] Receive failed: {e}")
            stats["Status"] = "Disconnected"
            draw_stats(stats)
            break

        if "method" in msg:
            method = msg["method"]

            if method == "mining.set_difficulty":
                difficulty = msg["params"][0]
                target_int = int((2 ** 256) / difficulty)
                target = '{:064x}'.format(target_int)

            elif method == "mining.notify":
                job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean = msg["params"]

                extranonce2 = str(random.randint(0, 999999)).zfill(extranonce2_size * 2)
                coinbase = coinb1 + extranonce1 + extranonce2 + coinb2
                coinbase_hash = sha256d(bytes.fromhex(coinbase)).hex()

                merkle_root = coinbase_hash
                for branch in merkle_branch:
                    merkle_root = sha256d(bytes.fromhex(merkle_root + branch)).hex()

                block_header = version + prevhash + merkle_root + nbits + ntime + "00000000"
                data = bytes.fromhex(block_header)

                nonce_start = 0
                nonce_end = 2 ** 24

                energy = capsule_energy()
                temp += random.uniform(-0.3, 0.3)
                nonce_step = adaptive_nonce_step(temp, energy)

                results = []
                threads = []
                for i in range(MAX_THREADS):
                    start = nonce_start + i * (nonce_end // MAX_THREADS)
                    end = start + (nonce_end // MAX_THREADS)
                    t = threading.Thread(target=miner_thread,
                                         args=(job_id, data, target, extranonce2, start, end, results))
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join()

                if results:
                    job_id, extranonce2, nonce, hash_hex = results[0]
                    print(f"[✓] FOUND: JobID {job_id}, Nonce {nonce}, Hash {hash_hex}")
                    submit_share(s, job_id, extranonce2, format(nonce, '08x'), ntime, nbits)
                    stats["Status"] = f"FOUND: {nonce}"
                    stats["Shares Found"] = str(len(found_hashes))
                else:
                    stats["Status"] = "Mining..."

        stats["Temp"] = f"{temp:.1f} °C"
        stats["Capsule Energy"] = f"{energy:.2e} J"
        stats["Nonce Step"] = nonce_step
        if hashrate_avg:
            stats["Hashrate"] = f"{sum(hashrate_avg[-10:])/len(hashrate_avg[-10:]):.2f} H/s"
        draw_stats(stats)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(2)

if __name__ == "__main__":
    main()
