import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import sys

# Windows uyumu için arayüz stili
matplotlib.use('TkAgg')

# Galaksi ve küresel küme verileri
data = {
    "Galaksiler": {
        "M31 (Andromeda)": {
            "Çap (ışık yılı)": 220000,
            "Küresel Küme Sayısı": 450,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 1e8,
            "Açıklama": "Samanyolu'na en yakın büyük galaksi, spiral yapıdadır."
        },
        "M87": {
            "Çap (ışık yılı)": 240000,
            "Küresel Küme Sayısı": 13000,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 6.5e9,
            "Açıklama": "Dev eliptik galaksi, merkezinde süper kütleli kara delik vardır."
        },
        "M81": {
            "Çap (ışık yılı)": 90000,
            "Küresel Küme Sayısı": 210,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 7e7,
            "Açıklama": "Büyük Ayı takımyıldızında bulunan spiral galaksi."
        },
        "M82": {
            "Çap (ışık yılı)": 37000,
            "Küresel Küme Sayısı": 200,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 3e7,
            "Açıklama": "Yıldız patlamalarıyla bilinen düzensiz galaksi."
        }
    },
    "Küresel Kümeler": {
        "M15": {
            "Çap (ışık yılı)": 175,
            "Küresel Küme Sayısı": 1,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 4000,
            "Açıklama": "Pegasus takımyıldızında yoğun bir küresel küme."
        },
        "M13": {
            "Çap (ışık yılı)": 145,
            "Küresel Küme Sayısı": 1,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 0,
            "Açıklama": "Herkül takımyıldızında bulunan en parlak küresel kümelerden."
        },
        "Omega Erboğa": {
            "Çap (ışık yılı)": 170,
            "Küresel Küme Sayısı": 1,
            "Kara Delik Kütlesi (Güneş Kütlesi)": 40000,
            "Açıklama": "Samanyolu'nun en büyük küresel kümelerinden biri."
        }
    }
}

class GalaxyComparer:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Galaksi ve Küresel Küme Karşılaştırma Programı")
        self.root.geometry("900x700")

        self.type_var = tk.StringVar(value="Galaksiler")
        self.object_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Kategori:").grid(row=0, column=0, sticky="w")
        type_menu = ttk.OptionMenu(frame, self.type_var, "Galaksiler", *data.keys(), command=self.update_objects)
        type_menu.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Nesne:").grid(row=1, column=0, sticky="w")
        self.object_menu = ttk.OptionMenu(frame, self.object_var, "")
        self.object_menu.grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Verileri Göster", command=self.plot_data).grid(row=2, column=0, columnspan=2, pady=10)

        self.info_label = tk.Label(self.root, text="Açıklama: ", justify="left", anchor="w")
        self.info_label.pack(fill="x", padx=10)

        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_objects(self.type_var.get())

    def update_objects(self, object_type):
        menu = self.object_menu["menu"]
        menu.delete(0, "end")
        for name in data[object_type]:
            menu.add_command(label=name, command=lambda value=name: self.object_var.set(value))
        self.object_var.set(next(iter(data[object_type])))

    def plot_data(self):
        self.ax.clear()
        object_type = self.type_var.get()
        obj_name = self.object_var.get()
        obj_data = data[object_type][obj_name]

        x = obj_data["Çap (ışık yılı)"]
        y = obj_data["Küresel Küme Sayısı"]
        z = obj_data["Kara Delik Kütlesi (Güneş Kütlesi)"]

        self.ax.scatter(x, y, z, c='blue', marker='o', s=100, label=obj_name)
        self.ax.set_xlabel("Çap (ışık yılı)")
        self.ax.set_ylabel("Küresel Küme Sayısı")
        self.ax.set_zlabel("Kara Delik Kütlesi (Güneş Kütlesi)")
        self.ax.set_title("3D Karşılaştırma Grafiği")
        self.ax.legend()

        self.info_label.config(text=f"Açıklama: {obj_data['Açıklama']}")
        self.canvas.draw()

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            root = tk.Tk()
            app = GalaxyComparer(root)
            root.mainloop()
        except Exception as e:
            print("Hata oluştu:", e)
    else:
        print("Bu program yalnızca Windows ortamı için tasarlanmıştır.")
