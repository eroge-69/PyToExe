import ssl
#!/usr/bin/env python3
# usp_autoabholer.py
# USP Autoabholung (Mein Postkorb, AT) – Multi-Mandanten, Mail-Client-UI, Auto-Loop, SMTP
# SSL-Validierung ist deaktiviert (verify=False). Nutzung auf eigene Gefahr.
# © Thomas Kirchler 2025 v1.11

import os, sys, sqlite3, threading, time, traceback
from pathlib import Path
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from email.message import EmailMessage
import smtplib
import xml.etree.ElementTree as ET

# cryptography (PKCS12 -> PEM)
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.backends import default_backend

APP_NAME   = "USP Autoabholer"
APP_VER    = "v1.11"
APP_AUTHOR = "Thomas Kirchler"

# ----- Pfade / Defaults -----
BASE = Path.cwd()
CONFIG_DIR = BASE / "config"; CONFIG_DIR.mkdir(exist_ok=True)
DB_FILE    = CONFIG_DIR / "usp_multi.db"
DEFAULT_DL_ROOT = (BASE / "downloads").resolve(); DEFAULT_DL_ROOT.mkdir(exist_ok=True)
CERT_PEM   = CONFIG_DIR / "cert.pem"   # wird pro aktivem Mandanten überschrieben
KEY_PEM    = CONFIG_DIR / "key.pem"

ENDPOINT_DEFAULT = "https://autoabholung.meinpostkorb.brz.gv.at/soap"

# Namespaces
NS_AA  = "http://reference.e-government.gv.at/namespace/zustellung/autoabholung/phase2/20181206#"
NS_ENV = "http://www.w3.org/2003/05/soap-envelope"
NS_PD  = "http://reference.e-government.gv.at/namespace/persondata/phase2/20181206#"
NS_MSG = "http://reference.e-government.gv.at/namespace/zustellung/msg/phase2/20181206#"
NS = {"aa":NS_AA, "env":NS_ENV, "pd":NS_PD, "msg":NS_MSG}

# ----- In-Memory GUI-Log (Ringpuffer) -----
class GuiLogger:
    def __init__(self, text_widget:scrolledtext.ScrolledText, cap_lines:int=200):
        self.txt = text_widget
        self.cap = max(50, cap_lines)
        # Tags
        self.txt.tag_config("DEBUG", foreground="#777777")
        self.txt.tag_config("INFO",  foreground="#000000")
        self.txt.tag_config("WARN",  foreground="#d17f00")
        self.txt.tag_config("ERROR", foreground="#b00020")
    def write(self, line:str, level:str="INFO"):
        try:
            level = level.upper()
            if level not in ("DEBUG","INFO","WARN","ERROR"):
                level = "INFO"
            # Einfügen
            self.txt.insert("end", line+"\n", level)
            # Ringpuffer begrenzen (Zeilen zählen)
            lines = int(self.txt.index('end-1c').split('.')[0])
            if lines > self.cap:
                # Überschuss entfernen
                start_line = lines - self.cap
                self.txt.delete("1.0", f"{start_line}.0")
            self.txt.see("end")
        except Exception:
            pass

# ----- DB & Migration -----
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS mandanten (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE,
      p12_path TEXT,
      p12_pass TEXT,
      p12_blob BLOB,
      endpoint TEXT,
      download_dir TEXT,
      smtp_server TEXT,
      smtp_port INTEGER,
      smtp_user TEXT,
      smtp_pass TEXT,
      smtp_security TEXT,
      smtp_target TEXT,
      auto_enabled INTEGER,
      auto_forward INTEGER,
      interval_min INTEGER
    )
    """)
    c.execute("""CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
      delivery_id TEXT,
      mandant TEXT,
      subject TEXT,
      sender TEXT,
      ts TEXT,
      fetched_at TEXT,
      forwarded_at TEXT,
      PRIMARY KEY (delivery_id, mandant)
    )
    """)
    # Defaults
    c.execute("SELECT COUNT(*) FROM mandanten")
    if c.fetchone()[0]==0:
        default_dl = str((DEFAULT_DL_ROOT / "Default").resolve())
        c.execute("""INSERT INTO mandanten
        (name,p12_path,p12_pass,p12_blob,endpoint,download_dir,smtp_server,smtp_port,smtp_user,smtp_pass,smtp_security,smtp_target,auto_enabled,auto_forward,interval_min)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("Default", "", "", None, ENDPOINT_DEFAULT, default_dl, "", 587, "", "", "STARTTLS", "", 0, 0, 60))
        c.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('active_mandant','Default')")
    else:
        c.execute("SELECT v FROM meta WHERE k='active_mandant'")
        if not c.fetchone():
            c.execute("SELECT name FROM mandanten ORDER BY id LIMIT 1")
            r = c.fetchone()
            if r: c.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('active_mandant',?)",(r[0],))
    conn.commit(); conn.close()
init_db()

def db_list_mandanten():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT name FROM mandanten ORDER BY name"); rows = [r[0] for r in c.fetchall()]
    conn.close(); return rows

def db_get_active():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT v FROM meta WHERE k='active_mandant'"); r = c.fetchone()
    conn.close(); return r[0] if r else None

def db_set_active(name:str):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('active_mandant',?)",(name,))
    conn.commit(); conn.close()

def db_get_cfg(name:str):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT name,p12_path,p12_pass,p12_blob,endpoint,download_dir,smtp_server,smtp_port,smtp_user,smtp_pass,smtp_security,smtp_target,auto_enabled,auto_forward,interval_min
                 FROM mandanten WHERE name=?""",(name,))
    r = c.fetchone(); conn.close()
    if not r: return None
    keys=("name","p12_path","p12_pass","p12_blob","endpoint","dl","smtp_server","smtp_port","smtp_user","smtp_pass","smtp_sec","smtp_to","auto_enabled","auto_forward","interval_min")
    d = dict(zip(keys,r))
    dl_dir = d["dl"] or str((DEFAULT_DL_ROOT / d["name"]).resolve())
    return {
        "name": d["name"],
        "p12_path": d["p12_path"] or "",
        "p12_blob": d["p12_blob"],
        "pw": d["p12_pass"] or "",
        "endpoint": d["endpoint"] or ENDPOINT_DEFAULT,
        "dl": dl_dir,
        "smtp_server": d["smtp_server"] or "",
        "smtp_port": int(d["smtp_port"] or 0),
        "smtp_user": d["smtp_user"] or "",
        "smtp_pass": d["smtp_pass"] or "",
        "smtp_sec": d["smtp_sec"] or "STARTTLS",
        "smtp_to": d["smtp_to"] or "",
        "auto_enabled": int(d["auto_enabled"] or 0),
        "auto_forward": int(d["auto_forward"] or 0),
        "interval_min": int(d["interval_min"] or 60),
    }

def db_upsert_cfg(cfg:dict):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id FROM mandanten WHERE name=?",(cfg["name"],))
    exists = c.fetchone() is not None
    dl_dir = cfg.get("dl") or str((DEFAULT_DL_ROOT / cfg["name"]).resolve())
    args = (
        cfg.get("p12_path",""), cfg.get("pw",""),
        cfg.get("p12_blob", None),
        cfg.get("endpoint",ENDPOINT_DEFAULT), dl_dir,
        cfg.get("smtp_server",""), int(cfg.get("smtp_port",0) or 0),
        cfg.get("smtp_user",""), cfg.get("smtp_pass",""),
        cfg.get("smtp_sec","STARTTLS"), cfg.get("smtp_to",""),
        int(bool(cfg.get("auto_enabled",0))), int(bool(cfg.get("auto_forward",0))),
        int(cfg.get("interval_min",60))
    )
    if exists:
        c.execute("""UPDATE mandanten SET
            p12_path=?, p12_pass=?, p12_blob=?, endpoint=?, download_dir=?, smtp_server=?, smtp_port=?, smtp_user=?, smtp_pass=?, smtp_security=?, smtp_target=?, auto_enabled=?, auto_forward=?, interval_min=?
            WHERE name=?""", args + (cfg["name"],))
    else:
        c.execute("""INSERT INTO mandanten
            (name,p12_path,p12_pass,p12_blob,endpoint,download_dir,smtp_server,smtp_port,smtp_user,smtp_pass,smtp_security,smtp_target,auto_enabled,auto_forward,interval_min)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (cfg["name"],)+args)
    conn.commit(); conn.close()

def db_delete_mandant(name:str):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM mandanten WHERE name=?", (name,))
    conn.commit(); conn.close()

# Delivery-Status
def db_mark_fetched(mandant, did, meta):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO deliveries(delivery_id,mandant,subject,sender,ts,fetched_at,forwarded_at)
                 VALUES(?,?,?,?,?,?,COALESCE((SELECT forwarded_at FROM deliveries WHERE delivery_id=? AND mandant=?),NULL))""",
              (did, mandant, meta.get("subject",""), meta.get("sender",""), meta.get("timestamp",""),
               datetime.now(timezone.utc).isoformat(), did, mandant))
    conn.commit(); conn.close()

def db_mark_forwarded(mandant, did):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""UPDATE deliveries SET forwarded_at=? WHERE delivery_id=? AND mandant=?""",
              (datetime.now(timezone.utc).isoformat(), did, mandant))
    conn.commit(); conn.close()

def db_is_fetched(mandant, did)->bool:
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT 1 FROM deliveries WHERE delivery_id=? AND mandant=? AND fetched_at IS NOT NULL", (did, mandant))
    r = c.fetchone(); conn.close(); return bool(r)

def db_is_forwarded(mandant, did)->bool:
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT 1 FROM deliveries WHERE delivery_id=? AND mandant=? AND forwarded_at IS NOT NULL", (did, mandant))
    r = c.fetchone(); conn.close(); return bool(r)

def db_list_known_ids(mandant)->set:
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT delivery_id FROM deliveries WHERE mandant=?", (mandant,))
    out = {r[0] for r in c.fetchall()}
    conn.close(); return out

# ----- PKCS#12 Laden & Export zu PEM -----
def _load_pkcs12_data(cfg):
    if cfg.get("p12_blob"):
        return cfg["p12_blob"]
    path = cfg.get("p12_path") or ""
    if not path or not Path(path).is_file():
        raise RuntimeError(".p12 nicht gefunden (weder DB noch Pfad).")
    return Path(path).read_bytes()

def export_p12_to_pem(cfg, ui_log=None):
    data = _load_pkcs12_data(cfg)
    try:
        key_obj, cert_obj, _ = load_key_and_certificates(data, cfg.get("pw","").encode() if cfg.get("pw") else None, backend=default_backend())
    except Exception as e:
        raise RuntimeError(f".p12 Laden fehlgeschlagen: {e}")
    if not cert_obj or not key_obj:
        raise RuntimeError("Zertifikat/Key fehlen in .p12")
    Path(CERT_PEM).write_bytes(cert_obj.public_bytes(Encoding.PEM))
    Path(KEY_PEM).write_bytes(key_obj.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))
    if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Zertifikat exportiert (cert.pem/key.pem)", "INFO")
    return str(CERT_PEM), str(KEY_PEM), cert_obj

# ----- SOAP Bodies -----
def soap_query(new_only: bool = True, limit: int = 100, start: int = 0):
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
  <env:Header/>
  <env:Body>
    <aa:QueryDeliveriesRequest aa:Version="2.4.0-004" xmlns:aa="{NS_AA}" xmlns:xsi="{xsi}">
      <aa:Query xsi:type="aa:{'NewDeliveriesOnlyType' if new_only else 'AllDeliveriesType'}">
        {'<aa:Limit>'+str(limit)+'</aa:Limit>' if new_only else f'<aa:Paging><aa:Start>{start}</aa:Start><aa:Limit>{limit}</aa:Limit></aa:Paging>'}
      </aa:Query>
    </aa:QueryDeliveriesRequest>
  </env:Body>
</env:Envelope>"""


def soap_get(delivery_id):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="{NS_ENV}">
  <env:Header/>
  <env:Body>
    <aa:GetDeliveryRequest aa:Version="2.4.0-004" xmlns:aa="{NS_AA}">
      <aa:DeliveryID>{delivery_id}</aa:DeliveryID>
    </aa:GetDeliveryRequest>
  </env:Body>
</env:Envelope>"""

def soap_close(delivery_id):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="{NS_ENV}">
  <env:Header/>
  <env:Body>
    <aa:CloseDeliveryRequest aa:Version="2.4.0-004" xmlns:aa="{NS_AA}">
      <aa:DeliveryID>{delivery_id}</aa:DeliveryID>
    </aa:CloseDeliveryRequest>
  </env:Body>
</env:Envelope>"""

def soap_delete(delivery_id):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="{NS_ENV}">
  <env:Header/>
  <env:Body>
    <aa:DeleteDeliveryRequest aa:Version="2.4.0-004" xmlns:aa="{NS_AA}">
      <aa:DeliveryID>{delivery_id}</aa:DeliveryID>
    </aa:DeleteDeliveryRequest>
  </env:Body>
</env:Envelope>"""

# ----- HTTP -----
def soap_post(endpoint, cert_tuple, xml_body, ui_log=None, timeout=90):
    """
    SOAP POST (SOAP 1.2) using client cert; TLS verification disabled (enterprise proxy safe).
    """
    pm = urllib3.PoolManager(
        cert_file=cert_tuple[0],
        key_file=cert_tuple[1],
        cert_reqs=ssl.CERT_NONE,
        assert_hostname=False,
        retries=False,
        timeout=urllib3.util.Timeout(connect=timeout, read=timeout),
    )
    try:
        urllib3.disable_warnings(InsecureRequestWarning)
    except Exception:
        pass

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    body = xml_body if isinstance(xml_body, str) else xml_body.decode("utf-8", "ignore")

    if ui_log:
        ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [DEBUG] POST {endpoint} (SOAP1.2; verify=OFF)", "DEBUG")

    class _Resp:
        def __init__(self, status, data, headers):
            self.status_code = status
            self.content = data or b""
            try:
                self.text = (data or b"").decode("utf-8", "ignore")
            except Exception:
                self.text = ""
            self.headers = headers or {}

    try:
        r = pm.request("POST", endpoint, body=body.encode("utf-8"), headers=headers, preload_content=True)
        resp = _Resp(r.status, r.data, dict(r.headers or {}))
        if resp.status_code != 200 and ui_log:
            snippet = (resp.text or "")[:400]
            ui_log(f"[ERROR] HTTP {resp.status_code} beim SOAP POST: {snippet}", "ERROR")
        return resp
    except Exception as e:
        if ui_log:
            ui_log(f"[ERROR] SOAP POST fehlgeschlagen: {e}", "ERROR")
        raise
def rest_download_attachment(endpoint, delivery_id, attachment_id, filename, cert_tuple, target_dir:Path, ui_log=None):
    """
    Attachment GET; TLS verification disabled (enterprise proxy safe).
    """
    pm = urllib3.PoolManager(
        cert_file=cert_tuple[0],
        key_file=cert_tuple[1],
        cert_reqs=ssl.CERT_NONE,
        assert_hostname=False,
        retries=False,
        timeout=urllib3.util.Timeout(connect=30, read=120),
    )
    try:
        urllib3.disable_warnings(InsecureRequestWarning)
    except Exception:
        pass
    base = f"{requests.utils.urlparse(endpoint).scheme}://{requests.utils.urlparse(endpoint).netloc}"
    url = f"{base}/attachment?delivery_id={delivery_id}&attachment_id={attachment_id}"
    target = (Path(target_dir) / filename).resolve()

    if ui_log:
        ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [DEBUG] GET {url} (verify=OFF)", "DEBUG")

    r = pm.request("GET", url, preload_content=False)
    if r.status not in (200, 206):
        raise RuntimeError(f"HTTP {r.status}")
    with open(target, "wb") as f:
        for chunk in r.stream(65536):
            if chunk:
                f.write(chunk)
    r.release_conn()
    return str(target)


def rest_download_attachment(endpoint, delivery_id, attachment_id, filename, cert_tuple, target_dir:Path, ui_log=None):
    base = f"{requests.utils.urlparse(endpoint).scheme}://{requests.utils.urlparse(endpoint).netloc}"
    url = f"{base}/attachment?delivery_id={delivery_id}&attachment_id={attachment_id}"
    if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Attachment -> {url}", "INFO")
    r = requests.get(url, cert=cert_tuple, verify=False, timeout=120, stream=True)
    r.raise_for_status()
    safe = filename or f"{attachment_id}.bin"
    path = (target_dir / safe).resolve()
    with open(path,"wb") as f:
        for chunk in r.iter_content(8192):
            if chunk: f.write(chunk)
    if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Gespeichert: {path}", "INFO")
    return str(path)

# ----- Parsing -----
def parse_query_ids(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
        ids  = [e.text for e in root.findall(".//aa:DeliveryID", NS) if e is not None and e.text]
        hit_el = root.find(".//aa:HitCount", NS)
        hit = int(hit_el.text) if (hit_el is not None and (hit_el.text or "").isdigit()) else len(ids)
        return ids, hit
    except Exception:
        return [], 0

def parse_delivery_meta(xml_bytes):
    out = {"subject":"", "timestamp":"", "sender":"", "receiver":"", "attachments":[], "mailbody_text":"", "raw": xml_bytes}
    try:
        root = ET.fromstring(xml_bytes)
        subj = root.find(".//msg:Subject", NS); out["subject"] = subj.text if subj is not None else ""
        ts   = root.find(".//msg:DeliveryTimestamp", NS); out["timestamp"] = ts.text if ts is not None else ""
        sfn  = root.find(".//aa:Sender/pd:CorporateBody/pd:FullName", NS); out["sender"]= sfn.text if sfn is not None else ""
        rfn  = root.find(".//aa:Receiver/pd:CorporateBody/pd:FullName", NS); out["receiver"]= rfn.text if rfn is not None else ""
        atts=[]
        for att in root.findall(".//aa:Attachment", NS):
            aid = att.find("aa:AttachmentID", NS)
            fn  = att.find("aa:FileName", NS)
            mt  = att.find("msg:MimeType", NS)
            if aid is not None and fn is not None:
                fname = (fn.text or "").strip()
                if fname.lower()=="mailbody":
                    # Mailbody als Attachment gelistet -> nicht zu den Anhängen zählen
                    continue
                atts.append({"id":aid.text, "file":fname, "mime": (mt.text if mt is not None else None)})
        out["attachments"] = atts
        return out
    except Exception:
        return out

# ----- SMTP -----
def smtp_send(cfg, attachments, subject, body, ui_log=None):
    srv = cfg.get("smtp_server") or ""
    to  = cfg.get("smtp_to") or ""
    if not srv or not to:
        if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [WARN] SMTP unvollständig -> übersprungen","WARN")
        return False
    port = int(cfg.get("smtp_port") or 0)
    user = cfg.get("smtp_user") or ""
    pwd  = cfg.get("smtp_pass") or ""
    sec  = (cfg.get("smtp_sec") or "STARTTLS").upper()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user or f"usp@{os.uname().nodename if hasattr(os,'uname') else 'localhost'}"
    msg["To"] = to
    msg.set_content(body or subject)

    for p in attachments:
        try:
            with open(p,"rb") as f: data=f.read()
            msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=Path(p).name)
        except Exception as e:
            if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] Attachment-Fehler: {e}","ERROR")

    try:
        if sec=="SSL":
            s = smtplib.SMTP_SSL(srv, port or 465, timeout=30)
        else:
            s = smtplib.SMTP(srv, port or 587, timeout=30)
            if sec=="STARTTLS": s.starttls()
        if user and pwd: s.login(user,pwd)
        s.send_message(msg); s.quit()
        if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] SMTP OK -> {to} (Anhänge: {len(attachments)})","INFO")
        return True
    except Exception as e:
        if ui_log: ui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] SMTP Fehler: {e}","ERROR")
        return False

# ----- Auto-Runner je Mandant -----
class AutoRunner:
    def __init__(self, app, mandant_name):
        self.app = app
        self.mandant = mandant_name
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        if not self.thread.is_alive():
            self.stop.clear()
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def terminate(self):
        self.stop.set()

    def run(self):
        while not self.stop.is_set():
            try:
                cfg = db_get_cfg(self.mandant)
                if not cfg or not cfg.get("auto_enabled"):
                    for _ in range(10):
                        if self.stop.is_set(): return
                        time.sleep(1)
                    continue
                # IDs holen (neu)
                ids = self.app._query_ids_only(cfg)
                known = db_list_known_ids(cfg["name"])
                to_get = [i for i in ids if i not in known]
                if to_get:
                    self.app._download_ids_for(cfg, to_get, auto=True)
                # Warten
                interval = int(cfg.get("interval_min") or 60)
                for _ in range(interval*60):
                    if self.stop.is_set(): return
                    time.sleep(1)
            except Exception as e:
                self.app.gui_log.write(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] AutoLoop[{self.mandant}] Fehler: {e}", "ERROR")
                for _ in range(10):
                    if self.stop.is_set(): return
                    time.sleep(1)

# ----- GUI App -----
class App:
    def __init__(self, root):
        self.root = root
        root.title(f"{APP_NAME} {APP_VER}")
        self.inbox = {}      # mandant -> {delivery_id: meta}
        self.last_raw = {}   # mandant -> bytes
        self.runners = {}    # mandant -> AutoRunner
        self.active_mandant = db_get_active() or "Default"
        self._sort_state = {"col":"Datum","reverse":True}  # Datum ↓
        self._filter_state = tk.StringVar(value="Alle")
        self._search_state = tk.StringVar(value="")
        self.preview_right = True

        self._build_ui()
        self._load_mandanten()
        self._build_mailbox_tree()
        self._select_mailbox_node(self.active_mandant)
        self._load_cfg_into_form(self.active_mandant)
        self._start_autos_for_enabled()

        # Initial befüllen
        self._thread(self.query_all)
        self._status("Bereit", ok=True)

    # ----- UI -----
    def _build_ui(self):
        # Menü
        menubar = tk.Menu(self.root)
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="Beenden", command=self.root.destroy)
        menubar.add_cascade(label="Datei", menu=m_file)

        m_mand = tk.Menu(menubar, tearoff=0)
        m_mand.add_command(label="Neuer Mandant …", command=self._new_mandant_dialog)
        m_mand.add_command(label="Mandant löschen …", command=self._delete_mandant)
        menubar.add_cascade(label="Mandanten", menu=m_mand)

        m_view = tk.Menu(menubar, tearoff=0)
        m_view.add_command(label="Vorschau rechts", command=lambda:self._set_layout(True))
        m_view.add_command(label="Vorschau unten", command=lambda:self._set_layout(False))
        menubar.add_cascade(label="Ansicht", menu=m_view)

        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="Disclaimer / Impressum", command=self._show_disclaimer)
        m_help.add_command(label="Über", command=lambda: messagebox.showinfo("Über", f"{APP_NAME} {APP_VER}\n© {APP_AUTHOR} 2025"))
        menubar.add_cascade(label="Hilfe", menu=m_help)
        self.root.config(menu=menubar)

        # Tabs
        self.nb = ttk.Notebook(self.root); self.nb.pack(fill="both", expand=True, padx=8, pady=8)
        tab_in = ttk.Frame(self.nb); self.nb.add(tab_in, text="Posteingang")
        tab_set= ttk.Frame(self.nb); self.nb.add(tab_set, text="Einstellungen")

        # Statusleiste
        self.status_frame = ttk.Frame(tab_in); self.status_frame.pack(fill="x")
        self.status_label = ttk.Label(self.status_frame, text=""); self.status_label.pack(side="left", padx=6)
        self.status_after_id = None

        # Toolbar-Zeile (Posteingang)
        tl = ttk.Frame(tab_in); tl.pack(fill="x", padx=0, pady=(6,0))
        ttk.Label(tl, text="Aktiver Mandant:").pack(side="left")
        self.cmb_active = ttk.Combobox(tl, state="readonly", width=30)
        self.cmb_active.pack(side="left", padx=(4,10))
        self.cmb_active.bind("<<ComboboxSelected>>", lambda e: self._switch_active_via_dropdown())
        ttk.Button(tl, text="Aktualisieren (Neu)", command=lambda:self._thread(self.query_new)).pack(side="left", padx=3)
        ttk.Button(tl, text="Alle abrufen", command=lambda:self._thread(self.get_all)).pack(side="left", padx=3)
        ttk.Button(tl, text="Auto Start/Stop", command=self._toggle_auto_active).pack(side="left", padx=10)
        ttk.Label(tl, text="Ansicht:").pack(side="left", padx=(16,2))
        self.cmb_view = ttk.Combobox(tl, state="readonly", values=["Alle","Neu","Bereits abgeholt"], width=18, textvariable=self._filter_state)
        self.cmb_view.pack(side="left", padx=(4,8))
        self.cmb_view.set("Alle")
        self.cmb_view.bind("<<ComboboxSelected>>", lambda e: self._refresh_inbox_ui())
        ttk.Label(tl, text="Suche:").pack(side="left")
        self.e_search = ttk.Entry(tl, textvariable=self._search_state, width=28); self.e_search.pack(side="left", padx=(4,6))
        ttk.Button(tl, text="Suchen", command=self._refresh_inbox_ui).pack(side="left")

        # Hauptbereich Posteingang: Panes
        outer = ttk.PanedWindow(tab_in, orient="horizontal"); outer.pack(fill="both", expand=True, padx=0, pady=8)

        # Links: Postfächer/Mandantenbaum
        self.left_frame = ttk.Frame(outer)
        outer.add(self.left_frame, weight=0)
        ttk.Label(self.left_frame, text="Postfächer", padding=(0,0,0,4)).pack(anchor="w")
        self.mbox = ttk.Treeview(self.left_frame, show="tree", height=18)
        self.mbox.pack(fill="both", expand=True)
        self.mbox.bind("<<TreeviewSelect>>", self._on_mailbox_select)

        # Mitte+Rechts: Paned (immer horizontal)
        center_right = ttk.PanedWindow(outer, orient="horizontal")
        outer.add(center_right, weight=1)

        # Mitte: Nachrichtenliste
        self.mid_frame = ttk.Frame(center_right); center_right.add(self.mid_frame, weight=1)
        stats = ttk.Frame(self.mid_frame); stats.pack(fill="x", pady=(0,4))
        ttk.Label(stats, text="Gefunden:").pack(side="left"); self.lbl_found= ttk.Label(stats, text="0"); self.lbl_found.pack(side="left", padx=(2,12))
        ttk.Label(stats, text="Abgeholt:").pack(side="left"); self.lbl_fetched=ttk.Label(stats, text="0"); self.lbl_fetched.pack(side="left", padx=(2,12))
        ttk.Label(stats, text="Zielordner:").pack(side="left"); self.lbl_dl = ttk.Label(stats, text=str(DEFAULT_DL_ROOT)); self.lbl_dl.pack(side="left", padx=(2,12))

        cols=("Status","Betreff","Absender","Datum","DeliveryID")
        self.tree=ttk.Treeview(self.mid_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c, command=lambda col=c: self._sort_by(col))
        self.tree.column("Status", width=90, anchor="center")
        self.tree.column("Betreff", width=320, anchor="w")
        self.tree.column("Absender", width=220, anchor="w")
        self.tree.column("Datum", width=170, anchor="w")
        self.tree.column("DeliveryID", width=320, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btnbar = ttk.Frame(self.mid_frame); btnbar.pack(fill="x", pady=(6,0))
        ttk.Button(btnbar, text="Ausgewählte abrufen", command=lambda:self._thread(self.get_selected)).pack(side="left", padx=3)
        ttk.Button(btnbar, text="Anhänge erneut per E-Mail senden", command=lambda:self._thread(self.forward_selected_attachments)).pack(side="left", padx=6)
        ttk.Button(btnbar, text="Ausgewählte schließen", command=lambda:self._thread(self.close_selected)).pack(side="left", padx=6)
        ttk.Button(btnbar, text="Ausgewählte löschen", command=lambda:self._thread(self.delete_selected)).pack(side="left", padx=6)

        # Rechts: Vorschau + Log (vertikal)
        self.preview_log = ttk.PanedWindow(center_right, orient="vertical")
        center_right.add(self.preview_log, weight=1)

        # Vorschau
        self.preview_frame = ttk.Frame(self.preview_log, padding=6); self.preview_log.add(self.preview_frame, weight=3)
        self.lbl_meta = ttk.Label(self.preview_frame, text="— Keine Auswahl —", anchor="w", justify="left")
        self.lbl_meta.pack(fill="x")
        ttk.Label(self.preview_frame, text="Mailbody (Vorschau):").pack(anchor="w", pady=(6,0))
        self.txt_body = scrolledtext.ScrolledText(self.preview_frame, height=12, wrap="word")
        self.txt_body.pack(fill="both", expand=True)
        ttk.Label(self.preview_frame, text="Anhänge:").pack(anchor="w", pady=(6,0))
        self.attach_list = tk.Listbox(self.preview_frame, height=6); self.attach_list.pack(fill="x")
        pbtns = ttk.Frame(self.preview_frame); pbtns.pack(fill="x", pady=(6,0))
        ttk.Button(pbtns, text="Anhänge herunterladen", command=lambda:self._thread(self.download_selected_attachments)).pack(side="left", padx=3)
        ttk.Button(pbtns, text="Anhänge per E-Mail weiterleiten", command=lambda:self._thread(self.forward_selected_attachments)).pack(side="left", padx=3)
        ttk.Button(pbtns, text="Rohantwort anzeigen", command=self._show_raw).pack(side="right", padx=3)

        # Log (immer sichtbar, H/V scrollbar)
        self.log_frame = ttk.Frame(self.preview_log, padding=(6,0,6,6)); self.preview_log.add(self.log_frame, weight=1)
        self.txt_log = scrolledtext.ScrolledText(self.log_frame, wrap="none", height=10)
        self.txt_log.pack(fill="both", expand=True)
        # Logger initialisieren
        self.gui_log = GuiLogger(self.txt_log, cap_lines=200)

        # Einstellungen-Tab (vollständig)
        fr = ttk.Frame(tab_set, padding=8); fr.pack(fill="both", expand=True)
        ttk.Label(fr, text="Mandant:").grid(row=0,column=0,sticky="w")
        self.cmb_mand = ttk.Combobox(fr, state="readonly", values=db_list_mandanten(), width=32)
        self.cmb_mand.grid(row=0,column=1,sticky="w"); self.cmb_mand.bind("<<ComboboxSelected>>", self._switch_mandant_event)
        ttk.Button(fr, text="Neu …", command=self._new_mandant_dialog).grid(row=0,column=2,padx=3)
        ttk.Button(fr, text="Löschen", command=self._delete_mandant).grid(row=0,column=3,padx=3)

        ttk.Label(fr, text=".p12 Zertifikat (optional – Import in DB):").grid(row=1,column=0,sticky="w", pady=(8,0))
        self.e_p12 = ttk.Entry(fr, width=70); self.e_p12.grid(row=1,column=1,sticky="w", pady=(8,0))
        ttk.Button(fr, text="Durchsuchen", command=self._choose_p12).grid(row=1,column=2,padx=3, pady=(8,0))
        ttk.Label(fr, text="Zert.-Passwort:").grid(row=2,column=0,sticky="w")
        self.e_p12_pw = ttk.Entry(fr, width=30, show="*"); self.e_p12_pw.grid(row=2,column=1,sticky="w")
        ttk.Button(fr, text="👁", width=3, command=lambda:self._toggle_show(self.e_p12_pw)).grid(row=2,column=2,sticky="w")

        ttk.Label(fr, text="Endpoint:").grid(row=3,column=0,sticky="w")
        self.e_endpoint = ttk.Entry(fr, width=70); self.e_endpoint.grid(row=3,column=1,sticky="w"); self.e_endpoint.insert(0, ENDPOINT_DEFAULT)

        ttk.Label(fr, text="Zielordner:").grid(row=4,column=0,sticky="w")
        self.e_dl = ttk.Entry(fr, width=70); self.e_dl.grid(row=4,column=1,sticky="w"); self.e_dl.insert(0, str((DEFAULT_DL_ROOT / self.active_mandant).resolve()))
        ttk.Button(fr, text="Ordner wählen", command=self._choose_dl).grid(row=4,column=2,padx=3)

        ttk.Label(fr, text="Intervall (Min):").grid(row=5,column=0,sticky="w")
        self.e_interval = ttk.Entry(fr, width=8); self.e_interval.grid(row=5,column=1,sticky="w"); self.e_interval.insert(0,"60")

        ttk.Label(fr, text="SMTP Server:").grid(row=6,column=0,sticky="w", pady=(8,0))
        self.e_smtp_srv = ttk.Entry(fr, width=40); self.e_smtp_srv.grid(row=6,column=1,sticky="w", pady=(8,0))
        ttk.Label(fr, text="Port:").grid(row=6,column=2,sticky="w"); self.e_smtp_port=ttk.Entry(fr,width=8); self.e_smtp_port.grid(row=6,column=3,sticky="w")
        ttk.Label(fr, text="SMTP User:").grid(row=7,column=0,sticky="w"); self.e_smtp_user=ttk.Entry(fr,width=40); self.e_smtp_user.grid(row=7,column=1,sticky="w")
        ttk.Label(fr, text="SMTP Passwort:").grid(row=7,column=2,sticky="w"); self.e_smtp_pass=ttk.Entry(fr,width=20, show="*"); self.e_smtp_pass.grid(row=7,column=3,sticky="w")
        ttk.Button(fr, text="👁", width=3, command=lambda:self._toggle_show(self.e_smtp_pass)).grid(row=7,column=4,sticky="w")
        ttk.Label(fr, text="Empfänger (To):").grid(row=8,column=0,sticky="w"); self.e_smtp_to=ttk.Entry(fr,width=40); self.e_smtp_to.grid(row=8,column=1,sticky="w")
        ttk.Label(fr, text="Security:").grid(row=8,column=2,sticky="w"); self.cmb_sec=ttk.Combobox(fr, values=["PLAIN","STARTTLS","SSL"], width=12, state="readonly"); self.cmb_sec.set("STARTTLS"); self.cmb_sec.grid(row=8,column=3,sticky="w")

        self.auto_enabled_var = tk.IntVar()
        self.auto_forward_var = tk.IntVar()
        ttk.Checkbutton(fr, text="Autoabholung aktiv", variable=self.auto_enabled_var).grid(row=9,column=0,sticky="w", pady=(8,0))
        ttk.Checkbutton(fr, text="Neue automatisch per E-Mail weiterleiten", variable=self.auto_forward_var).grid(row=9,column=1,sticky="w", pady=(8,0))

        btns = ttk.Frame(fr); btns.grid(row=10,column=0,columnspan=5, pady=(10,0))
        ttk.Button(btns, text="Konfiguration speichern", command=self._save_cfg).pack(side="left", padx=6)
        ttk.Button(btns, text="SMTP Test", command=lambda:self._thread(self._smtp_test)).pack(side="left", padx=6)
        ttk.Button(btns, text="Zertifikat prüfen", command=lambda:self._thread(self._preview_cert)).pack(side="left", padx=6)

        # GUI-Logger-Funktion (Convenience)
        self._gui_log = lambda line, lvl="INFO": self.gui_log.write(line, lvl)

    # ----- UI Helpers -----
    def _status(self, text, ok=True, timeout_ms=2500):
        self.status_label.config(text=(f"✔ {text}" if ok else f"✖ {text}"), foreground=("green" if ok else "red"))
        if self.status_after_id: self.root.after_cancel(self.status_after_id)
        self.status_after_id = self.root.after(timeout_ms, lambda: self.status_label.config(text="", foreground="black"))

    def _thread(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def _toggle_show(self, entry:tk.Entry):
        entry.config(show="" if entry.cget("show")=="*" else "*")

    # ----- Mandanten-Dialog (Neu: leer ODER kopieren) -----
    def _new_mandant_dialog(self):
        win = tk.Toplevel(self.root); win.title("Neuer Mandant")
        win.grab_set()
        ttk.Label(win, text="Name des neuen Mandanten:").grid(row=0, column=0, sticky="w", padx=8, pady=(8,2))
        e_name = ttk.Entry(win, width=32); e_name.grid(row=0, column=1, sticky="w", padx=8, pady=(8,2))

        mode = tk.StringVar(value="leer")
        ttk.Radiobutton(win, text="Manuell (leer)", variable=mode, value="leer").grid(row=1, column=0, sticky="w", padx=8)
        ttk.Radiobutton(win, text="Kopieren von", variable=mode, value="copy").grid(row=2, column=0, sticky="w", padx=8)
        cmb_src = ttk.Combobox(win, state="readonly", values=db_list_mandanten(), width=28)
        cmb_src.grid(row=2, column=1, sticky="w", padx=8)

        btns = ttk.Frame(win); btns.grid(row=3, column=0, columnspan=2, pady=10)
        def ok():
            name = (e_name.get() or "").strip()
            if not name:
                messagebox.showerror("Fehler", "Name fehlt."); return
            if name in db_list_mandanten():
                messagebox.showerror("Fehler","Name existiert bereits."); return
            if mode.get()=="copy":
                src = cmb_src.get().strip()
                if not src:
                    messagebox.showerror("Fehler","Quelle wählen."); return
                src_cfg = db_get_cfg(src) or {}
                cfg = {
                    "name": name,
                    "p12_path": src_cfg.get("p12_path",""),
                    "p12_blob": src_cfg.get("p12_blob", None),
                    "pw": src_cfg.get("pw",""),
                    "endpoint": src_cfg.get("endpoint", ENDPOINT_DEFAULT),
                    "dl": str((DEFAULT_DL_ROOT / name).resolve()),
                    "smtp_server": src_cfg.get("smtp_server",""),
                    "smtp_port": src_cfg.get("smtp_port",587),
                    "smtp_user": src_cfg.get("smtp_user",""),
                    "smtp_pass": src_cfg.get("smtp_pass",""),
                    "smtp_sec": src_cfg.get("smtp_sec","STARTTLS"),
                    "smtp_to": src_cfg.get("smtp_to",""),
                    "auto_enabled": False,
                    "auto_forward": src_cfg.get("auto_forward", False),
                    "interval_min": src_cfg.get("interval_min",60),
                }
            else:
                cfg = {
                    "name": name, "p12_path":"", "p12_blob":None, "pw":"",
                    "endpoint": ENDPOINT_DEFAULT, "dl": str((DEFAULT_DL_ROOT / name).resolve()),
                    "smtp_server":"", "smtp_port":587, "smtp_user":"", "smtp_pass":"",
                    "smtp_sec":"STARTTLS", "smtp_to":"",
                    "auto_enabled":False, "auto_forward":False, "interval_min":60
                }
            Path(cfg["dl"]).mkdir(parents=True, exist_ok=True)
            db_upsert_cfg(cfg)
            db_set_active(name); self.active_mandant=name
            self._load_mandanten(); self._build_mailbox_tree(); self._select_mailbox_node(name)
            self._load_cfg_into_form(name)
            self._refresh_inbox_ui()
            win.destroy()
        ttk.Button(btns, text="Anlegen", command=ok).pack(side="left", padx=6)
        ttk.Button(btns, text="Abbrechen", command=win.destroy).pack(side="left", padx=6)

    def _delete_mandant(self):
        name = self.active_mandant
        if not name: return
        if messagebox.askyesno("Löschen", f"Mandant '{name}' wirklich löschen?"):
            r = self.runners.get(name)
            if r: r.terminate()
            db_delete_mandant(name)
            names = db_list_mandanten()
            if names:
                db_set_active(names[0]); self.active_mandant = names[0]
            else:
                self.active_mandant = "Default"
            self._load_mandanten(); self._build_mailbox_tree(); self._select_mailbox_node(self.active_mandant)
            self._load_cfg_into_form(self.active_mandant)
            self._refresh_inbox_ui()
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Mandant '{name}' gelöscht.")

    def _load_mandanten(self):
        mandanten = db_list_mandanten()
        # Posteingang-Toolbar
        self.cmb_active["values"] = mandanten
        if self.active_mandant in mandanten:
            self.cmb_active.set(self.active_mandant)
        # Einstellungen-Tab
        self.cmb_mand["values"] = mandanten
        if self.active_mandant in mandanten:
            self.cmb_mand.set(self.active_mandant)

    # ----- Mailbox (Mandantenbaum) -----
    def _build_mailbox_tree(self):
        self.mbox.delete(*self.mbox.get_children())
        for name in db_list_mandanten():
            nid = self.mbox.insert("", "end", iid=f"mand:{name}", text=name, open=True)
            self.mbox.insert(nid, "end", iid=f"inbox:{name}", text="Posteingang", open=True)

    def _on_mailbox_select(self, _evt):
        sel = self.mbox.selection()
        if not sel: return
        sid = sel[0]
        if sid.startswith("mand:") or sid.startswith("inbox:"):
            name = sid.split(":",1)[1]
            if name != self.active_mandant:
                db_set_active(name)
                self.active_mandant = name
                self.cmb_active.set(name); self.cmb_mand.set(name)
                self._load_cfg_into_form(name)
                self._refresh_inbox_ui()

    def _select_mailbox_node(self, name):
        try:
            self.mbox.selection_set(f"inbox:{name}")
            self.mbox.see(f"inbox:{name}")
        except: pass

    def _switch_active_via_dropdown(self):
        name = self.cmb_active.get().strip()
        if not name: return
        db_set_active(name)
        self.active_mandant = name
        self.cmb_mand.set(name)
        self._select_mailbox_node(name)
        self._load_cfg_into_form(name)
        self._refresh_inbox_ui()
        self._update_auto_status()

    # ----- Layout -----
    def _set_layout(self, preview_right:bool):
        # Kein orient-Wechsel zur Laufzeit (Tcl read-only). Wir lassen Vorschau+Log vertikal gestapelt rechts.
        self.preview_right = preview_right  # nur für Status
        self._status("Ansicht geändert", ok=True)

    # ----- Zertifikat (Preview im Einstellungs-Tab) -----
    def _preview_cert(self):
        cfg = db_get_cfg(self.active_mandant)
        if not cfg: return
        try:
            cert_pem, key_pem, cert = export_p12_to_pem(cfg, self.gui_log.write)
            subj = ""
            try: subj = cert.subject.rfc4514_string()
            except: subj = str(cert.subject)
            exp = cert.not_valid_after
            days = (exp - datetime.now(timezone.utc)).days
            self.lbl_cert_subj.config(text=f"Subject: {subj}")
            self.lbl_cert_exp.config(text=f"Ablauf: {exp.isoformat()} ({days} Tage)")
            self._status("Zertifikat geprüft", ok=True)
        except Exception as e:
            self._status(f"Zertifikat-Fehler: {e}", ok=False)

    # ----- Einstellungen laden/speichern -----
    def _switch_mandant_event(self, _evt=None):
        sel = self.cmb_mand.get().strip()
        if sel:
            db_set_active(sel)
            self.active_mandant = sel
            self.cmb_active.set(sel)
            self._load_cfg_into_form(sel)
            self._refresh_inbox_ui()
            self._update_auto_status()

    def _choose_p12(self):
        p = filedialog.askopenfilename(filetypes=[("PKCS12","*.p12")], title=".p12 wählen")
        if p:
            self.e_p12.delete(0,"end"); self.e_p12.insert(0,p)

    def _choose_dl(self):
        p = filedialog.askdirectory(title="Zielordner wählen")
        if p:
            self.e_dl.delete(0,"end"); self.e_dl.insert(0,p)
            self.lbl_dl.config(text=p)

    def _current_cfg_from_form(self):
        p12_blob = None
        p = self.e_p12.get().strip()
        if p and Path(p).is_file():
            try:
                p12_blob = Path(p).read_bytes()
            except Exception as e:
                self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [WARN] .p12 konnte nicht gelesen werden: {e}","WARN")
        return {
            "name": self.active_mandant,
            "p12_path": p,
            "p12_blob": p12_blob,
            "pw":  self.e_p12_pw.get().strip(),
            "endpoint": self.e_endpoint.get().strip() or ENDPOINT_DEFAULT,
            "dl": self.e_dl.get().strip() or str((DEFAULT_DL_ROOT / self.active_mandant).resolve()),
            "smtp_server": self.e_smtp_srv.get().strip(),
            "smtp_port": int(self.e_smtp_port.get().strip() or 0),
            "smtp_user": self.e_smtp_user.get().strip(),
            "smtp_pass": self.e_smtp_pass.get().strip(),
            "smtp_sec": self.cmb_sec.get().strip(),
            "smtp_to": self.e_smtp_to.get().strip(),
            "auto_enabled": bool(self.auto_enabled_var.get()),
            "auto_forward": bool(self.auto_forward_var.get()),
            "interval_min": int(self.e_interval.get().strip() or 60)
        }

    def _load_cfg_into_form(self, name):
        cfg = db_get_cfg(name)
        if not cfg: return
        self.e_p12.delete(0,"end"); self.e_p12.insert(0, cfg.get("p12_path",""))
        self.e_p12_pw.delete(0,"end"); self.e_p12_pw.insert(0, cfg.get("pw",""))
        self.e_endpoint.delete(0,"end"); self.e_endpoint.insert(0, cfg.get("endpoint",ENDPOINT_DEFAULT))
        self.e_dl.delete(0,"end"); self.e_dl.insert(0, cfg.get("dl",str((DEFAULT_DL_ROOT / name).resolve())))
        self.lbl_dl.config(text=cfg.get("dl",str((DEFAULT_DL_ROOT / name).resolve())))
        self.e_interval.delete(0,"end"); self.e_interval.insert(0, str(cfg.get("interval_min",60)))
        self.e_smtp_srv.delete(0,"end"); self.e_smtp_srv.insert(0, cfg.get("smtp_server",""))
        self.e_smtp_port.delete(0,"end"); self.e_smtp_port.insert(0, str(cfg.get("smtp_port","")))
        self.e_smtp_user.delete(0,"end"); self.e_smtp_user.insert(0, cfg.get("smtp_user",""))
        self.e_smtp_pass.delete(0,"end"); self.e_smtp_pass.insert(0, cfg.get("smtp_pass",""))
        self.e_smtp_to.delete(0,"end"); self.e_smtp_to.insert(0, cfg.get("smtp_to",""))
        self.cmb_sec.set(cfg.get("smtp_sec","STARTTLS"))
        self.auto_enabled_var.set(int(cfg.get("auto_enabled",0)))
        self.auto_forward_var.set(int(cfg.get("auto_forward",0)))

    def _save_cfg(self):
        cfg = self._current_cfg_from_form()
        Path(cfg["dl"]).mkdir(parents=True, exist_ok=True)
        db_upsert_cfg(cfg)
        db_set_active(cfg["name"])
        self.active_mandant = cfg["name"]
        self._load_mandanten()
        self._build_mailbox_tree()
        self._select_mailbox_node(cfg["name"])
        self._update_auto_status()
        if cfg["auto_enabled"]:
            self._start_runner(cfg["name"])
        else:
            self._stop_runner(cfg["name"])
        self._status("Konfiguration gespeichert", ok=True)

    # ----- Abfragen / Inbox -----
    def _ensure_inbox(self, name):
        if name not in self.inbox: self.inbox[name]={}

    def _query_ids_only(self, cfg):
        try:
            cert_pem, key_pem, _ = export_p12_to_pem(cfg, self.gui_log.write)
        except Exception as e:
            self._status(str(e), ok=False); return []
        body = soap_query(new_only=True, limit=100)
        try:
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [{cfg['name']}] QueryDeliveries (Neu, IDs) …","INFO")
            r = soap_post(cfg["endpoint"], (cert_pem,key_pem), body, self.gui_log.write)
            self.last_raw[cfg["name"]] = r.content
            if r.status_code != 200:
                self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] HTTP {r.status_code} {r.text[:400]}","ERROR")
                return []
            ids, _ = parse_query_ids(r.content)
            return ids
        except Exception as e:
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [{cfg['name']}] Query Fehler: {e}\n","ERROR")
            return []

    def query_new(self):
        cfg = db_get_cfg(self.active_mandant)
        if not cfg:
            self._status("Kein aktiver Mandant", ok=False); return
        self._query_for(cfg, new_only=True, refresh_ui=True)

    def query_all(self):
        cfg = db_get_cfg(self.active_mandant)
        if not cfg:
            self._status("Kein aktiver Mandant", ok=False); return
        self._query_for(cfg, new_only=False, refresh_ui=True)

    def _query_for(self, cfg, new_only=True, refresh_ui=False):
        try:
            cert_pem, key_pem, _ = export_p12_to_pem(cfg, self.gui_log.write)
        except Exception as e:
            self._status(f"Zertifikat: {e}", ok=False); return
        body = soap_query(new_only=new_only, limit=100)
        try:
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [{cfg['name']}] QueryDeliveries ({'Neu' if new_only else 'Alle'}) …","INFO")
            r = soap_post(cfg["endpoint"], (cert_pem,key_pem), body, self.gui_log.write)
            self.last_raw[cfg["name"]] = r.content
            if r.status_code != 200:
                self._status(f"HTTP {r.status_code}", ok=False)
                return
            ids, hit = parse_query_ids(r.content)

            # Fallback: Wenn Neu keine IDs -> Alle probieren
            if new_only and not ids and refresh_ui:
                self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Keine neuen Einträge – hole alle …","INFO")
                body_all = soap_query(new_only=False, limit=100)
                r_all = soap_post(cfg["endpoint"], (cert_pem,key_pem), body_all, self.gui_log.write)
                self.last_raw[cfg["name"]] = r_all.content
                if r_all.status_code == 200:
                    ids, hit = parse_query_ids(r_all.content)

            # Inbox nur ersetzen, wenn IDs vorhanden
            name = cfg["name"]
            self._ensure_inbox(name)
            new_box = {}
            for did in ids:
                meta = self._get_meta(cfg, did, fetch_mailbody=True)
                new_box[did] = meta
            if ids:
                self.inbox[name] = new_box

            if refresh_ui and name == self.active_mandant:
                self._refresh_inbox_ui()
                shown = len(self.inbox.get(name, {})) if not ids else len(new_box)
                try:
                    self.lbl_found.config(text=str(shown))
                except Exception:
                    pass

            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [{cfg['name']}] Treffer: {hit}","INFO")
            if refresh_ui:
                self._status(f"{hit} Einträge gefunden", ok=True)
        except Exception as e:
            self._status(f"Abfrage-Fehler: {e}", ok=False)
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [{cfg['name']}] Query Fehler: {e}\n","ERROR")

    def _get_meta(self, cfg, delivery_id, fetch_mailbody=False):
        try:
            cert_pem, key_pem, _ = export_p12_to_pem(cfg, self.gui_log.write)
            r = soap_post(cfg["endpoint"], (cert_pem,key_pem), soap_get(delivery_id), self.gui_log.write)
            if r.status_code != 200:
                self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [{cfg['name']}] GetDelivery {delivery_id}: HTTP {r.status_code}","ERROR")
                return {"subject":"", "timestamp":"", "sender":"", "receiver":"", "attachments":[], "mailbody_text":"", "raw":r.content}
            meta = parse_delivery_meta(r.content)

            if fetch_mailbody:
                # Mailbody gezielt holen (falls als Attachment "mailbody" vorhanden)
                cleaned_atts = []
                for a in meta.get("attachments",[]):
                    # attachments sind bereits ohne 'mailbody' (parse filtert)
                    cleaned_atts.append(a)
                # Aber der Text muss separat geholt werden: Suche Attachment-IDs in Original-XML
                try:
                    root = ET.fromstring(r.content)
                    for att in root.findall(".//aa:Attachment", NS):
                        fn = att.find("aa:FileName", NS)
                        aid = att.find("aa:AttachmentID", NS)
                        if fn is not None and aid is not None and (fn.text or "").strip().lower()=="mailbody":
                            dlpath = Path(cfg["dl"]).resolve(); dlpath.mkdir(parents=True, exist_ok=True)
                            p = rest_download_attachment(cfg["endpoint"], delivery_id, aid.text, fn.text, (cert_pem,key_pem), dlpath, self.gui_log.write)
                            try:
                                raw = Path(p).read_bytes()
                                try: meta["mailbody_text"] = raw.decode("utf-8")
                                except: meta["mailbody_text"] = raw.decode("latin-1","replace")
                            finally:
                                try: os.unlink(p)
                                except: pass
                            break
                except Exception as e:
                    self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [WARN] Mailbody-Vorschau fehlgeschlagen {delivery_id}: {e}","WARN")

                meta["attachments"] = cleaned_atts
            return meta
        except Exception as e:
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [{cfg['name']}] Meta Fehler {delivery_id}: {e}","ERROR")
            return {"subject":"", "timestamp":"", "sender":"", "receiver":"", "attachments":[], "mailbody_text":"", "raw":b""}

    def _refresh_inbox_ui(self):
        name = self.active_mandant
        self._ensure_inbox(name)
        mode = self._filter_state.get()
        q = self._search_state.get().lower().strip()
        self.tree.delete(*self.tree.get_children())
        fetched_ids = {did for did in self.inbox.get(name, {}) if db_is_fetched(name, did)}
        rows=[]
        for did, meta in self.inbox[name].items():
            subj = meta.get("subject",""); sender = meta.get("sender",""); ts= meta.get("timestamp","")
            status = "✔" if did in fetched_ids else "Neu"
            if mode=="Neu" and status!="Neu": continue
            if mode=="Bereits abgeholt" and status!="✔": continue
            if q and q not in f"{subj} {sender} {ts} {did}".lower(): continue
            rows.append((status, subj, sender, ts, did))
        col = self._sort_state["col"]; reverse = self._sort_state["reverse"]
        idx = {"Status":0,"Betreff":1,"Absender":2,"Datum":3,"DeliveryID":4}[col]
        def keyf(t):
            v=t[idx]
            if idx==3:
                try: return datetime.fromisoformat(v.replace("Z","+00:00"))
                except: return datetime.max if reverse else datetime.min
            return v or ""
        rows.sort(key=keyf, reverse=reverse)
        shown = 0
        for status,subj,sender,ts,did in rows:
            iid = self.tree.insert("", "end", values=(status,subj,sender,ts,did))
            shown += 1
            if status=="✔": self.tree.item(iid, tags=("done",))
            else: self.tree.item(iid, tags=("new",))
        self.tree.tag_configure("done", background="#eef6ee")
        self.tree.tag_configure("new", font=("TkDefaultFont", 9, "bold"))
        for c in ("Status","Betreff","Absender","Datum","DeliveryID"):
            txt = c + (" ↓" if (c==col and reverse) else (" ↑" if (c==col and not reverse) else ""))
            self.tree.heading(c, text=txt, command=lambda cc=c: self._sort_by(cc))
        cfg = db_get_cfg(name)
        self.lbl_dl.config(text=cfg.get("dl",str((DEFAULT_DL_ROOT / name).resolve())) if cfg else str(DEFAULT_DL_ROOT))
        try: self.lbl_found.config(text=str(shown))
        except: pass
        self._update_auto_status()

    def _sort_by(self, col):
        if self._sort_state["col"]==col:
            self._sort_state["reverse"] = not self._sort_state["reverse"]
        else:
            self._sort_state = {"col":col, "reverse": (col=="Datum")}
        self._refresh_inbox_ui()

    def _on_select(self, _evt):
        sel = self.tree.selection()
        if not sel:
            self.lbl_meta.config(text="— Keine Auswahl —"); self.txt_body.delete("1.0","end"); self.attach_list.delete(0,"end"); return
        did = self.tree.item(sel[0])["values"][4]
        meta = self.inbox.get(self.active_mandant,{}).get(did,{})
        self._show_preview(did, meta)

    def _show_preview(self, did, meta):
        txt = f"Betreff: {meta.get('subject','')}   |   Absender: {meta.get('sender','')}   |   Datum: {meta.get('timestamp','')}   |   DeliveryID: {did}"
        self.lbl_meta.config(text=txt)
        self.txt_body.delete("1.0","end")
        self.txt_body.insert("1.0", meta.get("mailbody_text",""))
        self.attach_list.delete(0,"end")
        for a in meta.get("attachments",[]):
            self.attach_list.insert("end", f"{a.get('file','(ohne Name)')}  [{a.get('id','')}]")

    # ----- Download / Forward -----
    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            self._status("Bitte Nachricht(en) markieren", ok=False); return
        ids = [self.tree.item(i)["values"][4] for i in sel]
        cfg = db_get_cfg(self.active_mandant)
        self._download_ids_for(cfg, ids, auto=False)

    def get_all(self):
        cfg = db_get_cfg(self.active_mandant)
        ids = list(self.inbox.get(self.active_mandant,{}).keys())
        if not ids:
            self._status("Keine Einträge", ok=False); return
        self._download_ids_for(cfg, ids, auto=False)

    def _download_ids_for(self, cfg, ids, auto:bool):
        fetched=0
        for did in ids:
            try:
                already = db_is_fetched(cfg["name"], did)
                paths, body_text, meta = self._download_single(cfg, did)
                if not already:
                    db_mark_fetched(cfg["name"], did, meta)
                fetched += 1 if not already else 0
                if cfg.get("auto_forward") and (not db_is_forwarded(cfg["name"], did)):
                    subj = f"USP Abholung - {self.inbox[cfg['name']][did].get('sender', '')} - {self.inbox[cfg['name']][did].get('subject', '')}"
                    ok = self._forward_files(cfg, [p for p in paths if Path(p).is_file()], subj, body_text or "")
                    if ok: db_mark_forwarded(cfg["name"], did)
            except Exception as e:
                self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] [{cfg['name']}] Abholung {did} Fehler: {e}","ERROR")
        if cfg["name"]==self.active_mandant:
            self.lbl_fetched.config(text=str(int(self.lbl_fetched.cget("text"))+fetched))
            self._refresh_inbox_ui()
        if fetched and not auto:
            self._status(f"{fetched} Nachricht(en) abgeholt", ok=True)

    def _download_single(self, cfg, delivery_id):
        cert_pem, key_pem, _ = export_p12_to_pem(cfg, self.gui_log.write)
        r = soap_post(cfg["endpoint"], (cert_pem,key_pem), soap_get(delivery_id), self.gui_log.write)
        if r.status_code != 200:
            raise RuntimeError(f"GetDelivery HTTP {r.status_code}: {r.text[:400]}")
        meta = parse_delivery_meta(r.content)
        dlpath = Path(cfg["dl"]).resolve(); dlpath.mkdir(parents=True, exist_ok=True)
        saved = []
        # Delivery-XML
        meta_path = dlpath / f"delivery_{delivery_id}.xml"
        with open(meta_path,"wb") as f: f.write(r.content)
        saved.append(str(meta_path))
        # Mailbody + Attachments
        mailbody_text = ""
        # suche Mailbody in Original-XML und lade ihn
        try:
            root = ET.fromstring(r.content)
            for att in root.findall(".//aa:Attachment", NS):
                fn = att.find("aa:FileName", NS)
                aid = att.find("aa:AttachmentID", NS)
                if fn is not None and aid is not None and (fn.text or "").strip().lower()=="mailbody":
                    p = rest_download_attachment(cfg["endpoint"], delivery_id, aid.text, fn.text, (cert_pem,key_pem), dlpath, self.gui_log.write)
                    try:
                        raw = Path(p).read_bytes()
                        try: mailbody_text = raw.decode("utf-8")
                        except: mailbody_text = raw.decode("latin-1","replace")
                    finally:
                        try: os.unlink(p)
                        except: pass
                    break
        except Exception as e:
            self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [WARN] Mailbody lesen fehlgeschlagen: {e}","WARN")
        # echte Attachments laden
        for a in meta.get("attachments",[]):
            fname = (a.get("file") or "").strip()
            attid = a.get("id")
            if not attid: continue
            p = rest_download_attachment(cfg["endpoint"], delivery_id, attid, fname, (cert_pem,key_pem), dlpath, self.gui_log.write)
            if p: saved.append(p)
        # Vorschau aktualisieren
        self.inbox.setdefault(cfg["name"],{}).setdefault(delivery_id, meta)
        self.inbox[cfg["name"]][delivery_id]["mailbody_text"] = mailbody_text
        return saved, mailbody_text, meta

    def forward_selected_attachments(self):
        sel = self.tree.selection()
        if not sel:
            self._status("Bitte Nachricht auswählen", ok=False); return
        did = self.tree.item(sel[0])["values"][4]
        cfg = db_get_cfg(self.active_mandant)
        dl = Path(cfg["dl"]).resolve()
        files = [str(p) for p in dl.glob(f"*{did}*") if p.is_file() and p.name.lower()!="mailbody"]
        bodytext = self.inbox.get(cfg["name"],{}).get(did,{}).get("mailbody_text","")
        subj = f"USP Abholung – {self.inbox.get(cfg['name'],{}).get(did,{}).get('subject','')}"
        ok = self._forward_files(cfg, files, subj, bodytext)
        if ok: db_mark_forwarded(cfg["name"], did)
        self._status("E-Mail gesendet" if ok else "E-Mail fehlgeschlagen (Log)", ok=ok)

    def download_selected_attachments(self):
        sel = self.tree.selection()
        if not sel:
            self._status("Bitte Nachricht auswählen", ok=False); return
        did = self.tree.item(sel[0])["values"][4]
        cfg = db_get_cfg(self.active_mandant)
        self._download_ids_for(cfg, [did], auto=False)

    def _forward_files(self, cfg, files, subject, body):
        return smtp_send({
            "smtp_server": cfg["smtp_server"], "smtp_port": cfg["smtp_port"],
            "smtp_user": cfg["smtp_user"],     "smtp_pass": cfg["smtp_pass"],
            "smtp_to": cfg["smtp_to"],         "smtp_sec": cfg["smtp_sec"]
        }, files, subject, body, self.gui_log.write)

    # ----- Close/Delete -----
    def close_selected(self):
        self._apply_to_selected(lambda did: soap_close(did), "CloseDelivery")

    def delete_selected(self):
        self._apply_to_selected(lambda did: soap_delete(did), "DeleteDelivery")

    def _apply_to_selected(self, body_fn, label):
        sel = self.tree.selection()
        if not sel:
            self._status("Bitte Nachricht(en) markieren", ok=False); return
        ids = [self.tree.item(i)["values"][4] for i in sel]
        cfg = db_get_cfg(self.active_mandant)
        ok_all=True
        for did in ids:
            try:
                cert_pem, key_pem, _ = export_p12_to_pem(cfg, self.gui_log.write)
                r = soap_post(cfg["endpoint"], (cert_pem,key_pem), body_fn(did), self.gui_log.write)
                if r.status_code==200:
                    self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [INFO] {label} OK: {r.text[:200]}","INFO")
                else:
                    ok_all=False
                    self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] {label} HTTP {r.status_code}: {r.text[:400]}","ERROR")
            except Exception as e:
                ok_all=False
                self._gui_log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] {label} Fehler: {e}","ERROR")
        self._status(f"{label}: erledigt", ok=ok_all)

    # ----- Rohantwort -----
    def _show_raw(self):
        raw = self.last_raw.get(self.active_mandant)
        if not raw:
            self._status("Keine Rohantwort verfügbar", ok=False); return
        win = tk.Toplevel(self.root); win.title("Letzte Rohantwort")
        txt = scrolledtext.ScrolledText(win, width=120, height=40, wrap="none"); txt.pack(fill="both", expand=True)
        txt.insert("1.0", raw.decode("utf-8", errors="replace"))

    # ----- Auto Runners / Status -----
    def _start_autos_for_enabled(self):
        for name in db_list_mandanten():
            cfg = db_get_cfg(name)
            if cfg and cfg.get("auto_enabled"):
                if name not in self.runners:
                    self.runners[name] = AutoRunner(self, name)
                self.runners[name].start()
        self._update_auto_status()

    def _start_runner(self, name):
        if name not in self.runners:
            self.runners[name] = AutoRunner(self, name)
        self.runners[name].start()

    def _stop_runner(self, name):
        r = self.runners.get(name)
        if r: r.terminate()

    def _toggle_auto_active(self):
        name = self.active_mandant
        cfg = db_get_cfg(name)
        if not cfg: return
        cfg["auto_enabled"] = 0 if cfg.get("auto_enabled") else 1
        db_upsert_cfg(cfg)
        if cfg["auto_enabled"]:
            self._start_runner(name); self._status("Autoabholung aktiviert", ok=True)
        else:
            self._stop_runner(name);  self._status("Autoabholung deaktiviert", ok=True)
        self._update_auto_status()

    def _update_auto_status(self):
        cfg = db_get_cfg(self.active_mandant)
        running = (cfg and cfg.get("auto_enabled"))
        self.status_label.config(text=("Auto aktiv ✅" if running else "Auto inaktiv ⛔"))

    # ----- SMTP Test -----
    def _smtp_test(self):
        cfg = db_get_cfg(self.active_mandant)
        ok = smtp_send({
            "smtp_server": cfg["smtp_server"], "smtp_port": cfg["smtp_port"],
            "smtp_user": cfg["smtp_user"],     "smtp_pass": cfg["smtp_pass"],
            "smtp_to": cfg["smtp_to"],         "smtp_sec": cfg["smtp_sec"]
        }, [], "USP Testmail", "Testnachricht vom USP Autoabholer", self.gui_log.write)
        self._status("E-Mail gesendet" if ok else "E-Mail-Fehler (siehe Log)", ok=ok)

    # ----- Disclaimer -----
    def _show_disclaimer(self):
        text = (
            f"{APP_NAME} {APP_VER} — © {APP_AUTHOR}\n\n"
            "Haftungsausschluss (Disclaimer):\n"
            "Dieses Programm ist ein Hilfswerkzeug zur manuellen und automatisierten Abholung von Nachrichten aus dem USP-Portal "
            "('Mein Postkorb'). Es wird ohne Gewähr bereitgestellt. Thomas Kirchler übernimmt keinerlei Verantwortung oder Haftung "
            "für Funktion, Verfügbarkeit, Richtigkeit oder Vollständigkeit der Abholung, insbesondere nicht für Schäden, die durch "
            "eine nicht oder verspätet erfolgte Abholung, Verarbeitung oder Weiterleitung entstehen könnten. Die Nutzung erfolgt "
            "auf eigene Gefahr. Prüfen Sie regelmäßig den Postkorb im Originalportal.\n\n"
            "Sicherheit: SSL-Zertifikatsprüfung ist deaktiviert (verify=False). Beachten Sie interne Sicherheitsvorgaben."
        )
        win = tk.Toplevel(self.root); win.title("Disclaimer / Impressum")
        txt = scrolledtext.ScrolledText(win, wrap="word", width=90, height=26); txt.pack(fill="both", expand=True)
        txt.insert("1.0", text); txt.config(state="disabled")

# ----- Main -----
def main():
    root = tk.Tk()
    root.geometry("1400x900")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
