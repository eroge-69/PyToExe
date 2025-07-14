import customtkinter as ctk
import subprocess
import os
import requests
import zipfile
import shutil

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(APP_DIR, "descargas")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

URLS = {
    "Pulse": "https://inelcom.synology.me:4444/pulse.rar",
    "Gesco": "https://gesco.inelcom.com/setup/publish.htm",
    "AnyDesk": "https://download.anydesk.com/AnyDesk.exe",
    "Bastionado": "https://inelcom.synology.me:4444/Bastionado_Inelcom_v4.0.5.rar"
}

def descargar(nombre):
    url = URLS[nombre]
    destino = os.path.join(DOWNLOAD_DIR, f"{nombre}.exe" if nombre != "Pulse" and nombre != "Bastionado" else f"{nombre}.rar")
    r = requests.get(url, allow_redirects=True, verify=False)
    with open(destino, "wb") as f:
        f.write(r.content)
    return destino

def instalar(nombre):
    if nombre == "Pulse":
        rar_path = descargar("Pulse")
        pulse_folder = os.path.join(DOWNLOAD_DIR, "pulse_extraido")
        os.makedirs(pulse_folder, exist_ok=True)
        # Extraer con WinRAR
        winrar = r"C:\Program Files\WinRAR\WinRAR.exe"
        if os.path.exists(winrar):
            subprocess.run([winrar, "x", "-o+", rar_path, pulse_folder], check=True)
            # Buscar .exe
            for file in os.listdir(pulse_folder):
                if file.endswith(".exe"):
                    subprocess.run(["powershell", "Start-Process", "-Verb", "RunAs", os.path.join(pulse_folder, file)])
        else:
            app.log("❌ WinRAR no encontrado. No se pudo extraer Pulse.")
    elif nombre == "Bastionado":
        rar_path = descargar("Bastionado")
        app.log(f"✅ Bastionado descargado: {rar_path}\nEjecuta manualmente cuando quieras.")
    else:
        exe_path = descargar(nombre)
        subprocess.run(["powershell", "Start-Process", "-Verb", "RunAs", exe_path])

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instalador Inelcom")
        self.geometry("500x400")

        ctk.CTkLabel(self, text="Instalador Inelcom", font=("Arial", 22)).pack(pady=10)

        ctk.CTkButton(self, text="Instalar TODO (excepto Bastionado)", command=self.instalar_todo).pack(pady=10)

        ctk.CTkLabel(self, text="Instalar individual:").pack(pady=5)
        for nombre in ["Pulse", "Gesco", "AnyDesk", "Bastionado"]:
            ctk.CTkButton(self, text=nombre, command=lambda n=nombre: self.instalar_individual(n)).pack(pady=3)

        self.log_text = ctk.CTkTextbox(self, width=460, height=150)
        self.log_text.pack(pady=10)
        self.log("🟢 Listo para comenzar.")

    def instalar_todo(self):
        self.log("🔄 Instalando Pulse...")
        instalar("Pulse")
        self.log("🔄 Instalando Gesco...")
        instalar("Gesco")
        self.log("🔄 Instalando AnyDesk...")
        instalar("AnyDesk")
        self.log("📥 Bastionado solo descargado.")
        descargar("Bastionado")

    def instalar_individual(self, nombre):
        self.log(f"🔄 Instalando {nombre}...")
        instalar(nombre)

    def log(self, texto):
        self.log_text.insert("end", texto + "\n")
        self.log_text.see("end")

app = App()
app.mainloop()
