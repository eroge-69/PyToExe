import tkinter as tk

APP_TITLE = "Kenetic Executer"
WINDOW_SIZE = (560, 320)  # width, height
BG_COLOR = "#0b0f14"      # near-black
FG_COLOR = "#3ea7ff"     # electric blue text


def center_window(root, w, h):
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")


def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)

    # Center the window
    center_window(root, *WINDOW_SIZE)

    # Big label that just says "Kenetic Executer"
    label = tk.Label(
        root,
        text=APP_TITLE,
        font=("Segoe UI", 28, "bold"),
        fg=FG_COLOR,
        bg=BG_COLOR
    )
    label.pack(expand=True)

    # Optional: set a minimal app icon on Windows if you have one (.ico)
    # root.iconbitmap("path_to_icon.ico")

    root.mainloop()


if __name__ == "__main__":
    main()
