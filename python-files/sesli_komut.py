
import speech_recognition as sr
import keyboard
import time

print("🎤 Mikrofon dinleniyor. 'çizgi' dediğinizde L + Enter gönderilecek.")

def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🔊 Dinleniyor...")

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source, phrase_time_limit=3)
            text = recognizer.recognize_google(audio, language='tr-TR').lower()
            print(f"🗣️ Ses algılandı: {text}")
            if "çizgi" in text:
                keyboard.write("l")
                keyboard.press_and_release("enter")
                print("⌨️ L + Enter gönderildi.")
                time.sleep(1)
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"Hata: {e}")

if __name__ == "__main__":
    main()
