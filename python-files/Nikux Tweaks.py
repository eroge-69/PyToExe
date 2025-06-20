import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class NikuxTweaksApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nikux Tweaks")
        self.geometry("900x600")
        self.resizable(False, False)

        # Sidebar con solo el icono de configuración
        self.sidebar = ctk.CTkFrame(self, width=70)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkButton(self.sidebar, text="⚙️", width=50, height=50, fg_color="transparent", hover_color="#333", command=self.open_settings).pack(pady=10)

        # Header con logo y título
        self.header = ctk.CTkFrame(self, height=80)
        self.header.pack(fill="x")
        try:
            logo_img = Image.open("logo.png").resize((60, 60))
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ctk.CTkLabel(self.header, image=self.logo_photo, text="")
            logo_label.pack(side="left", padx=20)
        except Exception as e:
            logo_label = ctk.CTkLabel(self.header, text="[Logo]", font=ctk.CTkFont(size=32, weight="bold"))
            logo_label.pack(side="left", padx=20)
        ctk.CTkLabel(self.header, text="Nikux Tweaks", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left", padx=15)
        ctk.CTkButton(self.header, text="Crear Punto de Restauración", command=self.create_restore_point, fg_color="#516bff").pack(side="right", padx=20, pady=10)

        # Área principal scrollable
        self.content = ctk.CTkScrollableFrame(self, width=800)
        self.content.pack(padx=10, pady=10, fill="both", expand=True)

        # Opciones de tweaks
        self.tweaks = [
            {
                "name": "Desactivar Memory Compression",
                "desc": "Desactiva la compresión de memoria para mejorar rendimiento en sistemas con RAM suficiente y reducir uso de CPU.",
                "var": ctk.BooleanVar(),
                "func": self.disable_memory_compression
            },
            {
                "name": "Desactivar Page Combining",
                "desc": "Desactiva la combinación de páginas para mejorar la respuesta del sistema en algunos escenarios.",
                "var": ctk.BooleanVar(),
                "func": self.disable_page_combining
            },
            {
                "name": "Activar Large System Cache",
                "desc": "Aumenta la caché del sistema para mejorar la velocidad de acceso a datos en disco.",
                "var": ctk.BooleanVar(),
                "func": self.enable_large_system_cache
            },
            {
                "name": "Desactivar Paging Executive",
                "desc": "Evita que el kernel se pagine a disco, mejora rendimiento pero puede afectar estabilidad.",
                "var": ctk.BooleanVar(),
                "func": self.disable_paging_executive
            },
            {
                "name": "Activar Modo Juego de Windows",
                "desc": "Prioriza recursos para juegos, mejorando FPS y estabilidad.",
                "var": ctk.BooleanVar(),
                "func": self.enable_game_mode
            },
            {
                "name": "Desactivar efectos visuales innecesarios",
                "desc": "Reduce efectos visuales para liberar recursos y mejorar FPS.",
                "var": ctk.BooleanVar(),
                "func": self.disable_visual_effects
            },
            {
                "name": "Optimizar TCP para menor ping",
                "desc": "Ajusta parámetros de red para reducir latencia en juegos online.",
                "var": ctk.BooleanVar(),
                "func": self.optimize_tcp
            },
            {
                "name": "Desactivar actualizaciones automáticas temporales",
                "desc": "Evita que Windows descargue actualizaciones mientras juegas, para no consumir recursos.",
                "var": ctk.BooleanVar(),
                "func": self.disable_windows_update_temporarily
            }
        ]

        # Tarjetas de opciones
        for i, tweak in enumerate(self.tweaks):
            card = ctk.CTkFrame(self.content, border_width=1, border_color="#444", corner_radius=8)
            card.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
            ctk.CTkLabel(card, text=tweak["name"], font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10,0), padx=10)
            ctk.CTkLabel(card, text=tweak["desc"], wraplength=350, justify="left").pack(anchor="w", padx=10, pady=(0,10))
            ctk.CTkSwitch(card, text="Activar", variable=tweak["var"]).pack(anchor="w", padx=10, pady=(0,10))

        ctk.CTkButton(self, text="Aplicar seleccionados", command=self.apply_selected, fg_color="#2266bb").pack(pady=15)

    def create_restore_point(self):
        try:
            subprocess.run([
                "powershell", "-Command",
                "Checkpoint-Computer -Description 'NikuxTweaksRestorePoint' -RestorePointType 'MODIFY_SETTINGS'"
            ], check=True)
            messagebox.showinfo("Punto de restauración", "Punto de restauración creado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el punto de restauración.\n{e}")

    def disable_memory_compression(self):
        subprocess.run([
            "powershell", "-Command",
            "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management' -Name 'Compression' -Value 0"
        ], shell=True)

    def disable_page_combining(self):
        subprocess.run([
            "sc", "config", "SysMain", "start= disabled"
        ], shell=True)

    def enable_large_system_cache(self):
        subprocess.run([
            "reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management",
            "/v", "LargeSystemCache", "/t", "REG_DWORD", "/d", "1", "/f"
        ], shell=True)

    def disable_paging_executive(self):
        subprocess.run([
            "reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management",
            "/v", "DisablePagingExecutive", "/t", "REG_DWORD", "/d", "1", "/f"
        ], shell=True)

    def enable_game_mode(self):
        subprocess.run([
            "powershell", "-Command",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AllowAutoGameMode' -Value 1"
        ], shell=True)

    def disable_visual_effects(self):
        subprocess.run([
            "powershell", "-Command",
            "(Get-ItemProperty 'HKCU:\\Control Panel\\Desktop\\WindowMetrics').MinAnimate = 0; " +
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'UserPreferencesMask' -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00))"
        ], shell=True)

    def optimize_tcp(self):
        commands = [
            "netsh interface tcp set global autotuninglevel=disabled",
            "netsh interface tcp set global chimney=enabled",
            "netsh interface tcp set global congestionprovider=ctcp"
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True)

    def disable_windows_update_temporarily(self):
        subprocess.run([
            "powershell", "-Command",
            "UsoClient StartScan"
        ], shell=True)
        # Para pausar updates de verdad, se recomienda hacerlo manualmente o con políticas de grupo.

    def apply_selected(self):
        if messagebox.askyesno("Confirmar", "¿Deseas aplicar las optimizaciones seleccionadas? Se recomienda crear un punto de restauración primero."):
            for tweak in self.tweaks:
                if tweak["var"].get():
                    try:
                        tweak["func"]()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error aplicando {tweak['name']}:\n{e}")
            messagebox.showinfo("Listo", "Optimización aplicada. Reinicia el PC para ver los cambios.")

    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Configuración")
        settings_window.geometry("300x150")
        settings_window.resizable(False, False)

        ctk.CTkLabel(settings_window, text="Tema de la aplicación:", font=ctk.CTkFont(size=14)).pack(pady=15)
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode().lower())
        def set_theme():
            ctk.set_appearance_mode(theme_var.get())
        ctk.CTkRadioButton(settings_window, text="Claro", variable=theme_var, value="light", command=set_theme).pack()
        ctk.CTkRadioButton(settings_window, text="Oscuro", variable=theme_var, value="dark", command=set_theme).pack()

if __name__ == "__main__":
    app = NikuxTweaksApp()
    app.mainloop()
