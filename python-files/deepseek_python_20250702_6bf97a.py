import time
from datetime import datetime
import pygame
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def resurs_manzili(nisbiy_manzil):
    """EXE fayli uchun resurs manzilini olish"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, nisbiy_manzil)

def papka_tanlash():
    """Musiqa papkasini tanlash uchun oyna ochish"""
    root = tk.Tk()
    root.withdraw()
    
    # Birinchi marta standart papkani tekshirish
    standart_papka = resurs_manzili("musiqa")
    if os.path.exists(standart_papka) and any(f.endswith('.mp3') for f in os.listdir(standart_papka)):
        return standart_papka
    
    # Agar standart papkada MP3 bo'lmasa, foydalanuvchidan so'rash
    papka = filedialog.askdirectory(title="Musiqa qo'shiqlari joylashgan papkani tanlang")
    
    if not papka:
        messagebox.showerror("Xato", "Musiqa papkasi tanlanmadi! Dastur yopiladi.")
        sys.exit()
    
    if not any(f.endswith('.mp3') for f in os.listdir(papka)):
        messagebox.showerror("Xato", "Tanlangan papkada MP3 fayllari topilmadi!")
        sys.exit()
    
    return papka

def qoshiqlarni_yuklash(papka_manzili):
    """MP3 fayllarini yuklash"""
    try:
        qoshiqlar = [os.path.join(papka_manzili, f) for f in os.listdir(papka_manzili) 
                    if f.lower().endswith(".mp3")]
        qoshiqlar.sort()
        return qoshiqlar
    except Exception as e:
        messagebox.showerror("Xato", f"Qo'shiqlarni yuklashda xato: {e}")
        return []

def asosiy():
    # Musiqa papkasini tanlash
    musiqa_papkasi = papka_tanlash()
    qoshiqlar = qoshiqlarni_yuklash(musiqa_papkasi)
    
    if not qoshiqlar:
        messagebox.showerror("Xato", "Ishlash uchun hech qanday qo'shiq topilmadi!")
        sys.exit()
    
    # Tanaffus vaqtlari
    tanaffus_vaqtlari = [
        (10, 35, 10), (12, 20, 40),
        (14, 26, 10), (16, 20, 10),
        (18, 5, 10),
    ]
    
    # Dasturni ishga tushirish
    pygame.mixer.init()
    allaqachon_ijro_etilgan = set()
    qoshiq_indeksi = 0
    
    try:
        while True:
            hozir = datetime.now()
            joriy_vaqt = (hozir.hour, hozir.minute)
            
            for soat, daqiqa, davomiylik in tanaffus_vaqtlari:
                if (soat, daqiqa) == joriy_vaqt and (soat, daqiqa) not in allaqachon_ijro_etilgan:
                    print(f"\n⏰ Tanaffus vaqti! {hozir.strftime('%H:%M')} - {davomiylik} daqiqa")
                    
                    start_time = time.time()
                    while time.time() - start_time < davomiylik * 60:
                        try:
                            current_song = qoshiqlar[qoshiq_indeksi % len(qoshiqlar)]
                            pygame.mixer.music.load(current_song)
                            pygame.mixer.music.play()
                            print(f"🎶 {os.path.basename(current_song)}")
                            
                            while pygame.mixer.music.get_busy():
                                if time.time() - start_time >= davomiylik * 60:
                                    pygame.mixer.music.stop()
                                    break
                                time.sleep(1)
                                
                            qoshiq_indeksi += 1
                        except Exception as e:
                            print(f"Xato: {e}")
                            time.sleep(1)
                    
                    allaqachon_ijro_etilgan.add((soat, daqiqa))
            
            if hozir.hour == 0 and hozir.minute == 0:
                allaqachon_ijro_etilgan.clear()
                
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nDastur to'xtatildi")
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    asosiy()