import re
import socket
from collections import Counter
from typing import Dict, List, Tuple

# --- Yapılandırma ---
# Log dosyanızın yolu. Bu genellikle /var/log/auth.log veya /var/log/secure gibi bir dosya olur.
LOG_DOSYASI = "örnek_log.log" 
# Log dosyasında IP adreslerini tespit etmek için kullanılacak düzenli ifade (regex).
# Bu regex, genel bir IPv4 formatını yakalamak için tasarlanmıştır.
IP_REGEX = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
# Başarısız giriş denemesini belirten anahtar kelime/ifade
HATA_IFADESI = "Failed password" 
# Spamhaus DNSBL sunucusu. IP adresini ters çevirip sonuna bu eklenir.
SPAMHAUS_SUNUCUSU = ".zen.spamhaus.org"
# Spamhaus'tan gelen yanıt kodlarının açıklamaları
SPAMHAUS_KODLARI = {
    "127.0.0.2": "SBL (Spamhaus Block List) - Genel spam faaliyeti",
    "127.0.0.3": "SBL CSS (Spamhaus CSS) - Statik spam göndericileri",
    "127.0.0.4": "XBL (Exploits Block List) - Botnet veya zararlı yazılım kaynaklı",
    "127.0.0.5": "XBL (CBL) - Botnet veya zararlı yazılım kaynaklı (eski CBL)",
    "127.0.0.9": "DROP/EDROP (Don't Route/Extended DROP) - Hijacked/botnet netblock'ları",
    "127.0.0.10": "PBL (Policy Block List) - Dinamik/ev kullanıcısı IP'leri (Sunucu olarak kullanılmamalı)",
    "127.0.0.11": "PBL (Policy Block List) - Dinamik/ev kullanıcısı IP'leri (Sunucu olarak kullanılmamalı)"
}

# ----------------------------------------
# 1. Log Dosyasını Oku ve IP Denemelerini Say
# ----------------------------------------

def log_dosyasini_analiz_et(dosya_yolu: str, hata_ifadesi: str, ip_regex: str) -> Dict[str, int]:
    """
    Belirtilen log dosyasını okur, hata ifadesi içeren satırlardaki IP'leri bulur
    ve her IP için deneme sayısını döndürür.
    """
    ip_denemeleri = Counter()
    try:
        with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
            for satir in f:
                if hata_ifadesi in satir:
                    # Satırda IP adresini ara
                    eslesme = re.search(ip_regex, satir)
                    if eslesme:
                        ip_adresi = eslesme.group(0)
                        ip_denemeleri[ip_adresi] += 1
    except FileNotFoundError:
        print(f"HATA: '{dosya_yolu}' dosyası bulunamadı. Lütfen yolu kontrol edin.")
        return {}
    except Exception as e:
        print(f"HATA: Log dosyasını okurken bir hata oluştu: {e}")
        return {}
        
    return dict(ip_denemeleri)

# ----------------------------------------
# 2. Spamhaus Kontrolü
# ----------------------------------------

def spamhaus_kontrol_et(ip_adresi: str) -> Tuple[bool, str]:
    """
    IP adresini Spamhaus zen.spamhaus.org DNSBL üzerinden sorgular.
    Başarılı olursa True ve Spamhaus listesi/açıklaması, aksi takdirde
    False ve 'Temiz' veya hata mesajı döndürür.
    """
    try:
        # 1. IP adresini ters çevir
        ters_ip = ".".join(reversed(ip_adresi.split(".")))
        # 2. DNS sorgusu için tam alan adını oluştur
        sorgu_adresi = f"{ters_ip}{SPAMHAUS_SUNUCUSU}"
        
        # 3. DNS sorgusunu yap. DNSBL, listedeyse 127.0.0.x formatında bir IP döndürür.
        # DNS sorgusu için sistemin varsayılan çözücüsünü kullanır.
        yanit_ip = socket.gethostbyname(sorgu_adresi)
        
        # 4. Yanıtı kontrol et ve Spamhaus listesini belirle
        if yanit_ip.startswith("127.0.0."):
            aciklama = SPAMHAUS_KODLARI.get(yanit_ip, f"Bilinmeyen Spamhaus Kodu: {yanit_ip}")
            return True, aciklama
        else:
            # Bu durum normalde oluşmamalıdır, genellikle ya 127.0.0.x ya da NXDOMAIN (Bulunamadı)
            return False, "Sorgu Başarısız (Beklenmedik Yanıt)"
            
    except socket.gaierror:
        # socket.gaierror hatası (Name or service not known), IP'nin listede olmadığı anlamına gelir (NXDOMAIN).
        return False, "Temiz (Listede Değil)"
    except Exception as e:
        return False, f"Sorgu Hatası: {e}"

# ----------------------------------------
# Ana Program Çalıştırma
# ----------------------------------------

def main():
    print(f"--- Log Analizi Başlatılıyor: {LOG_DOSYASI} ---")
    
    # Adım 1: IP Denemelerini Say
    ip_deneme_sayilari = log_dosyasini_analiz_et(LOG_DOSYASI, HATA_IFADESI, IP_REGEX)
    
    if not ip_deneme_sayilari:
        print("Analiz edilecek bir IP adresi bulunamadı veya bir hata oluştu.")
        return

    print(f"Tespit Edilen Benzersiz IP Sayısı: {len(ip_deneme_sayilari)}")
    print("\n--- Sonuçlar ---")
    print("IP Adresi         | Deneme Sayısı | Spamhaus Kaydı")
    print("------------------|---------------|----------------------------------------------------")
    
    # Adım 2: Spamhaus Kontrolü ve Sonuçları Göster
    for ip, sayi in sorted(ip_deneme_sayilari.items(), key=lambda item: item[1], reverse=True):
        listede_mi, aciklama = spamhaus_kontrol_et(ip)
        
        if listede_mi:
            kayit_durumu = f"!!! KAYITLI !!! -> {aciklama}"
        else:
            kayit_durumu = aciklama
            
        print(f"{ip:17} | {sayi:13} | {kayit_durumu}")

# ----------------------------------------
# Örnek Log Dosyası Oluşturma (Test Amaçlı)
# ----------------------------------------

def ornek_log_olustur():
    """Programı test etmek için örnek bir log dosyası oluşturur."""
    print(f"'{LOG_DOSYASI}' adında örnek bir log dosyası oluşturuluyor...")
    ornek_icerik = [
        # 1.1.1.1: Temiz bir IP (Çok sayıda deneme)
        "Sep 29 10:00:01 sshd[123]: Failed password for root from 1.1.1.1 port 54321 ssh2",
        "Sep 29 10:00:02 sshd[124]: Failed password for invalid user from 1.1.1.1 port 54322 ssh2",
        "Sep 29 10:00:03 sshd[125]: Failed password for root from 1.1.1.1 port 54323 ssh2",
        "Sep 29 10:00:04 sshd[126]: Failed password for user from 1.1.1.1 port 54324 ssh2",
        "Sep 29 10:00:05 sshd[127]: Failed password for test from 1.1.1.1 port 54325 ssh2",
        # 8.8.8.8: Google DNS (Temiz olmalı, tek deneme)
        "Sep 29 10:00:06 sshd[128]: Failed password for root from 8.8.8.8 port 12345 ssh2",
        # 127.0.0.1: Localhost (Hariç tutulabilir, tek deneme)
        "Sep 29 10:00:07 sshd[129]: Failed password for root from 127.0.0.1 port 22222 ssh2",
        # 104.140.198.125: Spamhaus'ta genellikle listelenen bir IP (Çok sayıda deneme)
        "Sep 29 10:00:08 sshd[130]: Failed password for admin from 104.140.198.125 port 33333 ssh2",
        "Sep 29 10:00:09 sshd[131]: Failed password for user from 104.140.198.125 port 33334 ssh2",
        "Sep 29 10:00:10 sshd[132]: Failed password for root from 104.140.198.125 port 33335 ssh2",
        "Sep 29 10:00:11 sshd[133]: Failed password for test from 104.140.198.125 port 33336 ssh2",
        "Sep 29 10:00:12 sshd[134]: Failed password for admin from 104.140.198.125 port 33337 ssh2",
    ]
    with open(LOG_DOSYASI, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ornek_icerik))
    print("Örnek dosya başarıyla oluşturuldu.\n")


# Programı çalıştır
if __name__ == "__main__":
    # Gerçek bir log dosyanız yoksa bu fonksiyonu çağırarak test yapabilirsiniz
    # ornek_log_olustur()
    
    main()