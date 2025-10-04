#!/usr/bin/env python3
# Arcandum Incident Editor (Simplified)
# - Paste Google Maps coords "49.05881269336688, 9.895987319093946" -> parsed to point.lat/lon
# - No time field required
# - Adds "site": "unknown" | "critical_infrastructure" | "military_base"
# - Tkinter only

import json, re, uuid, datetime, math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ALLOWED_TYPES = ["detection", "sabotage", "interception", "other"]
ALLOWED_SEVERITIES = ["low", "medium", "high"]
ALLOWED_SITES = ["unknown", "critical_infrastructure", "military_base"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COORD_RE = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*$")

def gen_id(prefix="arc"):
    return f"{prefix}-{datetime.datetime.utcnow():%Y%m%d}-{uuid.uuid4().hex[:6]}"

def parse_float(s):
    try: return float(s)
    except: return None

def validate_item(item):
    errs = []
    if item.get("type") not in ALLOWED_TYPES:
        errs.append("type must be one of: " + ", ".join(ALLOWED_TYPES))
    if item.get("severity") not in ALLOWED_SEVERITIES:
        errs.append("severity must be one of: " + ", ".join(ALLOWED_SEVERITIES))
    if item.get("site") not in ALLOWED_SITES:
        errs.append("site must be one of: " + ", ".join(ALLOWED_SITES))
    # either point or bbox must exist
    if not item.get("point") and not item.get("bbox"):
        errs.append("either point or bbox is required")
    # point range
    if item.get("point"):
        try:
            lat=float(item["point"]["lat"]); lon=float(item["point"]["lon"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180): raise ValueError()
        except: errs.append("invalid point coordinates")
    # bbox
    if item.get("bbox"):
        b=item["bbox"]
        if not (isinstance(b,list) and len(b)==4):
            errs.append("bbox must be [minLon, minLat, maxLon, maxLat]")
        else:
            try: _=[float(x) for x in b]
            except: errs.append("bbox values must be numbers")
    # sources
    for s in item.get("sources", []):
        if s.get("published") and not DATE_RE.match(s["published"]):
            errs.append("source published date must be YYYY-MM-DD")
    return errs

class SourcesEditor(tk.Toplevel):
    def __init__(self, master, sources):
        super().__init__(master); self.title("Edit Sources"); self.geometry("700x320")
        self.sources = [dict(s) for s in (sources or [])]
        cols=("title","url","published"); self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for c in cols:
            self.tree.heading(c,text=c); self.tree.column(c,width=220 if c!="published" else 100,anchor="w")
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)
        btns=ttk.Frame(self); btns.pack(fill="x",padx=6,pady=(0,6))
        ttk.Button(btns,text="Add",command=self.add_src).pack(side="left")
        ttk.Button(btns,text="Edit",command=self.edit_src).pack(side="left",padx=4)
        ttk.Button(btns,text="Delete",command=self.del_src).pack(side="left")
        ttk.Button(btns,text="Move ↑",command=lambda:self.move(-1)).pack(side="left",padx=8)
        ttk.Button(btns,text="Move ↓",command=lambda:self.move(1)).pack(side="left")
        ttk.Button(btns,text="OK",command=self.ok).pack(side="right")
        ttk.Button(btns,text="Cancel",command=self.cancel).pack(side="right",padx=4)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for s in self.sources:
            self.tree.insert("", "end", values=(s.get("title",""), s.get("url",""), s.get("published","")))

    def prompt_source(self, initial=None):
        d=tk.Toplevel(self); d.title("Source"); d.geometry("520x180"); d.grab_set()
        vals={"title":"","url":"","published":""}; 
        if initial: vals.update(initial)
        entries={}
        for i,(label,key) in enumerate([("Title","title"),("URL","url"),("Published (YYYY-MM-DD)","published")]):
            ttk.Label(d,text=label).grid(row=i,column=0,sticky="e",padx=6,pady=6)
            e=ttk.Entry(d,width=58); e.grid(row=i,column=1,sticky="w",padx=6,pady=6); e.insert(0,vals[key]); entries[key]=e
        ok={"val":None}
        def done():
            s={k:entries[k].get().strip() for k in entries}
            if s["published"] and not DATE_RE.match(s["published"]):
                messagebox.showerror("Invalid","Published must be YYYY-MM-DD"); return
            ok["val"]=s; d.destroy()
        ttk.Button(d,text="OK",command=done).grid(row=3,column=1,sticky="e",padx=6,pady=8)
        ttk.Button(d,text="Cancel",command=d.destroy).grid(row=3,column=1,sticky="w",padx=6,pady=8)
        d.wait_window(); return ok["val"]

    def add_src(self):
        s=self.prompt_source(); 
        if s: self.sources.append(s); self.refresh()
    def edit_src(self):
        sel=self.tree.selection()
        if not sel: return
        idx=self.tree.index(sel[0]); cur=self.sources[idx]; s=self.prompt_source(cur)
        if s: self.sources[idx]=s; self.refresh()
    def del_src(self):
        sel=self.tree.selection()
        if not sel: return
        idx=self.tree.index(sel[0]); del self.sources[idx]; self.refresh()
    def move(self, direction):
        sel=self.tree.selection()
        if not sel: return
        idx=self.tree.index(sel[0]); new=idx+direction
        if 0<=new<len(self.sources):
            self.sources[idx],self.sources[new]=self.sources[new],self.sources[idx]
            self.refresh(); self.tree.selection_set(self.tree.get_children()[new])
    def ok(self): self.result=self.sources; self.destroy()
    def cancel(self): self.result=None; self.destroy()

class EditorApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Arcandum Incident Editor"); self.geometry("1100x640")
        self.file_path=None; self.items=[]
        self.columnconfigure(1,weight=1); self.rowconfigure(0,weight=1)
        left=ttk.Frame(self); left.grid(row=0,column=0,sticky="ns")
        ttk.Label(left,text="Incidents").pack(anchor="w",padx=8,pady=(8,2))
        self.listbox=tk.Listbox(left,width=40,height=28); self.listbox.pack(fill="y",padx=8,pady=4)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        lbtn=ttk.Frame(left); lbtn.pack(fill="x",padx=8,pady=6)
        ttk.Button(lbtn,text="New",command=self.new_item).pack(side="left")
        ttk.Button(lbtn,text="Duplicate",command=self.duplicate_item).pack(side="left",padx=4)
        ttk.Button(lbtn,text="Delete",command=self.delete_item).pack(side="left")
        ttk.Button(lbtn,text="Validate",command=self.validate_current).pack(side="right")

        frm=ttk.Frame(self); frm.grid(row=0,column=1,sticky="nsew")
        for i in range(6): frm.columnconfigure(i,weight=1)

        ttk.Label(frm,text="ID").grid(row=0,column=0,sticky="e",padx=6,pady=6)
        self.var_id=tk.StringVar(); ttk.Entry(frm,textvariable=self.var_id).grid(row=0,column=1,sticky="we",padx=6,pady=6)
        ttk.Button(frm,text="Generate",command=lambda:self.var_id.set(gen_id())).grid(row=0,column=2,sticky="w",padx=6,pady=6)

        ttk.Label(frm,text="Type").grid(row=0,column=3,sticky="e",padx=6,pady=6)
        self.var_type=tk.StringVar(); ttk.Combobox(frm,textvariable=self.var_type,values=ALLOWED_TYPES,state="readonly").grid(row=0,column=4,sticky="we",padx=6,pady=6)

        ttk.Label(frm,text="Severity").grid(row=0,column=5,sticky="e",padx=6,pady=6)
        self.var_sev=tk.StringVar(); ttk.Combobox(frm,textvariable=self.var_sev,values=ALLOWED_SEVERITIES,state="readonly").grid(row=0,column=5+1-1,sticky="we",padx=6,pady=6)

        ttk.Label(frm,text="Site").grid(row=1,column=0,sticky="e",padx=6,pady=6)
        self.var_site=tk.StringVar(value="unknown")
        ttk.Combobox(frm,textvariable=self.var_site,values=ALLOWED_SITES,state="readonly").grid(row=1,column=1,sticky="we",padx=6,pady=6)

        ttk.Label(frm,text="Region").grid(row=1,column=3,sticky="e",padx=6,pady=6)
        self.var_region=tk.StringVar(); ttk.Entry(frm,textvariable=self.var_region).grid(row=1,column=4,sticky="we",padx=6,pady=6)

        ttk.Label(frm,text="Verified").grid(row=1,column=5,sticky="e",padx=6,pady=6)
        self.var_verified=tk.BooleanVar(value=True); ttk.Checkbutton(frm,variable=self.var_verified).grid(row=1,column=5+1-1,sticky="w",padx=6,pady=6)

        # PASTE COORDS
        ttk.Label(frm,text="Paste coords (lat, lon)").grid(row=2,column=0,sticky="e",padx=6,pady=6)
        self.var_paste=tk.StringVar()
        ttk.Entry(frm,textvariable=self.var_paste).grid(row=2,column=1,columnspan=2,sticky="we",padx=6,pady=6)
        ttk.Button(frm,text="Parse → Point",command=self.parse_coords).grid(row=2,column=3,sticky="w",padx=6,pady=6)

        # Point
        ttk.Label(frm,text="Point lat").grid(row=3,column=0,sticky="e",padx=6,pady=6)
        self.var_lat=tk.StringVar(); ttk.Entry(frm,textvariable=self.var_lat).grid(row=3,column=1,sticky="we",padx=6,pady=6)
        ttk.Label(frm,text="Point lon").grid(row=3,column=2,sticky="e",padx=6,pady=6)
        self.var_lon=tk.StringVar(); ttk.Entry(frm,textvariable=self.var_lon).grid(row=3,column=3,sticky="we",padx=6,pady=6)
        ttk.Button(frm,text="Clear Point",command=lambda:(self.var_lat.set(''),self.var_lon.set(''))).grid(row=3,column=4,sticky="w",padx=6,pady=6)

        # BBox
        ttk.Label(frm,text="BBox [minLon, minLat, maxLon, maxLat]").grid(row=4,column=0,sticky="e",padx=6,pady=6)
        self.var_bminlon=tk.StringVar(); self.var_bminlat=tk.StringVar(); self.var_bmaxlon=tk.StringVar(); self.var_bmaxlat=tk.StringVar()
        ttk.Entry(frm,width=12,textvariable=self.var_bminlon).grid(row=4,column=1,sticky="we",padx=3,pady=6)
        ttk.Entry(frm,width=12,textvariable=self.var_bminlat).grid(row=4,column=2,sticky="we",padx=3,pady=6)
        ttk.Entry(frm,width=12,textvariable=self.var_bmaxlon).grid(row=4,column=3,sticky="we",padx=3,pady=6)
        ttk.Entry(frm,width=12,textvariable=self.var_bmaxlat).grid(row=4,column=4,sticky="we",padx=3,pady=6)
        ttk.Button(frm,text="Clear BBox",command=lambda:(self.var_bminlon.set(''),self.var_bminlat.set(''),self.var_bmaxlon.set(''),self.var_bmaxlat.set(''))).grid(row=4,column=5,sticky="w",padx=6,pady=6)

        ttk.Label(frm,text="Tags (comma separated)").grid(row=5,column=0,sticky="e",padx=6,pady=6)
        self.var_tags=tk.StringVar(); ttk.Entry(frm,textvariable=self.var_tags).grid(row=5,column=1,columnspan=4,sticky="we",padx=6,pady=6)

        ttk.Label(frm,text="Summary").grid(row=6,column=0,sticky="ne",padx=6,pady=6)
        self.txt_summary=tk.Text(frm,height=6,wrap="word"); self.txt_summary.grid(row=6,column=1,columnspan=5,sticky="nsew",padx=6,pady=6)
        frm.rowconfigure(6,weight=1)

        ttk.Button(frm,text="Edit Sources…",command=self.edit_sources).grid(row=7,column=1,sticky="w",padx=6,pady=6)
        self.lbl_src_count=ttk.Label(frm,text="(0 sources)"); self.lbl_src_count.grid(row=7,column=2,sticky="w")

        bottom=ttk.Frame(self); bottom.grid(row=1,column=0,columnspan=2,sticky="we")
        ttk.Button(bottom,text="Open JSON…",command=self.open_json).pack(side="left",padx=6,pady=8)
        ttk.Button(bottom,text="Save",command=lambda:self.save_json(False)).pack(side="left")
        ttk.Button(bottom,text="Save As…",command=lambda:self.save_json(True)).pack(side="left",padx=6)
        ttk.Button(bottom,text="Save Item",command=self.save_current).pack(side="right",padx=6)

        self.current_sources=[]

    # Parse "lat, lon" string to fields
    def parse_coords(self):
        s=self.var_paste.get().strip()
        m=COORD_RE.match(s)
        if not m:
            messagebox.showerror("Invalid format","Bitte im Format: 49.05881269336688, 9.895987319093946")
            return
        lat=float(m.group(1)); lon=float(m.group(2))
        self.var_lat.set(f"{lat:.6f}"); self.var_lon.set(f"{lon:.6f}")
        messagebox.showinfo("OK","Koordinaten übernommen → Point.lat/lon")

    # File ops
    def open_json(self):
        path=filedialog.askopenfilename(title="Open incidents.json",filetypes=[("JSON","*.json"),("All files","*.*")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f: data=json.load(f)
            if not isinstance(data,list): raise ValueError("JSON root must be a list")
            self.file_path=path; self.items=data; self.refresh_list()
            if self.items: self.listbox.selection_set(0); self.on_select()
        except Exception as e:
            messagebox.showerror("Open failed", str(e))

    def save_json(self, force_dialog=False):
        if not self.items:
            messagebox.showinfo("Nothing to save","No items loaded."); return
        path=self.file_path
        if force_dialog or not path:
            path=filedialog.asksaveasfilename(title="Save incidents.json",defaultextension=".json",filetypes=[("JSON","*.json")])
            if not path: return
            self.file_path=path
        try:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(self.items,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("Saved",f"Saved {len(self.items)} items to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def refresh_list(self):
        self.listbox.delete(0,"end")
        for it in self.items:
            lab=f"{it.get('id','<no id>')}  •  {it.get('type','?')}/{it.get('severity','?')}  •  {it.get('site','unknown')}  •  {it.get('region','')}"
            self.listbox.insert("end", lab)

    def new_item(self):
        it={"id":gen_id(),"type":ALLOWED_TYPES[0],"severity":ALLOWED_SEVERITIES[0],
            "site":"unknown","region":"","summary":"","verified":True,
            "point":{"lat":52.52,"lon":13.405},"sources":[]}
        self.items.append(it); self.refresh_list(); self.listbox.selection_clear(0,"end"); self.listbox.selection_set("end"); self.on_select()

    def duplicate_item(self):
        idx=self.get_index()
        if idx is None: return
        import copy; cpy=copy.deepcopy(self.items[idx]); cpy["id"]=gen_id(); self.items.append(cpy)
        self.refresh_list(); self.listbox.selection_set("end"); self.on_select()

    def delete_item(self):
        idx=self.get_index()
        if idx is None: return
        if messagebox.askyesno("Delete","Delete selected incident?"):
            del self.items[idx]; self.refresh_list()
            if self.items: self.listbox.selection_set(0); self.on_select()
            else: self.clear_form()

    def get_index(self):
        sel=self.listbox.curselection(); 
        return sel[0] if sel else None

    def clear_form(self):
        self.var_id.set(""); self.var_type.set(""); self.var_sev.set(""); self.var_site.set("unknown")
        self.var_region.set(""); self.var_verified.set(False)
        self.var_paste.set(""); self.var_lat.set(""); self.var_lon.set("")
        self.var_bminlon.set(""); self.var_bminlat.set(""); self.var_bmaxlon.set(""); self.var_bmaxlat.set("")
        self.var_tags.set(""); self.txt_summary.delete("1.0","end"); self.current_sources=[]; self.lbl_src_count.config(text="(0 sources)")

    def on_select(self, evt=None):
        idx=self.get_index()
        if idx is None: return
        it=self.items[idx]
        self.var_id.set(it.get("id","")); self.var_type.set(it.get("type","")); self.var_sev.set(it.get("severity",""))
        self.var_site.set(it.get("site","unknown"))
        self.var_region.set(it.get("region","")); self.var_verified.set(bool(it.get("verified",False)))
        p=it.get("point") or {}; self.var_lat.set("" if p is None else str(p.get("lat",""))); self.var_lon.set("" if p is None else str(p.get("lon","")))
        b=it.get("bbox") or []; vals=(str(b[0]) if len(b)>0 else "", str(b[1]) if len(b)>1 else "", str(b[2]) if len(b)>2 else "", str(b[3]) if len(b)>3 else "")
        self.var_bminlon.set(vals[0]); self.var_bminlat.set(vals[1]); self.var_bmaxlon.set(vals[2]); self.var_bmaxlat.set(vals[3])
        self.var_tags.set(",".join(it.get("tags", [])))
        self.txt_summary.delete("1.0","end"); self.txt_summary.insert("1.0", it.get("summary",""))
        self.current_sources=list(it.get("sources", [])); self.lbl_src_count.config(text=f"({len(self.current_sources)} sources)")

    def collect_form(self):
        it={"id":self.var_id.get().strip() or gen_id(),
            "type":self.var_type.get().strip(),
            "severity":self.var_sev.get().strip(),
            "site":self.var_site.get().strip() or "unknown",
            "region":self.var_region.get().strip(),
            "summary":self.txt_summary.get("1.0","end").strip(),
            "verified":bool(self.var_verified.get()),
            "sources":self.current_sources}
        tags=[t.strip() for t in self.var_tags.get().split(",") if t.strip()]; 
        if tags: it["tags"]=tags
        lat=parse_float(self.var_lat.get().strip()) if self.var_lat.get().strip()!="" else None
        lon=parse_float(self.var_lon.get().strip()) if self.var_lon.get().strip()!="" else None
        if lat is not None and lon is not None: it["point"]={"lat":lat,"lon":lon}
        bvals=[self.var_bminlon.get().strip(),self.var_bminlat.get().strip(),self.var_bmaxlon.get().strip(),self.var_bmaxlat.get().strip()]
        if any(v!="" for v in bvals):
            try: it["bbox"]=[float(bvals[0]),float(bvals[1]),float(bvals[2]),float(bvals[3])]
            except: pass
        return it

    def save_current(self):
        idx=self.get_index()
        if idx is None: messagebox.showinfo("No selection","Select an item first."); return
        it=self.collect_form(); errs=validate_item(it)
        if errs: messagebox.showerror("Validation failed","\n".join(errs)); return
        self.items[idx]=it; self.refresh_list(); self.listbox.selection_set(idx)
        messagebox.showinfo("Saved","Item saved in memory. Use Save to write JSON.")

    def validate_current(self):
        idx=self.get_index()
        if idx is None: return
        it=self.collect_form(); errs=validate_item(it)
        if errs: messagebox.showerror("Invalid","\n".join(errs))
        else: messagebox.showinfo("OK","Item looks valid.")

    def edit_sources(self):
        ed=SourcesEditor(self,self.current_sources); self.wait_window(ed)
        if getattr(ed,"result",None) is not None:
            self.current_sources=ed.result; self.lbl_src_count.config(text=f"({len(self.current_sources)} sources)")

if __name__ == "__main__":
    app=EditorApp(); app.mainloop()
