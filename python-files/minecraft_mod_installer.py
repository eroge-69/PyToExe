import os
import platform
import subprocess
import requests
import tkinter as tk
from tkinter import messagebox

# Configuration
FORGE_VERSION = "1.20.1-forge-47.2.0"
FORGE_INSTALLER_URL = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{FORGE_VERSION}/forge-{FORGE_VERSION}-installer.jar"
MOD_URL = "https://example.com/mod.jar"  # Remplacez ceci par le vrai lien CurseForge

# Détecter le dossier Minecraft
def get_minecraft_dir():
    if platform.system() == "Windows":
        return os.path.join(os.getenv('APPDATA'), ".minecraft")
    return os.path.expanduser("~/.minecraft")

# Vérifie si Forge est déjà installé
def is_forge_installed(minecraft_dir):
    return os.path.exists(os.path.join(minecraft_dir, "versions", FORGE_VERSION))

# Télécharge un fichier

def download_file(url, dest):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# Installe Forge automatiquement

def install_forge(minecraft_dir):
    installer_path = os.path.join(minecraft_dir, "forge-installer.jar")
    download_file(FORGE_INSTALLER_URL, installer_path)
    subprocess.run(["java", "-jar", installer_path, "--installClient"], check=True)

# Télécharge et installe le mod

def install_mod(minecraft_dir):
    mods_dir = os.path.join(minecraft_dir, "mods")
    os.makedirs(mods_dir, exist_ok=True)
    mod_path = os.path.join(mods_dir, "mod.jar")
    download_file(MOD_URL, mod_path)

# Action principale déclenchée par le bouton

def install_all():
    try:
        mc_dir = get_minecraft_dir()
        if not is_forge_installed(mc_dir):
            install_forge(mc_dir)
        install_mod(mc_dir)
        messagebox.showinfo("Succès", "Forge et le mod ont été installés !")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Interface graphique simple
root = tk.Tk()
root.title("Installateur de Mods Minecraft")
root.geometry("300x150")

btn = tk.Button(root, text="Installer Forge + Mod", command=install_all, height=2, width=25)
btn.pack(pady=40)

root.mainloop()
