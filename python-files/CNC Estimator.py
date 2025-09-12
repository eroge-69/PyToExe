import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import math
import re

class CNC_Time_Estimator:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Router Time Estimator")
        self.root.geometry("800x700")
        
        # Variabel default
        self.default_feedrate = 889  # mm/min
        self.current_feedrate = self.default_feedrate
        self.effective_feedrate = self.default_feedrate
        self.file_path = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame utama
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        ttk.Label(main_frame, text="File G-code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(main_frame, text="Tidak ada file dipilih", foreground="red")
        self.file_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Pilih File", command=self.select_file).grid(row=0, column=2, pady=5)
        
        # Feedrate slider dengan input angka
        ttk.Label(main_frame, text="Feedrate Efektif:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Frame untuk slider, input, dan label
        slider_frame = ttk.Frame(main_frame)
        slider_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.feedrate_var = tk.DoubleVar(value=100)  # Default 100%
        
        # Input angka untuk feedrate percentage
        self.feedrate_entry = ttk.Entry(slider_frame, textvariable=tk.StringVar(value="100"), width=5)
        self.feedrate_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.feedrate_entry.bind('<Return>', self.update_feedrate_from_entry)
        self.feedrate_entry.bind('<FocusOut>', self.update_feedrate_from_entry)
        
        ttk.Label(slider_frame, text="%").pack(side=tk.LEFT, padx=(0, 10))
        
        self.feedrate_slider = ttk.Scale(slider_frame, from_=0, to=200, 
                                       variable=self.feedrate_var, 
                                       orient=tk.HORIZONTAL,
                                       command=self.update_feedrate_from_slider,
                                       length=250)
        self.feedrate_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.feedrate_percent_label = ttk.Label(slider_frame, text="100%", width=6)
        self.feedrate_percent_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.effective_feedrate_label = ttk.Label(main_frame, text=f"Feedrate: {self.default_feedrate} mm/min")
        self.effective_feedrate_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Info range slider
        ttk.Label(main_frame, text="Slider: 0-200% (100% = default)", foreground="gray", font=("Arial", 8)).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Harga per menit
        ttk.Label(main_frame, text="Harga per Menit (Rp):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.harga_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.harga_var, width=15).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Diskon nominal
        ttk.Label(main_frame, text="Diskon Nominal (Rp):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.diskon_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.diskon_var, width=15).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Calculate button
        ttk.Button(main_frame, text="Hitung Estimasi", command=self.calculate_estimate).grid(row=6, column=0, columnspan=3, pady=15)
        
        # Frame untuk hasil dan preview
        results_preview_frame = ttk.Frame(main_frame)
        results_preview_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(results_preview_frame, text="Hasil Perhitungan", padding="10")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Preview frame
        preview_frame = ttk.LabelFrame(results_preview_frame, text="Preview G-code", padding="10")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Results labels
        ttk.Label(results_frame, text="Estimasi Waktu:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.time_label = ttk.Label(results_frame, text="0 menit", font=("Arial", 10))
        self.time_label.grid(row=0, column=1, sticky=tk.W, pady=3)
        
        self.time_detail_label = ttk.Label(results_frame, text="(0 jam, 0 menit, 0 detik)", font=("Arial", 8), foreground="blue")
        self.time_detail_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(results_frame, text="Feedrate Efektif:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.feedrate_result_label = ttk.Label(results_frame, text="0 mm/min", font=("Arial", 10))
        self.feedrate_result_label.grid(row=2, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(results_frame, text="Harga Awal:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=3)
        self.harga_awal_label = ttk.Label(results_frame, text="Rp 0", font=("Arial", 10))
        self.harga_awal_label.grid(row=3, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(results_frame, text="Diskon:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=3)
        self.diskon_label = ttk.Label(results_frame, text="Rp 0 (0%)", font=("Arial", 10))
        self.diskon_label.grid(row=4, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(results_frame, text="Harga Akhir:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=3)
        self.harga_akhir_label = ttk.Label(results_frame, text="Rp 0", font=("Arial", 10))
        self.harga_akhir_label.grid(row=5, column=1, sticky=tk.W, pady=3)
        
        # Preview G-code
        self.preview_text = scrolledtext.ScrolledText(preview_frame, width=40, height=15, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)
        
        # Canvas untuk visual preview
        self.canvas = tk.Canvas(preview_frame, width=300, height=200, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Siap", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        results_preview_frame.columnconfigure(0, weight=1)
        results_preview_frame.columnconfigure(1, weight=1)
        results_preview_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File G-code",
            filetypes=[("G-code files", "*.nc *.gcode *.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=file_path.split('/')[-1], foreground="green")
            self.status_label.config(text=f"File dipilih: {file_path.split('/')[-1]}")
            self.load_gcode_preview()
    
    def load_gcode_preview(self):
        if not self.file_path:
            return
        
        try:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines[:100]):  # Tampilkan 100 baris pertama
                    if i >= 100:
                        self.preview_text.insert(tk.END, "...\n")
                        break
                    self.preview_text.insert(tk.END, line)
            
            self.preview_text.config(state=tk.DISABLED)
            self.visualize_gcode()
            
        except Exception as e:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error membaca file: {str(e)}")
            self.preview_text.config(state=tk.DISABLED)
    
    def visualize_gcode(self):
        self.canvas.delete("all")
        
        if not self.file_path:
            return
        
        try:
            coordinates = []
            last_position = [0, 0]
            
            with open(self.file_path, 'r') as file:
                for line in file:
                    line = line.strip().upper()
                    
                    if not line or line.startswith((';', '(', '%')):
                        continue
                    
                    if line.startswith('G0') or line.startswith('G1'):
                        x_match = re.search(r'X([-+]?\d+\.?\d*)', line)
                        y_match = re.search(r'Y([-+]?\d+\.?\d*)', line)
                        
                        new_position = last_position.copy()
                        
                        if x_match:
                            new_position[0] = float(x_match.group(1))
                        if y_match:
                            new_position[1] = float(y_match.group(1))
                        
                        coordinates.append(new_position.copy())
                        last_position = new_position
            
            if not coordinates:
                self.canvas.create_text(150, 100, text="Tidak ada koordinat XY yang ditemukan", fill="red")
                return
            
            # Normalize coordinates untuk fitting di canvas
            x_coords = [coord[0] for coord in coordinates]
            y_coords = [coord[1] for coord in coordinates]
            
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
            
            canvas_width = self.canvas.winfo_width() - 20
            canvas_height = self.canvas.winfo_height() - 20
            
            if max_x - min_x == 0 or max_y - min_y == 0:
                self.canvas.create_text(150, 100, text="Koordinat tidak valid untuk visualisasi", fill="red")
                return
            
            scale_x = canvas_width / (max_x - min_x) * 0.8
            scale_y = canvas_height / (max_y - min_y) * 0.8
            scale = min(scale_x, scale_y)
            
            # Draw the path
            for i in range(len(coordinates) - 1):
                x1 = 10 + (coordinates[i][0] - min_x) * scale
                y1 = 10 + (coordinates[i][1] - min_y) * scale
                x2 = 10 + (coordinates[i+1][0] - min_x) * scale
                y2 = 10 + (coordinates[i+1][1] - min_y) * scale
                
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
            
            # Draw start and end points
            if coordinates:
                start_x = 10 + (coordinates[0][0] - min_x) * scale
                start_y = 10 + (coordinates[0][1] - min_y) * scale
                end_x = 10 + (coordinates[-1][0] - min_x) * scale
                end_y = 10 + (coordinates[-1][1] - min_y) * scale
                
                self.canvas.create_oval(start_x-3, start_y-3, start_x+3, start_y+3, fill="green", outline="green")
                self.canvas.create_oval(end_x-3, end_y-3, end_x+3, end_y+3, fill="red", outline="red")
                
                self.canvas.create_text(start_x, start_y-10, text="Start", fill="green")
                self.canvas.create_text(end_x, end_y+10, text="End", fill="red")
                
        except Exception as e:
            self.canvas.create_text(150, 100, text=f"Error visualisasi: {str(e)}", fill="red")
    
    def update_feedrate_from_slider(self, value):
        percentage = float(value)
        self.feedrate_entry.delete(0, tk.END)
        self.feedrate_entry.insert(0, f"{percentage:.1f}")
        self.update_feedrate_display(percentage)
    
    def update_feedrate_from_entry(self, event=None):
        try:
            percentage = float(self.feedrate_entry.get())
            if percentage < 0:
                percentage = 0
            elif percentage > 200:
                percentage = 200
            
            self.feedrate_var.set(percentage)
            self.feedrate_entry.delete(0, tk.END)
            self.feedrate_entry.insert(0, f"{percentage:.1f}")
            self.update_feedrate_display(percentage)
        except ValueError:
            self.feedrate_entry.delete(0, tk.END)
            self.feedrate_entry.insert(0, "100")
            self.feedrate_var.set(100)
            self.update_feedrate_display(100)
    
    def update_feedrate_display(self, percentage):
        self.effective_feedrate = self.default_feedrate * (percentage / 100)
        self.feedrate_percent_label.config(text=f"{percentage:.1f}%")
        self.effective_feedrate_label.config(text=f"Feedrate: {self.effective_feedrate:.1f} mm/min")
        self.status_label.config(text=f"Feedrate diatur ke {percentage:.1f}% ({self.effective_feedrate:.1f} mm/min)")
    
    def format_time(self, minutes):
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        seconds = int((minutes * 60) % 60)
        return f"{hours} jam, {remaining_minutes} menit, {seconds} detik"
    
    def parse_gcode(self):
        if not self.file_path:
            messagebox.showerror("Error", "Silakan pilih file G-code terlebih dahulu!")
            return None
        
        total_time = 0
        current_feedrate = self.default_feedrate
        last_position = [0, 0, 0]  # X, Y, Z
        line_count = 0
        
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    line_count += 1
                    line = line.strip().upper()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith((';', '(', '%')):
                        continue
                    
                    # Parse feedrate (F parameter)
                    if 'F' in line:
                        feed_match = re.search(r'F(\d+\.?\d*)', line)
                        if feed_match:
                            current_feedrate = float(feed_match.group(1))
                    
                    # Parse G0 (rapid move) and G1 (linear move)
                    if line.startswith('G0') or line.startswith('G1'):
                        # Extract coordinates
                        x_match = re.search(r'X([-+]?\d+\.?\d*)', line)
                        y_match = re.search(r'Y([-+]?\d+\.?\d*)', line)
                        z_match = re.search(r'Z([-+]?\d+\.?\d*)', line)
                        
                        new_position = last_position.copy()
                        
                        if x_match:
                            new_position[0] = float(x_match.group(1))
                        if y_match:
                            new_position[1] = float(y_match.group(1))
                        if z_match:
                            new_position[2] = float(z_match.group(1))
                        
                        # Calculate distance
                        dx = new_position[0] - last_position[0]
                        dy = new_position[1] - last_position[1]
                        dz = new_position[2] - last_position[2]
                        
                        distance = math.sqrt(dx**2 + dy**2 + dz**2)
                        
                        # Calculate time for this segment
                        if current_feedrate > 0 and distance > 0:
                            segment_time = distance / current_feedrate  # in minutes
                            total_time += segment_time
                        
                        last_position = new_position
            
            self.status_label.config(text=f"File berhasil diproses: {line_count} baris dibaca")
            return total_time
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat membaca file:\n{str(e)}")
            self.status_label.config(text="Error saat membaca file")
            return None
    
    def calculate_estimate(self):
        # Parse G-code and calculate time
        total_time_minutes = self.parse_gcode()
        
        if total_time_minutes is None:
            return
        
        # Apply effective feedrate adjustment
        if self.effective_feedrate > 0:
            adjusted_time = total_time_minutes * (self.default_feedrate / self.effective_feedrate)
        else:
            adjusted_time = total_time_minutes
        
        # Get price and discount
        try:
            harga_per_menit = float(self.harga_var.get()) if self.harga_var.get() else 0
            diskon_nominal = float(self.diskon_var.get()) if self.diskon_var.get() else 0
        except ValueError:
            messagebox.showerror("Error", "Harga dan diskon harus berupa angka!")
            self.status_label.config(text="Error: Input harga/diskon tidak valid")
            return
        
        # Calculate prices
        harga_awal = adjusted_time * harga_per_menit
        persen_diskon = (diskon_nominal / harga_awal * 100) if harga_awal > 0 else 0
        harga_akhir = max(0, harga_awal - diskon_nominal)
        
        # Update results
        self.time_label.config(text=f"{adjusted_time:.2f} menit")
        self.time_detail_label.config(text=f"({self.format_time(adjusted_time)})")
        self.feedrate_result_label.config(text=f"{self.effective_feedrate:.1f} mm/min")
        self.harga_awal_label.config(text=f"Rp {harga_awal:,.0f}")
        self.diskon_label.config(text=f"Rp {diskon_nominal:,.0f} ({persen_diskon:.1f}%)")
        self.harga_akhir_label.config(text=f"Rp {harga_akhir:,.0f}")
        
        self.status_label.config(text=f"Perhitungan selesai: {self.format_time(adjusted_time)}, Harga akhir: Rp {harga_akhir:,.0f}")

def main():
    root = tk.Tk()
    app = CNC_Time_Estimator(root)
    root.mainloop()

if __name__ == "__main__":
    main()