import tkinter as tk
import webbrowser

def abrir_url(event=None):
    texto = entrada.get().strip()
    if not texto:
        return
    if texto.startswith("http://") or texto.startswith("https://") or "." in texto:
        url = texto if texto.startswith("http") else "https://" + texto
    else:
        url = f"https://www.google.com/search?q={texto}"
    webbrowser.open_new_tab(url)

janela = tk.Tk()
janela.title("ISCZN Station")
janela.geometry("800x100")  # Janela mais larga para nomes grandes

frame = tk.Frame(janela)
frame.pack(padx=10, pady=10, fill="x", expand=True)

entrada = tk.Entry(frame, font=("Arial", 14))
entrada.pack(side="left", fill="x", expand=True)
entrada.bind("<Return>", abrir_url)

botao_ir = tk.Button(frame, text="Ir", font=("Arial", 12), width=5, command=abrir_url)
botao_ir.pack(side="left", padx=5)

janela.mainloop()
