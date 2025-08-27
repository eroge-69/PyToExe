import random
import time
import winsound
import tkinter
from tkinter import messagebox
print('hola peruano hermoso')
input('este programa sirve para hacer gambling si obtienes un multiplo de 10 ganas')
peru = random.choice(range(1,10000)) #range dice entre que valores escoger
messagebox.showerror('VALOR', str(peru))#str antes de la funcion permite que la caja de error muestre el valor en numero
time.sleep(2)
if peru %10 == 0: #% es el operador de multiplo en python
    messagebox.showerror('GANASTE BRO','ganaste') #**es el operador de potencia en python
    winsound.PlaySound(r'C:\Users\Admin\Documents\proyectos random we\ene.wav', winsound.SND_FILENAME)
else:
    messagebox.showerror('PERDISTE BRO','por gei')
    winsound.PlaySound(r'C:\Users\Admin\Documents\proyectos random we\sig.wav', winsound.SND_FILENAME)