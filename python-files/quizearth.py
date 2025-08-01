import tkinter as tk
from tkinter import messagebox

def enviar_respostas():
    q1 = var1.get()
    q2 = var2.get()
    if q1 == "Júpiter" and q2 == "Paris":
        messagebox.showinfo("Resultado", "Parabéns, você acertou tudo!")
    else:
        messagebox.showinfo("Resultado", "Respostas registradas. Boa sorte!")

root = tk.Tk()
root.title("QuizEarth")
root.geometry("400x300")

tk.Label(root, text="🌍 QuizEarth", font=("Segoe UI", 16)).pack(pady=10)
tk.Label(root, text="1. Qual é o maior planeta do sistema solar?").pack()

var1 = tk.StringVar()
tk.Radiobutton(root, text="Terra", variable=var1, value="Terra").pack()
tk.Radiobutton(root, text="Júpiter", variable=var1, value="Júpiter").pack()
tk.Radiobutton(root, text="Marte", variable=var1, value="Marte").pack()

tk.Label(root, text="2. Qual é a capital da França?").pack(pady=10)

var2 = tk.StringVar()
tk.Radiobutton(root, text="Roma", variable=var2, value="Roma").pack()
tk.Radiobutton(root, text="Paris", variable=var2, value="Paris").pack()
tk.Radiobutton(root, text="Madrid", variable=var2, value="Madrid").pack()

tk.Button(root, text="Enviar", command=enviar_respostas, bg="#28a745", fg="white").pack(pady=20)

root.mainloop()