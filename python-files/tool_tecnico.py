import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import urllib.request
import socket
import uuid

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# Colori hacker style
BG_COLOR = "#000000"          # nero
FG_COLOR = "#39FF14"          # verde brillante
BTN_BG = "#002200"            # verde scuro bottone
BTN_HOVER_BG = "#006600"      # verde hover bottone
TITLE_BAR_BG = "#000000"      # barra titolo nera
TITLE_FG = "#39FF14"          # testo verde

def download_supremo():
    try:
        url = "https://www.nanosystems.it/public/download/Supremo.exe"
        local_path = os.path.join(desktop_path, "Supremo.exe")
        urllib.request.urlretrieve(url, local_path)
        messagebox.showinfo("Download", "✅ Supremo scaricato correttamente sul desktop.")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel download di Supremo:\n{e}")

def get_serial_number():
    try:
        # Eseguo il comando e catturo l'output
        output = subprocess.check_output("wmic bios get serialnumber", shell=True, text=True)
        # Pulisco l'output per mostrare solo il serial number
        lines = output.strip().split('\n')
        if len(lines) >= 2:
            serial = lines[1].strip()
        else:
            serial = "Serial number non trovato"
    except Exception as e:
        serial = f"Errore nel recupero serial number:\n{e}"

    # Popup per mostrare il serial number
    popup = tk.Toplevel()
    popup.title("Serial Number")
    popup.configure(bg=BG_COLOR)
    popup.geometry("400x150")
    popup.resizable(False, False)

    label = tk.Label(popup, text="Serial Number del PC:", bg=BG_COLOR, fg=FG_COLOR,
                     font=("Consolas", 14, "bold"), pady=10)
    label.pack()

    serial_label = tk.Label(popup, text=serial, bg=BG_COLOR, fg=FG_COLOR,
                            font=("Consolas", 16), pady=10)
    serial_label.pack()

    btn_close = tk.Button(popup, text="Chiudi", command=popup.destroy,
                          bg=BTN_BG, fg=FG_COLOR, activebackground=BTN_HOVER_BG,
                          font=("Consolas", 12), relief="raised", bd=3, width=10)
    btn_close.pack(pady=10)

    popup.grab_set()
    popup.focus_set()
    popup.wait_window()

def avvia_supremo_e_istruzioni():
    try:
        exe_path = os.path.join(desktop_path, "Supremo.exe")
        if not os.path.exists(exe_path):
            messagebox.showerror("Errore", "Supremo non trovato sul desktop.")
            return
        
        subprocess.Popen(exe_path, shell=True)

        popup = tk.Toplevel()
        popup.title("Attendere")
        popup.configure(bg=BG_COLOR)
        popup.geometry("450x150")
        label = tk.Label(popup, text="Attendere 5 secondi per l'avvio di Supremo...", pady=50,
                         bg=BG_COLOR, fg=FG_COLOR, font=("Consolas", 14))
        label.pack(expand=True)
        popup.after(5000, popup.destroy)
        popup.grab_set()
        popup.focus_set()
        popup.wait_window()

        istruzioni_popup = tk.Toplevel()
        istruzioni_popup.title("Istruzioni Supporto Tecnico")
        istruzioni_popup.configure(bg=BG_COLOR)
        istruzioni_popup.geometry("500x300")

        testo = (
            "Leggere l'ID e la password temporanea da Supremo e inserirli nella scheda di supporto.\n\n"
            "Questi dati permetteranno di completare correttamente l'installazione e la configurazione remota.\n\n"
            "Assicurarsi di verificare che i dati inseriti siano corretti prima di procedere."
        )

        label_istruzioni = tk.Label(istruzioni_popup, text=testo, wraplength=460, justify="left",
                                    padx=15, pady=15, bg=BG_COLOR, fg=FG_COLOR,
                                    font=("Consolas", 12))
        label_istruzioni.pack(expand=True, fill="both")

        btn_ok = tk.Button(istruzioni_popup, text="OK", width=12, command=istruzioni_popup.destroy,
                           bg=BTN_BG, fg=FG_COLOR, activebackground=BTN_HOVER_BG,
                           font=("Consolas", 12), relief="raised", bd=3)
        btn_ok.pack(pady=15)

        istruzioni_popup.grab_set()
        istruzioni_popup.focus_set()
        istruzioni_popup.wait_window()

    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'avvio di Supremo:\n{e}")

def get_ip_mac_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "Non disponibile"

    try:
        import requests
        public_ip = requests.get('https://api.ipify.org').text
    except Exception:
        public_ip = "Non disponibile"

    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                        for ele in range(0,8*6,8)][::-1])
    except Exception:
        mac = "Non disponibile"

    info_text = (
        f"IP Locale: {local_ip}\n"
        f"IP Pubblico: {public_ip}\n"
        f"MAC Address: {mac}"
    )

    messagebox.showinfo("Informazioni Rete", info_text)

def pulizia_file_temporanei():
    import shutil
    try:
        temp_path = os.environ.get('TEMP')
        if not temp_path or not os.path.exists(temp_path):
            messagebox.showerror("Errore", "Cartella temporanea non trovata.")
            return

        for root_dir, dirs, files in os.walk(temp_path):
            for file in files:
                try:
                    os.remove(os.path.join(root_dir, file))
                except Exception:
                    pass
            for dir in dirs:
                try:
                    shutil.rmtree(os.path.join(root_dir, dir))
                except Exception:
                    pass

        messagebox.showinfo("Pulizia", "✅ Pulizia file temporanei completata.")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la pulizia:\n{e}")

def on_enter(e):
    e.widget['background'] = BTN_HOVER_BG

def on_leave(e):
    e.widget['background'] = BTN_BG

def mostra_contatti():
    info_text = (
        "Marco Lauricella\n"
        "Cellulare: 334 165 9620\n"
        "Email: m.lauricella@solutionict.it"
    )
    messagebox.showinfo("Contatti", info_text)

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f'+{x}+{y}')

root = tk.Tk()
root.title("Censimento Supremo SKS")
root.geometry("700x450")
root.configure(bg=BG_COLOR)
root.overrideredirect(True)

title_bar = tk.Frame(root, bg=TITLE_BAR_BG, relief='raised', bd=0, highlightthickness=0)
title_bar.pack(fill='x')

title_label = tk.Label(title_bar, text="Censimento Supremo SKS", bg=TITLE_BAR_BG, fg=TITLE_FG,
                       font=("Consolas", 14, "bold"))
title_label.pack(side='left', padx=10)

def close_window():
    root.destroy()

close_button = tk.Button(title_bar, text='✕', bg='#AA0000', fg='white', bd=0,
                         font=("Consolas", 14, "bold"), command=close_window,
                         activebackground='#FF4444', padx=10, pady=2)
close_button.pack(side='right')

title_bar.bind('<Button-1>', start_move)
title_bar.bind('<ButtonRelease-1>', stop_move)
title_bar.bind('<B1-Motion>', do_move)
title_label.bind('<Button-1>', start_move)
title_label.bind('<ButtonRelease-1>', stop_move)
title_label.bind('<B1-Motion>', do_move)

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(expand=True, fill='both')

menu_bar = tk.Menu(root)
info_menu = tk.Menu(menu_bar, tearoff=0)
info_menu.add_command(label="Contatti", command=mostra_contatti)
menu_bar.add_cascade(label="Info", menu=info_menu)

def open_info_menu():
    try:
        info_menu.tk_popup(root.winfo_rootx() + 10, root
