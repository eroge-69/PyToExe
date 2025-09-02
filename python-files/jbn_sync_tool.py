
import os, sys, webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

APP_TITLE = "JBN Sync Tool — Part 1 (Stock→E‑Com/Merchant + Label)"
STATE = {"stock":None,"site":None,"merchant":None,"orders":None,"grid":None}

def load_csv(req=None, title="Choose CSV"):
    p = filedialog.askopenfilename(title=title, filetypes=[("CSV","*.csv")])
    if not p: return None
    df = pd.read_csv(p, dtype=str).fillna("")
    if req:
        missing = [c for c in req if c not in df.columns]
        if missing:
            messagebox.showerror("Missing columns", f"Missing: {missing}")
            return None
    return df

def fnum(x, default=0.0):
    try:
        return float(str(x).strip()) if str(x).strip()!="" else default
    except: return default
def fint(x, default=0):
    try:
        return int(float(str(x).strip()))
    except: return default

def build_grid(stock, site, merch):
    s = stock.copy()
    s['sku'] = s['sku'].astype(str).str.upper().str.strip()
    s['stock_qty'] = s['stock_qty'].apply(fint)
    s['price_aed'] = s['price_aed'].apply(fnum)
    site = site.copy() if site is not None else pd.DataFrame(columns=['sku','qty','price'])
    merch = merch.copy() if merch is not None else pd.DataFrame(columns=['sku','qty','price'])
    if not site.empty:
        site['sku']=site['sku'].str.upper().str.strip()
        site['qty']=site['qty'].apply(fint); site['price']=site['price'].apply(fnum)
    if not merch.empty:
        merch['sku']=merch['sku'].str.upper().str.strip()
        merch['qty']=merch['qty'].apply(fint); merch['price']=merch['price'].apply(fnum)
    m1 = pd.merge(s, site[['sku','qty','price']], on='sku', how='left')
    m1 = m1.rename(columns={'qty':'qty_site','price':'price_site'})
    m2 = pd.merge(m1, merch[['sku','qty','price']], on='sku', how='left')
    m2 = m2.rename(columns={'qty':'qty_merch','price':'price_merch'})
    m2['new_qty_site']=m2['stock_qty']; m2['new_price_site']=m2['price_aed']
    m2['new_qty_merch']=m2['stock_qty']; m2['new_price_merch']=m2['price_aed']
    def chg(a,b): 
        a=0 if pd.isna(a) else a; b=0 if pd.isna(b) else b; 
        try: return float(a)!=float(b)
        except: return str(a)!=str(b)
    m2['chg_site']=m2.apply(lambda r: chg(r.get('qty_site',0), r['new_qty_site']) or chg(r.get('price_site',0), r['new_price_site']), axis=1)
    m2['chg_merch']=m2.apply(lambda r: chg(r.get('qty_merch',0), r['new_qty_merch']) or chg(r.get('price_merch',0), r['new_price_merch']), axis=1)
    cols=['sku','stock_qty','price_aed','qty_site','price_site','new_qty_site','new_price_site','qty_merch','price_merch','new_qty_merch','new_price_merch','chg_site','chg_merch']
    return m2[cols]

def make_label_html(order_id, rows):
    hdr = rows[0]
    items = [f"• {r.get('sku','')} × {r.get('qty','')}" for r in rows[:6]]
    addr="\\n".join([hdr.get(k,'') for k in ['address','city','emirate','country','postal_code'] if hdr.get(k,'')])
    cod = f"COD: AED {hdr.get('cod_amount','')}" if (hdr.get('payment_method','').upper()=='COD') else "PAID"
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>{order_id}</title>
<style>
.label{{width:100mm;height:150mm;margin:0 auto;padding:8mm;border:2px solid #000;border-radius:8px;font-family:system-ui}}
h3{{margin:0 0 6px;font-size:16px}}
.pair{{display:flex;justify-content:space-between;font-size:12px;margin:2px 0}}
.addr{{white-space:pre-wrap;border:1px dashed #aaa;border-radius:6px;padding:6px;font-size:12px;margin-top:6px}}
.items{{font-size:12px;margin-top:6px}}
.pill{{display:inline-block;border:1px solid #0a0;padding:3px 8px;border-radius:999px;font-size:12px;margin-top:4px}}
.small{{font-size:11px;color:#444;margin-top:4px;text-align:right}}
@media print{{ .no-print{{display:none}} }}
</style></head><body>
<div class="label">
<h3>JBN — Shipping Label</h3>
<div class="pair"><div><b>Order:</b> {order_id}</div><div><b>Date:</b> {hdr.get('order_date','')}</div></div>
<div class="pair"><div><b>To:</b> {hdr.get('customer_name','')}</div><div><b>Phone:</b> {hdr.get('phone','')}</div></div>
<div class="pill">{cod}</div>
<div class="addr">{addr}</div>
<div class="items"><b>Items:</b><br>{"<br>".join(items)}</div>
<div class="small">Print: Ctrl+P (100×150mm)</div>
</div></body></html>"""

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE); self.geometry("1200x700")
        self.make_ui()
    def make_ui(self):
        top=tk.Frame(self); top.pack(fill='x', padx=10, pady=6)
        ttk.Button(top,text="Load Stocklist",command=self.load_stock).pack(side='left',padx=4)
        ttk.Button(top,text="Load Website (opt)",command=self.load_site).pack(side='left',padx=4)
        ttk.Button(top,text="Load Merchant (opt)",command=self.load_merch).pack(side='left',padx=4)
        ttk.Button(top,text="Load Orders (labels)",command=self.load_orders).pack(side='left',padx=4)
        ttk.Button(top,text="Build Grid",command=self.build).pack(side='left',padx=4)
        self.info=tk.Label(self,text="Load CSVs to begin…",anchor='w'); self.info.pack(fill='x',padx=12)
        cols=["sku","stock_qty","price_aed","qty_site","price_site","new_qty_site","new_price_site","qty_merch","price_merch","new_qty_merch","new_price_merch","chg_site","chg_merch"]
        self.tree=ttk.Treeview(self,columns=cols,show="headings",height=22)
        names={"sku":"SKU","stock_qty":"Stock QTY","price_aed":"Stock Price","qty_site":"Site QTY","price_site":"Site Price",
               "new_qty_site":"NEW Site QTY","new_price_site":"NEW Site Price","qty_merch":"Merchant QTY","price_merch":"Merchant Price",
               "new_qty_merch":"NEW Merchant QTY","new_price_merch":"NEW Merchant Price","chg_site":"Δ Site","chg_merch":"Δ Merchant"}
        for c in cols:
            self.tree.heading(c,text=names[c]); self.tree.column(c,width=100 if c!="sku" else 180, anchor="e" if c!="sku" else "w")
        self.tree.pack(fill='both',expand=True,padx=12,pady=6)
        self.tree.bind("<Double-1>", self.edit_cell)
        bot=tk.Frame(self); bot.pack(fill='x', padx=10, pady=8)
        ttk.Button(bot,text="Export Website CSV",command=self.save_site).pack(side='left',padx=4)
        ttk.Button(bot,text="Export Merchant CSV",command=self.save_merch).pack(side='left',padx=4)
        ttk.Button(bot,text="Create Label (4x6)…",command=self.create_label).pack(side='left',padx=4)
    def load_stock(self):
        df=load_csv(["sku","stock_qty","price_aed"],"Stocklist CSV"); 
        if df is not None: STATE["stock"]=df; messagebox.showinfo("Loaded",f"Stocklist rows: {len(df)}")
    def load_site(self):
        df=load_csv(["sku","qty","price"],"Website CSV"); 
        if df is not None: STATE["site"]=df; messagebox.showinfo("Loaded",f"Website rows: {len(df)}")
    def load_merch(self):
        df=load_csv(["sku","qty","price"],"Merchant CSV"); 
        if df is not None: STATE["merchant"]=df; messagebox.showinfo("Loaded",f"Merchant rows: {len(df)}")
    def load_orders(self):
        req=["order_id","order_date","customer_name","phone","address","city","emirate","country","postal_code","payment_method","cod_amount","sku","qty"]
        df=load_csv(req,"Orders CSV")
        if df is not None: STATE["orders"]=df; messagebox.showinfo("Loaded",f"Orders rows: {len(df)}")
    def build(self):
        if STATE["stock"] is None: messagebox.showwarning("Missing","Load Stocklist first"); return
        grid=build_grid(STATE["stock"], STATE["site"], STATE["merchant"]); STATE["grid"]=grid
        for r in self.tree.get_children(): self.tree.delete(r)
        if grid is None or grid.empty: self.info.config(text="No data"); return
        self.info.config(text=f"Rows: {len(grid)}  •  Site changes: {int(grid['chg_site'].sum())}  •  Merchant changes: {int(grid['chg_merch'].sum())}")
        for _,row in grid.iterrows():
            self.tree.insert("", "end", values=[row[c] if pd.notna(row[c]) else "" for c in self.tree["columns"]])
    def edit_cell(self, evt):
        iid=self.tree.focus(); 
        if not iid: return
        col=self.tree.identify_column(evt.x); idx=int(col.replace("#",""))-1
        name=self.tree["columns"][idx]
        if not (name.startswith("new_qty") or name.startswith("new_price")): return
        x,y,w,h=self.tree.bbox(iid, column=col); val=self.tree.set(iid,name)
        e=ttk.Entry(self.tree); e.place(x=x,y=y,width=w,height=h); e.insert(0,val); e.focus()
        def save(_=None):
            new=e.get(); self.tree.set(iid,name,new); e.destroy()
            # update STATE grid
            sku_idx=self.tree["columns"].index("sku"); sku=self.tree.item(iid,"values")[sku_idx]
            g=STATE["grid"]; 
            if "price" in name: g.loc[g["sku"]==sku, name]=float(new)
            else: g.loc[g["sku"]==sku, name]=int(float(new))
            # flags
            r=g.loc[g["sku"]==sku].iloc[0]
            def chg(a,b):
                try: return float(a)!=float(b)
                except: return str(a)!=str(b)
            g.loc[g["sku"]==sku,"chg_site"]= chg(r.get("qty_site",0),r.get("new_qty_site",0)) or chg(r.get("price_site",0),r.get("new_price_site",0))
            g.loc[g["sku"]==sku,"chg_merch"]= chg(r.get("qty_merch",0),r.get("new_qty_merch",0)) or chg(r.get("price_merch",0),r.get("new_price_merch",0))
            STATE["grid"]=g
            self.build()
        e.bind("<Return>", save); e.bind("<FocusOut>", save)
    def save_site(self):
        g=STATE["grid"]
        if g is None or g.empty: messagebox.showwarning("No data","Build Grid first"); return
        path=filedialog.asksaveasfilename(defaultextension=".csv", initialfile="website_export.csv")
        if not path: return
        g[["sku","new_qty_site","new_price_site"]].rename(columns={"new_qty_site":"qty","new_price_site":"price"}).to_csv(path,index=False)
        messagebox.showinfo("Saved", path)
    def save_merch(self):
        g=STATE["grid"]
        if g is None or g.empty: messagebox.showwarning("No data","Build Grid first"); return
        path=filedialog.asksaveasfilename(defaultextension=".csv", initialfile="merchant_export.csv")
        if not path: return
        g[["sku","new_qty_merch","new_price_merch"]].rename(columns={"new_qty_merch":"qty","new_price_merch":"price"}).to_csv(path,index=False)
        messagebox.showinfo("Saved", path)
    def create_label(self):
        o=STATE["orders"]
        if o is None or o.empty: messagebox.showwarning("No orders","Load Orders CSV first"); return
        ids=list(o["order_id"].astype(str).unique())
        win=tk.Toplevel(self); win.title("Choose Order"); win.geometry("360x120")
        tk.Label(win,text="Order:").pack(pady=6)
        var=tk.StringVar(value=ids[0]); cb=ttk.Combobox(win,textvariable=var,values=ids,state="readonly"); cb.pack(fill="x",padx=10)
        def go():
            oid=var.get(); rows=o[o["order_id"].astype(str)==oid].to_dict("records")
            html=make_label_html(oid, rows)
            path=filedialog.asksaveasfilename(defaultextension=".html", initialfile=f"label_{oid.replace('/','-')}.html")
            if not path: return
            with open(path,"w",encoding="utf-8") as f: f.write(html)
            webbrowser.open("file://"+os.path.abspath(path)); win.destroy()
        ttk.Button(win,text="Create 4×6 Label",command=go).pack(pady=10)
if __name__=="__main__":
    app=App(); app.mainloop()
