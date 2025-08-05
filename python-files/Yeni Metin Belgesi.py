import cv2
import numpy as np
import pyautogui
import sounddevice as sd
import scipy.io.wavfile as wav
import threading
import keyboard
import datetime
import os
import wave
import time

# Ayarlar
ekran_boyutu = pyautogui.size()
fps = 20  # Kayıt kalitesi (düşürürsen daha az yer kaplar)
fourcc = cv2.VideoWriter_fourcc(*"XVID")
dosya_tarih = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
video_dosya = f"kayit_{dosya_tarih}.avi"
ses_dosya = f"ses_{dosya_tarih}.wav"
cikis_durum = False
kayit_durum = False
duraklatma = False

# Webcam aç
kamera = cv2.VideoCapture(0)

# Video yazıcı
video_kayit = cv2.VideoWriter(video_dosya, fourcc, fps, ekran_boyutu)

# Ses kaydı listesi
ses_verisi = []

def ses_kaydi():
    global ses_verisi, cikis_durum, kayit_durum, duraklatma
    while not cikis_durum:
        if kayit_durum and not duraklatma:
            data = sd.rec(int(44100 / fps), samplerate=44100, channels=2, dtype='int16')
            sd.wait()
            ses_verisi.append(data)
        else:
            time.sleep(0.1)

def ekran_kaydi():
    global kayit_durum, cikis_durum, duraklatma
    while not cikis_durum:
        if kayit_durum and not duraklatma:
            ekran = pyautogui.screenshot()
            ekran_frame = np.array(ekran)
            ekran_frame = cv2.cvtColor(ekran_frame, cv2.COLOR_BGR2RGB)

            # Kamera görüntüsü
            ret, kamera_frame = kamera.read()
            if ret:
                kamera_frame = cv2.resize(kamera_frame, (200, 150))
                ekran_frame[10:160, 10:210] = kamera_frame

            video_kayit.write(ekran_frame)
            cv2.imshow("Kaydediliyor... (CTRL+SHIFT+E = Çık)", ekran_frame)

            if cv2.waitKey(1) & 0xFF == ord("x"):
                break
        else:
            time.sleep(0.1)

    video_kayit.release()
    kamera.release()
    cv2.destroyAllWindows()

    # Ses dosyasını kaydet
    if ses_verisi:
        ses_np = np.concatenate(ses_verisi, axis=0)
        wav.write(ses_dosya, 44100, ses_np)
        print("🎙️ Mikrofon sesi kaydedildi.")

    print("🎬 Kayıt tamamlandı.")

def kisayol_dinle():
    global kayit_durum, cikis_durum, duraklatma
    print("""
🎮 Kısayollar:
▶  CTRL + SHIFT + S → Kaydı Başlat
⏸  CTRL + SHIFT + D → Kaydı Duraklat / Devam Et
⏹  CTRL + SHIFT + Q → Kaydı Durdur
❌  CTRL + SHIFT + E → Uygulamadan Çık
    """)

    while True:
        if keyboard.is_pressed("ctrl+shift+s"):
            if not kayit_durum:
                kayit_durum = True
                print("▶ Kayıt başladı.")
                time.sleep(1)
        elif keyboard.is_pressed("ctrl+shift+d"):
            if kayit_durum:
                duraklatma = not duraklatma
                print("⏸ Kayıt duraklatıldı." if duraklatma else "▶ Kayıt devam ediyor.")
                time.sleep(1)
        elif keyboard.is_pressed("ctrl+shift+q"):
            if kayit_durum:
                kayit_durum = False
                print("⏹ Kayıt durduruldu.")
                time.sleep(1)
        elif keyboard.is_pressed("ctrl+shift+e"):
            cikis_durum = True
            break
        time.sleep(0.1)

# Thread’ler
threading.Thread(target=ekran_kaydi).start()
threading.Thread(target=ses_kaydi).start()
threading.Thread(target=kisayol_dinle).start()
