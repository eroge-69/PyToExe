import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment


def mix_audio(vocal_path, instrumental_path, output_path):
    try:
        vocal = AudioSegment.from_file(vocal_path)
        instrumental = AudioSegment.from_file(instrumental_path)

        while len(instrumental) < len(vocal):
            instrumental += instrumental

        instrumental = instrumental[:len(vocal)]
        mixed = vocal.overlay(instrumental)

        mixed.export(output_path, format="mp3")
        print(f"Created: {output_path}")
    except Exception as e:
        print(f"Error processing {vocal_path}: {str(e)}")
        raise


def process_all(vocals_dir, instrumental_path, output_dir):
    try:
        print(f"Looking in vocals directory: {vocals_dir}")
        print(f"Instrumental file: {instrumental_path}")
        print(f"Output directory: {output_dir}")

        all_files = os.listdir(vocals_dir)
        print(f"All files found: {all_files}")

        wav_files = [f for f in all_files if f.lower().endswith(('.wav', '.mp3', '.m4a', '.flac'))]
        print(f"Audio files found: {wav_files}")

        counter = 1
        processed = 0
        for file in wav_files:
            vocal_path = os.path.join(vocals_dir, file)
            output_path = os.path.join(output_dir, f"AH_vocals_{counter}.mp3")
            print(f"Processing: {file}")
            mix_audio(vocal_path, instrumental_path, output_path)
            counter += 1
            processed += 1
        messagebox.showinfo("Done", f"Processed {processed} files successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def browse_dir(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)


def browse_file(entry):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)


def create_gui():
    root = tk.Tk()
    root.title("Auto Mixer GUI")

    tk.Label(root, text="Vocals Folder").grid(row=0, column=0, sticky="e")
    tk.Label(root, text="Instrumental File").grid(row=1, column=0, sticky="e")
    tk.Label(root, text="Output Folder").grid(row=2, column=0, sticky="e")

    vocals_entry = tk.Entry(root, width=50)
    instrumental_entry = tk.Entry(root, width=50)
    output_entry = tk.Entry(root, width=50)

    vocals_entry.grid(row=0, column=1)
    instrumental_entry.grid(row=1, column=1)
    output_entry.grid(row=2, column=1)

    tk.Button(root, text="Browse", command=lambda: browse_dir(vocals_entry)).grid(row=0, column=2)
    tk.Button(root, text="Browse", command=lambda: browse_file(instrumental_entry)).grid(row=1, column=2)
    tk.Button(root, text="Browse", command=lambda: browse_dir(output_entry)).grid(row=2, column=2)

    tk.Button(root, text="Start Mixing", command=lambda: process_all(
        vocals_entry.get(), instrumental_entry.get(), output_entry.get())
              ).grid(row=3, column=1, pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()