import pandas as pd
import os, shutil, subprocess, re
import webbrowser
from tkinter import *
from tkinter import messagebox, filedialog, scrolledtext, Toplevel
from PIL import Image, ImageTk
# --- LIBRERIE PDF MODIFICATE ---
try:
    import PyPDF2
    import extract_msg
    from fpdf import FPDF # <-- Nuova libreria per creare PDF
except ImportError:
    messagebox.showerror("Librerie Mancanti", "Esegui 'pip install PyPDF2 extract-msg fpdf2' nel terminale.")
    exit()

# --- Configurazione ---
STATES = ['Fatturato','Da fatturare','Da lavorare','Annullato','Permessi da pagare']
Excel_FILE = 'IMPIANTI COS.xlsx'
SHEET_NAME = 'Impianti cos Catania'
PDF_DIR = 'pdf_pratiche'
ATTACH_ROOT = 'allegati'
for d in (PDF_DIR, ATTACH_ROOT): os.makedirs(d, exist_ok=True)
ALL_COLUMNS = (
    ['DTU','WR','WR COS','NTW COS','IMPIANTO','CENTRALE','TIPOLOGIA','IMPRESA REALIZZATRICE'] +
    ['CLIENTE','RECAPITO','INDIRIZZO', 'Coordinate'] +
    ['NOTE', 'NOTE 2', 'MDB', 'DIRITTI FISSI'] +
    ['FINE LAVORI (CRE)', 'INVIO RL'] +
    STATES + ['Allegato','Mail Preventivo','Totale Preventivo']
)

# --- Gestione Dati ---
def load_df():
    try:
        df = pd.read_excel(Excel_FILE, sheet_name=SHEET_NAME, dtype=str).fillna('')
        for col in ALL_COLUMNS:
            if col not in df.columns: df[col] = ''
        return df
    except FileNotFoundError:
        messagebox.showinfo("File non Trovato", f"Il file '{Excel_FILE}' non è stato trovato.\nNe verrà creato uno nuovo.")
        try:
            df = pd.DataFrame(columns=ALL_COLUMNS)
            df.to_excel(Excel_FILE, index=False, sheet_name=SHEET_NAME)
            return df
        except Exception as e: messagebox.showerror("Errore Creazione File", f"Impossibile creare il file Excel.\n{e}"); return None
    except Exception as e: messagebox.showerror("Errore Caricamento", f"Impossibile leggere il file Excel.\n{e}"); return None

# --- Funzioni ---
def open_gmaps():
    coords = secB_items['Coordinate'].get().strip()
    if coords and ',' in coords:
        webbrowser.open_new_tab(f"https://www.google.com/maps/search/?api=1&query={coords}")
    else: messagebox.showwarning("Info", "Coordinate non valide o mancanti.")

def format_date(v):
    try: return pd.to_datetime(v, dayfirst=True).strftime('%d/%m/%y')
    except: return v

def orig_index():
    if not filtered.empty and idx < len(filtered):
        original_indices = df.index[df.apply(lambda r: r.equals(filtered.iloc[idx]), axis=1)].tolist()
        if original_indices: return original_indices[0]
    return None

def check_for_changes():
    if new_mode: return True
    if filtered.empty or idx >= len(filtered): return False
    gui_data = {}
    all_items = {**secA_items, **secB_items, **secC_items, **secD_items}
    for k, w in all_items.items():
        gui_data[k] = w.get('1.0', END).strip() if isinstance(w, scrolledtext.ScrolledText) else w.get()
    gui_data['Mail Preventivo'] = ent_mail_var.get(); gui_data['Totale Preventivo'] = entot.get()
    gui_data['Allegato'] = '|'.join(attachments)
    for st, var in check_vars.items(): gui_data[st] = 'SI' if var.get() else 'NO'
    original_rec = filtered.iloc[idx].to_dict()
    for key, gui_value in gui_data.items():
        if str(gui_value).strip() != str(original_rec.get(key, '')).strip(): return True
    return False

def check_and_proceed(action_to_take):
    if check_for_changes():
        response = messagebox.askyesnocancel("Salvare?", "Ci sono modifiche non salvate. Vuoi salvarle?")
        if response is True: save_rec()
        elif response is False: action_to_take()
    else: action_to_take()

def load_rec():
    global attachments, new_mode
    if filtered.empty: messagebox.showinfo('Info','Nessun record trovato.'); clear_fields(); return
    new_mode = False
    rec = filtered.iloc[idx]
    all_items = {**secA_items, **secB_items, **secC_items, **secD_items}
    for k,w in all_items.items():
        value_to_insert = rec.get(k, '')
        if isinstance(w, scrolledtext.ScrolledText):
            w.delete('1.0', END); w.insert('1.0', value_to_insert)
        else:
            w.delete(0, END); w.insert(0, format_date(value_to_insert))
    ent_mail_var.set(rec.get('Mail Preventivo', '')); update_mail_indicator(bool(rec.get('Mail Preventivo')))
    entot.delete(0, END); entot.insert(0, rec.get('Totale Preventivo', ''))
    attachments = rec.get('Allegato', '').split('|') if rec.get('Allegato') else []
    refresh_attachment_list()
    for st,var in check_vars.items(): var.set(1 if rec.get(st)=='SI' else 0)
    status_label.config(text=f'Record {idx+1} di {len(filtered)}')

def clear_fields():
    global attachments, new_mode
    all_items = {**secA_items, **secB_items, **secC_items, **secD_items}
    for w in all_items.values():
        if isinstance(w, scrolledtext.ScrolledText): w.delete('1.0', END)
        else: w.delete(0, END)
    ent_mail_var.set(''); update_mail_indicator(False); entot.delete(0, END)
    attachments, new_mode = [], False; refresh_attachment_list()
    for var in check_vars.values(): var.set(0)
    status_label.config(text='Nessun record caricato'); search_var.set(''); status_filter.set('Tutti')

def nav(dest):
    if 0 <= dest < len(filtered):
        global idx, new_mode
        idx, new_mode = dest, False
        load_rec()

def new_rec():
    global new_mode, attachments
    clear_fields(); attachments, new_mode = [], True
    status_label.config(text='Nuova pratica (non salvata)')

def save_rec():
    global df, new_mode, idx
    data = {}
    all_items = {**secA_items, **secB_items, **secC_items, **secD_items}
    for k,w in all_items.items(): data[k] = w.get('1.0', END).strip() if isinstance(w, scrolledtext.ScrolledText) else w.get()
    data['Mail Preventivo'] = ent_mail_var.get(); data['Totale Preventivo'] = entot.get(); data['Allegato'] = '|'.join(attachments)
    for st, var in check_vars.items(): data[st] = 'SI' if var.get() else 'NO'
    original_idx_val = orig_index() if not new_mode else None
    if new_mode:
        df = pd.concat([df, pd.Series(data).to_frame().T], ignore_index=True)
        messagebox.showinfo('Salvato', 'Nuova pratica salvata.')
    else:
        if original_idx_val is not None:
            for key, value in data.items():
                if key in df.columns: df.at[original_idx_val, key] = value
            messagebox.showinfo('Salvato', 'Modifiche salvate.')
        else: messagebox.showerror("Errore", "Impossibile trovare il record da aggiornare."); return
    new_mode = False
    try:
        df.to_excel(Excel_FILE, index=False, sheet_name=SHEET_NAME)
    except Exception as e: messagebox.showerror("Errore di Salvataggio", f"Impossibile salvare il file Excel.\n{e}"); return
    current_dtu = data['DTU']
    on_search(reloading=True)
    found_idx = filtered.index[filtered['DTU'] == current_dtu].tolist()
    idx = found_idx[0] if found_idx else (len(filtered) - 1 if not filtered.empty else 0)
    if not filtered.empty: load_rec()

def on_search(reloading=False):
    global filtered, idx, new_mode
    term, stf = search_var.get().strip(), status_filter.get()
    tmp_df = df.copy()
    if term: tmp_df = tmp_df[tmp_df.apply(lambda row: row.astype(str).str.contains(term, case=False, na=False)).any(axis=1)]
    if stf != 'Tutti':
        if stf == 'Parcheggiati': tmp_df = tmp_df[~tmp_df[STATES].eq('SI').any(axis=1)]
        else: tmp_df = tmp_df[tmp_df[stf] == 'SI']
    filtered, idx, new_mode = tmp_df.reset_index(drop=True), 0, False
    if not reloading:
        if not filtered.empty: load_rec()
        else: clear_fields(); status_label.config(text="Nessun record corrisponde.")

def refresh_attachment_list():
    listbox_attachments.delete(0, END)
    for f in attachments: listbox_attachments.insert(END, os.path.basename(f))

def add_attach():
    files = filedialog.askopenfilenames(title='Seleziona allegati')
    if not files: return
    folder_name = f"{secA_items['DTU'].get() or 'senza_dtu'} - {secB_items['INDIRIZZO'].get('1.0',END).strip().replace('/','-') or 'senza_indirizzo'}"
    attach_folder = os.path.join(ATTACH_ROOT, folder_name)
    os.makedirs(attach_folder, exist_ok=True)
    for f_path in files:
        try:
            dst = shutil.copy(f_path, attach_folder)
            if dst not in attachments: attachments.append(dst)
        except Exception as e: messagebox.showwarning("Errore Copia", f"Impossibile copiare il file {os.path.basename(f_path)}.\n{e}")
    refresh_attachment_list()

def rem_attach():
    selected_indices = listbox_attachments.curselection()
    if not selected_indices: messagebox.showinfo("Info", "Seleziona un allegato.")
    for i in reversed(selected_indices): attachments.pop(i)
    refresh_attachment_list()

def open_attach():
    sel = listbox_attachments.curselection()
    if sel:
        try: os.startfile(attachments[sel[0]])
        except Exception as e: messagebox.showerror("Errore Apertura", f"Impossibile aprire il file.\n{e}")

def load_mail():
    filepath = filedialog.askopenfilename(title='Seleziona Preventivo', filetypes=[("File supportati", "*.pdf *.msg *.eml *.txt"), ("Tutti i file", "*.*")])
    if not filepath: return
    try:
        folder_name = f"{secA_items['DTU'].get() or 'senza_dtu'} - {secB_items['INDIRIZZO'].get('1.0',END).strip().replace('/','-') or 'senza_indirizzo'}"
        attach_folder = os.path.join(ATTACH_ROOT, folder_name)
        os.makedirs(attach_folder, exist_ok=True)
        dst = shutil.copy(filepath, attach_folder)
        if dst not in attachments: attachments.append(dst)
        refresh_attachment_list()
    except Exception as e: messagebox.showerror("Errore Salvataggio Allegato", f"Impossibile copiare il file.\n{e}"); return
    text = ""
    try:
        if filepath.lower().endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f); text = "".join(p.extract_text() or "" for p in reader.pages)
        elif filepath.lower().endswith('.msg'): text = extract_msg.Message(filepath).body
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: text = f.read()
    except Exception as e: messagebox.showerror("Errore Lettura File", f"Impossibile leggere il contenuto.\n{e}")
    ent_mail_var.set(text); update_mail_indicator(True)
    match = re.search(r"TOTALE CON MATERIALI\s*€?\s*([0-9.,]+)", text, re.IGNORECASE)
    if not match: match = re.search(r"Totale[:\s]*€?\s*([0-9.,]+)", text, re.IGNORECASE)
    if match:
        total_str = match.group(1).replace('.', '').replace(',', '.')
        try: entot.delete(0, END); entot.insert(0, f"{float(total_str):.2f}")
        except ValueError: pass

def update_mail_indicator(has_mail):
    mail_indicator.config(text='✓' if has_mail else '✗', fg='green' if has_mail else 'red')

# --- FUNZIONE EXPORT PDF CORRETTA ---
def export_pdf():
    if filtered.empty: messagebox.showwarning("Attenzione", "Nessuna pratica da esportare."); return
    rec = filtered.iloc[idx].to_dict()
    safe_filename = f"pratica_{rec.get('DTU', idx+1)}.pdf".replace('/', '-').replace('\\', '-')
    final_pdf_path = os.path.join(PDF_DIR, safe_filename)
    
    temp_pdfs, pid = [], os.getpid()
    
    # 1. Crea pagina di riepilogo
    temp_data_pdf = os.path.join(PDF_DIR, f"temp_data_{pid}.pdf")
    temp_pdfs.append(temp_data_pdf)
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Riepilogo Pratica: {rec.get('DTU', '')}", 0, 1, 'C')
        pdf.ln(10)

        items_to_export = {k: v for k, v in rec.items() if k != 'Allegato'}
        for k, v in items_to_export.items():
            if v is not None and pd.notna(v) and str(v).strip():
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 5, f"{k}:", 0, 1)
                pdf.set_font("Helvetica", "", 10)
                clean_v = str(v).replace('_x000D_', '').replace('\r', '')
                pdf.multi_cell(0, 5, clean_v.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(2)
        pdf.output(temp_data_pdf)
    except Exception as e: messagebox.showerror("Errore PDF", f"Impossibile creare pagina riepilogo.\n{e}"); return

    # 2. Processa allegati
    current_attachments = rec.get('Allegato', '').split('|') if rec.get('Allegato') else []
    attach_counter = 0
    temp_email_attach_dir = os.path.join(ATTACH_ROOT, f"temp_email_attachments_{pid}")
    
    for attach_path in current_attachments:
        if not os.path.exists(attach_path): continue
        try:
            attach_counter += 1
            temp_attach_pdf = os.path.join(PDF_DIR, f"temp_attach_{attach_counter}_{pid}.pdf")
            
            if attach_path.lower().endswith('.pdf'):
                shutil.copyfile(attach_path, temp_attach_pdf); temp_pdfs.append(temp_attach_pdf)
            
            elif attach_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                pdf = FPDF(); pdf.add_page(); pdf.image(attach_path, x=10, y=10, w=190); pdf.output(temp_attach_pdf); temp_pdfs.append(temp_attach_pdf)
            
            elif attach_path.lower().endswith('.msg'):
                msg = extract_msg.Message(attach_path)
                if msg.attachments:
                    os.makedirs(temp_email_attach_dir, exist_ok=True)
                    for email_attach in msg.attachments:
                        if email_attach.long_filename and os.path.splitext(email_attach.long_filename)[1]:
                            email_attach.save(custom_path=temp_email_attach_dir)
                            saved_path = os.path.join(temp_email_attach_dir, email_attach.long_filename)
                            if os.path.exists(saved_path):
                                attach_counter += 1; temp_attach_pdf_inner = os.path.join(PDF_DIR, f"temp_attach_{attach_counter}_{pid}.pdf")
                                if saved_path.lower().endswith('.pdf'):
                                    shutil.copyfile(saved_path, temp_attach_pdf_inner); temp_pdfs.append(temp_attach_pdf_inner)
                                elif saved_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                    pdf_img = FPDF(); pdf_img.add_page(); pdf_img.image(saved_path, x=10, y=10, w=190); pdf_img.output(temp_attach_pdf_inner); temp_pdfs.append(temp_attach_pdf_inner)
        except Exception as e: messagebox.showwarning("Errore Allegato", f"Impossibile processare {os.path.basename(attach_path)}.\n{e}")
    # 3. Unisce i PDF
    try:
        pdf_writer = PyPDF2.PdfWriter()
        for path in temp_pdfs:
            if os.path.exists(path):
                pdf_reader = PyPDF2.PdfReader(path)
                for page in pdf_reader.pages: pdf_writer.add_page(page)
        with open(final_pdf_path, 'wb') as f_out: pdf_writer.write(f_out)
        messagebox.showinfo('PDF Creato', f"Esportato con successo in:\n{os.path.abspath(final_pdf_path)}")
    except Exception as e: messagebox.showerror("Errore Unione PDF", f"Impossibile unire i PDF.\n{e}")
    finally:
        for path in temp_pdfs:
            if os.path.exists(path): os.remove(path)
        if os.path.exists(temp_email_attach_dir): shutil.rmtree(temp_email_attach_dir)

def on_exit(): check_and_proceed(root.destroy)

# --- GUI Setup ---
if __name__ == "__main__":
    df = load_df()
    if df is None:
        exit()

    filtered = df.copy()
    idx = 0
    new_mode = False
    attachments = []

    root = Tk()
    root.title('Gestione Pratiche')
    root.geometry('1200x800')
    root.protocol('WM_DELETE_WINDOW', on_exit)
    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=1)
    search_var, status_filter, ent_mail_var = StringVar(root), StringVar(root, value='Tutti'), StringVar(root)
    
    # ... (Il resto della GUI rimane invariato)
    frm_search = Frame(main_frame)
    frm_search.grid(row=0, column=0, columnspan=4, sticky='we', padx=10, pady=10)
    Label(frm_search, text='Cerca:').pack(side=LEFT, padx=(0,5)); Entry(frm_search, textvariable=search_var, width=30).pack(side=LEFT)
    Label(frm_search, text='Filtra Stato:').pack(side=LEFT, padx=(10,5)); OptionMenu(frm_search, status_filter, *(['Tutti'] + STATES + ['Parcheggiati'])).pack(side=LEFT)
    Button(frm_search, text='Applica', command=on_search).pack(side=LEFT, padx=5); Button(frm_search, text='Reset', command=lambda: (clear_fields(), on_search())).pack(side=LEFT)

    secA = LabelFrame(main_frame, text='A - Info Tecnica', padx=10, pady=10); secA.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
    secA_items, secA_keys = {}, ['DTU','WR','WR COS','NTW COS','IMPIANTO','CENTRALE','TIPOLOGIA','IMPRESA REALIZZATRICE']
    for i, key in enumerate(secA_keys):
        Label(secA, text=key).grid(row=i, column=0, sticky='w', pady=2); e = Entry(secA, bd=2, relief='groove', width=25); e.grid(row=i, column=1, sticky='we'); secA_items[key] = e

    secB = LabelFrame(main_frame, text='B - Cliente', padx=10, pady=10); secB.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
    secB_items = {}
    for i, key in enumerate(['CLIENTE','RECAPITO','INDIRIZZO']):
        Label(secB, text=key).grid(row=i, column=0, sticky='nw', pady=2); st = scrolledtext.ScrolledText(secB, width=40, height=2 if key != 'INDIRIZZO' else 3, bd=2, relief='sunken'); st.grid(row=i, column=1, sticky='we'); secB_items[key] = st
    Label(secB, text="Coordinate").grid(row=3, column=0, sticky='nw', pady=2); coord_entry = Entry(secB, bd=2, relief='groove'); coord_entry.grid(row=3, column=1, sticky='we'); secB_items['Coordinate'] = coord_entry
    Button(secB, text="🌍 Apri Mappa", command=open_gmaps).grid(row=4, column=1, sticky='e', pady=(5,0))

    att_frame = LabelFrame(main_frame, text='Allegati', padx=10, pady=10); att_frame.grid(row=1, column=2, rowspan=4, columnspan=2, sticky='nsew', padx=10, pady=5)
    listbox_attachments = Listbox(att_frame, height=10); listbox_attachments.grid(row=0, column=0, sticky='nsew', pady=5)
    sb = Scrollbar(att_frame, orient=VERTICAL, command=listbox_attachments.yview); sb.grid(row=0, column=1, sticky='ns', pady=5); listbox_attachments.config(yscrollcommand=sb.set)
    btn_att_frame = Frame(att_frame); btn_att_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
    Button(btn_att_frame, text='Aggiungi', command=add_attach).pack(side=LEFT, expand=True, fill=X); Button(btn_att_frame, text='Rimuovi', command=rem_attach).pack(side=LEFT, expand=True, fill=X); Button(btn_att_frame, text='Apri', command=open_attach).pack(side=LEFT, expand=True, fill=X)
    att_frame.grid_columnconfigure(0, weight=1)

    gstatus = LabelFrame(main_frame, text='Stato pratica', padx=10, pady=10); gstatus.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=10, pady=5)
    check_vars = {}
    for st in STATES: var = IntVar(); Checkbutton(gstatus, text=st, variable=var).pack(side=LEFT, padx=10); check_vars[st] = var

    secC = LabelFrame(main_frame, text='C - Fatturazione e Preventivo', padx=10, pady=10); secC.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=10, pady=5)
    secC_items = {}
    Label(secC, text='NOTE').grid(row=0, column=0, sticky='nw', pady=(2,10)); n1 = scrolledtext.ScrolledText(secC, width=60, height=3, bd=2, relief='sunken'); n1.grid(row=0, column=1, columnspan=3, sticky='nsew', pady=2); secC_items['NOTE'] = n1
    Label(secC, text='NOTE 2').grid(row=1, column=0, sticky='nw', pady=(2,10)); n2 = scrolledtext.ScrolledText(secC, width=60, height=2, bd=2, relief='sunken'); n2.grid(row=1, column=1, columnspan=3, sticky='nsew', pady=2); secC_items['NOTE 2'] = n2
    Label(secC, text='MDB').grid(row=2, column=0, sticky='nw', pady=2); w = scrolledtext.ScrolledText(secC, width=20, height=2, bd=2, relief='sunken'); w.grid(row=2, column=1, sticky='nsew'); secC_items['MDB'] = w
    Label(secC, text='DIRITTI FISSI').grid(row=2, column=2, sticky='nw', padx=(10,0), pady=2); w2 = Entry(secC, width=20, bd=2, relief='groove'); w2.grid(row=2, column=3, sticky='we'); secC_items['DIRITTI FISSI'] = w2
    preventivo_frame = Frame(secC); preventivo_frame.grid(row=3, column=0, columnspan=4, sticky='we', pady=(15,0))
    Button(preventivo_frame, text='Carica Preventivo', command=load_mail).pack(side=LEFT)
    mail_indicator = Label(preventivo_frame, text='✗', fg='red', font=('Helvetica', 10, 'bold')); mail_indicator.pack(side=LEFT, padx=5)
    Label(preventivo_frame, text='Totale').pack(side=LEFT, padx=(20,5)); entot = Entry(preventivo_frame, width=15, bd=2, relief='groove'); entot.pack(side=LEFT)

    secD = LabelFrame(main_frame, text='D - Lavori e Invio', padx=10, pady=10); secD.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=10, pady=5)
    secD_items = {}
    for i, key in enumerate(['FINE LAVORI (CRE)', 'INVIO RL']):
        Label(secD, text=key).grid(row=0, column=2*i, sticky='w', padx=5); e = Entry(secD, bd=2, relief='groove', width=20); e.grid(row=0, column=2*i+1, sticky='we', padx=5); secD_items[key] = e
    secD.grid_columnconfigure(1, weight=1); secD.grid_columnconfigure(3, weight=1)

    cmd_frame = Frame(main_frame); cmd_frame.grid(row=5, column=0, columnspan=4, sticky='w', padx=10, pady=10)
    cmds = [('Prev', lambda: check_and_proceed(lambda: nav(idx - 1))), ('Next', lambda: check_and_proceed(lambda: nav(idx + 1))), ('New', lambda: check_and_proceed(new_rec)), ('Save', save_rec), ('Export PDF', export_pdf), ('Exit', on_exit)]
    for txt, cmd in cmds: Button(cmd_frame, text=txt, command=cmd, width=12).pack(side=LEFT, padx=2)

    status_label = Label(main_frame, text='', bd=1, relief=SUNKEN, anchor='w'); status_label.grid(row=6, column=0, columnspan=4, sticky='we', padx=10, pady=(5,10))
    for i in range(3): main_frame.grid_columnconfigure(i, weight=1); main_frame.grid_rowconfigure(i+1, weight=1)
    
    # --- LOGICA DI AVVIO CORRETTA ---
    if not df.empty:
         load_rec()
    else:
         new_rec()
    root.mainloop()