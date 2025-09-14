import os
import subprocess
import customtkinter as ctk
from tkinter import messagebox
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])

    # Forcer pythonw.exe (à ajuster selon ton install Python)
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")

    ctypes.windll.shell32.ShellExecuteW(None, "runas", pythonw, f'"{script}" {params}', None, 1)
    sys.exit()

FOLDER_NAME = "Download File"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALL_FOLDER = os.path.join(SCRIPT_DIR, FOLDER_NAME)


class CustomTitleBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=30, fg_color="#2b2b2b")
        self.pack(fill="x")
        self.master = master

        self.close_button = ctk.CTkButton(
            self, text="✕", width=30, height=30,
            fg_color="#2b2b2b", hover_color="#ff3c3c",
            text_color="white", command=self.master.animated_close,
            corner_radius=5, border_width=0
        )
        self.close_button.pack(side="right", padx=5, pady=0)


class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # === Config fenêtre ===
        self.overrideredirect(True)
        self.geometry("800x550")
        self.attributes("-topmost", True)
        self.configure(fg_color="#1e1e1e")
        self.center_window(800, 550)
        self.attributes("-alpha", 1.0)

        self.title_bar = CustomTitleBar(self)

        self.checkbox_widgets = []

        self.main_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True)

        self.build_ui()

        self.animated_open()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def build_ui(self):
        title = ctk.CTkLabel(self.main_frame, text="Programmes disponibles à l'installation",
                             text_color="white", font=ctk.CTkFont(size=16, weight="bold"),
                             fg_color="#1e1e1e")
        title.pack(pady=(20, 10))

        self.scroll_container = ctk.CTkScrollableFrame(self.main_frame, width=760, height=350, fg_color="#1e1e1e")
        self.scroll_container.pack(padx=20, pady=10, fill="both", expand=True)

        if not os.path.exists(INSTALL_FOLDER):
            messagebox.showerror("Erreur", f"Dossier introuvable : {INSTALL_FOLDER}")
            self.destroy()
            return

        exe_msi_files = [f for f in os.listdir(INSTALL_FOLDER) if f.lower().endswith((".exe", ".msi"))]
        if not exe_msi_files:
            messagebox.showinfo("Information", "Aucun fichier .exe ou .msi trouvé dans le dossier.")
            self.destroy()
            return

        self.checkbox_widgets.clear()

        for file in exe_msi_files:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                self.scroll_container,
                text=file,
                variable=var,
                fg_color="green",  # vert
                border_color="orange",
                text_color="white",
                font=ctk.CTkFont(size=12),
                corner_radius=15,
                checkbox_width=20,
                checkbox_height=20,
                border_width=2,
                width=720,
                height=30
            )
            cb.pack(padx=10, pady=5, fill="x")
            self.checkbox_widgets.append((file, var, cb))

        self.toggle_button = ctk.CTkButton(self.main_frame, text="Tout désélectionner",
                                           command=self.toggle_all,
                                           fg_color="#2351CE", hover_color="#386AF3",
                                           text_color="white", font=ctk.CTkFont(size=11),
                                           corner_radius=5)
        self.toggle_button.pack(pady=(5, 5))

        install_button = ctk.CTkButton(self.main_frame, text="Installer la sélection",
                                       command=self.install_selected,
                                       fg_color="#28a745", hover_color="#218838",
                                       text_color="white", font=ctk.CTkFont(size=12),
                                       corner_radius=5)
        install_button.pack(pady=(0, 10))

        self.status_label = ctk.CTkLabel(self.main_frame,
                                         text="Statut : prêt",
                                         text_color="#bbbbbb", fg_color="#1e1e1e",
                                         font=ctk.CTkFont(size=10, slant="italic"))
        self.status_label.pack(pady=(5, 15))

    def toggle_all(self):
        all_checked = all(var.get() for _, var, _ in self.checkbox_widgets)
        new_state = not all_checked
        for _, var, _ in self.checkbox_widgets:
            var.set(new_state)
        btn_text = "Tout désélectionner" if new_state else "Tout sélectionner"
        self.toggle_button.configure(text=btn_text)

    def install_selected(self):
        selected = [file for file, var, _ in self.checkbox_widgets if var.get()]
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un programme à installer.")
            return
        self.status_label.configure(text="Installation en cours...")
        self.update()

        for file in selected:
            fullpath = os.path.join(INSTALL_FOLDER, file)
            try:
                subprocess.run([fullpath], check=True)
                self.status_label.configure(text=f"Installation terminée : {file}")
                self.update()
            except subprocess.CalledProcessError:
                messagebox.showerror("Erreur", f"Erreur pendant l'installation de {file}")
                self.status_label.configure(text=f"Erreur sur : {file}")
                return

        self.status_label.configure(text="Toutes les installations terminées.")

    def animated_open(self):
        def step(alpha, scale):
            if alpha >= 1:
                self.attributes("-alpha", 1.0)
                self.center_window(800, 550)
                return
            self.attributes("-alpha", min(alpha, 1.0))
            width = int(800 * scale)
            height = int(550 * scale)
            self.center_window(width, height)
            self.after(5, lambda: step(alpha + 0.3, scale + 0.06))

        self.attributes("-alpha", 0.0)
        step(0.0, 0.9)

    def animated_close(self):
        def step(alpha, scale):
            if alpha <= 0:
                self.destroy()
                return
            self.attributes("-alpha", max(alpha, 0))
            width = int(800 * scale)
            height = int(550 * scale)
            self.center_window(width, height)
            self.after(5, lambda: step(alpha - 0.3, scale - 0.06))

        step(1.0, 1.0)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = InstallerApp()
    app.mainloop()
