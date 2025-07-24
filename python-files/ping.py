import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import ipaddress

def hacer_ping(ip):
    try:
        output = subprocess.run(
            ["ping", "-n", "1", "-w", "300", str(ip)],
            stdout=subprocess.DEVNULL
        )
        return output.returncode == 0
    except:
        return False

def validar_ips():
    entrada = campo_ip.get().strip()
    resultado_text.delete(1.0, tk.END)

    # Detectar si es rango o IP única
    if "-" in entrada:
        try:
            ip_inicio, ip_fin = entrada.split("-")
            ip_base = ipaddress.IPv4Address(ip_inicio.strip())
            ip_final = ipaddress.IPv4Address(ip_fin.strip())
            if ip_final < ip_base:
                raise ValueError("Rango inválido")

            lista_ips = [ipaddress.IPv4Address(ip) for ip in range(int(ip_base), int(ip_final)+1)]
        except:
            messagebox.showerror("Error", "Formato de rango inválido. Usa: 192.168.1.1-192.168.1.10")
            return
    else:
        try:
            ip = ipaddress.IPv4Address(entrada)
            lista_ips = [ip]
        except:
            messagebox.showerror("Error", "IP inválida.")
            return

    # Deshabilitar botón mientras se ejecuta
    boton_ping.config(state=tk.DISABLED)
    resultado_text.insert(tk.END, f"Validando {len(lista_ips)} IP(s)...\n\n")
    ventana.update()

    def ejecutar_ping():
        for ip in lista_ips:
            ok = hacer_ping(ip)
            estado = "✅ Responde" if ok else "❌ No responde"
            resultado_text.insert(tk.END, f"{ip} --> {estado}\n")
        boton_ping.config(state=tk.NORMAL)

    threading.Thread(target=ejecutar_ping).start()

# GUI
ventana = tk.Tk()
ventana.title("Validador de IP por Ping")
ventana.geometry("450x400")

tk.Label(ventana, text="IP o Rango (ej. 192.168.1.1 o 192.168.1.1-192.168.1.10):").pack(pady=10)
campo_ip = tk.Entry(ventana, width=40)
campo_ip.pack()

boton_ping = tk.Button(ventana, text="Validar", command=validar_ips)
boton_ping.pack(pady=10)

resultado_text = scrolledtext.ScrolledText(ventana, width=50, height=15)
resultado_text.pack(pady=10)

ventana.mainloop()
