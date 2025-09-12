#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StandFacile-mac — Gestionale semplice per stand / proloco (macOS friendly)
VERSIONE POTENZIATA CON NUOVE FEATURE (ESC/POS e Talloncini Multipli) E NUOVA GRAFICA (ttkbootstrap)
VERSIONE ULTERIORMENTE MODIFICATA CON FUNZIONE SCONTO E STAMPA TALLONCINI MULTIPLI

Funzioni principali:
- Listino prodotti interno modificabile, persistente e importabile via CSV.
- Carrello con quantità, totale aggiornato in tempo reale.
- Funzione Sconto (fisso o percentuale) applicabile al carrello.
- Scontrino: anteprima, salvataggio (TXT/HTML), stampa, esportazione PDF, template avanzato.
- Stampa termica ESC/POS per scontrini e talloncini multipli automatici.
- Gestione di 4 talloncini personalizzabili e stampabili manualmente (con scelta della quantità).
- Report di fine giornata e storico vendite completo e filtrabile.
- Backup automatico giornaliero e protezione con password.
- Interfaccia grafica moderna con temi.
- Tastierino per importi personalizzati e calcolo del resto.
"""
from __future__ import annotations
import csv, sys, os, subprocess, platform, webbrowser, json, shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# --- NUOVA DIPENDENZA: Interfaccia grafica moderna ---
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog, filedialog

# --- DIPENDENZA OPZIONALE: Stampa termica ---
try:
    from escpos.printer import Usb, Network
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False

# --- DIPENDENZA OPZIONALE: Esportazione PDF ---
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

APP_TITLE = "Easy Vendite - POS System"
CURRENCY = "€"

# --- MODIFICA PER LA DISTRIBUZIONE ---
# Questa funzione assicura che il programma trovi sempre i suoi file,
# sia quando lo esegui come script (.py) sia come applicazione compilata (.exe/.app).
def get_base_path():
    """ Ottiene il percorso di base corretto per l'applicazione. """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # In esecuzione come bundle PyInstaller
        return Path(sys._MEIPASS)
    else:
        # In esecuzione come script .py normale
        return Path(__file__).resolve().parent

BASE_DIR = get_base_path()
# Per i dati modificabili dall'utente (vendite, backup), usiamo una cartella vicino all'eseguibile
# Questo rende l'app "portatile"
if getattr(sys, 'frozen', False):
    WRITABLE_DIR = Path(sys.executable).parent
else:
    WRITABLE_DIR = Path(__file__).resolve().parent

DATA_DIR = WRITABLE_DIR / "data"
SALES_DIR = DATA_DIR / "sales"
BACKUP_DIR = DATA_DIR / "backups"
PRODUCTS_FILE = DATA_DIR / "products.csv"
SETTINGS_FILE = DATA_DIR / "settings.json"

# File di partenza (solo lettura)
INITIAL_PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
INITIAL_SETTINGS_FILE = BASE_DIR / "data" / "settings.json"


# ----------------------- Utility -----------------------
def ensure_dirs() -> None:
    """Crea le cartelle necessarie e copia i file di default se non esistono."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SALES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Se il file dei prodotti non esiste nella cartella di scrittura, copialo da quello "impacchettato"
    if not PRODUCTS_FILE.exists() and INITIAL_PRODUCTS_FILE.exists():
        shutil.copy(INITIAL_PRODUCTS_FILE, PRODUCTS_FILE)
        
    # Fa lo stesso per le impostazioni
    if not SETTINGS_FILE.exists() and INITIAL_SETTINGS_FILE.exists():
        shutil.copy(INITIAL_SETTINGS_FILE, SETTINGS_FILE)


def money(value: float) -> str:
    return f"{CURRENCY} {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def today_sales_path() -> Path:
    d = datetime.now().strftime("%Y-%m-%d")
    return SALES_DIR / f"{d}-sales.csv"

def append_sale_line(receipt_id: str, item_name: str, unit_price: float, qty: int, subtotal: float, method: str) -> None:
    path = today_sales_path()
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp","receipt_id","item","unit_price","qty","subtotal","payment_method"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            receipt_id,
            item_name,
            f"{unit_price:.2f}",
            qty,
            f"{subtotal:.2f}",
            method
        ])

def aggregate_today_sales() -> Tuple[List[Tuple[str,int,float]], int, float]:
    path = today_sales_path()
    summary: Dict[str, Tuple[int,float]] = {}
    total_receipts = 0
    total_revenue = 0.0
    if not path.exists(): return [],0,0.0
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        seen_receipts = set()
        for row in reader:
            item = row.get("item","")
            qty = int(float(row.get("qty","0") or 0))
            subtotal = float(row.get("subtotal","0") or 0)
            rid = row.get("receipt_id","")
            if rid and rid not in seen_receipts:
                seen_receipts.add(rid)
                total_receipts += 1
            if item:
                q, rev = summary.get(item,(0,0.0))
                summary[item] = (q+qty, rev+subtotal)
            total_revenue += subtotal
    rows = sorted(((name,q,rev) for name,(q,rev) in summary.items()), key=lambda x:x[2], reverse=True)
    return rows, total_receipts, total_revenue

def next_receipt_id() -> str:
    base = datetime.now().strftime("%Y%m%d")
    path = today_sales_path()
    n=1
    if path.exists():
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ids = [row.get("receipt_id","") for row in reader]
        for rid in reversed(ids):
            if rid.startswith(base+"-"):
                try: k=int(rid.split("-")[-1]); n=k+1; break
                except Exception: pass
    return f"{base}-{n:03d}"

# ----------------------- GUI App -----------------------
class StandFacileApp(b.Window):
    def __init__(self):
        super().__init__(themename="litera")
        ensure_dirs()
        
        self.settings = {}
        self.load_settings()

        self.price_items: List[Dict[str, Any]] = []
        self.load_price_list()

        self.filtered_items = list(self.price_items)
        self.cart: Dict[str,Dict[str,float]] = {}
        self.current_receipt_id: Optional[str] = None
        self.discount_amount = 0.0
        
        self.title(APP_TITLE)
        self.geometry("1280x768")
        self.minsize(1024, 700)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._build_menu()
        self._build_layout()
        self._update_categories_combo()

        self._apply_filter()
        self._update_total()
        self._refresh_favorites_bar()

        self.run_backup()

    def on_closing(self):
        self.save_price_list()
        self.save_settings()
        self.destroy()

    def _build_menu(self):
        menubar = b.Menu(self)
        m_file = b.Menu(menubar, tearoff=0)
        m_file.add_command(label="Apri cartella dati", command=lambda:webbrowser.open(DATA_DIR.as_uri()))
        m_file.add_separator()
        m_file.add_command(label="Esci", command=self.on_closing)
        menubar.add_cascade(label="File", menu=m_file)
        
        m_tools = b.Menu(menubar, tearoff=0)
        m_tools.add_command(label="Report di oggi", command=self.show_daily_report)
        m_tools.add_command(label="Storico vendite...", command=self.show_sales_history)
        m_tools.add_command(label="Ordini di oggi (Ristampa/Elimina)...", command=self.show_todays_orders)
        m_tools.add_separator()
        m_tools.add_command(label="Azzera carrello", command=self.cmd_clear_cart)
        menubar.add_cascade(label="Strumenti", menu=m_tools)

        m_manage = b.Menu(menubar, tearoff=0)
        m_manage.add_command(label="Modifica listino", command=self.edit_price_list)
        m_manage.add_command(label="Importa listino da CSV...", command=self.import_price_list)
        m_manage.add_separator()
        m_manage.add_command(label="Modifica Scontrino", command=self.edit_receipt_template)
        m_manage.add_command(label="Modifica Talloncini", command=self.edit_tags_template)
        m_manage.add_command(label="Impostazioni Stampanti", command=self.edit_printer_settings)
        m_manage.add_separator()
        m_manage.add_command(label="Imposta Password Gestione...", command=self.set_management_password)
        menubar.add_cascade(label="Gestione", menu=m_manage)

        m_help = b.Menu(menubar, tearoff=0)
        m_help.add_command(label="Guida rapida", command=self.show_quick_help)
        m_help.add_command(label="Informazioni", command=lambda:messagebox.showinfo(APP_TITLE,f"{APP_TITLE}\nSemplice gestionale per stand — Versione potenziata"))
        menubar.add_cascade(label="Aiuto", menu=m_help)
        self.config(menu=menubar)

    def show_todays_orders(self):
        try:
            TodayOrdersWindow(self)
        except FileNotFoundError:
            messagebox.showinfo(APP_TITLE, "Nessuna vendita registrata oggi.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Errore apertura ordini di oggi: {e}")

    def _build_layout(self):
        root = b.Frame(self, padding=10)
        root.pack(fill=BOTH, expand=True)
        top = b.Frame(root)
        top.pack(side=TOP, fill=X, pady=(0, 10))
        b.Label(top,text="Cerca:").pack(side=LEFT, padx=(0, 5))
        self.var_search = b.StringVar()
        ent = b.Entry(top,textvariable=self.var_search,width=30)
        ent.pack(side=LEFT,padx=6)
        ent.bind("<KeyRelease>",lambda e:self._apply_filter())
        
        cats = sorted({str(i.get("category","")) for i in self.price_items if i.get("category","")})
        self.var_cat = b.StringVar(value="Tutte le categorie")
        self.cat_combo = b.Combobox(top, values=["Tutte le categorie"]+cats, textvariable=self.var_cat, state="readonly", width=24)
        self.cat_combo.pack(side=LEFT)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e:self._apply_filter())
        
        b.Button(top,text="Nuovo scontrino", command=self.cmd_new_receipt, bootstyle="info-outline").pack(side=RIGHT)
        
        self.favorites_bar = b.Frame(root)
        self.favorites_bar.pack(side=TOP, fill=X, pady=(0, 10))
        b.Label(self.favorites_bar, text="Preferiti:", font="-weight bold").pack(side=LEFT, padx=(0,10))

        main = b.PanedWindow(root,orient=HORIZONTAL)
        main.pack(fill=BOTH, expand=True)
        left = b.Frame(main)
        main.add(left, weight=3)
        self._build_product_grid(left)
        right = b.Frame(main,padding=6)
        main.add(right, weight=2)
        self._build_cart(right)

    def _build_product_grid(self,parent):
        container = b.Frame(parent)
        container.pack(fill=BOTH, expand=True, padx=6,pady=6)
        
        self.canvas = b.Canvas(container, highlightthickness=0, borderwidth=0)
        vsb = b.Scrollbar(container, orient="vertical", command=self.canvas.yview, bootstyle="round")
        
        self.products_frame = b.Frame(self.canvas)
        self.products_frame.bind("<Configure>", lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0,0),window=self.products_frame,anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)

    def _build_cart(self,parent):
        b.Label(parent,text="Carrello", font="-size 14 -weight bold").pack(anchor="w")
        columns = ("item","qty","unit","subtotal")
        self.tree = b.Treeview(parent, columns=columns, show="headings", height=14, bootstyle="primary")
        for col,text in zip(columns,("Articolo","Qtà","Prezzo","Subtotale")):
            self.tree.heading(col,text=text)
        self.tree.column("item",width=180)
        self.tree.column("qty",width=40,anchor="center")
        self.tree.column("unit",width=70,anchor="e")
        self.tree.column("subtotal",width=80,anchor="e")
        self.tree.pack(fill=BOTH, expand=True,pady=(4,4))
        
        cart_btns_frame = b.Frame(parent)
        cart_btns_frame.pack(fill=X)
        
        left_btns = b.Frame(cart_btns_frame)
        left_btns.pack(side=LEFT)
        b.Button(left_btns,text="Rimuovi", command=self.cmd_remove_selected, bootstyle="danger-outline").pack(side=LEFT)
        b.Button(left_btns,text="Azzera", command=self.cmd_clear_cart, bootstyle="warning-outline").pack(side=LEFT,padx=4)
        b.Button(left_btns,text="+1", command=lambda:self.cmd_change_qty(+1), bootstyle="secondary-outline").pack(side=LEFT)
        b.Button(left_btns,text="-1", command=lambda:self.cmd_change_qty(-1), bootstyle="secondary-outline").pack(side=LEFT,padx=4)
        
        discount_frame = b.Frame(parent)
        discount_frame.pack(fill=X, pady=5)
        b.Label(discount_frame, text="Sconto (es. 5 o 10%):").pack(side=LEFT)
        self.var_discount = b.StringVar()
        entry_discount = b.Entry(discount_frame, textvariable=self.var_discount, width=10)
        entry_discount.pack(side=LEFT, padx=5)
        b.Button(discount_frame, text="Applica Sconto", command=self.cmd_apply_discount, bootstyle="info-outline").pack(side=LEFT)
        
        self.var_total = b.StringVar(value=money(0))
        b.Label(parent,textvariable=self.var_total, font="-size 12 -weight bold", justify=RIGHT).pack(fill=X, pady=4)
        
        self._build_numpad(parent)

        checkout_btn = b.Button(parent, text="Scontrino / Pagamento", command=self.cmd_checkout, bootstyle="success")
        checkout_btn.pack(fill=X, ipady=5, pady=(10,0))
        b.Button(parent, text="Stampa Talloncino", command=self.cmd_print_tag, bootstyle="info").pack(fill=X, ipady=4, pady=(6,0))
    
    def _build_numpad(self, parent):
        numpad_frame = b.LabelFrame(parent, text="Importo personalizzato", padding=10)
        numpad_frame.pack(fill=X, pady=(10,0))
        
        self.var_custom_amount = b.StringVar()
        entry = b.Entry(numpad_frame, textvariable=self.var_custom_amount, justify="right", font="-size 12")
        entry.pack(fill=X, pady=(2,4))
        
        keys_frame = b.Frame(numpad_frame)
        keys_frame.pack(fill=X)
        keys = ['7','8','9','4','5','6','1','2','3','C','0','.']
        for i, key in enumerate(keys):
            btn = b.Button(keys_frame, text=key, bootstyle="secondary", command=lambda k=key: self._numpad_press(k))
            btn.grid(row=i//3, column=i%3, sticky="ew", padx=2, pady=2)
        
        b.Button(keys_frame, text="Aggiungi Vario", bootstyle="primary", command=self.cmd_add_custom_item).grid(row=4, column=0, columnspan=3, sticky="ew", pady=(4,0))
        for i in range(5): keys_frame.rowconfigure(i, weight=1)
        for i in range(3): keys_frame.columnconfigure(i, weight=1)

    def _numpad_press(self, key):
        current = self.var_custom_amount.get()
        if key == 'C': self.var_custom_amount.set("")
        elif key == '.' and '.' in current: return
        else: self.var_custom_amount.set(current + key)

    def cmd_add_custom_item(self):
        try:
            price = float(self.var_custom_amount.get())
            if price <= 0: return
        except (ValueError, TypeError):
            messagebox.showerror("Errore", "Importo non valido.")
            return
        
        name = simpledialog.askstring("Articolo Vario", "Inserisci il nome dell'articolo:", initialvalue="Vario")
        if not name: return

        item_data = {"name": name, "price": price, "category": "Vari"}
        self.cmd_add_to_cart(item_data)
        self.var_custom_amount.set("")

    def _refresh_products(self):
        for w in self.products_frame.winfo_children(): w.destroy()
        
        num_columns = max(2, self.winfo_width() // 280)

        for i,item in enumerate(self.filtered_items):
            f = b.Frame(self.products_frame, borderwidth=1, relief=SOLID, padding=8)
            f.grid(row=i//num_columns, column=i%num_columns, padx=5, pady=5, sticky="nsew")
            
            b.Label(f,text=item["name"], font="-size 11").pack(fill=X)
            b.Label(f,text=money(item["price"]), font="-weight bold").pack(fill=X)
            b.Button(f,text="Aggiungi", bootstyle="primary-outline", command=lambda itm=item:self.cmd_add_to_cart(itm)).pack(pady=(8,0))
        
        for c in range(num_columns): self.products_frame.columnconfigure(c, weight=1)

    def _apply_filter(self):
        text = self.var_search.get().lower()
        cat = self.var_cat.get()
        self.filtered_items = [i for i in self.price_items if (text in i["name"].lower()) and (cat=="Tutte le categorie" or i["category"]==cat)]
        self._refresh_products()

    def cmd_add_to_cart(self,item):
        name = item["name"]; price = float(item["price"])
        if name in self.cart: self.cart[name]["qty"]+=1
        else: self.cart[name]={"unit":price,"qty":1}
        self._sync_cart_tree(); self._update_total()
    
    def cmd_add_to_cart_by_name(self, name: str):
        item = next((p for p in self.price_items if p["name"] == name), None)
        if item: self.cmd_add_to_cart(item)
        else: messagebox.showwarning("Prodotto non trovato", f"Il prodotto '{name}' non è più nel listino.")

    def _sync_cart_tree(self):
        self.tree.delete(*self.tree.get_children())
        for name,data in self.cart.items():
            qty = data["qty"]; unit=data["unit"]; subtotal=qty*unit
            self.tree.insert("",END,values=(name,int(qty),money(unit),money(subtotal)))

    def _cart_lines(self):
        lines = []
        subtotal = 0.0
        for name, data in sorted(self.cart.items()):
            full_item = next((p for p in self.price_items if p["name"] == name), {"name": name, "price": data["unit"]})
            qty, unit = data["qty"], data["unit"]
            line_total = qty * unit
            line_data = {"item": full_item, "qty": qty, "unit": unit, "subtotal": line_total}
            lines.append(line_data)
            subtotal += line_total
        return lines, subtotal
    
    def cmd_apply_discount(self):
        discount_str = self.var_discount.get().strip().replace(',', '.')
        if not discount_str:
            self.discount_amount = 0.0
            self._update_total()
            return
            
        _, subtotal = self._cart_lines()
        
        try:
            if discount_str.endswith('%'):
                percentage = float(discount_str[:-1])
                self.discount_amount = subtotal * (percentage / 100.0)
            else:
                self.discount_amount = float(discount_str)
            
            if self.discount_amount > subtotal:
                messagebox.showwarning("Attenzione", "Lo sconto non può superare il subtotale.")
                self.discount_amount = 0.0
                self.var_discount.set("")

        except ValueError:
            messagebox.showerror("Errore", "Valore sconto non valido. Usa un numero (es. 5) o una percentuale (es. 10%).")
            self.discount_amount = 0.0
            self.var_discount.set("")
        
        self._update_total()

    def _update_total(self):
        _, subtotal = self._cart_lines()
        final_total = subtotal - self.discount_amount
        
        text = f"Subtotale: {money(subtotal)}\n"
        if self.discount_amount > 0:
            text += f"Sconto: -{money(self.discount_amount)}\n"
        text += f"TOTALE: {money(final_total)}"
        
        self.var_total.set(text)

    def cmd_remove_selected(self):
        sel = self.tree.selection()
        if not sel: return
        for s in sel:
            name = self.tree.item(s,"values")[0]
            if name in self.cart: del self.cart[name]
        self._sync_cart_tree(); self._update_total()

    def cmd_clear_cart(self):
        if self.cart and messagebox.askyesno("Conferma", "Sei sicuro di voler azzerare il carrello?"):
            self.cart.clear()
            self.discount_amount = 0.0
            self.var_discount.set("")
            self._sync_cart_tree()
            self._update_total()

    def cmd_change_qty(self, delta:int):
        sel = self.tree.selection()
        if not sel: return
        name=self.tree.item(sel[0],"values")[0]
        row=self.cart.get(name)
        if not row: return
        row["qty"]=max(0,row["qty"]+delta)
        if row["qty"]==0: del self.cart[name]
        self._sync_cart_tree(); self._update_total()

    def cmd_checkout(self):
        if not self.cart: messagebox.showinfo(APP_TITLE,"Il carrello è vuoto."); return
        lines, subtotal = self._cart_lines()
        final_total = subtotal - self.discount_amount
        CheckoutWindow(self, lines, subtotal, self.discount_amount, final_total)

    def finalize_sale(self, lines, total, payment_method, discount_amount):
        rid = self.current_receipt_id or next_receipt_id()
        self.current_receipt_id = rid
        for line_data in lines:
            name, unit, qty, subtotal = line_data["item"]["name"], line_data["unit"], line_data["qty"], line_data["subtotal"]
            append_sale_line(rid,name,unit,qty,subtotal,payment_method)
        
        if discount_amount > 0:
            append_sale_line(rid, "SCONTO", -discount_amount, 1, -discount_amount, payment_method)

        ReceiptWindow(self, rid, lines, total,
            self.settings.get("receipt_title", "Scontrino non fiscale"),
            self.settings.get("receipt_notes", ["Grazie!"]),
            self.settings.get("receipt_logo_path", None),
            discount_amount
        )
        self.cart.clear()
        self.discount_amount = 0.0
        self.var_discount.set("")
        self._sync_cart_tree()
        self._update_total()
        self._refresh_favorites_bar()
        self.current_receipt_id=None

    def cmd_print_tag(self):
        SelectTagToPrintWindow(self)
        
    def _execute_print_tag(self, tag_content: str, quantity: int):
        full_content = []
        width = 48
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        for i in range(quantity):
            content = "\n".join(["="*width, f"{tag_content:^{width}}", "-"*width, f"Data: {now_str}".center(width), "="*width])
            full_content.append(content)
        
        tmp = WRITABLE_DIR / "talloncino_temp.txt"
        spacing_for_manual_cut = "\n" * 6
        tmp.write_text(spacing_for_manual_cut.join(full_content), encoding="utf-8")
        
        config = self.settings.get("printer_config", {})
        printer_type = config.get("type", "standard")
        
        if ESCPOS_AVAILABLE and printer_type in ["usb", "network"]:
            try:
                printer = None
                if printer_type == "usb": printer = Usb(int(config.get("usb_vendor_id","0"),16), int(config.get("usb_product_id","0"),16))
                elif printer_type == "network": printer = Network(host=config.get("network_ip", ""))
                
                for i in range(quantity):
                    printer.set(align='center', text_type='b', width=2, height=2)
                    printer.text(f"{tag_content}\n")
                    printer.set(align='center', text_type='normal')
                    printer.text(f"Ora: {now_str[11:]}\n")
                    printer.feed(3)
                    printer.cut()
                
                # --- MODIFICA STAMPA RAPIDA: Messaggio rimosso ---
                # messagebox.showinfo(APP_TITLE, f"{quantity} talloncini inviati alla stampante termica.")
                return
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"Errore stampa termica: {e}\n\nUso il metodo di stampa standard.")

        try:
            if platform.system()=="Darwin": subprocess.run(["lp", str(tmp)], check=True)
            elif platform.system()=="Windows": os.startfile(str(tmp), "print")
            else: subprocess.run(["lp", str(tmp)], check=True)
            # messagebox.showinfo(APP_TITLE, "Talloncino inviato alla stampante")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Errore stampa talloncino: {e}\nFile salvato in: {tmp}")

    def cmd_new_receipt(self):
        self.cmd_clear_cart()
        self.current_receipt_id=next_receipt_id()
        messagebox.showinfo("Nuovo scontrino", f"Carrello azzerato.\nProssimo ID scontrino: {self.current_receipt_id}")

    def check_password(self):
        pwd = self.settings.get("management_password")
        if pwd:
            entered = simpledialog.askstring("Password Richiesta", "Inserisci la password di gestione:", show='*')
            if entered != pwd:
                messagebox.showerror("Accesso Negato", "Password errata.")
                return False
        return True

    def load_price_list(self):
        if not PRODUCTS_FILE.exists():
            self.price_items = [
                {"name":"Panino salamella","price":5.0,"category":"Cucina", "ticket_text": ""},
                {"name":"Patatine","price":3.0,"category":"Cucina", "ticket_text": ""},
                {"name":"Birra media","price":5.0,"category":"Bar", "ticket_text": "BIRRA"},
                {"name":"Acqua","price":1.5,"category":"Bar", "ticket_text": ""},
            ]
            self.save_price_list()
        else:
            with PRODUCTS_FILE.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.price_items = []
                for row in reader:
                    try:
                        row['price'] = float(row['price'])
                        row.setdefault('ticket_text', '')
                        self.price_items.append(row)
                    except (ValueError, KeyError):
                        print(f"Riga ignorata in products.csv: {row}")
    
    def save_price_list(self):
        if not self.price_items: return
        with PRODUCTS_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "category", "ticket_text"])
            writer.writeheader()
            writer.writerows(self.price_items)

    def load_settings(self):
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as f: self.settings = json.load(f)
        else: self.settings = {}
        
        defaults = {
            "receipt_title": "Pro Loco — Scontrino non fiscale",
            "receipt_notes": ["Grazie e buona serata!"],
            "receipt_logo_path": None, "management_password": None, "theme": "Chiaro",
            "tag_templates": [{"title": "Talloncino Cucina", "text": "RITIRO CUCINA"}, {"title": "Talloncino Bar", "text": "RITIRO BAR"},
                              {"title": "Generico 1", "text": "TALLONCINO 3"}, {"title": "Generico 2", "text": "TALLONCINO 4"}],
            "printer_config": {"type": "standard", "usb_vendor_id": "0x04b8", "usb_product_id": "0x0e28", "network_ip": "192.168.1.100"}
        }
        for key, value in defaults.items(): self.settings.setdefault(key, value)
    
    def save_settings(self):
        with SETTINGS_FILE.open("w", encoding="utf-8") as f: json.dump(self.settings, f, indent=2)

    def edit_price_list(self):
        if not self.check_password(): return
        txt="\n".join([f"{i['name']}|{i['price']}|{i['category']}|{i.get('ticket_text','')}" for i in self.price_items])
        editor = TextEditorWindow(self, title="Modifica Listino", initial_text=txt,
            instructions="Modifica prodotti (nome|prezzo|categoria|testo_foglietto per riga).")
        if editor.result:
            self.price_items.clear()
            for line in editor.result.splitlines():
                parts=line.strip().split("|")
                if len(parts)<2: continue
                name=parts[0].strip()
                try: price=float(parts[1].strip())
                except: price=0.0
                category=parts[2].strip() if len(parts)>2 else ""
                ticket = parts[3].strip() if len(parts)>3 else ""
                if name: self.price_items.append({"name":name,"price":price,"category":category, "ticket_text": ticket})
            self._update_categories_combo(); self._apply_filter()
            self.save_price_list()

    def edit_receipt_template(self):
        if not self.check_password(): return
        EditReceiptWindow(self)

    def edit_tags_template(self):
        if not self.check_password(): return
        EditTagsWindow(self)

    def edit_printer_settings(self):
        if not self.check_password(): return
        PrinterSettingsWindow(self)
        
    def set_management_password(self):
        current_pwd = self.settings.get("management_password")
        if current_pwd:
            if simpledialog.askstring("Password", "Inserisci password attuale:", show='*') != current_pwd:
                messagebox.showerror("Errore", "Password attuale errata."); return
        new_pwd = simpledialog.askstring("Nuova Password", "Inserisci la nuova password (lascia vuoto per rimuovere):", show='*')
        if new_pwd is not None:
            self.settings["management_password"] = new_pwd if new_pwd else None
            self.save_settings(); messagebox.showinfo("Successo", "Password aggiornata.")

    def import_price_list(self):
        if not self.check_password(): return
        path = filedialog.askopenfilename(title="Seleziona file CSV", filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")])
        if not path: return
        mode = simpledialog.askstring("Modalità", "Digita 'sostituisci' o 'aggiorna'.", initialvalue="aggiorna")
        if mode not in ["sostituisci", "aggiorna"]: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f); next(reader); new_items = []
                for row in reader:
                    if len(row) < 3: continue
                    new_items.append({"name": row[0], "price": float(row[1]), "category": row[2], "ticket_text": row[3] if len(row)>3 else ""})
        except Exception as e: messagebox.showerror("Errore", f"Impossibile leggere il file CSV.\n{e}"); return
        
        if mode == "sostituisci": self.price_items = new_items
        else:
            current = {p["name"]: p for p in self.price_items}
            for item in new_items: current[item["name"]] = item
            self.price_items = list(current.values())
        
        self.price_items.sort(key=lambda x: x['name'])
        self._update_categories_combo(); self._apply_filter(); self.save_price_list()
        messagebox.showinfo("Successo", f"Listino importato in modalità '{mode}'.")
    
    def _update_categories_combo(self):
        cats = sorted({str(i.get("category","")) for i in self.price_items if i.get("category","")})
        self.cat_combo['values'] = ["Tutte le categorie"] + cats

    def show_daily_report(self):
        rows,count,revenue=aggregate_today_sales()
        txt=[f"Report vendite oggi ({datetime.now().strftime('%d/%m/%Y')}):\n"]
        txt.append("{:<25} {:>5} {:>12}".format("Prodotto", "Qtà", "Incasso")); txt.append("-" * 45)
        for name,qty,rev in rows: txt.append("{:<25} {:>5} {:>12}".format(name, qty, money(rev)))
        txt.append("-" * 45); txt.append(f"\nTotale scontrini: {count}"); txt.append(f"Totale incasso: {money(revenue)}")
        ReportWindow(self, "Report Giornaliero", "\n".join(txt))

    def show_sales_history(self): SalesHistoryWindow(self)

    def _get_top_products(self, limit=5):
        summary: Dict[str, int] = {}
        if not SALES_DIR.exists(): return []
        for f in SALES_DIR.glob("*.csv"):
            try:
                with f.open("r", encoding="utf-8") as fo:
                    for row in csv.DictReader(fo): summary[row.get("item","")] = summary.get(row.get("item",""), 0) + int(float(row.get("qty", "0") or 0))
            except Exception as e: print(f"Errore lettura {f.name}: {e}")
        return [name for name, qty in sorted(summary.items(), key=lambda x: x[1], reverse=True)[:limit]]

    def _refresh_favorites_bar(self):
        for w in self.favorites_bar.winfo_children():
            if isinstance(w, b.Button): w.destroy()
        
        for name in self._get_top_products():
            b.Button(self.favorites_bar, text=name, bootstyle="light", command=lambda n=name: self.cmd_add_to_cart_by_name(n)).pack(side=LEFT, padx=3)

    def run_backup(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if any(BACKUP_DIR.glob(f"backup-{today}-*.zip")): return
        try: shutil.make_archive(str(BACKUP_DIR / f"backup-{today}-{datetime.now().strftime('%H%M%S')}"), 'zip', DATA_DIR)
        except Exception as e: print(f"Errore backup: {e}")

    def show_quick_help(self):
        txt="1. Seleziona i prodotti o usa i preferiti per aggiungerli al carrello.\n" \
            "2. Usa il tastierino per aggiungere importi personalizzati.\n" \
            "3. Inserisci uno sconto (es. '5' o '10%') e clicca 'Applica Sconto'.\n" \
            "4. Clicca 'Scontrino / Pagamento' per finalizzare la vendita.\n" \
            "5. Nella finestra di pagamento, inserisci l'importo ricevuto per calcolare il resto.\n" \
            "6. Clicca 'Stampa Talloncino', scegli il modello e la quantità da stampare.\n" \
            "7. Gestisci listino, importazioni, password, stampanti e scontrino dal menu 'Gestione'.\n" \
            "8. Visualizza report e storico vendite dal menu 'Strumenti'."
        messagebox.showinfo("Guida rapida",txt)

# --- Finestre secondarie ---
class CheckoutWindow(b.Toplevel):
    def __init__(self, master, lines, subtotal, discount, total):
        super().__init__(master)
        self.master = master; self.lines = lines; self.total = total
        self.discount = discount
        self.title("Pagamento"); self.geometry("400x350"); self.resizable(False, False); self.transient(master); self.grab_set()
        
        frame = b.Frame(self, padding=20); frame.pack(fill=BOTH, expand=True)
        
        b.Label(frame, text=f"Subtotale: {money(subtotal)}").pack()
        if self.discount > 0:
            b.Label(frame, text=f"Sconto: -{money(self.discount)}", bootstyle="info").pack()
        
        b.Label(frame, text="Importo Totale:", font="-weight bold").pack(pady=(10,0))
        b.Label(frame, text=money(self.total), font="-size 24 -weight bold").pack(pady=(0, 20))
        
        b.Label(frame, text="Importo Ricevuto:", font="-weight bold").pack()
        self.var_received = b.StringVar(); self.var_received.trace_add("write", self.update_change)
        entry = b.Entry(frame, textvariable=self.var_received, font="-size 16", justify="center"); entry.pack(pady=5); entry.focus()
        
        b.Label(frame, text="Resto:", font="-weight bold").pack(pady=(10,0))
        self.lbl_change = b.Label(frame, text=money(0), font="-size 18 -weight bold", bootstyle="success")
        self.lbl_change.pack()
        
        buttons_frame = b.Frame(frame); buttons_frame.pack(side=BOTTOM, fill=X, pady=(20,0))
        b.Button(buttons_frame, text="Contanti", bootstyle="success", command=lambda: self.finalize("Contanti")).pack(side=LEFT, expand=True, fill=X, padx=(0,5))
        b.Button(buttons_frame, text="Carta/POS", bootstyle="success", command=lambda: self.finalize("Carta/POS")).pack(side=RIGHT, expand=True, fill=X, padx=(5,0))

    def update_change(self, *args):
        try:
            received = float(self.var_received.get().replace(",", ".")); change = received - self.total
            self.lbl_change.config(text=money(change), bootstyle="success" if change >= 0 else "danger")
        except (ValueError, TypeError): self.lbl_change.config(text=money(0), bootstyle="secondary")
        
    def finalize(self, method):
        self.master.finalize_sale(self.lines, self.total, method, self.discount)
        self.destroy()

class SalesHistoryWindow(b.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.title("Storico Vendite"); self.geometry("800x600"); self.all_sales = self._load_all_sales()
        filter_frame = b.Frame(self, padding=10); filter_frame.pack(fill=X)
        self.var_date, self.var_prod, self.var_receipt = b.StringVar(), b.StringVar(), b.StringVar()
        b.Label(filter_frame, text="Data:").grid(row=0, col=0, padx=5); b.Entry(filter_frame, textvariable=self.var_date).grid(row=0, col=1, padx=5)
        b.Label(filter_frame, text="Prodotto:").grid(row=0, col=2, padx=5); b.Entry(filter_frame, textvariable=self.var_prod).grid(row=0, col=3, padx=5)
        b.Label(filter_frame, text="Scontrino:").grid(row=0, col=4, padx=5); b.Entry(filter_frame, textvariable=self.var_receipt).grid(row=0, col=5, padx=5)
        b.Button(filter_frame, text="Filtra", command=self.apply_filters, bootstyle="primary").grid(row=0, col=6, padx=10)
        b.Button(filter_frame, text="Reset", command=self.reset_filters, bootstyle="secondary").grid(row=0, col=7)
        
        cols = ("timestamp","receipt_id","item","qty","subtotal","payment_method")
        self.tree = b.Treeview(self, columns=cols, show="headings", bootstyle="primary")
        for col,txt in zip(cols, ("Data/Ora", "ID Scontrino", "Prodotto", "Qtà", "Subtotale", "Pagamento")): self.tree.heading(col, text=txt)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb = b.Scrollbar(self, orient="vertical", command=self.tree.yview, bootstyle="round"); vsb.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=vsb.set)
        self.populate_tree(self.all_sales)

    def _load_all_sales(self):
        sales = []
        for f in sorted(SALES_DIR.glob("*.csv"), reverse=True):
            try:
                with f.open('r', encoding='utf-8') as csvfile: sales.extend(list(csv.DictReader(csvfile)))
            except Exception:
                pass
        return sales

    def populate_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=[row.get(c, '') for c in ("timestamp", "receipt_id", "item", "qty", "subtotal", "payment_method")])

    def apply_filters(self):
        f_date, f_prod, f_receipt = self.var_date.get().lower(), self.var_prod.get().lower(), self.var_receipt.get().lower()
        filtered = [s for s in self.all_sales if (f_date in s.get('timestamp','').lower()) and (f_prod in s.get('item','').lower()) and (f_receipt in s.get('receipt_id','').lower())]
        self.populate_tree(filtered)

    def reset_filters(self):
        self.var_date.set(""); self.var_prod.set(""); self.var_receipt.set(""); self.populate_tree(self.all_sales)

class TodayOrdersWindow(b.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Ordini di oggi (Ristampa/Elimina)")
        self.geometry("600x500")
        
        frame = b.Frame(self, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        cols = ("receipt_id", "time", "items", "total")
        self.tree = b.Treeview(frame, columns=cols, show="headings", height=16, bootstyle="primary")
        for col,txt in zip(cols, ("ID","Ora","Articoli","Totale")): self.tree.heading(col, text=txt)
        self.tree.pack(fill=BOTH, expand=True)
        
        btns = b.Frame(self, padding=(10,10))
        btns.pack(fill=X)
        b.Button(btns, text="Apri / Ristampa", bootstyle="success", command=self.open_selected).pack(side=RIGHT)
        b.Button(btns, text="Chiudi", command=self.destroy, bootstyle="secondary").pack(side=RIGHT, padx=6)
        b.Button(btns, text="Elimina Selezionato", bootstyle="danger", command=self.delete_selected).pack(side=LEFT)
        self.refresh_orders()

    def refresh_orders(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            data = self._load_today_grouped()
            self.orders = list(data.values())
            for order in self.orders:
                self.tree.insert("", END, iid=order["receipt_id"], values=(order["receipt_id"], order["time"], order["items_count"], f"{order['total']:.2f}{CURRENCY}"))
        except FileNotFoundError:
            self.orders = []
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aggiornare la lista ordini: {e}", parent=self)

    def _load_today_grouped(self):
        path = today_sales_path()
        if not path.exists(): raise FileNotFoundError("File vendite odierno non trovato")
        grouped = {}
        with path.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rid = row["receipt_id"]
                grouped.setdefault(rid, {"receipt_id": rid, "lines": [], "total": 0.0, "time": row["timestamp"][11:16], "items_count": 0, "discount": 0.0})
                
                if row["item"] == "SCONTO":
                    grouped[rid]["discount"] += abs(float(row["subtotal"]))
                else:
                    grouped[rid]["lines"].append({"item": {"name": row["item"]}, "unit": float(row["unit_price"]), "qty": int(float(row["qty"])), "subtotal": float(row["subtotal"])})
                    grouped[rid]["items_count"] += int(float(row["qty"]))

                grouped[rid]["total"] += float(row["subtotal"])
        return grouped
        
    def open_selected(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo(APP_TITLE, "Seleziona un ordine.", parent=self); return
        order = next((o for o in self.orders if o["receipt_id"] == sel[0]), None)
        if not order: messagebox.showerror(APP_TITLE, "Ordine non trovato.", parent=self); return
        ReceiptWindow(self.master, order["receipt_id"], order["lines"], order["total"],
                      self.master.settings.get("receipt_title"), self.master.settings.get("receipt_notes"), 
                      self.master.settings.get("receipt_logo_path"), order.get("discount", 0.0))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Seleziona uno scontrino da eliminare.", parent=self)
            return

        receipt_id_to_delete = sel[0]
        
        if not messagebox.askyesno("Conferma Eliminazione", 
            f"Sei sicuro di voler eliminare definitivamente lo scontrino {receipt_id_to_delete}?\n\nL'operazione è irreversibile e modificherà il totale giornaliero.",
            parent=self):
            return

        try:
            path = today_sales_path()
            if not path.exists():
                messagebox.showerror("Errore", "File vendite non trovato.", parent=self)
                return

            with path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                all_lines = list(reader)
            
            header = all_lines[0]
            updated_lines = [row for row in all_lines[1:] if row[1] != receipt_id_to_delete]

            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(updated_lines)

            messagebox.showinfo("Successo", f"Scontrino {receipt_id_to_delete} eliminato con successo.", parent=self)
            self.refresh_orders()

        except Exception as e:
            messagebox.showerror("Errore Critico", f"Impossibile eliminare lo scontrino: {e}", parent=self)

class EditReceiptWindow(b.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.master = master; self.title("Modifica Template Scontrino"); self.geometry("500x450")
        self.settings = master.settings; frame = b.Frame(self, padding=15); frame.pack(fill=BOTH, expand=True)
        b.Label(frame, text="Intestazione:", font="-weight bold").pack(anchor="w")
        self.var_title = b.StringVar(value=self.settings.get("receipt_title", "")); b.Entry(frame, textvariable=self.var_title).pack(fill=X, pady=(0,10))
        logo_frame = b.Frame(frame); logo_frame.pack(fill=X, pady=(0,10))
        b.Label(logo_frame, text="Logo:", font="-weight bold").pack(anchor="w")
        self.var_logo = b.StringVar(value=self.settings.get("receipt_logo_path", "Nessun logo")); b.Entry(logo_frame, textvariable=self.var_logo, state="readonly").pack(side=LEFT, fill=X, expand=True, padx=(0,5))
        b.Button(logo_frame, text="Scegli...", command=self.select_logo, bootstyle="secondary").pack(side=LEFT)
        b.Label(frame, text="Note finali (una per riga):", font="-weight bold").pack(anchor="w")
        self.txt_notes = b.Text(frame, height=5, wrap="word", relief=SOLID, borderwidth=1); self.txt_notes.pack(fill=BOTH, expand=True, pady=(0,15))
        self.txt_notes.insert("1.0", "\n".join(self.settings.get("receipt_notes", [])))
        btn_frame = b.Frame(frame); btn_frame.pack(fill=X)
        b.Button(btn_frame, text="Salva", command=self.save, bootstyle="success").pack(side=RIGHT)
        b.Button(btn_frame, text="Annulla", command=self.destroy, bootstyle="secondary").pack(side=RIGHT, padx=10)

    def select_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]);
        if path: self.var_logo.set(path)

    def save(self):
        self.settings["receipt_title"] = self.var_title.get()
        logo_path = self.var_logo.get()
        self.settings["receipt_logo_path"] = logo_path if os.path.exists(logo_path) else None
        self.settings["receipt_notes"] = [line for line in self.txt_notes.get("1.0", "end-1c").split("\n") if line.strip()]
        self.master.save_settings(); self.destroy()

class EditTagsWindow(b.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.master = master; self.title("Modifica Talloncini"); self.geometry("550x450")
        self.templates = master.settings.get("tag_templates", []); self.vars = []
        frame = b.Frame(self, padding=15); frame.pack(fill=BOTH, expand=True)
        notebook = b.Notebook(frame); notebook.pack(fill=BOTH, expand=True, pady=(0, 15))
        for i, template in enumerate(self.templates):
            tab = b.Frame(notebook, padding=10); notebook.add(tab, text=f"Talloncino {i+1}")
            b.Label(tab, text="Titolo (menu di scelta):", font="-weight bold").pack(anchor="w")
            var_title = b.StringVar(value=template.get("title", f"Talloncino {i+1}")); b.Entry(tab, textvariable=var_title).pack(fill=X, pady=(2, 10))
            b.Label(tab, text="Testo (stampato):", font="-weight bold").pack(anchor="w")
            txt_content = b.Text(tab, height=4, wrap="word", relief=SOLID, borderwidth=1); txt_content.pack(fill=BOTH, expand=True)
            txt_content.insert("1.0", template.get("text", ""))
            self.vars.append({'title': var_title, 'text_widget': txt_content})
        btn_frame = b.Frame(frame); btn_frame.pack(fill=X)
        b.Button(btn_frame, text="Salva", command=self.save, bootstyle="success").pack(side=RIGHT)
        b.Button(btn_frame, text="Annulla", command=self.destroy, bootstyle="secondary").pack(side=RIGHT, padx=10)

    def save(self):
        new_templates = [{"title": v['title'].get(), "text": v['text_widget'].get("1.0", "end-1c").strip()} for v in self.vars]
        self.master.settings["tag_templates"] = new_templates; self.master.save_settings(); self.destroy()

class SelectTagToPrintWindow(b.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.master = master; self.title("Scegli Talloncino"); self.transient(master); self.grab_set()
        frame = b.Frame(self, padding=20); frame.pack(fill=BOTH, expand=True)
        
        b.Label(frame, text="Quale talloncino vuoi stampare?", font="-size 12 -weight bold").pack(pady=(0, 15))
        
        for template in master.settings.get("tag_templates", []):
            if template.get('title') and template.get('text'):
                # --- MODIFICA STAMPA RAPIDA: Aggiornato comando ---
                b.Button(frame, text=template.get('title'), command=lambda t=template.get('text'): self.print_tag(t), bootstyle="primary").pack(fill=X, pady=4, ipady=5)
        
        qty_frame = b.Frame(frame); qty_frame.pack(pady=(15,0))
        b.Label(qty_frame, text="Quanti ne stampo?").pack(side=LEFT, padx=(0,5))
        self.var_qty = b.IntVar(value=1)
        b.Spinbox(qty_frame, from_=1, to=50, textvariable=self.var_qty, width=5).pack(side=LEFT)
        
        # --- MODIFICA STAMPA RAPIDA: Testo pulsante e comportamento ---
        b.Button(frame, text="Chiudi", command=self.destroy, bootstyle="secondary-outline").pack(pady=(15, 0)); self.update_idletasks()
        self.geometry(f"+{master.winfo_x()+(master.winfo_width()-self.winfo_width())//2}+{master.winfo_y()+(master.winfo_height()-self.winfo_height())//2}")

    def print_tag(self, text):
        """Stampa il talloncino senza chiudere la finestra."""
        try:
            quantity = self.var_qty.get()
            if quantity < 1:
                messagebox.showerror("Errore", "La quantità deve essere almeno 1.")
                return
        except Exception:
            messagebox.showerror("Errore", "Quantità non valida.")
            return
            
        self.master._execute_print_tag(text, quantity)
        # self.destroy() # Rimosso per permettere stampe multiple

class PrinterSettingsWindow(b.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.master = master; self.title("Impostazioni Stampanti"); self.geometry("500x400")
        self.config = master.settings.get("printer_config", {})
        frame = b.Frame(self, padding=15); frame.pack(fill=BOTH, expand=True)
        type_frame = b.LabelFrame(frame, text="Tipo Stampante Scontrini", padding=10); type_frame.pack(fill=X)
        self.var_printer_type = b.StringVar(value=self.config.get("type", "standard"))
        b.Radiobutton(type_frame, text="Standard (A4)", variable=self.var_printer_type, value="standard", command=self.toggle_frames).pack(anchor="w")
        rb_usb = b.Radiobutton(type_frame, text="Termica USB (ESC/POS)", variable=self.var_printer_type, value="usb", command=self.toggle_frames); rb_usb.pack(anchor="w")
        rb_net = b.Radiobutton(type_frame, text="Termica di Rete (ESC/POS)", variable=self.var_printer_type, value="network", command=self.toggle_frames); rb_net.pack(anchor="w")
        if not ESCPOS_AVAILABLE:
            rb_usb.config(state="disabled"); rb_net.config(state="disabled")
            b.Label(type_frame, text="Libreria 'python-escpos' non trovata.", bootstyle="danger").pack(pady=5)
        self.usb_frame = b.LabelFrame(frame, text="Impostazioni USB", padding=10)
        b.Label(self.usb_frame, text="Vendor ID:").grid(row=0, col=0, sticky="w", pady=2); self.var_usb_vid = b.StringVar(value=self.config.get("usb_vendor_id", "0x04b8")); b.Entry(self.usb_frame, textvariable=self.var_usb_vid).grid(row=0, col=1, sticky="ew")
        b.Label(self.usb_frame, text="Product ID:").grid(row=1, col=0, sticky="w", pady=2); self.var_usb_pid = b.StringVar(value=self.config.get("usb_product_id", "0x0e28")); b.Entry(self.usb_frame, textvariable=self.var_usb_pid).grid(row=1, col=1, sticky="ew")
        self.net_frame = b.LabelFrame(frame, text="Impostazioni Rete", padding=10)
        b.Label(self.net_frame, text="Indirizzo IP:").grid(row=0, col=0, sticky="w", pady=2); self.var_net_ip = b.StringVar(value=self.config.get("network_ip", "192.168.1.100")); b.Entry(self.net_frame, textvariable=self.var_net_ip).grid(row=0, col=1, sticky="ew")
        btn_frame = b.Frame(frame); btn_frame.pack(fill=X, side=BOTTOM, pady=(15,0))
        b.Button(btn_frame, text="Salva", command=self.save, bootstyle="success").pack(side=RIGHT)
        b.Button(btn_frame, text="Annulla", command=self.destroy, bootstyle="secondary").pack(side=RIGHT, padx=10)
        self.toggle_frames()

    def toggle_frames(self):
        ptype = self.var_printer_type.get()
        if ptype == "usb": self.usb_frame.pack(fill=X, pady=5); self.net_frame.pack_forget()
        elif ptype == "network": self.usb_frame.pack_forget(); self.net_frame.pack(fill=X, pady=5)
        else: self.usb_frame.pack_forget(); self.net_frame.pack_forget()

    def save(self):
        new_config = {"type": self.var_printer_type.get(), "usb_vendor_id": self.var_usb_vid.get(), "usb_product_id": self.var_usb_pid.get(), "network_ip": self.var_net_ip.get()}
        self.master.settings["printer_config"] = new_config; self.master.save_settings(); self.destroy()

class TextEditorWindow(simpledialog.Dialog):
    def __init__(self, parent, title=None, initial_text="", instructions=""):
        self.initial_text=initial_text; self.instructions=instructions; self.result=None
        super().__init__(parent, title)
    def body(self, master):
        if self.instructions: b.Label(master, text=self.instructions, wraplength=480).pack(pady=5)
        self.text = b.Text(master, width=80, height=20, wrap="word"); self.text.pack(fill="both", expand=True)
        self.text.insert("1.0", self.initial_text); return self.text
    def apply(self): self.result = self.text.get("1.0", "end-1c")

class ReportWindow(b.Toplevel):
    def __init__(self, master, title, text_content):
        super().__init__(master); self.title(title); self.geometry("500x600")
        text = b.Text(self, wrap="word", font=("Courier", 10), relief=FLAT); text.pack(fill=BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", text_content); text.config(state="disabled")
        b.Button(self, text="Chiudi", command=self.destroy, bootstyle="secondary").pack(pady=10)

class ReceiptWindow(b.Toplevel):
    def __init__(self, master, receipt_id, lines, total, title_text, note_lines, logo_path, discount_amount=0.0):
        super().__init__(master)
        self.master=master; self.title(f"Scontrino {receipt_id}"); self.geometry("520x620")
        self.receipt_id, self.lines, self.total = receipt_id, lines, total
        self.title_text, self.note_lines, self.logo_path = title_text, note_lines, logo_path
        self.discount_amount = discount_amount
        
        bar = b.Frame(self); bar.pack(fill=X,padx=8,pady=(8,4))
        b.Button(bar,text="Salva TXT", command=self.save_txt, bootstyle="secondary").pack(side=LEFT)
        b.Button(bar,text="Salva HTML", command=self.save_html, bootstyle="secondary").pack(side=LEFT,padx=6)
        if REPORTLAB_AVAILABLE: b.Button(bar,text="Esporta PDF", command=self.export_pdf, bootstyle="secondary").pack(side=LEFT)
        print_frame = b.Frame(bar); print_frame.pack(side=RIGHT)
        b.Button(print_frame,text="Stampa A4", command=self.print_receipt_standard, bootstyle="info").pack(side=RIGHT)
        btn_thermal = b.Button(print_frame,text="Stampa Termica", command=self.print_receipt_thermal, bootstyle="primary")
        btn_thermal.pack(side=RIGHT, padx=6)
        if not ESCPOS_AVAILABLE: btn_thermal.config(state="disabled")

        self.text = b.Text(self, wrap="word", font=("Courier New", 10)); self.text.pack(fill=BOTH, expand=True,padx=8,pady=8)
        self.text.insert("1.0", self._render_text()); self.text.configure(state="disabled")
        b.Button(self,text="Chiudi",command=self.destroy, bootstyle="secondary").pack(pady=4)

    def _render_text(self) -> str:
        # --- MODIFICA GRAFICA: Layout anteprima aggiornato ---
        width = 48
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        subtotal = self.total + self.discount_amount
        
        output = [
            f"{self.title_text:^{width}}", 
            "="*width, 
            f"ID: {self.receipt_id}".ljust(width//2) + f"Data: {now}".rjust(width//2), 
            "-"*width
        ]
        for line in self.lines:
            name, qty, unit, line_total = line["item"]["name"], line["qty"], line["unit"], line["subtotal"]
            output.append(f"{name}")
            line1 = f"  {int(qty)} x {money(unit)}"
            line2 = f"{money(line_total)}"
            output.append(line1.ljust(width - len(line2)) + line2)
        
        output.append("-" * width)
        
        if self.discount_amount > 0:
            sub_label, sub_value = "Subtotale:", money(subtotal)
            output.append(sub_label.ljust(width - len(sub_value)) + sub_value)
            
            disc_label, disc_value = "Sconto:", f"-{money(self.discount_amount)}"
            output.append(disc_label.ljust(width - len(disc_value)) + disc_value)
            output.append("") # Spazio
            
        total_label, total_value = "TOTALE:", money(self.total)
        output.append(total_label.ljust(width - len(total_value)) + total_value)
        output.append("=" * width)
        
        if self.note_lines: 
            output.append("")
            output.extend([f"{note:^{width}}" for note in self.note_lines])
        return "\n".join(output)

    def save_txt(self):
        path=filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"scontrino-{self.receipt_id}.txt", parent=self)
        if path: Path(path).write_text(self._render_text(), encoding="utf-8"); messagebox.showinfo(APP_TITLE,"Scontrino salvato (TXT)")

    def save_html(self):
        path=filedialog.asksaveasfilename(defaultextension=".html", initialfile=f"scontrino-{self.receipt_id}.html", parent=self)
        if path:
            html = f'<html><head><style>pre{{font-family:monospace;}}</style></head><body>'
            if self.logo_path and os.path.exists(self.logo_path): html += f'<img src="{Path(self.logo_path).as_uri()}" alt="logo" style="max-width:200px;display:block;margin:auto;"><br>'
            html += f'<pre>{self._render_text()}</pre></body></html>'
            Path(path).write_text(html, encoding="utf-8"); messagebox.showinfo(APP_TITLE, "Scontrino salvato (HTML)")

    def export_pdf(self):
        if not REPORTLAB_AVAILABLE: messagebox.showwarning(APP_TITLE,"Installa reportlab per PDF"); return
        path=filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"scontrino-{self.receipt_id}.pdf", parent=self)
        if not path: return
        c=pdf_canvas.Canvas(path,pagesize=A4); w,h=A4; y=h-40; c.setFont("Courier", 10)
        if self.logo_path and os.path.exists(self.logo_path):
            try: img = ImageReader(self.logo_path); w_img,h_img = img.getSize(); c.drawImage(self.logo_path, (A4[0]-100)/2, y-50, width=100, height=100*(h_img/float(w_img))); y -= (100*(h_img/float(w_img))) + 20
            except: pass
        for line in self._render_text().splitlines(): c.drawString(40,y,line); y-=12
        c.showPage(); c.save(); messagebox.showinfo(APP_TITLE,"Scontrino esportato in PDF")

    def print_receipt_standard(self):
        tmp=WRITABLE_DIR/f"scontrino_temp-{self.receipt_id}.txt"; tmp.write_text(self._render_text(), encoding="utf-8")
        try:
            if platform.system()=="Darwin": subprocess.run(["lp",str(tmp)],check=True)
            elif platform.system() == "Windows": os.startfile(str(tmp), "print")
            else: subprocess.run(["lp", str(tmp)], check=True)
            messagebox.showinfo(APP_TITLE,"Inviato alla stampante standard.")
        except Exception as e: messagebox.showerror(APP_TITLE,f"Errore stampa: {e}\nFile in {tmp}")

    def print_receipt_thermal(self):
        config = self.master.settings.get("printer_config", {})
        try:
            printer = None
            if config.get("type") == "usb": printer = Usb(int(config.get("usb_vendor_id","0"),16), int(config.get("usb_product_id","0"),16), timeout=0, in_ep=0x81, out_ep=0x03)
            elif config.get("type") == "network": printer = Network(host=config.get("network_ip", ""))
            else: messagebox.showerror("Errore", "Stampante termica non configurata."); return

            # --- MODIFICA GRAFICA: Nuovo layout di stampa termica ---
            width = 48
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # --- Intestazione ---
            printer.set(align='center', text_type='b'); printer.text(self.title_text + "\n"); printer.set(align='center')
            printer.text("="*width + "\n")
            header_l = f"ID: {self.receipt_id}"; header_r = f"Data: {now}"
            printer.text(header_l.ljust(width - len(header_r)) + header_r + "\n")
            printer.text("-"*width + "\n")
            
            # --- Articoli ---
            printer.set(align='left', text_type='normal')
            for line in self.lines:
                name, qty, unit, subtotal = line["item"]["name"], line["qty"], line["unit"], line["subtotal"]
                printer.text(f"{name}\n")
                line1 = f"  {int(qty)} x {money(unit)}"; line2 = f"{money(subtotal)}"
                printer.text(line1.ljust(width - len(line2)) + line2 + "\n")
            
            printer.text("-"*width + "\n")
            
            # --- Totali ---
            if self.discount_amount > 0:
                subtotal = self.total + self.discount_amount
                sub_label, sub_value = "Subtotale:", money(subtotal)
                printer.text(sub_label.ljust(width - len(sub_value)) + sub_value + "\n")
                disc_label, disc_value = "Sconto:", f"-{money(self.discount_amount)}"
                printer.text(disc_label.ljust(width - len(disc_value)) + disc_value + "\n")
            
            printer.feed(1) # Spazio prima del totale
            total_label, total_value = "TOTALE", money(self.total)
            printer.set(align='right', text_type='b', width=2, height=2)
            printer.text(f"{total_label} {total_value}\n")
            printer.set(align='center', text_type='normal', width=1, height=1)
            printer.feed(1) # Spazio dopo il totale

            # --- Note finali ---
            printer.text("="*width + "\n\n")
            if self.note_lines: 
                printer.text("\n".join(self.note_lines) + "\n\n")
            
            # --- Stampa Talloncini automatici ---
            tickets_printed = False
            for line_data in self.lines:
                qty, ticket_text = int(line_data["qty"]), line_data["item"].get("ticket_text", "").strip()
                if ticket_text:
                    tickets_printed = True
                    for _ in range(qty):
                        printer.set(align='center', text_type='b', width=2, height=2); printer.text(f"{ticket_text}\n"); printer.set(align='center', text_type='normal')
                        printer.text(f"ID: {self.receipt_id} Ora: {now[11:]}\n")
                        printer.feed(3)
                        printer.cut()
            
            # Taglio finale dello scontrino
            if not tickets_printed:
                printer.feed(3)
                printer.cut()

            messagebox.showinfo("Successo", "Scontrino e foglietti inviati alla stampante.")
        except Exception as e: messagebox.showerror("Errore Stampa Termica", f"Impossibile stampare.\nVerifica connessione e impostazioni.\n\nDettagli: {e}")

# ---------- Main ----------
if __name__=="__main__":
    app=StandFacileApp()
    app.mainloop()