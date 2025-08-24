import os
import zipfile

base_folder = "BatoceiraEmuladores"
icons = {
    "ps2.png": "https://upload.wikimedia.org/wikipedia/commons/5/5e/PlayStation_2_logo.svg",
    "3ds.png": "https://upload.wikimedia.org/wikipedia/commons/5/57/Nintendo_3DS_Logo.svg",
    "gba.png": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Game_Boy_Advance_logo.svg",
    "snes.png": "https://upload.wikimedia.org/wikipedia/commons/0/0e/SNES-Logo.svg",
    "nes.png": "https://upload.wikimedia.org/wikipedia/commons/8/87/Nintendo_Entertainment_System_logo.svg",
    "n64.png": "https://upload.wikimedia.org/wikipedia/commons/9/9a/N64_Logo.svg",
    "ps1.png": "https://upload.wikimedia.org/wikipedia/commons/4/4e/PlayStation_logo.svg",
    "psp.png": "https://upload.wikimedia.org/wikipedia/commons/8/8f/PSP-Logo.svg",
    "wii.png": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Wii_Logo.svg",
    "arcade.png": "https://upload.wikimedia.org/wikipedia/commons/f/f1/MAME_Logo.svg",
}

menu_py = """
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE_DIR, "icons")
EMU_DIR = os.path.join(BASE_DIR, "emuladores")

consoles = [
    {"nome": "PS2", "icone": "ps2.png", "exe": "pcsx2/pcsx2.exe"},
    {"nome": "3DS", "icone": "3ds.png", "exe": "citra/citra-qt.exe"},
    {"nome": "GBA", "icone": "gba.png", "exe": "visualboy/vba.exe"},
    {"nome": "SNES", "icone": "snes.png", "exe": "snes9x/snes9x.exe"},
    {"nome": "NES", "icone": "nes.png", "exe": "fceux/fceux.exe"},
    {"nome": "N64", "icone": "n64.png", "exe": "project64/Project64.exe"},
    {"nome": "PS1", "icone": "ps1.png", "exe": "epsxe/epsxe.exe"},
    {"nome": "PSP", "icone": "psp.png", "exe": "ppsspp/PPSSPPWindows.exe"},
    {"nome": "Wii", "icone": "wii.png", "exe": "dolphin/Dolphin.exe"},
    {"nome": "Arcade", "icone": "arcade.png", "exe": "mame/mame.exe"},
]

class MenuR36S(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menu R36S - Edição Windows")
        self.configure(bg="#1e1e1e")
        self.geometry("800x600")
        self.resizable(False, False)

        tk.Label(self, text="Selecione um console", fg="white", bg="#1e1e1e", font=("Segoe UI", 20)).pack(pady=20)
        
        self.frame = tk.Frame(self, bg="#1e1e1e")
        self.frame.pack(pady=10)

        self.carregar_botoes()

    def carregar_botoes(self):
        col = 0
        row = 0
        for console in consoles:
            caminho_icon = os.path.join(ICON_DIR, console["icone"])
            caminho_exe = os.path.join(EMU_DIR, console["exe"])
            if os.path.exists(caminho_icon):
                imagem = Image.open(caminho_icon).resize((64, 64))
                icon = ImageTk.PhotoImage(imagem)
                botao = tk.Button(
                    self.frame,
                    image=icon,
                    text=console["nome"],
                    compound="top",
                    fg="white",
                    bg="#2c2c2c",
                    font=("Segoe UI", 10),
                    command=lambda exe=caminho_exe: self.rodar_emulador(exe),
                    width=100,
                    height=100
                )
                botao.image = icon
                botao.grid(row=row, column=col, padx=15, pady=15)
                col += 1
                if col >= 5:
                    col = 0
                    row += 1

    def rodar_emulador(self, caminho):
        if os.path.exists(caminho):
            subprocess.Popen(caminho, shell=True)
        else:
            messagebox.showerror("Erro", f"Emulador não encontrado:\\n{caminho}")

if __name__ == "__main__":
    app = MenuR36S()
    app.mainloop()
"""

readme_txt = """
# Batoceira Emuladores Pack

## Estrutura

- `menu.py`: script principal que abre o menu com a interface R36S
- `icons/`: ícones dos consoles (64x64 PNG)
- `emuladores/`: pastas para colocar os emuladores correspondentes

## Como usar

1. Baixe ou copie os emuladores para as pastas corretas dentro de `emuladores/`.  
Exemplo: `emuladores/pcsx2/pcsx2.exe` para o PS2.

2. Execute `menu.py` com Python (recomendado Python 3.7+).  
Você precisa ter o módulo `Pillow` instalado (`pip install pillow`).

3. Clique no ícone do console para abrir o emulador.

---

## Observações

- Os emuladores não estão inclusos por questão de direitos autorais.  
- Baixe os emuladores originais nos sites oficiais.

---

Boa jogatina!
"""

with zipfile.ZipFile("BatoceiraEmuladoresPack.zip", "w") as zf:
    zf.writestr("menu.py", menu_py)
    zf.writestr("README.txt", readme_txt)
    for icon_name in icons:
        zf.writestr(f"icons/{icon_name}", f"[Ícone '{icon_name}' placeholder]\nFonte: {icons[icon_name]}")
    # Criar pastas vazias para emuladores
    emu_folders = ["pcsx2", "citra", "visualboy", "snes9x", "fceux", "project64", "epsxe", "ppsspp", "dolphin", "mame"]
    for folder in emu_folders:
        zf.writestr(f"emuladores/{folder}/.keep", "")

print("Arquivo BatoceiraEmuladoresPack.zip criado com sucesso!")
