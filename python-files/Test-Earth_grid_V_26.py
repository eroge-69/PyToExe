import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
import pyautogui
import csv
import os

class IEEE80GroundingGrid:
    def __init__(self, root):
        self.root = root
        self.root.title("IEEE 80 Substation Grounding Grid Analysis")
        self.root.geometry("1200x900")

        # Project Info
        self.project_name = tk.StringVar(value="")
        self.project_date = tk.StringVar(value="")
        self.project_rev = tk.StringVar(value="")

        # Grid parameters
        self.grid_length = tk.DoubleVar(value=100.0)
        self.grid_width = tk.DoubleVar(value=80.0)
        self.conductor_spacing = tk.DoubleVar(value=10.0)
        self.burial_depth = tk.DoubleVar(value=0.6)
        self.rod_depth = tk.DoubleVar(value=2.0)
        self.rod_diameter = tk.DoubleVar(value=16.0)
        self.num_rods_length = tk.IntVar(value=5)
        self.num_rods_width = tk.IntVar(value=3)
        self.conductor_diameter = tk.DoubleVar(value=9.5)

        # Electrical & Soil
        self.soil_rho1 = tk.DoubleVar(value=100.0)
        self.soil_rho2 = tk.DoubleVar(value=300.0)
        self.soil_h = tk.DoubleVar(value=1.0)
        self.fault_current = tk.DoubleVar(value=5000.0)
        self.fault_duration = tk.DoubleVar(value=0.5)

        # Output values
        self.grid_resistance = tk.StringVar(value="0.0")
        self.step_voltage = tk.StringVar(value="0.0")
        self.touch_voltage = tk.StringVar(value="0.0")
        self.safety_factor = tk.StringVar(value="0.0")
        self.apparent_rho = tk.StringVar(value="0.0")

        # Colorbar handle
        self._colorbar = None

        # Store last computed grids
        self.surface_X = None
        self.surface_Y = None
        self.surface_Z = None

        self.step_X = None
        self.step_Y = None
        self.step_Z = None

        self.touch_X = None
        self.touch_Y = None
        self.touch_Z = None

        self.setup_gui()
        self.create_initial_plot()
        
    def setup_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        param_frame = ttk.Frame(notebook)
        viz_frame = ttk.Frame(notebook)
        results_frame = ttk.Frame(notebook)

        notebook.add(param_frame, text="Grid Parameters")
        notebook.add(viz_frame, text="3D Visualization")
        notebook.add(results_frame, text="Analysis Results")

        self.setup_parameters_tab(param_frame)
        self.setup_visualization_tab(viz_frame)
        self.setup_results_tab(results_frame)

    def setup_parameters_tab(self, parent):
        frame_buttons = ttk.Frame(parent)
        frame_buttons.pack(anchor='ne', padx=10, pady=5)

        ttk.Button(frame_buttons, text="Print Screen", command=self.print_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="Export CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)

        try:
            logo_image = Image.open("my_logo.png")
            new_width = 200
            w0, h0 = logo_image.size
            aspect_ratio = h0 / w0
            new_height = int(new_width * aspect_ratio)

            logo_image = logo_image.resize((new_width, new_height), Image.LANCZOS)
            logo_tk = ImageTk.PhotoImage(logo_image)

            logo_label = tk.Label(parent, image=logo_tk, bg='white')
            logo_label.image = logo_tk
            logo_label.pack(side=tk.RIGHT, anchor='ne', padx=10, pady=(10, 20))
        except Exception as e:
            print(f"Could not load logo: {e}")

        proj_frame = ttk.LabelFrame(parent, text="Project Information", padding="10")
        proj_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(proj_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(proj_frame, textvariable=self.project_name, width=40).grid(row=0, column=1, padx=5)

        ttk.Label(proj_frame, text="Project Date:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Entry(proj_frame, textvariable=self.project_date, width=40).grid(row=1, column=1, padx=5)

        ttk.Label(proj_frame, text="Rev:").grid(row=2, column=0, sticky=tk.W, padx=5)
        ttk.Entry(proj_frame, textvariable=self.project_rev, width=40).grid(row=2, column=1, padx=5)

        dims_frame = ttk.LabelFrame(parent, text="Grid Dimensions", padding="10")
        dims_frame.pack(fill=tk.X, padx=10, pady=5)

        labels = [
            ("Grid Length (m):", self.grid_length),
            ("Grid Width (m):", self.grid_width),
            ("Conductor Spacing (m):", self.conductor_spacing),
            ("Burial Depth (m):", self.burial_depth),
            ("Earth Rod Depth (m):", self.rod_depth),
            ("Earth Rod Diameter (mm):", self.rod_diameter),
            ("Number of Rods Along Length:", self.num_rods_length),
            ("Number of Rods Along Width:", self.num_rods_width),
            ("Conductor Diameter (mm):", self.conductor_diameter),
        ]

        for i, (text, var) in enumerate(labels):
            ttk.Label(dims_frame, text=text).grid(row=i, column=0, sticky=tk.W, padx=5)
            ttk.Entry(dims_frame, textvariable=var, width=10).grid(row=i, column=1, padx=5)

        elec_frame = ttk.LabelFrame(parent, text="Electrical and Soil Parameters", padding="10")
        elec_frame.pack(fill=tk.X, padx=10, pady=5)

        labels2 = [
            ("Top Layer Resistivity ρ₁ (Ω·m):", self.soil_rho1),
            ("Bottom Layer Resistivity ρ₂ (Ω·m):", self.soil_rho2),
            ("Top Layer Thickness H (m):", self.soil_h),
            ("Fault Current (A):", self.fault_current),
            ("Fault Duration (s):", self.fault_duration),
        ]

        for i, (text, var) in enumerate(labels2):
            ttk.Label(elec_frame, text=text).grid(row=i, column=0, sticky=tk.W, padx=5)
            ttk.Entry(elec_frame, textvariable=var, width=10).grid(row=i, column=1, padx=5)

        ttk.Button(parent, text="Calculate Grid Analysis", command=self.calculate_ieee80).pack(pady=20)

    def setup_visualization_tab(self, parent):
        frame_buttons = ttk.Frame(parent)
        frame_buttons.pack(anchor='ne', padx=10, pady=5)

        ttk.Button(frame_buttons, text="Print Screen", command=self.print_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="Export CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(control_frame, text="Update 3D Plot", command=self.update_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Voltage Distribution", command=self.show_voltage_distribution).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Step Potentials", command=self.show_step_potentials).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Touch Potentials", command=self.show_touch_potentials).pack(side=tk.LEFT, padx=5)

        plot_frame = ttk.Frame(parent)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_results_tab(self, parent):
        frame_buttons = ttk.Frame(parent)
        frame_buttons.pack(anchor='ne', padx=10, pady=5)

        ttk.Button(frame_buttons, text="Print Screen", command=self.print_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="Export CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        labels = [
            ("Grid Resistance (Ω):", self.grid_resistance),
            ("Apparent Soil Resistivity (Ω·m):", self.apparent_rho),
            ("Step Voltage (V):", self.step_voltage),
            ("Touch Voltage (V):", self.touch_voltage),
            ("Safety Factor:", self.safety_factor),
        ]

        for i, (text, var) in enumerate(labels):
            ttk.Label(frame, text=text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(frame, textvariable=var, font=('Arial', 10, 'bold')).grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)

    def print_screen(self):
        try:
            project = self.project_name.get().strip()
            if project == "":
                filename = "screenshot.png"
            else:
                project_clean = "".join(c for c in project if c.isalnum() or c in (" ", "_", "-"))
                filename = f"{project_clean}.png"

            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            w = self.root.winfo_width()
            h = self.root.winfo_height()

            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot.save(filename)

            messagebox.showinfo("Print Screen", f"Screenshot saved as:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not capture screen:\n{e}")

    def export_to_csv(self):
        try:
            project = self.project_name.get().strip()
            if project == "":
                filename = "grid_analysis_export.csv"
            else:
                project_clean = "".join(c for c in project if c.isalnum() or c in (" ", "_", "-"))
                filename = f"{project_clean}.csv"

            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow(["Project Information"])
                writer.writerow(["Project Name", self.project_name.get()])
                writer.writerow(["Project Date", self.project_date.get()])
                writer.writerow(["Revision", self.project_rev.get()])
                writer.writerow([])

                writer.writerow(["Grid Parameters"])
                writer.writerow(["Grid Length (m)", self.grid_length.get()])
                writer.writerow(["Grid Width (m)", self.grid_width.get()])
                writer.writerow(["Conductor Spacing (m)", self.conductor_spacing.get()])
                writer.writerow(["Burial Depth (m)", self.burial_depth.get()])
                writer.writerow(["Rod Depth (m)", self.rod_depth.get()])
                writer.writerow(["Rod Diameter (mm)", self.rod_diameter.get()])
                writer.writerow(["Rods Along Length", self.num_rods_length.get()])
                writer.writerow(["Rods Along Width", self.num_rods_width.get()])
                writer.writerow(["Conductor Diameter (mm)", self.conductor_diameter.get()])
                writer.writerow([])

                writer.writerow(["Electrical and Soil Parameters"])
                writer.writerow(["Soil Rho1 (Ω·m)", self.soil_rho1.get()])
                writer.writerow(["Soil Rho2 (Ω·m)", self.soil_rho2.get()])
                writer.writerow(["Top Layer Thickness H (m)", self.soil_h.get()])
                writer.writerow(["Fault Current (A)", self.fault_current.get()])
                writer.writerow(["Fault Duration (s)", self.fault_duration.get()])
                writer.writerow([])

                writer.writerow(["Calculation Results"])
                writer.writerow(["Grid Resistance (Ω)", self.grid_resistance.get()])
                writer.writerow(["Apparent Soil Resistivity (Ω·m)", self.apparent_rho.get()])
                writer.writerow(["Step Voltage (V)", self.step_voltage.get()])
                writer.writerow(["Touch Voltage (V)", self.touch_voltage.get()])
                writer.writerow(["Safety Factor", self.safety_factor.get()])
                writer.writerow([])

                # Save surface voltage
                if self.surface_X is not None:
                    writer.writerow(["Surface Voltage Distribution (V)"])
                    writer.writerow(["X (m)", "Y (m)", "Voltage (V)"])
                    for x, y, z in zip(self.surface_X.flatten(),
                                       self.surface_Y.flatten(),
                                       self.surface_Z.flatten()):
                        writer.writerow([x, y, z])
                    writer.writerow([])

                # Save step potential
                if self.step_X is not None:
                    writer.writerow(["Step Potential Grid (V)"])
                    writer.writerow(["X (m)", "Y (m)", "Step Potential (V)"])
                    for x, y, z in zip(self.step_X.flatten(),
                                       self.step_Y.flatten(),
                                       self.step_Z.flatten()):
                        writer.writerow([x, y, z])
                    writer.writerow([])

                # Save touch potential
                if self.touch_X is not None:
                    writer.writerow(["Touch Potential Grid (V)"])
                    writer.writerow(["X (m)", "Y (m)", "Touch Potential (V)"])
                    for x, y, z in zip(self.touch_X.flatten(),
                                       self.touch_Y.flatten(),
                                       self.touch_Z.flatten()):
                        writer.writerow([x, y, z])
                    writer.writerow([])

            messagebox.showinfo("Export Complete", f"Data exported to:\n{os.path.abspath(filename)}")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def calculate_apparent_resistivity(self):
        rho1 = self.soil_rho1.get()
        rho2 = self.soil_rho2.get()
        H = self.soil_h.get()
        D = max(self.burial_depth.get(), self.conductor_spacing.get())
        rho_eq = rho1 + (rho2 - rho1) / (1 + (4 * H / D))
        return rho_eq

    def calculate_ieee80(self):
        try:
            rho = self.calculate_apparent_resistivity()
            L = self.grid_length.get()
            W = self.grid_width.get()
            spacing = self.conductor_spacing.get()
            h = self.burial_depth.get()
            I_fault = self.fault_current.get()
            t_fault = self.fault_duration.get()

            A = L * W
            n_long = int(L / spacing) + 1
            n_wide = int(W / spacing) + 1
            L_total = n_long * W + n_wide * L

            sqrt_A = math.sqrt(A)
            term1 = rho / (math.pi * sqrt_A)
            term2 = 1 + 1 / (1 + h * math.sqrt(20 / A))
            R_grid = term1 * term2

            d = self.conductor_diameter.get() / 1000
            D = spacing
            Km = 1 / (2 * math.pi) * math.log(D ** 2 / (16 * h * d))
            if Km < 0.5:
                Km = 0.5
            mesh_voltage = rho * I_fault * Km / L_total

            Ks = 1 / math.pi * (1/(2*h) + 1/(D + h) + 1/D)
            step_voltage = rho * I_fault * Ks / L_total

            Cs = 1.0
            ρs = 3000
            E_touch_50 = (1000 + 1.5 * Cs * ρs) / math.sqrt(t_fault)
            E_step_50 = (1000 + 6 * Cs * ρs) / math.sqrt(t_fault)

            touch_safety = E_touch_50 / mesh_voltage if mesh_voltage > 0 else float('inf')
            step_safety = E_step_50 / step_voltage if step_voltage > 0 else float('inf')
            overall_safety = min(touch_safety, step_safety)

            self.grid_resistance.set(f"{R_grid:.3f}")
            self.step_voltage.set(f"{step_voltage:.1f} (limit: {E_step_50:.1f})")
            self.touch_voltage.set(f"{mesh_voltage:.1f} (limit: {E_touch_50:.1f})")
            self.safety_factor.set(f"{overall_safety:.2f}")
            self.apparent_rho.set(f"{rho:.1f}")

            project_info = f"Project: {self.project_name.get()} | Date: {self.project_date.get()} | Rev: {self.project_rev.get()}"
            messagebox.showinfo("IEEE 80 Compliance",
                                f"{project_info}\n\n"
                                f"Grid Resistance: {R_grid:.3f} Ω\n"
                                f"Safety factor: {overall_safety:.2f}")
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))

    def remove_previous_colorbar(self):
        if self._colorbar:
            self._colorbar.remove()
            self._colorbar = None

    def create_grounding_grid(self):
        L = self.grid_length.get()
        W = self.grid_width.get()
        spacing = self.conductor_spacing.get()
        depth = -self.burial_depth.get()

        rod_depth = self.rod_depth.get()
        n_long_rods = max(1, self.num_rods_length.get())
        n_wide_rods = max(1, self.num_rods_width.get())

        long_cond = []
        for i in range(int(W/spacing)+1):
            y = i * spacing - W/2
            long_cond.append(([-L/2, L/2], [y, y], [depth, depth]))

        trans_cond = []
        for i in range(int(L/spacing)+1):
            x = i * spacing - L/2
            trans_cond.append(([x, x], [-W/2, W/2], [depth, depth]))

        ground_rods = []
        rod_tips_x, rod_tips_y, rod_tips_z = [], [], []

        x_positions = np.linspace(-L/2, L/2, n_long_rods)
        y_positions = np.linspace(-W/2, W/2, n_wide_rods)

        for x in x_positions:
            for y in y_positions:
                ground_rods.append(([x, x], [y, y], [depth, depth - rod_depth]))
                rod_tips_x.append(x)
                rod_tips_y.append(y)
                rod_tips_z.append(depth)

        return long_cond, trans_cond, ground_rods, rod_tips_x, rod_tips_y, rod_tips_z

    def update_plot(self):
        self.remove_previous_colorbar()
        self.ax.clear()

        long_cond, trans_cond, ground_rods, rod_tips_x, rod_tips_y, rod_tips_z = self.create_grounding_grid()

        for x, y, z in long_cond:
            self.ax.plot(x, y, z, 'b-', linewidth=2)
        for x, y, z in trans_cond:
            self.ax.plot(x, y, z, 'r-', linewidth=2)
        for x, y, z in ground_rods:
            self.ax.plot(x, y, z, 'g-', linewidth=4)

        self.ax.scatter(rod_tips_x, rod_tips_y, rod_tips_z, color='k', s=50, label='Rod Tops')

        L = self.grid_length.get()
        W = self.grid_width.get()
        xx, yy = np.meshgrid(np.linspace(-L/2, L/2, 10), np.linspace(-W/2, W/2, 10))
        zz = np.zeros_like(xx)
        self.ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')

        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_zlabel("Z (m)")
        self.ax.set_title("Grounding Grid Geometry")
        self.ax.legend()
        self.canvas.draw()

    def calculate_surface_potential(self, x, y):
        rho = self.calculate_apparent_resistivity()
        I_fault = self.fault_current.get()
        R_grid = float(self.grid_resistance.get())
        GPR = I_fault * R_grid
        spacing = self.conductor_spacing.get()
        dist = np.sqrt(x ** 2 + y ** 2)
        V_surface = GPR * math.exp(-dist / (spacing * 2))
        return V_surface

    def show_voltage_distribution(self):
        self.remove_previous_colorbar()
        self.ax.clear()

        L = self.grid_length.get()
        W = self.grid_width.get()
        x_range = np.linspace(-L/2, L/2, 30)
        y_range = np.linspace(-W/2, W/2, 30)
        X, Y = np.meshgrid(x_range, y_range)
        Z = np.vectorize(self.calculate_surface_potential)(X, Y)

        self.surface_X, self.surface_Y, self.surface_Z = X, Y, Z

        surf = self.ax.plot_surface(X, Y, Z, cmap='plasma')
        self.ax.set_title("Surface Voltage Distribution")

        self._colorbar = self.fig.colorbar(surf, ax=self.ax, shrink=0.5, aspect=10, pad=0.1,
                                           label='Surface Voltage (V)')
        self.canvas.draw()

    def show_step_potentials(self):
        if not self.grid_resistance.get() or float(self.grid_resistance.get()) == 0.0:
            messagebox.showerror("Missing Calculation", "Please calculate the grid analysis first.")
            return

        self.remove_previous_colorbar()
        self.ax.clear()

        L = self.grid_length.get()
        W = self.grid_width.get()
        step_size = 1.0
        x_range = np.arange(-L/2, L/2, step_size)
        y_range = np.arange(-W/2, W/2, step_size)
        X, Y = np.meshgrid(x_range, y_range)

        V1 = np.vectorize(self.calculate_surface_potential)(X, Y)
        V2 = np.vectorize(self.calculate_surface_potential)(X + step_size, Y)
        step_pot = np.abs(V2 - V1)

        self.step_X, self.step_Y, self.step_Z = X, Y, step_pot

        long_cond, trans_cond, ground_rods, rod_tips_x, rod_tips_y, rod_tips_z = self.create_grounding_grid()
        for x, y, z in long_cond:
            self.ax.plot(x, y, z, 'b-', linewidth=2)
        for x, y, z in trans_cond:
            self.ax.plot(x, y, z, 'r-', linewidth=2)
        for x, y, z in ground_rods:
            self.ax.plot(x, y, z, 'g-', linewidth=4)
        self.ax.scatter(rod_tips_x, rod_tips_y, rod_tips_z, color='k', s=50)

        surf = self.ax.plot_surface(X, Y, step_pot, cmap='viridis', alpha=0.7)
        self.ax.set_title("Step Potential Distribution")

        self.ax.set_xlim(-L/2, L/2)
        self.ax.set_ylim(-W/2, W/2)
        self.ax.set_zlim(0, np.max(step_pot)*1.2 if np.max(step_pot)>0 else 1)

        self._colorbar = self.fig.colorbar(surf, ax=self.ax, shrink=0.5, aspect=10, pad=0.1,
                                           label='Step Voltage (V)')
        self.canvas.draw()

    def show_touch_potentials(self):
        if not self.grid_resistance.get() or float(self.grid_resistance.get()) == 0.0:
            messagebox.showerror("Missing Calculation", "Please calculate the grid analysis first.")
            return

        self.remove_previous_colorbar()
        self.ax.clear()

        L = self.grid_length.get()
        W = self.grid_width.get()
        x_points = np.linspace(-L/2, L/2, 20)
        y_points = np.linspace(-W/2, W/2, 20)
        X, Y = np.meshgrid(x_points, y_points)
        Z = np.vectorize(self.calculate_surface_potential)(X, Y)
        touch_voltage = Z * 0.9

        self.touch_X, self.touch_Y, self.touch_Z = X, Y, touch_voltage

        long_cond, trans_cond, ground_rods, rod_tips_x, rod_tips_y, rod_tips_z = self.create_grounding_grid()
        for x, y, z in long_cond:
            self.ax.plot(x, y, z, 'b-', linewidth=2)
        for x, y, z in trans_cond:
            self.ax.plot(x, y, z, 'r-', linewidth=2)
        for x, y, z in ground_rods:
            self.ax.plot(x, y, z, 'g-', linewidth=4)
        self.ax.scatter(rod_tips_x, rod_tips_y, rod_tips_z, color='k', s=50)

        surf = self.ax.plot_surface(X, Y, touch_voltage, cmap='inferno', alpha=0.7)
        self.ax.set_title("Touch Potential Distribution")

        self.ax.set_xlim(-L/2, L/2)
        self.ax.set_ylim(-W/2, W/2)
        self.ax.set_zlim(0, np.max(touch_voltage)*1.2 if np.max(touch_voltage)>0 else 1)

        self._colorbar = self.fig.colorbar(surf, ax=self.ax, shrink=0.5, aspect=10, pad=0.1,
                                           label='Touch Voltage (V)')
        self.canvas.draw()

    def create_initial_plot(self):
        self.update_plot()

def main():
    root = tk.Tk()
    app = IEEE80GroundingGrid(root)
    root.mainloop()

if __name__ == "__main__":
    main()

