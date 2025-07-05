import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import os

# Cálculos

def calcular_circulo_y_cilindro(radio_cm, altura_cm):
    diametro_cm = 2 * radio_cm
    perimetro = 2 * np.pi * radio_cm
    area_circulo = np.pi * radio_cm**2
    area_lateral = 2 * np.pi * radio_cm * altura_cm
    area_total = 2 * area_circulo + area_lateral
    volumen = area_circulo * altura_cm

    resultados = {
        "radio": radio_cm,
        "diametro": diametro_cm,
        "perimetro": perimetro,
        "area_circulo": area_circulo,
        "area_lateral": area_lateral,
        "area_total": area_total,
        "volumen": volumen
    }
    return resultados

# Dibujo

def dibujar_circulo_y_cilindro(radio_cm, altura_cm, frame):
    diametro_cm = 2 * radio_cm
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    circle = plt.Circle((0, 0), radio_cm, fill=False, edgecolor='blue')
    axs[0].add_patch(circle)
    axs[0].plot([0, radio_cm], [0, 0], color='red', linestyle='--')
    axs[0].text(radio_cm / 2, 0.8, f'Radio = {radio_cm} cm', color='red')

    circunferencia = 2 * np.pi * radio_cm
    mm_total = int(circunferencia * 10)

    for i in range(mm_total):
        angle = (2 * np.pi / mm_total) * i
        x_outer = (radio_cm + (0.6 if i % 10 == 0 else 0.3)) * np.cos(angle)
        y_outer = (radio_cm + (0.6 if i % 10 == 0 else 0.3)) * np.sin(angle)
        x_inner = radio_cm * np.cos(angle)
        y_inner = radio_cm * np.sin(angle)
        axs[0].plot([x_inner, x_outer], [y_inner, y_outer], color='green' if i % 10 == 0 else 'gray', lw=1)

        if i % 10 == 0:
            etiqueta = f'{i // 10}'
            label_x = (radio_cm + 1.2) * np.cos(angle)
            label_y = (radio_cm + 1.2) * np.sin(angle)
            axs[0].text(label_x, label_y, etiqueta, fontsize=6, ha='center', va='center', color='green')

    axs[0].set_xlim(-radio_cm - 3, radio_cm + 3)
    axs[0].set_ylim(-radio_cm - 3, radio_cm + 3)
    axs[0].set_aspect('equal')
    axs[0].set_title('Círculo con regla')

    theta = np.linspace(0, 2 * np.pi, 100)
    x_top = radio_cm * np.cos(theta)
    y_top = radio_cm * np.sin(theta) + altura_cm
    x_bottom = radio_cm * np.cos(theta)
    y_bottom = radio_cm * np.sin(theta)

    axs[1].plot(x_top, y_top, color='blue')
    axs[1].plot(x_bottom, y_bottom, color='blue')
    axs[1].plot([radio_cm, radio_cm], [0, altura_cm], color='red', linestyle='--')
    axs[1].text(radio_cm + 1, altura_cm / 2, f'Altura = {altura_cm} cm', color='red')
    axs[1].text(0, -radio_cm - 2, f'Diámetro = {diametro_cm} cm', color='red', ha='center')
    axs[1].set_aspect('equal')
    axs[1].set_xlim(-radio_cm - 4, radio_cm + 4)
    axs[1].set_ylim(-radio_cm - 4, altura_cm + radio_cm + 3)
    axs[1].set_title('Cilindro')

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    return fig

# Exportar PDF

def exportar_pdf(resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Resultados del Círculo y Cilindro", ln=True, align='C')

    for clave, valor in resultados.items():
        pdf.cell(200, 10, txt=f"{clave.capitalize()}: {valor:.2f} cm", ln=True)

    pdf.output("resultados_cilindro.pdf")
    os.startfile("resultados_cilindro.pdf")

# GUI

def main():
    root = tk.Tk()
    root.title("Calculadora de Círculo y Cilindro")

    tk.Label(root, text="Radio (cm):").grid(row=0, column=0)
    entry_radio = tk.Entry(root)
    entry_radio.grid(row=0, column=1)

    tk.Label(root, text="Altura (cm):").grid(row=1, column=0)
    entry_altura = tk.Entry(root)
    entry_altura.grid(row=1, column=1)

    frame_grafico = tk.Frame(root)
    frame_grafico.grid(row=3, column=0, columnspan=2)

    def calcular_y_mostrar():
        try:
            radio = float(entry_radio.get())
            altura = float(entry_altura.get())
            resultados = calcular_circulo_y_cilindro(radio, altura)
            for widget in frame_grafico.winfo_children():
                widget.destroy()
            dibujar_circulo_y_cilindro(radio, altura, frame_grafico)
            exportar_pdf(resultados)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos.")

    tk.Button(root, text="Calcular e Imprimir", command=calcular_y_mostrar).grid(row=2, column=0, columnspan=2, pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
