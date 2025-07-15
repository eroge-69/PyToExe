import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle


class LooisPlezierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loois Plezier Planning")
        self.root.geometry("980x700")  # iets hoger ivm nieuwe checkbox
        self.root.config(bg="#222222")

        self.lp_geel = "#F7FF42"
        self.default_adres = "Wetsberg 93 3980 Tessenderlo-Ham"

        self.activities = []

        self.springkastelen = [
            "Piraat", "Smiley", "Glitter prinses", "Kleurrijke bouwblokjes", "Badeend",
            "Unicorn", "Dino", "Multiplay Jungle XL", "Stormbaan Leeuw", "Schuimparty"
        ]
        self.partytenten = ["10x5 M", "8x4 M"]
        self.lasergames = ["Anti cheat (kleurrijke)", "Kids (zwart wit)"]
        self.overige = ["Sint & Piet", "Muntenschuiver", "Popcornmachine", "Stroomgenerator"]
        
        # Voeg 'Pauze' toe als aparte optie
        self.extra_types = ["Pauze"]

        self.type_var = tk.StringVar()
        self.keuze_var = tk.StringVar()
        self.levering_var = tk.StringVar(value="Leveren")
        self.grondzeil_var = tk.BooleanVar()
        self.valmatten_var = tk.BooleanVar()
        self.zandzakken_var = tk.BooleanVar()
        self.roetzwart_var = tk.StringVar(value="Roetveeg")
        self.opmerkingen_var = tk.StringVar()

        self.create_widgets()
        self.update_greeting()
        self.update_keuze_options()

    def create_widgets(self):
        # Groet label
        self.greeting_label = tk.Label(self.root, text="", bg="#222222", fg=self.lp_geel, font=("Helvetica", 18, "bold"))
        self.greeting_label.pack(pady=12)

        # Frame invoer
        frame = tk.Frame(self.root, bg="#333333", pady=12, padx=15)
        frame.pack(fill=tk.X, padx=15, pady=5)

        # Type activiteit
        tk.Label(frame, text="Type activiteit:", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, state="readonly",
                                       values=["Springkasteel", "Partytent", "Lasergame", "Sint & Piet",
                                               "Muntenschuiver", "Popcornmachine", "Stroomgenerator"] + self.extra_types)
        self.type_combo.grid(row=0, column=1, padx=8, pady=5, sticky="we")
        self.type_combo.bind("<<ComboboxSelected>>", self.update_keuze_options)

        # Keuze
        tk.Label(frame, text="Keuze:", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky="w")
        self.keuze_combo = ttk.Combobox(frame, textvariable=self.keuze_var, state="readonly")
        self.keuze_combo.grid(row=0, column=3, padx=8, pady=5, sticky="we")

        # Levering / Ophalen (standaard verborgen)
        self.lever_radio1 = tk.Radiobutton(frame, text="Leveren", variable=self.levering_var, value="Leveren",
                                           bg="#333333", fg="white", selectcolor="#444444", font=("Arial", 10),
                                           command=self.update_lever_haal_adres)
        self.lever_radio2 = tk.Radiobutton(frame, text="Ophalen", variable=self.levering_var, value="Ophalen",
                                           bg="#333333", fg="white", selectcolor="#444444", font=("Arial", 10),
                                           command=self.update_lever_haal_adres)

        # Adres
        tk.Label(frame, text="Adres:", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.adres_entry = tk.Entry(frame, width=50, font=("Arial", 11))
        self.adres_entry.grid(row=1, column=1, columnspan=3, sticky="we", padx=8, pady=8)

        # Start en eind tijd
        tk.Label(frame, text="Starttijd (HH:MM):", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w")
        self.start_entry = tk.Entry(frame, width=12, font=("Arial", 11))
        self.start_entry.grid(row=2, column=1, sticky="w", padx=8)

        tk.Label(frame, text="Eindtijd (HH:MM):", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=2, column=2, sticky="w")
        self.eind_entry = tk.Entry(frame, width=12, font=("Arial", 11))
        self.eind_entry.grid(row=2, column=3, sticky="w", padx=8)

        # Prijs
        tk.Label(frame, text="Prijs (€):", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.prijs_entry = tk.Entry(frame, width=12, font=("Arial", 11))
        self.prijs_entry.grid(row=3, column=1, sticky="w", padx=8, pady=8)

        # Extra opties (checkbuttons), standaard weggehaald
        self.grondzeil_cb = tk.Checkbutton(frame, text="Grondzeil nodig", variable=self.grondzeil_var,
                                           bg="#333333", fg="white", selectcolor="#444444", font=("Arial", 10))
        self.valmatten_cb = tk.Checkbutton(frame, text="Valmatten nodig", variable=self.valmatten_var,
                                           bg="#333333", fg="white", selectcolor="#444444", font=("Arial", 10))
        self.zandzakken_cb = tk.Checkbutton(frame, text="Zandzakken nodig", variable=self.zandzakken_var,
                                            bg="#333333", fg="white", selectcolor="#444444", font=("Arial", 10))

        # Opmerkingen label en tekstvak (multiline)
        tk.Label(frame, text="Opmerkingen:", bg="#333333", fg="white", font=("Arial", 11, "bold")).grid(row=5, column=0, sticky="nw", pady=8)
        self.opmerkingen_text = tk.Text(frame, width=40, height=4, font=("Arial", 10))
        self.opmerkingen_text.grid(row=5, column=1, columnspan=3, sticky="we", padx=8, pady=8)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#222222")
        btn_frame.pack(pady=12)

        self.add_button = tk.Button(btn_frame, text="Activiteit toevoegen", bg=self.lp_geel, fg="black",
                                    font=("Arial", 12, "bold"), width=18, command=self.add_activity)
        self.add_button.grid(row=0, column=0, padx=10)

        self.remove_button = tk.Button(btn_frame, text="Geselecteerde verwijderen", bg="#FF5555", fg="white",
                                       font=("Arial", 12, "bold"), width=22, command=self.remove_activity)
        self.remove_button.grid(row=0, column=1, padx=10)

        self.export_button = tk.Button(btn_frame, text="Exporteren naar PDF", bg=self.lp_geel, fg="black",
                                       font=("Arial", 12, "bold"), width=18, command=self.export_pdf)
        self.export_button.grid(row=0, column=2, padx=10)

        # Treeview overzicht
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        columns = ("type", "keuze", "levering", "adres", "start", "eind", "extra", "opmerkingen", "prijs", "extra_boeking")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        headers = ["Type", "Keuze", "Leveren/Ophalen", "Adres", "Starttijd", "Eindtijd", "Extra", "Opmerkingen", "Prijs"]

        for col, hd in zip(columns, headers):
            self.tree.heading(col, text=hd)
            self.tree.column(col, minwidth=80, width=120, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_greeting(self):
        now = datetime.datetime.now()
        uur = now.hour
        if uur < 12:
            tekst = "Goedemorgen Tom"
        elif uur < 18:
            tekst = "Goedemiddag Tom"
        else:
            tekst = "Goedeavond Tom"
        self.greeting_label.config(text=f"{tekst}!")

    def update_keuze_options(self, event=None):
        t = self.type_var.get()

        # Verberg alle checkbuttons en radiobuttons
        self.grondzeil_cb.grid_remove()
        self.valmatten_cb.grid_remove()
        self.zandzakken_cb.grid_remove()
        self.lever_radio1.grid_remove()
        self.lever_radio2.grid_remove()
        self.roetzwart_var.set("Roetveeg")

        # Reset keuze combobox
        self.keuze_combo.config(state="normal")
        self.keuze_combo.set("")

        if t == "Springkasteel":
            opties = self.springkastelen
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set(self.springkastelen[0])
            self.grondzeil_cb.grid(row=3, column=2, sticky="w", padx=8)
            self.valmatten_cb.grid(row=3, column=3, sticky="w", padx=8)
            self.zandzakken_cb.grid(row=4, column=2, sticky="w", padx=8)
            self.levering_var.set("Leveren")
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)

        elif t == "Partytent":
            opties = self.partytenten
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set(self.partytenten[0])
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)


        elif t == "Lasergame":
            opties = self.lasergames
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set(self.lasergames[0])
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)

        elif t == "Sint & Piet":
            opties = ["Roetveeg", "Volledig zwart"]
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set("Roetveeg")
            self.lever_radio1.grid_remove()
            self.lever_radio2.grid_remove()
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)

        elif t == "Muntenschuiver":
            opties = ["Muntenschuiver"]
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set("Muntenschuiver")
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)

        elif t == "Popcornmachine":
            opties = ["Popcornmachine"]
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set("Popcornmachine")
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)

        elif t == "Stroomgenerator":
            opties = ["Stroomgenerator"]
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set("Stroomgenerator")
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)
            
        elif t == "Pauze":
            opties = ["Pauze"]
            self.keuze_combo.config(values=opties)
            self.keuze_combo.set("Pauze")
            self.lever_radio1.grid(row=1, column=2, sticky="w", padx=8)
            self.lever_radio2.grid(row=1, column=3, sticky="w", padx=8)
            self.grondzeil_var.set(False)
            self.valmatten_var.set(False)
            self.zandzakken_var.set(False)
            

        else:
            self.keuze_combo.config(values=[])
            self.keuze_combo.set("")

        self.update_lever_haal_adres()

    def update_lever_haal_adres(self):
        # Stel adres in standaardadres bij ophalen, en maak leeg bij leveren
        if self.levering_var.get() == "Ophalen":
            self.adres_entry.delete(0, tk.END)
            self.adres_entry.insert(0, self.default_adres)
        else:
            self.adres_entry.delete(0, tk.END)

    def add_activity(self):
        # Validaties
        t = self.type_var.get()
        k = self.keuze_var.get()
        levering = self.levering_var.get()
        adres = self.adres_entry.get().strip()
        start = self.start_entry.get().strip()
        eind = self.eind_entry.get().strip()
        prijs = self.prijs_entry.get().strip()
        opmerkingen = self.opmerkingen_text.get("1.0", "end").strip()
        
                # Bij pauze geen tijden of prijs nodig, direct toevoegen
        if k == "Pauze":
            # start = ""
            # eind = ""
            prijs = ""
            levering = ""

        if not t:
            messagebox.showerror("Fout", "Selecteer het type activiteit.")
            return
        if not k:
            messagebox.showerror("Fout", "Selecteer de keuze.")
            return
        if levering == "Leveren" and not adres:
            messagebox.showerror("Fout", "Vul het afleveradres in.")
            return
        if levering == "Ophalen" and not adres:
            # Bij ophalen wordt standaardadres ingevuld, maar check even
            adres = self.default_adres



        # Basis validatie tijden (optioneel, hier kan uitgebreid)
        if start and not self.is_valid_time(start):
            messagebox.showerror("Fout", "Starttijd is ongeldig, gebruik HH:MM.")
            return
        if eind and not self.is_valid_time(eind):
            messagebox.showerror("Fout", "Eindtijd is ongeldig, gebruik HH:MM.")
            return

        # Extra opties
        extra_opts = []
        if self.grondzeil_var.get():
            extra_opts.append("Grondzeil")
        if self.valmatten_var.get():
            extra_opts.append("Valmatten")
        if self.zandzakken_var.get():
            extra_opts.append("Zandzakken")

        self.activities.append({
            "type": t,
            "keuze": k,
            "levering": levering,
            "adres": adres,
            "start": start,
            "eind": eind,
            "extra": ", ".join(extra_opts),
            "opmerkingen": opmerkingen,
            "prijs": prijs,
        })

        self.refresh_tree()
        self.clear_inputs()

    def is_valid_time(self, tijd):
        try:
            datetime.datetime.strptime(tijd, "%H:%M")
            return True
        except ValueError:
            return False

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for act in self.activities:
            self.tree.insert("", tk.END, values=(
                act["type"], act["keuze"], act["levering"], act["adres"], act["start"], act["eind"],
                act["extra"], act["opmerkingen"], act["prijs"]))

    def clear_inputs(self):
        self.type_combo.set("")
        self.keuze_combo.set("")
        self.levering_var.set("Leveren")
        self.adres_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.eind_entry.delete(0, tk.END)
        self.prijs_entry.delete(0, tk.END)
        self.grondzeil_var.set(False)
        self.valmatten_var.set(False)
        self.zandzakken_var.set(False)
        self.opmerkingen_text.delete("1.0", tk.END)

    def remove_activity(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Waarschuwing", "Selecteer een activiteit om te verwijderen.")
            return
        index = self.tree.index(sel[0])
        del self.activities[index]
        self.refresh_tree()

    def export_pdf(self):
        if not self.activities:
            messagebox.showwarning("Waarschuwing", "Er zijn geen activiteiten om te exporteren.")
            return
            
        styles = getSampleStyleSheet()
        style_title = styles["Heading1"]
        style_table_header = styles["Heading4"]
        style_normal = styles["Normal"]
        
        
        datum = datetime.datetime.now().strftime("%d-%m-%Y")
        titel = Paragraph(f"Loois Plezier Planning - {datum}", style_title)
        elements = []
        elements.append(titel)
        elements.append(Spacer(1, 12))
        
        
        file_name = "LooisPlezier_Planning_" + datum + ".pdf"
        doc = SimpleDocTemplate(file_name, pagesize=landscape(A4))




       

        # Tabellenkop
        data = [["Type", "Keuze", "Leveren/Ophalen", "Adres", "Starttijd", "Eindtijd", "Extra", "Opmerkingen", "Prijs (€)"]]

        for act in self.activities:
            # data.append([
                # act["type"], act["keuze"], act["levering"], act["adres"], act["start"], act["eind"],
                # act["extra"], act["opmerkingen"], act["prijs"]
                # Zorg voor een stijl met kleinere tekst en automatische afbreking
                wrap_style = ParagraphStyle(name='Wrap', fontSize=10, leading=12)

                data.append([
    Paragraph(act["type"], wrap_style),
    Paragraph(act["keuze"], wrap_style),
    Paragraph(act["levering"], wrap_style),
    Paragraph(act["adres"], wrap_style),
    Paragraph(act["start"], wrap_style),
    Paragraph(act["eind"], wrap_style),
    Paragraph(act["extra"], wrap_style),
    Paragraph(act["opmerkingen"], wrap_style),
    Paragraph(str(act["prijs"]), wrap_style),
            ])

        table = Table(data, repeatRows=1, hAlign='LEFT')
        tbl_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.lp_geel)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ])
        table.setStyle(tbl_style)
        elements.append(table)

        try:
            doc.build(elements)
            messagebox.showinfo("Succes", f"Planning succesvol geëxporteerd naar {file_name}")
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij exporteren PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LooisPlezierApp(root)
    root.mainloop()
