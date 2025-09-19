import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from ultralytics import YOLO
import threading
import cv2
import time
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")
root = ctk.CTk()
root.title("SNVM AI Object Detector")
root.geometry("800x600")
root.resizable(False, False)
model = None
last_annotated_pil_image = None
is_camera_running = False
camera_thread = None
title = ctk.CTkLabel(
    root,
    text="SNVM AI Object Detector",
    font=("Times New Roman", 28, "bold"),
    text_color="black"
)
title.pack(pady=15)

image_frame = ctk.CTkFrame(root, fg_color="#e0e0e0", width=600, height=400)
image_frame.pack(pady=10)
image_frame.pack_propagate(False)

panel = ctk.CTkLabel(image_frame, text="")
panel.pack(expand=True)

loading_label = ctk.CTkLabel(
    image_frame,
    text="",
    font=("Times New Roman", 20),
    fg_color="#e0e0e0"
)

button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(pady=20, side="bottom")

button_style = {"fg_color": "white", "text_color": "black", "hover_color": "#f0f0f0", "corner_radius": 20}
btn_select = ctk.CTkButton(button_frame, text="Choose Image", **button_style, state="disabled")
btn_select.pack(side="left", padx=10)
btn_camera = ctk.CTkButton(button_frame, text="Camera Detection", **button_style, state="disabled")
btn_camera.pack(side="left", padx=10)
btn_save = ctk.CTkButton(button_frame, text="Save Result", **button_style, state="disabled")
btn_save.pack(side="left", padx=10)
exit_btn = ctk.CTkButton(
    button_frame, text="Exit", command=root.destroy,
    fg_color="#e74c3c", text_color="white", hover_color="#c0392b", corner_radius=20
)
exit_btn.pack(side="left", padx=10)

def load_model():
    """Loads the YOLO model, displaying progress in the loading_label."""
    global model
    loading_label.configure(text="⏳ Loading YOLO model...")
    loading_label.place(relx=0.5, rely=0.5, anchor='center')
    root.update_idletasks()
    
    model = YOLO("yolov8n.pt")
    
    loading_label.configure(text="✅ Model loaded!")
    root.after(1500, loading_label.place_forget)
    
    btn_select.configure(state="normal")
    btn_camera.configure(state="normal")

def update_image_panel(pil_image):
    """Updates the main panel with a new PIL image, resizing it for display."""
    panel_w, panel_h = 600, 400
    img_w, img_h = pil_image.size
    
    scale = min(panel_w / img_w, panel_h / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)
    
    img_resized = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(new_w, new_h))
    
    panel.configure(image=ctk_img, text="")
    panel.image = ctk_img

def process_and_display_result(annotated_frame_bgr):
    """Converts, stores, and displays the annotated frame."""
    global last_annotated_pil_image
    
    frame_rgb = cv2.cvtColor(annotated_frame_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    
    last_annotated_pil_image = pil_image
    
    update_image_panel(pil_image)
    btn_save.configure(state="normal")


def run_detection_on_image(file_path):
    """Runs YOLO detection in a thread with a mandatory 3-second loading screen."""
    def task():
        start_time = time.time()
        
        results = model.predict(source=file_path, save=False, verbose=False)
        annotated_frame = results[0].plot()

        processing_time = time.time() - start_time
        sleep_duration = max(0, 3 - processing_time)
        time.sleep(sleep_duration)

        root.after(0, loading_label.place_forget)
        root.after(0, process_and_display_result, annotated_frame)
        
        root.after(0, lambda: btn_select.configure(state="normal"))
        root.after(0, lambda: btn_camera.configure(state="normal"))

    threading.Thread(target=task, daemon=True).start()


def select_image():
    """Opens a file dialog and cleanly transitions to the loading state."""
    global is_camera_running
    
    if is_camera_running:
        toggle_camera()
        if camera_thread:
            camera_thread.join(timeout=0.5)
        btn_camera.configure(state="disabled")


    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
    )
    if file_path:
        btn_select.configure(state="disabled")
        btn_camera.configure(state="disabled")
        btn_save.configure(state="disabled")
        
        panel.configure(image=None, text="")
        
        loading_label.configure(text="Detecting objects... ⏳")
        loading_label.place(relx=0.5, rely=0.5, anchor='center')
        root.update_idletasks()
        
        run_detection_on_image(file_path)
    else:
        if not is_camera_running:
            btn_select.configure(state="normal")
            btn_camera.configure(state="normal")
            if last_annotated_pil_image:
                btn_save.configure(state="normal")


def save_result():
    """Saves the last annotated image to a file."""
    if last_annotated_pil_image:
        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        if save_path:
            last_annotated_pil_image.save(save_path)
            print(f"✅ Result saved to {save_path}")

def video_loop():
    """Main loop for capturing and processing camera frames."""
    global is_camera_running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        loading_label.configure(text="❌ Camera not found!")
        loading_label.place(relx=0.5, rely=0.5, anchor='center')
        root.after(1000, loading_label.place_forget)
        root.after(0, lambda: btn_select.configure(state="normal"))
        root.after(0, lambda: btn_camera.configure(text="Camera Detection", state="normal"))
        root.after(0, lambda: btn_save.configure(state="disabled"))
        return

    while is_camera_running:
        ret, frame = cap.read()
        if not ret:
            break
            
        results = model.predict(source=frame, save=False, verbose=False, stream=True)
        
        for r in results:
            if not is_camera_running:
                break
            annotated_frame = r.plot()
            root.after(0, process_and_display_result, annotated_frame)
            
    cap.release()
    if not is_camera_running:
        root.after(0, lambda: btn_select.configure(state="normal"))
        root.after(0, lambda: btn_camera.configure(text="Camera Detection", state="normal"))
        root.after(0, lambda: btn_save.configure(state="normal" if last_annotated_pil_image else "disabled"))


def toggle_camera():
    """Starts or stops the camera detection thread."""
    global is_camera_running, camera_thread
    if not is_camera_running:
        is_camera_running = True
        panel.configure(image=None, text="")
        loading_label.configure(text="Starting camera...")
        loading_label.place(relx=0.5, rely=0.5, anchor='center')
        root.after(500, loading_label.place_forget)
        
        btn_camera.configure(text="Stop Camera")
        btn_select.configure(state="disabled")
        btn_save.configure(state="disabled")
        
        camera_thread = threading.Thread(target=video_loop, daemon=True)
        camera_thread.start()
    else:
        is_camera_running = False
        btn_camera.configure(text="Camera Detection")
        if last_annotated_pil_image:
            btn_save.configure(state="normal")
        else:
            btn_save.configure(state="disabled")

        btn_select.configure(state="normal")


def on_closing():
    """Gracefully handles window closing."""
    global is_camera_running
    if is_camera_running:
        is_camera_running = False
        if camera_thread and camera_thread.is_alive():
            camera_thread.join(timeout=1)
    root.destroy()

btn_select.configure(command=select_image)
btn_save.configure(command=save_result)
btn_camera.configure(command=toggle_camera)

threading.Thread(target=load_model, daemon=True).start()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
