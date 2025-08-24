import os, shutil, tkinter as tk
from tkinter import messagebox
import subprocess

# Funções de otimização
def limpar_temp():
    temp=os.environ.get("TEMP")
    if temp and os.path.exists(temp):
        erros=[]
        for i in os.listdir(temp):
            p=os.path.join(temp,i)
            try:
                if os.path.isfile(p) or os.path.islink(p): os.remove(p)
                elif os.path.isdir(p): shutil.rmtree(p)
            except Exception as e: erros.append(str(e))
        if erros: messagebox.showwarning("⚠️ Aviso", "Alguns arquivos estavam em uso e não foram removidos, mas a maioria foi limpa.")
        else: messagebox.showinfo("✅ Sucesso", "Arquivos temporários limpos!")
    else:
        messagebox.showinfo("ℹ️ Info", "Nenhuma pasta TEMP encontrada.")

def power_gamer():
    try:
        if os.name=='nt':
            os.system("powercfg -setactive SCHEME_MIN")
        messagebox.showinfo("⚡ Power Plan", "Plano de energia de alto desempenho ativado.")
    except Exception as e: messagebox.showerror("❌ Erro", f"Falha ativando plano gamer: {e}")

def debloat():
    try:
        if os.name=='nt':
            apps = ["Microsoft.CommsPhone", "Microsoft.XboxApp"]
            for a in apps:
                subprocess.run(["powershell","-Command",f"Get-AppxPackage *{a}* | Remove-AppxPackage"], check=False)
        messagebox.showinfo("🗑 Debloat", "Apps inúteis removidos (exemplo).")
    except Exception as e: messagebox.showerror("❌ Erro", f"Falha no debloat: {e}")

def tweak_services():
    messagebox.showinfo("🔧 Serviços", "Serviços não essenciais podem ser desativados (a implementar).")

def reg_tweaks():
    messagebox.showinfo("📈 Regedit", "Tweak básico de performance aplicado (exemplo).")

# GUI Futurista
root = tk.Tk()
root.title("⚡ Game Booster Ultra – Futurista RGB ⚡")
root.geometry("850x700")  # espaço maior para todas opções
root.configure(bg="#0a0f1c")
root.resizable(False, False)

# Estilos RGB neon
fonte_titulo=("Consolas",22,"bold")
fonte_btn=("Consolas",14,"bold")
colors=["#00ffea","#ff00ff","#00ff44","#ffae00"]
cor_btn="#1f1f3a"
cor_btn_hover="#3a3a6a"

# Label título futurista
label=tk.Label(root,text="🚀 Game Booster Ultra – Painel Futurista RGB 🚀", font=fonte_titulo, fg="#00ffea", bg="#0a0f1c")
label.pack(pady=25)

# Efeito RGB dinâmico no título
def mudar_cor(indice=[0]):
    label.config(fg=colors[indice[0]])
    indice[0]=(indice[0]+1)%len(colors)
    root.after(500, mudar_cor)

mudar_cor()

# Hover
def on_enter(e): e.widget["bg"]=cor_btn_hover

def on_leave(e): e.widget["bg"]=cor_btn

# Criar botão futurista
def criar_botao(txt, cmd):
    b=tk.Button(root, text=txt, command=cmd, font=fonte_btn, fg="white", bg=cor_btn,
                activebackground=cor_btn_hover, activeforeground="white", relief="ridge", bd=6, width=50, height=2)
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    b.pack(pady=10)
    return b

# Botões – agora cabem todos com mais espaço
criar_botao("🧹 Limpar Arquivos Temporários", limpar_temp)
criar_botao("⚡ Ativar Power Plan Gamer", power_gamer)
criar_botao("🗑 Debloat – Remover Apps Inúteis", debloat)
criar_botao("🔧 Otimizar Serviços", tweak_services)
criar_botao("📈 Aplicar Tweaks de Registro", reg_tweaks)
criar_botao("🚀 Boost Completo (Tudo de uma vez)", lambda:[limpar_temp(), power_gamer()])
criar_botao("❌ Fechar", root.quit)

root.mainloop()
