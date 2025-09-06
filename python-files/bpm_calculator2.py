# This script creates a GUI application to calculate the Beats Per Minute (BPM)
# of a song file. It now includes drag-and-drop support, a waveform preview,
# and visual beat markers.
# It uses the `tkinter` and `tkinterdnd2` libraries for the graphical interface,
# and `librosa` and `matplotlib` for audio and data visualization.
#
# Before running this script, you must install the following libraries:
# pip install librosa
# pip install matplotlib
# pip install tkinterdnd2
#
# Tkinter is a standard library, so no installation should be necessary for it.

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import librosa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# A class to represent the BPM Calculator application
class BPMCalculatorApp:
    def __init__(self, root):
        # Initialize the main window, now using TkinterDnD
        self.root = root
        self.root.title("BPM Calculator")
        self.root.geometry("800x600")
        
        # Set a song file path variable
        self.song_path = ""

        # Create GUI widgets
        self.create_widgets()

    def create_widgets(self):
        # Create a main frame with padding
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for the control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)

        # Button to open a file dialog
        self.select_button = tk.Button(control_frame, text="Select Song File", command=self.select_file, font=("Helvetica", 12))
        self.select_button.pack(side=tk.LEFT, padx=5)

        # Button to calculate BPM
        self.calculate_button = tk.Button(control_frame, text="Calculate BPM", command=self.calculate_bpm, font=("Helvetica", 14), state=tk.DISABLED)
        self.calculate_button.pack(side=tk.LEFT, padx=5)

        # Label to display the selected file path
        self.file_label = tk.Label(main_frame, text="Drag and drop a song file here or click 'Select File'", font=("Helvetica", 10), wraplength=700)
        self.file_label.pack(pady=5)
        
        # Configure the main window to accept dropped files
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # Frame for the waveform plot
        self.plot_frame = tk.Frame(main_frame, borderwidth=2, relief="sunken")
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a placeholder label for the plot area
        self.plot_placeholder_label = tk.Label(self.plot_frame, text="Waveform Preview", font=("Helvetica", 12), fg="gray")
        self.plot_placeholder_label.pack(fill=tk.BOTH, expand=True)

        # Label to display the calculated BPM result
        self.result_label = tk.Label(main_frame, text="", font=("Helvetica", 20, "bold"))
        self.result_label.pack(pady=10)

    def on_drop(self, event):
        # Handle the drop event. `event.data` contains the file path(s).
        # We only process the first file if multiple are dropped.
        dropped_file = event.data.strip('{}').split(' ')[0]
        self.process_file(dropped_file)

    def select_file(self):
        # Open a file dialog to let the user select a song file.
        filetypes = [("Audio files", "*.mp3 *.wav *.flac *.ogg"), ("All files", "*.*")]
        selected_file = filedialog.askopenfilename(filetypes=filetypes)
        if selected_file:
            self.process_file(selected_file)

    def process_file(self, file_path):
        self.song_path = file_path
        if self.song_path:
            # Update the label with the selected file path
            self.file_label.config(text=f"Selected: {self.song_path}")
            # Enable the calculate button
            self.calculate_button.config(state=tk.NORMAL)
            # Clear the previous result
            self.result_label.config(text="")
        else:
            # If no file is selected, reset the state
            self.file_label.config(text="Drag and drop a song file here or click 'Select File'")
            self.calculate_button.config(state=tk.DISABLED)

    def calculate_bpm(self):
        if not self.song_path:
            messagebox.showwarning("No File", "Please select a song file first.")
            return

        # Use a try-except block to handle potential errors
        try:
            # Load the audio file using librosa
            y, sr = librosa.load(self.song_path, sr=None)
            
            # Use librosa to track the beats and estimate the tempo
            # `beat_track` returns the tempo and the beat frames
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            
            # Convert the beat frames to timestamps in seconds
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            # Draw the waveform and the beat markers
            self.draw_waveform(y, sr, beat_times)

            # Round the tempo to two decimal places
            bpm = round(tempo, 2)

            # Update the result label with the calculated BPM
            self.result_label.config(text=f"Estimated BPM: {bpm}")

        except Exception as e:
            # If an error occurs, display an error message
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.result_label.config(text="Calculation failed.")
            print(f"Error details: {e}")

    def draw_waveform(self, y, sr, beat_times):
        # Clear the placeholder label
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # Create a new matplotlib figure and an axes
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
        ax.set_facecolor('#f0f0f0') # Match Tkinter's background color
        fig.patch.set_facecolor('#f0f0f0')
        
        # Plot the waveform, converting time to seconds for the x-axis
        librosa.display.waveshow(y, sr=sr, ax=ax, color='blue')
        
        # Add vertical lines to mark the beats
        ax.vlines(beat_times, ymin=-1, ymax=1, color='red', linestyle='--', linewidth=2, label='Beats')
        
        # Customize the plot
        ax.set_title("Waveform Preview with Beat Markers", fontsize=14)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        
        # Embed the matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Main entry point of the application
if __name__ == "__main__":
    # Create the main window instance
    root = TkinterDnD.Tk()
    # Create an instance of the application
    app = BPMCalculatorApp(root)
    # Start the Tkinter event loop
    root.mainloop()