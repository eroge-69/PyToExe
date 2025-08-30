import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, json, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader

DATA_PATH = "stein_data.json"

def load_docs():
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_docs(docs):
    with open(DATA_PATH,"w",encoding="utf-8") as f:
        json.dump(docs,f,indent=2,ensure_ascii=False)

class SteinApp:
    def __init__(self, root):
        self.root = root
        root.title("Stein - Professionelles Dokumenten Tool")
        root.geometry("1100x700")
        root.configure(bg="#f9f9f9")

        self.docs = load_docs()
        self.selected_id = None
        self.logo_path = None

        # Stil ayarları
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure("Treeview", rowheight=28, font=("Segoe UI",10))
        style.configure("Treeview.Heading", font=("Segoe UI",10,"bold"))

        # Sol Panel
        self.left_frame = tk.Frame(root, width=250, bg="#e0e0e0")
        self.left_frame.pack(side="left", fill="y", padx=5, pady=5)
        tk.Label(self.left_frame, text="Dokumente", font=("Segoe UI",12,"bold"), bg="#e0e0e0").pack(pady=5)
        self.listbox = tk.Listbox(self.left_frame)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        btn_bg = "#0078d7"
        btn_fg = "white"
        tk.Button(self.left_frame,text="Neu",command=self.new_doc,bg=btn_bg,fg=btn_fg).pack(fill="x", padx=5,pady=2)
        tk.Button(self.left_frame,text="Speichern",command=self.save_doc,bg=btn_bg,fg=btn_fg).pack(fill="x", padx=5,pady=2)
        tk.Button(self.left_frame,text="Logo auswählen",command=self.select_logo,bg=btn_bg,fg=btn_fg).pack(fill="x", padx=5,pady=2)
        tk.Button(self.left_frame,text="Export PDF",command=self.export_pdf,bg=btn_bg,fg=btn_fg).pack(fill="x", padx=5,pady=2)

        # Sağ Panel
        self.right_frame = tk.Frame(root,bg="#f9f9f9")
        self.right_frame.pack(side="right",fill="both",expand=True,padx=10,pady=10)

        self.create_form()
        self.refresh_list()

    def create_form(self):
        labels = ["Dokumenttyp:","Nummer:","Datum:","Firma:","Kunde:","Notiz:"]
        self.typ_var = tk.StringVar(value="Angebot")
        self.nr_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.date.today().isoformat())
        self.firma_var = tk.StringVar()
        self.kunde_var = tk.StringVar()

        row=0
        tk.Label(self.right_frame,text=labels[0],bg="#f9f9f9").grid(row=row,column=0,sticky="e", pady=2)
        ttk.Combobox(self.right_frame,textvariable=self.typ_var,values=["Angebot","Rechnung","Auftragsbestätigung"]).grid(row=row,column=1,sticky="w")
        row+=1
        tk.Label(self.right_frame,text=labels[1],bg="#f9f9f9").grid(row=row,column=0,sticky="e", pady=2)
        tk.Entry(self.right_frame,textvariable=self.nr_var).grid(row=row,column=1,sticky="w")
        row+=1
        tk.Label(self.right_frame,text=labels[2],bg="#f9f9f9").grid(row=row,column=0,sticky="e", pady=2)
        tk.Entry(self.right_frame,textvariable=self.date_var).grid(row=row,column=1,sticky="w")
        row+=1
        tk.Label(self.right_frame,text=labels[3],bg="#f9f9f9").grid(row=row,column=0,sticky="e", pady=2)
        tk.Entry(self.right_frame,textvariable=self.firma_var,width=40).grid(row=row,column=1,sticky="w")
        row+=1
        tk.Label(self.right_frame,text=labels[4],bg="#f9f9f9").grid(row=row,column=0,sticky="e", pady=2)
        tk.Entry(self.right_frame,textvariable=self.kunde_var,width=40).grid(row=row,column=1,sticky="w")
        row+=1
        tk.Label(self.right_frame,text=labels[5],bg="#f9f9f9").grid(row=row,column=0,sticky="ne", pady=2)
        self.notiz_txt = tk.Text(self.right_frame,width=40,height=4)
        self.notiz_txt.grid(row=row,column=1,sticky="w")
        row+=1

        # Treeview Positionen
        tk.Label(self.right_frame,text="Positionen:",bg="#f9f9f9").grid(row=row,column=0,sticky="ne", pady=2)
        self.tree = ttk.Treeview(self.right_frame, columns=("Name","Menge","Preis","MwSt"), show="headings", height=12)
        for col in ("Name","Menge","Preis","MwSt"):
            self.tree.heading(col,text=col)
            self.tree.column(col,width=100)
        self.tree.grid(row=row,column=1,sticky="w")
        row+=1
        tk.Button(self.right_frame,text="+ Position",command=self.add_row,bg="#0078d7",fg="white").grid(row=row,column=1,sticky="w",pady=2)
        tk.Button(self.right_frame,text="- Position",command=self.remove_row,bg="#d9534f",fg="white").grid(row=row,column=1,sticky="e",pady=2)

    def add_row(self):
        self.tree.insert("", "end", values=("Produkt","1","0.0","19"))

    def remove_row(self):
        sel = self.tree.selection()
        for i in sel: self.tree.delete(i)

    def select_logo(self):
        path=filedialog.askopenfilename(filetypes=[("Bilder","*.png;*.jpg;*.jpeg")])
        if path:
            self.logo_path=path
            messagebox.showinfo("Logo","Logo ausgewählt!")

    def refresh_list(self):
        self.listbox.delete(0,"end")
        for d in self.docs:
            self.listbox.insert("end", f"{d['typ']} {d['nr']} - {d['kunde']}")

    def on_select(self, evt):
        idxs=self.listbox.curselection()
        if not idxs: return
        idx=idxs[0]
        doc=self.docs[idx]
        self.selected_id=idx
        self.typ_var.set(doc["typ"])
        self.nr_var.set(doc["nr"])
        self.date_var.set(doc["datum"])
        self.firma_var.set(doc["firma"])
        self.kunde_var.set(doc["kunde"])
        self.notiz_txt.delete("1.0","end")
        self.notiz_txt.insert("1.0",doc.get("notiz",""))
        for i in self.tree.get_children(): self.tree.delete(i)
        for p in doc.get("positionen",[]):
            self.tree.insert("", "end", values=(p["name"],p["menge"],p["preis"],p["mwst"]))
        self.logo_path=doc.get("logo_path")

    def collect_doc(self):
        pos=[]
        for item in self.tree.get_children():
            vals=self.tree.item(item)["values"]
            pos.append({"name":vals[0],"menge":float(vals[1]),"preis":float(vals[2]),"mwst":float(vals[3])})
        return {"typ":self.typ_var.get(),"nr":self.nr_var.get(),"datum":self.date_var.get(),
                "firma":self.firma_var.get(),"kunde":self.kunde_var.get(),"notiz":self.notiz_txt.get("1.0","end").strip(),
                "positionen":pos,"logo_path":self.logo_path}

    def new_doc(self):
        self.selected_id=None
        self.typ_var.set("Angebot")
        self.nr_var.set("")
        self.date_var.set(datetime.date.today().isoformat())
        self.firma_var.set("")
        self.kunde_var.set("")
        self.notiz_txt.delete("1.0","end")
        for i in self.tree.get_children(): self.tree.delete(i)
        self.logo_path=None

    def save_doc(self):
        doc=self.collect_doc()
        if self.selected_id is None:
            self.docs.append(doc)
        else:
            self.docs[self.selected_id]=doc
        save_docs(self.docs)
        self.refresh_list()
        messagebox.showinfo("Gespeichert","Dokument gespeichert.")

    def export_pdf(self):
        if self.selected_id is None:
            messagebox.showwarning("Fehler","Kein Dokument ausgewählt.")
            return
        doc=self.docs[self.selected_id]
        fname=filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not fname: return

        c=canvas.Canvas(fname,pagesize=A4)
        width,height=A4
        y=height-50
        c.setFont("Helvetica-Bold",16)
        c.drawString(50,y,doc["typ"])
        c.setFont("Helvetica",10)
        c.drawRightString(width-50,y,f"Nr. {doc['nr']} - {doc['datum']}")
        if doc.get("logo_path"):
            try:
                img=ImageReader(doc["logo_path"])
                c.drawImage(img,width-150,y-30,width=100,height=50,preserveAspectRatio=True)
            except: pass
        y-=70
        c.setFont("Helvetica-Bold",12)
        c.drawString(50,y,f"Firma: {doc['firma']}")
        c.drawString(50,y-15,f"Kunde: {doc['kunde']}")
        y-=50

        data=[["Name","Menge","Preis","MwSt","Betrag"]]
        total=0
        for p in doc["positionen"]:
            betrag=p["menge"]*p["preis"]*(1+p["mwst"]/100)
            total+=betrag
            data.append([p["name"],p["menge"],p["preis"],p["mwst"],round(betrag,2)])

        t=Table(data)
        t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,"black"),
                               ("BACKGROUND",(0,0),(-1,0),colors.grey)]))
        t.wrapOn(c,width,height)
        t.drawOn(c,50,y-20)
        y-=20+20*len(doc["positionen"])
        c.setFont("Helvetica-Bold",12)
        c.drawRightString(width-50, y, f"Gesamt: {round(total,2)} €")
        c.save()
        messagebox.showinfo("Exportiert","PDF gespeichert.")

if __name__=="__main__":
    root=tk.Tk()
    app=SteinApp(root)
    root.mainloop()
