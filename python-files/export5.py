# Confluence PDF mass export tool 0.02B by Ronny Görner
# Extended: Spaces & Labels workflow (v0.03 FIX7)
# Changes in FIX7:
# - Results list (Treeview): you can now combine selections freely.
#   * Click = select single
#   * Ctrl+Click = toggle item
#   * Drag = select range
#   * Ctrl+Drag = ADD the dragged range to existing selection (no clearing)
#
# Previous changes from FIX6 kept (max 5 spaces, no "Select all", labels w/ spaces, etc.).

import re, json, zipfile, tkinter as tk, requests, webbrowser, secrets, string
from requests import Session
SESSION = Session()
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from urllib.parse import urljoin, quote, urlencode

# Optional AES ZIP (pyzipper)
try:
    import pyzipper
    HAVE_PYZIPPER = True
except Exception:
    HAVE_PYZIPPER = False

APP_TITLE = "Confluence PDF mass export tool 0.02B by Ronny Görner"
DEFAULT_LIMIT = 200
MAX_RESULTS = 5000
MAX_LABEL_SCAN_PER_SPACE = 5000  # cap how many pages per space we scan for labels
MAX_SPACES_SELECT = 5

# Predefined Scroll PDF templates
TEMPLATES = [
    {"id": "de5975ff-52f6-4055-bbfa-607ba2674f2d", "name": "secupay (Landscape)"},
    {"id": "1afdcdf4-d1a8-4fad-a0da-7a3bb610af25", "name": "secupay - simple (Portrait)"},
]

LAST_ERROR_TEXT = None   # for "Show last error"

# ---------- Helpers ----------
def build_pages_url(base_url, space_key, page_id, title):
    base = base_url.rstrip("/")
    if space_key:
        slug = quote(title.replace(" ", "+"), safe="+")
        return f"{base}/spaces/{space_key}/pages/{page_id}/{slug}"
    return f"{base}/pages/{page_id}"

def sanitize_filename(name, fallback="file"):
    name = (name or "").strip() or fallback
    return re.sub(r'[\\/:*?"<>|]+', "_", name)[:150]

def _redact_headers(h):
    if not h: return {}
    out = {k:v for k,v in h.items()}
    for k in list(out):
        if k.lower()=="authorization": out[k] = "<redacted>"
    return out

def _is_probably_text(headers, body: bytes):
    ct = (headers or {}).get("Content-Type","").lower()
    if any(t in ct for t in ("json","xml","text","html","javascript")): return True
    if body.startswith((b"{", b"[")): return True
    sample = body[:200]
    printable = sum(32<=b<=126 or b in (9,10,13) for b in sample)
    return printable >= max(1, int(0.85*len(sample)))

def _looks_like_pdf(headers, body: bytes):
    ct = (headers or {}).get("Content-Type","").lower()
    cd = (headers or {}).get("Content-Disposition","")
    return ("pdf" in ct) or ("application/octet-stream" in ct and ".pdf" in cd.lower()) or body[:5]==b"%PDF-"

def _block(title, content):
    return f"{title}\n{'='*len(title)}\n{content}\n\n"

def _mk_error_text(name, method, url, req_headers, status, reason, resp_headers, body: bytes):
    if _looks_like_pdf(resp_headers, body or b""):
        body_summary = f"<binary PDF detected> size={len(body)} bytes; startswith=%PDF-? {body.startswith(b'%PDF-')}"
    else:
        if _is_probably_text(resp_headers, body or b""):
            try:
                enc="utf-8"; ct=resp_headers.get("Content-Type","") if resp_headers else ""
                if "charset=" in ct: enc = ct.split("charset=",1)[-1].split(";")[0].strip() or "utf-8"
                body_summary = (body or b"").decode(enc, errors="replace")
            except Exception:
                body_summary = "<failed to decode as text>"
        else:
            body_summary = f"<binary {len(body)} bytes; first64={(body or b'')[:64].hex(' ')}>"
    req_info = {"name":name,"method":method,"url":url,"headers":_redact_headers(req_headers or {})}
    resp_info = {"status":status,"reason":reason,"headers":resp_headers or {},"body_len":len(body or b"")}
    return _block("REQUEST", json.dumps(req_info, indent=2, ensure_ascii=False)) + \
           _block("RESPONSE META", json.dumps(resp_info, indent=2, ensure_ascii=False)) + \
           _block("RESPONSE BODY (safe)", body_summary or "<empty body>")

def _set_last_error(text:str):
    global LAST_ERROR_TEXT
    LAST_ERROR_TEXT = text

# ---------- Password generation ----------
def generate_password(length: int) -> str:
    length = max(8, min(32, int(length or 16)))
    alphabet_sets = {
        "upper": string.ascii_uppercase,
        "lower": string.ascii_lowercase,
        "digits": string.digits,
        "punct": "!#$%&()*+,-./:;<=>?@[]^_{|}~"
    }
    pwd = [
        secrets.choice(alphabet_sets["upper"]),
        secrets.choice(alphabet_sets["lower"]),
        secrets.choice(alphabet_sets["digits"]),
        secrets.choice(alphabet_sets["punct"]),
    ]
    allchars = "".join(alphabet_sets.values())
    pwd += [secrets.choice(allchars) for _ in range(length - len(pwd))]
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)

# ---------- Token verification ----------
def verify_token(base_url, token):
    url = urljoin(base_url.rstrip("/") + "/", "rest/api/user/current")
    headers = {"Authorization": f"Bearer {token.strip()}","Accept":"application/json"}
    try:
        r = SESSION.get(url, headers=headers, timeout=20)
    except Exception as e:
        _set_last_error(_block("Token verification exception", repr(e)))
        raise RuntimeError("Could not reach Confluence to verify the token.")
    if r.status_code in (401,403):
        _set_last_error(_mk_error_text("Token verification (auth error)", "GET", r.url, headers,
                                       r.status_code, r.reason, dict(r.headers), r.content or b""))
        raise PermissionError("Unauthorized/forbidden. Token invalid/expired or lacks permission.")
    if not r.ok:
        _set_last_error(_mk_error_text("Token verification (HTTP error)", "GET", r.url, headers,
                                       r.status_code, r.reason, dict(r.headers), r.content or b""))
        raise RuntimeError(f"Token verification failed (HTTP {r.status_code}).")
    try:
        data = r.json()
    except Exception:
        _set_last_error(_mk_error_text("Token verification (non-JSON)", "GET", r.url, headers,
                                       r.status_code, r.reason, dict(r.headers), r.content or b""))
        raise RuntimeError("Token verification returned an unexpected response.")
    user = data.get("username") or data.get("userKey") or data.get("accountId") or "unknown-user"
    display = data.get("displayName") or data.get("publicName") or user
    return {"user": user, "displayName": display}

# ---------- On-demand fetch of space key for content id ----------
_space_cache = {}
def _fetch_space_key_on_demand(base_url:str, token:str, page_id:str) -> str:
    if page_id in _space_cache:
        return _space_cache[page_id]
    url = urljoin(base_url.rstrip("/") + "/", f"rest/api/content/{page_id}")
    headers = {"Authorization": f"Bearer {token.strip()}","Accept":"application/json"}
    try:
        r = SESSION.get(url, headers=headers, params={"expand":"space"}, timeout=20)
        if r.ok:
            key = ((r.json().get("space") or {}).get("key")) or ""
            _space_cache[page_id] = key
            return key
        else:
            _set_last_error(_mk_error_text("Fetch space key (expand=space)", "GET", r.url, headers, r.status_code, r.reason, dict(r.headers), r.content or b""))
            return ""
    except Exception as e:
        _set_last_error(_block("Fetch space key exception", repr(e)))
        return ""

# ---------- Spaces ----------
def fetch_spaces(base_url, token, limit=100):
    base = base_url.rstrip("/") + "/"
    url = urljoin(base, "rest/api/space")
    headers = {"Authorization": f"Bearer {token.strip()}","Accept":"application/json"}
    start = 0
    out = []
    while True:
        try:
            r = SESSION.get(url, headers=headers, params={"type":"global","limit":limit,"start":start}, timeout=30)
            if r.status_code in (401,403):
                _set_last_error(_mk_error_text("Fetch spaces (auth error)","GET",r.url,headers,r.status_code,r.reason,dict(r.headers),r.content or b""))
                raise PermissionError("Unauthorized/forbidden while listing spaces.")
            if not r.ok:
                _set_last_error(_mk_error_text("Fetch spaces (HTTP error)","GET",r.url,headers,r.status_code,r.reason,dict(r.headers),r.content or b""))
                r.raise_for_status()
        except Exception as e:
            if LAST_ERROR_TEXT is None: _set_last_error(_block("Fetch spaces exception", repr(e)))
            raise
        data = r.json()
        results = data.get("results", [])
        for s in results:
            out.append({"key": s.get("key",""), "name": s.get("name",""), "type": s.get("type","")})
        if len(results) < limit: break
        start += len(results)
        if start > 10000: break  # safety
    out.sort(key=lambda x: (x["name"] or x["key"]).lower())
    return out

# ---------- Labels by scanning content ----------
def fetch_labels_for_spaces(base_url, token, space_keys, per_page_limit=200, max_pages_per_space=MAX_LABEL_SCAN_PER_SPACE):
    """
    Aggregate labels across spaces, and also remember which spaces each label appears in.
    Returns dict: {label_name: {"count": int, "spaces": set([...])}}
    """
    base = base_url.rstrip("/") + "/"
    headers = {"Authorization": f"Bearer {token.strip()}","Accept":"application/json"}
    labels = {}
    for key in space_keys:
        url = urljoin(base, "rest/api/content")
        start = 0
        scanned = 0
        while True:
            params = {"spaceKey": key, "type": "page", "limit": per_page_limit, "start": start, "expand": "metadata.labels"}
            try:
                r = SESSION.get(url, headers=headers, params=params, timeout=30)
                if r.status_code in (401,403):
                    _set_last_error(_mk_error_text("Fetch labels (auth error)","GET",r.url,headers,r.status_code,r.reason,dict(r.headers),r.content or b""))
                    raise PermissionError("Unauthorized/forbidden while scanning labels.")
                if not r.ok:
                    _set_last_error(_mk_error_text("Fetch labels (HTTP error)","GET",r.url,headers,r.status_code,r.reason,dict(r.headers),r.content or b""))
                    r.raise_for_status()
            except Exception as e:
                if LAST_ERROR_TEXT is None: _set_last_error(_block("Fetch labels exception", repr(e)))
                raise
            data = r.json()
            results = data.get("results", [])
            if not results: break
            for item in results:
                scanned += 1
                md = item.get("metadata") or {}
                labs = ((md.get("labels") or {}).get("results")) or []
                for lab in labs:
                    name = (lab.get("name") or "").strip()
                    if not name: continue
                    entry = labels.setdefault(name, {"count":0, "spaces": set()})
                    entry["count"] += 1
                    entry["spaces"].add(key)
            start += len(results)
            if len(results) < per_page_limit: break
            if scanned >= max_pages_per_space: break
    return labels

# ---------- Search pages by spaces and optional labels ----------

def search_pages_by_spaces_and_labels(base_url, token, space_keys, label_names=None, limit=DEFAULT_LIMIT, max_results=MAX_RESULTS):
    """
    Faster search using /rest/api/content/search with expand=space.
    Avoids per-page space lookups and reduces total HTTP calls.
    """
    if not space_keys:
        raise ValueError("No spaces selected.")
    headers = {"Authorization": f"Bearer {token.strip()}", "Accept":"application/json"}
    base = base_url.rstrip("/") + "/"
    url = urljoin(base, "rest/api/content/search")

    space_clause = "(" + " OR ".join([f'space="{s}"' for s in space_keys]) + ")"
    label_clause = ""
    if label_names:
        label_clause = " AND (" + " OR ".join([f'label="{l}"' for l in label_names]) + ")"
    cql = f'type=page AND {space_clause}{label_clause}'

    results, start = [], 0
    while True:
        params = {"cql": cql, "limit": limit, "start": start, "expand": "space", "status": "current"}
        try:
            r = SESSION.get(url, headers=headers, params=params, timeout=30)
            if r.status_code in (401,403):
                _set_last_error(_mk_error_text("Search (auth error)","GET",r.url,headers,r.status_code,r.reason,dict(r.headers),r.content or b""))
                raise PermissionError("Unauthorized/forbidden during search.")
            if not r.ok:
                _set_last_error(_mk_error_text("Search (HTTP error)","GET",r.url,headers,r.status_code,r.reason,dict(r.headers),r.content or b""))
                r.raise_for_status()
        except Exception as e:
            if LAST_ERROR_TEXT is None: _set_last_error(_block("Search exception", repr(e)))
            raise

        data = r.json()
        matches = data.get("results", [])
        if not matches:
            break

        for m in matches:
            cid = str(m.get("id","") or (m.get("content") or {}).get("id",""))
            title = m.get("title") or (m.get("content") or {}).get("title") or "(no title)"
            space_obj = m.get("space") or (m.get("content") or {}).get("space") or {}
            space_key = space_obj.get("key","")
            page_url = build_pages_url(base_url, space_key, cid, title) if cid else ""
            results.append({"title": title, "id": cid, "space": space_key, "url": page_url})

        start += len(matches)
        if start >= max_results or len(matches) < limit:
            break
    return results
# ---------- Scroll PDF (sync) ----------
def _do_export_request(url, headers, name_for_log):
    try:
        return SESSION.get(url, headers=headers, timeout=180)
    except Exception as e:
        _set_last_error(_block(f"{name_for_log} exception (network/timeout)", repr(e)))
        raise

def _looks_ok_pdf_response(resp):
    return resp.ok and _looks_like_pdf(resp.headers, resp.content or b"")

def export_scrollpdf_single_sync(base_url, token, template_id, page_id)->bytes:
    base = base_url.rstrip("/") + "/"
    path = "plugins/servlet/scroll-pdf/api/public/1/export-sync"
    qs = urlencode({"templateId":str(template_id),"pageId":str(page_id),"scope":"current"})
    url = urljoin(base, f"{path}?{qs}")
    h1 = {"Authorization": f"Bearer {token.strip()}","Accept":"application/pdf"}
    r1 = _do_export_request(url, h1, "Scroll PDF export (attempt 1)")
    if r1.status_code in (401,403):
        _set_last_error(_mk_error_text("Scroll PDF export (auth issue, attempt 1)","GET",url,h1,r1.status_code,r1.reason,dict(r1.headers),r1.content or b""))
        raise PermissionError("Export not permitted (401/403). Check token/permissions.")
    if _looks_ok_pdf_response(r1): return r1.content
    h2 = {"Authorization": f"Bearer {token.strip()}","Accept":"*/*","User-Agent":"PostmanRuntime/7.39.0",
          "Accept-Encoding":"gzip, deflate, br","Connection":"keep-alive","Accept-Language":"en-US,en;q=0.9"}
    r2 = _do_export_request(url, h2, "Scroll PDF export (attempt 2 with Postman-like headers)")
    if r2.status_code in (401,403):
        _set_last_error(_mk_error_text("Scroll PDF export (auth issue, attempt 2)","GET",url,h2,r2.status_code,r2.reason,dict(r2.headers),r2.content or b""))
        raise PermissionError("Export not permitted (401/403). Check token/permissions.")
    if _looks_ok_pdf_response(r2): return r2.content
    msg = _mk_error_text("Scroll PDF export failure (attempt 1)","GET",url,h1,r1.status_code,r1.reason,dict(r1.headers),r1.content or b"")
    msg+= _mk_error_text("Scroll PDF export failure (attempt 2)","GET",url,h2,r2.status_code,r2.reason,dict(r2.headers),r2.content or b"")
    _set_last_error(msg)
    raise RuntimeError("Export failed (non-PDF response). See 'Show last error' for details.")

# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE); self.geometry("1280x870")

        self.verified_user = None
        self.spaces_cache = []  # [{'key','name','type'}]
        self.labels_cache = {}  # label -> {"count": int, "spaces": set([...])}

        frm = ttk.Frame(self, padding=12); frm.pack(fill="x")

        # Row 0: Base URL
        ttk.Label(frm, text="Confluence Base URL:").grid(row=0, column=0, sticky="w")
        self.base_url_var = tk.StringVar(value="https://confluence.webhaus.de")
        ttk.Entry(frm, textvariable=self.base_url_var, width=70).grid(row=0, column=1, columnspan=6, sticky="we")

        # Row 1: Token
        ttk.Label(frm, text="Personal Access Token:").grid(row=1, column=0, sticky="w")
        self.token_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.token_var, width=70, show="•").grid(row=1, column=1, columnspan=6, sticky="we")

        # Row 2: Actions
        self.verify_btn = ttk.Button(frm, text="1) Verify token", command=self.on_verify)
        self.verify_btn.grid(row=2, column=0, sticky="w", pady=(6,0))

        self.load_spaces_btn = ttk.Button(frm, text="2) Load spaces", command=self.on_load_spaces, state="disabled")
        self.load_spaces_btn.grid(row=2, column=1, sticky="w", pady=(6,0))

        self.load_labels_btn = ttk.Button(frm, text="3) Load labels from selected spaces", command=self.on_load_labels, state="disabled")
        self.load_labels_btn.grid(row=2, column=2, sticky="w", pady=(6,0))

        # Panels
        panes = ttk.PanedWindow(frm, orient="horizontal"); panes.grid(row=3, column=0, columnspan=7, sticky="nsew", pady=(8,4))
        frm.grid_rowconfigure(3, weight=1); frm.grid_columnconfigure(6, weight=1)

        # Spaces panel
        spaces_frame = ttk.Labelframe(panes, text="Spaces")
        panes.add(spaces_frame, weight=1)
        self.spaces_list = tk.Listbox(spaces_frame, selectmode="extended", exportselection=False)
        self.spaces_list.pack(fill="both", expand=True, padx=8, pady=(8,0))
        # Indicator
        self.spaces_selected_var = tk.StringVar(value=f"Selected: 0 / {MAX_SPACES_SELECT} max")
        ttk.Label(spaces_frame, textvariable=self.spaces_selected_var).pack(anchor="w", padx=8, pady=(4,8))
        # Robust enabling hooks
        for seq in ("<<ListboxSelect>>", "<ButtonRelease-1>", "<KeyRelease>", "<FocusIn>"):
            self.spaces_list.bind(seq, self.on_spaces_select)

        spaces_btns = ttk.Frame(spaces_frame); spaces_btns.pack(fill="x", padx=8, pady=(0,8))
        ttk.Button(spaces_btns, text="Clear", command=self.clear_spaces).pack(side="left", padx=(6,0))

        # Labels panel
        labels_frame = ttk.Labelframe(panes, text="Labels (from selected spaces)")
        panes.add(labels_frame, weight=1)
        self.labels_list = tk.Listbox(labels_frame, selectmode="extended", exportselection=False)
        self.labels_list.pack(fill="both", expand=True, padx=8, pady=(8,0))
        self.labels_hint = tk.StringVar(value="0 labels loaded.")
        ttk.Label(labels_frame, textvariable=self.labels_hint).pack(anchor="w", padx=8, pady=(4,8))
        labels_btns = ttk.Frame(labels_frame); labels_btns.pack(fill="x", padx=8, pady=(0,8))
        ttk.Button(labels_btns, text="Select none", command=self.clear_labels).pack(side="left")
        self.selected_label_count = tk.StringVar(value="Selected: 0 / 5 max")
        ttk.Label(labels_btns, textvariable=self.selected_label_count).pack(side="right")

        self.labels_list.bind("<<ListboxSelect>>", self.on_labels_select)

        # Search mode (radios only)
        mode_frame = ttk.Frame(frm); mode_frame.grid(row=4, column=0, columnspan=7, sticky="we", pady=(6,0))
        self.mode_var = tk.StringVar(value="all")
        ttk.Radiobutton(mode_frame, text="Show ALL pages in selected spaces", value="all", variable=self.mode_var).pack(side="left", padx=(0,16))
        ttk.Radiobutton(mode_frame, text="Filter by selected labels (ANY of up to 5)", value="labels", variable=self.mode_var).pack(side="left")

        # Template + Encryption
        template_row = ttk.Frame(frm); template_row.grid(row=5, column=0, columnspan=7, sticky="we", pady=(8,0))
        ttk.Label(template_row, text="Scroll PDF Template:").pack(side="left")
        self.template_combo = ttk.Combobox(template_row, state="readonly", width=50, values=[t["name"] for t in TEMPLATES])
        self.template_combo.pack(side="left", padx=(6,0))
        if TEMPLATES: self.template_combo.current(0)

        enc_frame = ttk.LabelFrame(frm, text="ZIP Encryption (AES-256)")
        enc_frame.grid(row=6, column=0, columnspan=7, sticky="we", pady=(8,0))
        for i in range(8): enc_frame.grid_columnconfigure(i, weight=1)

        self.encrypt_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(enc_frame, text="Encrypt ZIP (AES-256)", variable=self.encrypt_var).grid(row=0, column=0, sticky="w", padx=(8,6), pady=6)
        ttk.Label(enc_frame, text="Password length:").grid(row=0, column=1, sticky="e")
        self.pw_len_var = tk.IntVar(value=16)
        ttk.Spinbox(enc_frame, from_=8, to=32, textvariable=self.pw_len_var, width=5).grid(row=0, column=2, sticky="w")
        ttk.Label(enc_frame, text="Password:").grid(row=1, column=0, sticky="e", padx=(8,6))
        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(enc_frame, textvariable=self.pw_var, width=50, show="•")
        self.pw_entry.grid(row=1, column=1, columnspan=3, sticky="w")
        ttk.Button(enc_frame, text="Generate", command=self.on_generate_password).grid(row=1, column=4, sticky="w", padx=(6,0))
        self.show_pw_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(enc_frame, text="Show password", variable=self.show_pw_var, command=self.on_toggle_show_password).grid(row=1, column=5, sticky="w")

        # Controls (main Search button + others)
        controls = ttk.Frame(frm); controls.grid(row=7, column=0, columnspan=7, sticky="we", pady=(8,0))
        self.search_btn_main = ttk.Button(controls, text="Search", command=self.on_search, state="disabled")
        self.search_btn_main.pack(side="left")
        self.export_btn = ttk.Button(controls, text="Export Selected Pages to ZIP", command=self.on_export, state="disabled")
        self.export_btn.pack(side="left", padx=(12,0))
        self.error_btn = ttk.Button(controls, text="Show last error", command=self.show_last_error, state="disabled")
        self.error_btn.pack(side="left", padx=(12,0))

        # Status
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(12, 6)).pack(fill="x")

        
        # Results tree + scrollbars
        cols = ("title","space","id","url")
        results_frame = ttk.Frame(self)
        results_frame.pack(fill="both", expand=True, padx=12, pady=(0,12))

        xscroll = ttk.Scrollbar(results_frame, orient="horizontal")
        yscroll = ttk.Scrollbar(results_frame, orient="vertical")

        self.tree = ttk.Treeview(
            results_frame,
            columns=cols,
            show="headings",
            selectmode="extended",
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set
        )
        self._base_headings = {"title":"Title","space":"Space","id":"ID","url":"URL"}
        for c,w in zip(cols,(600,100,130,420)):
            self.tree.heading(c, text=self._base_headings[c], command=lambda _c=c: self.on_heading_click(_c))
            self.tree.column(c, width=w, stretch=(c in ("title","url")))

        # Layout grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # Hook scrollbars
        yscroll.config(command=self.tree.yview)
        xscroll.config(command=self.tree.xview)

        self.tree.bind("<Double-1>", self.open_selected_url)

        
        # Sort state
        self.sort_col = 'title'
        self.sort_desc = False
# Improved multi-select: supports additive Ctrl+drag
        self._anchor_iid = None
        self._dragging = False
        self.tree.bind("<Button-1>", self._tree_on_button1, add="+")
        self.tree.bind("<B1-Motion>", self._tree_on_b1_motion, add="+")
        self.tree.bind("<ButtonRelease-1>", self._tree_on_button1_release, add="+")

        # Safety: small polling loop for spaces selection
        self._last_space_sel = ()
        self.after(300, self._poll_space_selection)

    # ----- polling safeguard -----
    def _poll_space_selection(self):
        cur = tuple(self.spaces_list.curselection())
        if cur != self._last_space_sel:
            self._last_space_sel = cur
            # Enforce limit silently during polling (no popup)
            if len(cur) > MAX_SPACES_SELECT:
                for idx in cur[MAX_SPACES_SELECT:]:
                    self.spaces_list.selection_clear(idx)
            self.update_label_controls()
        self.after(300, self._poll_space_selection)

    # ----- UI helpers -----
    def set_status(self, text): self.status_var.set(text); self.update_idletasks()
    def enable_error_button(self): self.error_btn.config(state="normal")

    def on_spaces_select(self, _evt=None):
        sel = list(self.spaces_list.curselection())
        if len(sel) > MAX_SPACES_SELECT:
            for idx in sel[MAX_SPACES_SELECT:]:
                self.spaces_list.selection_clear(idx)
            messagebox.showinfo("Limit", f"Please select at most {MAX_SPACES_SELECT} spaces.")
            sel = list(self.spaces_list.curselection())
        # update indicator
        self.spaces_selected_var.set(f"Selected: {len(sel)} / {MAX_SPACES_SELECT} max")
        self.update_label_controls()

    def clear_spaces(self):
        self.spaces_list.selection_clear(0, tk.END)
        self.spaces_selected_var.set(f"Selected: 0 / {MAX_SPACES_SELECT} max")
        self.update_label_controls()

    def clear_labels(self):
        self.labels_list.selection_clear(0, tk.END)
        self.selected_label_count.set("Selected: 0 / 5 max")

    def on_labels_select(self, _evt=None):
        sel = list(self.labels_list.curselection())
        if len(sel) > 5:
            for idx in sel[5:]:
                self.labels_list.selection_clear(idx)
            sel = list(self.labels_list.curselection())
            messagebox.showinfo("Limit", "Please select at most 5 labels.")
        self.selected_label_count.set(f"Selected: {len(sel)} / 5 max")

    def update_label_controls(self):
        has_space = len(self.spaces_list.curselection()) > 0
        state = (tk.NORMAL if has_space else tk.DISABLED)
        self.load_labels_btn.config(state=state)
        self.search_btn_main.config(state=state)

    # ----- Password UI handlers -----
    def on_generate_password(self):
        length = self.pw_len_var.get()
        pwd = generate_password(length)
        self.pw_var.set(pwd)
        if not self.show_pw_var.get():
            self.pw_entry.config(show="•")

    def on_toggle_show_password(self):
        self.pw_entry.config(show="" if self.show_pw_var.get() else "•")

    # ----- Treeview selection helpers -----
    def _tree_get_all_rows(self):
        return list(self.tree.get_children(""))

    def _tree_index_of(self, iid):
        rows = self._tree_get_all_rows()
        try:
            return rows.index(iid)
        except ValueError:
            return -1

    def _tree_range_between(self, iid1, iid2):
        rows = self._tree_get_all_rows()
        try:
            i0, i1 = rows.index(iid1), rows.index(iid2)
        except ValueError:
            return []
        lo, hi = (i0, i1) if i0 <= i1 else (i1, i0)
        return rows[lo:hi+1]

    def _ctrl_pressed(self, event):
        # Tk bitmask: Control modifier commonly 0x0004 on Windows/X11
        return (event.state & 0x0004) != 0

    # ----- Treeview mouse handlers (additive selection supported) -----
    def _tree_on_button1(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region in ("heading","separator"):
            return  # let heading click / resize work
        iid = self.tree.identify_row(event.y)
        if not iid:
            return  # don't break; allow default noop
        ctrl = self._ctrl_pressed(event)
        self._anchor_iid = iid
        self._dragging = False
        if ctrl:
            # Toggle selection without clearing others
            cur = set(self.tree.selection())
            if iid in cur:
                self.tree.selection_remove(iid)
            else:
                self.tree.selection_add(iid)
        else:
            # Replace selection with this single item
            self.tree.selection_set(iid)
        return "break"  # prevent default behavior from interfering

    def _tree_on_b1_motion(self, event):
        if not self._anchor_iid:
            return
        cur_iid = self.tree.identify_row(event.y)
        if not cur_iid:
            return "break"
        self._dragging = True
        rng = self._tree_range_between(self._anchor_iid, cur_iid)
        if not rng:
            return "break"
        if self._ctrl_pressed(event):
            # Add range to existing selection
            for iid in rng:
                self.tree.selection_add(iid)
        else:
            # Replace with range
            self.tree.selection_set(rng)
        return "break"

    def _tree_on_button1_release(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region in ("heading","separator"):
            return  # allow header interactions
        # Nothing special; keep our selection
        self._dragging = False
        return "break"

    # ----- Token verification -----
    def on_verify(self):
        base = self.base_url_var.get().strip()
        token = self.token_var.get().strip()
        if not base or not token:
            messagebox.showwarning("Missing input", "Provide Base URL and Token."); return
        self.set_status("Verifying token…")
        self.verify_btn.config(state="disabled")
        self.after(50, self._do_verify)

    def _do_verify(self):
        global LAST_ERROR_TEXT
        try:
            info = verify_token(self.base_url_var.get().strip(), self.token_var.get().strip())
            self.verified_user = f'{info.get("user")} — {info.get("displayName")}'
            self.set_status(f"Token OK: {self.verified_user}")
            self.load_spaces_btn.config(state=tk.NORMAL)
        except PermissionError:
            self.set_status("Authorization error. Check your token.")
            if LAST_ERROR_TEXT: self.enable_error_button()
            messagebox.showerror("Authorization error", "Token invalid/expired or lacks permission.\n\nClick 'Show last error' for details.")
        except Exception as e:
            self.set_status("Token verification failed. Click 'Show last error' for details.")
            if LAST_ERROR_TEXT: self.enable_error_button()
            messagebox.showerror("Token verification error", str(e))
        finally:
            self.verify_btn.config(state=tk.NORMAL)

    # ----- Load spaces -----
    def on_load_spaces(self):
        self.set_status("Loading spaces…")
        self.load_spaces_btn.config(state=tk.DISABLED)
        self.spaces_list.delete(0, tk.END)
        self.after(50, self._do_load_spaces)

    def _do_load_spaces(self):
        global LAST_ERROR_TEXT
        try:
            self.spaces_cache = fetch_spaces(self.base_url_var.get().strip(), self.token_var.get().strip())
            if not self.spaces_cache:
                messagebox.showinfo("No spaces", "No global spaces found or permission denied.")
                self.set_status("No spaces found."); return
            for s in self.spaces_cache:
                self.spaces_list.insert(tk.END, f'{s["name"]}  [{s["key"]}]')
            self.set_status(f"Loaded {len(self.spaces_cache)} spaces. Select (up to {MAX_SPACES_SELECT}), then click 'Load labels…' or 'Search'.")
            self.spaces_selected_var.set(f"Selected: 0 / {MAX_SPACES_SELECT} max")
        except Exception as e:
            self.set_status("Failed to load spaces. Click 'Show last error' for details.")
            if LAST_ERROR_TEXT: self.enable_error_button()
            messagebox.showerror("Load spaces error", str(e))
        finally:
            self.load_spaces_btn.config(state=tk.NORMAL)
            self.update_label_controls()

    # ----- Load labels for selected spaces -----
    def on_load_labels(self):
        sel_idxs = list(self.spaces_list.curselection())
        if not sel_idxs:
            messagebox.showinfo("Select spaces", "Please select at least one space first.")
            return
        space_keys = [self.spaces_cache[i]["key"] for i in sel_idxs]
        self.labels_list.delete(0, tk.END)
        self.labels_hint.set("Scanning labels…")
        self.set_status("Scanning labels from selected spaces…")
        self.load_labels_btn.config(state=tk.DISABLED)
        self.after(50, lambda: self._do_load_labels(space_keys))

    def _do_load_labels(self, space_keys):
        global LAST_ERROR_TEXT
        try:
            agg = fetch_labels_for_spaces(self.base_url_var.get().strip(), self.token_var.get().strip(), space_keys)
            self.labels_cache = agg
            if not agg:
                self.labels_hint.set("No labels found in the selected spaces.")
                self.set_status("No labels found.")
                return
            items = sorted(agg.items(), key=lambda kv: kv[0].lower())
            for name, meta in items:
                space_list = ", ".join(sorted(meta["spaces"]))
                self.labels_list.insert(tk.END, f"{name}  ({meta['count']}) [{space_list}]")
            self.labels_hint.set(f"Loaded {len(items)} labels. Select up to 5.")
            self.set_status(f"Loaded {len(items)} labels.")
        except Exception as e:
            self.labels_hint.set("Failed to load labels.")
            self.set_status("Failed to load labels. Click 'Show last error' for details.")
            if LAST_ERROR_TEXT: self.enable_error_button()
            messagebox.showerror("Load labels error", str(e))
        finally:
            self.load_labels_btn.config(state=tk.NORMAL)

    def _get_selected_spaces(self):
        idxs = list(self.spaces_list.curselection())
        return [self.spaces_cache[i]["key"] for i in idxs]

    def _get_selected_label_names(self):
        idxs = list(self.labels_list.curselection())
        names = []
        for i in idxs[:5]:
            raw = self.labels_list.get(i)
            name = raw.split("  (", 1)[0]  # before the "(count)"
            if name: names.append(name)
        return names

    # ----- Search -----
    def on_search(self):
        space_keys = self._get_selected_spaces()
        if not space_keys:
            messagebox.showinfo("Select spaces", "Please select at least one space."); return
        use_labels = (self.mode_var.get() == "labels")
        label_names = self._get_selected_label_names() if use_labels else []
        if use_labels and not label_names:
            messagebox.showinfo("Select labels", "Please select up to 5 labels (at least one)."); return
        for row in self.tree.get_children(): self.tree.delete(row)
        self.search_btn_main.config(state=tk.DISABLED)
        mode_txt = "with label filter" if use_labels else "without label filter"
        self.set_status(f"Searching in {len(space_keys)} space(s) {mode_txt}…")
        self.after(50, lambda: self._do_search(space_keys, label_names))

    def _do_search(self, space_keys, label_names):
        global LAST_ERROR_TEXT
        try:
            pages = search_pages_by_spaces_and_labels(self.base_url_var.get().strip(), self.token_var.get().strip(), space_keys, label_names)
            if not pages:
                flt = f" with labels {label_names}" if label_names else ""
                messagebox.showinfo("No results", f"No content found in selected spaces{flt}.")
                self.set_status("No results."); return
            # Order by title (A→Z, case-insensitive)
            pages.sort(key=lambda p: (p.get('title') or '').casefold())
            for p in pages:
                self.tree.insert("", "end", values=(p["title"], p["space"], p["id"], p["url"]))
            self.sort_tree('title', False)
            self.set_status(f"Found {len(pages)} item(s). Use Click / Ctrl+Click, Drag / Ctrl+Drag to refine selection.")
            self.export_btn.config(state=tk.NORMAL)
        except PermissionError:
            self.set_status("Authorization error during search. Check your token.")
            if LAST_ERROR_TEXT: self.enable_error_button()
            messagebox.showerror("Authorization error", "Your token lacks permission.")
        except Exception as e:
            self.set_status("Error during search. Click 'Show last error' for details.")
            if LAST_ERROR_TEXT: self.enable_error_button()
            messagebox.showerror("Search error", str(e))
        finally:
            self.search_btn_main.config(state=tk.NORMAL)

    # ----- Export -----
    def _get_selected_pages(self):
        return [dict(zip(("title","space","id","url"), self.tree.item(i,"values"))) for i in self.tree.selection()]

    def on_export(self):
        pages = self._get_selected_pages()
        if not pages:
            messagebox.showwarning("Selection required", "Select at least one item."); return
        idx = self.template_combo.current()
        if idx is None or idx < 0:
            messagebox.showwarning("Template required", "Select a template."); return
        template_id = TEMPLATES[idx]["id"]
        zip_path = filedialog.asksaveasfilename(title="Save ZIP", defaultextension=".zip", filetypes=[("ZIP archive","*.zip")])
        if not zip_path: return
        use_enc = self.encrypt_var.get()
        password = self.pw_var.get().strip()
        if use_enc:
            if not HAVE_PYZIPPER:
                messagebox.showerror("Missing dependency", "Encryption requires 'pyzipper'.\nInstall with: pip install pyzipper")
                return
            if not password:
                password = generate_password(self.pw_len_var.get())
                self.pw_var.set(password)
                if not self.show_pw_var.get():
                    self.pw_entry.config(show="•")
        self.set_status("Exporting PDFs…"); self.export_btn.config(state=tk.DISABLED)
        self.after(50, lambda: self._do_export_zip(pages, template_id, zip_path, use_enc, password))

    def _do_export_zip(self, pages, template_id, zip_path, use_enc, password):
        global LAST_ERROR_TEXT
        ok, errors, abort = 0, [], False
        try:
            if use_enc:
                with pyzipper.AESZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                    zf.setpassword(password.encode("utf-8"))
                    zf.setencryption(pyzipper.WZ_AES, nbits=256)
                    for i,p in enumerate(pages, start=1):
                        if abort: break
                        try:
                            self.set_status(f'Exporting {i}/{len(pages)}: {p["title"]}')
                            pdf = export_scrollpdf_single_sync(self.base_url_var.get().strip(), self.token_var.get().strip(), template_id, p["id"])
                            file_label = f'page_{p["id"]}'
                            filename = f'{sanitize_filename(p["title"], file_label)}__{p["id"]}.pdf'
                            zf.writestr(filename, pdf)
                            ok += 1
                        except PermissionError:
                            abort = True
                            if LAST_ERROR_TEXT: self.enable_error_button()
                            errors.append(f'{p["title"]}: authorization error')
                            messagebox.showerror("Authorization error during export", "Export aborted: token invalid/expired or lacks permission.\nClick 'Show last error' for details.")
                        except Exception as e:
                            if LAST_ERROR_TEXT: self.enable_error_button()
                            errors.append(f'{p["title"]}: {e}')
            else:
                with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    for i,p in enumerate(pages, start=1):
                        if abort: break
                        try:
                            self.set_status(f'Exporting {i}/{len(pages)}: {p["title"]}')
                            pdf = export_scrollpdf_single_sync(self.base_url_var.get().strip(), self.token_var.get().strip(), template_id, p["id"])
                            file_label = f'page_{p["id"]}'
                            filename = f'{sanitize_filename(p["title"], file_label)}__{p["id"]}.pdf'
                            zf.writestr(filename, pdf)
                            ok += 1
                        except PermissionError:
                            abort = True
                            if LAST_ERROR_TEXT: self.enable_error_button()
                            errors.append(f'{p["title"]}: authorization error')
                            messagebox.showerror("Authorization error during export", "Export aborted: token invalid/expired or lacks permission.\nClick 'Show last error' for details.")
                        except Exception as e:
                            if LAST_ERROR_TEXT: self.enable_error_button()
                            errors.append(f'{p["title"]}: {e}')

            if ok == 0 and not abort:
                self.set_status("All exports failed. Click 'Show last error' for details.")
                messagebox.showerror("Export failed", "No PDFs exported. Click 'Show last error' for details."); return
            if ok == 0 and abort:
                self.set_status("Export aborted due to authorization error."); return

            if errors:
                self.set_status(f"{ok} exported, {len(errors)} failed. Click 'Show last error' for details.")
                messagebox.showwarning("Partial success",
                                       f"{ok} exported, {len(errors)} failed.\nFirst error: {errors[0]}\n\n"
                                       "Click 'Show last error' for details.")
            else:
                enc_msg = " (encrypted, AES-256)" if use_enc else ""
                self.set_status(f"Finished. {ok} exported → {zip_path}{enc_msg}")
                if use_enc:
                    messagebox.showinfo("Done", f"Exported {ok} PDFs → {zip_path}\n\nZIP is AES-256 encrypted.")
                else:
                    messagebox.showinfo("Done", f"Exported {ok} PDFs → {zip_path}")
        finally:
            self.export_btn.config(state=tk.NORMAL)

    # ----- Error viewer & URL opener -----
    def show_last_error(self):
        global LAST_ERROR_TEXT
        if not LAST_ERROR_TEXT:
            messagebox.showinfo("No error", "No error details captured yet."); return
        win = tk.Toplevel(self); win.title("Last API Error (details)"); win.geometry("950x600")
        txt = ScrolledText(win, wrap="none"); txt.pack(fill="both", expand=True)
        txt.insert("1.0", LAST_ERROR_TEXT); txt.configure(state="disabled")
        btns = ttk.Frame(win); btns.pack(fill="x")
        def copy_clip(): self.clipboard_clear(); self.clipboard_append(LAST_ERROR_TEXT); self.update()
        def save_file():
            path = filedialog.asksaveasfilename(title="Save error details", defaultextension=".txt", filetypes=[("Text file","*.txt")])
            if not path: return
            with open(path,"w",encoding="utf-8") as f: f.write(LAST_ERROR_TEXT)
            messagebox.showinfo("Saved", f"Saved error details to:\n{path}")
        ttk.Button(btns, text="Copy to clipboard", command=copy_clip).pack(side="left", padx=6, pady=6)
        ttk.Button(btns, text="Save to file…", command=save_file).pack(side="left", padx=6, pady=6)
        ttk.Button(btns, text="Close", command=win.destroy).pack(side="right", padx=6, pady=6)

    
    def on_heading_click(self, col):
        # Toggle or set sort column
        if self.sort_col == col:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_col = col
            self.sort_desc = False
        self.sort_tree(self.sort_col, self.sort_desc)

    def _update_heading_arrows(self):
        # Update header text with arrows for the active column
        for c, base in self._base_headings.items():
            label = base
            if c == self.sort_col:
                label += " " + ("▼" if self.sort_desc else "▲")
            self.tree.heading(c, text=label, command=lambda _c=c: self.on_heading_click(_c))

    def sort_tree(self, col, descending=False):
        """Sort rows in the results Treeview by a column.
        col: one of 'title', 'space', 'id', 'url'
        descending: True for Z→A, False for A→Z
        """
        # Extract all row IDs
        children = list(self.tree.get_children(""))
        # Build key function per column
        def keyfunc(iid):
            v = self.tree.set(iid, col)
            if col == "id":
                # numeric-first sort for ids; fall back to casefold
                try:
                    return (0, int(v))
                except Exception:
                    return (1, (v or "").casefold())
            else:
                return ((v or "").casefold(),)
        # Sort iids
        children.sort(key=keyfunc, reverse=descending)
        # Preserve selection & focus
        sel = set(self.tree.selection())
        foc = self.tree.focus()
        # Reinsert in sorted order
        for idx, iid in enumerate(children):
            self.tree.move(iid, "", idx)
        # Restore selection & focus
        if sel:
            self.tree.selection_set([iid for iid in children if iid in sel])
        if foc in children:
            self.tree.focus(foc)
        # Update header arrows
        self._update_heading_arrows()

    def open_selected_url(self, _=None):
        cur = self.tree.focus(); vals = self.tree.item(cur,"values")
        if len(vals)>=4 and vals[3]: webbrowser.open(vals[3])

if __name__ == "__main__":
    App().mainloop()