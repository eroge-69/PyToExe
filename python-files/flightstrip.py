import tkinter as tk
from tkinter import simpledialog
import json
import os

SAVE_FILE = "strips.json"

class FlightStripApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Strip Anzeige")
        self.strips = []
        self.strip_y = 10

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=10)

        self.add_button = tk.Button(root, text="Strip hinzufügen", command=self.add_strip)
        self.add_button.pack()

        self.canvas = tk.Canvas(root, width=700, height=600, bg="lightgrey", scrollregion=(0, 0, 700, 2000))
        self.canvas.pack(pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        control_frame = tk.Frame(root)
        control_frame.pack()
        tk.Button(control_frame, text="Speichern", command=self.save_strips).pack(side="left", padx=5)
        tk.Button(control_frame, text="Laden", command=self.load_strips).pack(side="left", padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.load_strips()

    def add_strip(self):
        text = self.entry.get()
        if not text:
            return
        if len(text) > 100:
            text = text[:100]

        self.create_strip(text)
        self.entry.delete(0, tk.END)

    def create_strip(self, text):
        strip_frame = tk.Frame(self.canvas, bg="white", bd=1, relief="solid")
        label = tk.Label(strip_frame, text=text, font=("Courier", 12), anchor="w", width=60, bg="white")
        label.pack(side="left", padx=5, pady=5)

        edit_btn = tk.Button(strip_frame, text="Bearbeiten", command=lambda: self.edit_strip(label))
        edit_btn.pack(side="right", padx=5)

        del_btn = tk.Button(strip_frame, text="Löschen", command=lambda: self.delete_strip(strip_frame, label))
        del_btn.pack(side="right")

        self.canvas.create_window(10, self.strip_y, anchor="nw", window=strip_frame)
        self.strip_y += 50
        self.strips.append((strip_frame, label))

    def delete_strip(self, frame, label):
        self.strips = [s for s in self.strips if s[0] != frame]
        frame.destroy()

    def edit_strip(self, label):
        new_text = simpledialog.askstring("Bearbeiten", "Neuer Text (max. 100 Zeichen):", initialvalue=label.cget("text"))
        if new_text:
            label.config(text=new_text[:100])

    def save_strips(self):
        texts = [label.cget("text") for (_, label) in self.strips]
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(texts, f, indent=2)
        print("✅ Strips gespeichert.")

    def load_strips(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                texts = json.load(f)
            for text in texts:
                self.create_strip(text)
            print("✅ Strips geladen.")
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")

    def on_close(self):
        self.save_strips()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlightStripApp(root)
    root.mainloop()
