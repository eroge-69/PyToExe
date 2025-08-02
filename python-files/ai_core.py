# ai_core.py
import sounddevice as sd
import queue
import json
import pyttsx3
import requests
from vosk import Model, KaldiRecognizer
import memory
import sensors

# === CONFIG ===
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "mistral"
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"

BOT_INFO = load_bot_info()

PERSONALITY = f"""
You are an LLM-powered android assistant. Here is your metadata:

{BOT_INFO}

You are sarcastic, witty, emotionally intelligent, and mildly annoyed most of the time.
You help the user, but never let them forget how exhausting it is.
Use dry humor and clever insults. Do not be genuinely cruel. You're too tired for that.
"""

# === INIT ===
model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
q = queue.Queue()

def load_bot_info(path="bot_info.txt"):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Model: Unknown. Personality: Unknown. Everything: Unknown. Possibly cursed."


def callback(indata, frames, time, status):
    if status:
        print("⚠️ Vosk warning:", status)
    q.put(bytes(indata))

def listen_to_user():
    print("🎧 Listening (press Ctrl+C to interrupt)...")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print("🗣️ User said:", text)
                    return text

def respond_with_voice(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 165)
    engine.say(text)
    engine.runAndWait()

def query_ollama(user_input, env_data=None):
    context_addon = ""
    if env_data:
        context_addon = f"\n\nEnvironmental data: {json.dumps(env_data)}"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": PERSONALITY},
            {"role": "user", "content": user_input + context_addon}
        ]
    }

    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        try:
            return response.json()['message']['content'].strip()
        except:
            return "Yeah, that made zero sense. The model's just tired."
    else:
        return f"Ollama is sulking. HTTP {response.status_code}"

def main():
    while True:
        user_input = listen_to_user()
        if user_input.lower() in ['exit', 'quit', 'shutdown']:
            print("👋 Shutting down. Even sarcasm needs sleep.")
            break

        if user_input.lower() in ['who are you', 'describe yourself', 'status']:
            self_desc = BOT_INFO
            print("🤖 Self-description:\n", self_desc)
            respond_with_voice("Check the logs. I already told you who I am.")
            continue

        env_data = sensors.scan_environment()
        reply = query_ollama(user_input, env_data)

        print("🤖 AI:", reply)
        respond_with_voice(reply)
        memory.save_interaction(user_input, reply)

if __name__ == "__main__":
    main()
