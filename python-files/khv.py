import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class RSVPApp:
    def __init__(self, master):
        self.master = master
        master.title("RSVP Reader (Text files only)")

        # Text input area
        self.text_input = tk.Text(master, height=8, width=60)
        self.text_input.pack(pady=10)

        # Control panel
        control_frame = ttk.Frame(master)
        control_frame.pack(pady=5)

        ttk.Label(control_frame, text="WPM:").pack(side=tk.LEFT)
        self.wpm = tk.IntVar(value=300)
        ttk.Entry(control_frame, width=6, textvariable=self.wpm).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Start", command=self.start_rsvp).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_rsvp).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Open Text File", command=self.open_file).pack(side=tk.LEFT, padx=5)

        # Word display area
        self.word_label = tk.Label(master, text="", font=("Helvetica", 40), pady=20)
        self.word_label.pack()

        self.words = []
        self.word_index = 0
        self.running = False

    def start_rsvp(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
            self.word_label.config(text="(No text)")
            return

        self.words = raw_text.split()
        self.word_index = 0
        self.running = True
        self.next_word()

    def stop_rsvp(self):
        self.running = False

    def next_word(self):
        if not self.running or self.word_index >= len(self.words):
            self.running = False
            return

        self.word_label.config(text=self.words[self.word_index])
        self.word_index += 1

        delay = int(60000 / max(1, self.wpm.get()))  # ms per word
        self.master.after(delay, self.next_word)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            self.text_input.delete("1.0", tk.END)
            self.text_input.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RSVPApp(root)
    root.mainloop()
