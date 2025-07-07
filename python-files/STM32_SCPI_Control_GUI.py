import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
# from instrument import SerialInstrumentIf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import numpy as np
import re
from tkinter import PhotoImage


class YIGControlApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("YIG-Filter SCPI GUI")
        # Grid-Konfiguration für feste Zeilenhöhe
        for i in range(20):  # genug Zeilen definieren
            self.root.grid_rowconfigure(i, weight=0)
           
        self.root.grid_rowconfigure(2, weight=1)  # Zeile für log_output → darf sich strecken

       # Rechte Seite darf sich strecken
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_columnconfigure(6, weight=1)
        self.STM32 = None
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        
        # Hauptcontainer aufteilen
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=10)
    
        # --- Linker Bereich: Controls ---
        row = 0
        ttk.Label(self.left_frame, text="COM-Port:").grid(row=row, column=0, sticky='e')
        self.com_entry = ttk.Entry(self.left_frame)
        self.com_entry.insert(0, "COM6")
        self.com_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Connect", command=self.connect).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="Frequency (Hz):").grid(row=row, column=0, sticky='e')
        self.freq_entry = ttk.Entry(self.left_frame)
        self.freq_entry.insert(0, "10e9")
        self.freq_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Frequency", command=self.set_frequency).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="DAC1 (V):").grid(row=row, column=0, sticky='e')
        self.dac1_entry = ttk.Entry(self.left_frame)
        self.dac1_entry.insert(0, "0")
        self.dac1_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set DAC1", command=self.set_dac1).grid(row=row, column=2)
        
        row += 1
        ttk.Label(self.left_frame, text="DAC2 (V):").grid(row=row, column=0, sticky='e')
        self.dac1_entry = ttk.Entry(self.left_frame)
        self.dac1_entry.insert(0, "0")
        self.dac1_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set DAC2", command=self.set_dac2).grid(row=row, column=2)
    
        row += 1
        self.cc_var = tk.BooleanVar()
        self.pc_var = tk.BooleanVar()
        self.fast_var = tk.BooleanVar()
        self.cset = tk.BooleanVar()
        self.lookup = tk.BooleanVar()
        ttk.Checkbutton(self.left_frame, text="CurrentControl", variable=self.cc_var,
                        command=self.toggle_current_control).grid(row=row, column=0)
        ttk.Checkbutton(self.left_frame, text="PhaseControl", variable=self.pc_var,
                        command=self.toggle_phase_control).grid(row=row, column=1)
        ttk.Checkbutton(self.left_frame, text="Fast-Mode", variable=self.fast_var,
                        command=self.toggle_fastmode).grid(row=row, column=2)
        row += 1
        ttk.Checkbutton(self.left_frame, text="Cset-Mode", variable=self.cset,
                        command=self.toggle_Csetmode).grid(row=row, column=0)
        ttk.Checkbutton(self.left_frame, text="Lookup-Mode", variable=self.lookup,
                        command=self.toggle_Lookup).grid(row=row, column=1)
    
    
    
        # Current Control Settings
        
        row += 1
        ttk.Label(self.left_frame, text="Current Control Settings:").grid(row=row, column=0, sticky='w', pady=(30, 10)) 
        
        row += 1
        ttk.Label(self.left_frame, text="CurrentControl:SET:Iter").grid(row=row, column=0, sticky="e")
        self.delay_entry = ttk.Entry(self.left_frame)
        self.delay_entry.insert(0, "10")
        self.delay_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Iterations", command=self.set_iter).grid(row=row, column=2)
        
        row += 1
        ttk.Label(self.left_frame, text="CurrentControl:Delay (ms)").grid(row=row, column=0, sticky="e")
        self.delay_entry = ttk.Entry(self.left_frame)
        self.delay_entry.insert(0, "500")
        self.delay_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Delay", command=self.set_currentdelay).grid(row=row, column=2)
        
        
        row += 1
        ttk.Label(self.left_frame, text="CurrentControl:Th (mA)").grid(row=row, column=0, sticky="e")
        self.delay_entry = ttk.Entry(self.left_frame)
        self.delay_entry.insert(0, "0.5")
        self.delay_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Threshold", command=self.set_currentth).grid(row=row, column=2)
        

        
        
        
        
        # Phase Control Settings
        
        row += 1
        ttk.Label(self.left_frame, text="Phase Control Settings:").grid(row=row, column=0, sticky='w', pady=(30, 10))    
    
        row += 1
        ttk.Label(self.left_frame, text="PhaseControl:Mode").grid(row=row, column=0, sticky="e")
        self.pc_mode_options = {
            "Deltaphase = 0": 0,
            "ADCerror = 0": 1,
            "PI-Control": 2,
            "PID-Control": 3
        }
        self.pc_mode = ttk.Combobox(self.left_frame, values=list(self.pc_mode_options.keys()), state="readonly")
        self.pc_mode.current(0)
        self.pc_mode.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Mode", command=self.set_phasecontrol_mode).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="PhaseMeas:Mode").grid(row=row, column=0, sticky="e")
        self.pm_mode_options = {
            "Averaging": 0,
            "FIR-Filter": 1
        }
        self.pm_mode = ttk.Combobox(self.left_frame, values=list(self.pm_mode_options.keys()), state="readonly")
        self.pm_mode.current(0)
        self.pm_mode.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Mode", command=self.set_phasemeas_mode).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="PhaseControl:Delay (ms)").grid(row=row, column=0, sticky="e")
        self.delay_entry = ttk.Entry(self.left_frame)
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Delay", command=self.set_delay).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="PhaseControl:Th").grid(row=row, column=0, sticky="e")
        self.th_entry = ttk.Entry(self.left_frame)
        self.th_entry.insert(0, "0.05")
        self.th_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Threshold", command=self.set_th).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="uSource:CurrentStepsize (mA)").grid(row=row, column=0, sticky="e")
        self.step_entry = ttk.Entry(self.left_frame)
        self.step_entry.insert(0, "0.01")
        self.step_entry.grid(row=row, column=1)
        ttk.Button(self.left_frame, text="Set Stepsize", command=self.set_stepsize).grid(row=row, column=2)
    
        row += 1
        ttk.Label(self.left_frame, text="PID Kp / Ki / Kd").grid(row=row, column=0, sticky="e")
        self.kp_entry = ttk.Entry(self.left_frame, width=5)
        self.kp_entry.insert(0, "1.0")
        self.kp_entry.grid(row=row, column=1, sticky="w")
        self.ki_entry = ttk.Entry(self.left_frame, width=5)
        self.ki_entry.insert(0, "0.0")
        self.ki_entry.grid(row=row, column=1)
        self.kd_entry = ttk.Entry(self.left_frame, width=5)
        self.kd_entry.insert(0, "0.0")
        self.kd_entry.grid(row=row, column=1, sticky="e")
        ttk.Button(self.left_frame, text="Set PID", command=self.set_pid_params).grid(row=row, column=2)
        
        row += 1
        ttk.Button(self.left_frame, text="Read Config", command=self.read_config).grid(row=row, column=0, pady=(30, 0))
        ttk.Button(self.left_frame, text="Read Phase", command=self.read_phase).grid(row=row, column=1, pady=(30, 0))
        ttk.Button(self.left_frame, text="Reset", command=self.reset_device).grid(row=row, column=2, pady=(30, 0))
    
        # --- Rechter Bereich: Logger und Plot ---
        ttk.Label(self.right_frame, text="Logger:").grid(row=0, column=0, sticky='w')
        self.log_output = scrolledtext.ScrolledText(self.right_frame, width=60, height=10, wrap=tk.WORD)
        self.log_output.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
    
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Live Phase")
        self.ax.set_xlabel("Zeit")
        self.ax.set_ylabel("Phase")
        self.phase_data = []
        self.time_data = []
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=3)
    
        ttk.Button(self.right_frame, text="Start Live-Plot", command=self.start_plot).grid(row=3, column=0, pady=(10, 0))
        ttk.Button(self.right_frame, text="Stop", command=self.stop_plot).grid(row=3, column=1, pady=(10, 0))


    def connect(self):
        port = self.com_entry.get()
        try:
            self.STM32 = SerialInstrumentIf(port, 115200)
            idn = self.STM32.querySCPI("*IDN?")
            self.log(f"Connected: {idn}")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def log(self, msg):
        self.log_output.insert(tk.END, msg + "\n")
        self.log_output.see(tk.END)

    def set_frequency(self):
        freq = self.freq_entry.get()
        try:
            self.STM32.querySCPI(f"freq:SET {freq}")
            self.log(f"Frequency set to {freq} Hz")
        except Exception as e:
            self.log(f"Fehler: {e}")

    def set_dac1(self):
        val = self.dac1_entry.get()
        try:
            self.STM32.querySCPI(f"DAC1:SET {val}")
            self.log(f"DAC1 set to {val} V")
        except Exception as e:
            self.log(f"Fehler: {e}")
            
    def set_dac2(self):
        val = self.dac1_entry.get()
        try:
            self.STM32.querySCPI(f"DAC2:SET {val}")
            self.log(f"DAC2 set to {val} V")
        except Exception as e:
            self.log(f"Fehler: {e}")

    def toggle_current_control(self):
        state = "ON" if self.cc_var.get() else "OFF"
        self.STM32.querySCPI(f"CurrentControl:{state}")
        self.log(f"CurrentControl {state}")

    def toggle_phase_control(self):
        state = "ON" if self.pc_var.get() else "OFF"
        self.STM32.querySCPI(f"PhaseControl:{state}")
        self.log(f"PhaseControl {state}")

    def toggle_fastmode(self):
        state = "ON" if self.fast_var.get() else "OFF"
        self.STM32.querySCPI(f"Fastmode:{state}")
        self.log(f"Fastmode {state}")
      
        
    def toggle_Csetmode(self):
        state = "ON" if self.cset.get() else "OFF"
        self.STM32.querySCPI(f"CsetMode:{state}")
        self.log(f"Fastmode {state}")  
        
    def toggle_Lookup(self):
        state = "ON" if self.cset.get() else "OFF"
        self.STM32.querySCPI(f"freq:SET:Lookup:{state}")
        self.log(f"Lookup {state}")
        

    def read_phase(self):
        try:
            response = self.STM32.querySCPI("IQphase:GET")
            value = re.search(r"[\d.]+", response)
            phase_val = float(value.group()) if value else 0
            self.log(f"Phase: {phase_val}.")
        except Exception as e:
            self.log(f"Error reading Phase: {e}.")
            
    def read_config(self):
        try:
            self.STM32.querySCPI("CurrentControl:ON")
            self.STM32.querySCPI("CurrentControl:SET:Iter 10")
            self.STM32.querySCPI("CurrentControl:Th 0.5")
            self.STM32.querySCPI("CurrentControl:Delay 500")
            self.STM32.querySCPI("CsetMode:OFF")
            self.STM32.querySCPI("freq:SET:Lookup:ON")
            self.STM32.querySCPI("PhaseControl:Mode 3")              
            self.STM32.querySCPI("PhaseMeas:Mode 0")                 
            self.STM32.querySCPI("PhaseControl:Delay 10")   
            Phase_Th = 0.0015
            self.STM32.querySCPI(f"PhaseControl:Th {Phase_Th:.4f}")
            self.STM32.querySCPI("PhaseControl:CurrentStepSize:SET 0.004")  
            self.STM32.querySCPI("PhaseControl:SET:PIDparams 0.9, 0.0, 0.0") 
            self.STM32.querySCPI("Fastmode:ON")
            self.log("Standard Config set.")
        except Exception as e:
            self.log(f"Error setting config: {e}.")
            

    def reset_device(self):
        try:
            self.STM32.cmdSCPI("Reset")
            self.log("Device reset.")
        except Exception as e:
            self.log(f"Error: {e}.")

    def start_plot(self):
        if not self.STM32 or self.running:
            return
        self.running = True
        self.phase_data.clear()
        self.time_data.clear()
        self.plot_thread = threading.Thread(target=self.update_plot, daemon=True)
        self.plot_thread.start()
        self.log("Live-Plot started.")

    def stop_plot(self):
        self.running = False
        self.log("Live-Plot stopped.")

    def update_plot(self):
        start_time = time.time()
        while self.running:
            try:
                response = self.STM32.querySCPI("IQphase:GET")
                match = re.search(r"[\d.]+", response)
                phase = float(match.group()) if match else 0.0

                t = time.time() - start_time
                self.phase_data.append(phase)
                self.time_data.append(t)

                if len(self.phase_data) > 100:
                    self.phase_data.pop(0)
                    self.time_data.pop(0)

                self.ax.clear()
                self.ax.plot(self.time_data, self.phase_data, label="Phase")
                self.ax.set_title("Live Phase")
                self.ax.set_xlabel("Time [s]")
                self.ax.set_ylabel("Phase")
                self.ax.legend()
                self.ax.grid(True)
                self.canvas.draw()
            except Exception as e:
                self.log(f"Plot Error: {e}.")
                break
            time.sleep(0.2)



    def set_iter(self):
        itera = self.th_entry.get()
        self.STM32.querySCPI(f"CurrentControl:SET:Iter {itera}")
        self.log(f"CurrentControl:SET:Iter set to {itera}.")


    def set_currentth(self):
        ith = self.th_entry.get()
        self.STM32.querySCPI(f"CurrentControl:Th {ith}")
        self.log(f"CurrentControl:Th set to {ith} mA.")

    def set_currentdelay(self):
        delay = self.delay_entry.get()
        self.STM32.querySCPI(f"CurrentControl:Delay {delay}")
        self.log(f"CurrentControl:Delay set to {delay} ms.")


    def set_phasecontrol_mode(self):
        label = self.pc_mode.get()
        value = self.pc_mode_options[label]
        self.STM32.querySCPI(f"PhaseControl:Mode {value}")
        self.log(f"PhaseControl:Mode set to {label} ({value}).")

    def set_phasemeas_mode(self):
        label = self.pm_mode.get()
        value = self.pm_mode_options[label]
        self.STM32.querySCPI(f"PhaseMeas:Mode {value}")
        self.log(f"PhaseMeas:Mode set to {label} ({value}).")

    def set_delay(self):
        delay = self.delay_entry.get()
        self.STM32.querySCPI(f"PhaseControl:Delay {delay}")
        self.log(f"PhaseControlDelay set to {delay} ms.")

    def set_th(self):
        th = self.th_entry.get()
        self.STM32.querySCPI(f"PhaseControl:Th {th}")
        self.log(f"PhaseControl:Th set to {th}.")

    def set_stepsize(self):
        step = self.step_entry.get()
        self.STM32.querySCPI(f"PhaseControl:CurrentStepsize:SET {step}")
        self.log(f"PhaseControl:Stepsize set to {step} mA.")

    def set_pid_params(self):
        kp = self.kp_entry.get()
        ki = self.ki_entry.get()
        kd = self.kd_entry.get()
        self.STM32.querySCPI(f"PhaseControl:SET:PIDparams {kp} {ki} {kd}")
        self.log(f"PID-Parameter set: Kp={kp}, Ki={ki}, Kd={kd}.")

if __name__ == "__main__":
    
    if tk._default_root is not None:
        try:
            tk._default_root.destroy()
        except:
            pass
    
    root = tk.Tk()
    root.iconbitmap("./Icons/EROM_Logo.drawio.ico")
    app = YIGControlApp(root)
    root.mainloop()
