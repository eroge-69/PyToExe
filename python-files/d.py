import tkinter as tk
from tkinter import messagebox
import threading
import time

class FakeWindows(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows 10 Professional")
        self.geometry("600x400")
        self.configure(bg='lightblue')
        
        self.label = tk.Label(self, text="Welcome to Windows 10 Professional", font=("Segoe UI", 16), bg='lightblue')
        self.label.pack(pady=150)

        # Lancer le timer de 10 secondes pour alerte
        self.after(10000, self.show_hack_alert)

    def show_hack_alert(self):
        messagebox.showwarning("Alert", "ur computer has been hacked sir")
        self.fake_installation()

    def fake_installation(self):
        # Vider la fenêtre
        for widget in self.winfo_children():
            widget.destroy()

        self.label = tk.Label(self, text="Installing Super Antivirus PRO 2077...", font=("Segoe UI", 16), bg='lightblue')
        self.label.pack(pady=20)

        self.progress = tk.DoubleVar()
        self.progress_bar = tk.ttk.Progressbar(self, length=400, variable=self.progress, maximum=100)
        self.progress_bar.pack(pady=20)

        # Lancer installation dans un thread pour ne pas bloquer l'interface
        threading.Thread(target=self.run_installation).start()

    def run_installation(self):
        for i in range(101):
            time.sleep(0.05)
            self.progress.set(i)
        time.sleep(1)
        self.show_final_message()

    def show_final_message(self):
        # Vider la fenêtre
        for widget in self.winfo_children():
            widget.destroy()
        self.label = tk.Label(self, text="u are stupid, i have all ur money now sir", font=("Segoe UI", 16), fg='red', bg='lightblue')
        self.label.pack(pady=150)
        # Après 4 secondes, quitter
        self.after(4000, self.quit)

if __name__ == "__main__":
    import tkinter.ttk as ttk  # Import ici pour éviter erreurs
    app = FakeWindows()
    app.mainloop()
