import sounddevice as sd
from scipy.io.wavfile import write
import requests, os, datetime

# Parametrlər
DURATION = 300   # 1 dəqiqə = 60 saniyə
FS = 44100
SERVER_URL = "https://texnosoft.com.tr/ses/index.php"

while True:
    # Unikal fayl adı
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"record_{timestamp}.wav"

    print(f"🔴 Yazılır: {filename} (1 dəqiqə)")
    recording = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype='int16')
    sd.wait()

    # Faylı saxla
    write(filename, FS, recording)
    print(f"✅ Yazı tamamlandı: {filename}")

    # Serverə göndər
    try:
        with open(filename, "rb") as f:
            response = requests.post(SERVER_URL, files={"audio": f})
            print("⬆️ Server cavabı:", response.text)
    except Exception as e:
        print("❌ Göndərmə xətası:", e)

    # Lokal faylı sil
    if os.path.exists(filename):
        os.remove(filename)
        print("🗑️ Fayl silindi\n")
