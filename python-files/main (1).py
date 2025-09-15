
from decimal import Decimal, ROUND_HALF_UP, getcontext
import json
import datetime

getcontext().prec = 28

STAMP_DUTY = Decimal('1.00')

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title('TuniFact - Facturation simple')
        self.invoice_lines = []
        self.tva_rate = Decimal('0.00')
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky='nsew')

        # Client info
        client_frame = ttk.LabelFrame(frm, text='Client')
        client_frame.grid(row=0, column=0, sticky='ew')
        ttk.Label(client_frame, text='Nom:').grid(row=0, column=0)
        self.client_name = ttk.Entry(client_frame, width=40)
        self.client_name.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(client_frame, text='Code TVA:').grid(row=1, column=0)
        self.client_tva = ttk.Entry(client_frame, width=40)
        self.client_tva.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(client_frame, text='Adresse:').grid(row=2, column=0)
        self.client_addr = ttk.Entry(client_frame, width=40)
        self.client_addr.grid(row=2, column=1, padx=5, pady=2)

        # Item entry
        item_frame = ttk.LabelFrame(frm, text='Ajouter article')
        item_frame.grid(row=1, column=0, sticky='ew', pady=8)
        ttk.Label(item_frame, text='Article:').grid(row=0, column=0)
        self.item_name = ttk.Entry(item_frame)
        self.item_name.grid(row=0, column=1)
        ttk.Label(item_frame, text='Prix Unitaire (TND):').grid(row=0, column=2)
        self.item_price = ttk.Entry(item_frame)
        self.item_price.grid(row=0, column=3)
        ttk.Label(item_frame, text='Quantité:').grid(row=0, column=4)
        self.item_qty = ttk.Entry(item_frame, width=6)
        self.item_qty.grid(row=0, column=5)
        ttk.Button(item_frame, text='Ajouter', command=self.add_line).grid(row=0, column=6, padx=5)

        # Lines list
        cols = ('Article', 'PU', 'Qte', 'Total')
        self.tree = ttk.Treeview(frm, columns=cols, show='headings', height=8)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.grid(row=2, column=0, sticky='nsew')

        # TVA + stamp
        options = ttk.LabelFrame(frm, text='Options facture')
        options.grid(row=3, column=0, sticky='ew', pady=8)
        ttk.Label(options, text='TVA:').grid(row=0, column=0)
        self.tva_combo = ttk.Combobox(options, values=['0%', '7%', '19%'], width=6, state='readonly')
        self.tva_combo.current(1)
        self.tva_combo.grid(row=0, column=1)
        self.tva_combo.bind('<<ComboboxSelected>>', lambda e: self.update_totals())
        self.stamp_var = BooleanVar(value=True)
        ttk.Checkbutton(options, text=f'Timbre ({STAMP_DUTY} TND)', variable=self.stamp_var, command=self.update_totals).grid(row=0, column=2, padx=10)

        # Totals + actions
        bottom = ttk.Frame(frm)
        bottom.grid(row=4, column=0, sticky='ew')
        self.subtotal_var = StringVar(value='0.00')
        self.tva_amount_var = StringVar(value='0.00')
        self.total_var = StringVar(value='0.00')
        ttk.Label(bottom, text='Sous-total:').grid(row=0, column=0)
        ttk.Label(bottom, textvariable=self.subtotal_var).grid(row=0, column=1)
        ttk.Label(bottom, text='TVA montant:').grid(row=0, column=2)
        ttk.Label(bottom, textvariable=self.tva_amount_var).grid(row=0, column=3)
        ttk.Label(bottom, text='Total:').grid(row=0, column=4)
        ttk.Label(bottom, textvariable=self.total_var).grid(row=0, column=5)

        action_frame = ttk.Frame(frm)
        action_frame.grid(row=5, column=0, sticky='ew', pady=8)
        ttk.Button(action_frame, text='Enregistrer facture (sauver)', command=self.save_invoice).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text='Créer Bon de livraison', command=lambda: self.create_bon('Livraison')).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text='Créer Bon de sortie', command=lambda: self.create_bon('Sortie')).grid(row=0, column=2, padx=5)
        ttk.Button(action_frame, text='Nouveau', command=self.reset_all).grid(row=0, column=3, padx=5)

        # Make grid expand
        self.root.columnconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)
        self.update_totals()

    def add_line(self):
        name = self.item_name.get().strip()
        price_s = self.item_price.get().strip()
        qty_s = self.item_qty.get().strip()
        if not name:
            messagebox.showwarning('Erreur', 'Entrer le nom de l\'article')
            return
        try:
            # compute with Decimal carefully digit by digit
            price = Decimal(price_s).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            qty = Decimal(qty_s).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        except Exception:
            messagebox.showwarning('Erreur', 'Prix ou quantité non valides')
            return
        line_total = (price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.invoice_lines.append({'name': name, 'price': str(price), 'qty': str(qty), 'total': str(line_total)})
        self.tree.insert('', 'end', values=(name, f'{price}', f'{qty}', f'{line_total}'))
        self.item_name.delete(0, END); self.item_price.delete(0, END); self.item_qty.delete(0, END)
        self.update_totals()

    def compute_subtotal(self):
        total = Decimal('0.00')
        for ln in self.invoice_lines:
            total += Decimal(ln['total'])
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def update_totals(self):
        sub = self.compute_subtotal()
        tva_text = self.tva_combo.get() if hasattr(self, 'tva_combo') else '0%'
        if tva_text.endswith('%'):
            rate = Decimal(tva_text[:-1]) / Decimal('100')
        else:
            rate = Decimal('0.00')
        tva_amount = (sub * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = sub + tva_amount
        if self.stamp_var.get():
            total += STAMP_DUTY
        # save
        self.subtotal_var.set(f'{sub}')
        self.tva_amount_var.set(f'{tva_amount}')
        self.total_var.set(f'{total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)}')

    def gather_invoice_data(self):
        data = {
            'date': datetime.datetime.now().isoformat(),
            'client': {
                'name': self.client_name.get().strip(),
                'tva': self.client_tva.get().strip(),
                'address': self.client_addr.get().strip()
            },
            'lines': self.invoice_lines,
            'subtotal': str(self.compute_subtotal()),
            'tva_rate': self.tva_combo.get(),
            'tva_amount': self.tva_amount_var.get(),
            'stamp': str(STAMP_DUTY) if self.stamp_var.get() else '0.00',
            'total': self.total_var.get()
        }
        return data

    def save_invoice(self):
        data = self.gather_invoice_data()
        if not data['client']['name']:
            messagebox.showwarning('Erreur', 'Entrer les informations du client')
            return
        fn = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')], title='Sauver facture')
        if not fn:
            return
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo('OK', f'Facture sauvée: {fn}')

    def create_bon(self, bon_type):
        # require driver + plate before finalizing
        if not self.invoice_lines:
            messagebox.showwarning('Erreur', 'Aucune ligne dans la facture')
            return
        driver = simpledialog.askstring('Chauffeur', "Entrer nom du chauffeur (obligatoire) :")
        if not driver:
            messagebox.showwarning('Erreur', 'Nom du chauffeur requis')
            return
        plate = simpledialog.askstring('Matricule', "Entrer matricule du véhicule (obligatoire) :")
        if not plate:
            messagebox.showwarning('Erreur', 'Matricule requis')
            return
        # create a simple textual bon
        data = self.gather_invoice_data()
        lines_text = '\n'.join([f"- {l['name']} | PU {l['price']} | Qte {l['qty']} | Total {l['total']}" for l in data['lines']])
        content = f"Bon: {bon_type}\nDate: {datetime.datetime.now().isoformat()}\nClient: {data['client']['name']}\nTVA: {data['tva_rate']} | Timbre: {data['stamp']} TND\nDriver: {driver} | Vehicule: {plate}\n\nLignes:\n{lines_text}\n\nSous-total: {data['subtotal']} TND\nTVA: {data['tva_amount']} TND\nTotal: {data['total']} TND\n"
        fn = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files','*.txt')], title=f'Sauver {bon_type}')
        if not fn:
            return
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo('OK', f'{bon_type} sauvé: {fn}')

    def reset_all(self):
        if messagebox.askyesno('Confirmer', 'Voulez-vous réinitialiser la facture?'):
            self.invoice_lines = []
            for i in self.tree.get_children():
                self.tree.delete(i)
            self.client_name.delete(0, END); self.client_tva.delete(0, END); self.client_addr.delete(0, END)
            self.update_totals()


