import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Entry

from PIL import Image, ImageTk
import math
from tkinter import messagebox

from PIL.ImageTk import PhotoImage
from openpyxl import Workbook
from datetime import datetime
from tkinter import filedialog

class ShaftHubInterferenceCalculator:
    temp_shaft: Entry
    logo_photo: PhotoImage

    def __init__(self, root):
        self.root = root
        self.root.title("Shaft & Hub Interference Calculator")

        # Set the background color for the main window
        bg_color = '#000000'  # Black background
        self.root.configure(bg=bg_color)

        # Set style for frames
        style = ttk.Style()
        style.configure('TLabelframe', background=bg_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground='white')

        try:
            logo_path = "LAVA_logo_white_on_red.png"
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(root, image=self.logo_photo, bg=bg_color)
            logo_label.grid(row=0, column=0, padx=5, pady=5)

            # Load and display interference fit image
            fit_path = "shafthub.png"
            fit_img = Image.open(fit_path)
            fit_img = fit_img.resize((200, 200), Image.Resampling.LANCZOS)
            self.fit_photo = ImageTk.PhotoImage(fit_img)
            fit_label = tk.Label(root, image=self.fit_photo, bg=bg_color)
            fit_label.grid(row=1, column=4, rowspan=2, padx=10, pady=5)

            # Load and display prime formulas
            formulas_path ="formulas.png"
            formulas_img = Image.open(formulas_path)
            formulas_img = formulas_img.resize((600, 400), Image.Resampling.LANCZOS)
            self.formulas_photo = ImageTk.PhotoImage(formulas_img)
            formulas_label = tk.Label(root, image=self.formulas_photo, bg=bg_color)
            formulas_label.grid(row=3, column=4, rowspan=2, padx=10, pady=5)

        except Exception as e:
            print(f"Error initializing the calculator: {e}")

        # Title (moved to row 0, column 1 to be next to the logo)
        title_label = tk.Label(root, text="Shaft & Hub Interference Calculator",
                               font=('Arial', 20, 'bold'), fg='white', bg=bg_color)
        title_label.grid(row=0, column=1, columnspan=3, pady=10)
        # Input Frame
        input_frame = ttk.LabelFrame(root, text="Input Parameters")
        input_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        # Power and Speed inputs
        ttk.Label(input_frame, text="Power (MW):", foreground='white', background=bg_color).grid(row=0, column=0, padx=5, pady=5)
        self.power = ttk.Entry(input_frame)
        self.power.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Speed (RPM):", foreground='white', background=bg_color).grid(row=0, column=2, padx=5, pady=5)
        self.speed = ttk.Entry(input_frame)
        self.speed.grid(row=0, column=3, padx=5, pady=5)

        # Friction and geometry inputs
        ttk.Label(input_frame, text="Friction Coefficient:", foreground='white', background=bg_color).grid(row=1, column=0, padx=5, pady=5)
        self.friction = ttk.Entry(input_frame)
        self.friction.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="b - Interface Radius (mm):", foreground='white', background=bg_color).grid(row=2, column=2, padx=5, pady=5)
        self.radius = ttk.Entry(input_frame)
        self.radius.grid(row=2, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="L- Interface Length (mm):", foreground='white', background=bg_color).grid(row=2, column=0, padx=5, pady=5)
        self.length = ttk.Entry(input_frame)
        self.length.grid(row=2, column=1, padx=5, pady=5)

        # Additional parameters
        ttk.Label(input_frame, text="Short circuit torque factor (1-10):", foreground='white', background=bg_color).grid(row=3, column=0, padx=5, pady=5)
        self.sct = ttk.Entry(input_frame)
        self.sct.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="a - shaft Inner Radius (mm):", foreground='white', background=bg_color).grid(row=1, column=2, padx=5, pady=5)
        self.radius_a = ttk.Entry(input_frame)
        self.radius_a.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="c - Outer Radius (mm):", foreground='white', background=bg_color).grid(row=3, column=2, padx=5, pady=5)
        self.radius_c = ttk.Entry(input_frame)
        self.radius_c.grid(row=3, column=3, padx=5, pady=5)

        # Material properties
        ttk.Label(input_frame, text="μo Hub (Poisson's ratio):", foreground='white', background=bg_color).grid(row=5, column=0, padx=5, pady=5)
        self.mu_o = ttk.Entry(input_frame)
        self.mu_o.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="μi shaft (Poisson's ratio):", foreground='white', background=bg_color).grid(row=5, column=2, padx=5, pady=5)
        self.mu_i = ttk.Entry(input_frame)
        self.mu_i.grid(row=5, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Eo Hub GPa:", foreground='white', background=bg_color).grid(row=6, column=0, padx=5, pady=5)
        self.E_o = ttk.Entry(input_frame)
        self.E_o.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Ei shaft GPa:", foreground='white', background=bg_color).grid(row=6, column=2, padx=5, pady=5)
        self.E_i = ttk.Entry(input_frame)
        self.E_i.grid(row=6, column=3, padx=5, pady=5)

        # Add density inputs
        ttk.Label(input_frame, text="Hub Density (kg/m³):", foreground='white', background=bg_color).grid(row=7, column=0, padx=5, pady=5)
        self.density_hub = ttk.Entry(input_frame)
        self.density_hub.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Shaft Density (kg/m³):", foreground='white', background=bg_color).grid(row=7, column=2, padx=5, pady=5)
        self.density_shaft = ttk.Entry(input_frame)
        self.density_shaft.grid(row=7, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Hub Yield Strength (MPa):", foreground='white', background=bg_color).grid(row=8, column=0, padx=5, pady=5)
        self.yield_hub = ttk.Entry(input_frame)
        self.yield_hub.grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Shaft Yield Strength (MPa):", foreground='white', background=bg_color).grid(row=8, column=2, padx=5, pady=5)
        self.yield_shaft = ttk.Entry(input_frame)
        self.yield_shaft.grid(row=8, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Hub Thermal Expansion Coefficient (1/°C) x10^-6:", foreground='white', background=bg_color).grid(row=9, column=0, padx=5, pady=5)
        self.alpha_hub = ttk.Entry(input_frame)
        self.alpha_hub.grid(row=9, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Shaft Thermal Expansion Coefficient (1/°C) x10^-6:", foreground='white', background=bg_color).grid(row=9, column=2, padx=5, pady=5)
        self.alpha_shaft = ttk.Entry(input_frame)
        self.alpha_shaft.grid(row=9, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Hub Temperature (°C):", foreground='white', background=bg_color).grid(row=10, column=0, padx=5, pady=5)
        self.temp_hub = ttk.Entry(input_frame)
        self.temp_hub.grid(row=10, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Shaft Temperature (°C):", foreground='white', background=bg_color).grid(row=10, column=2, padx=5, pady=5)
        self.temp_shaft = ttk.Entry(input_frame)
        self.temp_shaft.grid(row=10, column=3, padx=5, pady=5)

        # Add tolerance inputs - Hole tolerances stacked vertically
        ttk.Label(input_frame, text="Hole Plus Tolerance (mm):", foreground='white', background=bg_color).grid(row=11, column=0, padx=5, pady=5)
        self.hole_plus = ttk.Entry(input_frame)
        self.hole_plus.grid(row=11, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Hole Minus Tolerance (mm):", foreground='white', background=bg_color).grid(row=12, column=0, padx=5, pady=5)
        self.hole_minus = ttk.Entry(input_frame)
        self.hole_minus.grid(row=12, column=1, padx=5, pady=5)

        # Shaft tolerances stacked vertically
        ttk.Label(input_frame, text="Shaft Plus Tolerance (mm):", foreground='white', background=bg_color).grid(row=11, column=2, padx=5, pady=5)
        self.shaft_plus = ttk.Entry(input_frame)
        self.shaft_plus.grid(row=11, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Shaft Minus Tolerance (mm):", foreground='white', background=bg_color).grid(row=12, column=2, padx=5, pady=5)
        self.shaft_minus = ttk.Entry(input_frame)
        self.shaft_minus.grid(row=12, column=3, padx=5, pady=5)

        # Results Frame
        results_frame = ttk.LabelFrame(root, text="Results")
        results_frame.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        # Add Save Button
        self.save_button = ttk.Button(root, text="Save Results to Excel",
                                      command=self.save_to_excel,
                                      style='Large.TButton')
        self.save_button.grid(row=5, column=0, columnspan=4, pady=10, padx=10)

        # Results labels
        self.torque_var = tk.StringVar()
        self.pressure_var = tk.StringVar()
        self.interference_var = tk.StringVar()
        self.max_interference_var = tk.StringVar()
        self.min_interference_var = tk.StringVar()
        self.hole_diameter_var = tk.StringVar()
        self.shaft_diameter_var = tk.StringVar()
        self.fit_status_var = tk.StringVar()
        self.fit_status_label = tk.Label(results_frame, textvariable=self.fit_status_var,
                                          font=('Arial', 12, 'bold'), bg=bg_color)
        self.fit_status_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        # Add new labels for stress results in the results_frame
        self.stress_hub_var = tk.StringVar()
        self.stress_shaft_var = tk.StringVar()
        self.stress_status_var = tk.StringVar()
        self.thermal_interference_var = tk.StringVar()
        self.thermal_status_var = tk.StringVar()
        self.thermal_loss_var = tk.StringVar()
        self.stress_status_label = tk.Label(results_frame, textvariable=self.stress_status_var,
                                            font=('Arial', 12, 'bold'), bg=bg_color)
        self.stress_status_label.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        ttk.Label(results_frame, text="Shaft Torque (N·m):", foreground='white', background=bg_color).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.torque_var, foreground='white', background=bg_color).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Interference Pressure (Pa):", foreground='white', background=bg_color).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.pressure_var, foreground='white', background=bg_color).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Total Diametrical Interference (μm):", foreground='white', background=bg_color).grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.interference_var, foreground='white', background=bg_color).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Maximum Interference (μm):", foreground='white', background=bg_color).grid(row=3, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.max_interference_var, foreground='white', background=bg_color).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Minimum Interference (μm):", foreground='white', background=bg_color).grid(row=4, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.min_interference_var, foreground='white', background=bg_color).grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Hole Diameter (mm):", foreground='white', background=bg_color).grid(row=5, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.hole_diameter_var, foreground='white', background=bg_color).grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Shaft Diameter (mm):", foreground='white', background=bg_color).grid(row=6, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.shaft_diameter_var, foreground='white', background=bg_color).grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Stress in Hub (MPa):", foreground='white', background=bg_color).grid(row=8, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.stress_hub_var, foreground='white', background=bg_color).grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Stress in Shaft (MPa):", foreground='white', background=bg_color).grid(row=9, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.stress_shaft_var, foreground='white', background=bg_color).grid(row=9, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Total Thermal Interference Loss (μm):", foreground='white', background=bg_color).grid(row=11, column=0, padx=5, pady=5)
        ttk.Label(results_frame, textvariable=self.thermal_loss_var, foreground='white', background=bg_color).grid(row=11, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Total Diametrical Thermal Interference (μm):", foreground='white', background=bg_color).grid(row=12, column=0, padx=5,
                                                                                         pady=5)
        ttk.Label(results_frame, textvariable=self.thermal_interference_var, foreground='white', background=bg_color).grid(row=12, column=1, padx=5, pady=5)

        self.thermal_status_label = tk.Label(results_frame, textvariable=self.thermal_status_var,
                                             font=('Arial', 12, 'bold'), bg=bg_color)
        self.thermal_status_label.grid(row=13, column=0, columnspan=2, padx=5, pady=5)

        # Bind events to update calculations
        self.bind_updates()

    def bind_updates(self):
        self.power.bind('<KeyRelease>', self.update_calculations)
        self.speed.bind('<KeyRelease>', self.update_calculations)
        self.friction.bind('<KeyRelease>', self.update_calculations)
        self.radius.bind('<KeyRelease>', self.update_calculations)
        self.length.bind('<KeyRelease>', self.update_calculations)
        self.sct.bind('<KeyRelease>', self.update_calculations)
        self.radius_a.bind('<KeyRelease>', self.update_calculations)
        self.radius_c.bind('<KeyRelease>', self.update_calculations)
        self.mu_o.bind('<KeyRelease>', self.update_calculations)
        self.mu_i.bind('<KeyRelease>', self.update_calculations)
        self.E_o.bind('<KeyRelease>', self.update_calculations)
        self.E_i.bind('<KeyRelease>', self.update_calculations)
        self.hole_plus.bind('<KeyRelease>', self.update_calculations)
        self.hole_minus.bind('<KeyRelease>', self.update_calculations)
        self.shaft_plus.bind('<KeyRelease>', self.update_calculations)
        self.shaft_minus.bind('<KeyRelease>', self.update_calculations)
        self.yield_hub.bind('<KeyRelease>', self.update_calculations)
        self.yield_shaft.bind('<KeyRelease>', self.update_calculations)
        self.density_hub.bind('<KeyRelease>', self.update_calculations)
        self.density_shaft.bind('<KeyRelease>', self.update_calculations)
        self.alpha_hub.bind('<KeyRelease>', self.update_calculations)
        self.alpha_shaft.bind('<KeyRelease>', self.update_calculations)
        self.temp_hub.bind('<KeyRelease>', self.update_calculations)
        self.temp_shaft.bind('<KeyRelease>', self.update_calculations)

    def update_calculations(self, event=None):
        try:
            # Calculate torque
            P = float(self.power.get()) * 1e6  # Convert MW to W
            S = float(self.speed.get())
            T = P / ((S * 2 * math.pi) / 60)
            self.torque_var.set(f"{T:.4f}")

            # Calculate interference pressure
            f = float(self.friction.get())
            b = float(self.radius.get()) / 1000  # Convert mm to m
            L = float(self.length.get()) / 1000  # Convert mm to m
            p = T / (2 * f * math.pi * b ** 2 * L)
            self.pressure_var.set(f"{p:.4f}")

            # Calculate total diametrical interference
            sct = float(self.sct.get())
            a = float(self.radius_a.get()) / 1000  # Convert mm to m
            c = float(self.radius_c.get()) / 1000  # Convert mm to m
            mu_o = float(self.mu_o.get())
            mu_i = float(self.mu_i.get())
            E_o = float(self.E_o.get()) * 1e9  # Convert GPa to Pa
            E_i = float(self.E_i.get()) * 1e9  # Convert GPa to Pa

            delta = sct * 2 * b * p * (
                    (1 / E_o * ((c ** 2 + b ** 2) / (c ** 2 - b ** 2) + mu_o)) +
                    (1 / E_i * ((b ** 2 + a ** 2) / (b ** 2 - a ** 2) - mu_i))
            )

            self.interference_var.set(f"{delta * 1e6:.4f}")  # Convert m to μm

            # Update diameter displays
            self.hole_diameter_var.set(f"{2 * b * 1000:.4f}")  # Show in mm
            self.shaft_diameter_var.set(f"{2 * b * 1000:.4f}")  # Show in mm

            # Calculate interference fits
            hole_plus = float(self.hole_plus.get()) / 1000  # Convert mm to m
            hole_minus = float(self.hole_minus.get()) / 1000
            shaft_plus = float(self.shaft_plus.get()) / 1000
            shaft_minus = float(self.shaft_minus.get()) / 1000

            max_interference = abs(shaft_plus - hole_minus) * 1e6  # Convert to μm
            min_interference = abs(shaft_minus - hole_plus) * 1e6  # Convert to μm

            self.max_interference_var.set(f"{max_interference:.4f}")
            self.min_interference_var.set(f"{min_interference:.4f}")

            # Check if interference fit works
            if min_interference >= delta * 1e6:
                self.fit_status_var.set("This interference fit works")
                self.fit_status_label.configure(foreground="green")
            else:
                self.fit_status_var.set("This interference fit doesn't work, Try again")
                self.fit_status_label.configure(foreground="red")

            # Calculate stresses
            # Convert interference pressure to MPa for comparison with yield strength
            p_MPa = p/1e6

            # Calculate stresses in MPa
            stress_hub = p_MPa * ((c ** 2 + b ** 2) / (c ** 2 - b ** 2))
            stress_shaft = p_MPa * ((b ** 2 + a ** 2) / (b ** 2 - a ** 2))

            self.stress_hub_var.set(f"{stress_hub:.2f}")
            self.stress_shaft_var.set(f"{stress_shaft:.2f}")

            # Check stresses against yield strengths
            try:
                yield_hub = float(self.yield_hub.get())
                yield_shaft = float(self.yield_shaft.get())

                if stress_hub > yield_hub:
                    self.stress_status_var.set("Stress in Hub exceeds material properties")
                    self.stress_status_label.configure(foreground="red")
                elif stress_shaft > yield_shaft:
                    self.stress_status_var.set("Stress in Shaft exceeds material properties")
                    self.stress_status_label.configure(foreground="red")
                else:
                    self.stress_status_var.set("Stress both in Hub & shaft remains in the elastic region")
                    self.stress_status_label.configure(foreground="green")

            except ValueError:
                    # Handle case when yield strengths are not yet entered
                    self.stress_status_var.set("")

            # Thermal interference calculations
            alpha_hub = float(self.alpha_hub.get())*1e-6
            alpha_shaft = float(self.alpha_shaft.get())* 1e-6
            temp_hub = float(self.temp_hub.get())
            temp_shaft = float(self.temp_shaft.get())

            # Calculate thermal interference loss
            thermal_loss = (-2*b*alpha_shaft*(temp_shaft-25)+2*b*alpha_hub*(temp_hub-25)) * 1e6 # Convert m to μm
            self.thermal_loss_var.set(f"{thermal_loss:.4f}")

            total_thermal_interference = (delta + 2*b*alpha_shaft*(temp_shaft-25)-2*b*alpha_hub*(temp_hub-25)) * 1e6 # Convert m to μm
            self.thermal_interference_var.set(f"{total_thermal_interference:.4f}")

            if 0 < total_thermal_interference <= min_interference:
                self.thermal_status_var.set("Total diametrical interference is sufficient, good job!")
                self.thermal_status_label.configure(foreground="green")
            else:
                self.thermal_status_var.set("Total diametrical interference is insufficient")
                self.thermal_status_label.configure(foreground="red")

        except ValueError:
            pass
        except ZeroDivisionError:
            messagebox.showerror("Error", "Division by zero error. Please check your inputs.")

    def save_to_excel(self):
        try:
            # Create a new workbook and select the active sheet
            wb = Workbook()
            ws = wb.active
            ws.title = "Shrink Fit Calculations"

            # Get current date and time for filename
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Add headers and values
            data = [
                ["Shrink Fit Calculator Results", ""],
                ["Calculated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["", ""],
                ["Input Parameters", "Values"],
                ["Power (MW)", self.power.get()],
                ["Speed (RPM)", self.speed.get()],
                ["Friction Coefficient", self.friction.get()],
                ["Interface Radius (mm)", self.radius.get()],
                ["Interface Length (mm)", self.length.get()],
                ["Short circuit torque factor", self.sct.get()],
                ["Shaft Inner Radius (mm)", self.radius_a.get()],
                ["Outer Radius (mm)", self.radius_c.get()],
                ["Hub Poisson's ratio", self.mu_o.get()],
                ["Shaft Poisson's ratio", self.mu_i.get()],
                ["Hub Young's modulus (GPa)", self.E_o.get()],
                ["Shaft Young's modulus (GPa)", self.E_i.get()],
                ["Hub Density (kg/m³)", self.density_hub.get()],
                ["Shaft Density (kg/m³)", self.density_shaft.get()],
                ["Hub Yield Strength (MPa)", self.yield_hub.get()],
                ["Shaft Yield Strength (MPa)", self.yield_shaft.get()],
                ["Hub Thermal Expansion Coefficient x10^-6 (1/°C)", self.alpha_hub.get()],
                ["Shaft Thermal Expansion Coefficient x10^-6 (1/°C)", self.alpha_shaft.get()],
                ["Hub Temperature (°C)", self.temp_hub.get()],
                ["Shaft Temperature (°C)", self.temp_shaft.get()],
                ["", ""],
                ["Tolerances", ""],
                ["Hole diameter", self.hole_diameter_var.get()],
                ["Hole plus", self.hole_plus.get()],
                ["Hole minus", self.hole_minus.get()],
                ["Shaft diameter", self.shaft_diameter_var.get()],
                ["Shaft plus", self.shaft_plus.get()],
                ["Shaft minus", self.shaft_minus.get()],
                ["", ""],
                ["Results", ""],
                ["Shaft Torque (N·m)", self.torque_var.get()],
                ["Interference Pressure (Pa)", self.pressure_var.get()],
                ["Total Diametrical Interference (μm)", self.interference_var.get()],
                ["Maximum Interference (μm)", self.max_interference_var.get()],
                ["Minimum Interference (μm)", self.min_interference_var.get()],
                ["Stress in Hub (MPa)", self.stress_hub_var.get()],
                ["Stress in Shaft (MPa)", self.stress_shaft_var.get()],
                ["Total Thermal Interference Loss (μm)", self.thermal_loss_var.get()],
                ["Total Diametrical Thermal Interference (μm)", self.thermal_interference_var.get()],
                ["", ""],
                ["Status Messages", ""],
                ["Fit Status", self.fit_status_var.get()],
                ["Stress Status", self.stress_status_var.get()],
                ["Thermal Interference Status", self.thermal_status_var.get()]
            ]

            # Write data to worksheet
            for row in data:
                ws.append(row)

            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column = list(column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column[0].column_letter].width = adjusted_width

            # Ask user where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                initialfile=f'ShrinkFit_Calculation_{current_time}.xlsx',
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if file_path:  # If user didn't cancel the save dialog
                wb.save(file_path)
                messagebox.showinfo("Success", "Results saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShaftHubInterferenceCalculator(root)
    root.mainloop()


