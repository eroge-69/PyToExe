import ipaddress
import tkinter as tk
from tkinter import messagebox, scrolledtext

def calcular_red():
    entrada = entrada_ip.get()

    try:
        red = ipaddress.ip_network(entrada, strict=False)
        ip_obj = ipaddress.ip_interface(entrada).ip
        hosts = list(red.hosts())

        network_address = red.network_address
        broadcast_address = red.broadcast_address
        netmask = red.netmask
        gateway = hosts[0] if hosts else None

        resultado = []
        resultado.append("--- DATOS DE LA RED ---")
        resultado.append(f"Dirección de red (Network): {network_address}")
        resultado.append(f"Máscara de red: {netmask}")
        resultado.append(f"Broadcast: {broadcast_address}")
        
        if hosts:
            resultado.append(f"Gateway (primera IP utilizable): {gateway}")
            resultado.append(f"Cantidad de hosts utilizables: {len(hosts)}")
            resultado.append(f"Rango de hosts utilizables: {hosts[0]} - {hosts[-1]}")
        else:
            resultado.append("Esta red no tiene hosts utilizables.")

        resultado.append("\n--- VALIDACIÓN DE LA IP INGRESADA ---")
        if ip_obj == network_address:
            resultado.append("La IP ingresada es la **dirección de red**. No se puede asignar a un dispositivo.")
        elif ip_obj == broadcast_address:
            resultado.append("La IP ingresada es la **dirección de broadcast**. No se puede asignar a un dispositivo.")
        elif gateway and ip_obj == gateway:
            resultado.append("La IP ingresada es la **gateway (primera IP utilizable)**.")
        elif ip_obj in hosts:
            resultado.append("La IP ingresada es una **IP válida y utilizable** dentro del rango de hosts.")
        else:
            resultado.append("⚠️ La IP ingresada **no es válida para usar como host** en esta red.")

        # Mostrar resultado en el cuadro de texto
        salida_texto.delete("1.0", tk.END)
        salida_texto.insert(tk.END, "\n".join(resultado))

    except ValueError:
        messagebox.showerror("Error", "❌ Entrada inválida. Usa el formato CIDR, ej: 192.168.1.6/30")

# --- Interfaz con Tkinter ---
ventana = tk.Tk()
ventana.title("Calculadora de Red IP")
ventana.geometry("600x500")

tk.Label(ventana, text="Ingrese la IP con su máscara (CIDR):", font=("Arial", 12)).pack(pady=10)

entrada_ip = tk.Entry(ventana, font=("Courier", 14), width=30, justify="center")
entrada_ip.pack(pady=5)
entrada_ip.insert(0, "192.168.1.6/30")  # valor por defecto

tk.Button(ventana, text="Calcular", font=("Arial", 12), command=calcular_red).pack(pady=10)

salida_texto = scrolledtext.ScrolledText(ventana, width=70, height=20, font=("Courier", 10))
salida_texto.pack(pady=10)

ventana.mainloop()
