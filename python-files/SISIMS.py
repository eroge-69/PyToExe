import cv2
import numpy as np
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import datetime

# Database setup
db_path = os.path.join(os.getcwd(), "student_data.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    data TEXT,
    timestamp TEXT
)
""")
conn.commit()

# Tkinter Window Setup
root = tk.Tk()
root.title("Student Entry QR Code Scanner")
root.geometry("800x600")

# Create Table with Scrollbar
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree = ttk.Treeview(frame, columns=("Data", "Timestamp"), show='headings', yscrollcommand=scrollbar.set)
tree.heading("Data", text="QR Code Data")
tree.heading("Timestamp", text="Time Scanned")
tree.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=tree.yview)

# Detect Available Cameras
def get_available_cameras():
    available_cameras = []
    for i in range(5):  # Check up to 5 camera indexes
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(f"Camera {i}")
            cap.release()
    return available_cameras

# Select Camera
selected_camera_index = 0  # Default to camera 0

def select_camera():
    global selected_camera_index
    camera_window = tk.Toplevel(root)
    camera_window.title("Select Camera")

    tk.Label(camera_window, text="Choose the camera to use:").pack(pady=5)
    
    cameras = get_available_cameras()
    if not cameras:
        messagebox.showerror("Error", "No available cameras detected!")
        camera_window.destroy()
        return
    
    camera_var = tk.StringVar()
    camera_var.set(cameras[0])

    camera_dropdown = ttk.Combobox(camera_window, textvariable=camera_var, values=cameras)
    camera_dropdown.pack(pady=5)
    
    def confirm_selection():
        global selected_camera_index
        selected_camera_index = int(camera_var.get().split()[1])  # Extract the camera index
        messagebox.showinfo("Camera Selected", f"Using Camera {selected_camera_index}")
        camera_window.destroy()

    tk.Button(camera_window, text="Confirm", command=confirm_selection).pack(pady=5)

# Function to update the displayed table dynamically
def update_table():
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)

# Function to scan QR codes using the selected camera
def scan_qr_code():
    cap = cv2.VideoCapture(selected_camera_index)
    if not cap.isOpened():
        messagebox.showerror("Error", f"Camera {selected_camera_index} could not be accessed.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        for qr_code in decode(frame):
            data = qr_code.data.decode('utf-8')
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Check if the same QR code exists in the database
            cursor.execute("SELECT timestamp FROM students WHERE data = ?", (data,))
            last_entry = cursor.fetchone()

            if last_entry:
                last_timestamp = datetime.datetime.strptime(last_entry[0], "%Y-%m-%d %H:%M:%S")
                time_difference = (datetime.datetime.now() - last_timestamp).total_seconds()

                if time_difference < 60:  # Ensuring at least 1-minute difference
                    messagebox.showwarning("Duplicate Scan", f"QR code '{data}' was already scanned recently!")
                    continue

            # Insert data into SQLite database with timestamp
            cursor.execute("INSERT INTO students (data, timestamp) VALUES (?, ?)", (data, current_time))
            conn.commit()
            update_table()  # **Automatically refreshes displayed table**
            messagebox.showinfo("Success", f"Data '{data}' saved successfully!")

            points = np.array([qr_code.polygon], np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], True, (0, 255, 0), 2)

        cv2.imshow('QR Code Scanner', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to delete selected entry
def delete_selected():
    selected_item = tree.selection()
    if selected_item:
        for item in selected_item:
            values = tree.item(item, "values")
            data = values[0]
            cursor.execute("DELETE FROM students WHERE data = ?", (data,))
            conn.commit()
            update_table()  # **Refresh table after deletion**
            messagebox.showinfo("Deleted", f"Data '{data}' deleted permanently!")
    else:
        messagebox.showwarning("No Selection", "Please select an entry to delete.")

# Buttons with Improved Layout
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Select Camera", command=select_camera).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Start Scanning", command=scan_qr_code).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=5)

# Display Table Automatically on Start
update_table()

root.mainloop()
conn.close()