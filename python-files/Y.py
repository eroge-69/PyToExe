import pyttsx3

def pronounce_text(text):
    """
    Kullanıcının girdiği metni sesli olarak okur.

    Bu işlev, pyttsx3 kütüphanesini kullanarak metni
    sesli olarak telaffuz eder. Eğer bir Fransızca ses paketi
    bulunursa onu kullanır, aksi takdirde sistemin varsayılan
    sesini kullanır.

    Args:
        text (str): Sesli olarak okunacak metin.
    """
    normalized_text = text.strip()

    if not normalized_text:
        print("Hata: Lütfen sesli okunacak bir metin girin.")
        return

    # pyttsx3 kütüphanesini başlat
    engine = pyttsx3.init()

    # Fransızca ses paketi bulmaya çalış
    french_voice = None
    voices = engine.getProperty('voices')
    for voice in voices:
        # Fransızca sesleri bulmak için etiketleri kontrol et
        if 'fr' in voice.id.lower() or 'french' in voice.name.lower():
            french_voice = voice
            break

    if french_voice:
        engine.setProperty('voice', french_voice.id)
    else:
        print("Uyarı: Fransızca ses paketi bulunamadı, telaffuz varsayılan sesle yapılacaktır.")

    # Metni sesli oku ve işlemin tamamlanmasını bekle
    print(f"'{text}' telaffuz ediliyor...")
    engine.say(text)
    engine.runAndWait()
    print("Telaffuz tamamlandı.")

def main():
    """Ana program döngüsü."""
    print("Fransızca Telaffuz Uygulamasına Hoş Geldiniz!")
    print("Çıkmak için 'exit' yazın.")

    while True:
        user_input = input("Fransızca bir kelime veya cümle girin: ")

        if user_input.lower() == 'exit':
            print("Uygulamadan çıkılıyor...")
            break

        pronounce_text(user_input)

if __name__ == "__main__":
    # Programı çalıştırmadan önce pyttsx3 kütüphanesini kurduğunuzdan emin olun.
    # Terminale şunu yazın: pip install pyttsx3
    main()
