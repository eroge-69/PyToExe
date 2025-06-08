import pyttsx3
import os
import datetime
import socket
import wikipedia
import webbrowser
import smtplib
from email.message import EmailMessage
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import speech_recognition as sr  # For voice input

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def get_ip_address():
    return socket.gethostbyname(socket.gethostname())

def play_song_on_youtube(song_name):
    search_query = '+'.join(song_name.split())
    url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(url)
    speak(f"Playing {song_name} on YouTube.")

def send_email(subject, body, to_email):
    email_address = 'your_email@example.com'
    email_password = 'your_password'
    
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to_email

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
            speak(f"Email sent to {to_email}.")
    except Exception as e:
        speak("Sorry, I couldn't send the email.")

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            command = recognizer.recognize_google(audio, language='en-US')
            speak(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            speak("Speech service is unavailable.")
        except sr.WaitTimeoutError:
            speak("Listening timed out.")
    return ""

def process_command(command):
    command = command.lower()

    if 'what is your developer name ' in command:
        return "My developer name is Zain Javed."

    elif 'date' in command or 'time' in command:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"The current date and time is {now}"

    elif 'play song' in command:
        song_name = simpledialog.askstring("Input", "Enter the song name:")
        if song_name:
            play_song_on_youtube(song_name)
            return f"Playing {song_name} on YouTube."
        return "No song name provided."

    elif 'ip address' in command:
        ip_address = get_ip_address()
        return f"Your IP address is {ip_address}"

    elif 'search wikipedia' in command:
        search_query = simpledialog.askstring("Input", "Enter the Wikipedia search query:")
        if search_query:
            try:
                results = wikipedia.summary(search_query, sentences=2)
                return f"According to Wikipedia: {results}"
            except wikipedia.exceptions.PageError:
                return "Sorry, no page found."
            except wikipedia.exceptions.DisambiguationError:
                return "Search query is ambiguous."
        return "No query provided."

    elif 'open youtube' in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    elif 'open stack overflow' in command:
        webbrowser.open("https://stackoverflow.com")
        return "Opening Stack Overflow."

    elif 'send message to whatsapp' in command:
        number = simpledialog.askstring("Input", "Enter the phone number with country code:")
        message = simpledialog.askstring("Input", "Enter the message:")
        if number and message:
            webbrowser.open(f"https://web.whatsapp.com/send?phone={number}&text={message}")
            return f"Sending WhatsApp message to {number}."
        return "Incomplete WhatsApp info."

    elif 'send email' in command:
        subject = simpledialog.askstring("Input", "Enter the email subject:")
        body = simpledialog.askstring("Input", "Enter the email body:")
        to_email = simpledialog.askstring("Input", "Enter the recipient email:")
        if subject and body and to_email:
            send_email(subject, body, to_email)
            return f"Sending email to {to_email}."
        return "Incomplete email details."

    elif 'open google chrome' in command:
        chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        os.startfile(chrome_path)
        return "Opening Google Chrome."

    elif 'open camera' in command:
        os.system('start microsoft.windows.camera:')
        return "Opening Camera."

    elif 'open command prompt' in command or 'open cmd' in command:
        os.system('start cmd')
        return "Opening Command Prompt."

    elif 'exit' in command or 'stop' in command:
        speak("Goodbye!")
        window.quit()
        return "Goodbye!"

    return "Sorry, I didn't understand that command."

# --- GUI Setup ---
window = tk.Tk()
window.title("JERVIS - Professional Assistant")
window.geometry("360x640")
window.configure(bg="#121212")
window.resizable(False, False)

title_label = tk.Label(window, text="J A R V I S", font=("Helvetica", 24, "bold"),
                       fg="#00bcd4", bg="#121212", pady=10)
title_label.pack()

chat_window = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED,
                                        bg="#1e1e1e", fg="white", font=("Consolas", 10), bd=2)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

input_box = tk.Entry(window, font=("Helvetica", 12), bg="#2c2c2c", fg="white", insertbackground="white", relief=tk.FLAT)
input_box.pack(padx=10, pady=(0, 10), ipady=8, fill=tk.X)

def handle_user_input():
    user_input = input_box.get().strip()
    if user_input:
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"You: {user_input}\n")
        response = process_command(user_input)
        chat_window.insert(tk.END, f"Jervis: {response}\n\n")
        chat_window.config(state=tk.DISABLED)
        input_box.delete(0, tk.END)
        speak(response)

def handle_voice_input():
    command = take_command()
    if command:
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"You (voice): {command}\n")
        response = process_command(command)
        chat_window.insert(tk.END, f"Jervis: {response}\n\n")
        chat_window.config(state=tk.DISABLED)
        speak(response)

# Button setup
button_frame = tk.Frame(window, bg="#121212")
button_frame.pack(pady=10)

send_button = tk.Button(button_frame, text="Send", font=("Helvetica", 10, "bold"),
                        bg="#00bcd4", fg="white", width=10, command=handle_user_input)
send_button.grid(row=0, column=0, padx=10)

speak_button = tk.Button(button_frame, text="Speak", font=("Helvetica", 10),
                         bg="#2c2c2c", fg="white", width=10, command=handle_voice_input)
speak_button.grid(row=0, column=1, padx=10)

window.mainloop()
