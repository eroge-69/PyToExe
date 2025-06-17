import tkinter as tk 
from tkinter import ttk ,messagebox
import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion=mysql.connector.connect (
            host= 'localhost',
            user= 'root',
            password = '' ,
            database='consulta'
        )
        return conexion 
    except Error as e:
        messagebox.showerror( 'Error', str(e))



def insertar():
    conexion =conectar()
    cursor=conexion.cursor()
    sql=  'INSERT INTO datos (id, nombre ,apellido , telefono ,email ) VALUES(%s, %s, %s, %s, %s )'
    valores =(entry_id.get(), entry_nombre.get(), entry_apellido.get(), entry_telefono.get(), entry_email.get() )

    try:
        cursor.execute(sql ,valores)
        conexion.commit()
        messagebox.showinfo ('informacion , registro insertado con exito ') 
        limpiar_campos ()
    except Error as e:
        messagebox.showerror( 'Error', str(e))
    finally:
        conexion.close()



def editar():
    conexion =conectar()
    cursor=conexion.cursor()
    sql="UPDATE datos SET  id=%s, nombre=%s, apellido=%s, telefono=%s WHERE  email=%s "
    valores =(entry_id.get(), entry_nombre.get(), entry_apellido.get(), entry_telefono.get(), entry_email.get() )

    try:
        cursor.execute(sql ,valores)
        conexion.commit()
        messagebox.showinfo ('informacion , registro actualizado con exito ') 
        limpiar_campos ()
    except Error as e:
        messagebox.showerror( 'Error', str(e))
    finally:
        conexion.close()
    


def eliminar():
    conexion =conectar()
    cursor=conexion.cursor()
    sql="DELETE FROM datos WHERE id=%s "

    try:
        cursor.execute(sql,(entry_id.get(),))
        conexion.commit()
        messagebox.showinfo ('informacion , registro eliminado  con exito ') 
        limpiar_campos ()
    except Error as e:
        messagebox.showerror( 'Error', str(e))
    finally:
        conexion.close()


def buscar():
    conexion =conectar()
    cursor=conexion.cursor()
    sql="SELECT * FROM datos WHERE id=%s "
    try:
        cursor.execute(sql,(entry_id.get(),))
        registro=cursor.fetchone()
        if registro:
            entry_nombre.insert(0, registro[1])
            entry_apellido.insert(0, registro[2])
            entry_telefono.insert(0, registro[3])
            entry_email.insert(0, registro[4])
        else:
            messagebox.showinfo('informacion , no se encontro el registro solicitado ')
    
    except Error as e:
        messagebox.showerror( 'Error', str(e))
    finally:
        conexion.close()


def limpiar_campos():
    entry_id .delete(0, tk.END)
    entry_nombre .delete(0, tk.END)
    entry_apellido.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)
    entry_email.delete(0, tk.END)   





app = tk.Tk()
app.title("formulario datos personales ")

ttk.Label (app,text="ID:" ).grid(column =0 ,row= 0)
entry_id = ttk.Entry(app)
entry_id.grid(column= 1, row =0)

ttk.Label (app,text="Nombres:" ).grid(column =0 ,row= 1)
entry_nombre = ttk.Entry(app)
entry_nombre.grid(column= 1, row =1)

ttk.Label (app,text="Apellido:" ).grid(column =0 ,row= 2)
entry_apellido = ttk.Entry(app)
entry_apellido.grid(column= 1, row =2)

ttk.Label (app,text="Telefono:" ).grid(column =0 ,row= 3)
entry_telefono = ttk.Entry(app)
entry_telefono.grid(column= 1, row =3)

ttk.Label (app,text="Email:" ).grid(column =0 ,row= 4)
entry_email = ttk.Entry(app)
entry_email.grid(column= 1, row =4)

ttk.Button(app,text="insertar ", command=insertar) .grid(column=0,row=5)
ttk.Button(app,text="Editar  ", command=editar) .grid(column=1,row=5)
ttk.Button(app,text="Eliminar  ", command=eliminar) .grid(column=2,row=5)
ttk.Button(app,text="Buscar ", command=buscar) .grid(column=3,row=5)
ttk.Button(app,text="Limpiar ", command=limpiar_campos) .grid(column=4,row=5)

app.mainloop()
