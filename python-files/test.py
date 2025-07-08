import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
import pyttsx3
from PIL import Image
import win32gui
import win32con
import numpy as np
import cv2
import threading
import time
import os

# Ścieżka do Tesseract-OCR (musi być dołączona do .exe)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SubtitleReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inteligentny Lektor Napisów")
        self.root.geometry("300x150")

        # Zmienne
        self.language = tk.StringVar(value="polski")
        self.area = None
        self.running = False
        self.last_text = ""
        self.engine = None

        # GUI
        tk.Label(root, text="Wybierz język napisów:").pack(pady=10)
        tk.OptionMenu(root, self.language, "polski", "angielski").pack()
        tk.Button(root, text="Zaznacz obszar", command=self.select_area).pack(pady=10)
        tk.Button(root, text="Start", command=self.start_reading).pack(pady=10)

        # Inicjalizacja TTS
        self.init_tts()

    def init_tts(self):
        """Inicjalizacja silnika TTS z odpowiednim głosem."""
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if self.language.get() == "polski":
            for voice in voices:
                if "polish" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        else:  # angielski
            for voice in voices:
                if "english" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        self.engine.setProperty('rate', 150)  # Szybkość mowy

    def select_area(self):
        """Zaznaczanie obszaru ekranu."""
        self.root.iconify()  # Minimalizuj okno
        messagebox.showinfo("Instrukcja", "Naciśnij i przeciągnij myszą, aby zaznaczyć obszar z napisami.")

        # Proste zaznaczanie obszaru za pomocą pyautogui
        print("Kliknij lewym przyciskiem myszy, aby rozpocząć zaznaczanie.")
        while not pyautogui.mouseDown():
            pass
        x1, y1 = pyautogui.position()
        while pyautogui.mouseDown():
            pass
        x2, y2 = pyautogui.position()

        self.area = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        print(f"Zaznaczono obszar: {self.area}")
        self.root.deiconify()  # Przywróć okno

    def capture_screen(self):
        """Przechwytywanie zrzutu ekranu z wybranego obszaru."""
        if not self.area:
            return None
        x, y, w, h = self.area
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return img

    def preprocess_image(self, img):
        """Preprocessing obrazu dla lepszego OCR."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_text(self, img):
        """Rozpoznawanie tekstu z obrazu."""
        lang = "pol" if self.language.get() == "polski" else "eng"
        text = pytesseract.image_to_string(img, lang=lang).strip()
        return text

    def speak_text(self, text):
        """Odtwarzanie tekstu za pomocą TTS."""
        if text and text != self.last_text:
            self.engine.say(text)
            self.engine.runAndWait()
            self.last_text = text

    def reading_loop(self):
        """Główna pętla przetwarzania napisów."""
        while self.running:
            img = self.capture_screen()
            if img is not None:
                processed_img = self.preprocess_image(img)
                text = self.extract_text(processed_img)
                self.speak_text(text)
                del img, processed_img  # Czyszczenie pamięci
            time.sleep(0.1)  # Minimalne opóźnienie dla zmniejszenia obciążenia CPU

    def start_reading(self):
        """Uruchomienie głównej pętli w osobnym wątku."""
        if not self.area:
            messagebox.showerror("Błąd", "Najpierw zaznacz obszar z napisami!")
            return
        if not self.running:
            self.running = True
            self.last_text = ""
            threading.Thread(target=self.reading_loop, daemon=True).start()
            messagebox.showinfo("Info", "Lektor uruchomiony. Działa w tle.")

    def on_closing(self):
        """Zatrzymanie aplikacji."""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleReaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()