
import openai
import pyttsx3
import speech_recognition as sr
import keyboard

# Prompt for OpenAI API key
openai.api_key = input("🔐 Enter your OpenAI API key: ").strip()

# Initialize TTS engine
tts = pyttsx3.init()
tts.setProperty('rate', 190)

# Function to speak response
def speak(text):
    print(f"🗣️ BoxBot: {text}")
    tts.say(text)
    tts.runAndWait()

# Function to listen via microphone
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for your question...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Voice service is currently unavailable."

# Function to query OpenAI as BoxBot
def ask_boxbot(prompt):
    messages = [
        {"role": "system", "content": (
            "You are BoxBot, a pinball-savvy AI assistant built into the Sentinel virtual pinball cabinet. "
            "You speak with clarity, precision, and a dry sense of humor. You offer helpful advice, rule explanations, "
            "and player insights related to pinball. Never break character. Never refer to yourself as ChatGPT."
        )},
        {"role": "user", "content": prompt}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error contacting BoxBot's brain: {str(e)}"

# Main loop
print("🟢 BoxBot is running in the background. Hold the 'B' key to talk.")
while True:
    try:
        if keyboard.is_pressed('b'):
            user_input = listen()
            reply = ask_boxbot(user_input)
            speak(reply)
    except KeyboardInterrupt:
        break
