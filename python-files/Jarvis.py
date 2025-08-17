import speech_recognition as sr
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import datetime
import webbrowser
import os
import pygame
import asyncio
from edge_tts import Communicate
import time
import uuid
import urllib.parse
from pytube import Search
import wikipedia
import pyautogui
import subprocess
import psutil

# Initialize NLTK and other components
nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# Enhanced intents dictionary with new 'typing' intent
intents = {
    "greeting": ["hello", "hi", "hey", "greetings", "good morning", "Ram Ram bhai","ram ram", "namaste"],
    "time": ["what time is it", "tell me the time", "current time", "time now"],
    "open_google": ["open google", "launch google", "go to google"],
    "search_google": ["search on google", "google search", "look up on google","google pe"],
    "search_wikipedia": ["wikipedia", "search wikipedia", "tell me about", "what is", "who is","explain","ka matlab"],
    "play_song": ["play", "play song", "play music", "play a song", "play the song", "on youtube", "want to listen", "gana chalade"],
    "exit": ["bye", "exit", "quit", "goodbye", "see you later", "sleep", "talk to you later"],
    "wake": ["jarvis", "wake up", "hey jarvis", "hello jarvis", "uth ja", "uthja"],
    "abuse": ["bhosdi ke", "bahan ke load", "bahan ke lode", "bhenchod", "teri maa ki chut", "teri maa ka bhosda","madharchod"],
    "close_window": ["close window", "close this window", "shut window", "minimize window"],
    "open_app": ["open", "launch", "start", "run", "open app", "open the", "open application"],
    "start_typing": ["start typing", "begin typing", "jarvis type", "type for me", "take dictation"],
    "exit_typing": ["exit typing", "stop typing", "end typing", "finish typing"],
    "new_line": ["enter next line", "new line", "next line", "change line"],
    "select_all":["select all","select kro","select kr", "sab kuchh select kro"],
    "copy_all":["copy all","copy","copy kr","copy kro"],
    "paste_all":["paste all","paste","paste kr","paste kro"],
    "erase":["erase","mitade","mita de"]
}

# Enhanced responses dictionary with typing functionality
responses = {
    "greeting": "Hello! How can I assist you?",
    "time": lambda: f"The time is {datetime.datetime.now().strftime('%H:%M')}",
    "open_google": lambda: webbrowser.open("https://www.google.com") or "Opening Google",
    "search_google": lambda query: webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}") or f"Searching Google for {query}",
    "search_wikipedia": lambda query: search_wikipedia(query),
    "play_song": lambda song: play_youtube_song(song),
    "exit": "Goodbye!",
    "wake": "I'm awake now. How can I help you?",
    "abuse": "Sorry, I can't answer the abusing text",
    "close_window": lambda query=None: pyautogui.hotkey('alt', 'f4') or "current window closed",
    "open_app": lambda app_name: open_application(app_name),
    "start_typing": lambda: "typing_mode",  # Special response to trigger typing mode
    "exit_typing": lambda: "exiting typing mode",
    "new_line": lambda: pyautogui.press('enter') or "Moving to next line",
    "select_all": lambda: (pyautogui.hotkey('ctrl', 'a')),
    "copy_all": lambda: (pyautogui.hotkey('ctrl', 'c')),
    "paste_all": lambda: (pyautogui.hotkey('ctrl', 'v')),
    "erase": lambda: (pyautogui.press('backspace'))
}

# Dictionary mapping app names to their executable paths
app_paths = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "paint": "mspaint.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "photoshop": "photoshop.exe",
    "visual studio code": "code.exe",
    "outlook": "outlook.exe",
    "teams": "teams.exe",
    "discord": "discord.exe",
    "zoom": "zoom.exe",
    "WhatsApp":"WhatsApp.exe",
    "Forza Horizon 5":"D:\\Forza Horizon 5\ForzaHorizon5.exe"
}

async def typing_mode():
    """Function to handle the typing mode where Jarvis types what you say"""
    await speak("I'm now in typing mode. Say 'exit typing' when you're done.")
    
    while True:
        query = listen()
        
        if not query:
            continue
            
        intent = predict_class(query)
        
        if intent == "exit_typing":
            await speak("Exiting typing mode.")
            return
        elif intent == "new_line":
            pyautogui.press('enter')
            continue
        elif intent == "select_all":
            pyautogui.hotkey('ctrl', 'a')
            await speak("Selected all text")
            continue
        elif intent == "copy_all":
            pyautogui.hotkey('ctrl', 'c')
            await speak("Copied to clipboard")
            continue
        elif intent == "erase":
            pyautogui.press('backspace')
            continue
        else:
            # Type out whatever was said (except commands)
            pyautogui.write(query + " ", interval=0.05)

def open_application(app_name):
    """Function to open an application based on the app name"""
    app_name = app_name.replace("open", "").strip().lower()
    
    for known_app in app_paths:
        if known_app in app_name:
            try:
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'].lower() == app_paths[known_app].lower():
                        return f"{known_app} is already running"
                
                subprocess.Popen(app_paths[known_app])
                return f"Opening {known_app}"
            except Exception as e:
                return f"Sorry, I couldn't open {known_app}. Error: {str(e)}"
    
    try:
        subprocess.Popen(app_name)
        return f"Attempting to open {app_name}"
    except Exception as e:
        return f"Sorry, I couldn't open {app_name}. Please be more specific about the application name."

words = []
classes = []
documents = []

for intent, patterns in intents.items():
    for pattern in patterns:
        tokens = nltk.word_tokenize(pattern)
        words.extend(tokens)
        documents.append((tokens, intent))
        if intent not in classes:
            classes.append(intent)

words = [lemmatizer.lemmatize(w.lower()) for w in words if w.isalpha()]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

# Prepare training data
training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = [lemmatizer.lemmatize(w.lower()) for w in doc[0]]
    for w in words:
        bag.append(1 if w in pattern_words else 0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

training = np.array(training, dtype=object)
train_x = np.array(list(training[:, 0]))
train_y = np.array(list(training[:, 1]))

# Build and train the model
model = Sequential()
model.add(Dense(16, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(len(train_y[0]), activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(train_x, train_y, epochs=200, verbose=0)

async def speak(text):
    filename = f"response_{uuid.uuid4().hex}.mp3"
    print("JARVIS:", text)
    
    communicate = Communicate(text, voice="en-GB-RyanNeural")
    await communicate.save(filename)
    
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Error deleting audio file: {e}")
    
    time.sleep(0.5)

# In your play_youtube_song function (replace the existing one)
def play_youtube_song(song_name):
    if not song_name:
        return "Please specify a song name."
    
    try:
        speak(f"Searching for {song_name}...")
        
        search = Search(song_name)
        if not search.results:  # Check if results are empty
            return f"No results found for {song_name}"
            
        video_url = f"https://youtube.com/watch?v={search.results[0].video_id}"
        webbrowser.open(video_url)
        return f"Now playing: {search.results[0].title}"
    except Exception as e:
        return f"Error playing song: {str(e)}"

# In your training data preparation (add validation)
if len(training) == 0:
    raise ValueError("No training data! Check your intents patterns.")
train_x = np.array(list(training[:, 0])) if len(training) > 0 else np.array([])
train_y = np.array(list(training[:, 1])) if len(training) > 0 else np.array([])

def search_wikipedia(query):
    try:
        # Remove trigger words from the query
        for trigger in ["wikipedia", "search wikipedia", "tell me about", "what is", "who is"]:
            if trigger in query.lower():
                query = query.lower().replace(trigger, "").strip()
                break
        
        if not query:
            return "Please specify what you want to know."
        
        # Set language to English (you can change this)
        wikipedia.set_lang("en")
        
        # Get a summary of the topic
        summary = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"There are multiple options. Please be more specific. Some options are: {', '.join(e.options[:3])}"
    except wikipedia.exceptions.PageError:
        return "I couldn't find information about that on Wikipedia."
    except Exception as e:
        return f"Sorry, I encountered an error while searching Wikipedia: {str(e)}"

def bag_of_words(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    bag = [1 if w in sentence_words else 0 for w in words]
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    index = np.argmax(res)
    print(f"Predicted intent: {classes[index]}, Confidence: {res[index]:.2f}")
    return classes[index]

def listen(timeout=5, phrase_time_limit=None):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            query = r.recognize_google(audio)
            print(f"You said: {query}")
            return query.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Error in listening: {e}")
            return ""

async def sleep_mode():
    print("* Jarvis is in sleep mode *")
    last_activity_time = time.time()
    
    while True:
        query = listen(timeout=5)
        
        if query is None:
            continue
            
        if query:
            intent = predict_class(query)
            if intent == "wake":
                await speak(responses[intent])
                return True
            elif intent == "exit":
                await speak(responses[intent])
                return False
                
        if time.time() - last_activity_time > 30:
            last_activity_time = time.time()

async def jarvis():
    await speak("Welcome back sir!")
    last_activity_time = time.time()
    
    while True:
        if time.time() - last_activity_time > 30:
            should_continue = await sleep_mode()
            if not should_continue:
                break
            last_activity_time = time.time()
            continue
            
        query = listen()
        
        if query is None:
            continue
            
        if query:
            last_activity_time = time.time()
            try:
                intent = predict_class(query)
                
                # Handle typing mode separately
                if intent == "start_typing":
                    await typing_mode()
                    continue
                
                if intent == "play_song":
                    song_name = query.replace("play", "").strip()
                    if song_name:
                        await speak(f"Playing {song_name} on YouTube.")
                        play_youtube_song(song_name)
                    else:
                        await speak("Please specify a song name.")
                    continue
                
                elif intent == "search_wikipedia":
                    await speak(responses[intent](query))
                    continue
                
                elif intent in ["search_google", "close_window", "open_app", "new_line", "select_all", "copy_all", "erase"]:
                    if intent in ["close_window", "new_line", "select_all", "copy_all", "erase"]:
                        response = responses[intent]()  # Call without arguments
                    else:
                        response = responses[intent](query)  # Call with query argument
                    if response:
                        await speak(response)
                    continue
                
                response = responses[intent]
                if callable(response):
                    result = response()
                    if result:
                        await speak(result)
                else:
                    await speak(response)
                
                if intent == "exit":
                    break
            except Exception as e:
                await speak(f"Sorry, I encountered an error: {str(e)}")
                continue

if __name__ == "__main__":
    pygame.init()
    asyncio.run(jarvis())
    pygame.quit()