
import cv2
import face_recognition
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import sqlite3
import io
import pickle
import os

# ============================ DATABASE SETUP ============================
DB_PATH = "faces.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS faces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        encoding BLOB
                    )""")
    conn.commit()
    conn.close()

def save_face_to_db(name, encoding):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (name, pickle.dumps(encoding)))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Name '{name}' already exists!")
    conn.close()

def load_faces_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, encoding FROM faces")
    rows = cursor.fetchall()
    conn.close()
    known_encodings = [pickle.loads(row[1]) for row in rows]
    known_names = [row[0] for row in rows]
    return known_encodings, known_names

def delete_face_from_db(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faces WHERE name=?", (name,))
    conn.commit()
    conn.close()

# ============================ GUI SETUP ============================
root = tk.Tk()
root.title("Advanced Face Recognition System 🧠")
root.geometry("900x700")
root.configure(bg="#121212")

video_label = tk.Label(root, bg="#121212")
video_label.pack(padx=10, pady=10)

status_label = tk.Label(root, text="Status: Idle", fg="white", bg="#121212", font=("Arial", 14))
status_label.pack()

cap = None
running = False

# ============================ CORE FUNCTIONS ============================
def register_face():
    global cap
    cap = cv2.VideoCapture(0)
    status_label.config(text="Status: Registering face... Look at the camera.")

    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Cannot access camera.")
        cap.release()
        return

    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if len(face_encodings) == 0:
        messagebox.showwarning("No Face", "No face detected. Try again.")
        cap.release()
        return

    name = simpledialog.askstring("Register Face", "Enter your name:")
    if not name:
        messagebox.showinfo("Cancelled", "Registration cancelled.")
        cap.release()
        return

    save_face_to_db(name, face_encodings[0])
    messagebox.showinfo("Success", f"Face registered for {name}.")
    status_label.config(text=f"Status: Face registered for {name}.")
    cap.release()

def recognize_faces_webcam():
    global cap, running
    known_encodings, known_names = load_faces_from_db()

    if len(known_encodings) == 0:
        messagebox.showwarning("No Data", "No registered faces found.")
        return

    cap = cv2.VideoCapture(0)
    running = True
    status_label.config(text="Status: Recognizing faces via webcam...")

    def update_frame():
        global running
        if not running:
            return
        ret, frame = cap.read()
        if not ret:
            return

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left + 6, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
        video_label.after(10, update_frame)

    update_frame()

def recognize_faces_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    known_encodings, known_names = load_faces_from_db()

    if len(known_encodings) == 0:
        messagebox.showwarning("No Data", "No registered faces found.")
        return

    image = face_recognition.load_image_file(file_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(img_bgr, (left, top), (right, bottom), color, 2)
        cv2.putText(img_bgr, name, (left + 6, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Recognition Result", img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def delete_face():
    name = simpledialog.askstring("Delete Face", "Enter the name to delete:")
    if not name:
        return
    delete_face_from_db(name)
    messagebox.showinfo("Deleted", f"Face data for '{name}' removed successfully.")
    status_label.config(text=f"Status: Face '{name}' deleted.")

def stop_camera():
    global cap, running
    running = False
    if cap:
        cap.release()
    video_label.config(image='')
    status_label.config(text="Status: Camera stopped.")

def exit_app():
    stop_camera()
    root.destroy()

# ============================ BUTTONS ============================
button_frame = tk.Frame(root, bg="#121212")
button_frame.pack(pady=10)

btn_style = {"bg": "#1f1f1f", "fg": "white", "font": ("Arial", 12), "width": 18, "relief": "flat"}

tk.Button(button_frame, text="Register Face", command=register_face, **btn_style).grid(row=0, column=0, padx=8, pady=5)
tk.Button(button_frame, text="Recognize (Webcam)", command=recognize_faces_webcam, **btn_style).grid(row=0, column=1, padx=8, pady=5)
tk.Button(button_frame, text="Recognize (Image)", command=recognize_faces_image, **btn_style).grid(row=0, column=2, padx=8, pady=5)
tk.Button(button_frame, text="Delete Face", command=delete_face, **btn_style).grid(row=1, column=0, padx=8, pady=5)
tk.Button(button_frame, text="Stop Camera", command=stop_camera, **btn_style).grid(row=1, column=1, padx=8, pady=5)
tk.Button(button_frame, text="Exit", command=exit_app, **btn_style).grid(row=1, column=2, padx=8, pady=5)

init_db()
root.mainloop()
