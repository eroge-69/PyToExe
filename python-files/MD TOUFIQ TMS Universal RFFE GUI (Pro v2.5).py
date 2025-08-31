# app.py — MD TOUFIQ TMS Universal RFFE GUI (Pro v2.5)
# -----------------------------------------------------
# pip install pyserial pandas openpyxl xlsxwriter
# run:  python app.py
# EXE:  pyinstaller --noconsole --onefile --name "I2C_RFFE_Tool_MD_TOUFIQ_TMS_Pro" app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, time, csv, threading, queue
import serial, serial.tools.list_ports

# Optional Excel support
try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:
    HAVE_PANDAS = False

APP_TITLE = "MD TOUFIQ TMS - Universal RFFE Tool (PC UI Pro v2.5)"
PROFILE_FILE = "ic_profiles.json"

DEFAULT_PROFILES = {
    "Generic": {
        "mode": "AUTO",
        "notes": "Generic RFFE device. Auto width.",
        "defaults": {"id": "0x0", "reg": "0x0"}
    },
    "Qualcomm_PA": {
        "mode": "2BYTE",
        "notes": "Typical PA: 2-byte reads, auto-increment.",
        "defaults": {"id": "0x2", "reg": "0x00"}
    },
    "MTK_LNA": {
        "mode": "7BIT",
        "notes": "Some LNA blocks use 7-bit payload.",
        "defaults": {"id": "0x1", "reg": "0x00"}
    }
}

def load_profiles():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return DEFAULT_PROFILES.copy()

def save_profiles(profiles):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
    except Exception as e:
        messagebox.showwarning("Profiles", f"Could not save profiles: {e}")

class SerialWorker(threading.Thread):
    def __init__(self, ser, rx_queue):
        super().__init__(daemon=True)
        self.ser = ser
        self.q = rx_queue
        self.running = True
    def run(self):
        buf = b""
        while self.running:
            try:
                if self.ser and self.ser.in_waiting:
                    chunk = self.ser.read(self.ser.in_waiting)
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        s = line.decode(errors="ignore").strip()
                        if s:
                            self.q.put(s)
                time.sleep(0.01)
            except Exception as e:
                self.q.put(f"[ERR] {e}")
                break

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x720")
        self.minsize(980, 640)
        self.style = ttk.Style()
        self._theme = "light"
        self._set_theme(self._theme)

        self.ser = None
        self.worker = None
        self.rx_q = queue.Queue()
        self.profiles = load_profiles()

        self._build_ui()
        self.after(60, self._poll_rx)

    # ---------- THEME ----------
    def _set_theme(self, which):
        try:
            # simple ttk presets
            if which == "dark":
                self.style.theme_use("clam")
                self.style.configure(".", background="#1e1e1e", foreground="#eaeaea", fieldbackground="#2b2b2b")
                self.style.configure("Treeview", background="#1e1e1e", foreground="#eaeaea", fieldbackground="#1e1e1e")
                self.configure(bg="#1e1e1e")
            else:
                self.style.theme_use("clam")
                self.style.configure(".", background="#f7f7f7", foreground="#232323", fieldbackground="#ffffff")
                self.style.configure("Treeview", background="#ffffff", foreground="#232323", fieldbackground="#ffffff")
                self.configure(bg="#f7f7f7")
        except Exception:
            pass

    # ---------- UI ----------
    def _build_ui(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=8, pady=6)

        ttk.Label(top, text="MD TOUFIQ TMS", font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 10))

        self.cmb_port = ttk.Combobox(top, values=self._ports(), width=26, state="readonly")
        self.cmb_port.pack(side="left")
        ttk.Button(top, text="Refresh", command=lambda: self.cmb_port.config(values=self._ports())).pack(side="left", padx=6)

        ttk.Label(top, text="Baud:").pack(side="left", padx=(16, 4))
        self.cmb_baud = ttk.Combobox(top, values=["115200","230400","57600"], width=10, state="readonly")
        self.cmb_baud.set("115200"); self.cmb_baud.pack(side="left")

        self.btn_conn = ttk.Button(top, text="Connect", command=self.on_connect)
        self.btn_conn.pack(side="left", padx=8)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Label(top, text="Data Width:").pack(side="left", padx=(8, 4))
        self.cmb_mode = ttk.Combobox(top, values=["AUTO","7BIT","8BIT","2BYTE"], width=10, state="readonly")
        self.cmb_mode.set("AUTO"); self.cmb_mode.pack(side="left")
        ttk.Button(top, text="Apply", command=self.on_apply_mode).pack(side="left", padx=4)

        ttk.Label(top, text="Theme:").pack(side="left", padx=(18,4))
        self.cmb_theme = ttk.Combobox(top, values=["light","dark"], width=8, state="readonly")
        self.cmb_theme.set("light"); self.cmb_theme.pack(side="left")
        ttk.Button(top, text="Set", command=self.on_theme).pack(side="left", padx=(4,0))

        # Profiles bar
        prof = ttk.Frame(self); prof.pack(fill="x", padx=8, pady=(0,6))
        ttk.Label(prof, text="IC Profile:").pack(side="left", padx=(0,4))
        self.cmb_profile = ttk.Combobox(prof, values=list(self.profiles.keys()), width=18, state="readonly")
        self.cmb_profile.set("Generic"); self.cmb_profile.pack(side="left")
        ttk.Button(prof, text="Load", command=self.on_profile_load).pack(side="left", padx=4)
        ttk.Button(prof, text="Save As", command=self.on_profile_save_as).pack(side="left")
        ttk.Button(prof, text="Delete", command=self.on_profile_delete).pack(side="left", padx=(4,0))

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # Action bar
        act = ttk.Frame(self); act.pack(fill="x", padx=8, pady=6)
        ttk.Button(act, text="I2C Scan", command=lambda: self.send("I2C_SCAN")).pack(side="left", padx=4)
        ttk.Button(act, text="RFFE Scan", command=lambda: self.send("RFFE_SCAN")).pack(side="left", padx=4)
        ttk.Button(act, text="ATIVA RF", command=lambda: self.send("ATIVA_RF")).pack(side="left", padx=4)

        ttk.Label(act, text="ID:").pack(side="left", padx=(16,4))
        self.e_id = ttk.Entry(act, width=8); self.e_id.insert(0,"0x0"); self.e_id.pack(side="left")
        ttk.Label(act, text="Reg:").pack(side="left", padx=(6,4))
        self.e_reg = ttk.Entry(act, width=8); self.e_reg.insert(0,"0x0"); self.e_reg.pack(side="left")
        ttk.Label(act, text="Val0:").pack(side="left", padx=(6,4))
        self.e_val0 = ttk.Entry(act, width=8); self.e_val0.insert(0,"0x00"); self.e_val0.pack(side="left")
        ttk.Label(act, text="Val1(2B):").pack(side="left", padx=(6,4))
        self.e_val1 = ttk.Entry(act, width=8); self.e_val1.insert(0,"0x00"); self.e_val1.pack(side="left")
        ttk.Button(act, text="Read", command=self.on_read).pack(side="left", padx=4)
        ttk.Button(act, text="Write", command=self.on_write).pack(side="left", padx=4)

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # Map + Table area
        mid = ttk.Frame(self); mid.pack(fill="both", expand=True, padx=8, pady=6)

        left = ttk.Frame(mid); left.pack(side="left", fill="y")
        ttk.Label(left, text="Register Map (CSV)").pack(anchor="w")
        self.btn_load_map = ttk.Button(left, text="Load CSV", command=self.on_load_map)
        self.btn_load_map.pack(anchor="w", pady=(2,8))

        self.filter_var = tk.StringVar()
        ttk.Label(left, text="Search").pack(anchor="w")
        ent = ttk.Entry(left, textvariable=self.filter_var, width=26)
        ent.pack(anchor="w"); ent.bind("<KeyRelease>", lambda e: self.refresh_table_filter())

        ttk.Button(left, text="Export Table CSV", command=self.on_export_table_csv).pack(anchor="w", pady=(10,2))
        ttk.Button(left, text="Export Table XLSX", command=self.on_export_table_xlsx).pack(anchor="w")

        center = ttk.Frame(mid); center.pack(side="left", fill="both", expand=True, padx=(10,0))

        cols=("time","type","id","reg","len","data","ack","info","name","notes")
        self.tbl = ttk.Treeview(center, columns=cols, show="headings", height=12)
        for c in cols:
            self.tbl.heading(c, text=c.upper(), command=lambda c=c: self._sort_table(c, False))
            self.tbl.column(c, stretch=True, width=100)
        self.tbl.pack(fill="both", expand=True)
        self.tbl.bind("<Double-1>", self.on_row_double_click)

        # Right side log + export
        right = ttk.Frame(mid); right.pack(side="left", fill="y", padx=(10,0))
        ttk.Label(right, text="Log").pack(anchor="w")
        self.txt = tk.Text(right, wrap="none", width=48, height=20, font=("Consolas",10))
        self.txt.pack(fill="both", expand=True)
        ttk.Button(right, text="Save Log", command=self.on_save_log).pack(fill="x", pady=(6,2))
        ttk.Button(right, text="Export Log XLSX", command=self.on_export_log_xlsx).pack(fill="x")

        self.status = ttk.Label(self, relief="sunken", anchor="w")
        self.status.pack(fill="x")

        # Data holders
        self.map_rows = []  # from CSV
        self._table_cache = []  # for filtering

    # ---------- Ports ----------
    def _ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    # ---------- Theme ----------
    def on_theme(self):
        self._theme = self.cmb_theme.get()
        self._set_theme(self._theme)

    # ---------- Profiles ----------
    def on_profile_load(self):
        name = self.cmb_profile.get()
        prof = self.profiles.get(name)
        if not prof:
            messagebox.showwarning("Profiles", "Profile not found.")
            return
        # apply mode + defaults
        mode = prof.get("mode", "AUTO")
        self.cmb_mode.set(mode)
        self.on_apply_mode()
        d = prof.get("defaults", {})
        if "id" in d:  self.e_id.delete(0,"end");  self.e_id.insert(0, d["id"])
        if "reg" in d: self.e_reg.delete(0,"end"); self.e_reg.insert(0, d["reg"])
        note = prof.get("notes","")
        self._set_status(f"Profile '{name}' loaded. {note}")

    def on_profile_save_as(self):
        name = tk.simpledialog.askstring("Save Profile As", "Profile name:")
        if not name:
            return
        prof = {
            "mode": self.cmb_mode.get(),
            "notes": "User saved profile.",
            "defaults": {"id": self.e_id.get(), "reg": self.e_reg.get()}
        }
        self.profiles[name] = prof
        save_profiles(self.profiles)
        self.cmb_profile.config(values=list(self.profiles.keys()))
        self.cmb_profile.set(name)
        self._set_status(f"Profile '{name}' saved.")

    def on_profile_delete(self):
        name = self.cmb_profile.get()
        if name in DEFAULT_PROFILES:
            messagebox.showinfo("Profiles", "Default profiles cannot be deleted.")
            return
        if name in self.profiles:
            if messagebox.askyesno("Delete", f"Delete profile '{name}'?"):
                del self.profiles[name]
                save_profiles(self.profiles)
                self.cmb_profile.config(values=list(self.profiles.keys()))
                self.cmb_profile.set("Generic")
                self._set_status(f"Profile '{name}' deleted.")

    # ---------- Connect / Serial ----------
    def on_connect(self):
        if self.ser:
            try:
                if self.worker: self.worker.running=False
                self.ser.close()
            except: pass
            self.ser=None
            self.btn_conn.config(text="Connect")
            self._set_status("Disconnected")
            return

        port = self.cmb_port.get()
        if not port:
            messagebox.showwarning("Port","Select COM port"); return
        try:
            self.ser = serial.Serial(port, baudrate=int(self.cmb_baud.get()), timeout=0.05)
            self.worker = SerialWorker(self.ser, self.rx_q); self.worker.start()
            self.btn_conn.config(text="Disconnect")
            self._set_status(f"Connected {port}")
            self.send("GET_MODE")
        except Exception as e:
            messagebox.showerror("Serial", str(e))
            self.ser=None

    def send(self, cmd):
        if not self.ser:
            messagebox.showwarning("Serial","Not connected"); return
        try:
            self.ser.write((cmd+"\n").encode("ascii"))
            self._log(f">>> {cmd}")
        except Exception as e:
            self._log(f"[ERR] {e}")

    # ---------- Actions ----------
    def on_apply_mode(self):
        m = self.cmb_mode.get()
        if   m=="AUTO":  self.send("SET_MODE AUTO")
        elif m=="7BIT":  self.send("SET_MODE 7")
        elif m=="8BIT":  self.send("SET_MODE 8")
        elif m=="2BYTE": self.send("SET_MODE 2B")

    def on_read(self):
        try:
            sid = int(self.e_id.get(), 0)
            reg = int(self.e_reg.get(), 0)
        except:
            messagebox.showwarning("Input","ID/Reg? e.g., 0x2 / 0x10"); return
        self.send(f"RFFE_READ {sid} {reg}")

    def on_write(self):
        try:
            sid = int(self.e_id.get(), 0)
            reg = int(self.e_reg.get(), 0)
            v0  = int(self.e_val0.get(), 0)
            if self.cmb_mode.get()=="2BYTE":
                v1 = int(self.e_val1.get(), 0)
                self.send(f"RFFE_WRITE {sid} {reg} {v0} {v1}")
            else:
                self.send(f"RFFE_WRITE {sid} {reg} {v0}")
        except:
            messagebox.showwarning("Input","Enter valid hex/dec values"); return

    # ---------- Map / Table ----------
    def on_load_map(self):
        p = filedialog.askopenfilename(title="Open Register Map (CSV)", filetypes=[("CSV","*.csv")])
        if not p: return
        rows = []
        try:
            with open(p, "r", newline="", encoding="utf-8") as f:
                for i, row in enumerate(csv.DictReader(f)):
                    idv = row.get("id","").strip()
                    reg = row.get("reg","").strip()
                    name = row.get("name","").strip()
                    notes = row.get("notes","").strip()
                    if idv and reg:
                        rows.append({"id":idv, "reg":reg, "name":name, "notes":notes})
        except Exception as e:
            messagebox.showerror("CSV", f"Failed to load: {e}")
            return
        self.map_rows = rows
        self.refresh_table_filter()
        self._set_status(f"Loaded map: {os.path.basename(p)} ({len(rows)} rows)")

    def refresh_table_filter(self):
        key = self.filter_var.get().strip().lower()
        self.tbl.delete(*self.tbl.get_children())
        self._table_cache.clear()
        # Show just the mapping rows as a base “view”; live data will append
        for r in self.map_rows:
            if key and (key not in r["id"].lower() and key not in r["reg"].lower() and key not in r["name"].lower() and key not in r["notes"].lower()):
                continue
            vals = ("-", "MAP", r["id"], r["reg"], "-", "-", "-", "-", r["name"], r["notes"])
            self.tbl.insert("", "end", values=vals)
            self._table_cache.append(vals)

    def on_row_double_click(self, event):
        item = self.tbl.focus()
        if not item: return
        vals = self.tbl.item(item, "values")
        # If it's a MAP row, apply id/reg to inputs
        if vals[1] == "MAP":
            self.e_id.delete(0,"end"); self.e_id.insert(0, vals[2])
            self.e_reg.delete(0,"end"); self.e_reg.insert(0, vals[3])
            self._set_status(f"Applied from map: ID={vals[2]} REG={vals[3]}")

    def _sort_table(self, col, reverse):
        # simple sort on current rows only
        items = [(self.tbl.set(k, col), k) for k in self.tbl.get_children("")]
        try:
            items.sort(key=lambda t: int(t[0],16), reverse=reverse)  # hex-ish
        except Exception:
            items.sort(reverse=reverse)
        for idx, (_, k) in enumerate(items):
            self.tbl.move(k, "", idx)
        self.tbl.heading(col, command=lambda: self._sort_table(col, not reverse))

    # ---------- Export ----------
    def on_export_table_csv(self):
        p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not p: return
        cols=("time","type","id","reg","len","data","ack","info","name","notes")
        try:
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(cols)
                for iid in self.tbl.get_children(""):
                    w.writerow(self.tbl.item(iid, "values"))
            messagebox.showinfo("Export", f"Saved: {p}")
        except Exception as e:
            messagebox.showerror("Export", str(e))

    def on_export_table_xlsx(self):
        if not HAVE_PANDAS:
            messagebox.showinfo("Excel", "Install pandas/openpyxl/xlsxwriter for XLSX export."); return
        p = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not p: return
        cols=("time","type","id","reg","len","data","ack","info","name","notes")
        rows=[self.tbl.item(i,"values") for i in self.tbl.get_children("")]
        try:
            df = pd.DataFrame(rows, columns=cols)
            df.to_excel(p, index=False)
            messagebox.showinfo("Export", f"Saved: {p}")
        except Exception as e:
            messagebox.showerror("Export", str(e))

    def on_save_log(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")])
        if not p: return
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.txt.get("1.0","end"))
            messagebox.showinfo("Saved", p)
        except Exception as e:
            messagebox.showerror("Save", str(e))

    def on_export_log_xlsx(self):
        if not HAVE_PANDAS:
            messagebox.showinfo("Excel", "Install pandas/openpyxl/xlsxwriter for XLSX export."); return
        p = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not p: return
        # very simple: one column log
        try:
            lines = [ln for ln in self.txt.get("1.0","end").splitlines()]
            df = pd.DataFrame({"log": lines})
            df.to_excel(p, index=False)
            messagebox.showinfo("Export", f"Saved: {p}")
        except Exception as e:
            messagebox.showerror("Export", str(e))

    # ---------- RX / Parse ----------
    def _poll_rx(self):
        upd=False
        while True:
            try:
                s = self.rx_q.get_nowait()
            except queue.Empty:
                break
            self._log(s)
            self._parse_line(s)
            upd=True
        if upd:
            self._set_status(time.strftime("%H:%M:%S")+"  updated")
        self.after(60, self._poll_rx)

    def _log(self, s):
        self.txt.insert("end", s+"\n"); self.txt.see("end")

    def _set_status(self, s):
        self.status.config(text=s)

    def _insert_row(self, vals):
        self.tbl.insert("", "end", values=vals)

    def _map_lookup(self, sid_hex, reg_hex):
        sid = sid_hex.lower()
        reg = reg_hex.lower()
        for r in self.map_rows:
            if r["id"].lower()==sid and r["reg"].lower()==reg:
                return r["name"], r["notes"]
        return "", ""

    def _parse_line(self, s):
        ts = time.strftime("%H:%M:%S")
        line = s.strip()

        # Mode handshake
        if line.startswith("MODE "):
            md = line.split()[-1].upper()
            if md in ("AUTO","7BIT","8BIT","2BYTE"):
                self.cmb_mode.set(md)
            return

        # I2C scan
        if line.startswith("ADDR "):
            addr = line.split()[1]
            self._insert_row((ts,"I2C","-","-","1",addr,"1","I2C device","",""))
            return

        # RFFE scan lines
        if line.startswith("RFFE ID"):
            # Example: RFFE ID 0 REG00 5 ACK 1
            parts = line.replace(":"," ").split()
            try:
                sid = int(parts[2], 16) if parts[2].startswith("0x") else int(parts[2], 0)
            except:
                sid = int(parts[2], 0)
            # data tokens before ACK
            data_tokens=[]
            if "ACK" in parts:
                ai = parts.index("ACK")
                for p in parts[ai-2:ai]:
                    if all(c in "0123456789ABCDEFabcdef" for c in p) and len(p)<=2:
                        data_tokens.append(p)
            dstr = " ".join([f"0x{int(x,16):02X}" for x in data_tokens])
            sid_hex = f"0x{sid:02X}"
            name, notes = self._map_lookup(sid_hex, "0x00")
            self._insert_row((ts,"RFFE",sid_hex,"0x00",str(len(data_tokens)),dstr,"1","scan",name,notes))
            return

        # Read response: DATA n xx [yy] ACK a [PARITY_ERR 1]
        if line.startswith("DATA "):
            parts = line.split()
            try:
                length = int(parts[1])
            except: length = 1
            data_tokens=[]
            i=2
            for _ in range(max(0,length)):
                if i < len(parts):
                    data_tokens.append(parts[i]); i+=1
            ack_val="0"
            if "ACK" in parts:
                ack_val = parts[parts.index("ACK")+1]
            info = "PARITY_ERR" if "PARITY_ERR" in parts else ""
            sid_hex = self.e_id.get()
            reg_hex = self.e_reg.get()
            name, notes = self._map_lookup(sid_hex, reg_hex)
            self._insert_row((ts,"READ",sid_hex,reg_hex,str(length)," ".join(data_tokens),ack_val,info,name,notes))
            return

        # Write response: ACK 1 [PARITY_ERR 1]
        if line.startswith("ACK "):
            ack_val = line.split()[1]
            info = "PARITY_ERR" if "PARITY_ERR" in line else ""
            sid_hex = self.e_id.get(); reg_hex = self.e_reg.get()
            name, notes = self._map_lookup(sid_hex, reg_hex)
            self._insert_row((ts,"WRITE",sid_hex,reg_hex,"-","-",ack_val,info,name,notes))
            return

if __name__ == "__main__":
    App().mainloop()
