import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

class MatiSAMtool:
    def __init__(self, root):
        self.root = root
        self.root.title("MatiSAMtool v1.1")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.file_paths = {
            "BL": None,
            "AP": None,
            "CP": None,
            "CSC": None
        }

        # === Sección para seleccionar archivos ===
        row = 0
        for part in ["BL", "AP", "CP", "CSC"]:
            tk.Button(root, text=f"Seleccionar {part}", width=20, command=lambda p=part: self.load_file(p)).grid(row=row, column=0, padx=10, pady=8)
            setattr(self, f"{part}_label", tk.Label(root, text="Ningún archivo", anchor="w", width=50))
            getattr(self, f"{part}_label").grid(row=row, column=1)
            row += 1

        # === Botón Detectar dispositivo ===
        self.detect_button = tk.Button(root, text="Detectar dispositivo", command=self.detect_device, bg="lightblue")
        self.detect_button.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        # Info del dispositivo
        self.device_info = tk.Label(root, text="Dispositivo no detectado", fg="red")
        self.device_info.grid(row=row, column=0, columnspan=2)
        row += 1

        # === Botón Flashear ===
        self.flash_button = tk.Button(root, text="FLASHEAR", bg="green", fg="white", font=("Arial", 12, "bold"), width=20, command=self.flash_all)
        self.flash_button.grid(row=row, column=0, columnspan=2, pady=15)
        row += 1

        # === Opciones avanzadas ===
        tk.Label(root, text="Opciones avanzadas de flasheo:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        self.add_custom_option("RECOVERY TWRP", row, self.do_twrp)
        row += 1
        self.add_custom_option("CSC CHANGE", row, self.do_csc_change)
        row += 1
        self.add_custom_option("SOFTBRICK FIX", row, self.do_softbrick_fix)
        row += 1
        self.add_custom_option("FRP ERASE", row, self.do_frp_erase)
        row += 1

    def load_file(self, part):
        file_path = filedialog.askopenfilename(title=f"Selecciona el archivo {part}")
        if file_path:
            self.file_paths[part] = file_path
            label = getattr(self, f"{part}_label")
            label.config(text=file_path.split("/")[-1])

    def detect_device(self):
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')

            if len(lines) <= 1:
                self.device_info.config(text="No se detectó ningún dispositivo", fg="red")
                return

            device_id = lines[1].split()[0]
            brand = subprocess.run(["adb", "shell", "getprop", "ro.product.brand"], capture_output=True, text=True).stdout.strip()
            model = subprocess.run(["adb", "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()

            self.device_info.config(text=f"Detectado: {brand} {model} ({device_id})", fg="green")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo detectar el dispositivo:\n{str(e)}")

    def flash_all(self):
        # Simulación del flasheo
        if all(self.file_paths.values()):
            messagebox.showinfo("Flasheo", "Iniciando flasheo completo (simulado)...")
            # Aquí se puede llamar a heimdall o similar
        else:
            messagebox.showwarning("Error", "Debes cargar todos los archivos: BL, AP, CP y CSC.")

    def add_custom_option(self, label_text, row, command):
        tk.Label(self.root, text=label_text).grid(row=row, column=0, sticky="w", padx=10)
        tk.Button(self.root, text="HACERLO", command=command, bg="gray90").grid(row=row, column=1, sticky="e", padx=10)

    # === Funciones simuladas para cada opción ===

    def do_twrp(self):
        messagebox.showinfo("TWRP", "Instalación de Recovery TWRP (simulado)")

    def do_csc_change(self):
        messagebox.showinfo("CSC", "Cambio de CSC (simulado)")

    def do_softbrick_fix(self):
        messagebox.showinfo("Softbrick Fix", "Reparación de softbrick (simulado)")

    def do_frp_erase(self):
        messagebox.showinfo("FRP", "Eliminación de FRP (simulado)")

# Iniciar app
if __name__ == "__main__":
    root = tk.Tk()
    app = MatiSAMtool(root)
    root.mainloop()
