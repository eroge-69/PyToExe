import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
import time
import threading

# ===== Variables globales =====
start_bytes_sent = psutil.net_io_counters().bytes_sent
start_bytes_recv = psutil.net_io_counters().bytes_recv

# Función para formatear bytes
def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

# ===== Actualización de datos =====
def update_stats():
    prev_sent = psutil.net_io_counters().bytes_sent
    prev_recv = psutil.net_io_counters().bytes_recv
    prev_time = time.time()

    while True:
        time.sleep(1)
        now = time.time()
        sent = psutil.net_io_counters().bytes_sent
        recv = psutil.net_io_counters().bytes_recv

        elapsed = now - prev_time
        upload_speed = (sent - prev_sent) / elapsed
        download_speed = (recv - prev_recv) / elapsed

        session_upload = sent - start_bytes_sent
        session_download = recv - start_bytes_recv

        prev_sent = sent
        prev_recv = recv
        prev_time = now

        # CPU, RAM
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        # GPU
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_load = gpus[0].load * 100
                gpu_mem = gpus[0].memoryUsed
                gpu_temp = gpus[0].temperature
            else:
                gpu_load, gpu_mem, gpu_temp = 0, 0, 0
        except:
            gpu_load, gpu_mem, gpu_temp = 0, 0, 0

        # ===== Actualizar UI =====
        lbl_upload_speed.config(text=f"↑ {upload_speed/1024:.2f} KB/s")
        lbl_download_speed.config(text=f"↓ {download_speed/1024:.2f} KB/s")
        lbl_session.config(text=f"Sesión: ↑ {format_bytes(session_upload)} / ↓ {format_bytes(session_download)}")

        lbl_cpu_text.config(text=f"CPU: {cpu:.1f}%")
        bar_cpu['value'] = cpu

        lbl_ram_text.config(text=f"RAM: {ram:.1f}%")
        bar_ram['value'] = ram

        lbl_gpu_text.config(text=f"GPU: {gpu_load:.1f}% | Mem: {gpu_mem}MB | Temp: {gpu_temp}°C")
        bar_gpu['value'] = gpu_load

# ===== Ventana principal =====
root = tk.Tk()
root.title("MONITOR GAMER")

# Obtener tamaño de pantalla y centrar ventana
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 800
window_height = 600
pos_x = (screen_width // 2) - (window_width // 2)
pos_y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
root.configure(bg="#0a0a0a")  # Fondo oscuro

# ===== Estilo gamer =====
style = ttk.Style()
style.theme_use("clam")
style.configure("TProgressbar", troughcolor="#1a1a1a", bordercolor="#1a1a1a",
                background="#00ffcc", lightcolor="#00ffcc", darkcolor="#00ffcc")

# Fuentes más grandes
font_title = ("Consolas", 28, "bold")
font_data = ("Consolas", 20)

# ===== Contenedor central =====
main_frame = tk.Frame(root, bg="#0a0a0a")
main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Centrado absoluto

# ===== Frame Red =====
frame_net = tk.Frame(main_frame, bg="#0a0a0a")
frame_net.pack(pady=25)

lbl_title_net = tk.Label(frame_net, text="RED", font=font_title, fg="#00ffcc", bg="#0a0a0a")
lbl_title_net.pack()

lbl_upload_speed = tk.Label(frame_net, text="↑ 0 KB/s", font=font_data, fg="#00ff00", bg="#0a0a0a")
lbl_upload_speed.pack()

lbl_download_speed = tk.Label(frame_net, text="↓ 0 KB/s", font=font_data, fg="#ff0000", bg="#0a0a0a")
lbl_download_speed.pack()

lbl_session = tk.Label(frame_net, text="Sesión: ↑ 0 B / ↓ 0 B", font=font_data, fg="#ffffff", bg="#0a0a0a")
lbl_session.pack()

# ===== Frame Hardware =====
frame_hw = tk.Frame(main_frame, bg="#0a0a0a")
frame_hw.pack(pady=35)

lbl_title_hw = tk.Label(frame_hw, text="HARDWARE", font=font_title, fg="#ff00ff", bg="#0a0a0a")
lbl_title_hw.pack(pady=(0, 20))

# RAM
lbl_ram_text = tk.Label(frame_hw, text="RAM: 0%", font=font_data, fg="#ffffff", bg="#0a0a0a")
lbl_ram_text.pack(pady=10)
bar_ram = ttk.Progressbar(frame_hw, orient="horizontal", length=500, mode="determinate")
bar_ram.pack(pady=5)

# CPU
lbl_cpu_text = tk.Label(frame_hw, text="CPU: 0%", font=font_data, fg="#ffffff", bg="#0a0a0a")
lbl_cpu_text.pack(pady=10)
bar_cpu = ttk.Progressbar(frame_hw, orient="horizontal", length=500, mode="determinate")
bar_cpu.pack(pady=5)

# GPU
lbl_gpu_text = tk.Label(frame_hw, text="GPU: 0%", font=font_data, fg="#ffffff", bg="#0a0a0a")
lbl_gpu_text.pack(pady=10)
bar_gpu = ttk.Progressbar(frame_hw, orient="horizontal", length=500, mode="determinate")
bar_gpu.pack(pady=5)

# ===== Hilo de actualización =====
threading.Thread(target=update_stats, daemon=True).start()

root.mainloop()

