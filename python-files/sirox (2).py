
import openai
import speech_recognition as sr
import pyttsx3
import json
import os

# ▶️ OpenAI API Anahtarı güvenli şekilde yükleniyor
try:
    with open("api_key.txt", "r") as f:
        openai.api_key = f.read().strip()
except FileNotFoundError:
    print("❌ API anahtar dosyası (api_key.txt) bulunamadı.")
    exit()

# ▶️ Hafıza dosyası
MEMORY_FILE = "memory.json"
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {"chat": []}

# ▶️ Ses motoru ve tanıyıcı
engine = pyttsx3.init()
engine.setProperty("rate", 175)
voice_on = True
recognizer = sr.Recognizer()

def speak(text):
    print("Sirox:", text)
    if voice_on:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"🛠️ Sesli cevapta hata: {e}")

def listen():
    with sr.Microphone() as source:
        print("🎤 Dinliyorum...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="tr-TR")
    except sr.UnknownValueError:
        print("❗ Ses anlaşılamadı.")
        return ""
    except sr.RequestError as e:
        print(f"❗ Google API hatası: {e}")
        return ""

def generate_image(prompt):
    try:
        res = openai.Image.create(prompt=prompt, n=1, size="512x512")
        url = res['data'][0]['url']
        return f"Görsel oluşturuldu: {url}"
    except Exception as e:
        return f"Görsel oluşturulamadı: {e}"

def get_response(prompt):
    try:
        memory["chat"].append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=memory["chat"]
        )
        reply = response.choices[0].message.content.strip()
        memory["chat"].append({"role": "assistant", "content": reply})
        memory["chat"] = memory["chat"][-10:]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False)
        return reply
    except Exception as e:
        return f"❌ Yanıt alınamadı: {e}"

# ▶️ Giriş mesajı
speak("Sirox başlatıldı.")

while True:
    user_input = listen().lower()

    if not user_input:
        continue

    elif "çık" in user_input or "kapat" in user_input:
        speak("Görüşmek üzere.")
        break

    elif "sessiz mod" in user_input:
        voice_on = False
        print("🔇 Sessiz moda geçildi.")

    elif "sesli mod" in user_input:
        voice_on = True
        print("🔊 Sesli moda geçildi.")

    elif "seni kim yaptı" in user_input:
        speak("Abdulhadi Meera yaptı.")

    elif "görsel oluştur" in user_input:
        speak("Ne oluşturmamı istersin?")
        img_prompt = listen()
        img_result = generate_image(img_prompt)
        speak(img_result)

    elif "paragraf yaz" in user_input:
        speak("Hangi konuda yazmamı istersin?")
        topic = listen()
        para_response = get_response(f"{topic} hakkında detaylı bir paragraf yazar mısın?")
        speak(para_response)

    else:
        reply = get_response(user_input)
        speak(reply)
