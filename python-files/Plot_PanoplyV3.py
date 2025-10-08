import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os


class NetCDFPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetCDF Plotter")

        self.dataset = None
        self.plot_configs = []
        self.previous_vars = set()
        self.fig = None
        self.canvas = None
        self.file_path = None

        self.setup_layout()

    def setup_layout(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # --- Panel de controles (izquierda) ---
        self.control_frame = tk.Frame(self.main_frame, width=250, bg="lightgray")
        self.control_frame.pack(side='left', fill='y', padx=10, pady=10)

        # --- Panel de ploteo (derecha) ---
        self.plot_frame = tk.Frame(self.main_frame, bg="white")
        self.plot_frame.pack(side='right', fill='both', expand=True)

        # Texto inicial en el área de ploteo
        tk.Label(self.plot_frame, fg="gray", bg="white").pack()

        # --- Fila 1: Load y nombre de archivo ---
        row1 = tk.Frame(self.control_frame, bg="lightgray")
        row1.pack(fill='x', pady=5)

        self.browse_button = tk.Button(row1, text="Load .nc File", command=self.load_dataset)
        self.browse_button.pack(side='left', padx=5)

        self.file_label = tk.Label(row1, text="No file loaded", width=25, anchor='w', bg="lightgray")
        self.file_label.pack(side='left', padx=5)

        # --- Fila 2: Rows / Columns ---
        row2 = tk.Frame(self.control_frame, bg="lightgray")
        row2.pack(fill='x', pady=5)

        tk.Label(row2, text="Rows", bg="lightgray").pack(side='left')
        self.rows_var = tk.IntVar(value=1)
        tk.Entry(row2, textvariable=self.rows_var, width=5).pack(side='left', padx=5)

        tk.Label(row2, text="Columns", bg="lightgray").pack(side='left')
        self.cols_var = tk.IntVar(value=1)
        tk.Entry(row2, textvariable=self.cols_var, width=5).pack(side='left', padx=5)

        # --- Fila 3: Figure description ---
        row3 = tk.Frame(self.control_frame, bg="lightgray")
        row3.pack(fill='x', pady=5)

        tk.Label(row3, text="Figure description", bg="lightgray").pack(anchor='w')
        self.title_textbox = tk.Text(row3, width=25, height=4, wrap='word')
        self.title_textbox.pack(fill='x')

        # --- Fila 4: Botones centrados ---
        row4 = tk.Frame(self.control_frame, bg="lightgray")
        row4.pack(pady=10)

        self.setup_button = tk.Button(row4, text="Plot Setup", command=self.setup_plot_configs)
        self.setup_button.pack(side='left', padx=10)

        self.plot_button = tk.Button(row4, text="Plot", command=self.plot_all)
        self.plot_button.pack(side='left', padx=10)

        self.save_button = tk.Button(row4, text="Save Plot", command=self.save_plot)
        self.save_button.pack(side='left', padx=10)

        # --- Fila 5: Frame dinámico para configuraciones ---
        self.config_frame = tk.Frame(self.control_frame, bg="lightgray")
        self.config_frame.pack(fill='x', pady=5)

    def shorten_filename(self, path, maxlen=8):
        base = os.path.basename(path)
        if len(base) > maxlen:
            return base[:maxlen] + "..."
        return base

    def load_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("NetCDF files", "*.nc")])
        if not file_path:
            return

        self.dataset = xr.open_dataset(file_path)
        self.file_path = file_path

        short_name = self.shorten_filename(file_path, maxlen=20)
        self.file_label.config(text=short_name)

        self.convert_units()

        current_vars = set([var for var in self.dataset.data_vars
                            if any(self.dataset.sizes[dim] > 1 for dim in self.dataset[var].dims)])

        if current_vars != self.previous_vars:
            self.plot_configs.clear()
            for widget in self.config_frame.winfo_children():
                widget.destroy()
        self.previous_vars = current_vars

    def convert_units(self):
        # Convert certain variables' units if present (keeps original in attrs)
        def convert_var(var_name, factor, new_units):
            var_keys = [v for v in self.dataset.variables if v.lower() == var_name.lower()]
            if not var_keys:
                return
            var_key = var_keys[0]
            orig_units = self.dataset[var_key].attrs.get('units', None)
            self.dataset[var_key] = self.dataset[var_key] * factor
            self.dataset[var_key].attrs['units'] = new_units
            if orig_units and orig_units != new_units:
                self.dataset[var_key].attrs['original_units'] = orig_units

        def convert_vars_by_prefix(prefix, factor, new_units):
            for var_name in list(self.dataset.variables):
                if var_name.lower().startswith(prefix.lower()):
                    orig_units = self.dataset[var_name].attrs.get('units', None)
                    self.dataset[var_name] = self.dataset[var_name] * factor
                    self.dataset[var_name].attrs['units'] = new_units
                    if orig_units and orig_units != new_units:
                        self.dataset[var_name].attrs['original_units'] = orig_units

        convert_var('frequency', 1e-9, 'GHz')
        convert_vars_by_prefix('voltage', 1e6, 'uV')

    def setup_plot_configs(self):
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.plot_configs.clear()

        rows = self.rows_var.get()
        cols = self.cols_var.get()

        for r in range(rows):
            row_frame = tk.Frame(self.config_frame)
            row_frame.pack()
            for c in range(cols):
                idx = r * cols + c
                self.add_plot_config(row_frame, idx)

    def add_plot_config(self, parent, idx):
        frame = tk.LabelFrame(parent, text=f"Plot {idx + 1}")
        frame.pack(side='left', padx=5, pady=5)

        z_var = tk.StringVar()
        x_var = tk.StringVar()
        y_var = tk.StringVar()
        is_slice_plot = tk.BooleanVar(value=False)

        # Valid variables: data_vars with at least one dimension > 1
        if self.dataset is None:
            vars_valid = []
        else:
            vars_valid = [var for var in self.dataset.data_vars
                          if any(self.dataset.sizes[dim] > 1 for dim in self.dataset[var].dims)]

        ttk.Label(frame, text="Z Axis").pack()
        z_menu = ttk.Combobox(frame, textvariable=z_var, values=vars_valid, state="readonly")
        z_menu.pack()
        z_menu.bind('<<ComboboxSelected>>', lambda e, i=idx: self.update_axis_options(i))

        ttk.Label(frame, text="X Axis").pack()
        x_menu = ttk.Combobox(frame, textvariable=x_var, state="readonly")
        x_menu.pack()

        ttk.Label(frame, text="Y Axis (slice variable)").pack()
        y_menu = ttk.Combobox(frame, textvariable=y_var, state="readonly")
        y_menu.pack()

        chk = ttk.Checkbutton(frame, text="Line plot slices", variable=is_slice_plot)
        chk.pack(pady=5)

        # Save as TXT button
        save_txt_btn = tk.Button(frame, text="Save as TXT", command=lambda i=idx: self.save_plot_data_as_txt(i))
        save_txt_btn.pack(pady=5)

        fixed_dims = {}

        extra_dims_frame = tk.Frame(frame)
        extra_dims_frame.pack()

        self.plot_configs.append({
            'z_var': z_var,
            'x_var': x_var,
            'y_var': y_var,
            'x_menu': x_menu,
            'y_menu': y_menu,
            'is_slice_plot': is_slice_plot,
            'fixed_dims': fixed_dims,
            'extra_dims_frame': extra_dims_frame,
            # 'plotted_data' will be set when plotting
            'plotted_data': None
        })

    def update_axis_options(self, idx):
        cfg = self.plot_configs[idx]
        z_val = cfg['z_var'].get()

        if not z_val or self.dataset is None:
            cfg['x_menu']['values'] = []
            cfg['y_menu']['values'] = []
            cfg['x_var'].set('')
            cfg['y_var'].set('')
            return

        z_var = self.dataset[z_val]
        valid_dims = list(z_var.dims)
        # Keep only dims with size > 1
        valid_dims = [dim for dim in valid_dims if self.dataset.sizes.get(dim, 0) > 1]

        current_x = cfg['x_var'].get()
        current_y = cfg['y_var'].get()

        x_options = valid_dims[:]
        y_options = [dim for dim in valid_dims if dim != current_x]

        if current_x not in x_options:
            current_x = x_options[0] if x_options else ''
        if current_y not in y_options or current_y == current_x:
            y_candidates = [d for d in y_options if d != current_x]
            current_y = y_candidates[0] if y_candidates else ''

        cfg['x_var'].set(current_x)
        cfg['y_var'].set(current_y)

        cfg['x_menu']['values'] = x_options
        cfg['y_menu']['values'] = y_options

        cfg['x_menu'].config(state='readonly' if x_options else 'disabled')
        cfg['y_menu'].config(state='readonly' if y_options else 'disabled')

        # Reassign binds so changing X will update Y options and selectors
        cfg['x_menu'].bind('<<ComboboxSelected>>', lambda e, i=idx: self.update_axis_options(i))
        cfg['y_menu'].bind('<<ComboboxSelected>>', lambda e, i=idx: self.update_axis_options(i))

        # Update extra (fixed) dim selectors
        self.update_fixed_dim_selectors(idx)

    def update_fixed_dim_selectors(self, idx):
        cfg = self.plot_configs[idx]
        zname = cfg['z_var'].get()
        xname = cfg['x_var'].get()
        yname = cfg['y_var'].get()
        extra_frame = cfg['extra_dims_frame']

        # Clear previous widgets
        for widget in extra_frame.winfo_children():
            widget.destroy()
        cfg['fixed_dims'].clear()

        if not zname:
            return

        z = self.dataset[zname]
        dims_used = {xname, yname}
        extra_dims = [dim for dim in z.dims if dim not in dims_used]

        for dim in extra_dims:
            values = self.dataset[dim].values
            if len(values) <= 1:
                continue

            pretty_name = dim
            units = self.dataset[dim].attrs.get('units')
            if units:
                pretty_name += f" ({units})"
            dim_label = tk.Label(extra_frame, text=pretty_name + ":")
            dim_label.pack(anchor='w')

            # If the dimension is the chosen "slice variable" show a multi-select listbox
            if dim == yname:
                label = tk.Label(extra_frame, text=f"{dim} (slice values):")
                label.pack(anchor='w')
                listbox = tk.Listbox(extra_frame, selectmode='multiple', exportselection=False, height=6)
                for val in values:
                    listbox.insert(tk.END, str(val))
                listbox.pack(fill='x')

                def make_listbox_callback(d=dim, lb=listbox):
                    def callback(*_):
                        selected = [lb.get(i) for i in lb.curselection()]
                        cfg['fixed_dims'][d] = selected
                    return callback

                listbox.bind("<<ListboxSelect>>", make_listbox_callback())
                # default: select the first value
                cfg['fixed_dims'][dim] = [str(values[0])]
            else:
                var = tk.StringVar(value=str(values[0]))
                dropdown = ttk.Combobox(extra_frame, textvariable=var, values=[str(v) for v in values],
                                        state="readonly")
                dropdown.pack(fill='x')

                def make_callback(d=dim, v=var):
                    return lambda *_: cfg['fixed_dims'].update({d: v.get()})
                dropdown.bind("<<ComboboxSelected>>", make_callback())
                cfg['fixed_dims'][dim] = var

    def plot_all(self):
        if self.dataset is None:
            return

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        rows = self.rows_var.get()
        cols = self.cols_var.get()

        self.fig, self.axs = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
        # Ensure axs is always 2D array-like
        if rows * cols == 1:
            self.axs = np.array([[self.axs]])
        else:
            self.axs = np.array(self.axs).reshape(rows, cols)

        for idx, cfg in enumerate(self.plot_configs):
            if idx >= rows * cols:
                break

            # reset stored plotted data for this plot
            cfg['plotted_data'] = None

            row, col = divmod(idx, cols)
            ax = self.axs[row, col]

            zname = cfg['z_var'].get()
            xname = cfg['x_var'].get()
            yname = cfg['y_var'].get()
            use_slices = cfg['is_slice_plot'].get()

            if not zname or not xname:
                ax.set_title("Missing axis selection")
                ax.axis('off')
                continue

            try:
                z = self.dataset[zname]

                # Apply fixed values to dimensions not used as X or Y
                extra_dims = [dim for dim in z.dims if dim not in [xname, yname]]
                for dim, val in cfg.get('fixed_dims', {}).items():
                    # convert selection to python values
                    if isinstance(val, list):
                        cleaned_vals = []
                        for v in val:
                            if isinstance(v, str):
                                cleaned_vals.append(v)
                            elif isinstance(v, tk.StringVar):
                                cleaned_vals.append(v.get())
                            else:
                                cleaned_vals.append(v)
                        selected_val = cleaned_vals[0]
                    else:
                        selected_val = val.get() if isinstance(val, tk.StringVar) else val

                    coord_vals = self.dataset[dim].values
                    # try to convert to numeric type that matches coords if possible
                    try:
                        val_num = type(coord_vals[0])(selected_val)
                        z = z.sel({dim: val_num}, method='nearest')
                    except Exception:
                        z = z.sel({dim: selected_val}, method='nearest')

                z = z.squeeze()

                # Units and labels
                z_units = z.attrs.get('units', '')
                x_units = self.dataset[xname].attrs.get('units', '') if xname in self.dataset else ''
                y_units = self.dataset[yname].attrs.get('units', '') if yname in self.dataset else ''

                xlabel = f"{xname} ({x_units})" if x_units else xname
                ylabel = f"{yname} ({y_units})" if y_units else yname
                zlabel = f"{zname} ({z_units})" if z_units else zname

                # Determine x values robustly
                if xname in self.dataset:
                    x_vals = self.dataset[xname].values
                elif xname in z.coords:
                    x_vals = z.coords[xname].values
                elif len(z.dims) == 1:
                    x_vals = self.dataset[z.dims[0]].values if z.dims[0] in self.dataset else np.arange(z.size)
                else:
                    x_vals = np.arange(z.size)

                # Simple line plot (1D)
                if not yname or yname == '' or yname == xname:
                    # plot with x coordinate if possible
                    if xname in z.dims:
                        z.plot(ax=ax, x=xname)
                    else:
                        z.plot(ax=ax)

                    ax.set_xlabel(xlabel)
                    # show z variable on y-axis
                    ax.set_ylabel(zlabel)

                    # store plotted data for saving
                    y_vals = z.values
                    # ensure 1D array
                    y_arr = np.array(y_vals).ravel()
                    # align lengths if necessary
                    if y_arr.shape != x_vals.shape:
                        try:
                            y_arr = np.broadcast_to(y_arr, x_vals.shape)
                        except Exception:
                            # fallback resize
                            y_arr = np.resize(y_arr, x_vals.shape)

                    cfg['plotted_data'] = {
                        'type': 'line',
                        'x_name': xname,
                        'x_units': x_units,
                        'x': np.array(x_vals),
                        'y': [np.array(y_arr)],
                        'labels': [zname]
                    }

                else:
                    # 2D case (either slices or 2D map)
                    if xname not in z.dims or yname not in z.dims:
                        ax.set_title(f"Axes '{xname}', '{yname}' not in dims")
                        ax.axis('off')
                        continue

                    if use_slices:
                        # If user selected specific slice values in fixed_dims[yname], prefer them
                        selected_list = cfg.get('fixed_dims', {}).get(yname, None)
                        if isinstance(selected_list, list) and len(selected_list) > 0:
                            # convert strings to appropriate types if possible matching dataset dtype
                            raw_vals = []
                            coord_vals = self.dataset[yname].values
                            for s in selected_list:
                                try:
                                    raw_vals.append(type(coord_vals[0])(s))
                                except Exception:
                                    raw_vals.append(s)
                            slice_vals = raw_vals
                        else:
                            slice_vals = self.dataset[yname].values

                        y_slices = []
                        labels = []
                        handles = []
                        for i, sval in enumerate(slice_vals):
                            try:
                                data_slice = z.sel({yname: sval}, method='nearest')
                            except Exception:
                                # try with original string
                                data_slice = z.sel({yname: str(sval)}, method='nearest')

                            # squeeze everything except x and slice dim
                            dims_to_keep = {xname, yname}
                            dims_to_squeeze = [dim for dim in data_slice.dims if dim not in dims_to_keep]
                            if dims_to_squeeze:
                                try:
                                    data_slice = data_slice.squeeze(dim=dims_to_squeeze)
                                except Exception:
                                    data_slice = data_slice.squeeze()

                            # Ensure y array compatible with x_vals
                            y_arr = np.array(data_slice.values)
                            if y_arr.shape != np.array(x_vals).shape:
                                try:
                                    y_arr = np.broadcast_to(y_arr, np.array(x_vals).shape)
                                except Exception:
                                    if y_arr.size == np.array(x_vals).size:
                                        y_arr = y_arr.ravel()
                                    elif y_arr.size == 1:
                                        y_arr = np.full_like(np.array(x_vals), y_arr.item(), dtype=float)
                                    else:
                                        y_arr = np.resize(y_arr, np.array(x_vals).shape)

                            line, = ax.plot(x_vals, y_arr)
                            # label only for legend (we can limit how many labels appear if many slices)
                            labels.append(str(sval))
                            y_slices.append(np.array(y_arr))
                            handles.append(line)

                        ax.set_xlabel(xlabel)
                        ax.set_ylabel(zlabel)

                        # Build a legend with a limited number of entries if many slices
                        total = len(slice_vals)
                        max_legend = 15
                        if total <= max_legend:
                            selected_indices = list(range(total))
                        else:
                            selected_indices = list(np.linspace(0, total - 1, num=max_legend, dtype=int))

                        # Set legend only for selected indices
                        legend_handles = [handles[i] for i in selected_indices]
                        legend_labels = [labels[i] for i in selected_indices]
                        leg = ax.legend(legend_handles, legend_labels, loc='center left', bbox_to_anchor=(1.05, 0.5),
                                        borderaxespad=0.)
                        if leg is not None:
                            leg.set_title(yname)

                        # store plotted data
                        cfg['plotted_data'] = {
                            'type': 'slices',
                            'x_name': xname,
                            'x_units': x_units,
                            'x': np.array(x_vals),
                            'y': [np.array(arr) for arr in y_slices],
                            'labels': labels
                        }

                    else:
                        # 2D map plot (cannot be saved as TXT)
                        z.plot(ax=ax, x=xname, y=yname, cmap='viridis')
                        ax.set_xlabel(xlabel)
                        ax.set_ylabel(ylabel)
                        cfg['plotted_data'] = {'type': '2dmap'}

            except Exception as e:
                ax.set_title(f"Error: {e}")
                ax.axis('off')

        plt.tight_layout()

        desc = self.title_textbox.get("1.0", "end").strip()
        if desc:
            # Reservar espacio arriba (0.85 significa que las gráficas ocupan hasta el 85% de la altura)
            self.fig.subplots_adjust(top=0.88)
            self.fig.suptitle(desc, fontsize=9, ha='center', va='top', wrap=True)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Toolbar con lupa y mover
        toolbar_frame = tk.Frame(self.plot_frame)
        toolbar_frame.pack(side='bottom', fill='x')
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

    def save_plot_data_as_txt(self, idx):
        """
        Save the exact data that was plotted for plot index idx.
        For line plots: column headers are exactly the X and Y axis labels from the plot.
        For slice plots: first column is the X axis label, subsequent columns are 'Y axis label | slice_var = value'.
        """
        if idx >= len(self.plot_configs):
            messagebox.showwarning("Warning", "Invalid plot index.")
            return

        cfg = self.plot_configs[idx]
        plotted = cfg.get('plotted_data', None)
        if not plotted:
            messagebox.showwarning("Warning", "No plotted data available to save. Please plot first.")
            return

        if plotted.get('type') == '2dmap':
            messagebox.showwarning("Warning", "2D map plots cannot be saved as TXT.")
            return

        try:
            x_vals = np.array(plotted['x'])
            y_list = plotted['y']
            plot_type = plotted['type']

            # Find the right axes to read labels from
            row, col = divmod(idx, self.cols_var.get())
            ax = self.axs[row, col]
            xlabel = ax.get_xlabel()
            ylabel = ax.get_ylabel()

            if plot_type == 'line':
                # Take axis labels directly from the plot
                header_labels = [xlabel, ylabel]

            elif plot_type == 'slices':
                # First column: X axis label
                slice_var = cfg['y_var'].get()
                labels = [f"{ylabel} | {slice_var} = {val}" for val in plotted['labels']]
                header_labels = [xlabel] + labels

            else:
                messagebox.showwarning("Warning", "Unsupported plot type for saving.")
                return

            # Ensure y columns align with x
            cols = [x_vals]
            for y in y_list:
                y_arr = np.array(y)
                if y_arr.shape != x_vals.shape:
                    try:
                        y_arr = np.broadcast_to(y_arr, x_vals.shape)
                    except Exception:
                        if y_arr.size == x_vals.size:
                            y_arr = y_arr.ravel()
                        elif y_arr.size == 1:
                            y_arr = np.full_like(x_vals, y_arr.item(), dtype=float)
                        else:
                            y_arr = np.resize(y_arr, x_vals.shape)
                cols.append(y_arr)

            data = np.column_stack(cols)

            save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", "*.txt")])
            if not save_path:
                return

            header_str = "\t".join(header_labels)
            np.savetxt(save_path, data, delimiter="\t", header=header_str, comments="", fmt="%g")

            messagebox.showinfo("Success", f"Data saved as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data:\n{e}")

    def save_plot(self):
        if self.fig is None:
            messagebox.showwarning("Warning", "No plot available to save.")
            return
        if not hasattr(self, 'file_path') or self.file_path is None:
            messagebox.showwarning("Warning", "No file loaded to determine save location.")
            return

        base_dir = os.path.dirname(self.file_path)
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        save_path = os.path.join(base_dir, base_name + "_plot.png")

        try:
            self.fig.savefig(save_path)
            messagebox.showinfo("Success", f"Plot saved as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetCDFPlotterApp(root)
    root.mainloop()
