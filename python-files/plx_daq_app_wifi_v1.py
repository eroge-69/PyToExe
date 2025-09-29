import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import websocket
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------
# Wi-Fi WebSocket PLX-DAQ GUI
# ---------------------------
class WiFiWSDAQApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 WebSocket PLX-DAQ")
        self.root.geometry("900x700")

        # WebSocket and state
        self.ws = None
        self.ws_thread = None
        self.connected = False

        # Data store (list of tuples: (time, v1, v2, v3))
        self.data_log = []
        self.max_rows = 1000  # keep at most this many rows (auto-trim)

        self._build_ui()

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self):
        # Connection frame
        conn = ttk.LabelFrame(self.root, text="Connection", padding=8)
        conn.pack(fill="x", padx=8, pady=6)

        ttk.Label(conn, text="WebSocket URL:").pack(side="left")
        self.url_var = tk.StringVar(value="ws://192.168.1.120:81")
        self.url_entry = ttk.Entry(conn, textvariable=self.url_var, width=30)
        self.url_entry.pack(side="left", padx=6)

        self.btn_connect = ttk.Button(conn, text="Connect", command=self._on_connect_clicked)
        self.btn_connect.pack(side="left", padx=6)

        self.lbl_status = ttk.Label(conn, text="Disconnected")
        self.lbl_status.pack(side="right", padx=6)

        # Indicators frame
        ind = ttk.LabelFrame(self.root, text="Indicators", padding=8)
        ind.pack(fill="x", padx=8, pady=6)

        # use tk.Label so background colors work
        self.ind_widgets = {}
        for i, name in enumerate(("Val1", "Val2", "Val3")):
            tk.Label(ind, text=f"{name}:", font=("Arial", 11)).grid(row=0, column=i*2, sticky="w", padx=(10,2))
            lbl = tk.Label(ind, text="---", width=10, bg="lightgray", font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=i*2+1, padx=(2,10))
            self.ind_widgets[name] = lbl

        # Table + plot frame
        middle = ttk.Frame(self.root)
        middle.pack(fill="both", expand=True, padx=8, pady=6)

        # Table (left)
        table_frame = ttk.LabelFrame(middle, text="Data Log", padding=6)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0,8))

        cols = ("Time", "Val1", "Val2", "Val3")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=90, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Plot (right)
        plot_frame = ttk.LabelFrame(middle, text="Live Plot", padding=6)
        plot_frame.pack(side="right", fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(5,4))
        self.lines = [self.ax.plot([], [], label=f"Val{i+1}")[0] for i in range(3)]
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Value")
        self.ax.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Bottom controls
        bottom = ttk.Frame(self.root, padding=8)
        bottom.pack(fill="x", padx=8, pady=6)

        self.btn_save = ttk.Button(bottom, text="Save CSV", command=self.save_csv, state="disabled")
        self.btn_save.pack(side="left", padx=4)

        self.btn_export = ttk.Button(bottom, text="Export Excel", command=self.export_excel, state="disabled")
        self.btn_export.pack(side="left", padx=4)

        ttk.Label(bottom, text="Keep rows:").pack(side="left", padx=(20,2))
        self.rows_spin = tk.Spinbox(bottom, from_=10, to=10000, width=6, command=self._update_max_rows)
        self.rows_spin.delete(0,"end"); self.rows_spin.insert(0, str(self.max_rows))
        self.rows_spin.pack(side="left")

        self.btn_clear = ttk.Button(bottom, text="Clear Log", command=self.clear_log)
        self.btn_clear.pack(side="right", padx=4)

    # -------------------------
    # Connect / Disconnect
    # -------------------------
    def _on_connect_clicked(self):
        if not self.connected:
            self._connect_ws()
        else:
            self._disconnect_ws()

    def _connect_ws(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL required", "Enter the WebSocket URL (e.g. ws://192.168.1.120:81)")
            return

        # create WebSocketApp with callbacks
        try:
            self.ws = websocket.WebSocketApp(
                url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
        except Exception as e:
            messagebox.showerror("WebSocket creation failed", str(e))
            return

        # run in background thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={"ping_interval": 20, "ping_timeout": 5}, daemon=True)
        self.ws_thread.start()

        # optimistic UI change (finalized in on_open/on_close)
        self.lbl_status.config(text="Connecting...")
        self.btn_connect.config(state="disabled")

    def _disconnect_ws(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        self.connected = False
        self.lbl_status.config(text="Disconnected")
        self.btn_connect.config(text="Connect")
        self.btn_save.config(state="disabled")
        self.btn_export.config(state="disabled")

    # -------------------------
    # WebSocket callbacks
    # -------------------------
    def _on_open(self, ws):
        # runs in ws thread — marshal to main thread
        self.root.after(0, self._on_open_ui)

    def _on_open_ui(self):
        self.connected = True
        self.lbl_status.config(text="Connected")
        self.btn_connect.config(text="Disconnect", state="normal")
        self.btn_save.config(state="normal")
        self.btn_export.config(state="normal")

    def _on_error(self, ws, error):
        # marshal to UI thread
        self.root.after(0, lambda: self._on_error_ui(error))

    def _on_error_ui(self, error):
        messagebox.showerror("WebSocket Error", str(error))
        self.connected = False
        self.lbl_status.config(text="Error")
        self.btn_connect.config(text="Connect", state="normal")

    def _on_close(self, ws, close_status_code, close_msg):
        # marshal to main thread
        self.root.after(0, self._on_close_ui)

    def _on_close_ui(self):
        self.connected = False
        self.lbl_status.config(text="Disconnected")
        self.btn_connect.config(text="Connect", state="normal")
        self.btn_save.config(state="disabled")
        self.btn_export.config(state="disabled")

    def _on_message(self, ws, message):
        # called in ws thread, so marshal data to the GUI thread
        # Accept both LABEL and DATA messages:
        # LABEL,Time,Val1,Val2,Val3
        # DATA,123,12.3,45.6,78.9
        if not isinstance(message, str):
            try:
                message = message.decode("utf-8", errors="ignore")
            except Exception:
                message = str(message)

        if message.startswith("LABEL"):
            parts = message.split(",")
            # update column headings if given
            if len(parts) >= 2:
                headings = parts[1:]
                # marshal to UI
                self.root.after(0, lambda: self._update_headings(headings))
            return

        if message.startswith("DATA"):
            parts = message.split(",")
            if len(parts) >= 5:
                t, v1, v2, v3 = parts[1:5]
                # marshal to UI updates
                self.root.after(0, lambda: self._handle_data_row(t, v1, v2, v3))

    # -------------------------
    # UI helpers
    # -------------------------
    def _update_headings(self, headings):
        # set column headings if length matches
        cols = ("Time", "Val1", "Val2", "Val3")
        for i, h in enumerate(headings[:4]):
            if i < len(cols):
                self.tree.heading(cols[i], text=h)

    def _handle_data_row(self, t, v1, v2, v3):
        # convert values when possible
        try:
            vf1 = float(v1)
        except Exception:
            vf1 = v1
        try:
            vf2 = float(v2)
        except Exception:
            vf2 = v2
        try:
            vf3 = float(v3)
        except Exception:
            vf3 = v3

        # update indicators (colors simple)
        try:
            self.ind_widgets["Val1"].config(text=f"{v1}", bg="lightgreen")
            self.ind_widgets["Val2"].config(text=f"{v2}", bg="lightblue")
            self.ind_widgets["Val3"].config(text=f"{v3}", bg="lightyellow")
        except Exception:
            pass  # ignore UI color errors

        # append to data log (keep typed values for plotting)
        self.data_log.append((t, vf1, vf2, vf3))
        if len(self.data_log) > self.max_rows:
            # trim oldest rows
            self.data_log = self.data_log[-self.max_rows:]
            # also remove rows from tree
            children = self.tree.get_children()
            # delete excess top rows if needed
            if len(children) > self.max_rows:
                for cid in children[:len(children) - self.max_rows]:
                    self.tree.delete(cid)

        # add to table
        self.tree.insert("", "end", values=(t, v1, v2, v3))
        self.tree.yview_moveto(1.0)  # scroll to bottom

        # update plot
        self._update_plot()

    def _update_plot(self):
        if not self.data_log:
            return

        # build series (times index as sample count)
        xs = list(range(len(self.data_log)))
        try:
            ys1 = [float(r[1]) for r in self.data_log]
            ys2 = [float(r[2]) for r in self.data_log]
            ys3 = [float(r[3]) for r in self.data_log]
        except Exception:
            # if some values not numeric, skip plotting
            return

        self.lines[0].set_data(xs, ys1)
        self.lines[1].set_data(xs, ys2)
        self.lines[2].set_data(xs, ys3)

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    # -------------------------
    # Data operations
    # -------------------------
    def save_csv(self):
        if not self.data_log:
            messagebox.showinfo("No data", "No data to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            df = pd.DataFrame(self.data_log, columns=["Time", "Val1", "Val2", "Val3"])
            df.to_csv(path, index=False)
            messagebox.showinfo("Saved", f"CSV saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def export_excel(self):
        if not self.data_log:
            messagebox.showinfo("No data", "No data to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not path:
            return
        try:
            df = pd.DataFrame(self.data_log, columns=["Time", "Val1", "Val2", "Val3"])
            df.to_excel(path, index=False)
            messagebox.showinfo("Saved", f"Excel saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

    def clear_log(self):
        self.data_log.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        # reset indicators
        for w in self.ind_widgets.values():
            w.config(text="---", bg="lightgray")
        # clear plot
        for ln in self.lines:
            ln.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def _update_max_rows(self):
        try:
            self.max_rows = int(self.rows_spin.get())
        except Exception:
            pass

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    # ensure websocket-client uses the right default behavior
    # (no need to enable trace here)
    root = tk.Tk()
    app = WiFiWSDAQApp(root)
    root.mainloop()
