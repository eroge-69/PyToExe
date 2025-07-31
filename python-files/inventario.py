from tkinter import *
import customtkinter as ctk
from tkinter.messagebox import showinfo
x = int
i = str
ventas = []
compras = []
root = ctk.CTk(ctk.set_default_color_theme('green'))
root.title("inventario")
root.geometry("1300x920")
def insert():
    x = textbox.get()
    if x == "":
        showinfo(title="inventario", message="error")
    else:
        lista.insert(0, x)
        ventas.insert(0, 0)
        compras.insert(0, 0)

def acceder():
    global seleccionado
    indice = lista.curselection()
    seleccionado = indice[0]
    producto = ctk.CTkLabel(root, text=lista.get(lista.curselection()), text_color="red", width=70)
    inventario = ctk.CTkLabel(root, text= compras[seleccionado] - ventas[seleccionado])
    n_v = ctk.CTkLabel(root,text= ventas[seleccionado], width=20)
    n_c = ctk.CTkLabel(root,text= compras[seleccionado], width=20)

    producto.place(x=358,y=50)
    n_c.place(x=948,y=50)
    e_c.place(x=940,y=78.5)
    n_v.place(x=665,y=50)
    e_v.place(x=658,y=78.5)
    inventario.place(x=1264,y=50)

    sumarv.place(x=668,y=105)
    sumarc.place(x=950,y=105)

def sumac():
    entrada = e_c.get()
    if entrada.isalpha() == True:
        showinfo(title="inventario", message="error")
    else:
        entradac = int(e_c.get())
        compras[seleccionado] += entradac
        n_c = ctk.CTkLabel(root,text=compras[seleccionado], width=20)
        n_c.place(x=948,y=50)
        inventario = ctk.CTkLabel(root, text= compras[seleccionado] - ventas[seleccionado],width=20)
        inventario.place(x=1264,y=50)

def sumav ():
    entrada = e_v.get()
    if entrada.isalpha() == True:
        showinfo(title="inventario", message="error")
    elif int(entrada) > compras[seleccionado] or (ventas[seleccionado] + int(entrada)) > compras[seleccionado]:
        showinfo(title="inventario", message="error")
    else:
        entradav = int(e_v.get())
        ventas[seleccionado] += entradav
        n_v = ctk.CTkLabel(root,text=ventas[seleccionado], width=20)
        n_v.place(x=665,y=50)
        inventario = ctk.CTkLabel(root, text= compras[seleccionado] - ventas[seleccionado], width=20)
        inventario.place(x=1264,y=50)
def save():
    with open("inventario.txt", "w") as guardar:
        for i in range(len(lista.get(0, END))):
            guardar.write(f"{lista.get(i)}|{ventas[i]}|{compras[i]}\n")
        
e_c = (ctk.CTkEntry(root,height=10,width=35))
e_v = (ctk.CTkEntry(root,height=10,width=35))
tabla = ctk.CTkLabel(root, text= "                                              producto                                                                                ventas                                                                                compras                                                                                inventario final                  ", bg_color="white",text_color="black")
lista = Listbox(root)
sumarv = ctk.CTkButton(root,text='+',command=sumav, height=2,width=2)
sumarc = ctk.CTkButton(root,text='+',command=sumac, height=2,width=2)
insertar = ctk.CTkButton(root, text="insertar producto", command=insert, height=20, width=225)
acceder = ctk.CTkButton(root, text = "acceder", command=acceder, height=20, width=125)
guardar = ctk.CTkButton(root, text="guardar datos", command=save, height=20, width=225)
Label = ctk.CTkLabel(root)
textbox = ctk.CTkEntry(root,width=1135, height=10)

insertar.place(x=0,y=0)
acceder.place(x=225,y=685)
lista.place(x = 225,y = 50, height=800)
tabla.place(x=225,y=20)
guardar.place(x=0,y=40)
textbox.place(x=225,y=0)

try:
    with open("inventario.txt", "r") as file:
        for readline in file:
            parts = readline.strip().split('|')
            if len(parts) == 3:
                producto, venta, compra = parts
                lista.insert(END, producto)
                ventas.append(int(venta))
                compras.append(int(compra))
except:
    pass
root.mainloop()