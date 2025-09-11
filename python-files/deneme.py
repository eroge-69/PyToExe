import os
import time
from datetime import datetime

# ==========================================================
# AYARLAR - BU BÖLÜMÜ KENDİNİZE GÖRE DÜZENLEYİN
# ==========================================================
# Silinmesini istediğiniz dosyanın adını girin.
TARGET_FILENAME = "sysas.ask"

# Dosyanın silinmesini istediğiniz tarih ve saati girin.
# Format: YYYY-MM-DD
DELETE_DATE = "2025-09-11" 
# Format: HH:MM
DELETE_TIME = "18:00"

# ==========================================================

LOG_FILENAME = "silici_log.txt"

def write_log(message):
    """
    Belirtilen mesajı bir log dosyasına yazar.
    """
    try:
        with open(LOG_FILENAME, "a") as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        # Log dosyası yazılırken hata oluşursa konsola yaz
        print(f"Log dosyası yazma hatası: {e}")

def secure_delete(filepath):
    """
    Belirtilen dosyayı üzerine rastgele veri yazarak geri dönüştürülemez şekilde siler.
    """
    if not os.path.exists(filepath):
        write_log(f"Hata: Dosya '{filepath}' bulunamadı.")
        return

    try:
        file_size = os.path.getsize(filepath)

        # Dosyayı yazma modunda aç
        with open(filepath, 'r+b') as f:
            # Üzerine rastgele veri yaz
            f.seek(0)
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())

        # Dosyayı sil
        os.remove(filepath)
        write_log(f"Dosya başarıyla silindi: {filepath}")
    except Exception as e:
        write_log(f"Dosya silinirken bir hata oluştu: {e}")

def main():
    """
    Hardcoded değerleri kullanarak dosya silme işlemini zamanlar.
    """
    write_log("Uygulama başlatıldı.")

    # Betiğin bulunduğu dizini bulur
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_filepath = os.path.join(current_directory, TARGET_FILENAME)

    try:
        schedule_time = datetime.strptime(f"{DELETE_DATE} {DELETE_TIME}", "%Y-%m-%d %H:%M")
    except ValueError:
        write_log("Hata: Geçersiz tarih veya saat formatı. Lütfen kod içindeki ayarları kontrol edin.")
        return

    write_log(f"Dosya silme işlemi {schedule_time.strftime('%Y-%m-%d %H:%M')} tarihine ve saatine ayarlandı.")

    while datetime.now() < schedule_time:
        # Her dakika kontrol eder
        time.sleep(60)

    write_log("Silme zamanı geldi, dosya siliniyor...")
    secure_delete(target_filepath)
    write_log("Uygulama sonlandırıldı.")

if __name__ == "__main__":
    main()
