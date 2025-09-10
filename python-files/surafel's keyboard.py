import tkinter as tk
from tkinter import messagebox

# --------------------------
# Amharic families (33 main letters)
# --------------------------
AMHARIC_FAMILIES = {
    "ሀ": ["ሀ","ሁ","ሂ","ሃ","ሄ","ህ","ሆ","ኋ"],
    "ለ": ["ለ","ሉ","ሊ","ላ","ሌ","ል","ሎ","ሏ"],
    "ሐ": ["ሐ","ሑ","ሒ","ሓ","ሔ","ሕ","ሖ","ሗ"],
    "መ": ["መ","ሙ","ሚ","ማ","ሜ","ም","ሞ","ሟ"],
    "ሠ": ["ሠ","ሡ","ሢ","ሣ","ሤ","ሥ","ሦ","ሧ"],
    "ረ": ["ረ","ሩ","ሪ","ራ","ሬ","ር","ሮ","ሯ"],
    "ሰ": ["ሰ","ሱ","ሲ","ሳ","ሴ","ስ","ሶ","ሷ"],
    "ሸ": ["ሸ","ሹ","ሺ","ሻ","ሼ","ሽ","ሾ","ሿ"],
    "ቀ": ["ቀ","ቁ","ቂ","ቃ","ቄ","ቅ","ቆ","ቈ"],
    "በ": ["በ","ቡ","ቢ","ባ","ቤ","ብ","ቦ","ቧ"],
    "ተ": ["ተ","ቱ","ቲ","ታ","ቴ","ት","ቶ","ቷ"],
    "ቸ": ["ቸ","ቹ","ቺ","ቻ","ቼ","ች","ቾ","ቿ"],
    "ኀ": ["ኀ","ኁ","ኂ","ኃ","ኄ","ኅ","ኆ","ኇ"],
    "ነ": ["ነ","ኑ","ኒ","ና","ኔ","ን","ኖ","ኗ"],
    "ኘ": ["ኘ","ኙ","ኚ","ኛ","ኜ","ኝ","ኞ","ኟ"],
    "አ": ["አ","ኡ","ኢ","ኣ","ኤ","እ","ኦ","ኧ"],
    "ከ": ["ከ","ኩ","ኪ","ካ","ኬ","ክ","ኮ","ኯ"],
    "ኸ": ["ኸ","ኹ","ኺ","ኻ","ኼ","ኽ","ኾ","ዀ"],
    "ወ": ["ወ","ዉ","ዊ","ዋ","ዌ","ው","ዎ","ዏ"],
    "ዐ": ["ዐ","ዑ","ዒ","ዓ","ዔ","ዕ","ዖ","዗"],
    "ዘ": ["ዘ","ዙ","ዚ","ዛ","ዜ","ዝ","ዞ","ዟ"],
    "ዠ": ["ዠ","ዡ","ዢ","ዣ","ዤ","ዥ","ዦ","ዧ"],
    "የ": ["የ","ዩ","ዪ","ያ","ዬ","ይ","ዮ","ዯ"],
    "ደ": ["ደ","ዱ","ዲ","ዳ","ዴ","ድ","ዶ","ዷ"],
    "ዸ": ["ዸ","ዹ","ዺ","ዻ","ዼ","ዽ","ዾ","ዿ"],
    "ጀ": ["ጀ","ጁ","ጂ","ጃ","ጄ","ጅ","ጆ","ጇ"],
    "ገ": ["ገ","ጉ","ጊ","ጋ","ጌ","ግ","ጎ","ጏ"],
    "ጘ": ["ጘ","ጙ","ጚ","ጛ","ጜ","ጝ","ጞ","ጟ"],
    "ጠ": ["ጠ","ጡ","ጢ","ጣ","ጤ","ጥ","ጦ","ጧ"],
    "ጨ": ["ጨ","ጩ","ጪ","ጫ","ጬ","ጭ","ጮ","ጯ"],
    "ጰ": ["ጰ","ጱ","ጲ","ጳ","ጴ","ጵ","ጶ","ጷ"],
    "ጸ": ["ጸ","ጹ","ጺ","ጻ","ጼ","ጽ","ጾ","ጿ"],
}

PUNCTUATION = ["፡", "።", "፣", "፤", "፥", "፦", "፧", "፨"]
ENGLISH = [chr(i) for i in range(65, 91)]
NUMBERS_SYMBOLS = ["1","2","3","4","5","6","7","8","9","0","!","@","#","$","%","&","*","(",")"]

# --------------------------
class AmharicKeyboard:
    def __init__(self, root, btn_width=6, btn_height=2):
        self.root = root
        self.root.title("Surafel Wolde's Keyboard")
        self.root.geometry("1000x400")
        self.root.resizable(True, True)
        self.btn_width = btn_width
        self.btn_height = btn_height

        self.textbox = tk.Text(root, height=5, font=("Noto Sans Ethiopic", 16), bg="#1e1e1e", fg="white")
        self.textbox.pack(fill="x", padx=5, pady=5)

        # Top bar
        top_frame = tk.Frame(root, bg="#1e1e1e")
        top_frame.pack(fill="x")

        self.send_btn = tk.Button(top_frame, text="Send → Paste", command=self.send_to_clipboard,
                                  width=12, height=2, bg="#555", fg="white")
        self.send_btn.pack(side="left", padx=2, pady=2)

        self.copy_btn = tk.Button(top_frame, text="📋 Copy", command=self.copy_to_clipboard,
                                  width=8, height=2, bg="#008CBA", fg="white")
        self.copy_btn.pack(side="left", padx=2, pady=2)

        self.layout_var = tk.StringVar(value="AMHARIC")
        tk.OptionMenu(top_frame, self.layout_var, "AMHARIC", "ENGLISH", "NUMBERS", command=self.switch_layout).pack(side="left", padx=5)

        self.keyboard_frame = tk.Frame(root, bg="#1e1e1e")
        self.keyboard_frame.pack(expand=True, fill="both")

        self.load_main_keys()

    # --------------------------
    def load_main_keys(self):
        self.clear_keys()
        keys = list(AMHARIC_FAMILIES.keys())
        # Arrange main keys in grid
        rows = []
        temp_row = []
        for i, key in enumerate(keys, 1):
            temp_row.append(key)
            if i % 8 == 0:  # 8 keys per row
                rows.append(temp_row)
                temp_row = []
        if temp_row:
            rows.append(temp_row)

        for row_keys in rows:
            frame = tk.Frame(self.keyboard_frame, bg="#1e1e1e")
            frame.pack(pady=2)
            for key in row_keys:
                btn = tk.Button(frame, text=key, width=self.btn_width, height=self.btn_height,
                                command=lambda val=key: self.show_family(val),
                                bg="#333", fg="white", relief="flat")
                btn.pack(side="left", padx=2)
        self.create_bottom_row(PUNCTUATION)

    def show_family(self, family_key):
        self.clear_bottom_row()
        family = AMHARIC_FAMILIES.get(family_key, [])
        self.create_bottom_row(family)

    def reset_to_punctuation(self, event=None):
        self.clear_bottom_row()
        self.create_bottom_row(PUNCTUATION)

    def create_bottom_row(self, keys):
        self.bottom_frame = tk.Frame(self.keyboard_frame, bg="#1e1e1e")
        self.bottom_frame.pack(side="top", pady=5)
        for key in keys:
            btn = tk.Button(self.bottom_frame, text=key, width=self.btn_width, height=self.btn_height,
                            command=lambda val=key: self.textbox.insert("end", val),
                            bg="#444", fg="white", relief="flat")
            btn.pack(side="left", padx=2)

        space_btn = tk.Button(self.bottom_frame, text="Space", width=self.btn_width*2, height=self.btn_height,
                              command=lambda: [self.textbox.insert("end", " "), self.reset_to_punctuation()],
                              bg="#666", fg="white")
        space_btn.pack(side="left", padx=2)

        clear_btn = tk.Button(self.bottom_frame, text="Clear", width=self.btn_width*2, height=self.btn_height,
                              command=lambda: self.textbox.delete("1.0", "end"),
                              bg="#a00", fg="white")
        clear_btn.pack(side="left", padx=2)

    def clear_keys(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

    def clear_bottom_row(self):
        if hasattr(self, "bottom_frame") and self.bottom_frame.winfo_exists():
            self.bottom_frame.destroy()

    def send_to_clipboard(self):
        text = self.textbox.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Text copied! Now press Ctrl+V in Word/Excel/PowerPoint.")

    def copy_to_clipboard(self):
        text = self.textbox.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("Copied", "Copied to clipboard!")

    def switch_layout(self, choice):
        self.clear_keys()
        if choice == "AMHARIC":
            self.load_main_keys()
        elif choice == "ENGLISH":
            # arrange in multiple rows
            row_size = 10
            for i in range(0, len(ENGLISH), row_size):
                frame = tk.Frame(self.keyboard_frame, bg="#1e1e1e")
                frame.pack(pady=2)
                for key in ENGLISH[i:i+row_size]:
                    btn = tk.Button(frame, text=key, width=self.btn_width, height=self.btn_height,
                                    command=lambda val=key: self.textbox.insert("end", val),
                                    bg="#333", fg="white", relief="flat")
                    btn.pack(side="left", padx=2)
            self.create_bottom_row([".",",","?","!"])
        elif choice == "NUMBERS":
            frame = tk.Frame(self.keyboard_frame, bg="#1e1e1e")
            frame.pack(pady=2)
            for key in NUMBERS_SYMBOLS:
                btn = tk.Button(frame, text=key, width=self.btn_width, height=self.btn_height,
                                command=lambda val=key: self.textbox.insert("end", val),
                                bg="#333", fg="white", relief="flat")
                btn.pack(side="left", padx=2)
            self.create_bottom_row(["+", "-", "/", "*", "="])

# -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AmharicKeyboard(root, btn_width=6, btn_height=2)
    root.mainloop()
