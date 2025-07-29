import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import threading
import os

class ToolsApp:
    def __init__(self, master):
        self.master = master
        master.title("Tools Application")

        self.clock_label = tk.Label(master, font=("Helvetica", 14))
        self.clock_label.pack()

        self.update_clock()

        self.create_buttons()

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.master.after(1000, self.update_clock)

    def create_buttons(self):
        tk.Button(self.master, text="Calculator", command=self.open_calculator).pack(pady=5)
        tk.Button(self.master, text="Text Editor", command=self.open_text_editor).pack(pady=5)
        tk.Button(self.master, text="Video Player", command=self.open_video_player).pack(pady=5)
        tk.Button(self.master, text="Audio Player", command=self.open_audio_player).pack(pady=5)
        tk.Button(self.master, text="MP3 Stream Player", command=self.open_mp3_stream_player).pack(pady=5)

    def open_calculator(self):
        calc_window = tk.Toplevel(self.master)
        calc_window.title("Calculator")
        entry = tk.Entry(calc_window, width=20)
        entry.pack()

        def calculate():
            try:
                result = eval(entry.get())
                messagebox.showinfo("Result", f"Result: {result}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(calc_window, text="Calculate", command=calculate).pack()

    def open_text_editor(self):
        editor_window = tk.Toplevel(self.master)
        editor_window.title("Text Editor")
        text_area = tk.Text(editor_window, wrap='word')
        text_area.pack(expand=True, fill='both')

        def save_file():
            file_path = simpledialog.askstring("Save File", "Enter file name:")
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(text_area.get("1.0", tk.END))

        tk.Button(editor_window, text="Save", command=save_file).pack()

    def open_video_player(self):
        messagebox.showinfo("Video Player", "Video player functionality is not implemented.")

    def open_audio_player(self):
        messagebox.showinfo("Audio Player", "Audio player functionality is not implemented.")

    def open_mp3_stream_player(self):
        messagebox.showinfo("MP3 Stream Player", "MP3 stream player functionality is not implemented.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolsApp(root)
    root.mainloop()
