import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import csv
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BilanciaApp:
    """
    Applicazione con interfaccia grafica per leggere i dati da una bilancia USB,
    visualizzarli in tempo reale (con tabella e grafico) e salvarli su file.
    Versione ottimizzata per la creazione di file eseguibili (.exe).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Acquisizione Dati Bilancia USB")
        self.root.geometry("800x800")

        # Variabili di stato
        self.serial_connection = None
        self.is_reading = False
        self.is_paused = False
        self.reading_thread = None
        self.weight_data = []
        self.reading_interval = tk.DoubleVar(value=1.0)
        self.start_time = 0

        # --- Dettagli Esperimento ---
        exp_details_frame = ttk.LabelFrame(self.root, text="Dettagli Esperimento", padding="10")
        exp_details_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.exp_name = tk.StringVar()
        self.tela_name = tk.StringVar()
        self.pressione_val = tk.StringVar()

        ttk.Label(exp_details_frame, text="Nome Esperimento:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.exp_name_entry = ttk.Entry(exp_details_frame, textvariable=self.exp_name, width=30)
        self.exp_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(exp_details_frame, text="Tipo di Tela:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.tela_name_entry = ttk.Entry(exp_details_frame, textvariable=self.tela_name, width=30)
        self.tela_name_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(exp_details_frame, text="Pressione:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.pressione_val_entry = ttk.Entry(exp_details_frame, textvariable=self.pressione_val, width=15)
        self.pressione_val_entry.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        exp_details_frame.columnconfigure(1, weight=1)

        # --- Controlli ---
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side="top", fill="x", padx=10)

        ttk.Label(control_frame, text="Intervallo (s):").pack(side="left", padx=(0, 5))
        ttk.Entry(control_frame, textvariable=self.reading_interval, width=5).pack(side="left", padx=(0, 20))
        
        # --- PULSANTI CON TESTO SEMPLICE PER COMPATIBILITA' ---
        self.play_button = ttk.Button(control_frame, text="Play", command=self.play_reading)
        self.play_button.pack(side="left", padx=5)

        self.pause_button = ttk.Button(control_frame, text="Pausa", command=self.toggle_pause_reading, state="disabled")
        self.pause_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_reading, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        self.save_txt_button = ttk.Button(control_frame, text="Salva .txt", command=lambda: self.save_data("txt"), state="disabled")
        self.save_txt_button.pack(side="right", padx=5)
        
        self.save_csv_button = ttk.Button(control_frame, text="Salva .csv", command=lambda: self.save_data("csv"), state="disabled")
        self.save_csv_button.pack(side="right", padx=5)

        # --- Visualizzazione Dati ---
        data_frame = ttk.Frame(self.root, padding="10")
        data_frame.pack(side="top", fill="x", padx=10)

        ttk.Label(data_frame, text="Peso Attuale:", font=("Helvetica", 14)).pack(side="left")
        self.weight_label = ttk.Label(data_frame, text="--.--", font=("Helvetica", 24, "bold"), foreground="blue")
        self.weight_label.pack(side="left", padx=10)
        ttk.Label(data_frame, text="g", font=("Helvetica", 14)).pack(side="left", anchor="s")

        self.status_label = ttk.Label(data_frame, text="Stato: In ricerca della bilancia...", foreground="orange")
        self.status_label.pack(side="right", padx=10)

        # --- Tabella Dati ---
        table_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        table_frame.pack(fill="x", padx=10)
        
        columns = ('tempo', 'peso')
        self.data_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
        self.data_table.heading('tempo', text='Tempo (s)')
        self.data_table.heading('peso', text='Peso (g)')
        self.data_table.column('tempo', width=100, anchor='center')
        self.data_table.column('peso', width=100, anchor='center')
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_table.yview)
        self.data_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.data_table.pack(side='left', fill='x', expand=True)

        # --- Grafico ---
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Grafico Peso vs. Tempo")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Peso (g)")
        self.ax.grid(True)
        self.line, = self.ax.plot([], [], 'r-o', markersize=4)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        
        self.find_scale_thread = threading.Thread(target=self.find_scale, daemon=True)
        self.find_scale_thread.start()

    def find_scale(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2)
                line = ser.readline()
                if not line:
                    ser.close()
                    continue
                peso_str = line.decode('utf-8', errors='ignore').strip()
                float(peso_str.replace(",", "."))
                self.serial_connection = ser
                self.root.after(0, self.update_status, f"Stato: Bilancia trovata su {port.device}", "green")
                return
            except (serial.SerialException, ValueError, TypeError):
                if 'ser' in locals() and ser.is_open:
                    ser.close()
                continue
        self.root.after(0, self.update_status, "Stato: Nessuna bilancia trovata. Controlla la connessione.", "red")

    def play_reading(self):
        if not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Errore", "La bilancia non è connessa o non è stata trovata.")
            return
        if not self.exp_name.get():
            messagebox.showwarning("Dati Mancanti", "Per favore, inserisci il nome dell'esperimento.")
            return

        self.is_reading = True
        self.is_paused = False
        self.weight_data = []
        for i in self.data_table.get_children():
            self.data_table.delete(i)
        self.start_time = time.time()

        self.play_button.config(state="disabled")
        self.pause_button.config(state="normal", text="Pausa")
        self.stop_button.config(state="normal")
        self.save_txt_button.config(state="disabled")
        self.save_csv_button.config(state="disabled")
        self.exp_name_entry.config(state="disabled")
        self.tela_name_entry.config(state="disabled")
        self.pressione_val_entry.config(state="disabled")
        self.update_status("Stato: Lettura in corso...", "blue")

        self.reading_thread = threading.Thread(target=self.read_data_loop, daemon=True)
        self.reading_thread.start()

    def toggle_pause_reading(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Riprendi")
            self.update_status("Stato: Lettura in pausa.", "orange")
        else:
            self.pause_button.config(text="Pausa")
            self.update_status("Stato: Lettura in corso...", "blue")

    def stop_reading(self):
        self.is_reading = False
        if self.reading_thread and self.reading_thread.is_alive():
            self.reading_thread.join()

        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pausa")
        self.stop_button.config(state="disabled")
        self.save_txt_button.config(state="normal" if self.weight_data else "disabled")
        self.save_csv_button.conf