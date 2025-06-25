import tkinter as tk

# Diccionario con los calibres y espesores
calibres = {
    "1/2": 12.7,
    "7/16": 11.11,
    "3/8": 9.53,
    "5/16": 7.94,
    "1/4": 6.35,
    "3": 6.07,
    "4": 5.69,
    "5": 5.31,
    "6": 4.94,
    "3/16": 4.76,
    "7": 4.55,
    "8": 4.18,
    "9": 3.8,
    "10": 3.42,
    "1/8": 3.18,
    "11": 3.04,
    "12": 2.66,
    "13": 2.28,
    "14": 1.9,
    "15": 1.71,
    "1/16": 1.59,
    "16": 1.52,
    "17": 1.37,
    "18": 1.21,
    "19": 1.06,
    "20": 0.91,
    "21": 0.84,
    "1/32": 0.79,
    "22": 0.76,
    "23": 0.68,
    "24": 0.61,
    "25": 0.53,
    "26": 0.45,
    "27": 0.42,
    "1/64": 0.4,
    "28": 0.38,
    "29": 0.34,
    "30": 0.3,
    "31": 0.27,
    "32": 0.25,
    "33": 0.23,
    "34": 0.21
}

def obtener_espesor():
    calibre = entrada.get()
    if calibre in calibres:
        espesor = calibres[calibre]
        resultado.config(text=f"El espesor es: {espesor} mm")
    else:
        resultado.config(text="Calibre no encontrado")

root = tk.Tk()
root.title("Calibre a Espesor")

entrada = tk.Entry(root)
entrada.pack()

boton = tk.Button(root, text="Obtener Espesor", command=obtener_espesor)
boton.pack()

resultado = tk.Label(root, text="")
resultado.pack()

root.mainloop()