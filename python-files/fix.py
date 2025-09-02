import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import shutil
import tempfile
from pathlib import Path

class OnlineFixGUI:
    def __init__(self):
        # Configurações
        self.STEAM_LIB = r"E:\SteamLibrary\steamapps\common"
        self.FIX_ROOT = r"C:\Users\tayna\Documents\Onlinefix"
        self.WINRAR_PATH = r"C:\Program Files\WinRAR\WinRAR.exe"
        self.RAR_PASSWORD = "online-fix.me"

        # Criar janela principal
        self.root = tk.Tk()
        self.root.title("🎮 OnlineFix Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título
        title_label = tk.Label(main_frame, text="⚡ ONLINEFIX INSTALLER ⚡", 
                              font=("Arial", 16, "bold"), fg="#0066CC")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Seleção de jogo
        ttk.Label(main_frame, text="🎮 Selecione o jogo:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        self.combo_jogos = ttk.Combobox(main_frame, width=70, state="readonly")
        self.combo_jogos.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Seleção de fix
        ttk.Label(main_frame, text="📦 Selecione o fix:", 
                 font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))

        self.combo_fixes = ttk.Combobox(main_frame, width=70, state="readonly")
        self.combo_fixes.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Botão instalar
        self.btn_instalar = tk.Button(main_frame, text="🚀 INSTALAR FIX", 
                                     font=("Arial", 12, "bold"), bg="#00AA00", fg="white",
                                     command=self.instalar_fix, height=2)
        self.btn_instalar.grid(row=5, column=0, pady=(0, 20), sticky=tk.W)

        # Botão configurações
        btn_config = tk.Button(main_frame, text="⚙️ Configurações", 
                              command=self.abrir_configuracoes)
        btn_config.grid(row=5, column=1, pady=(0, 20), sticky=tk.E)

        # Status
        self.status_var = tk.StringVar(value="📋 Status: Carregando dados...")
        status_label = tk.Label(main_frame, textvariable=self.status_var, 
                               font=("Arial", 10), anchor=tk.W)
        status_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, length=560, mode='determinate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Informações
        info_frame = ttk.LabelFrame(main_frame, text="📂 Configurações Atuais", padding="10")
        info_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(info_frame, text=f"📁 Steam: {self.STEAM_LIB}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"📦 Fixes: {self.FIX_ROOT}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"🗜️ WinRAR: {self.WINRAR_PATH}").grid(row=2, column=0, sticky=tk.W)

    def load_data(self):
        self.progress['value'] = 20
        self.status_var.set("📋 Status: Carregando jogos...")
        self.root.update()

        # Carregar jogos
        try:
            if not os.path.exists(self.STEAM_LIB):
                messagebox.showerror("Erro", f"Pasta da Steam não encontrada:\n{self.STEAM_LIB}")
                return

            jogos = [d for d in os.listdir(self.STEAM_LIB) 
                    if os.path.isdir(os.path.join(self.STEAM_LIB, d))]
            self.combo_jogos['values'] = jogos

            self.progress['value'] = 60
            self.status_var.set(f"📋 Status: {len(jogos)} jogos carregados")
            self.root.update()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar jogos:\n{str(e)}")

        # Carregar fixes
        try:
            if not os.path.exists(self.FIX_ROOT):
                os.makedirs(self.FIX_ROOT)
                messagebox.showwarning("Aviso", f"Pasta de fixes criada:\n{self.FIX_ROOT}")

            fixes = [f for f in os.listdir(self.FIX_ROOT) if f.lower().endswith('.rar')]
            self.combo_fixes['values'] = fixes

            self.progress['value'] = 100
            if fixes:
                self.status_var.set(f"📋 Status: {len(fixes)} fixes disponíveis")
            else:
                self.status_var.set("📋 Status: Nenhum fix encontrado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar fixes:\n{str(e)}")

    def instalar_fix(self):
        jogo = self.combo_jogos.get()
        fix = self.combo_fixes.get()

        if not jogo:
            messagebox.showwarning("Aviso", "Selecione um jogo!")
            return

        if not fix:
            messagebox.showwarning("Aviso", "Selecione um fix!")
            return

        # Confirmação
        resposta = messagebox.askyesno("Confirmar", 
            f"🎮 Jogo: {jogo}\n📦 Fix: {fix}\n\n⚠️ Os arquivos serão sobrescritos!\nContinuar?")

        if not resposta:
            return

        self.btn_instalar.config(state="disabled")

        try:
            # Caminhos
            jogo_path = os.path.join(self.STEAM_LIB, jogo)
            fix_path = os.path.join(self.FIX_ROOT, fix)

            # Verificar WinRAR
            if not os.path.exists(self.WINRAR_PATH):
                messagebox.showerror("Erro", f"WinRAR não encontrado:\n{self.WINRAR_PATH}")
                return

            # Pasta temporária
            self.progress['value'] = 20
            self.status_var.set("📋 Status: Criando pasta temporária...")
            self.root.update()

            temp_dir = tempfile.mkdtemp()

            # Extrair RAR
            self.progress['value'] = 50
            self.status_var.set("📋 Status: Extraindo arquivo RAR...")
            self.root.update()

            cmd = [self.WINRAR_PATH, 'x', fix_path, temp_dir + '\\', 
                   f'-p{self.RAR_PASSWORD}', '-y']

            result = subprocess.run(cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode != 0:
                messagebox.showerror("Erro", "Falha ao extrair o arquivo RAR!")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            # Copiar arquivos
            self.progress['value'] = 80
            self.status_var.set("📋 Status: Copiando arquivos...")
            self.root.update()

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join(jogo_path, file)
                    shutil.copy2(src, dst)

            # Limpeza
            shutil.rmtree(temp_dir, ignore_errors=True)

            # Sucesso
            self.progress['value'] = 100
            self.status_var.set("📋 Status: ✅ Fix instalado com sucesso!")

            messagebox.showinfo("Sucesso", 
                f"✅ FIX INSTALADO COM SUCESSO!\n\n🎮 Jogo: {jogo}\n📦 Fix: {fix}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a instalação:\n{str(e)}")

        finally:
            self.btn_instalar.config(state="normal")

    def abrir_configuracoes(self):
        # Janela de configurações
        config_window = tk.Toplevel(self.root)
        config_window.title("⚙️ Configurações")
        config_window.geometry("500x300")
        config_window.resizable(False, False)

        frame = ttk.Frame(config_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Entradas
        ttk.Label(frame, text="📁 Pasta Steam:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        steam_entry = tk.Entry(frame, width=60)
        steam_entry.pack(fill=tk.X, pady=(0, 10))
        steam_entry.insert(0, self.STEAM_LIB)

        ttk.Label(frame, text="📦 Pasta Fixes:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        fix_entry = tk.Entry(frame, width=60)
        fix_entry.pack(fill=tk.X, pady=(0, 10))
        fix_entry.insert(0, self.FIX_ROOT)

        ttk.Label(frame, text="🗜️ Caminho WinRAR:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        winrar_entry = tk.Entry(frame, width=60)
        winrar_entry.pack(fill=tk.X, pady=(0, 10))
        winrar_entry.insert(0, self.WINRAR_PATH)

        ttk.Label(frame, text="🔑 Senha RAR:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        senha_entry = tk.Entry(frame, width=60)
        senha_entry.pack(fill=tk.X, pady=(0, 20))
        senha_entry.insert(0, self.RAR_PASSWORD)

        # Botões
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        def salvar_config():
            self.STEAM_LIB = steam_entry.get()
            self.FIX_ROOT = fix_entry.get()
            self.WINRAR_PATH = winrar_entry.get()
            self.RAR_PASSWORD = senha_entry.get()
            messagebox.showinfo("Sucesso", "Configurações salvas!")
            config_window.destroy()
            self.load_data()

        tk.Button(btn_frame, text="💾 Salvar", command=salvar_config, 
                 bg="#00AA00", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="❌ Cancelar", 
                 command=config_window.destroy).pack(side=tk.LEFT)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = OnlineFixGUI()
    app.run()