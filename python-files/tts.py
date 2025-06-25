import pyttsx3
import tkinter as tk
from tkinter import messagebox

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Function to speak the text
def speak_text():
    text = text_input.get("1.0", "end-1c")
    if not text.strip():  # Check if the input is empty
        messagebox.showwarning("Input Error", "Please enter some text to read.")
        return

    # Set voice properties
    engine.setProperty('rate', rate_slider.get())  # Set speech rate
    engine.setProperty('volume', volume_slider.get())  # Set volume

    # Get selected voice
    selected_voice = voice_var.get()
    voices = engine.getProperty('voices')
    if selected_voice == 'Male':
        engine.setProperty('voice', voices[0].id)  # Male voice (first voice in list)
    else:
        engine.setProperty('voice', voices[1].id)  # Female voice (second voice in list)
    
    # Speak the text
    engine.say(text)
    engine.runAndWait()

# Function to stop speech
def stop_speech():
    engine.stop()

# Create the main window
root = tk.Tk()
root.title("Text-to-Speech Application")

# Set the window size
root.geometry("400x400")

# Text input box
text_input_label = tk.Label(root, text="Enter Text:")
text_input_label.pack(pady=5)

text_input = tk.Text(root, height=10, width=40)
text_input.pack(pady=5)

# Voice selection (Male/Female)
voice_var = tk.StringVar()
voice_var.set('Male')  # Default voice is Male

voice_label = tk.Label(root, text="Select Voice:")
voice_label.pack(pady=5)

male_radio = tk.Radiobutton(root, text="Male", variable=voice_var, value="Male")
male_radio.pack()

female_radio = tk.Radiobutton(root, text="Female", variable=voice_var, value="Female")
female_radio.pack()

# Speech rate control
rate_label = tk.Label(root, text="Speech Rate:")
rate_label.pack(pady=5)

rate_slider = tk.Scale(root, from_=50, to=200, orient="horizontal")
rate_slider.set(150)  # Default rate
rate_slider.pack()

# Volume control
volume_label = tk.Label(root, text="Volume:")
volume_label.pack(pady=5)

volume_slider = tk.Scale(root, from_=0, to=1, orient="horizontal", resolution=0.1)
volume_slider.set(1)  # Default volume
volume_slider.pack()

# Control Buttons
speak_button = tk.Button(root, text="Speak", command=speak_text)
speak_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop", command=stop_speech)
stop_button.pack(pady=5)

# Run the application
root.mainloop()

