import tkinter as tk
from tkinter import *
import os
from PIL import ImageTk, Image
import datetime
import time
import pyttsx3
import threading
import schedule

# Project modules
import takeImage
import trainImage
import automaticAttendance
import show_attendance

# TTS Function
def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()

# Paths
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimage_path = "./TrainingImage"
studentdetail_path = "./StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

# Ensure necessary directories
os.makedirs(trainimage_path, exist_ok=True)
os.makedirs("UI_Image", exist_ok=True)
os.makedirs("StudentDetails", exist_ok=True)

# Main Window
window = Tk()
window.title("Face Recognizer")
window.geometry("1280x720")
window.configure(background="#1c1c1c")

# Error popup
def err_screen():
    sc1 = tk.Toplevel()
    sc1.geometry("400x110")
    sc1.title("Warning!!")
    sc1.configure(background="#1c1c1c")
    sc1.resizable(0, 0)
    tk.Label(sc1, text="All Fields Required!", fg="yellow", bg="#1c1c1c", font=("Verdana", 16, "bold")).pack(pady=10)
    tk.Button(sc1, text="OK", command=sc1.destroy, fg="yellow", bg="#333333", font=("Verdana", 14, "bold")).pack(pady=5)

# Header
try:
    logo = Image.open("UI_Image/0001.png").resize((50, 47))
    logo1 = ImageTk.PhotoImage(logo)
    tk.Label(window, image=logo1, bg="#1c1c1c").place(x=470, y=10)
except:
    pass

tk.Label(window, text="CLASS VISION", bg="#1c1c1c", fg="yellow", font=("Verdana", 27, "bold")).place(x=525, y=12)
tk.Label(window, text="Welcome to CLASS VISION", bg="#1c1c1c", fg="yellow", font=("Verdana", 35, "bold")).pack(pady=70)

# Icons
try:
    img1 = ImageTk.PhotoImage(Image.open("UI_Image/register.png"))
    img2 = ImageTk.PhotoImage(Image.open("UI_Image/attendance.png"))
    img3 = ImageTk.PhotoImage(Image.open("UI_Image/verifyy.png"))
    Label(window, image=img1).place(x=100, y=270)
    Label(window, image=img3).place(x=600, y=270)
    Label(window, image=img2).place(x=980, y=270)
except:
    pass

# Register Student Form
def TakeImageUI():
    ImageUI = Toplevel(window)
    ImageUI.title("Take Student Image")
    ImageUI.geometry("850x580")
    ImageUI.configure(background="#1c1c1c")
    ImageUI.resizable(0, 0)

    tk.Label(ImageUI, text="Register New Student", bg="#1c1c1c", fg="green", font=("Verdana", 30, "bold")).pack(pady=10)

    labels = ["Register No", "Category", "DOB", "Roll No", "Student Name", "Mother Name"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(ImageUI, text=label, bg="#1c1c1c", fg="yellow", font=("Verdana", 14, "bold")).place(x=100, y=80 + i*60)
        entry = tk.Entry(ImageUI, width=25, bg="#333333", fg="yellow", font=("Verdana", 16))
        entry.place(x=280, y=80 + i*60)
        entries.append(entry)

    tk.Label(ImageUI, text="Notification", bg="#1c1c1c", fg="yellow", font=("Verdana", 14)).place(x=100, y=440)
    message = tk.Label(ImageUI, text="", width=40, height=2, bg="#333333", fg="yellow", font=("Verdana", 12, "bold"))
    message.place(x=280, y=440)

def TakeImageUI():
    ImageUI = Toplevel(window)
    ImageUI.title("Register New Student")
    ImageUI.geometry("850x580")
    ImageUI.configure(background="#1c1c1c")
    ImageUI.resizable(0, 0)

    tk.Label(ImageUI, text="Register New Student", bg="#1c1c1c", fg="green", font=("Verdana", 30, "bold")).pack(pady=10)

    labels = ["Register No", "Category", "DOB (DD/MM/YYYY)", "Roll No", "Student Name", "Mother Name"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(ImageUI, text=label, bg="#1c1c1c", fg="yellow", font=("Verdana", 14, "bold")).place(x=100, y=80 + i*60)
        entry = tk.Entry(ImageUI, width=25, bg="#333333", fg="yellow", font=("Verdana", 16))
        entry.place(x=350, y=80 + i*60)
        entries.append(entry)

    tk.Label(ImageUI, text="Notification", bg="#1c1c1c", fg="yellow", font=("Verdana", 14)).place(x=100, y=440)
    message = tk.Label(ImageUI, text="", width=40, height=2, bg="#333333", fg="yellow", font=("Verdana", 12, "bold"))
    message.place(x=280, y=440)

    def take_image():
        reg_no = entries[0].get().strip()
        category = entries[1].get().strip()
        dob = entries[2].get().strip()
        roll_no = entries[3].get().strip()
        name = entries[4].get().strip()
        mother_name = entries[5].get().strip()

        if not all([reg_no, category, dob, roll_no, name, mother_name]):
            err_screen()
            return

        takeImage.TakeImage(
            reg_no, category, dob, roll_no, name, mother_name,
            haarcasecade_path, trainimage_path,
            message, err_screen, text_to_speech
        )

        for entry in entries:
            entry.delete(0, "end")

    def train_image():
        trainImage.TrainImage(haarcasecade_path, trainimage_path)

    tk.Button(ImageUI, text="Take Image", command=take_image, bg="#333333", fg="yellow", font=("Verdana", 16), width=15).place(x=200, y=500)
    tk.Button(ImageUI, text="Train Image", command=train_image, bg="#333333", fg="yellow", font=("Verdana", 16), width=15).place(x=450, y=500)

# Buttons
tk.Button(window, text="Register a new student", command=TakeImageUI, bd=10, font=("Verdana", 16), bg="black", fg="yellow", height=2, width=17).place(x=100, y=520)
tk.Button(window, text="Take Attendance", command=lambda: automaticAttendance.subjectChoose(text_to_speech), bd=10, font=("Verdana", 16), bg="black", fg="yellow", height=2, width=17).place(x=600, y=520)
tk.Button(window, text="View Attendance", command=lambda: show_attendance.subjectchoose(text_to_speech), bd=10, font=("Verdana", 16), bg="black", fg="yellow", height=2, width=17).place(x=1000, y=520)
tk.Button(window, text="EXIT", command=window.destroy, bd=10, font=("Verdana", 16), bg="black", fg="yellow", height=2, width=17).place(x=600, y=660)

# Auto Schedule Attendance
def auto_attendance_mf():
    automaticAttendance.subjectChoose(text_to_speech)

schedule.every().monday.at("11:00").do(auto_attendance_mf)
schedule.every().tuesday.at("11:00").do(auto_attendance_mf)
schedule.every().wednesday.at("11:00").do(auto_attendance_mf)
schedule.every().thursday.at("11:00").do(auto_attendance_mf)
schedule.every().friday.at("11:00").do(auto_attendance_mf)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(30)

threading.Thread(target=run_schedule, daemon=True).start()

window.mainloop()
