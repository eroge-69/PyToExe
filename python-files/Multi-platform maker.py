import tkinter as tk
from tkinter import messagebox
import webbrowser

PASSWORD = "Bangladesh1971"

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Secure Multi-platform Mobile Number Search")
        self.geometry("450x350")
        self.configure(bg="#121212")  # Dark background

        # Initially hide main UI, show login UI
        self.main_frame = None
        self.login_frame = None
        self.create_login_ui()

    def create_login_ui(self):
        self.login_frame = tk.Frame(self, bg="#121212")
        self.login_frame.pack(expand=True, fill="both")

        label = tk.Label(self.login_frame, text="Enter Password", font=("Consolas", 18), fg="#00FF00", bg="#121212")
        label.pack(pady=(40, 10))

        self.password_entry = tk.Entry(self.login_frame, font=("Consolas", 16), fg="#00FF00", bg="#000000", insertbackground="#00FF00", show="*")
        self.password_entry.pack(pady=10, ipadx=10, ipady=5)
        self.password_entry.focus()

        btn = tk.Button(self.login_frame, text="Login", font=("Consolas", 14), bg="#006400", fg="white", activebackground="#00AA00", command=self.check_password)
        btn.pack(pady=20, ipadx=10, ipady=5)

    def check_password(self):
        entered = self.password_entry.get()
        if entered == PASSWORD:
            self.login_frame.destroy()
            self.create_main_ui()
        else:
            messagebox.showerror("Access Denied", "Incorrect Password. Try again.")
            self.password_entry.delete(0, tk.END)

    def create_main_ui(self):
        self.main_frame = tk.Frame(self, bg="#121212")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        title_label = tk.Label(self.main_frame, text="Multi-platform Mobile Number Search", font=("Consolas", 16, "bold"), fg="#00FF00", bg="#121212")
        title_label.pack(pady=(0, 20))

        number_label = tk.Label(self.main_frame, text="Enter Mobile Number (with country code):", font=("Consolas", 12), fg="#00FF00", bg="#121212")
        number_label.pack(anchor="w")

        self.entry = tk.Entry(self.main_frame, font=("Consolas", 14), fg="#00FF00", bg="#000000", insertbackground="#00FF00")
        self.entry.pack(fill="x", pady=5)

        search_btn = tk.Button(self.main_frame, text="Search", font=("Consolas", 14), bg="#006400", fg="white", activebackground="#00AA00", command=self.search)
        search_btn.pack(pady=15, ipadx=10, ipady=5)

        self.frame_results = tk.Frame(self.main_frame, bg="#121212")
        self.frame_results.pack(fill="both", expand=True)

    def open_link(self, url):
        webbrowser.open(url)

    def search(self):
        number = self.entry.get().strip()
        if not number:
            messagebox.showwarning("Warning", "Please enter a mobile number")
            return

        # URLs for search
        truecaller_url = f"https://www.truecaller.com/search/in/phone-number/{number}"
        facebook_search_url = f"https://www.facebook.com/search/top/?q={number}"
        google_search_url = f"https://www.google.com/search?q={number}"
        whatsapp_url = f"https://wa.me/{number}"

        # Clear previous buttons
        for widget in self.frame_results.winfo_children():
            widget.destroy()

        # Create buttons with hacker-style colors
        btn_truecaller = tk.Button(self.frame_results, text="Search Truecaller", font=("Consolas", 12), fg="#00FF00", bg="#000000", activebackground="#003300",
                                   command=lambda: self.open_link(truecaller_url))
        btn_truecaller.pack(pady=5, fill='x')

        btn_facebook = tk.Button(self.frame_results, text="Search Facebook", font=("Consolas", 12), fg="#00FF00", bg="#000000", activebackground="#003300",
                                 command=lambda: self.open_link(facebook_search_url))
        btn_facebook.pack(pady=5, fill='x')

        btn_google = tk.Button(self.frame_results, text="Search Google", font=("Consolas", 12), fg="#00FF00", bg="#000000", activebackground="#003300",
                               command=lambda: self.open_link(google_search_url))
        btn_google.pack(pady=5, fill='x')

        btn_whatsapp = tk.Button(self.frame_results, text="Open WhatsApp Chat", font=("Consolas", 12), fg="#00FF00", bg="#000000", activebackground="#003300",
                                 command=lambda: self.open_link(whatsapp_url))
        btn_whatsapp.pack(pady=5, fill='x')


if __name__ == "__main__":
    app = App()
    app.mainloop()
