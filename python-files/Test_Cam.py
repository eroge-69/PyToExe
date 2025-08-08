import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
class USBCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Camera Capture")
        self.root.geometry("550x550")
        # Font กำหนดไว้ตรงนี้เผื่ออยากเปลี่ยนรวดเร็ว
        self.default_font = ("Arial", 24)
        # กล้องที่เจอ (ลองแค่กล้อง 0-4)
        self.camera_options = self.find_cameras()
        # UI
        tk.Label(root, text="เลือกกล้อง:", font=self.default_font).pack(pady=10)
        self.cam_combo = ttk.Combobox(root, values=self.camera_options, state="readonly", font=self.default_font)
        self.cam_combo.pack(pady=5)
        if self.camera_options:
            self.cam_combo.current(0)
        self.capture_button = tk.Button(root, text="📷 ถ่ายภาพ", command=self.capture_image, font=self.default_font, width=20)
        self.capture_button.pack(pady=20)
        self.image_label = tk.Label(root, text="Preview", width=400, height=300, font=self.default_font)
        self.image_label.pack()
        self.cap = None
    def find_cameras(self):
        options = []
        for i in range(5):  # ลองเช็คกล้อง 0-4
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                options.append(f"Camera {i}")
                cap.release()
        return options
    def capture_image(self):
        selected_index = self.cam_combo.current()
        if selected_index == -1:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกกล้องก่อน")
            return
        self.cap = cv2.VideoCapture(selected_index)
        if not self.cap.isOpened():
            messagebox.showerror("ผิดพลาด", "ไม่สามารถเปิดกล้องได้")
            return
        ret, frame = self.cap.read()
        self.cap.release()
        if not ret:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถถ่ายภาพได้")
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image = image.resize((400, 300))
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo
if __name__ == "__main__":
    root = tk.Tk()
    app = USBCameraApp(root)
    root.mainloop()