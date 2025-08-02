import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import serial.tools.list_ports
import time
import csv
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BilanciaApp:
    """
    Applicazione con interfaccia grafica per leggere i dati da una bilancia USB.
    Versione Definitiva: completamente single-thread utilizzando tkinter.after()
    per la massima stabilità e compatibilità con gli eseguibili (.exe).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Acquisizione Dati Bilancia USB (v. Definitiva)")
        self.root.geometry("800x800")

        # Variabili di stato
        self.serial_connection = None
        self.is_reading = False
        self.is_paused = False
        self.weight_data = []
        self.reading_interval = tk.DoubleVar(value=1.0)
        self.start_time = 0
        self.polling_job = None
        self.ports_to_scan = []

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
        
        # Avvia la ricerca della bilancia usando il metodo after()
        self.root.after(200, self.start_scale_search)

    def start_scale_search(self):
        """Prepara e avvia la scansione delle porte."""
        self.ports_to_scan = serial.tools.list_ports.comports()
        if not self.ports_to_scan:
            self.update_status("Stato: Nessuna porta COM/USB trovata.", "red")
            return
        self.scan_next_port()

    def scan_next_port(self):
        """Scansiona una porta alla volta per non bloccare la GUI."""
        if not self.ports_to_scan:
            self.update_status("Stato: Nessuna bilancia trovata. Controlla la connessione.", "red")
            return

        port_info = self.ports_to_scan.pop(0)
        try:
            ser = serial.Serial(port_info.device, 9600, timeout=1)
            # Diamo un attimo alla porta per stabilizzarsi
            time.sleep(1.5) 
            line = ser.readline()
            ser.close()

            if line:
                peso_str = line.decode('utf-8', errors='ignore').strip()
                float(peso_str.replace(",", "."))
                
                # Bilancia trovata!
                self.serial_connection = serial.Serial(port_info.device, 9600, timeout=1)
                self.update_status(f"Stato: Bilancia trovata su {port_info.device}", "green")
                return # Interrompe la scansione
        except (serial.SerialException, ValueError, TypeError):
            # Se questa porta non va, programma la scansione della prossima
            self.root.after(50, self.scan_next_port)

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

        self.poll_scale()

    def toggle_pause_reading(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Riprendi")
            self.update_status("Stato: Lettura in pausa.", "orange")
        else:
            self.pause_button.config(text="Pausa")
            self.update_status("Stato: Lettura in corso...", "blue")
            self.poll_scale()

    def stop_reading(self):
        self.is_reading = False
        if self.polling_job:
            self.root.after_cancel(self.polling_job)
            self.polling_job = None

        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pausa")
        self.stop_button.config(state="disabled")
        self.save_txt_button.config(state="normal" if self.weight_data else "disabled")
        self.save_csv_button.config(state="normal" if self.weight_data else "disabled")
        self.exp_name_entry.config(state="normal")
        self.tela_name_entry.config(state="normal")
        self.pressione_val_entry.config(state="normal")
        self.update_status("Stato: Lettura fermata.", "green")

    def poll_scale(self):
        if not self.is_reading or self.is_paused:
            return

        try:
            if self.serial_connection and self.serial_connection.is_open:
                line = self.serial_connection.readline()
                if line:
                    peso_str = line.decode('utf-8', errors='ignore').strip()
                    peso = float(peso_str.replace(",", "."))
                    elapsed_time = time.time() - self.start_time
                    self.weight_data.append((elapsed_time, peso))
                    self.update_gui()
        except (serial.SerialException, ValueError, TypeError) as e:
            messagebox.showerror("Errore di Lettura", f"Errore: {e}\nLettura interrotta.")
            self.stop_reading()
            return
        
        interval_ms = int(self.reading_interval.get() * 1000)
        self.polling_job = self.root.after(interval_ms, self.poll_scale)

    def update_gui(self):
        if not self.weight_data: return
        last_time, last_weight = self.weight_data[-1]
        self.weight_label.config(text=f"{last_weight:.2f}")
        self.data_table.insert('', 'end', values=(f"{last_time:.2f}", f"{last_weight:.2f}"))
        self.data_table.yview_moveto(1)
        times = [d[0] for d in self.weight_data]
        weights = [d[1] for d in self.weight_data]
        self.line.set_data(times, weights)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()

    def save_data(self, file_format):
        if not self.weight_data:
            messagebox.showinfo("Nessun Dato", "Non ci sono dati da salvare.")
            return
        
        exp = self.exp_name.get().replace(" ", "_") or "esperimento"
        tela = self.tela_name.get().replace(" ", "_") or "tela_ignota"
        press = self.pressione_val.get().replace(" ", "_") or "pressione_ignota"
        filename = f"{exp}_{tela}_{press}"

        file_types = [("File CSV", "*.csv")] if file_format == "csv" else [("File di Testo", "*.txt")]
        extension = f".{file_format}"
        filepath = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=file_types,
            initialfile=f"{filename}{extension}"
        )
        if not filepath:
            return
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if file_format == "csv":
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(['Tempo (s)', 'Peso (g)'])
                    for time_val, weight_val in self.weight_data:
                        writer.writerow([f"{time_val:.2f}", f"{weight_val:.2f}"])
                else:
                    f.write("Tempo (s)\tPeso (g)\n")
                    for time_val, weight_val in self.weight_data:
                        f.write(f"{time_val:.2f}\t{weight_val:.2f}\n")
            messagebox.showinfo("Salvataggio Completato", f"Dati salvati correttamente in:\n{filepath}")
        except IOError as e:
            messagebox.showerror("Errore di Salvataggio", f"Impossibile salvare il file:\n{e}")

    def update_status(self, message, color):
        self.status_label.config(text=message, foreground=color)

    def on_closing(self):
        self.is_reading = False
        if self.polling_job:
            self.root.after_cancel(self.polling_job)
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BilanciaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
