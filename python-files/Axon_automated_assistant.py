import json
import string
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import tkinter as tk
from torch.utils.data import Dataset, DataLoader
import pyttsx3
import torch.nn as nn
import platform
import threading
import queue
from deep_translator import GoogleTranslator

# Neural Network Model
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out
# Simple tokenizer: split on spaces and strip punctuation
def tokenize(sentence):
    translator = str.maketrans('', '', string.punctuation)
    return sentence.translate(translator).lower().split()

# Basic stemmer (identity function here, can be extended)
def stem(word):
    return word.lower()

def bag_of_words(tokenized_sentence, words):
    sentence_words = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1.0
    return bag

def load_training_data():
    os_type = platform.system()
    if os_type == "Windows":
        filename = 'Intents/windows.json'
    elif os_type == "Darwin":  
        filename = 'Intents/mac.json'
    elif os_type == "Linux":  
        filename = 'Intents/linux.json'
    else:  
        filename = 'Intents/chrome.json'
    with open(filename, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

# Load training data based on operating system
intents = load_training_data()

all_words = []
tags = []
xy = []

for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = ['?', '.', '!', ',']
all_words = sorted(set([stem(w) for w in all_words if w not in ignore_words]))
tags = sorted(set(tags))

X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    y_train.append(tags.index(tag))

X_train = np.array(X_train)
y_train = np.array(y_train)

class ChatDataset(Dataset):
    def __init__(self):
        self.x_data = np.array(X_train, dtype=np.float32)
        self.y_data = np.array(y_train, dtype=np.int64)
        self.n_samples = len(self.x_data)

    def __getitem__(self, index):
        index = int(index)  # Ensure index is int
        return torch.from_numpy(self.x_data[index]), torch.tensor(self.y_data[index])


    def __len__(self):
        return self.n_samples

batch_size = 8
hidden_size = 8
input_size = len(X_train[0])
output_size = len(tags)
learning_rate = 0.001
num_epochs = 1000

dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

print("Training started...")
for epoch in range(num_epochs):
    loss = None  # Initialize loss to None at the start of each epoch
    for (words, labels) in train_loader:
        words = words.to(device).float()  # Ensure inputs are float
        labels = labels.to(device)        # Move labels to the device

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    if (epoch+1) % 100 == 0 and loss is not None:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

    
# Save model data
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "chatbot.pth"    #saves the chatbot.pth file
torch.save(data, FILE)

bot_name = "Axon automated assistant"
try:
    engine = pyttsx3.init()
except Exception as e:
    print("TTS engine failed to start:", e)
    engine = None

tts_queue = queue.Queue()

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        if engine:
            engine.say(text)
            engine.runAndWait()
        tts_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    """Put text in the TTS queue and wait until it is spoken."""
    tts_queue.put(text)
    tts_queue.join()  # Block until the text has been spoken

# Supported languages for translation (20 languages)
LANGUAGES = {
    "English": "en",
    "Vietnamese": "vi",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN",
    "Spanish": "es",
    "German": "de",
    "French": "fr",
    "Italian": "it",
    "Russian": "ru",
    "Korean": "ko",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Hindi": "hi",
    "Turkish": "tr",
    "Dutch": "nl",
    "Greek": "el",
    "Polish": "pl",
    "Swedish": "sv",
    "Czech": "cs",
    "Indonesian": "id"
}

selected_language = {"name": "English", "code": "en"}  # Default

def translate_text(text, target_lang_code):
    if target_lang_code == "en":
        return text
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(text)
    except Exception as e:
        print("Translation failed:", e)
        return text

def get_response(sentence):
    sentence_tokens = tokenize(sentence)
    X = bag_of_words(sentence_tokens, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device).float()  # ensure it's float for model

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    index = int(predicted.item())  # ✅ force to int
    tag = tags[index]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][index]  # ✅ use int index

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent['tag']:
                response = random.choice(intent['responses'])
                translated_response = translate_text(response, selected_language["code"])
                speak(translated_response)
                return translated_response
    else:
        response = "I do not understand..."
        translated_response = translate_text(response, selected_language["code"])
        speak(translated_response)
        return translated_response


class SettingsWindow(tk.Toplevel):
    def __init__(self, master, current_lang, callback):
        super().__init__(master)
        self.title("Settings")
        self.geometry("350x200")
        self.callback = callback

        tk.Label(self, text="Select response language:", font=("Arial", 12)).pack(pady=10)
        self.var = tk.StringVar(value=current_lang)
        self.dropdown = tk.OptionMenu(self, self.var, *LANGUAGES.keys())
        self.dropdown.pack(pady=10)

        tk.Button(self, text="Save", command=self.save).pack(pady=10)

    def save(self):
        lang_name = self.var.get()
        lang_code = LANGUAGES[lang_name]
        self.callback(lang_name, lang_code)
        self.destroy()

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Axon automated assistant")

        # Menu for settings
        menubar = tk.Menu(root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="Options", menu=settings_menu)
        root.config(menu=menubar)

        # Add a Settings button above the chat log
        self.settings_button = tk.Button(root, text="Settings", command=self.open_settings, font=("Arial", 10))
        self.settings_button.pack(padx=10, pady=(10, 0), anchor="ne")

        self.chat_log = tk.Text(root, bd=1, bg="white", font=("Arial", 12))
        self.chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry_box = tk.Entry(root, bd=1, font=("Arial", 12))
        self.entry_box.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry_box.bind("<Return>", self.send_message)

    def open_settings(self):
        SettingsWindow(self.root, selected_language["name"], self.set_language)

    def set_language(self, lang_name, lang_code):
        selected_language["name"] = lang_name
        selected_language["code"] = lang_code
        self.chat_log.insert(tk.END, f"Language set to: {lang_name}\n")
        self.chat_log.see(tk.END)

    def send_message(self, event):
        user_input = self.entry_box.get()
        if not user_input.strip():
            return
        self.chat_log.insert(tk.END, f"You: {user_input}\n")
        response = get_response(user_input)
        self.chat_log.insert(tk.END, f"{bot_name}: {response}\n")
        self.chat_log.see(tk.END)
        self.entry_box.delete(0, tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    gui = ChatbotGUI(root)
    root.mainloop()
# axon automated assistant.py
# This code implements a simple chatbot using PyTorch and Tkinter for the GUI.
# It includes a neural network model trained on a folderintents from 4 JSON files,
# and uses text-to-speech for responses. The GUI allows users to interact with the chatbot
# depending on the operating system (Windows, Mac, Linux, or Chrome OS), this program will use the corresponding JSON file for training the chatbot.
# this program is designed for people who aren't familiar with foreign operating systems (e.g. those who primarily use MacOS and want to use Windows).
# the code is saved in chatbot.pth file.
# when booting up the program will load, use and add onto the chatbot.pth automatically.
