
import tkinter as tk
from tkinter import filedialog, font, messagebox, ttk
import os

class KeyboardASMRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyboard ASMR Therapy")
        self.root.geometry("900x600")

        self.default_text = """Mommy Duck lived on a farm. In her nest, she had five little eggs and one big egg. One day, the five little eggs started to crack. Tap, tap, tap! Five pretty, yellow baby ducklings came out.

Then the big egg started to crack. Bang, bang, bang! One big, ugly duckling came out. “That’s strange”, thought Mummy Duck.

Nobody wanted to play with him. “Go away”, said his brothers and sisters. “You’re ugly!” The ugly duckling was sad. So he went to find some new friends.

“Go away” said the pig! “Go away” said the sheep! “Go away” said the cow! “Go away” said the horse!

No one wanted to be his friend. It started to get cold. It started to snow! The ugly duckling found an empty barn and lived there. He was cold, sad and alone. Then spring came. The ugly duckling left the barn and went back to the pond.

He was very thirsty and put his beak into the water. He saw a beautiful, white bird! “Wow” he said. “Who’s that?”

“It’s you”, said another beautiful, white bird.

“Me? But I’m an ugly duckling.”

“Not any more. You’re a beautiful swan, like me. Do you want to be my friend?”

“Yes”, he smiled.

All the other animals watched as the two swans flew away, friends forever."""

        self.current_index = 0
        self.font_dir = "fonts"
        os.makedirs(self.font_dir, exist_ok=True)

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        title = tk.Label(self.root, text="Keyboard ASMR Therapy", font=("Helvetica", 18, "bold"))
        title.pack(pady=10)

        top_frame = tk.Frame(self.root)
        top_frame.pack()

        # Language
        self.language = tk.StringVar(value="English")
        tk.OptionMenu(top_frame, self.language, "English", "Persian", command=self.set_direction).pack(side="left", padx=5)

        # Font Style
        self.font_style = tk.StringVar(value="normal")
        tk.OptionMenu(top_frame, self.font_style, "normal", "bold", "italic", "underline", command=lambda e=None: self.update_font()).pack(side="left", padx=5)

        # Font Size
        self.font_size = tk.IntVar(value=16)
        tk.Spinbox(top_frame, from_=8, to=48, textvariable=self.font_size, command=self.update_font, width=5).pack(side="left", padx=5)

        # Font Family
        self.font_family = tk.StringVar(value="Helvetica")
        self.font_menu = ttk.Combobox(top_frame, textvariable=self.font_family, values=self.get_fonts())
        self.font_menu.pack(side="left", padx=5)
        self.font_menu.bind("<<ComboboxSelected>>", lambda e: self.update_font())

        # Add/Remove Fonts
        tk.Button(top_frame, text="Add Font", command=self.add_font).pack(side="left", padx=5)
        tk.Button(top_frame, text="Remove Font", command=self.remove_font).pack(side="left", padx=5)

        # Image
        self.image_label = tk.Label(self.root, text="No image selected", fg="gray")
        self.image_label.pack()
        tk.Button(self.root, text="Load Image", command=self.load_image).pack()

        # Text Box
        self.text_box = tk.Text(self.root, height=15, wrap="word", fg="gray")
        self.text_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_box.bind("<Key>", self.check_typing)

        self.set_direction()

    def get_fonts(self):
        system_fonts = list(font.families())
        custom_fonts = [f.replace(".ttf", "") for f in os.listdir(self.font_dir) if f.endswith(".ttf")]
        return sorted(set(system_fonts + custom_fonts))

    def add_font(self):
        file = filedialog.askopenfilename(filetypes=[("Font files", "*.ttf *.otf")])
        if file:
            name = os.path.basename(file)
            dest = os.path.join(self.font_dir, name)
            with open(file, "rb") as fsrc, open(dest, "wb") as fdst:
                fdst.write(fsrc.read())
            messagebox.showinfo("Font Added", f"{name} added successfully.")
            self.font_menu["values"] = self.get_fonts()

    def remove_font(self):
        fname = self.font_family.get() + ".ttf"
        fpath = os.path.join(self.font_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            messagebox.showinfo("Removed", f"{fname} removed.")
            self.font_menu["values"] = self.get_fonts()

    def update_font(self):
        f = self.font_family.get()
        size = self.font_size.get()
        style = self.font_style.get()
        actual_font = (f, size, style if style != "normal" else "")
        self.text_box.config(font=actual_font)

    def load_image(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp")])
        if file:
            self.image_label.config(text=f"Image: {os.path.basename(file)}", fg="black")

    def set_direction(self, *args):
        if self.language.get() == "Persian":
            self.text_box.config(justify="right")
        else:
            self.text_box.config(justify="left")

    def update_display(self):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", self.default_text)
        self.text_box.tag_add("faded", "1.0", "end")
        self.text_box.tag_config("faded", foreground="#cccccc")
        self.text_box.tag_config("typed", foreground="#000000")
        self.text_box.tag_config("wrong", foreground="red")
        self.update_font()

    def check_typing(self, event):
        char = event.char
        if len(char) == 0 or ord(char) in (8, 13):  # ignore control keys
            return
        if self.current_index >= len(self.default_text):
            return "break"

        expected = self.default_text[self.current_index]
        if char == expected:
            self.text_box.tag_add("typed", f"1.0 + {self.current_index} chars", f"1.0 + {self.current_index+1} chars")
            self.current_index += 1
        else:
            self.text_box.tag_add("wrong", f"1.0 + {self.current_index} chars", f"1.0 + {self.current_index+1} chars")

        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyboardASMRApp(root)
    root.mainloop()
