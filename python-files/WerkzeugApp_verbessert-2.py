
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import re

typ_dict = {
    '0': "Sonderwerkzeug", '1': "Bohrer", '2': "Fräser", '3': "Fräser Besäumen",
    '4': "Gewindebohrer", '5': "Radiusfräser", '6': "Torusfräser", '7': "Reibahle",
    '8': "Wendeplattenwerkzeug", '9': "Sonstiges"
}
werkstoff_dict = {
    '1': "Hartmetall", '2': "HSS", '3': "Wendeplatten", '4': "Hartmetall Lang",
    '5': "Hartmetall Extra Lang", '6': "HSS Lang", '7': "HSS Extra Lang",
    '8': "Wendeplatten Lang", '9': "Wendeplatten Extra Lang"
}

def parse_nc_file(file_path):
    pattern = re.compile(r"P(\d+)\s+T(\d{7})\s+L([\d\.]+)\s+R([\d\.]+)")
    tools = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                position, tool_id, length, radius = match.groups()
                pos_num = int(position)
                typ_code, werkstoff_code = tool_id[0], tool_id[1]
                typ = typ_dict.get(typ_code, "Unbekannt")
                werkstoff = werkstoff_dict.get(werkstoff_code, "Unbekannt")

                if typ_code == '4':
                    steigung = float(f"{int(tool_id[2:5]) / 100:.2f}")
                    durchmesser = float(tool_id[5:7])
                    schneidanzahl = "-"
                else:
                    durchmesser = float(f"{int(tool_id[2:4])}.{tool_id[4]}")
                    schneidanzahl = int(tool_id[5])
                    steigung = "-"

                eckenradius = float(tool_id[6]) if tool_id[6].isdigit() else 0.0
                status = "Aktiv" if pos_num <= 60 else "Inaktiv"

                tools.append({
                    "Werkzeugnummer": tool_id,
                    "Typ": typ,
                    "Durchmesser [mm]": durchmesser,
                    "Werkzeugradius [mm]": float(radius),
                    "Länge [mm]": float(length),
                    "Steigung [mm]": steigung,
                    "Werkstoff": werkstoff,
                    "Schneiden": schneidanzahl,
                    "Status": status
                })
    return pd.DataFrame(tools)

class WerkzeugApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Werkzeugübersicht")
        self.df = pd.DataFrame()
        self.search_var = tk.StringVar()
        self.sort_column = None
        self.sort_reverse = False

        frame = tk.Frame(root)
        frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(frame, text="Datei laden", command=self.load_file).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(frame, text="Suchen", command=self.search).pack(side=tk.LEFT)
        tk.Button(frame, text="Status umschalten", command=self.toggle_status).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(root, columns=[
            "Werkzeugnummer", "Typ", "Durchmesser [mm]", "Werkzeugradius [mm]", "Länge [mm]",
            "Steigung [mm]", "Werkstoff", "Schneiden", "Status"
        ], show="headings")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=130)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("NC-Dateien", "*.nc"), ("Alle Dateien", "*.*")])
        if path:
            self.df = parse_nc_file(path)
            self.update_tree(self.df)

    def update_tree(self, df):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for _, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def search(self):
        query = self.search_var.get().lower()
        if not query or self.df.empty:
            self.update_tree(self.df)
        else:
            filtered = self.df[self.df.apply(lambda row: query in str(row).lower(), axis=1)]
            self.update_tree(filtered)

    def toggle_status(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Hinweis", "Bitte ein Werkzeug auswählen.")
            return
        values = list(self.tree.item(selected)["values"])
        idx = self.df[self.df["Werkzeugnummer"] == values[0]].index
        if not idx.empty:
            current = self.df.at[idx[0], "Status"]
            self.df.at[idx[0], "Status"] = "Inaktiv" if current == "Aktiv" else "Aktiv"
            self.update_tree(self.df)

    def sort_by_column(self, col):
        if self.df.empty:
            return
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        self.df.sort_values(by=col, ascending=not self.sort_reverse, inplace=True)
        self.update_tree(self.df)

if __name__ == "__main__":
    root = tk.Tk()
    app = WerkzeugApp(root)
    root.mainloop()
