import whisper
import gradio as gr
import webbrowser
import requests
import os
import platform
import subprocess

# Load Whisper model
model = whisper.load_model("base")

# Your OpenRouter API key
OPENROUTER_API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "deepseek/deepseek-chat:free"

# Weather coordinates (Dhaka example)
LAT, LON = 23.8103, 90.4125

# ----- WEATHER -----
def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
        res = requests.get(url)
        data = res.json()
        temp = data['current_weather']['temperature']
        wind = data['current_weather']['windspeed']
        return f"🌤️ Weather in Dhaka:\nTemperature: {temp}°C\nWind Speed: {wind} km/h"
    except Exception as e:
        return f"❌ Weather fetch error: {e}"

# ----- OPEN BROWSER -----
def open_browser_path(browser_name):
    try:
        if browser_name == "opera":
            if platform.system() == "Windows":
                path = r"C:\Users\%USERNAME%\AppData\Local\Programs\Opera\launcher.exe"
                subprocess.Popen(path, shell=True)
            else:
                subprocess.Popen(["opera"])
        elif browser_name == "edge":
            if platform.system() == "Windows":
                os.system("start msedge")
            else:
                subprocess.Popen(["microsoft-edge"])
        return f"🔓 Opening {browser_name.capitalize()}..."
    except Exception as e:
        return f"❌ Failed to open {browser_name}: {e}"

# ----- LLM CHATBOT -----
def query_openrouter(message):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Voice AI Assistant"
        }

        payload = {
            "model": MODEL_NAME,  # <- now correct
            "messages": [
                {"role": "system", "content": "You're a smart, friendly AI assistant who responds clearly."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(API_URL, json=payload, headers=headers)
        data = response.json()
        print("🧠 OpenRouter API response:", data)

        # Fix: OpenRouter returns 'error' wrapper around actual error
        if "error" in data:
            return f"❌ API Error: {data['error']['message']}"

        if "choices" not in data:
            return f"❌ API Error: Unexpected response: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Chatbot Error: {str(e)}"


# ----- MAIN TRANSCRIBE + ACTION HANDLER -----
def transcribe_and_respond(audio_file):
    if audio_file is None:
        return "⚠️ No audio provided."

    result = model.transcribe(audio_file)
    text = result["text"].strip()
    lowered = text.lower()

    # Voice Command Actions
    if "open browser" in lowered or "open chrome" in lowered:
        webbrowser.open("https://google.com")
        return f"🌐 Opening Chrome...\n\n🗣️ Transcript: {text}"
    
    if "open youtube" in lowered:
        webbrowser.open("https://youtube.com")
        return f"📺 Opening YouTube...\n\n🗣️ Transcript: {text}"

    if "open opera" in lowered:
        return f"{open_browser_path('opera')}\n\n🗣️ Transcript: {text}"

    if "open edge" in lowered:
        return f"{open_browser_path('edge')}\n\n🗣️ Transcript: {text}"

    if "weather" in lowered:
        weather = get_weather()
        return f"{weather}\n\n🗣️ Transcript: {text}"

    if "open facebook" in lowered:
        webbrowser.open("https://facebook.com")
        return f"📘 Opening Facebook...\n\n🗣️ Transcript: {text}"
    if "open twitter" in lowered:
        webbrowser.open("https://twitter.com")
        return f"🐦 Opening Twitter...\n\n🗣️ Transcript: {text}"
    if "open instagram" in lowered:
        webbrowser.open("https://instagram.com")
        return f"📸 Opening Instagram...\n\n🗣️ Transcript: {text}"
    if "open whatsapp" in lowered:
        webbrowser.open("https://web.whatsapp.com")
        return f"💬 Opening WhatsApp...\n\n🗣️ Transcript: {text}"
    if "open gmail" in lowered:
        webbrowser.open("https://mail.google.com")
        return f"📧 Opening Gmail...\n\n🗣️ Transcript: {text}"
    if "open google drive" in lowered:
        webbrowser.open("https://drive.google.com")
        return f"📂 Opening Google Drive...\n\n🗣️ Transcript: {text}"
    if "open google docs" in lowered:
        webbrowser.open("https://docs.google.com")
        return f"📄 Opening Google Docs...\n\n🗣️ Transcript: {text}"
    if "open google sheets" in lowered:
        webbrowser.open("https://sheets.google.com")
        return f"📊 Opening Google Sheets...\n\n🗣️ Transcript: {text}"
    if "open google calendar" in lowered:
        webbrowser.open("https://calendar.google.com")
        return f"📅 Opening Google Calendar...\n\n🗣️ Transcript: {text}"
    if "open google maps" in lowered:
        webbrowser.open("https://maps.google.com")
        return f"🗺️ Opening Google Maps...\n\n🗣️ Transcript: {text}"
    if "open linkedin" in lowered:
        webbrowser.open("https://linkedin.com")
        return f"🔗 Opening LinkedIn...\n\n🗣️ Transcript: {text}"
    if "open github" in lowered:
        webbrowser.open("https://github.com")
        return f"🐱 Opening GitHub...\n\n🗣️ Transcript: {text}"
    if "open stack overflow" in lowered:
        webbrowser.open("https://stackoverflow.com")
        return f"💻 Opening Stack Overflow...\n\n🗣️ Transcript: {text}"
    if "open reddit" in lowered:
        webbrowser.open("https://reddit.com")
        return f"👾 Opening Reddit...\n\n🗣️ Transcript: {text}"
    if "open quora" in lowered:
        webbrowser.open("https://quora.com")
        return f"❓ Opening Quora...\n\n🗣️ Transcript: {text}"
    if "open pinterest" in lowered:
        webbrowser.open("https://pinterest.com")
        return f"📌 Opening Pinterest...\n\n🗣️ Transcript: {text}"
    
    if "open netflix" in lowered:
        webbrowser.open("https://netflix.com")
        return f"🎬 Opening Netflix...\n\n🗣️ Transcript: {text}"
    if "open spotify" in lowered:
        webbrowser.open("https://spotify.com")
        return f"🎵 Opening Spotify...\n\n🗣️ Transcript: {text}"
    if "open amazon" in lowered:
        webbrowser.open("https://amazon.com")
        return f"🛒 Opening Amazon...\n\n🗣️ Transcript: {text}"
    #anything else site
    if "open online game" in lowered:
        webbrowser.open("https://poki.com")
        return f"🎮 Opening Poki...\n\n🗣️ Transcript: {text}"
    if "open wikipedia" in lowered:
        webbrowser.open("https://wikipedia.org")
        return f"📚 Opening Wikipedia...\n\n🗣️ Transcript: {text}"
    # Else: use LLM chatbot
    ai_response = query_openrouter(text)
    return f"🗣️ Transcript: {text}\n\n🤖 AI: {ai_response}"

# ----- GRADIO INTERFACE -----
interface = gr.Interface(
    fn=transcribe_and_respond,
    inputs=gr.Audio(type="filepath", label="🎙️ Speak or Upload Audio"),
    outputs=gr.Textbox(label="📋 Response"),
    title="🎤 Whisper + Voice Commands + AI Chat",
    description="Use your voice to give commands (open YouTube, check weather, etc.) or talk to an AI assistant."
)

if __name__ == "__main__":
    interface.launch(share=True)
