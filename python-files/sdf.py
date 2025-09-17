import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cv2
import numpy as np
import random
from PIL import ImageFont, ImageDraw, Image

class VideoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cutter & Merger")

        self.video_paths = []
        self.output_name = tk.StringVar(value="output")  # không kèm .mp4
        self.text_var = tk.StringVar()
        self.num_videos = tk.IntVar(value=2)  # số video xuất ra

        # Danh sách font có sẵn
        self.fonts = {
            "Arial": "C:/Windows/Fonts/arial.ttf",
            "Times New Roman": "C:/Windows/Fonts/times.ttf",
            "Courier New": "C:/Windows/Fonts/cour.ttf",
            "Verdana": "C:/Windows/Fonts/verdana.ttf"
        }

        # UI chọn video
        tk.Button(root, text="Chọn 6 video", command=self.load_videos).grid(row=0, column=0, columnspan=2, pady=5)

        # Ô nhập tên file xuất
        tk.Label(root, text="Tên file xuất (không .mp4):").grid(row=1, column=0, sticky="w")
        tk.Entry(root, textvariable=self.output_name).grid(row=1, column=1, sticky="ew")

        # Chọn số lượng video muốn xuất
        tk.Label(root, text="Số video cần xuất:").grid(row=2, column=0, sticky="w")
        tk.Spinbox(root, from_=1, to=20, textvariable=self.num_videos).grid(row=2, column=1, sticky="ew")

        # Chọn font
        tk.Label(root, text="Chọn font chữ:").grid(row=3, column=0, sticky="w")
        self.font_var = tk.StringVar(value="Arial")
        self.font_combo = ttk.Combobox(root, textvariable=self.font_var, values=list(self.fonts.keys()))
        self.font_combo.grid(row=3, column=1, sticky="ew")

        # Nhập text
        tk.Label(root, text="Thêm chữ:").grid(row=4, column=0, sticky="w")
        tk.Entry(root, textvariable=self.text_var).grid(row=4, column=1, sticky="ew")

        # Nút xử lý
        tk.Button(root, text="Xuất video", command=self.process_multiple_videos).grid(row=5, column=0, columnspan=2, pady=10)

    def load_videos(self):
        paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if len(paths) == 6:
            self.video_paths = list(paths)
        else:
            messagebox.showerror("Lỗi", "Vui lòng chọn đúng 6 video!")

    def add_text_to_frame(self, frame):
        """Thêm chữ vào frame bằng Pillow"""
        if self.text_var.get():
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            font_path = self.fonts.get(self.font_var.get(), "C:/Windows/Fonts/arial.ttf")
            font = ImageFont.truetype(font_path, 36)
            draw.text((50, 50), self.text_var.get(), font=font, fill=(255, 0, 0, 255))
            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return frame

    def process_single_video(self, output_file):
        """Xử lý 1 video với cắt ngẫu nhiên"""
        clips = []
        target_duration = 2.15  # thời lượng mỗi đoạn

        for path in self.video_paths:
            cap = cv2.VideoCapture(path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps

            # chọn random start time
            if duration > target_duration:
                start_time = random.uniform(0, duration - target_duration)
            else:
                start_time = 0

            start_frame = int(start_time * fps)
            end_frame = min(start_frame + int(target_duration * fps), total_frames)

            frames = []
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or int(cap.get(cv2.CAP_PROP_POS_FRAMES)) > end_frame:
                    break

                # Scale lên 110%
                h, w = frame.shape[:2]
                frame = cv2.resize(frame, (int(w * 1.1), int(h * 1.1)))

                # Thêm chữ
                frame = self.add_text_to_frame(frame)

                frames.append(frame)
            cap.release()
            clips.extend(frames)

        if not clips:
            return False

        # Xuất video
        h, w = clips[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_file, fourcc, 30, (w, h))
        for f in clips:
            out.write(f)
        out.release()
        return True

    def process_multiple_videos(self):
        """Xuất nhiều video theo số lượng người dùng chọn"""
        if not self.video_paths:
            messagebox.showerror("Lỗi", "Bạn chưa chọn video!")
            return

        base_name = self.output_name.get()
        count = self.num_videos.get()
        success_files = []

        for i in range(1, count + 1):
            file_name = f"{base_name}_{i}.mp4"
            success = self.process_single_video(file_name)
            if success:
                success_files.append(file_name)

        if success_files:
            messagebox.showinfo("Thành công", f"Đã xuất {len(success_files)} video:\n" + "\n".join(success_files))
        else:
            messagebox.showerror("Lỗi", "Không xuất được video nào!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorApp(root)
    root.mainloop()
