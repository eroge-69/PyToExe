import tkinter as tk
from tkinter import messagebox
import webbrowser
import pyperclip
from PIL import ImageTk, Image
import os

class SocialSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wyszukiwarka Social Media")
        self.root.attributes("-fullscreen", True)

        self.platforms = {
            "YouTube": True,
            "Instagram": True,
            "TikTok": True,
            "Facebook": True,
            "Spotify": True,
            "Snapchat": True,
            "Pinterest": True
        }

        self.bg_color = "#a9cde3"
        self.fg_color = "#0c1f33"
        self.links_frame = None

        self.build_ui()
        self.apply_theme()

    def load_icon(self, filename, size=(48, 48)):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(script_dir, filename)
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Błąd ładowania ikony {filename}: {e}")
            return None

    def build_ui(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=20)

        self.entry = tk.Entry(self.top_frame, width=50, font=("Arial", 16))
        self.entry.pack(side=tk.LEFT, padx=10)

        search_icon = self.load_icon("search_icon.png")
        info_icon = self.load_icon("info_icon.png")          # Ikona przycisku informacji
        settings_icon = self.load_icon("settings_icon.png")
        close_icon = self.load_icon("close_icon.png")

        self.search_button = tk.Button(self.top_frame, image=search_icon, command=self.generate_links, bg="lightblue")
        self.search_button.image = search_icon
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.info_button = tk.Button(self.top_frame, image=info_icon, command=self.show_info, bg="lightgreen")
        self.info_button.image = info_icon
        self.info_button.pack(side=tk.LEFT, padx=5)

        self.settings_button = tk.Button(self.top_frame, image=settings_icon, command=self.open_settings, bg="gray")
        self.settings_button.image = settings_icon
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(self.top_frame, image=close_icon, command=self.root.destroy, bg="red")
        self.close_button.image = close_icon
        self.close_button.pack(side=tk.LEFT, padx=5)

        self.links_frame = tk.Frame(self.root)
        self.links_frame.pack(pady=20)

    def show_info(self):
        messagebox.showinfo("Informacje", "To jest wyszukiwarka Social Media.\nWpisz nazwę i kliknij lupę, aby wyszukać.")

    def generate_links(self):
        for widget in self.links_frame.winfo_children():
            widget.destroy()

        query = self.entry.get().strip()
        if not query:
            messagebox.showwarning("Błąd", "Wpisz nazwę do wyszukania.")
            return

        urls = {
            "YouTube": f"https://www.youtube.com/results?search_query={query}",
            "Instagram": f"https://www.instagram.com/{query}",
            "TikTok": f"https://www.tiktok.com/@{query}",
            "Facebook": f"https://www.facebook.com/search/top?q={query}",
            "Spotify": f"https://open.spotify.com/search/{query}",
            "Snapchat": f"https://www.snapchat.com/add/{query}",
            "Pinterest": f"https://www.pinterest.com/search/pins/?q={query}"
        }

        copy_icon = self.load_icon("copy_icon.png", size=(24, 24))

        for platform, url in urls.items():
            if self.platforms.get(platform):
                row = tk.Frame(self.links_frame, bg=self.bg_color)
                row.pack(pady=5, padx=10, anchor='w')

                label = tk.Label(row, text=platform + ":", font=("Arial", 14), bg=self.bg_color, fg=self.fg_color)
                label.pack(side=tk.LEFT, padx=5)

                link_label = tk.Label(row, text=url, font=("Arial", 12), fg="blue", cursor="hand2", bg=self.bg_color)
                link_label.pack(side=tk.LEFT)
                link_label.bind("<Button-1>", lambda e, url=url: webbrowser.open_new_tab(url))

                copy_button = tk.Button(
                    row,
                    image=copy_icon,
                    command=lambda url=url: self.copy_to_clipboard(url),
                    bg=self.bg_color,
                    bd=0,
                    highlightthickness=0,
                    activebackground=self.bg_color
                )
                copy_button.image = copy_icon
                copy_button.pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("Skopiowano", "Link został skopiowany do schowka.")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ustawienia")
        settings_window.geometry("400x400")
        settings_window.configure(bg=self.bg_color)

        tk.Label(settings_window, text="Wybierz platformy do wyszukiwania:", font=("Arial", 12),
                 bg=self.bg_color, fg=self.fg_color).pack(pady=10)

        checkboxes = {}
        for platform in self.platforms:
            var = tk.BooleanVar(value=self.platforms[platform])
            chk = tk.Checkbutton(settings_window, text=platform, variable=var, font=("Arial", 11),
                                 bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
            chk.pack(anchor='w', padx=20)
            checkboxes[platform] = var

        def save_settings():
            for platform, var in checkboxes.items():
                self.platforms[platform] = var.get()
            settings_window.destroy()

        save_button = tk.Button(settings_window, text="Zapisz", command=save_settings, font=("Arial", 12), bg="grey")
        save_button.pack(pady=20)

    def apply_theme(self):
        self.root.configure(bg=self.bg_color)
        self.top_frame.configure(bg=self.bg_color)
        self.links_frame.configure(bg=self.bg_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = SocialSearchApp(root)
    root.mainloop()
