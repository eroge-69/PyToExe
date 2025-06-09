import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class SliderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HS2 Facial Slider Tool")

        self.categories = {
            "Head": ["Width", "Height", "Depth"],
            "Eyes": ["Width", "Height", "Spacing", "Angle"],
            "Nose": ["Bridge Height", "Tip Size", "Nostril Width"],
            "Mouth": ["Width", "Upper Lip", "Lower Lip", "Depth"],
            "Jaw": ["Jaw Width", "Chin Length", "Jaw Depth"]
        }

        self.sliders = {}
        self.create_ui()

    def create_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        for cat, sliders in self.categories.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=cat)
            self.sliders[cat] = {}

            for i, name in enumerate(sliders):
                label = ttk.Label(frame, text=name)
                label.grid(row=i, column=0, padx=10, pady=5, sticky='w')

                scale = ttk.Scale(frame, from_=-100, to=100, orient='horizontal')
                scale.set(0)
                scale.grid(row=i, column=1, padx=10, pady=5)
                self.sliders[cat][name] = scale

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(btn_frame, text="Save Preset", command=self.save_preset)
        save_btn.grid(row=0, column=0, padx=10)

        load_btn = ttk.Button(btn_frame, text="Load Preset", command=self.load_preset)
        load_btn.grid(row=0, column=1, padx=10)

    def save_preset(self):
        preset = {cat: {name: slider.get() for name, slider in sliders.items()} for cat, sliders in self.sliders.items()}
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(preset, f, indent=4)
            messagebox.showinfo("Saved", "Preset saved successfully!")

    def load_preset(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'r') as f:
                preset = json.load(f)
                for cat, sliders in preset.items():
                    if cat in self.sliders:
                        for name, value in sliders.items():
                            if name in self.sliders[cat]:
                                self.sliders[cat][name].set(value)
            messagebox.showinfo("Loaded", "Preset loaded successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SliderApp(root)
    root.mainloop()
