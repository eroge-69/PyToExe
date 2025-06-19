import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import threading
import time


menu = {
    "Smokey Dill": "Mesquite Barbeque and Dill Sauce ",
    "Smokey Jerk": "Mesquite Barbeque and Caribbean jerk",
    "Smokey Ranch": "Mesquite Barbeque and ranch",
    "fries": "Potato sticks deep fried with salt",
    "chicken nugget": "Crispy chicken pieces with batter",
    "cola": "Carbonated water with flavor and sugar"
}


engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def typewriter_effect(label, text):
    label.configure(text="")
    for char in text:
        label.configure(text=label.cget("text") + char)
        label.update()
        time.sleep(0.04)


def listen_and_respond(display_label, animation_label):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        animation_label.configure(text="🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            animation_label.configure(text="")

            result = f"You said: {command}"
            typewriter_effect(display_label, result)

            response = menu.get(command, "I don't recognize that item.")
            time.sleep(0.5)
            typewriter_effect(display_label, f"\n\nIngredients: {response}")
            speak(response)

        except sr.UnknownValueError:
            animation_label.configure(text="")
            typewriter_effect(display_label, "Could not understand.")
            speak("Sorry, I didn't catch that.")

        except sr.RequestError:
            animation_label.configure(text="")
            typewriter_effect(display_label, "Speech service unavailable.")
            speak("Speech service is unavailable.")

        except Exception as e:
            animation_label.configure(text="")
            typewriter_effect(display_label, f"Error: {str(e)}")
            speak("An error occurred.")


app = ctk.CTk()
app.geometry("900x600")
app.title("WingHouse - Kitchen Assistant")
ctk.set_appearance_mode("dark")

bg_image = ctk.CTkImage(Image.open("assets/Background/Background.png"), size=(900, 600))
bg_label = ctk.CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0)


glass_frame = ctk.CTkFrame(app, width=520, height=400, corner_radius=20, fg_color=("#1f1f1f", "#1f1f1f"), border_width=1, border_color="#444")
glass_frame.place(x=40, y=130)


display_label = ctk.CTkLabel(glass_frame, text="", anchor="nw", justify="left", font=("Segoe UI", 16), width=500, height=350, text_color="white")
display_label.place(x=10, y=10)

animation_label = ctk.CTkLabel(app, text="", font=("Segoe UI", 18), text_color="white")
animation_label.place(x=40, y=550)


root_tk = app._w
mic_img_raw = Image.open("assets/Buttons/mic2.png").resize((360, 450))
mic_img_tk = ImageTk.PhotoImage(mic_img_raw)

mic_button_tk = tk.Button(
    app,
    image=mic_img_tk,
    command=lambda: threading.Thread(target=listen_and_respond, args=(display_label, animation_label), daemon=True).start(),
    borderwidth=0,
    highlightthickness=0,
    bg="#231C1C",
    activebackground="#231C1C"
)
mic_button_tk.place(x=972, y=424) 
app.mainloop() 