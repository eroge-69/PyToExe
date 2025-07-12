
# EMVWriterX Simulator (Tkinter version with Sound, Flip, and Loading Animation)
# Author: Converted from HTML/JS by ChatGPT
# Note: Educational use only

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import random
import time
import threading
import winsound  # For Windows beep sound

class EMVWriterXApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMVWriterX - Terminal Simulator")
        self.root.configure(bg='black')
        self.root.geometry("720x580")

        self.is_front = True

        # Header
        self.header = tk.Label(root, text="EMVWriterX", fg="lime", bg="black", font=("Courier", 20, "bold"))
        self.header.pack(pady=5)

        # Ghost animation
        self.ghost_label = tk.Label(root, text="👻", font=("Courier", 22), bg='black', fg='lime')
        self.ghost_label.place(x=10, y=10)
        self.animate_ghost()

        # Flip card display
        self.card_frame = tk.Frame(root, bg='black')
        self.card_frame.pack(pady=5)
        self.card_front = tk.Label(self.card_frame, text="[💳 FRONT OF CARD]", fg='lime', bg='black', font=("Courier", 12, "bold"))
        self.card_back = tk.Label(self.card_frame, text="[🔄 BACK OF CARD]", fg='lime', bg='black', font=("Courier", 12, "bold"))
        self.card_front.pack()
        self.flip_button = tk.Button(root, text="Flip Card", command=self.flip_card, bg='lime', fg='black')
        self.flip_button.pack()

        # Terminal display
        self.terminal = tk.Text(root, height=12, width=80, bg='black', fg='lime', font=("Courier", 10))
        self.terminal.pack(pady=10)
        self.log("Welcome to EMVWriterX Terminal...\nInsert Card to Begin\n")

        # Amount input
        frame = tk.Frame(root, bg='black')
        frame.pack()
        tk.Label(frame, text="Amount:", bg='black', fg='lime', font=("Courier", 10)).pack(side='left')
        self.amount_entry = tk.Entry(frame, bg='black', fg='lime', width=10, insertbackground='lime')
        self.amount_entry.insert(0, "25.00")
        self.amount_entry.pack(side='left', padx=5)
        tk.Button(frame, text="Start Transaction", command=self.start_transaction, bg='lime', fg='black').pack(side='left')

        # Loading animation label
        self.loading_label = tk.Label(root, text="", fg='lime', bg='black', font=('Courier', 10))
        self.loading_label.pack()

    def log(self, message):
        self.terminal.insert(tk.END, message + "\n")
        self.terminal.see(tk.END)
        self.root.update()

    def beep(self, success=True):
        try:
            freq = 1000 if success else 400
            winsound.Beep(freq, 200)
        except:
            pass

    def animate_ghost(self):
        def blink():
            while True:
                self.ghost_label.config(fg='black')
                time.sleep(0.6)
                self.ghost_label.config(fg='lime')
                time.sleep(0.6)
        threading.Thread(target=blink, daemon=True).start()

    def flip_card(self):
        if self.is_front:
            self.card_front.pack_forget()
            self.card_back.pack()
        else:
            self.card_back.pack_forget()
            self.card_front.pack()
        self.is_front = not self.is_front

    def show_loading(self, text="Processing", duration=3):
        def animate():
            for i in range(duration * 2):  # 0.5s intervals
                dots = "." * (i % 4)
                self.loading_label.config(text=text + dots)
                self.root.update()
                time.sleep(0.5)
            self.loading_label.config(text="")
        animate()

    def start_transaction(self):
        amount = self.amount_entry.get()
        self.terminal.delete("1.0", tk.END)
        self.log("Initializing Terminal...")
        self.beep()
        time.sleep(1)

        self.log("[✓] EMV Card Detected")
        self.beep()
        time.sleep(1)

        self.log("[✓] Reading Data...")
        time.sleep(1)

        self.log("[✓] Processing Amount: $" + amount)
        self.beep()
        time.sleep(1)

        self.log("[✓] Authenticating...")
        self.show_loading("Authenticating", duration=4)

        approved = random.choice([True, True, False])
        if approved:
            self.log("[✓] Transaction Approved")
            self.beep()
            self.print_receipt(amount, approved=True)
        else:
            self.log("[X] Transaction Declined")
            self.beep(success=False)
            self.print_receipt(amount, approved=False)

    def print_receipt(self, amount, approved=True):
        self.log("\n----- EMV RECEIPT -----")
        self.log("Merchant: CLI Market")
        self.log(f"Amount: ${amount}")
        self.log("Card: **** **** **** 4242")
        self.log("Status: " + ("APPROVED" if approved else "DECLINED"))
        self.log("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.log("------------------------")

if __name__ == "__main__":
    root = tk.Tk()
    app = EMVWriterXApp(root)
    root.mainloop()
