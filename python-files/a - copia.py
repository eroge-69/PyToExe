from tkinter import simpledialog as sim
from tkinter import messagebox as msg
import sys
import time as ti
def bienvenida():
    msg.showinfo(title="Hola",message="Hola y bienvenido a esta app")
    ti.sleep(1.2)
    ususarioname = sim.askstring(title="Usuario",prompt="Ingrese su nombre de usuario",initialvalue="1x1x1x1")
    if ususarioname is not None:
        msg.showinfo(title="Bienvenido",message="HOLA:" + str(ususarioname))
        print("Muy bien ahora ingrese su contraseña")
        ti.sleep(0.1)
        contraseña = sim.askinteger(title="Contraseña " + str(ususarioname),prompt="Ingrese una contraseña",initialvalue=12345,minvalue=999,maxvalue=99999999)
        if contraseña is not None:
            msg.showinfo(title="Contraseña correcta",message="Ah ingreasado contraseña")
            ti.sleep(0.1)
            msg.showinfo(title="Procesando",message="Procesando datos...")
            ti.sleep(1.5)
            msg.showwarning(title="Advertencia de datos sensibles",message="Recuerde los datos elegidos y por si acaso se crearon copias en su directorio")
            with open("Usuario.txt","w",encoding="utf-8") as user:
                user.write("Usuario:" + str(ususarioname))
            with open("Usuario.md","w",encoding="utf-8") as usermd:
                usermd.write("*Usuario:* **" + str(ususarioname) + "**")
            with open("Contraseña.txt","w",encoding="utf-8") as passw:
                passw.write("Contraseña:" + str(contraseña))
            with open("Contraseña.md","w",encoding="utf-8") as passwmd:
                passwmd.write("*Contraseña:* **" + str(contraseña) + "**")
            sys.exit(0)
        else:
            print("Contraseña necesaria")      
            sys.exit(0)
    else:
        msg.showinfo(title="Ingrese info",message="Disculpe ese dato es obligatorio")
        sys.exit(0)
bienvenida()