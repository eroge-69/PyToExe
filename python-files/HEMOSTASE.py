import tkinter as tk
from tkinter import ttk, messagebox

class HemostaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Logiciel Hémostase - TP & TCK")
        self.root.geometry("650x400")

        # Variables
        self.tq_var = tk.StringVar()
        self.tp_percent_var = tk.StringVar()
        self.inr_var = tk.StringVar()
        self.tca_patient_var = tk.StringVar()

        # Frame principal
        frame = ttk.Frame(root)
        frame.pack(padx=10, pady=10, fill='x', expand=True)

        # Zone logo (placeholder)
        logo_frame = ttk.Frame(frame, width=120, height=80, relief="sunken")
        logo_frame.grid(row=0, column=0, rowspan=3, sticky="nw", padx=(0, 15), pady=(0,15))
        logo_label = ttk.Label(logo_frame, text="Zone Logo\n(à insérer)")
        logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # Champs côte à côte
        labels = ["Temps Quick (TQ) en s :", "TP (%) :", "INR :", "Temps témoin TCK (s) :", "Temps patient TCK (s) :"]
        variables = [self.tq_var, self.tp_percent_var, self.inr_var, None, self.tca_patient_var]
        default_values = ["", "", "", "24", ""]

        # Temps témoin TCK fixe à 24 s, en lecture seule
        ttk.Label(frame, text=labels[3]).grid(row=1, column=3, sticky="w")
        ttk.Label(frame, text=default_values[3]).grid(row=1, column=4, sticky="w")

        # Placement champs côte à côte
        ttk.Label(frame, text=labels[0]).grid(row=0, column=1, sticky="w", padx=5)
        tq_entry = ttk.Entry(frame, textvariable=self.tq_var, width=10)
        tq_entry.grid(row=0, column=2, sticky="w", padx=5)

        ttk.Label(frame, text=labels[1]).grid(row=0, column=3, sticky="w", padx=5)
        tp_entry = ttk.Entry(frame, textvariable=self.tp_percent_var, width=10)
        tp_entry.grid(row=0, column=4, sticky="w", padx=5)

        ttk.Label(frame, text=labels[2]).grid(row=0, column=5, sticky="w", padx=5)
        self.inr_entry = ttk.Entry(frame, textvariable=self.inr_var, width=10)
        self.inr_entry.grid(row=0, column=6, sticky="w", padx=5)

        ttk.Label(frame, text=labels[4]).grid(row=1, column=5, sticky="w", padx=5)
        tca_patient_entry = ttk.Entry(frame, textvariable=self.tca_patient_var, width=10)
        tca_patient_entry.grid(row=1, column=6, sticky="w", padx=5)

        # Surveille changement de TQ pour auto-remplir TP et INR si TQ = 11.8
        self.tq_var.trace_add("write", self.tq_changed)

    def tq_changed(self, *args):
        try:
            tq_val = float(self.tq_var.get())
        except ValueError:
            # Valeur non valide, on réactive l'édition INR
            self.inr_entry.config(state="normal")
            return

        if tq_val == 11.8:
            self.tp_percent_var.set("100")
            self.inr_var.set("1.00")
            self.inr_entry.config(state="readonly")
        else:
            self.inr_entry.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = HemostaseApp(root)
    root.mainloop()
