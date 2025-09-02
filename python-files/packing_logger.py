import tkinter as tk
from tkinter import messagebox
import csv
import datetime
import speech_recognition as sr

def capture_voice_note():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Please speak your note...")
        audio = recognizer.listen(source)
        try:
            note = recognizer.recognize_google(audio)
            print("📝 Voice Note Captured:", note)
            return note
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            return "Unrecognized speech"
        except sr.RequestError as e:
            print(f"⚠️ Speech recognition error: {e}")
            return "Speech recognition error"

def log_data():
    barcode = barcode_entry.get().strip()
    operator = operator_entry.get().strip()
    if not barcode or not operator:
        messagebox.showwarning("Input Error", "Please enter both barcode and operator name.")
        return

    voice_note = capture_voice_note()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("packing_activity_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([barcode, voice_note, timestamp, operator, "No"])

    messagebox.showinfo("Success", "Data logged successfully.")
    barcode_entry.delete(0, tk.END)

# GUI setup
app = tk.Tk()
app.title("Packing Activity Logger")
app.geometry("400x250")

tk.Label(app, text="Operator Name:").pack(pady=5)
operator_entry = tk.Entry(app, width=40)
operator_entry.pack(pady=5)

tk.Label(app, text="Scan Barcode:").pack(pady=5)
barcode_entry = tk.Entry(app, width=40)
barcode_entry.pack(pady=5)

log_button = tk.Button(app, text="Log Packing Activity", command=log_data)
log_button.pack(pady=20)

app.mainloop()