# smartMaint_gui.py
import subprocess
import schedule
import time
import os
from datetime import datetime
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class SmartMaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛠 smartMaint Monitor")
        self.root.geometry("600x400")

        self.log_text = ScrolledText(
            root, state="disabled", wrap="word", font=("Courier", 10)
        )
        self.log_text.pack(expand=True, fill="both")

        self.log("⏳ smartMaint avviato. In attesa delle pianificazioni...")

        # Pianifica i task
        schedule.every().hour.at(":00").do(self.hourly_task)
        schedule.every().hour.at(":00").do(self.monthly_task)

        # Avvia il loop in thread separato
        threading.Thread(target=self.scheduler_loop, daemon=True).start()

    def log(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, timestamp + message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def run_script(self, script_name):
        base_path = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_path, script_name)
        self.log(f"▶️ Eseguendo {script_name}")
        try:
            subprocess.run(["python", script_path], check=True)
            self.log(f"✅ Completato: {script_name}")
        except subprocess.CalledProcessError:
            self.log(f"❌ Errore durante l'esecuzione di {script_name}")

    def hourly_task(self):
        self.run_script("extract_data.py")
        self.run_script("run_inference.py")

    def monthly_task(self):
        today = datetime.today()
        if today.day == 1 and today.hour == 0:
            self.run_script("train_model.py")

    def scheduler_loop(self):
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartMaintApp(root)
    root.mainloop()
