import requests
import random
import json
import time
import os
import sys
from typing import Optional, Dict

# ============ AYARLAR (ihtiyaca göre düzenle) =============
V3S_URL = "http://91.102.163.174/v3s/"     # PHP dosyasında kullanılan v3s adresi
API_URL = "https://example.com/register"   # Kayıt isteğinin gönderildiği asıl API (php dosyasındaki endpoint ile değiştir)
VERIFY_URL = "https://example.com/verify"  # Doğrulama kodu gönderme/çekme endpoint'i (php dosyasındaki ile eşleştir)
SAVE_FILE = "kayitlar.txt"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100 Safari/537.36"
# =========================================================

def generate_fingerprint() -> str:
    """Sabit fingerprint döndürür (PHP'deki hardcoded)."""
    return "12f21e1a65756deae49ce55edb7c50a9"
    # alternatif rastgele:
    # import secrets; return secrets.token_hex(16)

def convert_date(date_str: str) -> Optional[Dict[str,str]]:
    """DD.MM.YYYY veya DD/MM/YYYY biçimlerindeki tarihi
    YYYY-MM-DD ve parçalarına dönüştürür."""
    if not date_str:
        return None
    date_str = date_str.replace("/", ".").strip()
    parts = date_str.split(".")
    if len(parts) == 3:
        day, month, year = parts[0], parts[1], parts[2]
        return {
            "birthDate": f"{year}-{month.zfill(2)}-{day.zfill(2)}",
            "birthDateDay": day.zfill(2),
            "birthDateMonth": month.zfill(2),
            "birthDateYear": year
        }
    return None

def generate_random_phone() -> str:
    """Türkiye +90 formatında rastgele telefon üretir (php: '905' + 9 hane)."""
    return "905" + str(random.randint(100000000, 999999999))

def get_valid_user_data() -> Dict[str, str]:
    """
    v3s'den kullanıcı verisi alır.
    PHP mantığı: satır satır JSON'lar var; uygun bir kayıt gelene kadar döner.
    """
    print("📦 v3s'ten kullanıcı verisi alınıyor...")
    while True:
        try:
            r = requests.get(V3S_URL, timeout=15)
            raw = r.text.strip()
        except Exception as e:
            print(f"⚠️ v3s'e bağlanırken hata: {e} — 3 saniye sonra tekrar deneniyor")
            time.sleep(3)
            continue

        lines = [ln for ln in raw.splitlines() if ln.strip()]
        for line in lines:
            try:
                entry = json.loads(line)
            except Exception:
                continue

            tc = entry.get("TC Kimlik No", "") or entry.get("TC Kimlik No ", "") or ""
            name = entry.get("Adı", "") or entry.get("Adı ") or ""
            surname = entry.get("Soyadı", "") or entry.get("Soyadı ") or ""
            date_raw = entry.get("Doğrum Tarihi") or entry.get("Doğum Tarihi") or entry.get("DoğumTarihi") or ""

            # isim veya soyisimde boşluk varsa atla (PHP dosyasında böyle eleme vardı)
            if " " in name or " " in surname:
                continue

            date_data = convert_date(date_raw)
            if not (tc and name and surname and date_data):
                continue

            username = entry.get("Kullanıcı Adı") or f"{name.lower()}{random.randint(100,999)}"
            email = f"{username.lower()}@mail.com"

            print(f"✅ Kullanıcı verisi alındı: {name} {surname}")
            return {
                "name": name,
                "surname": surname,
                "username": username,
                "email": email,
                "phone": generate_random_phone(),
                "PersonalNo": tc,
                "country": 236,
                "currencyId": 1,
                "birthDate": date_data["birthDate"],
                "birthDateDay": date_data["birthDateDay"],
                "birthDateMonth": date_data["birthDateMonth"],
                "birthDateYear": date_data["birthDateYear"],
                "password": "123123Aa",
            }

def make_headers(fingerprint: str) -> Dict[str,str]:
    """Kayıt isteği için header'ları hazırlar."""
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "x-fingerprint": fingerprint
    }

def write_save_file(line: str):
    """Kaydı dosyaya ekler (UTF-8)."""
    with open(SAVE_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def send_registration(payload: Dict, headers: Dict, proxies: Optional[Dict]=None, timeout: int=30) -> Optional[requests.Response]:
    """
    Kayıt isteğini gönderir. PHP'deki curl işlevinin karşılığı.
    proxies parametresi istenirse requests ile verilebilir.
    """
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=timeout, proxies=proxies)
        return resp
    except Exception as e:
        print(f"❌ Kayıt isteği gönderilemedi: {e}")
        return None

def check_verify_code(phone: str, token: str, headers: Dict, proxies: Optional[Dict]=None) -> Optional[bool]:
    """
    Telefon doğrulaması gibi bir endpoint varsa çağrılır.
    (PHP dosyasındaki mantığa göre burada doğrulama kontrolü yapılıyordu.)
    Bu fonksiyon örnek/placeholder'dır: gerçek endpoint'e göre uyarlayın.
    """
    try:
        data = {
            "phone": phone,
            "token": token,
        }
        r = requests.post(VERIFY_URL, json=data, headers=headers, timeout=20, proxies=proxies)
        # PHP'de muhtemelen r.body JSON parse ediliyor; burada de aynı şekilde
        try:
            j = r.json()
            # örnek: {"status":"ok"} veya {"success": True} vs.
            if isinstance(j, dict):
                if j.get("success") or j.get("status") == "ok":
                    return True
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"⚠️ Doğrulama kontrolünde hata: {e}")
        return None

def main_loop():
    """
    Ana akış: v3s -> payload oluştur -> kayıt isteği gönder -> doğrulama -> kaydet
    PHP dosyasındaki mantığı takip eder.
    """
    while True:
        user = get_valid_user_data()
        fingerprint = generate_fingerprint()

        # payload'u PHP mantığına göre kuruyoruz (örnek)
        payload = {
            "name": user["name"],
            "surname": user["surname"],
            "username": user["username"],
            "email": user["email"],
            "password": user["password"],
            "phone": [user["phone"]],   # PHP tarafında phone1/phone2 vs. olabilirdi
            "personalNo": user["PersonalNo"],
            "country": user["country"],
            "currencyId": user["currencyId"],
            "birthDate": user["birthDate"],
            "birthDateDay": user["birthDateDay"],
            "birthDateMonth": user["birthDateMonth"],
            "birthDateYear": user["birthDateYear"],
            "fingerprint": fingerprint
        }

        headers = make_headers(fingerprint)

        print("🚀 Kayıt isteği gönderiliyor...")
        resp = send_registration(payload, headers)

        if resp is None:
            print("❌ İstek başarısız; 2 saniye bekleyip devam ediliyor.")
            time.sleep(2)
            continue

        # Yanıt kontrolü (PHP dosyasındaki mantığa göre)
        try:
            js = resp.json()
        except Exception:
            js = None

        if resp.status_code == 200 and js:
            # başarılıysa dosyaya kaydet (PHP dosyasında farklı alanlar kaydediliyordu)
            # Kaydetme formatını PHP'de olduğu gibi JSON_UNESCAPED_UNICODE ile kaydediyoruz
            line = json.dumps({
                "username": user["username"],
                "email": user["email"],
                "phone": user["phone"],
                "personalNo": user["PersonalNo"],
                "response": js
            }, ensure_ascii=False)
            write_save_file(line)
            print(f"💾 Kullanıcı başarıyla kaydedildi: {user['username']}")

            # Eğer doğrulama tokeni veya telefon doğrulaması gerekiyorsa PHP mantığı burada vardı.
            # Örnek: token = js.get('token') ve sonra check_verify_code çağrısı
            token = js.get("token") if isinstance(js, dict) else None
            if token:
                ok = check_verify_code(user["phone"], token, headers)
                if ok:
                    print("✅ Telefon onayı başarılı.")
                else:
                    print("⚠️ Telefon onayı başarısız veya kontrol edilemedi.")
            else:
                print("ℹ️ Yanıtta token bulunmadı; telefon doğrulaması atlanıyor.")

        else:
            print("❌ Kayıt başarısız: HTTP", resp.status_code)
            # hata yanıtı varsa çıktıyı kaydet
            try:
                errtxt = resp.text
            except Exception:
                errtxt = "<no body>"
            write_save_file(json.dumps({
                "username": user["username"],
                "email": user["email"],
                "error_status": resp.status_code,
                "error_body": errtxt
            }, ensure_ascii=False))
        # PHP dosyasında döngü ve sleep vardı:
        print("\n==============================\n✅ İşlem tamamlandı.\n==============================\n")
        time.sleep(1)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nÇıkılıyor (CTRL+C).")
        sys.exit(0)
