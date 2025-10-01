import tkinter as tk

root = tk.Tk()
root.withdraw()

stop_flag = False

def mostrar_popup(i=1):
    global stop_flag
    if not stop_flag and i <= 10000:
        popup = tk.Toplevel(root)
        popup.title("fuiste jakiado")
        popup.geometry("200x100+500+300")

        tk.Label(popup, text="jakiado").pack(expand=True, padx=10, pady=10)
        tk.Button(popup, text="Cerrar", command=popup.destroy).pack(pady=5)

        root.after(100, mostrar_popup, i+1)
    else:
        root.destroy()

def detener(event=None):
    global stop_flag
    stop_flag = True

root.bind_all("<Control-j>", detener)
mostrar_popup()
root.mainloop()