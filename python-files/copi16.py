import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading, os, time
from datetime import datetime

__author__   = "Yoki + IA COPILOT"
LOG_FILE     = "copy_log.txt"
RESUME_FILE  = "resume_list.txt"
SUMMARY_NAME = "copy_summary.txt"

# Variables y función del cronómetro
cronometro_activo = False
t0_crono = 0.0

def actualizar_cronometro():
    if not cronometro_activo:
        return
    elapsed = time.time() - t0_crono
    lbl_timer.config(text=f"Tiempo: {elapsed:.1f} s")
    ventana.after(100, actualizar_cronometro)

# Modos de copia
SPEED_MODES = {
    "Lenta":       {"buffer":  64 * 1024,      "delay": 0.02},
    "Moderada":    {"buffer": 32 * 1024,       "delay": 0.01},
    "Ultrarrápida":{"buffer": 4 * 1024 * 1024, "delay": 0.0}
}

paused = False

def registrar_log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

def seleccionar_archivos():
    files = filedialog.askopenfilenames(title="Selecciona archivos")
    lista_archivos.set(list(files))

def cargar_lista_txt():
    path = filedialog.askopenfilename(
        title="Cargar lista desde .txt",
        filetypes=[("Texto", "*.txt")]
    )
    if not path: return
    with open(path, 'r', encoding='utf-8') as f:
        rutas = [l.strip() for l in f if l.strip()]
    validas = [r for r in rutas if os.path.isfile(r)]
    if len(validas) < len(rutas):
        messagebox.showwarning("Aviso",
            f"Omitidos {len(rutas)-len(validas)} rutas no válidas")
    lista_archivos.set(validas)
    registrar_log(f"Cargada lista ({len(validas)}) desde {path}")

def guardar_lista_txt():
    rutas = list(lista_archivos.get())
    if not rutas:
        return messagebox.showwarning("Aviso", "No hay rutas para guardar.")
    path = filedialog.asksaveasfilename(
        title="Guardar lista a .txt",
        defaultextension=".txt",
        filetypes=[("Texto", "*.txt")]
    )
    if not path: return
    with open(path, 'w', encoding='utf-8') as f:
        for r in rutas: f.write(r + "\n")
    registrar_log(f"Lista guardada ({len(rutas)}) en {path}")

def copiar_archivo(src, dst, buf_size, delay):
    size   = os.path.getsize(src)
    inicio = time.time()
    with open(src, 'rb') as r, open(dst, 'wb') as w:
        while True:
            if paused:
                time.sleep(0.2)
                continue
            chunk = r.read(buf_size)
            if not chunk: break
            w.write(chunk)
            if delay:
                time.sleep(delay)
    elapsed = time.time() - inicio or 1e-6
    speed   = (size / elapsed) / (1024 * 1024)
    return size, speed

def cargar_resume():
    if os.path.exists(RESUME_FILE):
        if messagebox.askyesno("Reanudar copia", 
                               "Sesión anterior detectada. ¿Reanudar?"):
            with open(RESUME_FILE,'r', encoding='utf-8') as f:
                return [l.strip() for l in f if l.strip()]
        else:
            os.remove(RESUME_FILE)
    return []

def pause_copy():
    global paused
    paused = True
    btn_pause.config(state='disabled')
    btn_resume.config(state='normal')
    registrar_log("Copia pausada")

def resume_copy():
    global paused
    paused = False
    btn_pause.config(state='normal')
    btn_resume.config(state='disabled')
    registrar_log("Copia reanudada")

def copiar_archivos():
    rutas = cargar_resume() or list(lista_archivos.get())
    try:
        price  = float(entry_price.get())
        budget = float(entry_budget.get())
    except:
        return messagebox.showerror("Error","Precio o presupuesto inválido.")
    if not rutas:
        return messagebox.showwarning("Aviso","Lista vacía.")

    destino = filedialog.askdirectory(title="Selecciona destino")
    if not destino: return

    max_files = int(budget // price)
    rutas      = rutas[:max_files]
    total      = len(rutas)
    if total == 0:
        return messagebox.showinfo("Info","Presupuesto insuficiente.")

    modo     = speed_var.get()
    cfg      = SPEED_MODES[modo]
    buf_size = cfg["buffer"]
    delay    = cfg["delay"]
    registrar_log(f"Modo de copia seleccionado: {modo}")

    t0 = time.time()
    # Iniciar cronómetro
    global cronometro_activo, t0_crono
    t0_crono = t0
    cronometro_activo = True
    actualizar_cronometro()

    lbl_start.config(text="Inicio: " +
                     datetime.fromtimestamp(t0).strftime("%H:%M:%S"))
    registrar_log("Inicio de copia a las " + lbl_start.cget("text"))
    if os.path.exists(RESUME_FILE): os.remove(RESUME_FILE)

    copied = 0; bytes_total = 0; speeds = []
    progress_bar['maximum']= total; progress_bar['value']=0
    btn_pause.config(state='normal'); btn_resume.config(state='disabled')

    for src in rutas:
        name = os.path.basename(src)
        dst  = os.path.join(destino, name)
        try:
            size, speed = copiar_archivo(src, dst, buf_size, delay)
            bytes_total += size; speeds.append(speed); copied += 1
            registrar_log(f"Copiado {name}: {size/(1024**3):.2f}GB a {speed:.2f}MB/s")
        except Exception as e:
            registrar_log(f"Error {name}: {e}")
            rem = rutas[copied:]
            with open(RESUME_FILE,'w', encoding='utf-8') as f:
                for r in rem: f.write(r+"\n")
            messagebox.showerror("Error",
                f"{e}\nSe guardó reanudar en {RESUME_FILE}")
            break
        finally:
            progress_bar['value'] = copied
            lbl_pct.config(text=f"{copied/total*100:.2f}%")
            lbl_gb.config(text=f"Copiado: {bytes_total/(1024**3):.2f} GB")
            elapsed = time.time() - t0
            avg_per = elapsed / copied if copied else 0
            eta     = datetime.fromtimestamp(
                time.time() + avg_per * (total - copied)
            )
            lbl_eta.config(text="ETA: " + eta.strftime("%H:%M:%S"))
            ventana.update_idletasks()

    # Detener cronómetro
    cronometro_activo = False

    btn_pause.config(state='disabled'); btn_resume.config(state='disabled')
    tf = time.time()

    if copied > 0:
        spent   = copied * price
        change  = budget - spent
        avg_vel = sum(speeds) / len(speeds) if speeds else 0
        dur     = tf - t0
        lines = [
            "Resumen de copia","================",
            f"Inicio       : {datetime.fromtimestamp(t0).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Fin          : {datetime.fromtimestamp(tf).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duración     : {dur:.2f} seg",
            f"Archivos     : {copied} de {total}",
            f"Total copiado: {bytes_total/(1024**3):.2f} GB",
            f"Velocidad avg: {avg_vel:.2f} MB/s",
            f"Gasto total  : ${spent:.2f}",
            f"Cambio       : ${change:.2f}",
            f"Autor        : {__author__}"
        ]
        summary_path = os.path.join(destino, SUMMARY_NAME)
        with open(summary_path,'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        registrar_log(f"Resumen guardado en {summary_path}")
        lbl_change.config(text=f"Cambio: ${change:.2f}")

    if copied == total and total > 0:
        messagebox.showinfo("Éxito",
            f"{copied} archivos copiados\nResumen: {summary_path}")

def iniciar_thread():
    threading.Thread(target=copiar_archivos, daemon=True).start()

# — INTERFAZ —
ventana = tk.Tk()
ventana.title(f"Copiador Completo de Archivos – Autor: {__author__}")
ventana.geometry("540x780")
ventana.resizable(False, False)

# Menú
menubar = tk.Menu(ventana)
m_lista = tk.Menu(menubar, tearoff=0)
m_lista.add_command(label="Seleccionar archivos", command=seleccionar_archivos)
m_lista.add_command(label="Cargar lista TXT",    command=cargar_lista_txt)
m_lista.add_command(label="Guardar lista TXT",   command=guardar_lista_txt)
m_lista.add_separator()
m_lista.add_command(label="Salir",                command=ventana.quit)
menubar.add_cascade(label="Lista", menu=m_lista)
ventana.config(menu=menubar)

# Frame selección
frame1 = ttk.LabelFrame(ventana, text="Archivos y Presupuesto")
frame1.pack(fill='x', padx=10, pady=10)
lista_archivos = tk.Variable()
ttk.Button(frame1, text="Seleccionar archivos", command=seleccionar_archivos)\
    .grid(row=0,column=0,padx=5,pady=5)
ttk.Button(frame1, text="Cargar lista TXT",    command=cargar_lista_txt)\
    .grid(row=0,column=1,padx=5)
ttk.Button(frame1, text="Guardar lista TXT",   command=guardar_lista_txt)\
    .grid(row=0,column=2,padx=5)
ttk.Label(frame1, text="Precio ($):")\
    .grid(row=1,column=0,sticky='e',padx=5)
entry_price = ttk.Entry(frame1)
entry_price.grid(row=1,column=1)
ttk.Label(frame1, text="Presupuesto ($):")\
    .grid(row=2,column=0,sticky='e',padx=5)
entry_budget = ttk.Entry(frame1)
entry_budget.grid(row=2,column=1)
ttk.Label(frame1, text="Velocidad copia:")\
    .grid(row=3,column=0,sticky='e',padx=5)
speed_var = tk.StringVar(value="Moderada")
ttk.Combobox(frame1, textvariable=speed_var,
             values=list(SPEED_MODES.keys()), state='readonly')\
    .grid(row=3, column=1, pady=5)

# Frame progreso
frame2 = ttk.LabelFrame(ventana, text="Progreso y Tiempos")
frame2.pack(fill='x', padx=10, pady=10)
progress_bar = ttk.Progressbar(frame2, orient='horizontal',
                               length=500, mode='determinate')
progress_bar.pack(pady=5)
status = ttk.Frame(frame2)
status.pack(fill='x',padx=10)
lbl_pct   = ttk.Label(status, text="0.00%")
lbl_pct.pack(side='left')
lbl_gb    = ttk.Label(status, text="Copiado: 0.00 GB")
lbl_gb.pack(side='left',padx=10)
lbl_start = ttk.Label(status, text="Inicio: --:--:--")
lbl_start.pack(side='right')
lbl_eta   = ttk.Label(status, text="ETA: --:--:--")
lbl_eta.pack(side='right',padx=20)

lbl_change = ttk.Label(ventana, text="Cambio: $0.00")
lbl_change.pack(pady=5)

# Etiqueta del cronómetro
lbl_timer = ttk.Label(ventana, text="Tiempo: 0.0 s")
lbl_timer.pack(pady=5)

# Botones control
ctrl = ttk.Frame(ventana)
ctrl.pack(pady=10)
btn_start  = ttk.Button(ctrl, text="Iniciar copia", command=iniciar_thread)
btn_start.grid(row=0,column=0,padx=5)
btn_pause  = ttk.Button(ctrl, text="Pausar",    command=pause_copy,
                        state='disabled')
btn_pause.grid(row=0,column=1,padx=5)
btn_resume = ttk.Button(ctrl, text="Reanudar",  command=resume_copy,
                        state='disabled')
btn_resume.grid(row=0,column=2,padx=5)

# Autor en interfaz
ttk.Label(ventana, text=f"Autor: {__author__}",
          font=("Segoe UI",8,"italic"))\
    .pack(side='bottom', pady=4)

ventana.mainloop()
