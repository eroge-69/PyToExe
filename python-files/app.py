import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from fpdf import FPDF
import json
import os
import time

# --- CLASSE PER LA GESTIONE DEI DATI ---
class DataManager:
    def __init__(self, filename="fatture_data.json"):
        self.filename = filename
    def load_data(self):
        default_data = {"aziende": [], "clienti": [], "prodotti": [], "fatture": []}
        if not os.path.exists(self.filename): return default_data
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in default_data: data.setdefault(key, [])
                return data
        except (json.JSONDecodeError, FileNotFoundError): return default_data
    def save_data(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

# --- CLASSE PER LA GENERAZIONE DEL PDF ---
class PdfGenerator(FPDF):
    def __init__(self, azienda, cliente, fattura):
        super().__init__()
        self.azienda, self.cliente, self.fattura = azienda, cliente, fattura
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # --- BLOCCO 1: AZIENDA (LOGO + DATI) ---
        logo_path = self.azienda.get('logo_path', '')
        has_logo = logo_path and os.path.exists(logo_path)
        
        x_text = 65 if has_logo else 10
        if has_logo: self.image(logo_path, x=10, y=10, w=50)
        
        self.set_xy(x_text, 12)
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 8, self.azienda['ragione_sociale'], 0, 1)
        
        self.set_x(x_text); self.set_font('Helvetica', '', 9)
        self.cell(0, 5, self.azienda.get('indirizzo', ''), 0, 1)
        self.set_x(x_text); self.cell(0, 5, f"P.IVA: {self.azienda.get('p_iva', '')}", 0, 1)
        if self.azienda.get('email'): self.set_x(x_text); self.cell(0, 5, f"Email: {self.azienda.get('email')}", 0, 1)
        if self.azienda.get('telefono'): self.set_x(x_text); self.cell(0, 5, f"Tel: {self.azienda.get('telefono')}", 0, 1)
        if self.azienda.get('sito_web'): self.set_x(x_text); self.cell(0, 5, f"Web: {self.azienda.get('sito_web')}", 0, 1)
        
        # --- LINEA DI SEPARAZIONE E SPAZIO SOTTO ---
        self.ln(5) # Aggiunge uno spazio tra i dati azienda e la linea
        y_line = self.get_y()
        self.line(10, y_line, 200, y_line)
        self.ln(8) # Spazio dopo la linea

        # --- BLOCCO 2: DATI FATTURA E CLIENTE ---
        y_start_block2 = self.get_y()
        
        # Dati Fattura a Sinistra
        self.set_font('Helvetica', 'B', 12); self.cell(95, 7, f"FATTURA N. {self.fattura['numero']}", 0, 1, 'L')
        self.set_font('Helvetica', '', 11); self.cell(95, 7, f"Data: {self.fattura['data']}", 0, 1, 'L')

        # Dati Cliente a Destra
        self.set_y(y_start_block2) # Riporta la Y all'inizio del blocco
        self.set_x(110)
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, 'Spett.le', 0, 1, 'L')
        self.set_x(110); self.set_font('Helvetica', '', 10)
        self.cell(0, 5, self.cliente.get('nome_cognome', ''), 0, 1, 'L')
        self.set_x(110); self.cell(0, 5, self.cliente.get('indirizzo', ''), 0, 1, 'L')
        self.set_x(110); self.cell(0, 5, f"Codice Fiscale: {self.cliente.get('codice_fiscale', '')}", 0, 1, 'L')
        if self.cliente.get('telefono'):
            self.set_x(110); self.cell(0, 5, f"Tel: {self.cliente.get('telefono')}", 0, 1, 'L')

        self.ln(15)

    def footer(self):
        self.set_y(-15); self.set_font('Helvetica', 'I', 8); self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def create_invoice_body(self):
        self.set_font('Helvetica', 'B', 10); self.set_fill_color(220, 220, 220)
        self.cell(100, 8, 'Descrizione', 1, 0, 'C', 1); self.cell(20, 8, 'Q.ta', 1, 0, 'C', 1)
        self.cell(30, 8, 'Prezzo Unit.', 1, 0, 'C', 1); self.cell(15, 8, 'IVA %', 1, 0, 'C', 1)
        self.cell(25, 8, 'Totale', 1, 1, 'C', 1)
        self.set_font('Helvetica', '', 10)
        imponibile = totale_iva = 0
        for item in self.fattura.get('righe', []):
            qta, prezzo, iva_perc = int(item.get('qta', 1)), float(item.get('prezzo', 0)), float(item.get('iva', 0))
            totale_riga = qta * prezzo; imponibile += totale_riga; totale_iva += totale_riga * (iva_perc / 100)
            y1 = self.get_y()
            self.multi_cell(100, 8, item.get('desc', ''), 1, 'L'); 
            h = self.get_y() - y1
            self.set_xy(110, y1)
            self.cell(20, h, str(qta), 1, 0, 'C'); self.cell(30, h, f"{prezzo:.2f} EUR", 1, 0, 'R')
            self.cell(15, h, str(iva_perc), 1, 0, 'C'); self.cell(25, h, f"{totale_riga:.2f} EUR", 1, 1, 'R')
        
        note = self.fattura.get('note', '').strip()
        if note:
            self.ln(5); self.set_font('Helvetica', 'B', 9); self.cell(0, 5, "Note:", 0, 1)
            self.set_font('Helvetica', '', 9); self.multi_cell(0, 5, note, border=1, align='L')
            
        y_before_totals = self.get_y()
        if y_before_totals < 220: self.set_y(220)
        else: self.ln(10)
        
        spedizione = float(self.fattura.get('spedizione', "0.00").replace(',', '.')); totale_fattura = imponibile + totale_iva + spedizione
        self.set_font('Helvetica', 'B', 10); self.set_x(110); self.set_fill_color(245, 245, 245)
        self.multi_cell(90, 8, f"Imponibile: {imponibile:.2f} EUR\n"
                                f"Totale IVA: {totale_iva:.2f} EUR\n"
                                f"Spedizione: {spedizione:.2f} EUR\n"
                                f"TOTALE: {totale_fattura:.2f} EUR",
                        border=1, align='R', fill=True)

# --- DIALOGHI ---
class GenericDialog(ttk.Toplevel):
    def __init__(self, parent, title, fields, data=None):
        super().__init__(title=title); self.transient(parent)
        self.result = None; self.entries = {}
        row_counter = 0
        for key, label in fields.items():
            ttk.Label(self, text=label).grid(row=row_counter, column=0, padx=10, pady=5, sticky='w')
            if key == 'logo_path':
                entry_frame = ttk.Frame(self); entry_frame.grid(row=row_counter, column=1, padx=10, pady=5, sticky='ew')
                entry = ttk.Entry(entry_frame, width=30); entry.pack(side=LEFT, fill=X, expand=True)
                ttk.Button(entry_frame, text="...", command=lambda e=entry: self.browse_logo(e)).pack(side=LEFT, padx=5)
            else: entry = ttk.Entry(self, width=40); entry.grid(row=row_counter, column=1, padx=10, pady=5, sticky='ew')
            if data: entry.insert(0, data.get(key, ''))
            self.entries[key] = entry; row_counter += 1
        btn_frame = ttk.Frame(self); btn_frame.grid(row=row_counter, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Salva", command=self.on_save, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy, bootstyle=DANGER).pack(side=LEFT, padx=5)
        self.wait_window(self)
    def browse_logo(self, entry_widget):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath: entry_widget.delete(0, END); entry_widget.insert(0, filepath)
    def on_save(self): self.result = {key: entry.get() for key, entry in self.entries.items()}; self.destroy()

class InvoiceDialog(ttk.Toplevel):
    def __init__(self, parent, aziende, clienti, prodotti, data=None):
        super().__init__(title="Crea/Modifica Fattura")
        self.transient(parent); self.geometry("850x700"); self.result = None
        self.aziende, self.clienti, self.prodotti = aziende, clienti, prodotti
        self.righe = data.get('righe', [])[:] if data else []
        main_frame = ttk.Frame(self); main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        main_frame.rowconfigure(1, weight=1); main_frame.columnconfigure(0, weight=1)
        header_frame = ttk.Labelframe(main_frame, text="Intestazione", padding=10); header_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        ttk.Label(header_frame, text="Azienda:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.azienda_combo = ttk.Combobox(header_frame, values=[a['ragione_sociale'] for a in aziende], state="readonly"); self.azienda_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(header_frame, text="Cliente:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.cliente_combo = ttk.Combobox(header_frame, values=[c['nome_cognome'] for c in clienti], state="readonly"); self.cliente_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(header_frame, text="Numero Fattura:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.numero_entry = ttk.Entry(header_frame); self.numero_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        ttk.Label(header_frame, text="Data Fattura:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.data_entry = ttk.DateEntry(header_frame, bootstyle=PRIMARY, dateformat="%d/%m/%Y"); self.data_entry.grid(row=1, column=3, padx=5, pady=5, sticky='ew')
        header_frame.grid_columnconfigure(1, weight=1); header_frame.grid_columnconfigure(3, weight=1)
        rows_frame = ttk.Labelframe(main_frame, text="Righe (doppio click per modificare)", padding=10); rows_frame.grid(row=1, column=0, sticky='nsew')
        cols = ('desc', 'qta', 'prezzo', 'iva'); self.righe_tree = ttk.Treeview(rows_frame, columns=cols, show='headings')
        for col in cols: self.righe_tree.heading(col, text=col.replace('_', ' ').title()); self.righe_tree.column(col, width=100)
        self.righe_tree.column('desc', width=300); self.righe_tree.pack(fill=BOTH, expand=True)
        # --- MODIFICA INIZIO: BINDING DOPPIO CLICK ---
        self.righe_tree.bind("<Double-1>", self.on_riga_double_click)
        # --- MODIFICA FINE ---
        righe_btn_frame = ttk.Frame(main_frame); righe_btn_frame.grid(row=1, column=1, sticky='ns', padx=5)
        ttk.Button(righe_btn_frame, text="Aggiungi Riga", command=self.add_riga).pack(pady=5, fill=X)
        ttk.Button(righe_btn_frame, text="Da Lista", command=self.add_prodotto_da_lista, bootstyle=INFO).pack(pady=5, fill=X)
        # --- MODIFICA INIZIO: AGGIUNTA PULSANTE MODIFICA RIGA ---
        ttk.Button(righe_btn_frame, text="Modifica Riga", command=self.edit_riga, bootstyle="outline").pack(pady=5, fill=X)
        # --- MODIFICA FINE ---
        ttk.Button(righe_btn_frame, text="Elimina Riga", command=self.delete_riga, bootstyle=DANGER).pack(pady=5, fill=X)
        notes_frame = ttk.Labelframe(main_frame, text="Note", padding=10); notes_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        self.note_text = ttk.Text(notes_frame, height=4); self.note_text.pack(fill=X, expand=True)
        footer_frame = ttk.Frame(main_frame, padding=10); footer_frame.grid(row=3, column=0, columnspan=2, sticky='ew')
        ttk.Label(footer_frame, text="Spedizione (€):").pack(side=LEFT, padx=5)
        self.spedizione_entry = ttk.Entry(footer_frame, width=10); self.spedizione_entry.insert(0, "0.00"); self.spedizione_entry.pack(side=LEFT, padx=5)
        self.totali_label = ttk.Label(footer_frame, text="TOTALE: 0.00 EUR", font="-weight bold"); self.totali_label.pack(side=LEFT, padx=20)
        ttk.Button(footer_frame, text="Salva e Genera PDF", command=self.on_generate, bootstyle=SUCCESS).pack(side=RIGHT, padx=5)
        ttk.Button(footer_frame, text="Aggiorna Totali", command=self.update_totals, bootstyle=INFO).pack(side=RIGHT, padx=5)
        if data: self.load_invoice_data(data)
        self.refresh_righe_list(); self.update_totals()
        self.wait_window(self)
    def load_invoice_data(self, data):
        self.numero_entry.insert(0, data.get('numero', '')); self.data_entry.entry.delete(0, END); self.data_entry.entry.insert(0, data.get('data', ''))
        self.spedizione_entry.delete(0, END); self.spedizione_entry.insert(0, data.get('spedizione', '0.00')); self.note_text.insert("1.0", data.get('note', ''))
        azienda_idx = next((i for i, a in enumerate(self.aziende) if a['ragione_sociale'] == data['azienda_nome']), -1)
        if azienda_idx != -1: self.azienda_combo.current(azienda_idx)
        cliente_idx = next((i for i, c in enumerate(self.clienti) if c['nome_cognome'] == data['cliente_nome']), -1)
        if cliente_idx != -1: self.cliente_combo.current(cliente_idx)
    def add_riga(self):
        fields = {'desc': 'Descrizione', 'qta': 'Quantità', 'prezzo': 'Prezzo Unitario', 'iva': 'IVA %'}
        dialog = GenericDialog(self, "Aggiungi Riga", fields, data={'iva': '22'})
        if dialog.result: self.righe.append(dialog.result); self.refresh_righe_list(); self.update_totals()
        
    # --- MODIFICA INIZIO: NUOVA FUNZIONE PER MODIFICARE RIGA ---
    def edit_riga(self):
        if not self.righe_tree.focus():
            messagebox.showwarning("Attenzione", "Seleziona una riga da modificare.")
            return
        
        index = int(self.righe_tree.focus())
        riga_data = self.righe[index]

        fields = {'desc': 'Descrizione', 'qta': 'Quantità', 'prezzo': 'Prezzo Unitario', 'iva': 'IVA %'}
        dialog = GenericDialog(self, "Modifica Riga", fields, data=riga_data)
        
        if dialog.result:
            self.righe[index] = dialog.result
            self.refresh_righe_list()
            self.update_totals()

    def on_riga_double_click(self, event):
        # Controlla che il click sia avvenuto su una cella valida
        region = self.righe_tree.identify_region(event.x, event.y)
        if region == "cell":
            self.edit_riga()
    # --- MODIFICA FINE ---

    def add_prodotto_da_lista(self):
        if not self.prodotti: messagebox.showinfo("Info", "Nessun prodotto predefinito."); return
        win = ttk.Toplevel(title="Scegli Prodotto"); win.transient(self)
        listbox = ttk.Treeview(win, columns=('desc', 'prezzo'), show='headings'); listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)
        listbox.heading('desc', text='Descrizione'); listbox.heading('prezzo', text='Prezzo')
        for prod in self.prodotti: listbox.insert('', END, values=(prod['desc'], prod['prezzo']))
        def on_select():
            if not listbox.focus(): return
            selected_values = listbox.item(listbox.focus())['values']
            prodotto = next((p for p in self.prodotti if p['desc'] == selected_values[0] and str(p['prezzo']) == str(selected_values[1])), None)
            if prodotto: self.righe.append(prodotto.copy()); self.refresh_righe_list(); self.update_totals()
            win.destroy()
        ttk.Button(win, text="Seleziona", command=on_select, bootstyle=SUCCESS).pack(pady=10)
    def delete_riga(self):
        if not self.righe_tree.focus(): return
        self.righe.pop(int(self.righe_tree.focus())); self.refresh_righe_list(); self.update_totals()
    def refresh_righe_list(self):
        for i in self.righe_tree.get_children(): self.righe_tree.delete(i)
        for i, riga in enumerate(self.righe): self.righe_tree.insert('', END, iid=i, values=(riga['desc'], riga['qta'], riga['prezzo'], riga['iva']))
    def update_totals(self):
        try:
            imponibile = totale_iva = 0
            for riga in self.righe:
                totale_riga = int(riga.get('qta', 0)) * float(riga.get('prezzo', 0))
                imponibile += totale_riga; totale_iva += totale_riga * (float(riga.get('iva', 0)) / 100)
            spedizione = float(self.spedizione_entry.get().replace(',', '.') or 0)
            totale_fattura = imponibile + totale_iva + spedizione
            self.totali_label.config(text=f"Imponibile: {imponibile:.2f} | IVA: {totale_iva:.2f} | TOTALE: {totale_fattura:.2f} EUR")
        except (ValueError, KeyError): self.totali_label.config(text="Errore nei dati")
    def on_generate(self):
        if self.azienda_combo.current() == -1 or self.cliente_combo.current() == -1: messagebox.showerror("Errore", "Seleziona un'azienda e un cliente."); return
        if not self.numero_entry.get(): messagebox.showerror("Errore", "Inserisci un numero di fattura."); return
        if not self.righe: messagebox.showerror("Errore", "Aggiungi almeno una riga."); return
        self.update_totals()
        self.result = {"azienda": self.aziende[self.azienda_combo.current()], "cliente": self.clienti[self.cliente_combo.current()],
            "fattura_details": {"numero": self.numero_entry.get(), "data": self.data_entry.entry.get(), "spedizione": self.spedizione_entry.get(), "righe": self.righe, "note": self.note_text.get("1.0", 'end-1c')}}
        self.destroy()

# --- APPLICAZIONE PRINCIPALE ---
class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("FatturaPro Python Edition"); self.geometry("900x600")
        self.data_manager = DataManager(); self.data = self.data_manager.load_data()
        self.notebook = ttk.Notebook(self); self.notebook.pack(expand=True, fill=BOTH, padx=10, pady=10)
        self.create_fatture_tab(self.notebook); self.create_aziende_tab(self.notebook); self.create_clienti_tab(self.notebook); self.create_prodotti_tab(self.notebook)

    def create_tab_frame(self, parent, text):
        frame = ttk.Frame(parent); parent.add(frame, text=text)
        btn_frame = ttk.Frame(frame); btn_frame.pack(fill=X, padx=5, pady=5)
        tree_frame = ttk.Frame(frame); tree_frame.pack(expand=True, fill=BOTH, padx=5, pady=5)
        return tree_frame, btn_frame
    def create_aziende_tab(self, parent):
        tree_frame, btn_frame = self.create_tab_frame(parent, " Anagrafica Aziende ")
        cols = ('ragione_sociale', 'p_iva', 'email'); self.aziende_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols: self.aziende_tree.heading(col, text=col.replace('_', ' ').title())
        self.aziende_tree.pack(expand=True, fill=BOTH)
        ttk.Button(btn_frame, text="Aggiungi", command=self.add_azienda).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Modifica", command=self.edit_azienda).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Elimina", command=self.delete_azienda, bootstyle=DANGER).pack(side=LEFT, padx=5)
        self.refresh_aziende_list()
    def refresh_aziende_list(self):
        for i in self.aziende_tree.get_children(): self.aziende_tree.delete(i)
        for i, azienda in enumerate(self.data['aziende']): self.aziende_tree.insert('', END, iid=i, values=(azienda['ragione_sociale'], azienda['p_iva'], azienda['email']))
    def add_azienda(self):
        fields = {'ragione_sociale': "Ragione Sociale", 'p_iva': "Partita IVA", 'indirizzo': "Indirizzo", 'telefono': "Telefono", 'email': "Email", 'sito_web': "Sito Web", 'logo_path': "Percorso Logo"}
        dialog = GenericDialog(self, "Aggiungi Azienda", fields)
        if dialog.result: self.data['aziende'].append(dialog.result); self.data_manager.save_data(self.data); self.refresh_aziende_list()
    def edit_azienda(self):
        if not self.aziende_tree.focus(): return
        index = int(self.aziende_tree.focus())
        fields = {'ragione_sociale': "Ragione Sociale", 'p_iva': "Partita IVA", 'indirizzo': "Indirizzo", 'telefono': "Telefono", 'email': "Email", 'sito_web': "Sito Web", 'logo_path': "Percorso Logo"}
        dialog = GenericDialog(self, "Modifica Azienda", fields, data=self.data['aziende'][index])
        if dialog.result: self.data['aziende'][index] = dialog.result; self.data_manager.save_data(self.data); self.refresh_aziende_list()
    def delete_azienda(self):
        if not self.aziende_tree.focus(): return
        if messagebox.askyesno("Conferma", "Eliminare l'azienda selezionata?"):
            self.data['aziende'].pop(int(self.aziende_tree.focus())); self.data_manager.save_data(self.data); self.refresh_aziende_list()
    def create_clienti_tab(self, parent):
        tree_frame, btn_frame = self.create_tab_frame(parent, " Anagrafica Clienti ")
        cols = ('nome_cognome', 'codice_fiscale', 'email'); self.clienti_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols: self.clienti_tree.heading(col, text=col.replace('_', ' ').title())
        self.clienti_tree.pack(expand=True, fill=BOTH)
        ttk.Button(btn_frame, text="Aggiungi", command=self.add_cliente).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Modifica", command=self.edit_cliente).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Elimina", command=self.delete_cliente, bootstyle=DANGER).pack(side=LEFT, padx=5)
        self.refresh_clienti_list()
    def refresh_clienti_list(self):
        for i in self.clienti_tree.get_children(): self.clienti_tree.delete(i)
        for i, cliente in enumerate(self.data['clienti']): self.clienti_tree.insert('', END, iid=i, values=(cliente['nome_cognome'], cliente['codice_fiscale'], cliente['email']))
    def add_cliente(self):
        fields = {'nome_cognome': "Nome e Cognome", 'codice_fiscale': "Codice Fiscale", 'indirizzo': "Indirizzo", 'email': "Email", 'telefono': "Telefono"}
        dialog = GenericDialog(self, "Aggiungi Cliente", fields)
        if dialog.result: self.data['clienti'].append(dialog.result); self.data_manager.save_data(self.data); self.refresh_clienti_list()
    def edit_cliente(self):
        if not self.clienti_tree.focus(): return
        index = int(self.clienti_tree.focus())
        fields = {'nome_cognome': "Nome e Cognome", 'codice_fiscale': "Codice Fiscale", 'indirizzo': "Indirizzo", 'email': "Email", 'telefono': "Telefono"}
        dialog = GenericDialog(self, "Modifica Cliente", fields, data=self.data['clienti'][index])
        if dialog.result: self.data['clienti'][index] = dialog.result; self.data_manager.save_data(self.data); self.refresh_clienti_list()
    def delete_cliente(self):
        if not self.clienti_tree.focus(): return
        if messagebox.askyesno("Conferma", "Eliminare il cliente selezionato?"):
            self.data['clienti'].pop(int(self.clienti_tree.focus())); self.data_manager.save_data(self.data); self.refresh_clienti_list()
    def create_prodotti_tab(self, parent):
        tree_frame, btn_frame = self.create_tab_frame(parent, " Prodotti/Servizi ")
        cols = ('desc', 'qta', 'prezzo', 'iva'); self.prodotti_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        self.prodotti_tree.heading('desc', text='Descrizione'); self.prodotti_tree.heading('qta', text='Q.tà Def.'); self.prodotti_tree.heading('prezzo', text='Prezzo Def.'); self.prodotti_tree.heading('iva', text='IVA % Def.')
        self.prodotti_tree.pack(expand=True, fill=BOTH)
        ttk.Button(btn_frame, text="Aggiungi", command=self.add_prodotto).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Modifica", command=self.edit_prodotto).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Elimina", command=self.delete_prodotto, bootstyle=DANGER).pack(side=LEFT, padx=5)
        self.refresh_prodotti_list()
    def refresh_prodotti_list(self):
        for i in self.prodotti_tree.get_children(): self.prodotti_tree.delete(i)
        for i, prod in enumerate(self.data['prodotti']): self.prodotti_tree.insert('', END, iid=i, values=(prod['desc'], prod['qta'], prod['prezzo'], prod['iva']))
    def add_prodotto(self):
        fields = {'desc': 'Descrizione', 'qta': 'Quantità', 'prezzo': 'Prezzo', 'iva': 'IVA %'}
        dialog = GenericDialog(self, "Aggiungi Prodotto", fields, data={'qta': 1, 'iva': 22})
        if dialog.result: self.data['prodotti'].append(dialog.result); self.data_manager.save_data(self.data); self.refresh_prodotti_list()
    def edit_prodotto(self):
        if not self.prodotti_tree.focus(): return
        index = int(self.prodotti_tree.focus())
        fields = {'desc': 'Descrizione', 'qta': 'Quantità', 'prezzo': 'Prezzo', 'iva': 'IVA %'}
        dialog = GenericDialog(self, "Modifica Prodotto", fields, data=self.data['prodotti'][index])
        if dialog.result: self.data['prodotti'][index] = dialog.result; self.data_manager.save_data(self.data); self.refresh_prodotti_list()
    def delete_prodotto(self):
        if not self.prodotti_tree.focus(): return
        if messagebox.askyesno("Conferma", "Eliminare il prodotto selezionato?"):
            self.data['prodotti'].pop(int(self.prodotti_tree.focus())); self.data_manager.save_data(self.data); self.refresh_prodotti_list()
    def create_fatture_tab(self, parent):
        tree_frame, btn_frame = self.create_tab_frame(parent, " Storico Fatture ")
        ttk.Button(btn_frame, text="Crea Nuova Fattura", command=self.create_invoice, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Modifica Selezionata", command=self.edit_invoice).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Elimina Selezionata", command=self.delete_invoice, bootstyle=DANGER).pack(side=LEFT, padx=5)
        search_frame = ttk.Frame(btn_frame); search_frame.pack(side=RIGHT, padx=5)
        self.search_entry = ttk.Entry(search_frame); self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", lambda event: self.search_invoices())
        ttk.Button(search_frame, text="Cerca", command=self.search_invoices).pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Pulisci", command=self.clear_search).pack(side=LEFT)
        cols = ('numero', 'data', 'cliente', 'azienda', 'totale'); self.fatture_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols: self.fatture_tree.heading(col, text=col.title())
        self.fatture_tree.pack(expand=True, fill=BOTH)
        self.refresh_fatture_list()
    def refresh_fatture_list(self, search_term=None):
        for i in self.fatture_tree.get_children(): self.fatture_tree.delete(i)
        fatture_da_visualizzare = self.data['fatture']
        if search_term:
            search_term = search_term.lower()
            fatture_da_visualizzare = [f for f in self.data['fatture'] if search_term in f.get('numero', '').lower() or search_term in f.get('cliente_nome', '').lower()]
        for fattura in fatture_da_visualizzare:
            totale = sum(int(r.get('qta',0))*float(r.get('prezzo',0))*(1+float(r.get('iva',0))/100) for r in fattura.get('righe',[])) + float(fattura.get('spedizione', "0.00").replace(',', '.'))
            self.fatture_tree.insert('', END, iid=fattura['id'], values=(fattura.get('numero', 'N/D'), fattura.get('data', 'N/D'), fattura.get('cliente_nome', 'N/D'), fattura.get('azienda_nome', 'N/D'), f"{totale:.2f} EUR"))
    def search_invoices(self): self.refresh_fatture_list(self.search_entry.get())
    def clear_search(self): self.search_entry.delete(0, END); self.refresh_fatture_list()
    def create_invoice(self, invoice_to_edit=None):
        if not self.data['aziende'] or not self.data['clienti']: messagebox.showerror("Errore", "Aggiungi almeno un'azienda e un cliente."); return
        dialog = InvoiceDialog(self, self.data['aziende'], self.data['clienti'], self.data.get('prodotti', []), data=invoice_to_edit)
        if dialog.result:
            azienda, cliente, fattura_data = dialog.result['azienda'], dialog.result['cliente'], dialog.result['fattura_details']
            filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Fattura_{fattura_data['numero']}_{cliente['nome_cognome'].replace(' ', '_')}.pdf")
            if not filepath: return
            try:
                pdf = PdfGenerator(azienda, cliente, fattura_data)
                pdf.add_page(); pdf.create_invoice_body(); pdf.output(filepath)
                messagebox.showinfo("Successo", f"Fattura salvata in:\n{filepath}")
                fattura_db_entry = {"id": invoice_to_edit['id'] if invoice_to_edit else int(time.time() * 1000), "azienda_nome": azienda['ragione_sociale'], "cliente_nome": cliente['nome_cognome'], **fattura_data}
                if invoice_to_edit:
                    idx_to_update = next((i for i, f in enumerate(self.data['fatture']) if f['id'] == invoice_to_edit['id']), -1)
                    if idx_to_update != -1: self.data['fatture'][idx_to_update] = fattura_db_entry
                else: self.data['fatture'].append(fattura_db_entry)
                self.data_manager.save_data(self.data); self.refresh_fatture_list()
            except Exception as e: messagebox.showerror("Errore PDF", f"Si è verificato un errore:\n{e}")
    def edit_invoice(self):
        if not self.fatture_tree.focus(): return
        fattura_da_modificare = next((f for f in self.data['fatture'] if f['id'] == int(self.fatture_tree.focus())), None)
        if fattura_da_modificare: self.create_invoice(invoice_to_edit=fattura_da_modificare)
    def delete_invoice(self):
        if not self.fatture_tree.focus(): return
        if messagebox.askyesno("Conferma", "Eliminare la fattura selezionata? L'operazione è irreversibile."):
            self.data['fatture'] = [f for f in self.data['fatture'] if f['id'] != int(self.fatture_tree.focus())]
            self.data_manager.save_data(self.data); self.refresh_fatture_list()

if __name__ == "__main__":
    app = App()
    app.mainloop()