
import os
import sys
import time
import pyttsx3
import speech_recognition as sr

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def speak(text, lang="tr"):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Türkçe ses seçimi
    if lang == "tr":
        for v in voices:
            if "tr" in v.id.lower():
                engine.setProperty('voice', v.id)
    engine.say(text)
    engine.runAndWait()

def listen(lang="tr-TR"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Dinliyorum...")
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio, language=lang)
        print(f"✅ Komut: {command}")
        return command
    except:
        print("❌ Ses algılanamadı.")
        return ""

def main():
    clear()
    print("===================================")
    print("      DostPlusGPT Admin Paneli     ")
    print("===================================")
    print("1) GPT'yi Başlat")
    print("2) Çıkış")
    secim = input("Seçiminiz: ")

    if secim == "1":
        clear()
        print("🌍 Dil seçiniz:")
        print("1) Türkçe")
        print("2) English")
        print("3) Русский")
        dil = input("Seçim: ")

        if dil == "1":
            lang = "tr-TR"
            speak("Merhaba, DostPlusGPT başlatıldı!", "tr")
        elif dil == "2":
            lang = "en-US"
            speak("Hello, DostPlusGPT started!", "en")
        elif dil == "3":
            lang = "ru-RU"
            speak("Привет, DostPlusGPT запущен!", "ru")
        else:
            print("Geçersiz seçim, Türkçe başlatılıyor.")
            lang = "tr-TR"

        time.sleep(1)
        clear()
        print("🎤 Sesli komut verebilirsiniz. Çıkmak için 'çıkış' deyin.")

        while True:
            komut = listen(lang)
            if "çıkış" in komut.lower() or "exit" in komut.lower():
                speak("DostPlusGPT kapatılıyor.", "tr")
                print("🚪 Program sonlandırıldı.")
                break
            elif komut:
                print(f"🤖 GPT cevabı: '{komut}' komutunu algıladım.")
                speak(f"{komut} komutunu algıladım.", "tr")

    else:
        print("🚪 Program kapatıldı.")

if __name__ == "__main__":
    main()
