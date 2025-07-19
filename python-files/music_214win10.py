#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import numpy as np
from sklearn.cluster import KMeans
from music21 import stream, note, tempo, midi

# --- Core logic (unchanged) ----------------------------------------------

def extract_image_features(image_path, k=5):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    pixels = hsv.reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, random_state=42).fit(pixels)
    centers = kmeans.cluster_centers_.astype(int)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    return centers, edge_density

def map_to_music_params(centers, edge_density):
    root_hue = int(centers[0][0])
    root_note = int(root_hue / 15)
    tempo_bpm = int(60 + edge_density * 80)
    return root_note, tempo_bpm

def generate_melody_music21(root_note, tempo_bpm,
                            num_steps=128,
                            steps_per_quarter=4):
    scale_degrees = [0, 2, 4, 5, 7, 9, 11]
    base_pitch = 60 + root_note

    s = stream.Stream()
    s.append(tempo.MetronomeMark(number=tempo_bpm))

    step_quarter = 1.0 / steps_per_quarter
    for _ in range(num_steps):
        deg = np.random.choice(scale_degrees)
        n = note.Note(base_pitch + deg)
        n.volume.velocity = 80
        n.quarterLength = step_quarter
        s.append(n)

    return s

def save_midi(s, output_path):
    mf = midi.translate.streamToMidiFile(s)
    mf.open(output_path, 'wb')
    mf.write()
    mf.close()

# --- GUI Application -----------------------------------------------------

class ImageToMidiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image → MIDI Converter")
        self.geometry("500x250")
        self.resizable(False, False)

        # Variables
        self.image_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.steps_var = tk.IntVar(value=128)
        self.spq_var = tk.IntVar(value=4)

        # Build UI
        self._build_widgets()

    def _build_widgets(self):
        pad = {'padx': 10, 'pady': 5}

        # Input image
        tk.Label(self, text="Ảnh đầu vào:").grid(row=0, column=0, sticky='e', **pad)
        tk.Entry(self, textvariable=self.image_path_var, width=40).grid(row=0, column=1, **pad)
        tk.Button(self, text="Browse…", command=self.browse_image).grid(row=0, column=2, **pad)

        # Output MIDI
        tk.Label(self, text="File MIDI lưu tại:").grid(row=1, column=0, sticky='e', **pad)
        tk.Entry(self, textvariable=self.output_path_var, width=40).grid(row=1, column=1, **pad)
        tk.Button(self, text="Browse…", command=self.browse_output).grid(row=1, column=2, **pad)

        # Steps and SPQ
        tk.Label(self, text="Số bước melody:").grid(row=2, column=0, sticky='e', **pad)
        tk.Spinbox(self, from_=16, to=1024, increment=16, textvariable=self.steps_var, width=10).grid(row=2, column=1, sticky='w', **pad)

        tk.Label(self, text="Steps per quarter:").grid(row=3, column=0, sticky='e', **pad)
        tk.Spinbox(self, from_=1, to=16, textvariable=self.spq_var, width=10).grid(row=3, column=1, sticky='w', **pad)

        # Generate button & status
        self.generate_btn = tk.Button(self, text="Tạo MIDI", command=self.on_generate, width=15)
        self.generate_btn.grid(row=4, column=1, pady=15)

        self.status_lbl = tk.Label(self, text="", fg="blue")
        self.status_lbl.grid(row=5, column=0, columnspan=3)

    def browse_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All Files", "*.*")]
        )
        if path:
            self.image_path_var.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid"), ("All Files", "*.*")]
        )
        if path:
            self.output_path_var.set(path)

    def on_generate(self):
        img = self.image_path_var.get().strip()
        out = self.output_path_var.get().strip()
        steps = self.steps_var.get()
        spq = self.spq_var.get()

        if not img or not out:
            messagebox.showwarning("Thiếu đối số", "Vui lòng chọn file ảnh và file MIDI đầu ra.")
            return

        # Disable button to prevent re-click
        self.generate_btn.config(state='disabled')
        self.status_lbl.config(text="Đang xử lý…")

        # Run conversion in background thread to keep UI responsive
        threading.Thread(
            target=self._generate_background,
            args=(img, out, steps, spq),
            daemon=True
        ).start()

    def _generate_background(self, img, out, steps, spq):
        try:
            centers, edge_density = extract_image_features(img)
            root_note, tempo_bpm = map_to_music_params(centers, edge_density)
            melody = generate_melody_music21(root_note, tempo_bpm,
                                             num_steps=steps,
                                             steps_per_quarter=spq)
            save_midi(melody, out)

            # Update UI on success
            self.after(0, lambda: self._finish("Hoàn thành! MIDI đã lưu."))
        except Exception as e:
            self.after(0, lambda: self._finish(f"Lỗi: {e}"))

    def _finish(self, msg):
        self.status_lbl.config(text=msg)
        self.generate_btn.config(state='normal')
        if msg.startswith("Hoàn thành"):
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)

if __name__ == "__main__":
    app = ImageToMidiApp()
    app.mainloop()
