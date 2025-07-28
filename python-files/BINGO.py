
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

def generar_cartro():
    return sorted(random.sample(range(1, 91), 15))

class BingoApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x600")
        self.numeros = list(range(1, 91))
        random.shuffle(self.numeros)
        self.numeros_sortits = []
        self.interval = tk.DoubleVar(value=3)
        self.color_fons = "#ffffff"
        self.color_num = "#0000cc"

        self.custom_frame = tk.LabelFrame(root, text="🎨 Personalitza el teu bingo", padx=10, pady=10)
        self.custom_frame.pack(pady=10)

        tk.Label(self.custom_frame, text="Títol:").grid(row=0, column=0, sticky="e")
        self.titol_input = tk.Entry(self.custom_frame, width=30)
        self.titol_input.grid(row=0, column=1, padx=5)

        tk.Label(self.custom_frame, text="Color de fons (#HEX):").grid(row=1, column=0, sticky="e")
        self.bg_input = tk.Entry(self.custom_frame, width=10)
        self.bg_input.insert(0, "#ffffff")
        self.bg_input.grid(row=1, column=1, sticky="w")

        tk.Label(self.custom_frame, text="Color del número (#HEX):").grid(row=2, column=0, sticky="e")
        self.num_input = tk.Entry(self.custom_frame, width=10)
        self.num_input.insert(0, "#0000cc")
        self.num_input.grid(row=2, column=1, sticky="w")

        tk.Label(self.custom_frame, text="Logo (opcional):").grid(row=3, column=0, sticky="e")
        self.logo_path = tk.StringVar()
        self.logo_entry = tk.Entry(self.custom_frame, textvariable=self.logo_path, width=30)
        self.logo_entry.grid(row=3, column=1)
        ttk.Button(self.custom_frame, text="📁 Navega", command=self.carrega_logo).grid(row=3, column=2)

        self.boto_aplica_titol = ttk.Button(self.custom_frame, text="✅ Aplica i inicia", command=self.aplica_personalitzacio)
        self.boto_aplica_titol.grid(row=4, column=0, columnspan=3, pady=10)

        self.label_logo = tk.Label(root)
        self.label_logo.pack()

        self.label_titol = tk.Label(root, text="", font=("Helvetica", 20, "bold"))
        self.label_titol.pack(pady=10)

        self.label_numero = tk.Label(root, text="", font=("Helvetica", 60))
        self.label_numero.pack(pady=20)

        self.label_sortits = tk.Label(root, text="Números cantats:", font=("Helvetica", 12))
        self.label_sortits.pack()

        self.text_sortits = tk.Text(root, height=5, width=60, state="disabled")
        self.text_sortits.pack()

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        ttk.Label(self.control_frame, text="⏱ Interval (2-6s):").grid(row=0, column=0, padx=5)
        self.spin_interval = ttk.Spinbox(self.control_frame, from_=2, to=6, textvariable=self.interval, width=5)
        self.spin_interval.grid(row=0, column=1, padx=5)

        self.boto_inici = ttk.Button(self.control_frame, text="▶ Comença el bingo", command=self.comenca_bingo, state="disabled")
        self.boto_inici.grid(row=0, column=2, padx=10)

        self.boto_cartro = ttk.Button(root, text="🎱 Genera un cartró nou", command=self.mostra_cartro, state="disabled")
        self.boto_cartro.pack(pady=10)

        self.label_cartro = tk.Label(root, text="", font=("Courier", 14))
        self.label_cartro.pack()

    def carrega_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Imatges", "*.png;*.jpg;*.jpeg")])
        if path:
            self.logo_path.set(path)

    def aplica_personalitzacio(self):
        titol = self.titol_input.get().strip()
        if not titol:
            messagebox.showwarning("Títol requerit", "Escriu un títol per començar.")
            return

        self.color_fons = self.bg_input.get()
        self.color_num = self.num_input.get()

        self.root.configure(bg=self.color_fons)
        self.label_titol.config(text=titol, bg=self.color_fons)
        self.label_numero.config(fg=self.color_num, bg=self.color_fons)
        self.text_sortits.config(bg=self.color_fons)
        self.label_sortits.config(bg=self.color_fons)

        if self.logo_path.get():
            try:
                img = Image.open(self.logo_path.get())
                img = img.resize((100, 100))
                self.logo_img = ImageTk.PhotoImage(img)
                self.label_logo.config(image=self.logo_img, bg=self.color_fons)
            except Exception as e:
                messagebox.showwarning("Error al carregar la imatge", str(e))

        self.root.title(titol)
        self.boto_inici.config(state="normal")
        self.boto_cartro.config(state="normal")

    def comenca_bingo(self):
        self.boto_inici.config(state="disabled")
        self.cantar_numero()

    def cantar_numero(self):
        if self.numeros:
            num = self.numeros.pop(0)
            self.numeros_sortits.append(num)
            self.label_numero.config(text=str(num))

            self.text_sortits.config(state="normal")
            self.text_sortits.insert("end", f"{num} ")
            self.text_sortits.config(state="disabled")
            self.text_sortits.see("end")

            self.root.after(int(self.interval.get() * 1000), self.cantar_numero)
        else:
            messagebox.showinfo("Bingo complet", "✅ S'han cantat tots els números!")
            self.label_numero.config(text="🎉")

    def mostra_cartro(self):
        cartro = generar_cartro()
        formatted = "  ".join(f"{n:2d}" for n in cartro[:5]) + "\n" +                     "  ".join(f"{n:2d}" for n in cartro[5:10]) + "\n" +                     "  ".join(f"{n:2d}" for n in cartro[10:])
        self.label_cartro.config(text=formatted, bg=self.color_fons)

if __name__ == "__main__":
    root = tk.Tk()
    app = BingoApp(root)
    root.mainloop()
