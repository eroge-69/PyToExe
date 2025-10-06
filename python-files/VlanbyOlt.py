import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import pandas as pd

# Optional OCR support
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

IP_REGEX = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,5})?)')

def extract_ips(text):
    if not isinstance(text, str):
        return []
    # findall returns items like '10.1.8.87' or '10.1.8.47:3680'
    found = IP_REGEX.findall(text)
    # Basic sanity: filter out invalid octets (>255)
    valid = []
    for f in found:
        ip_part = f.split(':')[0]
        octets = ip_part.split('.')
        if len(octets) == 4 and all(0 <= int(o) <= 255 for o in octets):
            valid.append(f)
    # remove duplicates while preserving order
    seen=set(); out=[]
    for ip in valid:
        if ip not in seen:
            seen.add(ip); out.append(ip)
    return out

class VlanApp:
    def __init__(self, root):
        self.root = root
        root.title("VLAN → OLT IP Opener")
        root.geometry("820x520")

        frm = ttk.Frame(root, padding=8); frm.pack(fill='both', expand=True)

        top = ttk.Frame(frm)
        top.pack(fill='x', pady=4)

        ttk.Button(top, text="Load CSV/Excel", command=self.load_file).pack(side='left', padx=4)
        if OCR_AVAILABLE:
            ttk.Button(top, text="Load Image (OCR)", command=self.load_image).pack(side='left', padx=4)

        ttk.Label(top, text="Search VLAN:").pack(side='left', padx=8)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var, width=12)
        search_entry.pack(side='left')
        search_entry.bind("<Return>", lambda e: self.search())

        ttk.Button(top, text="Search", command=self.search).pack(side='left', padx=6)
        ttk.Button(top, text="Open Selected in Browser", command=self.open_selected).pack(side='right', padx=4)

        # Treeview to show VLANs
        cols = ("Vlan", "Vlan Name", "OLT IPs (parsed)")
        self.tree = ttk.Treeview(frm, columns=cols, show='headings', height=22)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=250 if c!="Vlan" else 80, anchor='w')
        self.tree.pack(fill='both', expand=True, pady=8)

        bottom = ttk.Frame(frm)
        bottom.pack(fill='x')
        ttk.Button(bottom, text="Open All Visible", command=self.open_all_visible).pack(side='left', padx=4)
        ttk.Button(bottom, text="Clear List", command=self.clear).pack(side='left', padx=4)

        self.data = []  # list of dicts: {'vlan': '12', 'name':'...', 'raw':'...', 'ips': [...]}

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV/Excel", "*.csv *.xlsx *.xls"), ("All files","*.*")])
        if not path:
            return
        try:
            if path.lower().endswith('.csv'):
                df = pd.read_csv(path, dtype=str, keep_default_na=False)
            else:
                df = pd.read_excel(path, dtype=str, keep_default_na=False)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read file:\n{e}")
            return
        # Try to locate columns
        df_cols = [c.lower() for c in df.columns]
        vlan_col = None; name_col=None; ip_col=None
        for c in df.columns:
            cl = c.lower()
            if 'vlan' in cl and vlan_col is None:
                vlan_col = c
            elif ('name' in cl or 'vlan name' in cl) and name_col is None:
                name_col = c
            elif ('olt' in cl or 'ip' in cl) and ip_col is None:
                ip_col = c
        # fallback to first three columns if not found
        if vlan_col is None and len(df.columns) >= 1:
            vlan_col = df.columns[0]
        if name_col is None and len(df.columns) >= 2:
            name_col = df.columns[1]
        if ip_col is None and len(df.columns) >= 3:
            ip_col = df.columns[2]
        # populate
        self.data.clear()
        for idx, row in df.iterrows():
            vlan_val = str(row.get(vlan_col,"")).strip() if vlan_col else ""
            name_val = str(row.get(name_col,"")).strip() if name_col else ""
            raw_ip = str(row.get(ip_col,"")).strip() if ip_col else ""
            ips = extract_ips(raw_ip)
            self.data.append({'vlan': vlan_val, 'name': name_val, 'raw': raw_ip, 'ips': ips})
        self.refresh_tree(self.data)
        messagebox.showinfo("Loaded", f"Loaded {len(self.data)} rows from file.")

    def load_image(self):
        if not OCR_AVAILABLE:
            messagebox.showerror("OCR not available", "Pillow/pytesseract not installed.")
            return
        path = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.tiff *.bmp"),("All files","*.*")])
        if not path:
            return
        try:
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            messagebox.showerror("OCR Error", f"Error reading image:\n{e}")
            return
        # crude parsing: try to find lines with vlan number and ip
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        parsed = []
        for ln in lines:
            # try to find vlan number (first number <= 5 digits)
            m = re.search(r'\b(\d{1,4})\b', ln)
            vlan_val = m.group(1) if m else ""
            ips = extract_ips(ln)
            parsed.append({'vlan': vlan_val, 'name': ln, 'raw': ln, 'ips': ips})
        self.data = parsed
        self.refresh_tree(self.data)
        messagebox.showinfo("OCR", f"OCR parsed {len(parsed)} lines (manual verification recommended).")

    def refresh_tree(self, items):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for it in items:
            iptext = ", ".join(it['ips']) if it['ips'] else it['raw']
            self.tree.insert('', 'end', values=(it['vlan'], it['name'], iptext))

    def search(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_tree(self.data)
            return
        # treat q as VLAN number or text match
        filtered = [d for d in self.data if d['vlan']==q or q.lower() in str(d['name']).lower() or q.lower() in str(d['raw']).lower()]
        self.refresh_tree(filtered)
        if not filtered:
            messagebox.showinfo("No match", "Koi VLAN match nahi hua.")

    def open_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Koi item select karo pehle.")
            return
        for s in sel:
            vals = self.tree.item(s, 'values')
            ipcol = vals[2]
            # parse ip strings from displayed field
            ips = IP_REGEX.findall(ipcol)
            if not ips:
                # maybe raw text with no IP, skip
                continue
            for ip in ips:
                url = self.ip_to_url(ip)
                webbrowser.open_new_tab(url)

    def open_all_visible(self):
        for row in self.tree.get_children():
            vals = self.tree.item(row,'values')
            ipcol = vals[2]
            ips = IP_REGEX.findall(ipcol)
            for ip in ips:
                url = self.ip_to_url(ip)
                webbrowser.open_new_tab(url)

    def ip_to_url(self, ip_text):
        # ip_text may be '10.1.8.53' or '10.2.15.47:3680'
        if ':' in ip_text:
            # ip:port
            return f"https://{ip_text}"
        else:
            return f"https://{ip_text}"

    def clear(self):
        self.data.clear()
        self.refresh_tree(self.data)

if __name__ == "__main__":
    root = tk.Tk()
    app = VlanApp(root)
    root.mainloop()
