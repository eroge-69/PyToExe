import tkinter as tk
import random

# Fonction pour convertir le binaire en décimal
def binary_to_decimal(binary):
    return int(binary, 2)

# Fonction pour générer le calcul détaillé avec les puissances de 2
def generate_calculation(binary, decimal):
    terms = [f"{bit}*2^{len(binary)-1-i}" for i, bit in enumerate(binary)]
    return " + ".join(terms) + f" = {decimal}"

# Fonction pour mettre à jour la valeur décimale
def update_decimal(*args):
    binary = ''.join([str(var.get()) for var in bits])
    decimal = binary_to_decimal(binary)
    decimal_label.config(text=f"Decimal: {decimal}")
    calculation = generate_calculation(binary, decimal)
    binary_label.config(text=f"Calcul: {calculation}")
    for i, var in enumerate(bits):
        draw_bit_image(bit_canvases[i], var.get())

# Fonction pour dessiner l'image du bit
def draw_bit_image(canvas, bit_value):
    canvas.delete("all")
    if bit_value == 0:
        canvas.create_text(25, 25, text="0", font=("Arial", 24), fill="red")
    else:
        canvas.create_text(25, 25, text="1", font=("Arial", 24), fill="green")

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Fonction pour mettre à jour le nombre de bits
def update_bits(*args):
    num_bits = int(bit_var.get())
    
    # Clear existing widgets
    for widget in frame.winfo_children():
        widget.destroy()
    
    global bits, bit_canvases
    bits = [tk.IntVar(value=0) for _ in range(num_bits)]
    
    bit_canvases = []
    for i, var in enumerate(bits):
        title_lbl = tk.Label(frame, text=f"Bit {i+1}", font=("Arial", 16), fg=("blue" if i % 2 == 0 else "purple"))
        title_lbl.grid(row=0, column=i, padx=5)
        canvas = tk.Canvas(frame, width=50, height=50)
        canvas.grid(row=1, column=i, padx=5)
        bit_canvases.append(canvas)
        draw_bit_image(canvas, var.get())
        slider = tk.Scale(frame, from_=0, to=1, orient=tk.HORIZONTAL, variable=var, command=update_decimal, font=("Arial", 16), length=50)
        slider.grid(row=2, column=i, padx=5)
    
    update_decimal()

# Créer la fenêtre principale
root = tk.Tk()
root.title("Calculatrice Binaire vers Décimale")
root.option_add("*Font", "Arial 16")  # Augmenter la taille de la police par défaut

# Créer un cadre pour l'entrée binaire
frame = tk.Frame(root)
frame.pack(pady=10)

# Créer une étiquette et un menu déroulant pour le nombre de bits
bit_label = tk.Label(root, text="Nombre de bits (1-8):", font=("Arial", 16))
bit_label.pack(pady=5)
bit_var = tk.StringVar(value="4")
bit_menu = tk.OptionMenu(root, bit_var, *[str(i) for i in range(1, 9)], command=update_bits)
bit_menu.pack(pady=5)

# Créer des variables IntVar pour chaque bit (initialement 4 bits)
bits = [tk.IntVar(value=0) for _ in range(4)]

# Créer des étiquettes pour chaque bit (initialement 4 bits)
bit_canvases = []
for i, var in enumerate(bits):
    title_lbl = tk.Label(frame, text=f"Bit {i+1}", font=("Arial", 16), fg=("blue" if i % 2 == 0 else "purple"))
    title_lbl.grid(row=0, column=i, padx=5)
    canvas = tk.Canvas(frame, width=50, height=50)
    canvas.grid(row=1, column=i, padx=5)
    bit_canvases.append(canvas)
    draw_bit_image(canvas, var.get())
    slider = tk.Scale(frame, from_=0, to=1, orient=tk.HORIZONTAL, variable=var, command=update_decimal, font=("Arial", 16), length=50)
    slider.grid(row=2, column=i, padx=5)

# Créer une étiquette pour afficher la valeur décimale avec une couleur aléatoire
decimal_label = tk.Label(root, text="Decimal: 0", font=("Arial", 16), fg=random_color())
decimal_label.pack(pady=10)

# Créer une étiquette pour afficher le calcul binaire avec les puissances de 2
binary_label = tk.Label(root, text="Calcul: 0*2^3 + 0*2^2 + 0*2^1 + 0*2^0 = 0", font=("Arial", 16), fg="blue")
binary_label.pack(pady=10)

# Adapter la taille de la fenêtre au contenu
root.update_idletasks()
root.geometry(f"{root.winfo_reqwidth()}x{root.winfo_reqheight()}")

# Exécuter l'application
root.mainloop()

