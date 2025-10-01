import json
import datetime
import time
import pygame
import os

# Pygame mixer'ı başlat
pygame.mixer.init()

# Zil konfigürasyonu dosyasını yükle (bells.json)
def load_config(filename='bells.json'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Varsayılan konfigürasyon
        default_config = [
            {
                "time": "08:00",
                "sound": "bell1.mp3",  # Farklı zil sesleri için dosya adı
                "student_ann": "Günaydın sevgili öğrenciler! Dersler başlıyor.",
                "teacher_ann": "Öğretmenler, lütfen sınıflarınıza geçin."
            },
            {
                "time": "09:00",
                "sound": "bell2.mp3",
                "student_ann": "Ara vakti! 10 dakika mola.",
                "teacher_ann": "Öğretmenler, ara için hazır olun."
            },
            {
                "time": "15:00",
                "sound": "bell1.mp3",
                "student_ann": "Okul bitti! İyi günler.",
                "teacher_ann": "Günlük işler tamamlandı."
            }
        ]
        save_config(default_config, filename)
        return default_config

# Konfigürasyonu kaydet (değişiklikler için)
def save_config(config, filename='bells.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Zil çal ve anonsları yap
def ring_bell(bell):
    # Zil sesini çal (dosya mevcut olmalı)
    if os.path.exists(bell["sound"]):
        pygame.mixer.music.load(bell["sound"])
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    else:
        print(f"Uyarı: {bell['sound']} ses dosyası bulunamadı.")
    
    # Anonslar (basitçe yazdır; gerçekte TTS eklenebilir)
    print(f"\n--- ÖĞRENCİ ANONSU ({bell['time']}): {bell['student_ann']} ---")
    print(f"--- ÖĞRETMEN ANONSU ({bell['time']}): {bell['teacher_ann']} ---\n")

# Ana döngü
def main():
    config = load_config()
    print("Okul zil programı başlatıldı. Konfigürasyon 'bells.json' dosyasından yüklendi.")
    print("Değişiklik yapmak için programı durdurun, JSON'ı düzenleyin ve yeniden başlatın.")
    
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for bell in config:
            if now == bell["time"]:
                ring_bell(bell)
                time.sleep(60)  # Bir sonraki dakikaya geç (aynı dakikada tekrar çalmasın)
                break
        time.sleep(1)  # Her saniye kontrol et

if __name__ == "__main__":
    main()