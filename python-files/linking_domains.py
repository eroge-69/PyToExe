import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, shutil, zipfile, random
from datetime import datetime
import pandas as pd

ROBOTS = """User-agent: AhrefsBot
Allow: /

User-agent: rogerbot
Disallow: /

User-agent: dotbot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: SiteAuditBot
Disallow: /

User-agent: SemrushBot-BA
Disallow: /

User-agent: SemrushBot-SI
Disallow: /

User-agent: SemrushBot-SWA
Disallow: /

User-agent: SemrushBot-CT
Disallow: /

User-agent: SemrushBot-BM
Disallow: /

User-agent: SplitSignalBot
Disallow: /

User-agent: SemrushBot-COUB
Disallow: /
"""

HTACCESS = """RewriteEngine On

# Return 404 for requests with query strings
RewriteCond %{QUERY_STRING} .
RewriteRule ^$ - [R=404,L]

# Redirect to 404.shtml for /index.html
RewriteRule ^index\.html$ /404.shtml [L,R=404]
"""

HTML_404 = ""  # Empty

DEFAULT_INDEX_HTML = """<!DOCTYPE html>
<html lang='en-us'>
<head>
  <meta charset="utf-8">
  <title>Local Citation Links</title>
  <meta name="generator" content="WordPress 6.2">
  <style>
    body {
      font-family: Verdana, Geneva, Tahoma, sans-serif;
      background-color: #faf9f7;
      margin: 0;
      padding: 0;
    }
    main {
      display: block;
      position: relative;
      margin: 4rem auto 2rem auto;
      width: 85%;
      max-width: 950px;
      background-color: #ffffff;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      overflow: hidden;
      min-height: 600px;
    }
    #title {
      text-align: center;
      font-size: 36px;
      margin: 0;
      padding: 1.5rem;
      background: #7824aa;
      color: #ffffff;
      border-bottom: 4px solid #e2a1ff;
    }
    nav {
      background-color: #af4be7;
      color: #ffffff;
      text-align: center;
      padding: 0.75rem 0;
    }
    nav ul {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      justify-content: center;
    }
    nav li {
      margin: 0 1rem;
      transition: background-color 0.3s ease;
    }
    nav li:hover {
      background-color: #d791ff;
      border-radius: 5px;
    }
    nav a {
      color: #ffffff;
      text-decoration: none;
      display: block;
      padding: 0.5rem 1rem;
    }
    article {
      padding: 2rem;
      color: #333333;
    }
    article h2 {
      margin-top: 0;
      color: #44266e;
    }
    article p {
      line-height: 1.6;
      margin-bottom: 1.25rem;
      color: #555555;
    }
    footer {
      text-align: center;
      padding: 1rem;
      color: #666666;
      border-top: 1px solid #eee;
      background-color: #fdfdfd;
    }
    @media only screen and (max-width: 800px) {
      main {
        width: 90%;
        margin-top: 1rem;
      }
      nav ul {
        flex-direction: column;
        align-items: center;
      }
      nav li {
        margin: 0.5rem 0;
      }
    }
  </style>
</head>
<body>
  <main>
    <h1 id="title">Local Citation Links</h1>
    <header>
      <nav>
        <ul>
          <li><a href="#">Home</a></li>
        </ul>
      </nav>
    </header>
    <article>
      <h2>Understanding Local Citations</h2>
      <p>
        Local citations refer to any online mention of the name, address, and phone number (NAP) 
        for a local business. They can appear in local business directories, on websites and apps, 
        and on social platforms. Citations help Internet users to discover local businesses and can also 
        impact local search engine rankings.
      </p>
      <p>
        A comprehensive local citation will include not only the business NAP but also other information 
        like hours of operation, services offered, and more. Building and managing these citations 
        correctly is a critical component of local SEO. Inconsistencies in NAP data or missing citations 
        can cause confusion for search engines and may result in lower visibility in local search results.
      </p>
      {link Block}
      <h2>Why Local Citation Links Matter</h2>
      <p>
        When search engines see consistent information about your business across various credible 
        websites, they grow more confident that your company is legitimate and trustworthy. 
        This can lead to better local search rankings, helping potential customers find you more easily.
      </p>
      <a href="https://b314f8e.io" rel="nofollow"></a>
      <p>
        Additionally, listing your business on widely recognized directories or niche-specific platforms 
        can drive direct referral traffic and increase your overall online presence. 
        This boosts brand awareness and can lead to more conversions both online and in-store.
      </p>
    </article>
    <footer>
      &copy; 2025
    </footer>
  </main>
</body>
</html>
"""

STATIC_FILES = {
    "robots.txt": ROBOTS,
    ".htaccess": HTACCESS,
    "404.shtml": HTML_404
}

def make_link_block(domain, keyword):
    if keyword:
        keywords = [k.strip() for k in keyword.split(',') if k.strip()]
        block = ""
        if len(keywords) > 0:
            for k in keywords:
                block += f"<p> <a href='https://{domain}'>{k}</a></p>\n"
            return block
    return f"<p> <a href='https://{domain}'>{domain}</a></p>\n"

def build_and_zip(data_rows, output_dir, index_html_template):
    temp_root = os.path.join(output_dir, "folders")
    if os.path.exists(temp_root): shutil.rmtree(temp_root)
    os.makedirs(temp_root)
    csv_rows = []
    for idx, (link, domain, keyword) in enumerate(data_rows, 1):
        folder = os.path.join(temp_root, f"{link}")
        os.makedirs(folder, exist_ok=True)
        link_block = make_link_block(domain, keyword)
        index_html = index_html_template.replace("{link Block}", link_block)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)
        for fname, content in STATIC_FILES.items():
            with open(os.path.join(folder, fname), "w", encoding="utf-8") as f:
                f.write(content)
        csv_rows.append({"Row Number": idx, "Link": link, "Linking domains": domain, "Keyword(s)": keyword})
    csv_path = os.path.join(output_dir, "summary.csv")
    pd.DataFrame(csv_rows).to_csv(csv_path, index=False)
    zip_path = os.path.join(output_dir, "output.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_root):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_root)
                zf.write(file_path, arcname)
    shutil.rmtree(temp_root)
    return zip_path, csv_path

class CustomThemeDialog(tk.Toplevel):
    def __init__(self, master, initial_template, default_template, on_save_callback):
        super().__init__(master)
        self.title("Edit index.html Theme (use {link Block} for links!)")
        self.geometry("900x700")
        self.on_save_callback = on_save_callback
        self.default_template = default_template
        info = tk.Label(self, text="Edit the HTML theme for index.html. Place {link Block} where the list of links should appear.", font=("Segoe UI", 10, "italic"), fg="#7824aa")
        info.pack(pady=(8, 2))
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.text = tk.Text(frame, font=("Consolas", 11), wrap="word", undo=True)
        self.text.pack(side="left", fill="both", expand=True)
        self.text.insert("1.0", initial_template)
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.text.yview)
        yscroll.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=yscroll.set)
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Button-4>", self._on_mousewheel)
        self.text.bind("<Button-5>", self._on_mousewheel)
        self.text.bind("<Control-c>", self._on_copy)
        self.text.bind("<Control-C>", self._on_copy)
        self.text.bind("<Control-v>", self._on_paste)
        self.text.bind("<Control-V>", self._on_paste)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        save_btn = ttk.Button(btn_frame, text="Save", command=self.save)
        save_btn.pack(side="left", padx=10)
        reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        reset_btn.pack(side="left", padx=10)
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="left", padx=10)

    def save(self):
        new_template = self.text.get("1.0", "end-1c")
        if "{link Block}" not in new_template:
            messagebox.showerror("Missing Placeholder", "Please include {link Block} in the template to specify where links should appear.")
            return
        self.on_save_callback(new_template)
        self.destroy()

    def reset(self):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", self.default_template)

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.text.yview_scroll(-3, "units")
        elif event.num == 5 or event.delta < 0:
            self.text.yview_scroll(3, "units")

    def _on_copy(self, event):
        try:
            self.clipboard_clear()
            selected = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_append(selected)
        except Exception:
            pass
        return "break"

    def _on_paste(self, event):
        try:
            self.text.insert(tk.INSERT, self.clipboard_get())
        except Exception:
            pass
        return "break"

class GridTable(tk.Canvas):
    def __init__(self, parent, columns, initial_rows=200, cell_width=220, cell_height=28, row_num_width=36):
        super().__init__(parent, bg="#f7fafc", highlightthickness=0)
        self.columns = columns
        self.rows = initial_rows
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.row_num_width = row_num_width
        self.header_height = 30
        self.data = [["" for _ in columns] for _ in range(self.rows)]
        self.selected = set()
        self.edit_cell = None
        self.start_sel = None
        self.configure(scrollregion=(0,0,self.total_width(),self.total_height()))
        self.vsb = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.grid(row=0, column=0, sticky="nsew")
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<Button-4>", self.on_mousewheel)
        self.bind("<Button-5>", self.on_mousewheel)
        self.bind("<Key>", self.on_key)
        self.bind("<Control-c>", self.on_copy)
        self.bind("<Control-C>", self.on_copy)
        self.bind("<Control-v>", self.on_paste)
        self.bind("<Control-V>", self.on_paste)
        self.bind("<Control-d>", self.on_fill_down)
        self.bind("<Control-D>", self.on_fill_down)
        self.bind("<Delete>", self.on_delete)
        self.focus_set()
        self.draw_grid()

    def total_width(self):
        return self.row_num_width + len(self.columns)*self.cell_width

    def total_height(self):
        return self.header_height + self.rows*self.cell_height

    def draw_grid(self):
        self.delete("all")
        # Header
        self.create_rectangle(0, 0, self.row_num_width, self.header_height, fill="#f3eaff", outline="#4e217a")
        self.create_text(self.row_num_width//2, self.header_height//2, text="#", font=("Segoe UI", 10, "bold"), fill="#4e217a")
        for ci, col in enumerate(self.columns):
            x0 = self.row_num_width + ci*self.cell_width
            self.create_rectangle(x0, 0, x0+self.cell_width, self.header_height, fill="#f3eaff", outline="#4e217a")
            self.create_text(x0+self.cell_width//2, self.header_height//2, text=col, font=("Segoe UI", 10, "bold"), fill="#4e217a")
        # Rows
        for ri in range(self.rows):
            y0 = self.header_height + ri*self.cell_height
            # Row number
            self.create_rectangle(0, y0, self.row_num_width, y0+self.cell_height, fill="#f6f9fb", outline="#cccccc")
            self.create_text(self.row_num_width//2, y0+self.cell_height//2, text=str(ri+1), font=("Segoe UI", 10), fill="#333")
            for ci in range(len(self.columns)):
                x0 = self.row_num_width + ci*self.cell_width
                x1 = x0 + self.cell_width
                y1 = y0 + self.cell_height
                fill = "#e2a1ff" if (ri,ci) in self.selected else "white"
                self.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#cccccc")
                text = self.data[ri][ci]
                self.create_text(x0+5, y0+self.cell_height//2, text=text, anchor="w", font=("Segoe UI", 10), fill="#222")
        # Grid lines
        for ci in range(len(self.columns)+1):
            x = self.row_num_width + ci*self.cell_width
            self.create_line(x, 0, x, self.total_height(), fill="#b0b0b0")
        for ri in range(self.rows+1):
            y = self.header_height + ri*self.cell_height
            self.create_line(0, y, self.total_width(), y, fill="#b0b0b0")
        self.configure(scrollregion=(0,0,self.total_width(),self.total_height()))

    def cell_at(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        if y < self.header_height or x < self.row_num_width:
            return None
        ci = int((x - self.row_num_width)//self.cell_width)
        ri = int((y - self.header_height)//self.cell_height)
        if 0 <= ci < len(self.columns) and 0 <= ri < self.rows:
            return (ri, ci)
        return None

    def on_click(self, event):
        self.focus_set()
        pos = self.cell_at(event)
        if pos:
            if event.state & 0x0001:  # Shift
                if self.selected:
                    r0, c0 = min(self.selected)
                    r1, c1 = pos
                    r0 = int(r0); c0 = int(c0); r1 = int(r1); c1 = int(c1)
                    self.selected = set((r, c)
                        for r in range(min(r0, r1), max(r0, r1)+1)
                        for c in range(min(c0, c1), max(c0, c1)+1))
                else:
                    self.selected = set([pos])
            elif event.state & 0x0004:  # Ctrl
                if pos in self.selected:
                    self.selected.remove(pos)
                else:
                    self.selected.add(pos)
            else:
                self.selected = set([pos])
            self.start_sel = pos
            self.draw_grid()
        else:
            self.selected.clear()
            self.draw_grid()

    def on_drag(self, event):
        pos = self.cell_at(event)
        if pos and self.start_sel:
            r0, c0 = self.start_sel
            r1, c1 = pos
            r0 = int(r0); c0 = int(c0); r1 = int(r1); c1 = int(c1)
            self.selected = set((r, c)
                        for r in range(min(r0, r1), max(r0, r1)+1)
                        for c in range(min(c0, c1), max(c0, c1)+1))
            self.draw_grid()

    def on_release(self, event):
        pass

    def on_double_click(self, event):
        pos = self.cell_at(event)
        if pos:
            self.selected = set([pos])
            self.draw_grid()
            self.edit_cell_at(pos)

    def edit_cell_at(self, pos):
        if self.edit_cell: self.edit_cell.destroy()
        ri, ci = pos
        x0 = self.row_num_width + ci*self.cell_width
        y0 = self.header_height + ri*self.cell_height
        entry = ttk.Entry(self, font=("Segoe UI", 10))
        entry.insert(0, self.data[ri][ci])
        entry.place(x=x0+1, y=y0+1, width=self.cell_width-2, height=self.cell_height-2)
        entry.focus_set()
        entry.select_range(0, 'end')
        entry.bind("<FocusOut>", lambda e: self._save_edit(pos, entry))
        entry.bind("<Return>", lambda e: self._on_entry_return(pos, entry))
        entry.bind("<Tab>", lambda e: self._on_entry_tab(pos, entry))
        entry.bind("<Shift-Tab>", lambda e: self._on_entry_shift_tab(pos, entry))
        entry.bind("<Down>", lambda e: self._on_entry_down(pos, entry))
        entry.bind("<Up>", lambda e: self._on_entry_up(pos, entry))
        self.edit_cell = entry

    def _save_edit(self, pos, entry):
        ri, ci = pos
        val = entry.get()
        self.data[ri][ci] = val
        entry.destroy()
        self.edit_cell = None
        self.draw_grid()

    def _on_entry_return(self, pos, entry):
        self._save_edit(pos, entry)
        ri, ci = pos
        if ri+1 < self.rows:
            self.selected = {(ri+1, ci)}
            self.draw_grid()
            self.edit_cell_at((ri+1, ci))
        return "break"

    def _on_entry_tab(self, pos, entry):
        self._save_edit(pos, entry)
        ri, ci = pos
        if ci+1 < len(self.columns):
            self.selected = {(ri, ci+1)}
            self.draw_grid()
            self.edit_cell_at((ri, ci+1))
        elif ri+1 < self.rows:
            self.selected = {(ri+1, 0)}
            self.draw_grid()
            self.edit_cell_at((ri+1, 0))
        return "break"

    def _on_entry_shift_tab(self, pos, entry):
        self._save_edit(pos, entry)
        ri, ci = pos
        if ci-1 >= 0:
            self.selected = {(ri, ci-1)}
            self.draw_grid()
            self.edit_cell_at((ri, ci-1))
        elif ri-1 >= 0:
            self.selected = {(ri-1, len(self.columns)-1)}
            self.draw_grid()
            self.edit_cell_at((ri-1, len(self.columns)-1))
        return "break"

    def _on_entry_down(self, pos, entry):
        self._save_edit(pos, entry)
        ri, ci = pos
        if ri+1 < self.rows:
            self.selected = {(ri+1, ci)}
            self.draw_grid()
            self.edit_cell_at((ri+1, ci))
        return "break"

    def _on_entry_up(self, pos, entry):
        self._save_edit(pos, entry)
        ri, ci = pos
        if ri-1 >= 0:
            self.selected = {(ri-1, ci)}
            self.draw_grid()
            self.edit_cell_at((ri-1, ci))
        return "break"

    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.yview_scroll(-3, "units")
        elif event.num == 5 or event.delta < 0:
            self.yview_scroll(3, "units")

    def on_key(self, event):
        if self.edit_cell: return
        if event.keysym in ("Down", "Up", "Left", "Right", "Tab", "Return", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return
        if len(self.selected) == 1:
            ri, ci = next(iter(self.selected))
            self.edit_cell_at((ri, ci))

    def on_copy(self, event):
        if self.edit_cell:
            self.edit_cell.event_generate("<<Copy>>")
            return "break"
        if not self.selected:
            return "break"
        minr = int(min(r for r, c in self.selected))
        maxr = int(max(r for r, c in self.selected))
        minc = int(min(c for r, c in self.selected))
        maxc = int(max(c for r, c in self.selected))
        lines = []
        for r in range(minr, maxr+1):
            vals = []
            for c in range(minc, maxc+1):
                vals.append(self.data[r][c])
            lines.append('\t'.join(vals))
        self.clipboard_clear()
        self.clipboard_append('\n'.join(lines))
        return "break"

    def on_paste(self, event):
        if self.edit_cell: return
        try:
            content = self.clipboard_get()
        except Exception:
            return "break"
        rows = [r for r in content.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
        start = min(self.selected) if self.selected else (0, 0)
        for ri, rowdata in enumerate(rows):
            if not rowdata: continue
            cells = rowdata.split('\t')
            for ci, cellval in enumerate(cells):
                r = int(start[0]+ri)
                c = int(start[1]+ci)
                if 0 <= r < self.rows and 0 <= c < len(self.columns):
                    self.data[r][c] = cellval
        self.draw_grid()
        return "break"

    def on_fill_down(self, event):
        if not self.selected:
            return "break"
        minr = int(min(r for r, c in self.selected))
        minc = int(min(c for r, c in self.selected))
        maxr = int(max(r for r, c in self.selected))
        maxc = int(max(c for r, c in self.selected))
        for c in range(minc, maxc+1):
            top_val = self.data[minr][c]
            for r in range(minr+1, maxr+1):
                self.data[r][c] = top_val
        self.draw_grid()
        return "break"

    def on_delete(self, event):
        for r, c in self.selected:
            self.data[int(r)][int(c)] = ""
        self.draw_grid()
        return "break"

    def get_all_data(self):
        return [row[:] for row in self.data if row[0] and row[1]]

    def add_more_rows(self, n=200):
        for _ in range(n):
            self.data.append(["" for _ in self.columns])
        self.rows += n
        self.configure(scrollregion=(0,0,self.total_width(),self.total_height()))
        self.draw_grid()

class CitationApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Local Citation Builder")
        master.configure(bg="#f6f9fb")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f6f9fb")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8, background="#7824aa", foreground="#fff")
        style.map("TButton", background=[("active", "#4e217a")], foreground=[("active", "#fff")])
        style.configure("TLabel", background="#f6f9fb", font=("Segoe UI", 11))
        self.default_index_html_template = DEFAULT_INDEX_HTML
        self.index_html_template = DEFAULT_INDEX_HTML
        header = ttk.Label(self, text="Local Citation Builder", font=("Segoe UI", 21, "bold"), background="#f6f9fb", foreground="#7824aa")
        header.pack(pady=(18, 8))
        desc = ttk.Label(self, text="Double-click to edit. Paste or type up to 200 links, linking domains, and keywords below. Excel-style editing and copy/paste supported.", background="#f6f9fb")
        desc.pack()
        table_frame = ttk.Frame(self)
        table_frame.pack(padx=10, pady=12, fill=tk.BOTH, expand=True)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.table = GridTable(table_frame, columns=["Link", "Linking domains", "Keyword (comma separated)"], initial_rows=200)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=(6, 16))
        self.theme_btn = ttk.Button(btn_frame, text="🎨 Use Custom Theme", command=self.custom_theme)
        self.theme_btn.pack(side="left", padx=8)
        self.addrows_btn = ttk.Button(btn_frame, text="➕ Add 200 more rows", command=self.add_more_rows)
        self.addrows_btn.pack(side="left", padx=8)
        self.build_btn = ttk.Button(btn_frame, text="🚀 Build File", command=self.build)
        self.build_btn.pack(side="left", padx=8)

    def custom_theme(self):
        def on_save(new_template):
            self.index_html_template = new_template
            messagebox.showinfo("Theme Saved", "Custom index.html theme updated successfully!")
        CustomThemeDialog(self, self.index_html_template, self.default_index_html_template, on_save)

    def add_more_rows(self):
        self.table.add_more_rows(200)

    def build(self):
        data = self.table.get_all_data()
        if not data:
            messagebox.showerror("No Data", "Please enter at least one Link and one Linking domain.")
            return
        folder = filedialog.askdirectory(title="Select folder to save output")
        if not folder:
            return
        serial = random.randint(10000, 99999)
        today = datetime.now().strftime("%d-%m-%Y")
        output_dir_name = f"Tier-1_linking_domains_{serial}_({today})"
        output_dir = os.path.join(folder, output_dir_name)
        os.makedirs(output_dir, exist_ok=True)
        old_theme_path = os.path.join(output_dir, "Old_Index_Theme.txt")
        new_theme_path = os.path.join(output_dir, "New_Index_Theme.txt")
        with open(old_theme_path, "w", encoding="utf-8") as f:
            f.write(self.default_index_html_template)
        with open(new_theme_path, "w", encoding="utf-8") as f:
            f.write(self.index_html_template)
        try:
            zip_path, csv_path = build_and_zip(data, output_dir, self.index_html_template)
            messagebox.showinfo("Success", f"ZIP and CSV and theme files saved in:\n{output_dir}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = CitationApp(root)
    app.pack(fill="both", expand=True)
    root.geometry("900x700")
    root.mainloop()