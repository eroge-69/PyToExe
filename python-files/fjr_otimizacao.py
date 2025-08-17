# FJR Otimização - App Desktop para Windows (Tkinter)
# Autor: ChatGPT
# Requisitos: Python 3.9+ e pillow
# Execute: python fjr_otimizacao.py

import os
import sys
import shutil
import subprocess
import tempfile
import ctypes
from tkinter import Tk, Button, Label, Frame, Text, END, BOTH, DISABLED, NORMAL, messagebox, Scrollbar, RIGHT, Y
from tkinter import ttk

APP_NAME = "FJR Otimização"

def resource_path(relative):
    # Suporte a PyInstaller
    try:
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

def ensure_icon():
    """
    Gera um ícone .ico simples (4 quadrados azuis) se não existir.
    """
    ico_path = os.path.abspath("fjr.ico")
    if os.path.exists(ico_path):
        return ico_path
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # fundo leve
        draw.rectangle([0,0,255,255], fill=(20,130,255,255))
        # 4 quadrados divididos
        pad = 28
        gap = 12
        cell = (256 - pad*2 - gap) // 2
        # topo-esq
        draw.rectangle([pad, pad, pad+cell, pad+cell], fill=(240, 250, 255, 255))
        # topo-dir
        draw.rectangle([pad+cell+gap, pad, pad+cell+gap+cell, pad+cell], fill=(230, 245, 255, 255))
        # baixo-esq
        draw.rectangle([pad, pad+cell+gap, pad+cell, pad+cell+gap+cell], fill=(230, 245, 255, 255))
        # baixo-dir
        draw.rectangle([pad+cell+gap, pad+cell+gap, pad+cell+gap+cell, pad+cell+gap+cell], fill=(240, 250, 255, 255))
        ico_sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
        img.save(ico_path, sizes=ico_sizes)
        return ico_path
    except Exception as e:
        return None

def run_command(cmd, shell=False):
    try:
        completed = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        out = completed.stdout.strip()
        err = completed.stderr.strip()
        code = completed.returncode
        return code, out, err
    except Exception as e:
        return -1, "", str(e)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class App:
    def __init__(self, root: Tk):
        root.title(APP_NAME)
        root.geometry("760x520")
        root.minsize(720, 480)

        # Ícone
        ico = ensure_icon()
        if ico and os.path.exists(ico):
            try:
                root.iconbitmap(ico)
            except:
                pass

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        header = Frame(root)
        header.pack(fill='x', padx=16, pady=12)

        Label(header, text=APP_NAME, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        Label(header, text="Clique numa ação para otimizar/ajustar seu Windows. (Ações seguras)",
              font=("Segoe UI", 10)).pack(anchor="w")

        # Botões (lado esquerdo)
        left = Frame(root)
        left.pack(side="left", fill="y", padx=16, pady=8)

        actions = [
            ("🔄 Limpar arquivos temporários", self.clean_temp),
            ("🧹 Esvaziar Lixeira", self.empty_recycle_bin),
            ("🧽 Limpeza de Disco (Cleanmgr)", self.disk_cleanup),
            ("🧠 Limpar cache de DNS", self.flush_dns),
            ("🚀 Gerenciar Inicialização (Gerenciador de Tarefas)", self.open_startup_manager),
            ("🧭 Abrir Windows Update", self.open_windows_update),
            ("🧩 Desfragmentar/otimizar unidades", self.open_defrag),
            ("📦 Programas e Recursos", self.open_programs_features),
            ("🗂️ Pasta de Inicialização (atalhos de startup)", self.open_startup_folder),
            ("📁 Abrir pasta TEMP", self.open_temp_folder),
        ]

        for text, fn in actions:
            btn = Button(left, text=text, width=38, command=lambda f=fn, t=text: self.wrap_action(t, f))
            btn.pack(anchor="w", pady=4)

        # Log (lado direito)
        right = Frame(root)
        right.pack(side="right", fill="both", expand=True, padx=16, pady=8)

        Label(right, text="Log de ações", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.text = Text(right, wrap="word")
        self.text.pack(fill=BOTH, expand=True, side="left")
        scroll = Scrollbar(right, command=self.text.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.text.configure(yscrollcommand=scroll.set)

        self.write("Pronto! Selecione uma ação à esquerda.\n")

        # Rodapé
        footer = Frame(root)
        footer.pack(fill='x', padx=16, pady=6)
        Label(footer, text="Dica: algumas ações podem pedir permissões de administrador.", font=("Segoe UI", 9, "italic")).pack(anchor="w")

    def write(self, msg: str):
        self.text.configure(state=NORMAL)
        self.text.insert(END, msg + "\n")
        self.text.see(END)
        self.text.configure(state=DISABLED)

    def wrap_action(self, label, fn):
        self.write(f"▶ {label}...")
        try:
            result = fn()
            if result is None:
                self.write(f"✔ Concluído: {label}")
            else:
                self.write(result)
        except Exception as e:
            self.write(f"✖ Erro: {e}")

    # ===== AÇÕES =====
    def clean_temp(self):
        temp_dirs = [
            os.environ.get("TEMP"),
            os.environ.get("TMP"),
            os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Temp")
        ]
        total_deleted = 0
        for d in temp_dirs:
            if not d or not os.path.exists(d):
                continue
            for root, dirs, files in os.walk(d):
                for name in files:
                    path = os.path.join(root, name)
                    try:
                        size = os.path.getsize(path)
                        os.remove(path)
                        total_deleted += size
                    except Exception:
                        pass
                for name in dirs:
                    path = os.path.join(root, name)
                    try:
                        shutil.rmtree(path)
                    except Exception:
                        pass
        mb = total_deleted / (1024*1024)
        return f"✔ Temporários removidos (aprox.): {mb:.2f} MB"

    def empty_recycle_bin(self):
        # SHEmptyRecycleBin
        try:
            SHERB_NOCONFIRMATION = 0x00000001
            SHERB_NOPROGRESSUI   = 0x00000002
            SHERB_NOSOUND        = 0x00000004
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND)
            return "✔ Lixeira esvaziada."
        except Exception as e:
            return f"✖ Não foi possível esvaziar a Lixeira: {e}"

    def disk_cleanup(self):
        code, out, err = run_command(["cleanmgr", "/LOWDISK"])
        if code == 0:
            return "✔ Limpeza de Disco aberta."
        else:
            return f"ℹ Tentei abrir o Cleanmgr. Código {code}. Pode não estar disponível em algumas versões."

    def flush_dns(self):
        code, out, err = run_command(["ipconfig", "/flushdns"])
        if code == 0:
            return "✔ DNS limpo.\n" + (out or "")
        else:
            return f"✖ Não foi possível limpar DNS. Código {code}. {err}"

    def open_startup_manager(self):
        # Abre Gerenciador de Tarefas na aba Inicializar
        # /7 tenta abrir na aba Startup (pode variar por versão)
        code, out, err = run_command(["taskmgr", "/7"])
        if code != 0:
            # fallback: abre sem aba específica
            run_command(["taskmgr"])
        return "✔ Gerenciador de Tarefas aberto (aba Inicializar)."

    def open_windows_update(self):
        run_command(["start", "ms-settings:windowsupdate"], shell=True)
        return "✔ Windows Update aberto."

    def open_defrag(self):
        code, out, err = run_command(["dfrgui"])
        if code == 0:
            return "✔ Otimizador de Unidades aberto."
        else:
            return "ℹ Tentei abrir o Otimizador; pode não estar disponível."

    def open_programs_features(self):
        run_command(["appwiz.cpl"])
        return "✔ Programas e Recursos aberto."

    def open_startup_folder(self):
        path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        run_command(["explorer", path])
        return f"✔ Pasta de Inicialização aberta: {path}"

    def open_temp_folder(self):
        path = os.path.expandvars(r"%TEMP%")
        run_command(["explorer", path])
        return f"✔ Pasta TEMP aberta: {path}"


def main():
    root = Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
