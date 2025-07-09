import tkinter as tk
from tkinter import ttk, messagebox

# Data kekuatan tarik material (dalam MPa)
material_properties = {
    'fiber': {
        'Sisal': {'min': 801, 'max': 1475, 'typical': 1138},
        'Nanas': {'min': 2013, 'max': 9028, 'typical': 5520.5},
        'Bambu': {'min': 940, 'max': 945, 'typical': 942.5}
    },
    'matrix': {
        'epoxy': {'typical': 60},
        'polyester': {'typical': 65}
    }
}

class CompositeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator Kekuatan Tarik Komposit")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame utama
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Judul
        title_label = ttk.Label(
            main_frame, 
            text="Kalkulator Kekuatan Tarik Komposit",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame form
        form_frame = ttk.LabelFrame(main_frame, text="Parameter Komposit", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Jenis Serat
        ttk.Label(form_frame, text="Jenis Serat:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fiber_type = tk.StringVar()
        fiber_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.fiber_type,
            values=["Sisal", "Nanas", "Bambu"],
            state="readonly"
        )
        fiber_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5)
        fiber_combobox.current(0)
        
        # Persentase Serat
        ttk.Label(form_frame, text="Persentase Serat (% volume):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fiber_percentage = tk.DoubleVar(value=10.0)
        fiber_spinbox = ttk.Spinbox(
            form_frame,
            textvariable=self.fiber_percentage,
            from_=0,
            to=50,
            increment=0.5,
            width=10
        )
        fiber_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Jenis Matriks
        ttk.Label(form_frame, text="Jenis Matriks:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.matrix_type = tk.StringVar()
        matrix_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.matrix_type,
            values=["epoxy", "polyester"],
            state="readonly"
        )
        matrix_combobox.grid(row=2, column=1, sticky=tk.EW, pady=5)
        matrix_combobox.current(0)
        
        # Tombol Hitung
        calculate_btn = ttk.Button(
            main_frame,
            text="Hitung Kekuatan Tarik",
            command=self.calculate_strength
        )
        calculate_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Frame Hasil
        self.result_frame = ttk.LabelFrame(main_frame, text="Hasil Perhitungan", padding=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.result_frame.pack_forget()  # Sembunyikan awal
        
        # Label Hasil
        ttk.Label(self.result_frame, text="Kekuatan tarik komposit:").pack(anchor=tk.W)
        self.strength_value = ttk.Label(self.result_frame, text="0 MPa", font=("Arial", 11, "bold"))
        self.strength_value.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(self.result_frame, text="Komposisi:").pack(anchor=tk.W)
        self.composition_value = ttk.Label(self.result_frame, text="-", font=("Arial", 11))
        self.composition_value.pack(anchor=tk.W)
        
        # Informasi Material
        info_frame = ttk.LabelFrame(main_frame, text="Informasi Material", padding=10)
        info_frame.pack(fill=tk.BOTH, pady=(20, 0))
        
        info_text = """Informasi Kekuatan Tarik Material:
- Serat Sisal: 801-1475 MPa
- Serat Daun Nanas: 2013-9028 MPa
- Serat Bambu: 940-945 MPa
- Matriks Epoxy: 40-80 MPa
- Matriks Polyester: 40-90 MPa"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
    
    def calculate_strength(self):
        try:
            fiber_type = self.fiber_type.get()
            fiber_percentage = self.fiber_percentage.get()
            matrix_type = self.matrix_type.get()
            
            # Validasi input
            if fiber_percentage < 0 or fiber_percentage > 50:
                messagebox.showerror("Error", "Persentase serat harus antara 0-50%")
                return
            
            # Hitung persentase matriks
            matrix_percentage = 100 - fiber_percentage
            
            # Dapatkan nilai kekuatan material
            fiber_strength = material_properties['fiber'][fiber_type]['typical']
            matrix_strength = material_properties['matrix'][matrix_type]['typical']
            
            # Hitung kekuatan komposit
            composite_strength = (fiber_strength * fiber_percentage/100) + (matrix_strength * matrix_percentage/100)
            
            # Tampilkan hasil
            self.strength_value.config(text=f"{composite_strength:.2f} MPa")
            
            fiber_name = {
                'Sisal': "Serat Sisal",
                'Nanas': "Serat Daun Nanas",
                'Bambu': "Serat Bambu"
            }.get(fiber_type, fiber_type)
            
            matrix_name = {
                'epoxy': "Epoxy",
                'polyester': "Polyester"
            }.get(matrix_type, matrix_type)
            
            self.composition_value.config(
                text=f"{fiber_percentage}% {fiber_name} + {matrix_percentage}% {matrix_name}"
            )
            
            # Tampilkan frame hasil
            self.result_frame.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CompositeCalculator(root)
    root.mainloop()