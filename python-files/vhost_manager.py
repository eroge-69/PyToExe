#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XAMPP VirtualHost Manager (Windows)
- GUI to Add/Edit/Delete Apache VirtualHosts for XAMPP
- Manage Windows hosts mappings
- Quick Add: domain + ZIP/folder source -> auto extract, config, hosts, restart Apache
- Saved Sources: store reusable ZIPs or folders to reuse as project templates
Author: ChatGPT
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import zipfile

APP_TITLE = "XAMPP VirtualHost Manager"
MARK_BEGIN = "# >>> VHOST-MANAGER:"
MARK_END = "# <<< VHOST-MANAGER:"

DEFAULT_CONFIG = {
    "vhosts_conf_path": r"C:\xampp\apache\conf\extra\httpd-vhosts.conf",
    "hosts_path": r"C:\Windows\System32\drivers\etc\hosts",
    "apache_bin": r"C:\xampp\apache\bin\httpd.exe",
    "listen_ip": "127.0.0.1",
    "default_port": 80,
    "logs_dir": r"C:\xampp\apache\logs",
    "projects_dir": r"C:\xampp\htdocs\projects",
    "port_mode": "namebased",      # "namebased" (80) or "unique"
    "port_start": 8080,
    "port_end": 9000,
    "sources": []                  # [{ "name": "...", "path": "C:\\path\\to\\zip_or_folder" }, ...]
}

def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
        return json.loads(config_path.read_text(encoding="utf-8"))
    # merge defaults
    data = json.loads(config_path.read_text(encoding="utf-8"))
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    return merged

def save_config(config_path: Path, data: dict):
    # ensure keys from defaults exist
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data or {})
    config_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

@dataclass
class VHost:
    name: str
    server_name: str
    server_alias: str
    document_root: str
    port: int = 80
    allow_override: str = "All"
    directory_path: str = ""
    error_log: str = ""
    access_log: str = ""
    extra: str = ""  # custom lines

    def normalize(self):
        if not self.directory_path:
            self.directory_path = self.document_root
        def safe(n):
            return re.sub(r'[^A-Za-z0-9._-]+', '-', n)
        if not self.error_log:
            self.error_log = f"logs/{safe(self.server_name)}-error.log"
        if not self.access_log:
            self.access_log = f"logs/{safe(self.server_name)}-access.log"

    def to_block(self, listen_ip="*", logs_dir="logs"):
        self.normalize()
        err = self.error_log
        acc = self.access_log
        if not os.path.isabs(err) and logs_dir:
            err = os.path.join(logs_dir, os.path.basename(err)).replace("\\", "/")
        if not os.path.isabs(acc) and logs_dir:
            acc = os.path.join(logs_dir, os.path.basename(acc)).replace("\\", "/")

        lines = []
        lines.append(f"{MARK_BEGIN}{self.name}")
        lines.append(f"<VirtualHost {listen_ip}:{self.port}>")
        lines.append(f"    ServerName {self.server_name}")
        if self.server_alias.strip():
            lines.append(f"    ServerAlias {self.server_alias}")
        lines.append(f"    DocumentRoot \"{self.document_root}\"")
        lines.append(f"    <Directory \"{self.directory_path}\">")
        lines.append(f"        AllowOverride {self.allow_override}")
        lines.append(f"        Require all granted")
        lines.append(f"    </Directory>")
        if acc:
            lines.append(f"    CustomLog \"{acc}\" combined")
        if err:
            lines.append(f"    ErrorLog \"{err}\"")
        if self.extra.strip():
            lines.append("    # Extra directives")
            for ln in self.extra.strip().splitlines():
                lines.append(f"    {ln}")
        lines.append(f"</VirtualHost>")
        lines.append(f"{MARK_END}{self.name}")
        return "\n".join(lines) + "\n\n"

VHOST_RE = re.compile(
    rf"{re.escape(MARK_BEGIN)}(?P<name>[^\r\n]+)\r?\n(?P<body>.*?){re.escape(MARK_END)}(?P=name)",
    re.DOTALL
)

def read_file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")

def backup_file(path: Path):
    if not path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    shutil.copy2(str(path), str(bak))
    return bak

def ensure_include_enabled(httpd_conf: Path):
    try:
        text = read_file_text(httpd_conf)
    except FileNotFoundError:
        return
    include_line = r"Include conf/extra/httpd-vhosts.conf"
    if include_line in text and not re.search(r"^\s*#\s*Include\s+conf/extra/httpd-vhosts\.conf", text, re.MULTILINE):
        return
    new_text = re.sub(r"^\s*#\s*Include\s+conf/extra/httpd-vhosts\.conf",
                      "Include conf/extra/httpd-vhosts.conf", text, flags=re.MULTILINE)
    if new_text == text and include_line not in text:
        new_text = text + ("\n" if not text.endswith("\n") else "") + include_line + "\n"
    if new_text != text:
        backup_file(httpd_conf)
        httpd_conf.write_text(new_text, encoding="utf-8")

def parse_managed_vhosts(text: str) -> dict:
    vhosts = {}
    for m in VHOST_RE.finditer(text):
        name = m.group("name").strip()
        body = m.group("body")
        def grab(pattern, default=""):
            mm = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
            return mm.group(1).strip() if mm else default
        server_name = grab(r"^\s*ServerName\s+(.+)$", "")
        server_alias = grab(r"^\s*ServerAlias\s+(.+)$", "")
        document_root = grab(r"^\s*DocumentRoot\s+\"?(.+?)\"?\s*$", "")
        directory_path = grab(r"<Directory\s+\"?(.+?)\"?\s*>\s*", document_root)
        allow_override = grab(r"^\s*AllowOverride\s+(.+)$", "All")
        error_log = grab(r"^\s*ErrorLog\s+\"?(.+?)\"?\s*$", "")
        access_log = grab(r"^\s*CustomLog\s+\"?(.+?)\"?\s+\w+", "")
        port_m = re.search(r"<VirtualHost\s+[^\s>]+:(\d+)\s*>", body, re.IGNORECASE)
        port = int(port_m.group(1)) if port_m else 80
        vhosts[name] = VHost(
            name=name,
            server_name=server_name,
            server_alias=server_alias,
            document_root=document_root,
            port=port,
            allow_override=allow_override,
            directory_path=directory_path,
            error_log=error_log,
            access_log=access_log,
            extra=""
        )
    return vhosts

def write_managed_vhosts(original_text: str, vhosts: dict, listen_ip="*", logs_dir="logs") -> str:
    text = VHOST_RE.sub("", original_text).strip() + "\n\n"
    for name in sorted(vhosts.keys()):
        text += vhosts[name].to_block(listen_ip=listen_ip, logs_dir=logs_dir)
    return text

def add_hosts_entries(hosts_path: Path, ip: str, server_name: str, server_alias: str):
    content = read_file_text(hosts_path) if hosts_path.exists() else ""
    lines = content.splitlines()
    def has_mapping(host):
        pat = re.compile(rf"^\s*{re.escape(ip)}\s+.*\b{re.escape(host)}\b", re.IGNORECASE)
        return any(pat.search(ln) for ln in lines)
    changed = False
    for host in filter(None, [server_name] + server_alias.split()):
        if host and not has_mapping(host):
            lines.append(f"{ip} {host}")
            changed = True
    if changed:
        backup_file(hosts_path)
        hosts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed

def remove_hosts_entries(hosts_path: Path, hosts: list):
    if not hosts_path.exists():
        return False
    content = read_file_text(hosts_path)
    lines = content.splitlines()
    new_lines = []
    changed = False
    for ln in lines:
        if any(re.search(rf"\b{re.escape(h)}\b", ln, re.IGNORECASE) for h in hosts):
            tokens = ln.split()
            if len(tokens) >= 2:
                ip = tokens[0]
                names = [n for n in tokens[1:] if n.lower() not in [h.lower() for h in hosts]]
                if names:
                    new_lines.append(ip + " " + " ".join(names))
            changed = True
        else:
            new_lines.append(ln)
    if changed:
        backup_file(hosts_path)
        hosts_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return changed

def restart_apache(apache_bin: Path):
    if not apache_bin.exists():
        return "Apache binary not found: " + str(apache_bin)
    try:
        out = subprocess.check_output([str(apache_bin), "-k", "restart"], stderr=subprocess.STDOUT, shell=False, timeout=25)
        return out.decode(errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore")
    except Exception as e:
        return str(e)

# -------- Quick Add (domain + zip/folder) helpers --------
def ensure_listen_port(httpd_conf: Path, port: int):
    if port in (80, 443):
        return False
    txt = read_file_text(httpd_conf) if httpd_conf.exists() else ""
    pat = re.compile(rf"^\s*Listen\s+{port}\s*$", re.MULTILINE)
    if pat.search(txt):
        return False
    backup_file(httpd_conf)
    new_txt = txt + ("" if txt.endswith("\n") else "\n") + f"Listen {port}\n"
    httpd_conf.write_text(new_txt, encoding="utf-8")
    return True

def is_port_free(port: int, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            return s.connect_ex((host, port)) != 0
        except OSError:
            return False

def pick_free_port(start=8080, end=9000):
    for p in range(start, end+1):
        if is_port_free(p):
            return p
    return 0

def smart_extract_zip(zip_file: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file, 'r') as z:
        z.extractall(dest_dir)
    entries = [p for p in dest_dir.iterdir() if not p.name.startswith("__MACOSX")]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return dest_dir

def sanitize_domain_to_folder(domain: str):
    safe = re.sub(r'[^a-zA-Z0-9.-]', '-', domain).strip('.-')
    return safe or f"site-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def make_temp_zip_from_folder(folder: Path) -> Path:
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")
    tmpdir = Path(tempfile.mkdtemp(prefix="vhsrc_"))
    outzip = tmpdir / (folder.name + ".zip")
    with zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            for f in files:
                full = Path(root) / f
                arc = str(full.relative_to(folder))
                z.write(str(full), arcname=arc)
    return outzip

def resolve_source_to_zip(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_file() and p.suffix.lower() == ".zip":
        return p
    if p.is_dir():
        return make_temp_zip_from_folder(p)
    raise FileNotFoundError(f"Source not found or unsupported: {path_str}")

def get_sources_list(cfg: dict):
    arr = cfg.get("sources", [])
    if not isinstance(arr, list):
        return []
    out = []
    for item in arr:
        if isinstance(item, dict) and "name" in item and "path" in item:
            out.append({"name": item["name"], "path": item["path"]})
    return out

def add_source_to_config(config_path: Path, cfg: dict, name: str, path: str):
    arr = get_sources_list(cfg)
    for it in arr:
        if it["name"].lower() == name.lower():
            it["path"] = path
            break
    else:
        arr.append({"name": name, "path": path})
    cfg["sources"] = arr
    save_config(config_path, cfg)

def remove_source_from_config(config_path: Path, cfg: dict, name: str):
    arr = [it for it in get_sources_list(cfg) if it["name"].lower() != name.lower()]
    cfg["sources"] = arr
    save_config(config_path, cfg)

def quick_add_domain_zip(app, domain: str, zip_path: Path):
    domain = domain.strip().lower()
    if not domain or not zip_path.exists():
        raise ValueError("Missing domain or ZIP path.")
    projects_dir = Path(app.cfg.get("projects_dir", str(Path.home() / "xampp_projects")))
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = sanitize_domain_to_folder(domain) + "_" + suffix
    target_dir = projects_dir / folder_name

    docroot = smart_extract_zip(zip_path, target_dir)

    # port select
    port_mode = app.cfg.get("port_mode", "namebased")
    if port_mode == "unique":
        port = pick_free_port(app.cfg.get("port_start", 8080), app.cfg.get("port_end", 9000))
        if not port:
            raise RuntimeError("No free port found in configured range.")
        ensure_listen_port(app.httpd_conf, port)
    else:
        port = int(app.cfg.get("default_port", 80))

    name = re.sub(r'[^a-zA-Z0-9_-]+', '-', domain)
    vh = VHost(
        name=name,
        server_name=domain,
        server_alias="",
        document_root=str(docroot),
        port=port,
        allow_override="All"
    )
    app.vhosts[vh.name] = vh

    # write config
    text = write_managed_vhosts(app.original_text, app.vhosts, listen_ip=app.cfg.get("listen_ip", "*"), logs_dir=app.cfg.get("logs_dir", ""))
    backup_file(app.vhosts_conf)
    app.vhosts_conf.write_text(text, encoding="utf-8")

    # hosts mapping
    add_hosts_entries(app.hosts_path, app.cfg.get("listen_ip", "127.0.0.1"), vh.server_name, vh.server_alias)

    # restart apache
    restart_apache(app.apache_bin)
    return vh, target_dir

class VHostDialog(tk.Toplevel):
    def __init__(self, master, cfg, vhost: VHost = None):
        super().__init__(master)
        self.title("VirtualHost")
        self.resizable(False, False)
        self.result = None
        self.cfg = cfg
        # Fields
        self.var_name = tk.StringVar(value=(vhost.name if vhost else ""))
        self.var_server_name = tk.StringVar(value=(vhost.server_name if vhost else ""))
        self.var_server_alias = tk.StringVar(value=(vhost.server_alias if vhost else ""))
        self.var_document_root = tk.StringVar(value=(vhost.document_root if vhost else ""))
        self.var_directory_path = tk.StringVar(value=(vhost.directory_path if vhost else ""))
        self.var_allow_override = tk.StringVar(value=(vhost.allow_override if vhost else "All"))
        self.var_port = tk.IntVar(value=(vhost.port if vhost else cfg.get("default_port", 80)))
        self.var_extra = tk.StringVar(value=(vhost.extra if vhost else ""))

        pad = {"padx": 6, "pady": 4}
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Internal Name (unique)").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_name, width=36).grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(frm, text="ServerName").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_server_name, width=36).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(frm, text="ServerAlias").grid(row=2, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_server_alias, width=36).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frm, text="DocumentRoot").grid(row=3, column=0, sticky="e", **pad)
        dr_ent = ttk.Entry(frm, textvariable=self.var_document_root, width=36)
        dr_ent.grid(row=3, column=1, sticky="w", **pad)
        ttk.Button(frm, text="Browse…", command=self.browse_root).grid(row=3, column=2, **pad)

        ttk.Label(frm, text="Directory (optional)").grid(row=4, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_directory_path, width=36).grid(row=4, column=1, sticky="w", **pad)

        ttk.Label(frm, text="AllowOverride").grid(row=5, column=0, sticky="e", **pad)
        ttk.Combobox(frm, textvariable=self.var_allow_override, values=["All", "None"], width=10, state="readonly").grid(row=5, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Port").grid(row=6, column=0, sticky="e", **pad)
        ttk.Spinbox(frm, from_=1, to=65535, textvariable=self.var_port, width=10).grid(row=6, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Extra directives").grid(row=7, column=0, sticky="ne", **pad)
        txt = tk.Text(frm, name="extra_txt", height=5, width=36)
        txt.grid(row=7, column=1, sticky="w", **pad)
        self.children_extra = txt
        self.children_extra.insert("1.0", self.var_extra.get())

        btns = ttk.Frame(frm)
        btns.grid(row=8, column=0, columnspan=3, sticky="e", pady=(10,0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text="OK", command=self.ok).pack(side="right")

    def browse_root(self):
        d = filedialog.askdirectory(title="Select DocumentRoot")
        if d:
            self.var_document_root.set(d)

    def ok(self):
        name = self.var_name.get().strip()
        sname = self.var_server_name.get().strip()
        if not name or not sname:
            messagebox.showerror("Missing field", "Please fill at least Internal Name and ServerName.")
            return
        v = VHost(
            name=name,
            server_name=sname,
            server_alias=self.var_server_alias.get().strip(),
            document_root=self.var_document_root.get().strip(),
            port=int(self.var_port.get() or 80),
            allow_override=self.var_allow_override.get().strip() or "All",
            directory_path=self.var_directory_path.get().strip(),
            error_log="",
            access_log="",
            extra=self.children_extra.get("1.0", "end").strip()
        )
        self.result = v
        self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x600")
        self.resizable(True, True)
        self.config_path = Path("vhost_manager.config.json")
        self.cfg = load_config(self.config_path)

        self.vhosts_conf = Path(self.cfg["vhosts_conf_path"])
        # httpd.conf is two levels up then /conf/httpd.conf
        self.httpd_conf = self.vhosts_conf.parent.parent / "conf" / "httpd.conf"
        self.hosts_path = Path(self.cfg["hosts_path"])
        self.apache_bin = Path(self.cfg["apache_bin"])
        self.logs_dir = self.cfg.get("logs_dir", "")
        ensure_include_enabled(self.httpd_conf)

        self.vhosts = {}
        self.original_text = ""

        self.create_widgets()
        self.load_vhosts()
        self.refresh_sources_ui()

    def create_widgets(self):
        # ---- ROW 1: VHost management ----
        row1 = ttk.Frame(self); row1.pack(fill="x", padx=10, pady=6)
        ttk.Button(row1, text="New", command=self.new_vhost).pack(side="left", padx=4)
        ttk.Button(row1, text="Edit", command=self.edit_vhost).pack(side="left", padx=4)
        ttk.Button(row1, text="Delete", command=self.delete_vhost).pack(side="left", padx=4)

        # ---- ROW 2: Apache actions ----
        row2 = ttk.Frame(self); row2.pack(fill="x", padx=10, pady=6)
        ttk.Button(row2, text="Write Config", command=self.write_config).pack(side="left", padx=4)
        ttk.Button(row2, text="Restart Apache", command=self.do_restart).pack(side="left", padx=4)
        ttk.Button(row2, text="Open in Browser", command=self.open_in_browser).pack(side="left", padx=4)

        # ---- ROW 3: Hosts management ----
        row3 = ttk.Frame(self); row3.pack(fill="x", padx=10, pady=6)
        ttk.Button(row3, text="Add to hosts", command=self.add_to_hosts).pack(side="left", padx=4)
        ttk.Button(row3, text="Remove from hosts", command=self.remove_from_hosts).pack(side="left", padx=4)

        # ---- ROW 4: Config + Quick Add ----
        row4 = ttk.Frame(self); row4.pack(fill="x", padx=10, pady=6)
        ttk.Button(row4, text="Config…", command=self.edit_config).pack(side="left", padx=4)
        ttk.Button(row4, text="Reload", command=self.load_vhosts).pack(side="left", padx=4)
        ttk.Separator(row4, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(row4, text="Domain:").pack(side="left")
        self.var_q_domain = tk.StringVar(value="")
        ttk.Entry(row4, textvariable=self.var_q_domain, width=28).pack(side="left", padx=4)
        ttk.Button(row4, text="Select ZIP…", command=self.pick_zip).pack(side="left", padx=2)
        ttk.Button(row4, text="Quick Add", command=self.quick_add).pack(side="left", padx=2)
        ttk.Separator(row4, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(row4, text="Source:").pack(side="left")
        self.var_source = tk.StringVar(value="")
        self.cmb_source = ttk.Combobox(row4, textvariable=self.var_source, width=22, state="readonly")
        self.cmb_source.pack(side="left", padx=4)
        ttk.Button(row4, text="Add Source…", command=self.add_source).pack(side="left", padx=2)
        ttk.Button(row4, text="Remove Source", command=self.remove_source).pack(side="left", padx=2)
        ttk.Button(row4, text="Use Source", command=self.quick_add_from_source).pack(side="left", padx=2)

        # ---- Middle: Tree of vhosts ----
        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=10, pady=8)
        cols = ("name", "server_name", "server_alias", "document_root", "port")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140 if c != "document_root" else 260, anchor="w", stretch=True)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=8)
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(bottom, textvariable=self.status).pack(side="left")

    def set_status(self, msg):
        self.status.set(msg)
        self.update_idletasks()

    def load_vhosts(self):
        # ensure vhosts file exists
        if not self.vhosts_conf.exists():
            self.vhosts_conf.parent.mkdir(parents=True, exist_ok=True)
            self.vhosts_conf.write_text("", encoding="utf-8")
        self.original_text = read_file_text(self.vhosts_conf)
        self.vhosts = parse_managed_vhosts(self.original_text)
        # refresh tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        for name, v in sorted(self.vhosts.items()):
            self.tree.insert("", "end", iid=name, values=(v.name, v.server_name, v.server_alias, v.document_root, v.port))
        self.set_status(f"Loaded {len(self.vhosts)} managed vhost(s).")

    def selected_vhost(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select item", "Please select a VirtualHost in the list.")
            return None
        name = sel[0]
        return self.vhosts.get(name)

    def new_vhost(self):
        dlg = VHostDialog(self, self.cfg, None)
        self.wait_window(dlg)
        if dlg.result:
            v = dlg.result
            if v.name in self.vhosts:
                messagebox.showerror("Duplicate", "Internal Name must be unique.")
                return
            self.vhosts[v.name] = v
            self.tree.insert("", "end", iid=v.name, values=(v.name, v.server_name, v.server_alias, v.document_root, v.port))

    def edit_vhost(self):
        v = self.selected_vhost()
        if not v:
            return
        dlg = VHostDialog(self, self.cfg, v)
        self.wait_window(dlg)
        if dlg.result:
            nv = dlg.result
            if nv.name != v.name and nv.name in self.vhosts:
                messagebox.showerror("Duplicate", "Internal Name already exists.")
                return
            del self.vhosts[v.name]
            self.vhosts[nv.name] = nv
            self.load_vhosts_from_memory()

    def load_vhosts_from_memory(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for name, v in sorted(self.vhosts.items()):
            self.tree.insert("", "end", iid=name, values=(v.name, v.server_name, v.server_alias, v.document_root, v.port))

    def delete_vhost(self):
        v = self.selected_vhost()
        if not v:
            return
        if messagebox.askyesno("Confirm", f"Delete vhost '{v.name}'? (This removes it from config but not from hosts file.)"):
            del self.vhosts[v.name]
            self.tree.delete(v.name)

    def write_config(self):
        text = write_managed_vhosts(self.original_text, self.vhosts, listen_ip=self.cfg.get("listen_ip", "*"), logs_dir=self.cfg.get("logs_dir",""))
        backup_file(self.vhosts_conf)
        self.vhosts_conf.write_text(text, encoding="utf-8")
        self.set_status(f"Wrote {self.vhosts_conf} ({len(self.vhosts)} vhost(s)).")

    def do_restart(self):
        out = restart_apache(self.apache_bin)
        messagebox.showinfo("Apache restart", out or "Done")
        self.set_status("Apache restart attempted.")

    def open_in_browser(self):
        v = self.selected_vhost()
        if not v:
            return
        url = f"http://{v.server_name}:{v.port}/"
        webbrowser.open(url)

    def add_to_hosts(self):
        v = self.selected_vhost()
        if not v:
            return
        try:
            changed = add_hosts_entries(self.hosts_path, self.cfg.get("listen_ip", "127.0.0.1"), v.server_name, v.server_alias)
            if changed:
                self.set_status("Hosts file updated.")
                messagebox.showinfo("hosts", "Added mapping(s) to hosts file.\nNote: Requires Administrator rights.")
            else:
                messagebox.showinfo("hosts", "Mappings already present.")
        except PermissionError:
            messagebox.showerror("Permission denied", "Permission denied writing to hosts file.\nRun this app as Administrator.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_from_hosts(self):
        v = self.selected_vhost()
        if not v:
            return
        try:
            hosts = [v.server_name] + (v.server_alias.split() if v.server_alias else [])
            changed = remove_hosts_entries(self.hosts_path, hosts)
            if changed:
                self.set_status("Hosts file updated (removed entries).")
            else:
                messagebox.showinfo("hosts", "No matching entries found.")
        except PermissionError:
            messagebox.showerror("Permission denied", "Permission denied writing to hosts file.\nRun this app as Administrator.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_config(self):
        dlg = tk.Toplevel(self)
        dlg.title("Settings")
        dlg.resizable(False, False)

        def row(lbl, var, browse=False, is_dir=False):
            f = ttk.Frame(dlg)
            f.pack(fill="x", padx=10, pady=5)
            ttk.Label(f, text=lbl, width=20).pack(side="left")
            e = ttk.Entry(f, textvariable=var, width=60)
            e.pack(side="left", padx=4)
            if browse:
                def do_browse():
                    if is_dir:
                        p = filedialog.askdirectory()
                    else:
                        p = filedialog.askopenfilename()
                    if p:
                        var.set(p)
                ttk.Button(f, text="Browse…", command=do_browse).pack(side="left")
            return f

        var_vhosts = tk.StringVar(value=str(self.vhosts_conf))
        var_hosts = tk.StringVar(value=str(self.hosts_path))
        var_httpd = tk.StringVar(value=str(self.apache_bin))
        var_ip = tk.StringVar(value=self.cfg.get("listen_ip", "127.0.0.1"))
        var_port = tk.IntVar(value=self.cfg.get("default_port", 80))
        var_logs = tk.StringVar(value=self.cfg.get("logs_dir", ""))
        var_proj = tk.StringVar(value=self.cfg.get("projects_dir", ""))
        var_mode = tk.StringVar(value=self.cfg.get("port_mode", "namebased"))
        var_pstart = tk.IntVar(value=self.cfg.get("port_start", 8080))
        var_pend = tk.IntVar(value=self.cfg.get("port_end", 9000))

        row("httpd-vhosts.conf", var_vhosts, browse=True)
        row("hosts file", var_hosts, browse=True)
        row("Apache httpd.exe", var_httpd, browse=True)
        row("Listen IP", var_ip, browse=False)
        row("Default Port", var_port, browse=False)
        row("Logs dir", var_logs, browse=True, is_dir=True)
        row("Projects dir", var_proj, browse=True, is_dir=True)

        fmode = ttk.Frame(dlg); fmode.pack(fill="x", padx=10, pady=5)
        ttk.Label(fmode, text="Port mode", width=20).pack(side="left")
        ttk.Combobox(fmode, textvariable=var_mode, values=["namebased","unique"], state="readonly", width=12).pack(side="left")
        fports = ttk.Frame(dlg); fports.pack(fill="x", padx=10, pady=5)
        ttk.Label(fports, text="Unique range", width=20).pack(side="left")
        ttk.Entry(fports, textvariable=var_pstart, width=8).pack(side="left")
        ttk.Label(fports, text="to").pack(side="left", padx=4)
        ttk.Entry(fports, textvariable=var_pend, width=8).pack(side="left")

        btns = ttk.Frame(dlg); btns.pack(fill="x", padx=10, pady=10)
        def save():
            self.cfg["vhosts_conf_path"] = var_vhosts.get().strip()
            self.cfg["hosts_path"] = var_hosts.get().strip()
            self.cfg["apache_bin"] = var_httpd.get().strip()
            self.cfg["listen_ip"] = var_ip.get().strip() or "127.0.0.1"
            self.cfg["default_port"] = int(var_port.get() or 80)
            self.cfg["logs_dir"] = var_logs.get().strip()
            self.cfg["projects_dir"] = var_proj.get().strip()
            self.cfg["port_mode"] = var_mode.get().strip() or "namebased"
            self.cfg["port_start"] = int(var_pstart.get() or 8080)
            self.cfg["port_end"] = int(var_pend.get() or 9000)
            save_config(self.config_path, self.cfg)
            # reload paths
            self.vhosts_conf = Path(self.cfg["vhosts_conf_path"])
            self.hosts_path = Path(self.cfg["hosts_path"])
            self.apache_bin = Path(self.cfg["apache_bin"])
            self.logs_dir = self.cfg.get("logs_dir", "")
            ensure_include_enabled(self.httpd_conf)
            self.load_vhosts()
            self.refresh_sources_ui()
            dlg.destroy()
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text="Save", command=save).pack(side="right")

    def refresh_sources_ui(self):
        items = [it["name"] for it in get_sources_list(self.cfg)]
        if hasattr(self, "cmb_source"):
            self.cmb_source["values"] = items
        if items and hasattr(self, "var_source") and not self.var_source.get():
            self.var_source.set(items[0])

    def pick_zip(self):
        p = filedialog.askopenfilename(title="Select ZIP file", filetypes=[("ZIP files","*.zip")])
        if p:
            self._quick_zip_path = Path(p)

    def quick_add(self):
        try:
            z = getattr(self, "_quick_zip_path", None)
            if not z:
                messagebox.showerror("Missing ZIP", "Please select a ZIP file.")
                return
            domain = self.var_q_domain.get().strip()
            if not domain:
                messagebox.showerror("Missing domain", "Please enter a domain (e.g., mysite.local).")
                return
            vh, folder = quick_add_domain_zip(self, domain, Path(z))
            self.load_vhosts()
            self.set_status(f"Quick added {vh.server_name} -> {folder} (port {vh.port}).")
            messagebox.showinfo("Done", f"Domain: {vh.server_name}\nDocRoot: {folder}\nPort: {vh.port}")
        except PermissionError:
            messagebox.showerror("Permission denied", "Need Administrator rights to update hosts file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def quick_add_from_source(self):
        domain = self.var_q_domain.get().strip()
        if not domain:
            messagebox.showerror("Missing domain", "Please enter a domain."); return
        name = self.var_source.get().strip()
        if not name:
            messagebox.showerror("Missing source", "Please choose a Source or add one."); return
        path = None
        for it in get_sources_list(self.cfg):
            if it["name"] == name:
                path = it["path"]; break
        if not path:
            messagebox.showerror("Not found", f"Source '{name}' not found in config."); return
        try:
            src_zip = resolve_source_to_zip(path)
            vh, folder = quick_add_domain_zip(self, domain, Path(src_zip))
            self.load_vhosts()
            self.set_status(f"Quick added from source {name}: {vh.server_name} -> {folder} (port {vh.port}).")
            messagebox.showinfo("Done", f"Domain: {vh.server_name}\nDocRoot: {folder}\nPort: {vh.port}")
        except PermissionError:
            messagebox.showerror("Permission denied", "Need Administrator rights to update hosts file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_source(self):
        dlg = tk.Toplevel(self); dlg.title("Add Source"); dlg.resizable(False, False)
        name_var = tk.StringVar(value="")
        path_var = tk.StringVar(value="")

        f1 = ttk.Frame(dlg); f1.pack(fill="x", padx=10, pady=6)
        ttk.Label(f1, text="Name", width=12).pack(side="left")
        ttk.Entry(f1, textvariable=name_var, width=40).pack(side="left", padx=4)

        f2 = ttk.Frame(dlg); f2.pack(fill="x", padx=10, pady=6)
        ttk.Label(f2, text="Path", width=12).pack(side="left")
        ttk.Entry(f2, textvariable=path_var, width=40).pack(side="left", padx=4)
        def pick():
            p = filedialog.askopenfilename(title="Select ZIP or pick a folder", filetypes=[("ZIP files","*.zip"), ("All files","*.*")])
            if not p:
                d = filedialog.askdirectory(title="Select Source Folder")
                if d: path_var.set(d)
            else:
                path_var.set(p)
        ttk.Button(f2, text="Browse…", command=pick).pack(side="left")

        fb = ttk.Frame(dlg); fb.pack(fill="x", padx=10, pady=10)
        def ok():
            n = name_var.get().strip()
            pth = path_var.get().strip()
            if not n or not pth:
                messagebox.showerror("Missing", "Please enter both Name and Path (ZIP or Folder)."); return
            try:
                add_source_to_config(self.config_path, self.cfg, n, pth)
                self.cfg = load_config(self.config_path)
                self.refresh_sources_ui()
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(fb, text="Cancel", command=dlg.destroy).pack(side="right", padx=4)
        ttk.Button(fb, text="Save", command=ok).pack(side="right")

    def remove_source(self):
        name = self.var_source.get().strip()
        if not name:
            messagebox.showinfo("Select", "Choose a source to remove."); return
        if not messagebox.askyesno("Confirm", f"Remove source '{name}'?"): return
        remove_source_from_config(self.config_path, self.cfg, name)
        self.cfg = load_config(self.config_path)
        self.refresh_sources_ui()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
