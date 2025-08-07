import tkinter as tk
import time
import threading
import random

# Simulated "encrypted" files
fake_files = [f"Document_{i}.docx" for i in range(1, 6)] + \
             [f"Photo_{i}.jpg" for i in range(1, 6)] + \
             [f"Project_{i}.zip" for i in range(1, 4)]


class RansomwareSim:
    def __init__(self, root):
        self.root = root
        self.root.title("WannaCry Ransomware")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        self.countdown_seconds = 300 # 5 minutes

        self.decrypt_button = None  # placeholder to modify later
        self.author_label = None

        self.build_ui()
        threading.Thread(target=self.countdown, daemon=True).start()
        threading.Thread(target=self.simulate_encryption, daemon=True).start()

    def disable_event(self):
        pass  # Prevent manual window close

    def build_ui(self):
        self.title_label = tk.Label(self.root, text="Ooops, your files have been encrypted!", fg="red",
                                    bg="black", font=("Courier", 28, "bold"))
        self.title_label.pack(pady=30)

        self.info_label = tk.Label(self.root, text=(
            "All your important files are encrypted.\n"
            "To decrypt them, you must send $300 worth of Bitcoin.\n"
            "You have limited time before your files are permanently deleted."
        ), fg="white", bg="black", font=("Courier", 14))
        self.info_label.pack()

        self.timer_label = tk.Label(self.root, text="", fg="yellow", bg="black", font=("Courier", 20, "bold"))
        self.timer_label.pack(pady=20)

        self.file_list = tk.Text(self.root, height=10, width=60, bg="black", fg="lime", font=("Courier", 12))
        self.file_list.pack()
        self.file_list.insert(tk.END, "Encrypted Files:\n")
        self.file_list.config(state=tk.DISABLED)

        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(pady=20)

        self.decrypt_button = tk.Button(self.button_frame, text="Decrypt", command=self.decrypt,
                                        width=12, font=("Courier", 12))
        self.decrypt_button.pack(side=tk.LEFT, padx=20)

        tk.Button(self.button_frame, text="Pay", command=self.pay,
                  width=12, font=("Courier", 12)).pack(side=tk.LEFT, padx=20)

    def countdown(self):
        while self.countdown_seconds >= 0:
            mins, secs = divmod(self.countdown_seconds, 60)
            time_format = f"{mins:02d}:{secs:02d}"
            self.timer_label.config(text=f"Time Remaining: {time_format}")
            time.sleep(1)
            self.countdown_seconds -= 1
        self.timer_label.config(text="Time's up! Files permanently lost 😈")

    def simulate_encryption(self):
        for file in fake_files:
            time.sleep(random.uniform(0.5, 1.5))
            self.file_list.config(state=tk.NORMAL)
            self.file_list.insert(tk.END, f"• {file} -> {file}.ppt\n")
            self.file_list.config(state=tk.DISABLED)

    def decrypt(self):
        self.timer_label.config(text="Decrypting files...", fg="green")
        time.sleep(2)
        self.end_simulation()

    def pay(self):
        self.timer_label.config(text="Processing payment...", fg="orange")
        self.decrypt_button.destroy()  # remove decrypt button
        time.sleep(2)

        self.root.destroy()
        self.show_author_message()

    def show_author_message(self):
        # Show prank message after GUI closes
        msg_root = tk.Tk()
        msg_root.title("Created by: AXVIIB")
        msg_root.configure(bg='black')
        msg_root.geometry("600x200")

        prank_msg = tk.Label(msg_root,
                             text="🎉 RELAX! This was just a prank.\nNo files were harmed.",
                             fg="lime", bg="black",
                             font=("Courier", 16))
        prank_msg.pack(pady=20)

        self.author_label = tk.Label(msg_root,
                                     text="👨‍💻 Created by: AXVIIB",
                                     fg="cyan", bg="black",
                                     font=("Courier", 14, "italic"))
        self.author_label.pack()

        tk.Button(msg_root, text="Close", command=msg_root.destroy,
                  font=("Courier", 12), bg="gray", fg="black").pack(pady=20)

        msg_root.mainloop()

    def end_simulation(self):
        self.root.destroy()
        self.show_author_message()


if __name__ == "__main__":
    root = tk.Tk()
    app = RansomwareSim(root)
    root.mainloop()
