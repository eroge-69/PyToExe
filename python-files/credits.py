import tkinter as tk
from tkinter import ttk


CREDITS_TEXT24 = """\
Leandro Egger
Tim Lüthi
Zeyad Youssef
"""
CREDITS_TEXT25 = """\
Mael Zürcher
Yann Karlen
"""

def center_window(root, width=360, height=360):
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def make_ui(root):
    root.title("Credits")
    root.resizable(False, False)

    # Dark background
    bg_color = "#ddc9fc"
    title_color = "#494949"
    text_color = "#000000"
    btn_color = "#92d170"
    btn_hover = "#5c8347"

    root.configure(bg=bg_color)

    frm = tk.Frame(root, bg=bg_color, padx=16, pady=16)
    frm.pack(fill=tk.BOTH, expand=True)

    # Big text
    title = tk.Label(
        frm, text="Credits",
        font=("Helvetica", 18, "bold"),
        fg=title_color, bg=bg_color
    )
    title.pack(pady=(0, 8))

    title = tk.Label(
        frm, text="2024",
        font=("Helvetica", 14),
        fg=title_color, bg=bg_color
    )
    title.pack(pady=(0, 4))

    # Small text
    label = tk.Label(
        frm, text=CREDITS_TEXT24,
        justify=tk.CENTER,
        font=("Helvetica", 12),
        fg=text_color, bg=bg_color
    )
    label.pack(pady=(0, 16))


    title = tk.Label(
        frm, text="2025",
        font=("Helvetica", 14),
        fg=title_color, bg=bg_color
    )
    title.pack(pady=(0, 4))

    # Small text
    label = tk.Label(
        frm, text=CREDITS_TEXT25,
        justify=tk.CENTER,
        font=("Helvetica", 12),
        fg=text_color, bg=bg_color
    )
    label.pack(pady=(0, 16))
    # close button
    close_btn = tk.Button(
        frm, text="Schließen",
        command=root.destroy,
        font=("Helvetica", 11, "bold"),
        bg=btn_color, fg="white",
        activebackground=btn_hover,
        activeforeground="white",
        relief="flat", padx=12, pady=6
    )
    close_btn.pack()

    root.bind('<Escape>', lambda e: root.destroy())


def main():
    root = tk.Tk()
    center_window(root)
    make_ui(root)
    root.mainloop()


if __name__ == '__main__':
    main()