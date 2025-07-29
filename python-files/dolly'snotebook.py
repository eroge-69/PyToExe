import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.constants import RIDGE
from PIL import Image, ImageTk  # ✨ For background images

# 🧁 Sweet pastel color palette
PASTEL_PINK = "#FFD1DC"
LIGHT_PINK = "#FFB6C1"
VERY_LIGHT_PINK = "#FFE4E1"
WHITE = "#FFFFFF"
DRK_PINK = "#FFCEDE"

class PastelNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("｡ﾟ•┈꒰ა ♡ ໒꒱┈•  ｡ﾟ₊˚ ✧ ━━━━꒰ა ♡ ໒꒱━━━━ ✧ ₊˚｡ﾟ•┈꒰ა ♡ ໒꒱┈•𝒹𝑜𝓁𝓁𝓎'𝓈 𝓃𝑜𝓉𝑒𝒷𝑜𝑜𝓀｡ﾟ₊˚ ✧ ━━━━꒰ა ♡ ໒꒱━━━━ ✧ ₊˚｡ﾟ•┈꒰♡")
        self.root.geometry("800x700")

        # 💖 Load and place background image
        bg_image = Image.open(r"C:\Users\raabi\OneDrive\Desktop\ｌｉｂｒａｒｙ\ｐｈｏｔｏｓ\dolly's notebook\background.png")
        bg_image = bg_image.resize((800, 700))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = tk.Label(self.root, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 💌 Create a pastel pink border frame
        self.border_frame = tk.Frame(root, bg=PASTEL_PINK, bd=0)
        self.border_frame.place(relx=0.5, rely=0.45, anchor="center", width=694, height=504)

        # 📝 Add text area inside the border frame
        self.text_area = tk.Text(self.border_frame,
                                 font=("Comic Sans MS", 12),
                                 fg="#FFBDD5",
                                 wrap=tk.WORD,
                                 insertbackground="#FF69B4",
                                 bd=0,
                                 relief=tk.FLAT)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 🎀 Buttons Frame (bottom for file actions)
        self.button_frame = tk.Frame(root, bg="#FFF0F5")
        self.button_frame.place(relx=0.5, rely=0.9, anchor="center")

        self.save_button = tk.Button(self.button_frame, text="💾 𝓈𝒶𝓋𝑒",
                                     command=self.save_file,
                                     font=("Comic Sans MS", 10,),
                                     fg="#FC90B8",
                                     bg="#FFF0F5",
                                     relief=RIDGE, activebackground=DRK_PINK, activeforeground=PASTEL_PINK)
        self.save_button.grid(row=0, column=0, padx=10)

        self.open_button = tk.Button(self.button_frame, text="📂 𝑜𝓅𝑒𝓃",
                                     command=self.open_file,
                                     font=("Comic Sans MS", 10,),
                                     fg="#FC90B8",
                                     bg="#FFF0F5",
                                     relief=RIDGE, activebackground=DRK_PINK, activeforeground=PASTEL_PINK)
        self.open_button.grid(row=0, column=1, padx=10)

        self.clear_button = tk.Button(self.button_frame, text="🧼 𝒸𝓁𝑒𝒶𝓇",
                                      command=self.clear_text,
                                      font=("Comic Sans MS", 10),
                                      fg="#FC90B8",
                                      bg="#FFF0F5",
                                      relief=RIDGE, activebackground=DRK_PINK, activeforeground=PASTEL_PINK)
        self.clear_button.grid(row=0, column=2, padx=10)

        # 🎀 Formatting Buttons Frame (top)
        self.format_frame = tk.Frame(root, bg="#FFF0F5")
        self.format_frame.place(relx=0.5, rely=0.05, anchor="n")

        pastel_btns = [
            ("←", self.decrease_indent),
            ("→", self.increase_indent),
            ("∙", self.insert_bullet),
            ("✓", self.insert_checklist),
            ("#", self.insert_numbered),
            ("𝒷𝑜𝓁𝒹", self.toggle_bold),
            ("𝒾𝓉𝒶𝓁𝒾𝒸", self.toggle_italic),
            ("𝓊𝓃𝒹𝑒𝓇𝓁𝒾𝓃𝑒", self.toggle_underline),
            ("𝓈𝓉𝓇𝒾𝓀𝑒𝓉𝒽𝓇𝓊", self.toggle_strikethrough),
        ]

        for (text, command) in pastel_btns:
            tk.Button(
                self.format_frame,
                text=text,
                command=command,
                font=("Comic Sans MS", 10),
                fg="#FC90B8",
                bg="#FFF0F5",
                relief=RIDGE, activebackground=DRK_PINK, activeforeground=WHITE,
                bd=1,
            ).pack(side="left", padx=4)

        # ✨ Tag styles
        self.text_area.tag_configure("bold", font=("Comic Sans MS", 12, "bold"))
        self.text_area.tag_configure("italic", font=("Comic Sans MS", 12, "italic"))
        self.text_area.tag_configure("underline", font=("Comic Sans MS", 12, "underline"))
        self.text_area.tag_configure("strikethrough", font=("Comic Sans MS", 12, "normal"), overstrike=1)

    # 🌷 Indent Functions
    def increase_indent(self):
        self.text_area.insert("insert", "    ")

    def decrease_indent(self):
        index = self.text_area.index("insert linestart")
        line = self.text_area.get(index, f"{index} lineend")
        if line.startswith("    "):
            self.text_area.delete(index, f"{index}+4c")

    # 🌷 List Functions
    def insert_bullet(self):
        self.text_area.insert("insert", "• ")

    def insert_checklist(self):
        self.text_area.insert("insert", "☐ ")

    def insert_numbered(self):
        self.text_area.insert("insert", "1. ")

    # 🌷 Toggle Style Functions
    def toggle_tag(self, tag_name):
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if tag_name in current_tags:
                self.text_area.tag_remove(tag_name, "sel.first", "sel.last")
            else:
                self.text_area.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass  # No selection

    def toggle_bold(self):
        self.toggle_tag("bold")

    def toggle_italic(self):
        self.toggle_tag("italic")

    def toggle_underline(self):
        self.toggle_tag("underline")

    def toggle_strikethrough(self):
        self.toggle_tag("strikethrough")

    # 🌼 File Functions
    def save_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(self.text_area.get(1.0, tk.END))
            self.show_custom_popup("𝓃𝑒𝓌 𝓃𝑜𝓉𝒾𝒻𝒾𝒸𝒶𝓉𝒾𝑜𝓃:", "🎀 𝓎𝑜𝓊𝓇 𝓃𝑜𝓉𝑒 𝓌𝒶𝓈 𝓈𝒶𝓋𝑒𝒹! 🎀")

    def open_file(self):
        file = filedialog.askopenfilename(defaultextension=".txt",
                                          filetypes=[("Text Files", "*.txt")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def show_custom_popup(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg="#FFF0F5")
        popup.geometry("300x150")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        # Load and show custom icon
        icon_img = Image.open(r"C:\Users\raabi\OneDrive\Desktop\ｌｉｂｒａｒｙ\ｐｈｏｔｏｓ\dolly's notebook\bow stamp.png").resize((40, 40))
        icon_photo = ImageTk.PhotoImage(icon_img)
        popup.icon_ref = icon_photo  # Prevent garbage collection

        icon_label = tk.Label(popup, image=icon_photo, bg="#FFF0F5")
        icon_label.pack(pady=(10, 5))

        msg_label = tk.Label(popup, text=message, font=("Comic Sans MS", 10),
                             fg="#FC90B8", bg="#FFF0F5")
        msg_label.pack()

        ok_button = tk.Button(popup, text="Okay", command=popup.destroy,
                              font=("Comic Sans MS", 10),
                              bg=PASTEL_PINK, fg=WHITE,
                              relief=RIDGE, activebackground=DRK_PINK, activeforeground=WHITE)
        ok_button.pack(pady=(10, 5))

        # 💗 Custom cursor setup
        self.root.config(cursor="none")  # Hide the default arrow cursor

        cursor_img = Image.open(r"C:\Users\raabi\OneDrive\Desktop\ｌｉｂｒａｒｙ\ｐｈｏｔｏｓ\dolly's notebook\cursor.png").resize((32, 32))
        self.cursor_photo = ImageTk.PhotoImage(cursor_img)

        self.cursor_label = tk.Label(self.root, image=self.cursor_photo, bg="transparent", bd=0)
        self.cursor_label.place(x=-100, y=-100)  # Hide off-screen initially

        self.root.bind("<Motion>", self.move_cursor)  # Track mouse motion


# 💖 Run the app!
if __name__ == "__main__":
    root = tk.Tk()
    app = PastelNotepad(root)
    root.mainloop()
