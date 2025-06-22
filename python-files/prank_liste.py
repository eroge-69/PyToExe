import tkinter as tk
from tkinter import Label
import cv2
from PIL import Image, ImageTk

class PrankListeApp:
    def __init__(self, window=None):
        self._own_window = False
        if window is None:
            self.window = tk.Tk()
            self._own_window = True
        else:
            self.window = window
        self.window.title("Prank")
        self.window.resizable(False, False)

        # Überschrift
        self.label_liste = Label(self.window, text="liste:", font=("Arial", 24))
        self.label_liste.pack(pady=(10, 0))

        # "DU"
        self.label_du = Label(self.window, text="DU", font=("Arial", 18))
        self.label_du.pack(pady=(0, 10))

        # Kamera-Label
        self.video_label = Label(self.window)
        self.video_label.pack()

        # Kamera starten
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update_frame()

        # Fenster schließen
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                # Bild spiegeln für Selfie-Effekt
                frame = cv2.flip(frame, 1)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            self.window.after(20, self.update_frame)

    def on_closing(self):
        self.running = False
        self.cap.release()
        self.window.destroy()

    def run(self):
        if self._own_window:
            self.window.mainloop()


def start_prank_liste():
    app = PrankListeApp()
    app.run()


if __name__ == "__main__":
    start_prank_liste() 