import tkinter as tk
from tkinter import ttk

class PianoSheetDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Roblox Piano Sheet Display")
        self.root.geometry("600x400")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")

        # Font size variable
        self.font_size = tk.IntVar(value=18)

        # Frame for settings
        settings_frame = tk.Frame(self.root, bg="#1e1e1e")
        settings_frame.pack(fill="x", pady=5)

        # Font size label
        font_label = tk.Label(settings_frame, text="Font Size:", fg="white", bg="#1e1e1e")
        font_label.pack(side="left", padx=(10, 5))

        # Font size entry
        font_entry = ttk.Entry(settings_frame, textvariable=self.font_size, width=5)
        font_entry.pack(side="left", padx=5)

        # Apply button
        apply_button = ttk.Button(settings_frame, text="Apply", command=self.update_font)
        apply_button.pack(side="left", padx=5)

        # Textbox for piano sheet display
        self.textbox = tk.Text(
            self.root,
            wrap="word",
            fg="white",
            bg="#252526",
            insertbackground="white",
            font=("Consolas", self.font_size.get())
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Start the app
        self.root.mainloop()

    def update_font(self):
        try:
            new_size = int(self.font_size.get())
            self.textbox.config(font=("Consolas", new_size))
        except ValueError:
            pass

if __name__ == "__main__":
    PianoSheetDisplay()
