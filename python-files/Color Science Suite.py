import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import colour

matplotlib.use('TkAgg')

class ColorSuiteApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Color Science Suite")
        self.master.geometry("1100x850") # Increased size slightly for new widgets

        self.spectral_results = []
        self.spectral_filepath = tk.StringVar()
        self.cmf_choice = tk.StringVar()
        
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.plotter_tab = ttk.Frame(self.notebook, padding="10")
        self.calculator_tab = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.plotter_tab, text='Chromaticity Plotter')
        self.notebook.add(self.calculator_tab, text='Spectral Calculator')

        self.create_plotter_tab_widgets()
        self.create_calculator_tab_widgets()

        self.plot_data()

    # ===================================================================
    # TAB 1: CHROMATICITY PLOTTER (No changes in this section)
    # ===================================================================
    
    def create_plotter_tab_widgets(self):
        # ... (This entire function is unchanged from the previous version) ...
        self.diagram_choice = tk.StringVar(value="CIE 1931")
        control_panel = ttk.Frame(self.plotter_tab, padding="10", relief="solid", borderwidth=1)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ttk.Label(control_panel, text="1. Select Diagram", font=("Helvetica", 12, "bold")).pack(pady=5, anchor="w")
        ttk.Radiobutton(control_panel, text="CIE 1931 (xy)", variable=self.diagram_choice, value="CIE 1931", command=self.plot_data).pack(anchor="w", padx=10)
        ttk.Radiobutton(control_panel, text="CIE 1960 UCS (uv)", variable=self.diagram_choice, value="CIE 1960 UCS", command=self.plot_data).pack(anchor="w", padx=10)
        ttk.Label(control_panel, text="2. Enter CIE 1931 (xy) Values", font=("Helvetica", 12, "bold")).pack(pady=(20, 5), anchor="w")
        ttk.Label(control_panel, text="(x, y, optional_label per line)").pack(pady=2, anchor="w")
        self.text_input = tk.Text(control_panel, height=15, width=40, font=("Courier", 10))
        self.text_input.pack(pady=5, fill=tk.BOTH, expand=True)
        self.text_input.insert(tk.END, "# Data from the Spectral Calculator can be sent here.\n0.3135, 0.3290, D65")
        ttk.Label(control_panel, text="3. Actions", font=("Helvetica", 12, "bold")).pack(pady=(20, 5), anchor="w")
        ttk.Button(control_panel, text="Plot Points", command=self.plot_data).pack(pady=5, fill=tk.X)
        self.save_button = ttk.Button(control_panel, text="Save Plot...", command=self.save_plot, state='disabled')
        self.save_button.pack(pady=5, fill=tk.X)
        plot_frame = ttk.Frame(self.plotter_tab)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.figure = Figure(figsize=(7, 7), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def parse_plotter_input(self):
        # ... (This entire function is unchanged from the previous version) ...
        text_content = self.text_input.get("1.0", tk.END)
        lines = text_content.strip().split('\n')
        points, labels = [], []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.replace(',', ' ').split()
            if len(parts) < 2:
                messagebox.showerror("Input Error", f"Invalid format on line {i+1}: '{line}'.")
                return None, None
            try:
                points.append((float(parts[0]), float(parts[1])))
                labels.append(' '.join(parts[2:]) if len(parts) > 2 else None)
            except ValueError:
                messagebox.showerror("Input Error", f"Non-numeric coordinate on line {i+1}: '{line}'.")
                return None, None
        return np.array(points), labels

    def plot_data(self):
        # ... (This entire function is unchanged from the previous version) ...
        self.axes.clear()
        xy_data, labels = self.parse_plotter_input()
        if xy_data is None:
            self.save_button['state'] = 'disabled'
            return
        scatter_kwargs = {'s': 80, 'c': 'black', 'marker': 'x', 'label': 'User Data'}
        try:
            plot_coords = None
            if self.diagram_choice.get() == "CIE 1931":
                plot_coords = xy_data
                colour.plotting.plot_chromaticity_diagram_CIE1931(figure=self.figure, axes=self.axes, standalone=False, title="CIE 1931 Chromaticity Diagram (xy)")
            elif self.diagram_choice.get() == "CIE 1960 UCS":
                if xy_data.size > 0:
                    plot_coords = colour.xy_to_UCS_uv(xy_data)
                else:
                    plot_coords = np.array([])
                colour.plotting.plot_chromaticity_diagram_CIE1960UCS(figure=self.figure, axes=self.axes, standalone=False, title="CIE 1960 UCS Chromaticity Diagram (uv)")
            if plot_coords is not None and plot_coords.size > 0:
                self.axes.scatter(plot_coords[:, 0], plot_coords[:, 1], **scatter_kwargs)
                for i, label in enumerate(labels):
                    if label:
                        self.axes.text(plot_coords[i, 0] + 0.005, plot_coords[i, 1] + 0.005, label, fontsize=9, color='darkslategray')
                self.axes.legend()
            self.canvas.draw()
            self.save_button['state'] = 'normal'
        except Exception as e:
            messagebox.showerror("Plotting Error", f"An error occurred: {e}")
            self.save_button['state'] = 'disabled'

    def save_plot(self):
        # ... (This entire function is unchanged from the previous version) ...
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf"), ("All Files", "*.*")], title="Save Plot As")
        if file_path:
            try:
                self.figure.savefig(file_path, bbox_inches='tight', dpi=300)
                messagebox.showinfo("Success", f"Plot saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save plot: {e}")

    # ===================================================================
    # TAB 2: SPECTRAL CALCULATOR (This section is heavily modified)
    # ===================================================================

    def create_calculator_tab_widgets(self):
        # --- Top Frame for Controls ---
        top_controls_frame = ttk.Frame(self.calculator_tab)
        top_controls_frame.pack(fill=tk.X, pady=5)
        
        file_frame = ttk.Frame(top_controls_frame)
        file_frame.pack(fill=tk.X, pady=5)
        # --- MODIFIED --- Renamed button
        ttk.Button(file_frame, text="Load / Re-Calculate", command=self.load_and_calculate_spectral_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        ttk.Label(file_frame, textvariable=self.spectral_filepath, foreground="blue").pack(side=tk.LEFT)

        # --- MODIFIED --- Frame to hold parameter selection widgets side-by-side
        params_frame = ttk.LabelFrame(top_controls_frame, text="Calculation Parameters", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # --- Observer (CMFs) Selection ---
        cmf_frame = ttk.LabelFrame(params_frame, text="Observer", padding=5)
        cmf_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        cmf_names = sorted(list(colour.MSDS_CMFS.keys()))
        self.cmf_combobox = ttk.Combobox(cmf_frame, textvariable=self.cmf_choice, values=cmf_names, state='readonly', width=35)
        self.cmf_combobox.pack()
        default_cmf = 'CIE 1964 10 Degree Standard Observer'
        self.cmf_choice.set(default_cmf if default_cmf in cmf_names else cmf_names[0])

        # --- NEW --- Illuminant Multi-Selection Listbox ---
        illuminant_frame = ttk.LabelFrame(params_frame, text="Illuminants", padding=5)
        illuminant_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(illuminant_frame, text="(Ctrl/Shift to select multiple)").pack(anchor='w')
        
        listbox_frame = ttk.Frame(illuminant_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.illuminant_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=self.illuminant_listbox.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.illuminant_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate the listbox
        self.illuminant_names = sorted(list(colour.SDS_ILLUMINANTS.keys()))
        for name in self.illuminant_names:
            self.illuminant_listbox.insert(tk.END, name)
            
        # Set default selections
        for default_item in ['D65', 'FL2']:
            if default_item in self.illuminant_names:
                idx = self.illuminant_names.index(default_item)
                self.illuminant_listbox.selection_set(idx)

        # --- Results Treeview and Action Buttons (Unchanged) ---
        results_frame = ttk.Frame(self.calculator_tab)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        cols = ('Sample', 'Illuminant', 'X', 'Y', 'Z', 'x', 'y')
        self.results_tree = ttk.Treeview(results_frame, columns=cols, show='headings')
        for col in cols:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor='center')
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        actions_frame = ttk.Frame(self.calculator_tab)
        actions_frame.pack(fill=tk.X, pady=5)
        self.export_button = ttk.Button(actions_frame, text="Export Results to CSV...", command=self.export_results, state='disabled')
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        self.send_to_plotter_button = ttk.Button(actions_frame, text="Send to Plotter Tab", command=self.send_to_plotter, state='disabled')
        self.send_to_plotter_button.pack(side=tk.LEFT)

    def load_and_calculate_spectral_data(self):
        file_path = self.spectral_filepath.get()
        # If no file is loaded yet, open the dialog
        if not file_path:
             file_path = filedialog.askopenfilename(title="Select Spectral Data CSV", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
             if not file_path: return
        
        try:
            df = pd.read_csv(file_path)
            if df.shape[1] < 2: # Need at least Wavelength and one data column
                raise ValueError("CSV must have at least 2 columns")
            
            self.spectral_filepath.set(file_path)
            
            # --- Get CMFs from dropdown ---
            selected_cmf_name = self.cmf_choice.get()
            if not selected_cmf_name:
                messagebox.showerror("Parameter Error", "Please select an Observer (CMFs).")
                return
            cmfs = colour.MSDS_CMFS[selected_cmf_name]
            
            # --- NEW --- Get selected illuminants from the listbox
            selected_indices = self.illuminant_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Parameter Error", "Please select at least one illuminant.")
                return
            
            selected_illuminant_names = [self.illuminant_names[i] for i in selected_indices]
            
            illuminants_to_calculate = {
                name: colour.SDS_ILLUMINANTS[name] for name in selected_illuminant_names
            }

            # --- Data Processing Logic (largely unchanged) ---
            wavelengths = df.iloc[:, 0].values
            if df.columns[1].lower().strip() in ['dark', 'dark_ref', 'dark ref']:
                if df.shape[1] < 3: raise ValueError("CSV with Dark Ref needs at least 3 columns")
                dark_ref, white_ref, start_idx = df.iloc[:, 1].values, df.iloc[:, 2].values, 3
            else:
                dark_ref, white_ref, start_idx = np.zeros_like(wavelengths), df.iloc[:, 1].values, 2
            
            corrected_white = white_ref - dark_ref
            
            self.spectral_results.clear()
            for i in range(start_idx, df.shape[1]):
                sample_name = df.columns[i]
                raw_sample = df.iloc[:, i].values
                
                corrected_sample = raw_sample - dark_ref
                with np.errstate(divide='ignore', invalid='ignore'):
                    reflectance = corrected_sample / corrected_white
                reflectance = np.nan_to_num(reflectance)
                reflectance = np.clip(reflectance, 0, 1)
                sd_sample = colour.SpectralDistribution(reflectance, wavelengths, name=sample_name)
                
                for name, illuminant_sd in illuminants_to_calculate.items():
                    XYZ = colour.sd_to_XYZ(sd_sample, cmfs, illuminant_sd)
                    xy = colour.XYZ_to_xy(XYZ)
                    
                    self.spectral_results.append({
                        'Sample': sample_name, 'Illuminant': name,
                        'X': f"{XYZ[0]:.4f}", 'Y': f"{XYZ[1]:.4f}", 'Z': f"{XYZ[2]:.4f}",
                        'x': f"{xy[0]:.4f}", 'y': f"{xy[1]:.4f}"
                    })
            
            self.update_results_treeview()
            self.export_button['state'] = 'normal'
            self.send_to_plotter_button['state'] = 'normal'

        except Exception as e:
            messagebox.showerror("File/Calculation Error", f"An error occurred: {e}")
            self.export_button['state'] = 'disabled'
            self.send_to_plotter_button['state'] = 'disabled'

    def update_results_treeview(self):
        # ... (This entire function is unchanged from the previous version) ...
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for res in self.spectral_results:
            self.results_tree.insert('', tk.END, values=list(res.values()))

    def export_results(self):
        # ... (This entire function is unchanged from the previous version) ...
        if not self.spectral_results:
            messagebox.showwarning("No Data", "There is no data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")], title="Export Results As")
        if file_path:
            try:
                pd.DataFrame(self.spectral_results).to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def send_to_plotter(self):
        # ... (This entire function is unchanged from the previous version) ...
        if not self.spectral_results:
            messagebox.showwarning("No Data", "There is no data to send to the plotter.")
            return
        plotter_text = f"# Data from Spectral Calculator\n# Observer: {self.cmf_choice.get()}\n"
        for res in self.spectral_results:
            label = f"{res['Sample']} ({res['Illuminant']})"
            plotter_text += f"{res['x']}, {res['y']}, {label}\n"
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", plotter_text)
        self.notebook.select(self.plotter_tab)
        self.plot_data()
        messagebox.showinfo("Success", "Data sent to the plotter tab.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorSuiteApp(root)
    root.mainloop()