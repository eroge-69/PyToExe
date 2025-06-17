import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

REDEEM_URL = "https://www.roblox.com/fr/redeem?nl=true"
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), "chromedriver.exe")
LOG_FILE = "invalid_codes.log"

class RedeemBot:
    def __init__(self, master):
        self.master = master
        self.master.title("Roblox Code Bot")
        self.codes = []
        self.running = False
        self.paused = False
        self.driver = None

        self.label = tk.Label(master, text="Aucun fichier sélectionné")
        self.label.pack(pady=5)

        self.progress = tk.DoubleVar()
        self.progress_bar = tk.Scale(master, variable=self.progress, from_=0, to=100,
                                     orient='horizontal', length=300, label="Progression (%)")
        self.progress_bar.pack(pady=5)

        self.select_button = tk.Button(master, text="Choisir fichier de codes", command=self.load_codes)
        self.select_button.pack(pady=5)

        self.start_button = tk.Button(master, text="Démarrer", command=self.toggle_start, state='disabled')
        self.start_button.pack(pady=5)

        self.pause_button = tk.Button(master, text="Pause", command=self.toggle_pause, state='disabled')
        self.pause_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop, state='disabled')
        self.stop_button.pack(pady=5)

    def load_codes(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                self.codes = [line.strip() for line in f if line.strip()]
            self.label.config(text=f"{len(self.codes)} codes chargés.")
            self.start_button.config(state='normal')
            self.progress.set(0)

    def toggle_start(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.pause_button.config(state='normal')
            self.stop_button.config(state='normal')
            self.start_button.config(state='disabled')
            threading.Thread(target=self.run_bot, daemon=True).start()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Reprendre" if self.paused else "Pause")

    def stop(self):
        self.running = False
        self.paused = False
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.label.config(text="Bot arrêté.")
        self.progress.set(0)
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def run_bot(self):
        try:
            with open(LOG_FILE, 'w') as log:
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                self.driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

                total = len(self.codes)
                for idx, code in enumerate(self.codes):
                    if not self.running:
                        break
                    while self.paused:
                        time.sleep(0.5)

                    self.label.config(text=f"Essai {idx + 1}/{total} : {code}")
                    self.progress.set((idx + 1) * 100 / total)

                    try: 
                        time.sleep(2)
                        self.driver.get(REDEEM_URL)
                        time.sleep(2)
                        input_box = self.driver.find_element(By.ID, "code-input")
                        input_box.clear()
                        input_box.send_keys(code)
                        redeem_button = self.driver.find_element(By.XPATH, "//button[text()='Activer']")
                        redeem_button.click()
                        time.sleep(5)

                        if "invalid" in self.driver.page_source.lower():
                            log.write(f"{code}\n")
                            log.flush()

                    except Exception as e:
                        log.write(f"{code} - ERREUR: {str(e)}\n")
                        log.flush()
                        continue
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de démarrer le navigateur : {e}")
        finally:
            self.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = RedeemBot(root)
    root.mainloop()
