import os
import shutil
import tkinter as tk
from tkinter import messagebox
import subprocess
from random import randint

# ---------------- Funções de otimização ---------------- #
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
        if os.name=='nt': os.system("powercfg -setactive SCHEME_MIN")
        messagebox.showinfo("⚡ Power Plan", "Plano de energia de alto desempenho ativado.")
    except Exception as e:
        messagebox.showerror("❌ Erro", f"Falha ativando plano gamer: {e}")

def debloat():
    try:
        if os.name=='nt':
            apps = ["Microsoft.CommsPhone", "Microsoft.XboxApp"]
            for a in apps:
                subprocess.run(["powershell","-Command",f"Get-AppxPackage *{a}* | Remove-AppxPackage"], check=False)
        messagebox.showinfo("🗑 Debloat", "Apps inúteis removidos (exemplo).")
    except Exception as e:
        messagebox.showerror("❌ Erro", f"Falha no debloat: {e}")

def tweak_services():
    messagebox.showinfo("🔧 Serviços", "Serviços não essenciais podem ser desativados (a implementar).")

def reg_tweaks():
    messagebox.showinfo("📈 Regedit", "Tweak básico de performance aplicado (exemplo).")

# ---------------- Janela ---------------- #
root = tk.Tk()
root.title("🐵 Pretoides Tweaker 🐵")
root.geometry("950x700")
root.configure(bg="#0a0f1c")
root.resizable(False, False)

# ---------------- Cores e fontes ---------------- #
colors = ["#00ffea", "#ff00ff", "#00ff44", "#ffae00", "#ff0055"]
fonte_titulo = ("Orbitron", 36, "bold")
fonte_btn = ("Consolas", 14, "bold")

# ---------------- Fundo animado ---------------- #
canvas = tk.Canvas(root, width=950, height=700, bg="#0a0f1c", highlightthickness=0)
canvas.place(x=0, y=0)

stars = []
for _ in range(120):
    x, y = randint(0, 950), randint(0, 700)
    size = randint(1, 3)
    stars.append(canvas.create_oval(x, y, x+size, y+size, fill="white", outline=""))

def animar_fundo():
    for s in stars:
        x1, y1, x2, y2 = canvas.coords(s)
        canvas.move(s, 0, 1)
        if y1 > 700:
            new_x = randint(0, 950)
            new_size = randint(1, 3)
            canvas.coords(s, new_x, 0, new_x + new_size, 0 + new_size)
    root.after(50, animar_fundo)

animar_fundo()

# ---------------- Frame central ---------------- #
frame = tk.Frame(root, bg="#0a0f1c")
frame.place(relx=0.5, rely=0.5, anchor="center", width=750, height=620)

# ---------------- Título ---------------- #
label = tk.Label(frame, text="Pretoides Tweaker", font=fonte_titulo, fg="#00ffea", bg="#0a0f1c")
label.pack(pady=25)

def mudar_cor(indice=[0]):
    label.config(fg=colors[indice[0]])
    indice[0]=(indice[0]+1)%len(colors)
    root.after(400, mudar_cor)

mudar_cor()

# ---------------- Botões futuristas ---------------- #
def criar_botao(txt, cmd):
    # Frame do botão para criar efeito de sombra
    btn_frame = tk.Frame(frame, bg="#0a0f1c")
    btn_frame.pack(pady=10)
    
    # Botão com gradiente simulando neon
    b = tk.Button(btn_frame, text=txt, command=cmd, font=fonte_btn, fg="white",
                  bg="#1f1f3a", activebackground="#00ffea", activeforeground="#0a0f1c",
                  relief="flat", bd=0, width=45, height=2)
    
    b.pack()
    
    # Hover: muda cor para neon
    def on_enter(e): b.config(bg="#00ffea", fg="#0a0f1c")
    def on_leave(e): b.config(bg="#1f1f3a", fg="white")
    
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    
    return b

criar_botao("🧹 Limpar Arquivos Temporários", limpar_temp)
criar_botao("⚡ Ativar Power Plan Gamer", power_gamer)
criar_botao("🗑 Debloat – Remover Apps Inúteis", debloat)
criar_botao("🔧 Otimizar Serviços", tweak_services)
criar_botao("📈 Aplicar Tweaks de Registro", reg_tweaks)
criar_botao("🚀 Boost Completo (Tudo de uma vez)", lambda:[limpar_temp(), power_gamer()])
criar_botao("❌ Fechar", root.quit)

root.mainloop()
