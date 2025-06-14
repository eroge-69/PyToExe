import tkinter as tk
from tkinter import ttk


class VenomRat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VenomRat v1.2")
        self.geometry("900x600")
        self.configure(bg="#2e2e2e")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.create_widgets()

    def create_widgets(self):
        top_bar = tk.Frame(self, bg="#2e2e2e")
        top_bar.pack(side="top", fill="x")

        title = tk.Label(top_bar, text="VenomRat v1.2", font=("Consolas", 18), fg="#00ff00", bg="#2e2e2e")
        title.pack(side="left", padx=(10,0), pady=10)

        big_tsu = tk.Label(top_bar, text="ツ", font=("Segoe UI Emoji", 48), fg="#00ff00", bg="#2e2e2e")
        big_tsu.pack(side="left", padx=(5,15), pady=5)

        troll_button = ttk.Menubutton(top_bar, text="TROLL", direction="below")
        troll_button.pack(side="right", padx=10, pady=10)

        troll_menu = tk.Menu(troll_button, tearoff=0)
        troll_menu.add_command(label="Mavi Ekran Göster", command=self.show_fake_blue_screen)
        troll_menu.add_command(label="sistem hacklendi", command=self.show_troll_v2)
        troll_button["menu"] = troll_menu

        self.terminal = tk.Text(self, bg="#111", fg="#0f0", font=("Consolas", 12))
        self.terminal.pack(expand=True, fill="both", padx=15, pady=15)
        self.terminal.insert(tk.END, "     ratı kullanmak icin @yuxalyinc e yazabilirsiniz\n")

    def make_fullscreen_window(self, color_bg):
        window = tk.Toplevel(self)
        window.overrideredirect(True)
        window.config(bg=color_bg)
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(f"{screen_width}x{screen_height}+0+0")
        window.lift()
        window.attributes("-topmost", True)
        window.focus_force()
        window.grab_set()
        window.bind("<Escape>", lambda e: window.destroy())
        return window

    def show_fake_blue_screen(self):
        bsod = self.make_fullscreen_window("#0000AA")

        message = (
            "\n\n\n"
            "A problem has been detected and Windows has been shut down to prevent damage\n"
            "to your computer.\n\n"
            "CRITICAL_PROCESS_DIED\n\n"
            "If this is the first time you've seen this Stop error screen,\n"
            "restart your computer. If this screen appears again, follow\n"
            "these steps:\n\n"
            "*** STOP: 0x000000EF (0x0000000000000000, 0x0000000000000000)\n\n"
            "Collecting error info... (100% complete)\n\n"
            "Press ESC to close this screen."
        )

        label = tk.Label(
            bsod,
            text=message,
            font=("Consolas", 16),
            fg="white",
            bg="#0000AA",
            justify="left"
        )
        label.pack(fill="both", expand=True)

    def show_troll_v2(self):
        troll_win = self.make_fullscreen_window("black")

        label = tk.Label(troll_win, text="Bilgisayarınız hacklendi!", font=("Consolas", 36, "bold"), fg="red", bg="black")
        label.pack(expand=True)

        def show_deleting_message():
            label.config(text="Sistem siliniyor...", fg="white", font=("Consolas", 32, "bold"))

        troll_win.after(3000, show_deleting_message)


if __name__ == "__main__":
    app = VenomRat()
    app.mainloop()
