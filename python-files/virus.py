import tkinter as tk
from tkinter import messagebox
import time
import threading
import winsound  

def play_alarm():
    
    while True:
        winsound.Beep(1200, 500)  
        time.sleep(0.2)            

def show_virus_alert():
    
    sound_thread = threading.Thread(target=play_alarm, daemon=True)
    sound_thread.start()

    while True:
        
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="black")

        
        label = tk.Label(root, text=" VIRUS DÉTECTÉ ", font=("Arial", 50, "bold"), fg="red", bg="black")
        label.pack(expand=True)

        
        root.after(1000, lambda: messagebox.showerror("SÉCURITÉ WINDOWS", "Une menace critique a été détectée."))
        root.after(3000, lambda: messagebox.showwarning("ÉTAT DU SYSTÈME", "Le système tente une réparation..."))
        root.after(6000, lambda: messagebox.showerror("ERREUR IRRÉCUPÉRABLE", "La réparation a échoué. Restauration impossible."))

        
        root.after(10000, root.destroy)

        root.mainloop()
        time.sleep(2)


show_virus_alert()