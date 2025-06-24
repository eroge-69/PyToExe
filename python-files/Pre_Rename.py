import tkinter as tk
from tkinter import ttk

class AssetVersionFormatter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pre Rename")
        self.geometry("600x900")
        self.minsize(400, 600)

        self.configure(bg="#2e2e2e")  # dark background
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TNotebook", background="#2e2e2e", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#444", foreground="white", padding=5)
        self.style.map("TNotebook.Tab", background=[("selected", "#666")])
        self.style.configure("TFrame", background="#2e2e2e")
        self.style.configure("TLabel", background="#2e2e2e", foreground="white")

        self.create_widgets()

    def create_widgets(self):
        input_frame = tk.Frame(self, bg="#2e2e2e")
        input_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(input_frame, text="Shot Name:", fg="white", bg="#2e2e2e").pack(anchor="w")
        self.asset_input = tk.Entry(input_frame, bg="#444", fg="white", insertbackground="white")
        self.asset_input.pack(fill="x")

        tk.Label(input_frame, text="Version:", fg="white", bg="#2e2e2e").pack(anchor="w", pady=(10, 0))
        self.version_input = tk.Entry(input_frame, bg="#444", fg="white", insertbackground="white")
        self.version_input.insert(0, "1")
        self.version_input.pack(fill="x")

        btn_frame = tk.Frame(input_frame, bg="#2e2e2e")
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Run", bg="#4b8b3b", fg="white", command=self.generate_outputs).pack(side="left", expand=True, fill="x")
        tk.Button(btn_frame, text="Clear", bg="#c0392b", fg="white", command=self.clear_all).pack(side="left", expand=True, fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.outputs_normal = self.create_tab("Normal", [
            "Maya / .mp4 / Nuke Current", "for_roto", "flatten", "flatten AX",
            "Gridwarp", "STMap_Undistort", "STMap_Redistort", "3DE"
        ])

        self.outputs_craftyapes = self.create_tab("CRAFTYAPES", [
            "flatten", "Maya", "3DE", "STMap_Redistort", "STMap_Undistort",
            "Cam .abc", "track geo .abc", "camWire", "camCone", "camCenter",
            "objectWire", "objectCone", "objectCenter", "matchmoveWire",
            "matchmoveCone", "matchmoveCenter"
        ])

        self.outputs_netflix = self.create_tab("Netflix - Scanline", [
            "flatten", "Maya", "3DE", "cone", "perspective", "wireframe"
        ])

        self.outputs_rotomaker = self.create_tab("ROTOMAKER", [
            "flatten", "Maya", "3DE", "cone", "perspective", "wireframe"
        ])

    def create_tab(self, title, labels):
        frame = tk.Frame(self.notebook, bg="#2e2e2e")
        frame.pack(fill="both", expand=True)

        fields = []
        for label in labels:
            tk.Label(frame, text=label, fg="white", bg="#2e2e2e").pack(anchor="w", padx=5)
            entry = tk.Entry(frame, bg="#444", fg="white", insertbackground="white", readonlybackground="#444")
            entry.pack(fill="x", padx=5, pady=2)
            entry.config(state="readonly")
            fields.append(entry)

        self.notebook.add(frame, text=title)
        return fields

    def generate_outputs(self):
        asset_name = self.asset_input.get().strip()
        version_raw = self.version_input.get().strip()
        all_outputs = self.outputs_normal + self.outputs_craftyapes + self.outputs_netflix + self.outputs_rotomaker

        if not asset_name or not version_raw:
            for field in all_outputs:
                field.config(state="normal")
                field.delete(0, tk.END)
                field.config(state="readonly")
            return

        try:
            version_int = int(version_raw)
        except ValueError:
            version_int = 0

        version_3 = f"v{version_int:03d}"
        version_4 = f"v{version_int:04d}"

        def set_text(entries, texts):
            for e, t in zip(entries, texts):
                e.config(state="normal")
                e.delete(0, tk.END)
                e.insert(0, t)
                e.config(state="readonly")

        normal_texts = [
            f"{asset_name}_trk_{version_3}",
            f"{asset_name}_for_roto_{version_3}",
            f"{asset_name}_flatten_{version_3}",
            f"{asset_name}_undistort_{version_3}",
            f"{asset_name}_Gridwarp_{version_3}",
            f"{asset_name}_STMap_Undistort_{version_3}",
            f"{asset_name}_STMap_Redistort_{version_3}",
            f"{asset_name}_trk_{version_3}_LD_3de_len_distortion_node"
        ]
        set_text(self.outputs_normal, normal_texts)

        labels_craftyapes = [
            "undistorted", "trackScene", "distortion", "redistort", "undistort",
            "shotCam", "trackGeo", "camWire", "camCone", "camCenter",
            "objectWire", "objectCone", "objectCenter", "matchmoveWire",
            "matchmoveCone", "matchmoveCenter"
        ]
        ca_texts = [f"{asset_name}-{label}_{version_3}" for label in labels_craftyapes]
        set_text(self.outputs_craftyapes, ca_texts)

        nf_texts = [
            f"{asset_name}_flat_{version_4}_DAS",
            f"{asset_name}_camTrack_{version_4}_DAS",
            f"{asset_name}_camTrack_{version_4}_DAS",
            f"{asset_name}_cones_{version_4}_DAS",
            f"{asset_name}_perspective_v0001_DAS",
            f"{asset_name}_wireframe_{version_4}_DAS"
        ]
        set_text(self.outputs_netflix, nf_texts)

        rm_texts = [
            f"{asset_name}_flat_{version_4}_RMK",
            f"{asset_name}_camTrack_{version_4}_RMK",
            f"{asset_name}_camTrack_{version_4}_RMK",
            f"{asset_name}_cones_{version_4}_RMK",
            f"{asset_name}_perspective_{version_4}_RMK",
            f"{asset_name}_wireframe_{version_4}_RMK"
        ]
        set_text(self.outputs_rotomaker, rm_texts)

    def clear_all(self):
        self.asset_input.delete(0, tk.END)
        self.version_input.delete(0, tk.END)
        self.version_input.insert(0, "1")
        all_outputs = self.outputs_normal + self.outputs_craftyapes + self.outputs_netflix + self.outputs_rotomaker
        for field in all_outputs:
            field.config(state="normal")
            field.delete(0, tk.END)
            field.config(state="readonly")

if __name__ == "__main__":
    app = AssetVersionFormatter()
    app.mainloop()
