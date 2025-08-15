import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from imageio_ffmpeg import get_ffmpeg_exe
import os
import threading

class App:
    def __init__(self, master):
        self.master = master
        master.title("ClipShrinker")

        self.input_files = []
        self.output_files = []
        self.progress_bars = []
        self.completed_count = 0
        self.success_count = 0
        self.failed_files = []

        # GUI elements
        self.input_file_label = tk.Label(master, text="Input File(s):")
        self.input_file_label.grid(row=0, column=0, sticky="w")

        self.input_file_path = tk.StringVar(value="No file selected")
        self.input_file_path_label = tk.Label(master, textvariable=self.input_file_path, wraplength=300, anchor="w", justify="left")
        self.input_file_path_label.grid(row=0, column=1, sticky="w")

        self.output_file_label = tk.Label(master, text="Output File:")
        self.output_file_label.grid(row=1, column=0, sticky="w")

        self.output_file_path = tk.StringVar(value="No file selected")
        self.output_file_path_label = tk.Label(master, textvariable=self.output_file_path, wraplength=300, anchor="w", justify="left")
        self.output_file_path_label.grid(row=1, column=1, sticky="w")

        self.select_input_button = tk.Button(master, text="Select Input File(s)", command=self.select_input_files)
        self.select_input_button.grid(row=0, column=2, padx=5, pady=5)

        self.select_output_button = tk.Button(master, text="Select Output File", command=self.select_output_file)
        self.select_output_button.grid(row=1, column=2, padx=5, pady=5)

        self.render_button = tk.Button(master, text="Render", command=self.render_all)
        self.render_button.grid(row=2, column=1, pady=5)

        # Frame for progress bars
        self.progress_frame = tk.Frame(master)
        self.progress_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky="w")

    def select_input_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("MP4 files", "*.mp4")])
        if file_paths:
            self.input_files = list(file_paths)
            self.output_files = [os.path.splitext(p)[0] + "_opt.mp4" for p in self.input_files]
            self.input_file_path.set("\n".join(self.input_files))
            self.output_file_path.set("\n".join(self.output_files))
            self.create_progress_bars()

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".mp4")
        if file_path:
            if os.path.exists(file_path):
                result = messagebox.askyesno("File exists", "The file already exists. Do you want to overwrite it?")
                if not result:
                    return
            self.output_files = [file_path]
            self.output_file_path.set(file_path)

    def create_progress_bars(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        self.progress_bars.clear()
        for i, infile in enumerate(self.input_files):
            lbl = tk.Label(self.progress_frame, text=os.path.basename(infile), anchor="w")
            lbl.grid(row=i, column=0, sticky="w")
            pb = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate", maximum=100)
            pb.grid(row=i, column=1, padx=5, pady=2)
            self.progress_bars.append(pb)

    def render_all(self):
        if not self.input_files or not self.output_files:
            messagebox.showwarning("Warning", "Please select input file(s) first.")
            return

        self.completed_count = 0
        self.success_count = 0
        self.failed_files = []

        for idx, (infile, outfile) in enumerate(zip(self.input_files, self.output_files)):
            threading.Thread(target=self.render_video, args=(infile, outfile, self.progress_bars[idx]), daemon=True).start()

    def get_video_duration(self, filepath):
        ffmpeg_path = get_ffmpeg_exe()
        cmd = [
            ffmpeg_path.replace("ffmpeg", "ffprobe"),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception:
            return None

    def render_video(self, input_file, output_file, progress_bar):
        ffmpeg_path = get_ffmpeg_exe()
        duration = self.get_video_duration(input_file)
        if not duration:
            duration = 1

        command = [
            ffmpeg_path,
            "-i", input_file,
            "-y",
            "-fs", "7950000",
            "-r", "60",
            "-s", "1280x720",
            "-b:a", "96000",
            "-b:v", "4000000",
            "-progress", "pipe:1",
            "-nostats",
            output_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        for line in process.stdout:
            if "out_time_ms" in line:
                try:
                    time_ms = int(line.strip().split("=")[1])
                    percent = (time_ms / 1_000_000) / duration * 100
                    progress_bar["value"] = min(percent, 100)
                except ValueError:
                    pass
            self.master.update_idletasks()

        process.wait()
        progress_bar["value"] = 100

        if process.returncode == 0:
            self.success_count += 1
        else:
            self.failed_files.append(os.path.basename(input_file))

        self.completed_count += 1
        if self.completed_count == len(self.input_files):
            self.show_final_popup()

    def show_final_popup(self):
        total = len(self.input_files)
        failed_count = len(self.failed_files)

        if failed_count == 0:
            messagebox.showinfo("All Done", f"All {total} videos rendered successfully!")
        else:
            failed_list = "\n".join(self.failed_files)
            messagebox.showwarning(
                "Rendering Complete",
                f"Finished rendering {total} videos.\n"
                f"✅ Success: {self.success_count}\n"
                f"❌ Failed: {failed_count}\n\n"
                f"Failed files:\n{failed_list}"
            )
        # Close program after user clicks OK
        self.master.destroy()

root = tk.Tk()
app = App(root)
root.mainloop()