import os
import requests
import zipfile
import io
import shutil

BASE_DIR = "meu_menu"
EMUL_DIR = os.path.join(BASE_DIR, "emuladores")
ICON_DIR = os.path.join(BASE_DIR, "icons")

# Dicionário dos emuladores com URLs e executáveis
emuladores = {
    "NES": {
        "url": "https://github.com/TASEmulators/fceux/releases/download/2.6.4/fceux-2.6.4-win32.zip",
        "exe": "fceux.exe",
        "icon_url": "https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/scriptmodules/supplementary/emulationstation/emulationstation/themes/RetroPie/icons/nes.png"
    },
    "SNES": {
        "url": "https://github.com/snes9xgit/snes9x/releases/download/1.60.0/snes9x-x64-1.60.zip",
        "exe": "snes9x-x64.exe",
        "icon_url": "https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/scriptmodules/supplementary/emulationstation/emulationstation/themes/RetroPie/icons/snes.png"
    },
    "GBA": {
        "url": "https://github.com/visualboyadvance-m/visualboyadvance-m/releases/download/2.1.5/vbam-x64.zip",
        "exe": "VisualBoyAdvance-M.exe",
        "icon_url": "https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/scriptmodules/supplementary/emulationstation/emulationstation/themes/RetroPie/icons/gba.png"
    },
    "N64": {
        "url": "https://github.com/project64/project64/releases/download/3.0.1.0/Project64-3.0.1.0.zip",
        "exe": "Project64.exe",
        "icon_url": "https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/scriptmodules/supplementary/emulationstation/emulationstation/themes/RetroPie/icons/n64.png"
    },
    "PS1": {
        "url": "https://www.epsxe.com/files/ePSXe191.zip",
        "exe": "ePSXe.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Playstation_logo.svg/1024px-Playstation_logo.svg.png"
    },
    "PS2": {
        "url": "https://github.com/PCSX2/pcsx2/releases/download/v1.7.4980/pcsx2-1.7.4980-win64.zip",
        "exe": "pcsx2.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/PCSX2_logo.svg"
    },
    "3DS": {
        "url": "https://github.com/citra-emu/citra-nightly/releases/download/nightly-1626/citra-windows-msvc-2023-08-21-71c1a94.zip",
        "exe": "citra-qt.exe",
        "icon_url": "https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/scriptmodules/supplementary/emulationstation/emulationstation/themes/RetroPie/icons/3ds.png"
    }
}

# Função para baixar e extrair o emulador
def baixar_e_extrair(nome, info):
    pasta_destino = os.path.join(EMUL_DIR, nome)
    if os.path.exists(pasta_destino):
        print(f"[{nome}] Já existe, pulando download.")
        return
    print(f"[{nome}] Baixando emulador...")
    r = requests.get(info["url"])
    if r.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(pasta_destino)
        print(f"[{nome}] Extraído em {pasta_destino}")
    else:
        print(f"[{nome}] Erro ao baixar: {r.status_code}")

# Função para baixar o ícone
def baixar_icone(nome, url):
    caminho = os.path.join(ICON_DIR, f"{nome}.png")
    if os.path.exists(caminho):
        return
    print(f"[{nome}] Baixando ícone...")
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(caminho, 'wb') as f:
                f.write(r.content)
            print(f"[{nome}] Ícone salvo.")
        else:
            print(f"[{nome}] Falha ao baixar ícone.")
    except Exception as e:
        print(f"[{nome}] Erro no ícone: {e}")

# Função para criar ZIP do pacote
def criar_zip():
    zip_name = "meu_menu.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    print("[*] Criando arquivo ZIP...")
    shutil.make_archive("meu_menu", 'zip', BASE_DIR)
    print(f"[*] Arquivo {zip_name} criado com sucesso.")

# Código do menu.py
menu_code = """
import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EMUL_DIR = os.path.join(BASE_DIR, "emuladores")
ICON_DIR = os.path.join(BASE_DIR, "icons")

emuladores = {
    "NES": {
        "exe": "fceux.exe"
    },
    "SNES": {
        "exe": "snes9x-x64.exe"
    },
    "GBA": {
        "exe": "VisualBoyAdvance-M.exe"
    },
    "N64": {
        "exe": "Project64.exe"
    },
    "PS1": {
        "exe": "ePSXe.exe"
    },
    "PS2": {
        "exe": "pcsx2.exe"
    },
    "3DS": {
        "exe": "citra-qt.exe"
    }
}

class MenuR36S(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menu R36S Estilo")
        self.geometry("900x500")
        self.configure(bg="#111")
        self.resizable(False, False)
        self.btns = []
        self.selecionado = 0
        self.load_buttons()
        self.bind("<Left>", self.move_esquerda)
        self.bind("<Right>", self.move_direita)
        self.bind("<Return>", self.executar)
        self.update_selection()

    def load_buttons(self):
        x = 30
        y = 50
        for nome in emuladores.keys():
            icon_path = os.path.join(ICON_DIR, f"{nome}.png")
            if os.path.exists(icon_path):
                img = Image.open(icon_path).resize((80,80), Image.ANTIALIAS)
            else:
                img = Image.new("RGBA", (80,80), (255,0,0,255))
            photo = ImageTk.PhotoImage(img)
            btn = tk.Button(self, image=photo, bg="#222", activebackground="#660000",
                            relief="flat", command=lambda n=nome: self.abrir_emulador(n))
            btn.image = photo
            btn.place(x=x, y=y, width=100, height=100)
            self.btns.append(btn)
            x += 110
            if x > 800:
                x = 30
                y += 120

    def update_selection(self):
        for i, b in enumerate(self.btns):
            if i == self.selecionado:
                b.config(bg="#660000")
            else:
                b.config(bg="#222")

    def move_esquerda(self, event):
        self.selecionado = (self.selecionado - 1) % len(self.btns)
        self.update_selection()

    def move_direita(self, event):
        self.selecionado = (self.selecionado + 1) % len(self.btns)
        self.update_selection()

    def executar(self, event=None):
        nome = list(emuladores.keys())[self.selecionado]
        self.abrir_emulador(nome)

    def abrir_emulador(self, nome):
        info = emuladores[nome]
        pasta = os.path.join(EMUL_DIR, nome)
        exe_path = None
        for root, dirs, files in os.walk(pasta):
            for f in files:
                if f.lower() == info["exe"].lower():
                    exe_path = os.path.join(root, f)
                    break
            if exe_path:
                break
        if exe_path and os.path.exists(exe_path):
            try:
                subprocess.Popen(exe_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir emulador:\\n{e}")
        else:
            messagebox.showerror("Erro", f"Executável do emulador '{nome}' não encontrado.\\nProcure em:\\n{pasta}")

if __name__ == "__main__":
    app = MenuR36S()
    app.mainloop()
"""

# Função principal
def main():
    os.makedirs(EMUL_DIR, exist_ok=True)
    os.makedirs(ICON_DIR, exist_ok=True)

    for nome, info in emuladores.items():
        baixar_e_extrair(nome, info)
        baixar_icone(nome, info["icon_url"])

    # Salvar o menu.py no diretório base
    with open(os.path.join(BASE_DIR, "menu.py"), "w", encoding="utf-8") as f:
        f.write(menu_code.strip())

    criar_zip()

if __name__ == "__main__":
    main()
