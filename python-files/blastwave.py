import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import math
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import matplotlib.animation as animation

class BlastWaveSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blast Wave Simulation")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.update_idletasks()

        # Data storage
        self.blast_holes = []
        self.monitors = []
        self.simulation_data = []
        self.current_page = 1

        # Simulation parameters
        self.time_interval = 8  # ms
        self.k_constant = 1100
        self.e_constant = -1.60
        self.p_wave_speed = 3500  # m/s
        self.s_wave_speed = 2500  # m/s
        self.rayleigh_speed = 2000  # m/s

        # Wave visibility
        self.show_p_wave = tk.BooleanVar(value=True)
        self.show_s_wave = tk.BooleanVar(value=True)
        self.show_rayleigh = tk.BooleanVar(value=True)

        # Simulation control
        self.is_playing = False
        self.simulation_speed = 0.25
        self.current_time = 0

        # Animation objects
        self.wave_circles = {}
        self.anim = None

        # Initialize wave speed variables
        self.p_speed_var = tk.StringVar(value=str(self.p_wave_speed))
        self.s_speed_var = tk.StringVar(value=str(self.s_wave_speed))
        self.rayleigh_speed_var = tk.StringVar(value=str(self.rayleigh_speed))
        self.time_interval_var = tk.StringVar(value=str(self.time_interval))
        self.k_var = tk.StringVar(value=str(self.k_constant))
        self.e_var = tk.StringVar(value=str(self.e_constant))

        self.last_wave_arrival_time = 0
        self.recorded_arrivals = set()  # Track recorded arrivals to avoid duplicates
        self.all_expected_arrivals = set()  # Track all expected arrivals for completion detection

        # Store original data as strings to prevent widget access issues
        self.original_blast_data = ""
        self.original_monitors = []

        # Widget references
        self.blast_text = None
        self.monitor_listbox = None

        self.create_page1()

    def clear_window(self):
        # Stop animation if running
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None
        
        for widget in self.root.winfo_children():
            widget.destroy()

    def save_current_data(self):
        """Save current data before page transitions"""
        try:
            if self.blast_text is not None and self.blast_text.winfo_exists():
                self.original_blast_data = self.blast_text.get(1.0, tk.END)
        except tk.TclError:
            # Widget already destroyed, keep existing data
            pass
        
        try:
            if self.monitor_listbox is not None and self.monitor_listbox.winfo_exists():
                self.original_monitors = []
                for i in range(self.monitor_listbox.size()):
                    self.original_monitors.append(self.monitor_listbox.get(i))
        except tk.TclError:
            # Widget already destroyed, keep existing data
            pass

    def restore_data(self):
        """Restore data when returning to page 1"""
        if self.blast_text is not None and self.original_blast_data:
            self.blast_text.delete(1.0, tk.END)
            self.blast_text.insert(1.0, self.original_blast_data)
        
        if self.monitor_listbox is not None and self.original_monitors:
            self.monitor_listbox.delete(0, tk.END)
            for monitor in self.original_monitors:
                self.monitor_listbox.insert(tk.END, monitor)

    def create_page1(self):
        self.clear_window()
        self.current_page = 1
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = ttk.Label(main_frame, text="Blast Wave Simulation - Data Input", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Blast hole data frame
        blast_frame = ttk.LabelFrame(main_frame, text="Blast Hole Data", padding=10)
        blast_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        instr_label = ttk.Label(blast_frame, text="Format: Hole ID, Easting, Northing, Charge Weight, Hole Firing Time (ms)")
        instr_label.pack(anchor=tk.W)
        
        self.blast_text = tk.Text(blast_frame, height=10, width=80)
        self.blast_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        button_frame = ttk.Frame(blast_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Load from CSV", command=self.load_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Load from Excel", command=self.load_excel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=lambda: self.blast_text.delete(1.0, tk.END)).pack(side=tk.LEFT)

        # Monitor data frame
        monitor_frame = ttk.LabelFrame(main_frame, text="Monitor Data", padding=10)
        monitor_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(monitor_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Monitor Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.monitor_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.monitor_name_var, width=15).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(input_frame, text="Easting:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.monitor_easting_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.monitor_easting_var, width=12).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(input_frame, text="Northing:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.monitor_northing_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.monitor_northing_var, width=12).grid(row=0, column=5, padx=(0, 10))
        
        ttk.Button(input_frame, text="Add Monitor", command=self.add_monitor).grid(row=0, column=6)
        
        self.monitor_listbox = tk.Listbox(monitor_frame, height=5)
        self.monitor_listbox.pack(fill=tk.X, pady=5)
        
        ttk.Button(monitor_frame, text="Remove Selected Monitor", command=self.remove_monitor).pack()
        
        ttk.Button(main_frame, text="Next - Visualization", command=self.go_to_page2).pack(pady=20)

        # Restore data if returning from another page
        self.restore_data()

    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                df = pd.read_csv(filename)
                self.blast_text.delete(1.0, tk.END)
                for _, row in df.iterrows():
                    if len(row) >= 5:
                        line = f"{row.iloc[0]}, {row.iloc[1]}, {row.iloc[2]}, {row.iloc[3]}, {row.iloc[4]}\n"
                        self.blast_text.insert(tk.END, line)
                    else:
                        messagebox.showwarning("Warning", f"Row with insufficient columns: {row}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")

    def load_excel(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("Excel files", "*.xls")])
        if filename:
            try:
                df = pd.read_excel(filename)
                self.blast_text.delete(1.0, tk.END)
                for _, row in df.iterrows():
                    if len(row) >= 5:
                        line = f"{row.iloc[0]}, {row.iloc[1]}, {row.iloc[2]}, {row.iloc[3]}, {row.iloc[4]}\n"
                        self.blast_text.insert(tk.END, line)
                    else:
                        messagebox.showwarning("Warning", f"Row with insufficient columns: {row}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Excel: {str(e)}")

    def add_monitor(self):
        name = self.monitor_name_var.get().strip()
        try:
            easting = float(self.monitor_easting_var.get())
            northing = float(self.monitor_northing_var.get())
            if name:
                monitor_info = f"{name}: ({easting}, {northing})"
                self.monitor_listbox.insert(tk.END, monitor_info)
                self.monitor_name_var.set("")
                self.monitor_easting_var.set("")
                self.monitor_northing_var.set("")
            else:
                messagebox.showwarning("Warning", "Please enter a monitor name")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric coordinates")

    def remove_monitor(self):
        selection = self.monitor_listbox.curselection()
        if selection:
            self.monitor_listbox.delete(selection[0])

    def parse_input_data(self):
        self.blast_holes = []
        blast_data = self.blast_text.get(1.0, tk.END).strip()
        if not blast_data:
            messagebox.showerror("Error", "Please enter blast hole data")
            return False
            
        for line in blast_data.split('\n'):
            if line.strip():
                try:
                    parts = [x.strip() for x in line.split(',')]
                    if len(parts) >= 5:
                        hole_id = parts[0]
                        easting = float(parts[1])
                        northing = float(parts[2])
                        charge_weight = float(parts[3])
                        firing_time = float(parts[4])
                        self.blast_holes.append({
                            'hole_id': hole_id,
                            'easting': easting,
                            'northing': northing,
                            'charge_weight': charge_weight,
                            'firing_time': firing_time
                        })
                    else:
                        messagebox.showerror("Error", f"Insufficient data in line: {line}")
                        return False
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid data format in line: {line}\nError: {str(e)}")
                    return False
                    
        if not self.blast_holes:
            messagebox.showerror("Error", "No valid blast hole data found")
            return False

        # Normalize firing times to start from 0
        min_time = min(hole['firing_time'] for hole in self.blast_holes)
        for hole in self.blast_holes:
            hole['firing_time'] -= min_time

        # Parse monitors
        self.monitors = []
        for i in range(self.monitor_listbox.size()):
            monitor_text = self.monitor_listbox.get(i)
            try:
                name_part, coord_part = monitor_text.split(': ')
                coord_part = coord_part.strip('()')
                easting, northing = map(float, coord_part.split(', '))
                self.monitors.append({
                    'name': name_part,
                    'easting': easting,
                    'northing': northing
                })
            except ValueError:
                messagebox.showerror("Error", f"Invalid monitor format: {monitor_text}")
                return False
                
        if not self.monitors:
            messagebox.showerror("Error", "Please add at least one monitor")
            return False
            
        return True

    def go_to_page2(self):
        self.save_current_data()
        if self.parse_input_data():
            self.create_page2()

    def create_page2(self):
        self.clear_window()
        self.current_page = 2

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control panel at top
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Plot frame below controls
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.create_control_panel(control_frame)

        # Create matplotlib figure
        self.fig = plt.figure(figsize=(12, 7), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Calculate simulation parameters
        self.calculate_expected_arrivals()
        self.last_wave_arrival_time = self.compute_last_arrival_time()
        
        self.setup_plot()
        self.reset_simulation()

    def calculate_expected_arrivals(self):
        """Pre-calculate all expected wave arrivals to know when simulation should end"""
        self.all_expected_arrivals = set()
        
        try:
            p_speed = float(self.p_speed_var.get()) / 1000  # Convert to m/ms
            s_speed = float(self.s_speed_var.get()) / 1000
            rayleigh_speed = float(self.rayleigh_speed_var.get()) / 1000
        except Exception:
            p_speed = self.p_wave_speed / 1000
            s_speed = self.s_wave_speed / 1000
            rayleigh_speed = self.rayleigh_speed / 1000

        for monitor in self.monitors:
            for hole in self.blast_holes:
                wave_configs = []
                if self.show_p_wave.get() and p_speed > 0:
                    wave_configs.append('P')
                if self.show_s_wave.get() and s_speed > 0:
                    wave_configs.append('S')
                if self.show_rayleigh.get() and rayleigh_speed > 0:
                    wave_configs.append('Rayleigh')
                
                for wave_type in wave_configs:
                    arrival_key = (monitor['name'], hole['hole_id'], wave_type)
                    self.all_expected_arrivals.add(arrival_key)

    def compute_last_arrival_time(self):
        """Calculate when the last wave reaches the farthest monitor"""
        max_time = 0
        
        try:
            p_speed = float(self.p_speed_var.get()) / 1000  # Convert to m/ms
            s_speed = float(self.s_speed_var.get()) / 1000
            rayleigh_speed = float(self.rayleigh_speed_var.get()) / 1000
        except Exception:
            p_speed = self.p_wave_speed / 1000
            s_speed = self.s_wave_speed / 1000
            rayleigh_speed = self.rayleigh_speed / 1000

        # Calculate maximum arrival time for each monitor from each blast hole
        for monitor in self.monitors:
            for hole in self.blast_holes:
                distance = self.calculate_distance(hole['easting'], hole['northing'], 
                                                 monitor['easting'], monitor['northing'])
                
                # Check all enabled wave types
                arrival_times = []
                if self.show_p_wave.get() and p_speed > 0:
                    arrival_times.append(hole['firing_time'] + (distance / p_speed))
                if self.show_s_wave.get() and s_speed > 0:
                    arrival_times.append(hole['firing_time'] + (distance / s_speed))
                if self.show_rayleigh.get() and rayleigh_speed > 0:
                    arrival_times.append(hole['firing_time'] + (distance / rayleigh_speed))
                
                if arrival_times:
                    max_time = max(max_time, max(arrival_times))
        
        return max_time + 200  # Add 200ms buffer

    def create_control_panel(self, parent):
        # Wave parameters row
        wave_frame = ttk.LabelFrame(parent, text="Wave Parameters")
        wave_frame.pack(fill=tk.X, pady=2)
        
        # P Wave controls
        ttk.Checkbutton(wave_frame, text="P Wave", variable=self.show_p_wave, 
                       command=self.update_parameters).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Entry(wave_frame, textvariable=self.p_speed_var, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(wave_frame, text="m/s").grid(row=0, column=2, padx=(2, 10))
        
        # S Wave controls
        ttk.Checkbutton(wave_frame, text="S Wave", variable=self.show_s_wave, 
                       command=self.update_parameters).grid(row=0, column=3, padx=5, sticky=tk.W)
        ttk.Entry(wave_frame, textvariable=self.s_speed_var, width=8).grid(row=0, column=4, padx=2)
        ttk.Label(wave_frame, text="m/s").grid(row=0, column=5, padx=(2, 10))
        
        # Rayleigh Wave controls
        ttk.Checkbutton(wave_frame, text="Rayleigh", variable=self.show_rayleigh, 
                       command=self.update_parameters).grid(row=0, column=6, padx=5, sticky=tk.W)
        ttk.Entry(wave_frame, textvariable=self.rayleigh_speed_var, width=8).grid(row=0, column=7, padx=2)
        ttk.Label(wave_frame, text="m/s").grid(row=0, column=8, padx=2)

        # Control buttons row
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=2)
        
        # PPV parameters
        ppv_frame = ttk.LabelFrame(control_frame, text="PPV Parameters")
        ppv_frame.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(ppv_frame, text="K:").grid(row=0, column=0, padx=2)
        ttk.Entry(ppv_frame, textvariable=self.k_var, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(ppv_frame, text="E:").grid(row=0, column=2, padx=2)
        ttk.Entry(ppv_frame, textvariable=self.e_var, width=8).grid(row=0, column=3, padx=2)
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(control_frame, text="Simulation Controls")
        sim_frame.pack(side=tk.LEFT, padx=5)
        
        self.play_button = ttk.Button(sim_frame, text="Play", command=self.toggle_simulation)
        self.play_button.grid(row=0, column=0, padx=2)
        ttk.Button(sim_frame, text="Reset", command=self.reset_simulation).grid(row=0, column=1, padx=2)
        ttk.Button(sim_frame, text="Speed+", command=self.speed_up).grid(row=0, column=2, padx=2)
        ttk.Button(sim_frame, text="Speed-", command=self.slow_down).grid(row=0, column=3, padx=2)
        
        self.speed_label = ttk.Label(sim_frame, text=f"Speed: {self.simulation_speed}x")
        self.speed_label.grid(row=0, column=4, padx=5)
        
        # Zoom controls
        zoom_frame = ttk.LabelFrame(control_frame, text="View Controls")
        zoom_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(zoom_frame, text="Zoom In", command=self.zoom_in).grid(row=0, column=0, padx=2)
        ttk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out).grid(row=0, column=1, padx=2)
        
        # Navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(nav_frame, text="View Data", command=self.go_to_page3).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav_frame, text="Back to Input", command=self.go_back_to_page1).pack(side=tk.RIGHT, padx=2)

    def go_back_to_page1(self):
        """Return to page 1 without losing data"""
        self.save_current_data()
        self.create_page1()

    def go_to_page3(self):
        """Go to page 3 data view"""
        self.save_current_data()
        self.create_page3()

    def update_parameters(self):
        """Update simulation parameters when wave settings change"""
        self.calculate_expected_arrivals()
        self.last_wave_arrival_time = self.compute_last_arrival_time()

    def setup_plot(self):
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3, linewidth=0.5)
        
        # Plot blast holes (red circles)
        for hole in self.blast_holes:
            self.ax.plot(hole['easting'], hole['northing'], 'ro', markersize=6, 
                        markeredgecolor='darkred', markeredgewidth=1)

        # Plot monitors (blue squares) with labels
        for monitor in self.monitors:
            self.ax.plot(monitor['easting'], monitor['northing'], 'bs', markersize=10, 
                        markeredgecolor='darkblue', markeredgewidth=1)
            self.ax.annotate(monitor['name'], (monitor['easting'], monitor['northing']),
                           xytext=(8, 8), textcoords='offset points', fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", 
                                   alpha=0.8, edgecolor='blue'))

        # Set plot limits
        all_eastings = [h['easting'] for h in self.blast_holes] + [m['easting'] for m in self.monitors]
        all_northings = [h['northing'] for h in self.blast_holes] + [m['northing'] for m in self.monitors]
        
        padding = 3000
        self.ax.set_xlim(min(all_eastings) - padding, max(all_eastings) + padding)
        self.ax.set_ylim(min(all_northings) - padding, max(all_northings) + padding)

        # Time display
        self.time_text = self.ax.text(0.02, 0.98, 'Time: 0 ms',
                                    transform=self.ax.transAxes, fontsize=12, fontweight='bold',
                                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", 
                                            alpha=0.9, edgecolor='black'),
                                    verticalalignment='top')
        
        # Initialize wave circles storage
        self.wave_circles = {'p_wave': [], 's_wave': [], 'rayleigh': []}
        self.canvas.draw()

    def calculate_distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculate_ppv(self, distance, charge_weight):
        try:
            k = float(self.k_var.get())
            e = float(self.e_var.get())
            if charge_weight > 0 and distance > 0:
                ppv = k * ((distance / (charge_weight ** 0.5)) ** e)
                return abs(ppv)
            else:
                return 0
        except (ValueError, ZeroDivisionError):
            return 0

    def reset_simulation(self):
        self.current_time = 0
        self.is_playing = False
        self.play_button.config(text="Play")
        self.simulation_data = []
        self.recorded_arrivals = set()
        
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None
            
        self.setup_plot()

    def toggle_simulation(self):
        if not self.is_playing:
            self.is_playing = True
            self.play_button.config(text="Pause")
            if self.anim is None:
                self.anim = animation.FuncAnimation(
                    self.fig,
                    self.animate_frame,
                    interval=50,  # 20 FPS
                    blit=False,
                    cache_frame_data=False,
                    repeat=False
                )
            else:
                self.anim.event_source.start()
            self.canvas.draw()
        else:
            self.is_playing = False
            self.play_button.config(text="Play")
            if self.anim is not None:
                self.anim.event_source.stop()

    def animate_frame(self, frame_num):
        if not self.is_playing:
            return []
            
        # Time progression
        time_step = 10  # ms per frame
        self.current_time += time_step * self.simulation_speed
        self.time_text.set_text(f'Time: {self.current_time:.0f} ms')
        
        # Get current wave speeds (converted to m/ms)
        try:
            p_speed = float(self.p_speed_var.get()) / 1000
            s_speed = float(self.s_speed_var.get()) / 1000
            rayleigh_speed = float(self.rayleigh_speed_var.get()) / 1000
        except Exception:
            p_speed = self.p_wave_speed / 1000
            s_speed = self.s_wave_speed / 1000
            rayleigh_speed = self.rayleigh_speed / 1000

        # Clear previous wave circles
        for wave_type in self.wave_circles:
            for circle in self.wave_circles[wave_type]:
                try:
                    circle.remove()
                except Exception:
                    pass
        self.wave_circles = {'p_wave': [], 's_wave': [], 'rayleigh': []}
        
        # Draw wave circles for each fired hole
        for hole in self.blast_holes:
            if hole['firing_time'] <= self.current_time:
                time_since_firing = self.current_time - hole['firing_time']
                
                # Calculate wave radii
                radius_p = p_speed * time_since_firing
                radius_s = s_speed * time_since_firing
                radius_r = rayleigh_speed * time_since_firing
                
                # Draw P wave (fastest - blue)
                if self.show_p_wave.get() and radius_p > 0:
                    circle = Circle((hole['easting'], hole['northing']), radius_p, 
                                  fill=False, color='blue', alpha=0.6, linewidth=2)
                    self.ax.add_patch(circle)
                    self.wave_circles['p_wave'].append(circle)
                
                # Draw S wave (medium speed - purple)
                if self.show_s_wave.get() and radius_s > 0:
                    circle = Circle((hole['easting'], hole['northing']), radius_s, 
                                  fill=False, color='purple', alpha=0.6, linewidth=2)
                    self.ax.add_patch(circle)
                    self.wave_circles['s_wave'].append(circle)
                
                # Draw Rayleigh wave (slowest - orange)
                if self.show_rayleigh.get() and radius_r > 0:
                    circle = Circle((hole['easting'], hole['northing']), radius_r, 
                                  fill=False, color='orange', alpha=0.6, linewidth=2)
                    self.ax.add_patch(circle)
                    self.wave_circles['rayleigh'].append(circle)
                
                # Check for wave arrivals at monitors
                self.check_wave_arrivals(hole, time_since_firing, p_speed, s_speed, rayleigh_speed)

        # Check if all expected arrivals have been recorded or time exceeded
        all_arrivals_recorded = (len(self.recorded_arrivals) >= len(self.all_expected_arrivals)) and len(self.all_expected_arrivals) > 0
        time_exceeded = self.current_time >= self.last_wave_arrival_time
        
        # Stop simulation when all waves have arrived at all monitors
        if all_arrivals_recorded or time_exceeded:
            self.is_playing = False
            self.play_button.config(text="Completed")
            if self.anim is not None:
                self.anim.event_source.stop()
        
        self.canvas.draw()
        return [self.time_text] + self.wave_circles['p_wave'] + self.wave_circles['s_wave'] + self.wave_circles['rayleigh']

    def check_wave_arrivals(self, hole, time_since_firing, p_speed, s_speed, rayleigh_speed):
        """Check if waves have arrived at monitors and record data"""
        for monitor in self.monitors:
            distance = self.calculate_distance(hole['easting'], hole['northing'], 
                                             monitor['easting'], monitor['northing'])
            
            wave_configs = []
            if self.show_p_wave.get() and p_speed > 0:
                wave_configs.append(('P', p_speed))
            if self.show_s_wave.get() and s_speed > 0:
                wave_configs.append(('S', s_speed))
            if self.show_rayleigh.get() and rayleigh_speed > 0:
                wave_configs.append(('Rayleigh', rayleigh_speed))
            
            for wave_type, speed in wave_configs:
                travel_time = distance / speed
                
                # Check if wave has just arrived (within tolerance)
                tolerance = 25  # ms tolerance for wave arrival detection
                if abs(time_since_firing - travel_time) < tolerance:
                    arrival_key = (monitor['name'], hole['hole_id'], wave_type)
                    
                    # Only record if not already recorded
                    if arrival_key not in self.recorded_arrivals:
                        arrival_time = hole['firing_time'] + travel_time
                        ppv = self.calculate_ppv(distance, hole['charge_weight'])
                        
                        if ppv > 0:
                            self.record_arrival(monitor['name'], hole['hole_id'], arrival_time, 
                                              hole['charge_weight'], ppv, wave_type, distance)
                            self.recorded_arrivals.add(arrival_key)

    def record_arrival(self, monitor_name, hole_id, arrival_time, charge_weight, ppv, wave_type, distance):
        """Record wave arrival data"""
        self.simulation_data.append({
            'monitor': monitor_name,
            'hole_id': hole_id,
            'arrival_time': arrival_time,
            'charge_weight': charge_weight,
            'ppv': ppv,
            'wave_type': wave_type,
            'distance': distance
        })

    def speed_up(self):
        """Increase simulation speed"""
        self.simulation_speed = min(self.simulation_speed * 2, 8.0)
        self.speed_label.config(text=f"Speed: {self.simulation_speed}x")

    def slow_down(self):
        """Decrease simulation speed"""
        self.simulation_speed = max(self.simulation_speed / 2, 0.125)
        self.speed_label.config(text=f"Speed: {self.simulation_speed}x")

    def zoom_in(self):
        """Zoom into the plot"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        x_range = (xlim[1] - xlim[0]) * 0.8
        y_range = (ylim[1] - ylim[0]) * 0.8
        self.ax.set_xlim(x_center - x_range / 2, x_center + x_range / 2)
        self.ax.set_ylim(y_center - y_range / 2, y_center + y_range / 2)
        self.canvas.draw()

    def zoom_out(self):
        """Zoom out from the plot"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        x_range = (xlim[1] - xlim[0]) * 1.25
        y_range = (ylim[1] - ylim[0]) * 1.25
        self.ax.set_xlim(x_center - x_range / 2, x_center + x_range / 2)
        self.ax.set_ylim(y_center - y_range / 2, y_center + y_range / 2)
        self.canvas.draw()

    def create_page3(self):
        """Create data export page"""
        self.clear_window()
        self.current_page = 3
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = ttk.Label(main_frame, text="Simulation Data Export", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Check if simulation has been run
        if not self.simulation_data:
            warning_frame = ttk.Frame(main_frame)
            warning_frame.pack(fill=tk.X, pady=20)
            
            warning_label = ttk.Label(warning_frame, 
                                    text="No simulation data available. Please run the simulation first.",
                                    font=("Arial", 12), foreground="red")
            warning_label.pack()
            
            button_frame = ttk.Frame(warning_frame)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="Back to Simulation", 
                      command=self.create_page2).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="Back to Input", 
                      command=self.go_back_to_page1).pack(side=tk.LEFT, padx=10)
            return
        
        # Create frame for tree and scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create data table
        columns = ('Monitor', 'Hole ID', 'Arrival Time (ms)', 'MIC (kg)', 'PPV', 'Wave Type', 'Distance (m)')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Monitor':
                self.tree.column(col, width=100)
            elif col == 'Hole ID':
                self.tree.column(col, width=80)
            elif col == 'Wave Type':
                self.tree.column(col, width=80)
            else:
                self.tree.column(col, width=120)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Populate data table
        for record in sorted(self.simulation_data, key=lambda x: (x['monitor'], x['arrival_time'])):
            self.tree.insert('', tk.END, values=(
                record['monitor'],
                record['hole_id'],
                f"{record['arrival_time']:.2f}",
                f"{record['charge_weight']:.2f}",
                f"{record['ppv']:.2f}",
                record['wave_type'],
                f"{record['distance']:.2f}"
            ))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_records = len(self.simulation_data)
        unique_monitors = len(set(record['monitor'] for record in self.simulation_data))
        unique_holes = len(set(record['hole_id'] for record in self.simulation_data))
        
        if self.simulation_data:
            max_ppv = max(record['ppv'] for record in self.simulation_data)
            avg_ppv = sum(record['ppv'] for record in self.simulation_data) / total_records
            stats_text = (f"Total Records: {total_records} | Monitors: {unique_monitors} | "
                         f"Blast Holes: {unique_holes} | Max PPV: {max_ppv:.2f} | Avg PPV: {avg_ppv:.2f}")
        else:
            stats_text = f"Total Records: {total_records} | Monitors: {unique_monitors} | Blast Holes: {unique_holes}"
        
        ttk.Label(stats_frame, text=stats_text, font=("Arial", 10)).pack()
        
        # Show completion status
        expected_arrivals = len(self.all_expected_arrivals) if hasattr(self, 'all_expected_arrivals') else 0
        recorded_arrivals = len(self.recorded_arrivals) if hasattr(self, 'recorded_arrivals') else 0
        completion_text = f"Expected Arrivals: {expected_arrivals} | Recorded Arrivals: {recorded_arrivals}"
        ttk.Label(stats_frame, text=completion_text, font=("Arial", 9), foreground="blue").pack()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Back to Simulation", 
                  command=self.create_page2).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Back to Input", 
                  command=self.go_back_to_page1).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_csv).pack(side=tk.RIGHT)

    def export_csv(self):
        """Export simulation data to CSV file"""
        if not self.simulation_data:
            messagebox.showwarning("No Data", "No simulation data to export. Please run the simulation first.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save simulation data as...",
            initialname="blast_wave_simulation_results.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Monitor', 'Hole_ID', 'Arrival_Time_ms', 'MIC_kg', 'PPV', 'Wave_Type', 'Distance_m']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    # Sort data by monitor and arrival time
                    sorted_data = sorted(self.simulation_data, key=lambda x: (x['monitor'], x['arrival_time']))
                    
                    for record in sorted_data:
                        writer.writerow({
                            'Monitor': record['monitor'],
                            'Hole_ID': record['hole_id'],
                            'Arrival_Time_ms': f"{record['arrival_time']:.2f}",
                            'MIC_kg': f"{record['charge_weight']:.2f}",
                            'PPV': f"{record['ppv']:.2f}",
                            'Wave_Type': record['wave_type'],
                            'Distance_m': f"{record['distance']:.2f}"
                        })
                
                messagebox.showinfo("Export Successful", 
                                  f"Data exported successfully to:\n{filename}\n\n"
                                  f"Total records exported: {len(sorted_data)}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", f"An error occurred:\n{str(e)}")

if __name__ == "__main__":
    app = BlastWaveSimulation()
    app.run()
