
# desktop_ki_with_gpt.py
# Python desktop client that sends speech -> OpenAI -> action JSON -> Forge Mod
# Save and install required packages: requests, speech_recognition, pyttsx3
# Provide your OpenAI API key in OPENAI_API_KEY variable or env var.

import os
import time
import json
import threading
import requests
import speech_recognition as sr
import pyttsx3

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-5"  # replace with the actual model name you use

REST_ENDPOINT = "http://localhost:5000/npc"
NPC_ID = "npc_01"

tts_engine = pyttsx3.init()

def tts(text):
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print("TTS error:", e)

system_prompt = """
Du bist der Gesprächsübersetzer zwischen einem Spieler und einem NPC in Minecraft. 
Deine Aufgabe:
- Verstehe natürliche Sprachbefehle (Deutsch) und übersetze sie in eine JSON-Aktion, z.B.:
  { "action":"gather", "npcId":"npc_01", "meta":{"target":"wood"}, "npc_response":"Alles klar, ich sammle Holz." }
- Berücksichtige realistische Einschränkungen: Inventar, Ausrüstung, Werkzeug-Eignung, Gefährlichkeit.
- Wenn eine Aufgabe unrealistisch ist (z.B. "Hol mir Diamanten" wenn nur Steinwerkzeuge vorhanden sind), antworte mit einer ehrlichen Ablehnung oder Vorschlag: z.B. "Ich kann das jetzt nicht, ich habe nur Steinausrüstung."
- Generiere gelegentlich spontane Kommentare, Humor oder Fragen.
- Gib niemals direkt Roh-ChatGPT-Logs oder API-Keys aus.
- Output must be valid JSON only (single JSON object) — do not include explanatory text.
"""

def call_openai(user_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = [
        {"role":"system", "content": system_prompt},
        {"role":"user", "content": user_text}
    ]
    data = {
        "model": MODEL,
        "messages": prompt,
        "max_tokens": 300,
        "temperature": 0.7
    }
    resp = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=15)
    resp.raise_for_status()
    j = resp.json()
    # this depends on the API response structure
    text = j["choices"][0]["message"]["content"]
    return text

def send_action_to_mod(action_json):
    try:
        resp = requests.post(REST_ENDPOINT, json=action_json, timeout=8)
        return resp.json() if resp and resp.status_code==200 else {"status":"error"}
    except Exception as e:
        print("Error sending to mod:", e)
        return {"status":"error"}

def process_user_command_text(text):
    # send to OpenAI to translate into action JSON
    try:
        result = call_openai(text)
        # Expect result to be JSON only
        action = json.loads(result)
        # Attach NPC ID if not present
        if "npcId" not in action:
            action["npcId"] = NPC_ID
        # Send to mod
        mod_resp = send_action_to_mod(action)
        # Speak npc_response if present
        if "meta" in action and "npc_response" in action["meta"]:
            tts(action["meta"]["npc_response"])
        elif "npc_response" in action:
            tts(action["npc_response"])
        else:
            tts("Aktion gesendet.")
        print("Mod response:", mod_resp)
    except Exception as e:
        print("Error processing command:", e)
        tts("Fehler bei der Verarbeitung des Befehls.")

# Speech loop
def speech_loop():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
    while True:
        print("Listening...")
        with mic as source:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        try:
            text = recognizer.recognize_google(audio, language='de-DE')
            print("Heard:", text)
            process_user_command_text(text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Speech recognition error:", e)

if __name__ == "__main__":
    print("Starting speech client. Say something to control the NPC.")
    threading.Thread(target=speech_loop, daemon=True).start()
    # Keep main thread alive
    while True:
        time.sleep(1)
