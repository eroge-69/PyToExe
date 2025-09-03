import tkinter as tk
from tkinter import filedialog
from pytube import YouTube

window = tk.Tk()
window.title("Videa Youtube Downloader(made complete with python)")
window.geometry("1280x720")
window.config(bg="#7532a8")

def download_video():
    if input_url.get() == "":
        print("Url invalido.")
    else:
        download_button.config(state=tk.DISABLED)
        input_url.config(state=tk.DISABLED)
        download_directory = filedialog.askdirectory(title="Scegli la destinazione del file")
        youtube = YouTube(input_url.get())
        video = youtube.streams.get_highest_resolution()
        vd_title = tk.Label(window, text=("Il titolo del video è "+youtube.title), bg="#7532a8", fg="orange")
        vd_title.grid(row=5, column=0, pady=20)    

label_title = tk.Label(window, text="Videa Youtube Downloader", font=("youtube-sans-bold", 48), bg="#7532a8", fg="#f80800")
label_title.grid(row=1, column=0, pady=30, padx=360)

label_video = tk.Label(window, text="Copia il link del video e incollalo o inseriscilo qua sotto", bg="#7532a8", fg="yellow")
label_video.grid(row=2, column=0)

input_url = tk.Entry(window)
input_url.grid(row=3, column=0, pady=100)

download_button = tk.Button(window, text="Scarica", bd=3, bg="#7532a8", width=20, command=download_video)
download_button.grid(row=4, column=0, pady=20)

window.mainloop()