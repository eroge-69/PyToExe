import customtkinter as ctk
import cv2
from PIL import Image
import os
from datetime import datetime
import time
from customtkinter import CTkImage, CTkFont
import numpy as np

# DPI scaling
ctk.set_window_scaling(1.0)
ctk.set_widget_scaling(1.0)

# Create Project365 folder if it doesn't exist
output_dir = "Project365"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Configuration file for last selected camera
config_file = "config.txt"

# Function to load last selected camera index
def load_last_camera(available_cameras):
    try:
        with open(config_file, "r") as f:
            last_index = f.read().strip()
            if last_index in available_cameras:
                return last_index
    except FileNotFoundError:
        pass
    return available_cameras[0] if available_cameras else "No Camera"

# Function to save selected camera index
def save_last_camera(index):
    with open(config_file, "w") as f:
        f.write(str(index))

# Function to detect available cameras
def get_available_cameras(max_index=3):
    available = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available.append(str(index))
            cap.release()
    return available if available else ["No Camera"]

# Initialize OpenCV
available_cameras = get_available_cameras()
if not available_cameras or available_cameras == ["No Camera"]:
    error_popup = ctk.CTk()
    ctk.CTkLabel(error_popup, text="Error: No camera found. Please connect a webcam and try again.").pack(padx=20, pady=20)
    ctk.CTkButton(error_popup, text="OK", command=error_popup.quit).pack(pady=10)
    error_popup.mainloop()
    exit()

# Load last selected camera or default to first available
default_camera = load_last_camera(available_cameras)

# Initialize with the default camera
cap = cv2.VideoCapture(int(default_camera))
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
if face_cascade.empty():
    print("Error: Could not load face cascade.")
    exit()

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Detection box (portrait)
box_w, box_h = 400, 500
box_x = frame_width // 2 - box_w // 2
box_y = frame_height // 2 - box_h // 2
margin = 10  # Margin for flexible detection

# Countdown variables
hold_still_start_time = None
countdown_seconds = 3
face_saved = False

# Tkinter setup
main = ctk.CTk()
main.configure(fg_color="#23272D")
main.title("Project 365")
main.geometry("900x600+100+50")
main.minsize(600, 450)
main.resizable(True, True)

# Frame for the camera feed
camera_frame = ctk.CTkFrame(master=main, fg_color="#23272D")
camera_frame.place(relx=0.5, rely=0.5, relwidth=1.0, relheight=0.85, anchor="center")

camera_label = ctk.CTkLabel(master=camera_frame, text="", fg_color="#23272D")
camera_label.place(relwidth=1, relheight=1)

# Font for labels
console_font = CTkFont(family="Consolas", size=16)

# Camera selector label (top-center, left of dropdown)
camera_selector_label = ctk.CTkLabel(
    master=main,
    text="Select Camera",
    font=console_font,
    text_color="#CCCCCC",
    fg_color="#23272D"
)
camera_selector_label.place(relx=0.45, y=10, anchor="ne")

# Camera selector (top-center)
camera_selector = ctk.CTkOptionMenu(
    master=main,
    values=available_cameras,
    font=console_font,
    fg_color="#3B8ED0",
    button_color="#1F6AA5",
    dropdown_font=console_font,
    command=lambda value: change_camera(value)
)
camera_selector.place(relx=0.5, y=10, anchor="nw")
camera_selector.set(default_camera)  # Set default to last selected camera

# Info label (bottom-left)
info_label = ctk.CTkLabel(
    master=main,
    text="FoxLabs Project 365 ver1",
    font=console_font,
    text_color="#FFAA00",
    fg_color="#23272D"
)
info_label.place(x=10, rely=0.95, anchor="w")

# Status label (top-left for face confirmation)
status_label = ctk.CTkLabel(
    master=main,
    text="Face Not Confirmed ❌",
    font=console_font,
    text_color="#FF0000",
    fg_color="#23272D"
)
status_label.place(x=10, y=40, anchor="nw")

# Countdown label (top-right)
countdown_label = ctk.CTkLabel(
    master=main,
    text="",
    font=console_font,
    text_color="#FFFF00",
    fg_color="#23272D"
)
countdown_label.place(relx=0.95, y=40, anchor="ne")

# Save confirmation label (bottom-center)
save_label = ctk.CTkLabel(
    master=main,
    text="",
    font=console_font,
    text_color="#00FF00",
    fg_color="#23272D"
)
save_label.place(relx=0.5, rely=0.95, anchor="s")

def change_camera(value):
    global cap
    if value != "No Camera":
        cap.release()
        cap = cv2.VideoCapture(int(value))
        if not cap.isOpened():
            print(f"Error: Could not open camera {value}.")
            main.quit()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        save_last_camera(value)  # Save the selected camera index

def update_frame():
    global hold_still_start_time, face_saved

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        main.quit()
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )

    face_fully_inside = False
    selected_face = None

    for (x, y, w, h) in faces:
        # Draw light blue box around all detected faces
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        face_left = x - margin
        face_top = y - margin
        face_right = x + w + margin
        face_bottom = y + h + margin

        if (
            face_left >= box_x and
            face_top >= box_y and
            face_right <= box_x + box_w and
            face_bottom <= box_y + box_h
        ):
            face_fully_inside = True
            selected_face = (x, y, w, h)
            break

    current_time = time.time()

    if face_fully_inside:
        if hold_still_start_time is None:
            hold_still_start_time = current_time  # Start countdown
        elapsed = current_time - hold_still_start_time
        remaining = countdown_seconds - int(elapsed)
        if remaining <= 0 and not face_saved:
            # Prepare the frame with embedded date
            date_text = datetime.now().strftime("%Y-%m-%d")
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            font_color = (255, 255, 255)  # White text
            thickness = 2
            text_size = cv2.getTextSize(date_text, font, font_scale, thickness)[0]
            text_x = frame_width - text_size[0] - 20  # 20px padding from right
            text_y = frame_height - 20  # 20px padding from bottom

            # Draw semi-transparent black rectangle as background
            overlay = frame.copy()
            rect_x1, rect_y1 = text_x - 5, text_y - text_size[1] - 5
            rect_x2, rect_y2 = text_x + text_size[0] + 5, text_y + 5
            cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
            alpha = 0.6  # Semi-transparent
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Draw the date text
            cv2.putText(frame, date_text, (text_x, text_y), font, font_scale, font_color, thickness)

            # Save the entire frame with date
            date_str = datetime.now().strftime("%Y%m%d")
            output_path = os.path.join(output_dir, f"photo_{date_str}.jpg")
            cv2.imwrite(output_path, frame)
            print(f"Photo saved to {output_path}")
            face_saved = True
            save_label.configure(text="Photo taken, closing now")
            main.after(1000, main.quit)  # Close after 1 second
    else:
        # Reset countdown if face moves out
        hold_still_start_time = None
        face_saved = False

    # Update status and colors
    box_color = (0, 255, 0) if face_fully_inside else (0, 0, 255)
    status_text = "Face Confirmed ✅" if face_fully_inside else "Face Not Confirmed ❌"
    status_color = "#00FF00" if face_fully_inside else "#FF0000"
    status_label.configure(text=status_text, text_color=status_color)

    # Draw target rectangle
    cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), box_color, 2)

    # Update countdown label
    if face_fully_inside and not face_saved:
        countdown_label.configure(text=f"Hold still: {remaining}s")
    else:
        countdown_label.configure(text="")

    # Update save label
    if face_saved:
        save_label.configure(text="Photo taken, closing now")
    else:
        save_label.configure(text="")

    # Update camera feed
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h = camera_frame.winfo_height()
    w = camera_frame.winfo_width()
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_CUBIC)
    pil = Image.fromarray(img)
    ctk_img = CTkImage(light_image=pil, size=(w, h))
    camera_label.configure(image=ctk_img)
    camera_label.image = ctk_img

    if not face_saved:
        camera_label.after(5, update_frame)  # Reduced delay for higher frame rate

update_frame()
main.mainloop()
cap.release()
cv2.destroyAllWindows()