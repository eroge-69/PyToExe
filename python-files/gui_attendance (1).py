import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os

def run_face_recognition():
    subprocess.Popen(["python", "face_recognition.py"], shell=True)

def run_gui():
    window = tk.Tk()
    window.title("Smart Attendance System")
    window.geometry("800x600")
    window.configure(bg="white")

    # 🖼️ Try to load full background image
    try:
        bg_img = Image.open("background.jpg")
        bg_img = bg_img.resize((800, 600))
        bg_photo = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        print("✅ Background loaded successfully.")
    except Exception as e:
        print(f"❌ Could not load background image: {e}")

    # 🏫 Title
    title = tk.Label(window, text="Smart Attendance System", font=("Arial", 26, "bold"),
                     fg="black", bg="white")
    title.place(relx=0.5, rely=0.1, anchor="center")

    # 🖼️ Logo
    try:
        logo_img = Image.open("logo.jpeg")
        logo_img = logo_img.resize((120, 120))
        logo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(window, image=logo, bg="white")
        logo_label.image = logo
        logo_label.place(relx=0.5, rely=0.3, anchor="center")
    except Exception as e:
        print("❌ Could not load logo:", e)

    # ▶️ Start Attendance Button
    start_btn = tk.Button(window, text="Start Attendance", command=run_face_recognition,
                          font=("Arial", 16, "bold"), bg="#00FF7F", fg="black", padx=20, pady=10)
    start_btn.place(relx=0.5, rely=0.52, anchor="center")

    # 👣 Footer
    footer = tk.Label(window, text="Made by Shreeyans, Priyag, and Parv",
                      font=("Arial", 10), fg="gray", bg="white")
    footer.place(relx=0.5, rely=0.95, anchor="center")

    window.mainloop()

if __name__ == "__main__":
    run_gui()
