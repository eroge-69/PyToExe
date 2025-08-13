# -*- coding: utf-8 -*-
import os, smtplib, mimetypes, time, csv, io, re, json, threading, uuid, socket, ssl, tempfile, shutil, string, random, datetime
from email.message import EmailMessage
from email.utils import formataddr
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from PIL import Image
import imgkit  # requires wkhtmltoimage installed

load_dotenv()

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(APP_DIR, "state")
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
TMP_DIR = os.path.join(STATE_DIR, "tmp")
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

CAMPAIGNS = {}
LOCK = threading.Lock()

def safe_int(v, default=0):
    try: return int(v)
    except Exception: return default

def decode_bytes(b):
    if isinstance(b, (bytes, bytearray)):
        try: return b.decode("utf-8", errors="ignore")
        except Exception: return str(b)
    return str(b)

def classify_smtp_error(exc):
    import smtplib, socket, ssl
    code = None; msg = ""
    if isinstance(exc, smtplib.SMTPResponseException):
        code = getattr(exc, "smtp_code", None)
        msg = decode_bytes(getattr(exc, "smtp_error", ""))
    else:
        msg = str(exc)
    reason = "unknown_error"
    if code:
        if 400 <= code < 500:
            if code in (421, 450, 451, 452): reason = "temporary_failure"
            else: reason = "transient_error"
        elif 500 <= code < 600:
            if code in (550, 551, 552):
                if "user unknown" in msg.lower() or "no such" in msg.lower() or "recipient address rejected" in msg.lower():
                    reason = "mailbox_not_found"
                elif "quota" in msg.lower() or "exceeded" in msg.lower():
                    reason = "mailbox_full"
                else:
                    reason = "recipient_rejected"
            elif code in (553, 554):
                if "spam" in msg.lower() or "policy" in msg.lower() or "blocked" in msg.lower():
                    reason = "policy_blocked"
                else:
                    reason = "content_rejected"
            else:
                reason = "permanent_error"
        else:
            reason = "smtp_error"
    else:
        low = msg.lower()
        if isinstance(exc, (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected)):
            reason = "connection_error"
        elif isinstance(exc, (smtplib.SMTPAuthenticationError,)):
            reason = "auth_error"
        elif "timed out" in low or isinstance(exc, (socket.timeout, ssl.SSLError)):
            reason = "timeout"
        else:
            reason = "network_error" if any(k in low for k in ["network", "connection", "dns"]) else "unknown_error"
    return code, msg, reason

def random_token(n=15, alphabet=None):
    alphabet = alphabet or (string.ascii_uppercase + string.digits)
    return ''.join(random.choice(alphabet) for _ in range(n))

def imgkit_config():
    path = os.environ.get("WKHTMLTOIMAGE_PATH")
    if path and os.path.exists(path):
        return imgkit.config(wkhtmltoimage=path)
    return imgkit.config()

def render_html_to_jpg(html_str, out_jpg_path, width=800, height=1100, quality=92):
    cfg = imgkit_config()
    options = {
        "format": "jpg",
        "quality": str(int(quality)),
        "width": str(int(width)),
        "height": str(int(height)),
        "encoding": "UTF-8",
        "disable-smart-width": ""
    }
    imgkit.from_string(html_str, out_jpg_path, options=options, config=cfg)

def jpg_to_pdf(jpg_path, pdf_path):
    im = Image.open(jpg_path).convert("RGB")
    im.save(pdf_path, "PDF", resolution=300.0)

def html_to_pdf_via_jpg(html_str, out_pdf_path, width=800, height=1100, quality=92):
    tmp = tempfile.mkdtemp(dir=TMP_DIR)
    jpg_path = os.path.join(tmp, "page.jpg")
    try:
        render_html_to_jpg(html_str, jpg_path, width=width, height=height, quality=quality)
        jpg_to_pdf(jpg_path, out_pdf_path)
    finally:
        try: shutil.rmtree(tmp, ignore_errors=True)
        except Exception: pass

# -------- Tag system --------
NAME_POOL = [
    "Alex","Taylor","Jordan","Casey","Riley","Avery","Jamie","Morgan","Quinn","Cameron",
    "Reese","Rowan","Skyler","Parker","Hayden","Dakota","Blake","Drew","Elliot","Emerson"
]
STREET_POOL = [
    "108 Hemway Center", "3356 Leon Keys Suite 431", "72 Meadowbrook Rd", "4198 Valley View Ave",
    "12 Cypress Court", "980 Maple Hollow Dr", "1569 Oakridge Blvd"
]
CITY_POOL = [
    ("Shawton","WY","88912"), ("Austin","TX","78701"), ("San Mateo","CA","94401"),
    ("Lakewood","CO","80226"), ("Madison","WI","53703"), ("Tampa","FL","33602")
]

def rand_full_address():
    street = random.choice(STREET_POOL)
    city, st, zipc = random.choice(CITY_POOL)
    return f"{street}\n{city}, {st} {zipc}"

def gen_numeric(min_len, max_len):
    n = random.randint(min_len, max_len)
    first = random.choice("123456789")
    rest = ''.join(random.choice(string.digits) for _ in range(n-1)) if n>1 else ""
    return first+rest

def gen_alpha(pool, min_len, max_len):
    n = random.randint(min_len, max_len)
    return ''.join(random.choice(pool) for _ in range(n))

def expand_tags(text, row, tfn="", body_for_html=None):
    if not text: return text
    now = datetime.datetime.now()
    rep = {
        "#EMAIL#": row.get("email",""),
        "#NAME#": (row.get("name") or random.choice(NAME_POOL)),
        "#FNAME#": random.choice(NAME_POOL),
        "#UNAME#": f"{random.choice(NAME_POOL)[0]}. {random.choice(NAME_POOL)}",
        "#DATE#": now.strftime("%d %B, %Y"),
        "#DATE1#": now.strftime("%d/%m/%Y"),
        "#DATETIME#": now.strftime("%d %b, %Y %H:%M:%S"),
        "#INV#": f"INV-{gen_alpha(string.ascii_uppercase,8,12)}-{gen_numeric(5,8)}-{gen_alpha(string.ascii_uppercase,4,6)}",
        "#SNUM#": gen_numeric(5,10),
        "#LNUM#": gen_numeric(10,15),
        "#SMLETT#": gen_alpha(string.ascii_letters+string.digits,10,15),
        "#LMLETT#": gen_alpha(string.ascii_letters+string.digits,20,30),
        "#SCLETT#": gen_alpha(string.ascii_uppercase,10,15),
        "#LCLETT#": gen_alpha(string.ascii_uppercase,20,30),
        "#SLETT#": gen_alpha(string.ascii_lowercase,10,15),
        "#LLETT#": gen_alpha(string.ascii_lowercase,20,30),
        "#UKEY#": uuid.uuid4().hex,
        "#TRX#": gen_alpha(string.ascii_uppercase+string.digits,35,40),
        "#ADDRESS#": random.choice(STREET_POOL),
        "#FADDRESS#": rand_full_address(),
        "#TFN#": tfn or "",
    }
    if body_for_html is not None:
        rep["#CONTENT#"] = body_for_html
    for k,v in rep.items():
        text = text.replace(k, str(v))
    return text

# -------- App --------
def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", 20 * 1024 * 1024))

    @app.route("/health")
    def health():
        return "ok"

    @app.route("/", methods=["GET"])
    def index():
        defaults = {
            "smtp_host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": os.environ.get("SMTP_PORT", "587"),
            "smtp_user": os.environ.get("SMTP_USER", ""),
            "smtp_pass": os.environ.get("SMTP_PASS", ""),
            "use_tls": os.environ.get("USE_TLS", "1"),
            "use_ssl": os.environ.get("USE_SSL", "0"),
            "reply_to": os.environ.get("REPLY_TO", ""),
            "wkhtmltoimage_hint": os.environ.get("WKHTMLTOIMAGE_PATH", ""),
        }
        drafts = load_all_drafts()
        return render_template("index.html", defaults=defaults, drafts=drafts)

    def draft_path(tab): return os.path.join(STATE_DIR, f"draft_tab{tab}.json")
    def load_draft(tab):
        p = draft_path(tab)
        if not os.path.exists(p): return {}
        try:
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}
    def load_all_drafts(): return {i: load_draft(i) for i in range(1,4)}
    def save_draft(tab, data):
        with open(draft_path(tab), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @app.route("/save-draft/<int:tab>", methods=["POST"])
    def save_draft_endpoint(tab):
        data = request.get_json(silent=True) or {}
        save_draft(tab, data)
        return jsonify({"ok": True})

    import csv, io
    def parse_txt_string(s):
        res = []
        for line in s.splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            m = re.search(r"<([^>]+)>", line)
            name, email = "", ""
            if m and "@" in m.group(1):
                email = m.group(1).strip()
                name = re.sub(r"<[^>]+>", "", line).strip().strip(",")
            else:
                if "," in line and "@" in line:
                    parts = [p.strip() for p in line.split(",")]
                    for p in parts:
                        if "@" in p: email = p; break
                    name = (parts[0] if parts and "@" not in parts[0] else "")
                else:
                    toks = re.split(r"\s+", line)
                    for t in toks:
                        if "@" in t:
                            email = t.strip().strip("<>,"); break
                    name = " ".join([t for t in toks if "@" not in t]).strip(" ,")
            if email: res.append({"email": email, "name": name})
        return res

    def parse_uploaded_content(filename, raw):
        try: s = raw.decode("utf-8")
        except UnicodeDecodeError: s = raw.decode("latin-1", errors="ignore")
        if filename.lower().endswith(".csv"):
            reader = csv.DictReader(io.StringIO(s)); rows = []
            for row in reader:
                norm = { (k or '').strip().lower(): (v or '').strip() for k,v in row.items() }
                if 'email' in norm and norm['email']: rows.append(norm)
            if rows: return rows
            io_rows = csv.reader(io.StringIO(s)); out = []
            for parts in io_rows:
                if not parts: continue
                email = ""; name = ""
                for p in parts:
                    p = (p or "").strip()
                    if "@" in p and not email: email = p
                    elif p and not name: name = p
                if email: out.append({"email": email, "name": name})
            return out
        else:
            return parse_txt_string(s)

    def make_recipients(to_emails_raw, uploaded_rows, suppression_set):
        recipients = []
        if to_emails_raw:
            for e in re.split(r"[,;\s]+", to_emails_raw):
                e = e.strip()
                if e and "@" in e: recipients.append({"email": e, "name": ""})
        recipients.extend(uploaded_rows or [])
        unique = {}
        for r in recipients:
            email = (r.get("email") or "").lower().strip()
            if not email: continue
            if email in suppression_set: continue
            if email not in unique or (not unique[email].get("name") and r.get("name")):
                unique[email] = {"email": r.get("email",""), "name": r.get("name","")}
        return list(unique.values())

    def read_suppression(raw, filename=""):
        sset = set()
        if not raw: return sset
        try: data = raw.decode("utf-8")
        except UnicodeDecodeError: data = raw.decode("latin-1", errors="ignore")
        if filename.lower().endswith(".csv"):
            reader = csv.DictReader(io.StringIO(data))
            for row in reader:
                em = (row.get("email","") or "").strip().lower()
                if em: sset.add(em)
        else:
            for line in data.splitlines():
                line = line.strip()
                if "@" in line:
                    m = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', line)
                    if m: sset.add(m.group(1).lower())
        return sset

    def save_campaign_meta(meta):
        path = os.path.join(STATE_DIR, f"{meta['id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    def load_campaign_meta(cid):
        path = os.path.join(STATE_DIR, f"{cid}.json")
        if not os.path.exists(path): return None
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    def append_result_csv(meta):
        csv_path = os.path.join(STATE_DIR, f"{meta['id']}_results.csv")
        new = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new: w.writerow(["email","status","reason","smtp_code","error"])
            last = meta["results"][-1]
            w.writerow([last.get("email"), last.get("status"), last.get("reason"), last.get("smtp_code"), last.get("error")])

    def build_meta_from_tab(tab_id, recipients_override=None):
        port_raw = request.form.get(f"smtp_port_{tab_id}") or request.form.get("smtp_port") or "0"
        smtp_port = safe_int(port_raw, 0)
        smtp_host = (request.form.get(f"smtp_host_{tab_id}") or request.form.get("smtp_host") or "").strip()
        smtp_user = (request.form.get(f"smtp_user_{tab_id}") or request.form.get("smtp_user") or "").strip()
        smtp_pass = (request.form.get(f"smtp_pass_{tab_id}") or request.form.get("smtp_pass") or "").strip()
        use_tls = (request.form.get(f"use_tls_{tab_id}") == "on")
        use_ssl = (request.form.get(f"use_ssl_{tab_id}") == "on")
        from_email = (request.form.get(f"from_email_{tab_id}") or "").strip()
        from_name = (request.form.get(f"from_name_{tab_id}") or "").strip()
        reply_to = (request.form.get(f"reply_to_{tab_id}") or "").strip()
        subject_tpl = (request.form.get(f"subject_{tab_id}") or "").strip()
        body_tpl = request.form.get(f"body_{tab_id}") or ""
        send_as_html = (request.form.get(f"send_as_html_{tab_id}") == "on")
        pause_seconds = float((request.form.get(f"pause_seconds_{tab_id}") or "0") or 0)
        unsub_mailto = (request.form.get(f"unsub_mailto_{tab_id}") or "").strip()
        unsub_url = (request.form.get(f"unsub_url_{tab_id}") or "").strip()
        tfn = (request.form.get(f"tfn_{tab_id}") or "").strip()

        gen_pdf = (request.form.get(f"gen_pdf_{tab_id}") == "on")
        html_tpl = request.form.get(f"html_tpl_{tab_id}") or ""
        html_width = safe_int(request.form.get(f"html_width_{tab_id}") or 800, 800)
        html_height = safe_int(request.form.get(f"html_height_{tab_id}") or 1100, 1100)
        html_quality = safe_int(request.form.get(f"html_quality_{tab_id}") or 92, 92)

        cid = uuid.uuid4().hex[:10]
        meta = {
            "id": cid, "tab_id": tab_id, "created_ts": time.time(),
            "status": "queued", "error": "",
            "smtp_host": smtp_host, "smtp_port": smtp_port,
            "smtp_user": smtp_user, "smtp_pass": smtp_pass,
            "use_tls": use_tls, "use_ssl": use_ssl,
            "from_email": from_email, "from_name": from_name, "reply_to": reply_to,
            "subject_tpl": subject_tpl, "body_tpl": body_tpl, "tfn": tfn,
            "send_as_html": send_as_html, "pause_seconds": pause_seconds,
            "unsub_mailto": unsub_mailto, "unsub_url": unsub_url,
            "recipients": recipients_override or [], "total": len(recipients_override or []),
            "current": 0, "sent": 0, "failed": 0, "results": [],
            "upload_files": request.files.getlist(f"attachments_{tab_id}"),
            "gen_pdf": gen_pdf, "html_tpl": html_tpl,
            "html_width": html_width, "html_height": html_height, "html_quality": html_quality,
        }
        return meta

    def validate_required(tab_id):
        port_raw = request.form.get(f"smtp_port_{tab_id}") or request.form.get("smtp_port") or ""
        smtp_host = (request.form.get(f"smtp_host_{tab_id}") or request.form.get("smtp_host") or "").strip()
        from_email = (request.form.get(f"from_email_{tab_id}") or "").strip()
        if not smtp_host: return False, "SMTP host required."
        if not port_raw or safe_int(port_raw, 0) <= 0: return False, "Valid SMTP port required."
        if not from_email: return False, "From address required."
        return True, ""

    def add_unsub_headers(msg, meta):
        lh = []
        if meta.get("unsub_mailto"): lh.append(f"<mailto:{meta['unsub_mailto']}>")
        if meta.get("unsub_url"):
            lh.append(f"<{meta['unsub_url']}>")
            msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        if lh: msg["List-Unsubscribe"] = ", ".join(lh)

    def campaign_thread(meta):
        cid = meta["id"]
        with LOCK:
            CAMPAIGNS[cid] = {"status":"running","current":meta.get("current",0),"stop":False,"pause":False}
        inmem_attachments = []
        try:
            files = meta.get("attachments", [])
            for filename in files:
                full = os.path.join(APP_DIR, filename)
                if not os.path.exists(full): continue
                with open(full, "rb") as fh:
                    file_bytes = fh.read()
                ctype, _ = mimetypes.guess_type(filename)
                if ctype is None: maintype, subtype = "application", "octet-stream"
                else: maintype, subtype = ctype.split("/", 1)
                inmem_attachments.append((file_bytes, maintype, subtype, os.path.basename(filename)))
        except Exception as e:
            meta["status"] = "error"; meta["error"] = str(e); save_campaign_meta(meta); return

        try:
            if meta.get("use_ssl"):
                server = smtplib.SMTP_SSL(meta["smtp_host"], meta["smtp_port"], timeout=60)
            else:
                server = smtplib.SMTP(meta["smtp_host"], meta["smtp_port"], timeout=60)
            with server as smtp:
                smtp.ehlo()
                if meta.get("use_tls"): smtp.starttls(); smtp.ehlo()
                if meta.get("smtp_user") or meta.get("smtp_pass"): smtp.login(meta.get("smtp_user",""), meta.get("smtp_pass",""))
                total = len(meta["recipients"])
                while meta["current"] < total:
                    with LOCK:
                        st = CAMPAIGNS.get(cid, {})
                        if st.get("stop"):
                            meta["status"] = "stopped"; save_campaign_meta(meta); return
                        while st.get("pause"):
                            time.sleep(0.5); st = CAMPAIGNS.get(cid, {})

                    r = meta["recipients"][meta["current"]]
                    row = {k:v for k,v in r.items()}

                    repl = lambda m: str(row.get(m.group(1).strip().lower(), ""))
                    subject = re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, meta["subject_tpl"] or "")
                    body = re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, meta["body_tpl"] or "")

                    subject = expand_tags(subject, row, tfn=meta.get("tfn",""))
                    body_expanded = expand_tags(body, row, tfn=meta.get("tfn",""))

                    msg = EmailMessage()
                    if meta.get("from_name"):
                        msg["From"] = formataddr((meta["from_name"], meta["from_email"]))
                    else:
                        msg["From"] = meta["from_email"]
                    msg["To"] = r["email"]
                    msg["Subject"] = subject or "(no subject)"
                    if meta.get("reply_to"): msg["Reply-To"] = meta["reply_to"]
                    msg["X-Mailer"] = "CompliantMailer/3.0"
                    add_unsub_headers(msg, meta)

                    if meta.get("send_as_html"):
                        plain = re.sub("<[^>]+>", "", body_expanded or "")
                        msg.set_content(plain or " ")
                        msg.add_alternative(body_expanded or "<p>(empty)</p>", subtype="html")
                    else:
                        msg.set_content(body_expanded or " ")

                    for (file_bytes, maintype, subtype, filename) in inmem_attachments:
                        msg.add_attachment(file_bytes, maintype=maintype, subtype=subtype, filename=filename)

                    if meta.get("gen_pdf") and (meta.get("html_tpl") or "").strip():
                        html_raw = re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, meta.get("html_tpl") or "")
                        content_html = body_expanded if meta.get("send_as_html") else (body_expanded or "").replace("\n","<br>")
                        html = expand_tags(html_raw, row, tfn=meta.get("tfn",""), body_for_html=content_html)
                        if "<html" not in html.lower():
                            html = f"<html><head><meta charset='utf-8'></head><body>{html}</body></html>"
                        rnd = random_token(15)
                        tmp_pdf = os.path.join(TMP_DIR, f"{cid}_{meta['current']+1}_{rnd}.pdf")
                        try:
                            html_to_pdf_via_jpg(html, tmp_pdf, width=meta.get('html_width',800), height=meta.get('html_height',1100), quality=meta.get('html_quality',92))
                            attach_name = f"{rnd}.pdf"
                            with open(tmp_pdf, "rb") as fh:
                                fb = fh.read()
                            msg.add_attachment(fb, maintype="application", subtype="pdf", filename=attach_name)
                        except Exception as gen_err:
                            meta["results"].append({"email": r["email"], "status": "mail nosto", "reason":"html_pdf_generation_failed", "smtp_code": None, "error": str(gen_err)})
                            meta["current"] += 1; meta["failed"] += 1
                            save_campaign_meta(meta); append_result_csv(meta)
                            continue

                    ok = True; err = ""; code = None; reason = "sent"
                    try:
                        smtp.send_message(msg)
                    except Exception as e:
                        ok = False
                        code, err, reason = classify_smtp_error(e)

                    meta["results"].append({
                        "email": r["email"],
                        "status": "sent" if ok else "mail nosto",
                        "reason": reason,
                        "smtp_code": code,
                        "error": err
                    })
                    meta["current"] += 1
                    if ok: meta["sent"] += 1
                    else: meta["failed"] += 1
                    save_campaign_meta(meta); append_result_csv(meta)

                    if meta.get("pause_seconds", 0) and meta["current"] < total:
                        time.sleep(float(meta["pause_seconds"]))

                meta["status"] = "completed"; save_campaign_meta(meta)
        except Exception as e:
            meta["status"] = "error"; meta["error"] = str(e); save_campaign_meta(meta)

    def status_payload(meta):
        reasons = {}
        for r in meta.get("results", []):
            if r.get("status") == "mail nosto":
                key = r.get("reason","unknown_error")
                reasons[key] = reasons.get(key, 0) + 1
        pct = int((meta.get("current",0) / max(1, meta.get("total",1))) * 100)
        payload = {
            "id": meta["id"], "status": meta.get("status","unknown"),
            "current": meta.get("current",0), "total": meta.get("total",0),
            "sent": meta.get("sent",0), "failed": meta.get("failed",0),
            "percent": pct, "error": meta.get("error",""),
            "last": (meta.get("results") or [])[-1] if meta.get("results") else None,
            "reasons": reasons
        }
        return payload

    def start_campaign(meta):
        saved_files = []
        for f in meta.get("upload_files", []):
            filename = secure_filename(f.filename)
            if not filename: continue
            dest = os.path.join("uploads", f"{meta['id']}_{filename}")
            full_dest = os.path.join(APP_DIR, dest)
            f.save(full_dest)
            saved_files.append(dest)
        meta["attachments"] = saved_files
        if "upload_files" in meta: del meta["upload_files"]
        save_campaign_meta(meta)
        t = threading.Thread(target=campaign_thread, args=(meta,), daemon=True)
        t.start()
        with LOCK:
            CAMPAIGNS[meta["id"]] = {"status":"running","current":meta.get("current",0),"stop":False,"pause":False}

    @app.route("/start", methods=["POST"])
    def start():
        tab_id = int(request.form.get("tab_id", "1") or 1)
        ok, msg = validate_required(tab_id)
        if not ok: return jsonify({"ok": False, "error": msg}), 400

        suppression = set()
        sup_file = request.files.get(f"suppression_file_{tab_id}")
        if sup_file and sup_file.filename:
            suppression = read_suppression(sup_file.read(), sup_file.filename)

        uploaded_rows = []
        rec_file = request.files.get(f"recipient_file_{tab_id}")
        if rec_file and rec_file.filename:
            raw = rec_file.read()
            uploaded_rows = parse_uploaded_content(rec_file.filename, raw)

        to_emails_raw = request.form.get(f"to_emails_{tab_id}", "").strip()
        recipients = make_recipients(to_emails_raw, uploaded_rows, suppression)
        if not recipients: return jsonify({"ok": False, "error": "No recipients found after suppression."}), 400

        meta = build_meta_from_tab(tab_id, recipients_override=recipients)
        start_campaign(meta)
        return jsonify({"ok": True, "cid": meta["id"]})

    @app.route("/status/<cid>", methods=["GET"])
    def status(cid):
        meta = load_campaign_meta(cid)
        if not meta: return jsonify({"error":"not found"}), 404
        return jsonify(status_payload(meta))

    @app.route("/control/<cid>", methods=["POST"])
    def control(cid):
        action = request.form.get("action","")
        with LOCK:
            st = CAMPAIGNS.setdefault(cid, {"status":"unknown","pause":False,"stop":False})
            if action == "pause": st["pause"] = True
            elif action == "resume": st["pause"] = False
            elif action == "stop": st["stop"] = True
        return jsonify({"ok": True, "action": action})

    @app.route("/results/<cid>.csv", methods=["GET"])
    def results_csv(cid):
        path = os.path.join(STATE_DIR, f"{cid}_results.csv")
        if not os.path.exists(path):
            meta = load_campaign_meta(cid)
            if meta and meta.get("results"):
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f); w.writerow(["email","status","reason","smtp_code","error"])
                    for r in meta["results"]:
                        w.writerow([r.get("email"), r.get("status"), r.get("reason"), r.get("smtp_code"), r.get("error")])
        if not os.path.exists(path): return "No results yet.", 404
        return send_file(path, as_attachment=True, download_name=f"{cid}_results.csv")

    @app.route("/gen-preview", methods=["POST"])
    def gen_preview():
        tab_id = int(request.form.get("tab_id","1") or 1)
        html_raw = request.form.get(f"html_tpl_{tab_id}") or ""
        if not html_raw.strip():
            return jsonify({"ok": False, "error": "HTML is empty."}), 400
        row = {"email":"preview@example.com","name":"Preview User"}
        body = (request.form.get(f"body_{tab_id}") or "").strip() or "Sample body"
        send_as_html = (request.form.get(f"send_as_html_{tab_id}") == "on")
        content_html = body if send_as_html else body.replace("\n","<br>")
        html_tmp = re.sub(r"\{\{\s*([^}]+)\s*\}\}", lambda m: str(row.get(m.group(1).strip().lower(), "")), html_raw)
        html = expand_tags(html_tmp, row, tfn=request.form.get(f"tfn_{tab_id}") or "", body_for_html=content_html)
        if "<html" not in html.lower():
            html = f"<html><head><meta charset='utf-8'></head><body>{html}</body></html>"
        width = safe_int(request.form.get(f"html_width_{tab_id}") or 800, 800)
        height = safe_int(request.form.get(f"html_height_{tab_id}") or 1100, 1100)
        quality = safe_int(request.form.get(f"html_quality_{tab_id}") or 92, 92)
        rnd = random_token(15)
        tmp_pdf = os.path.join(TMP_DIR, f"preview_{rnd}.pdf")
        try:
            html_to_pdf_via_jpg(html, tmp_pdf, width=width, height=height, quality=quality)
            return send_file(tmp_pdf, as_attachment=True, download_name=f"preview_{rnd}.pdf")
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 200

    @app.route("/test-send", methods=["POST"])
    def test_send():
        tab_id = int(request.form.get("tab_id","1") or 1)
        port_raw = request.form.get(f"smtp_port_{tab_id}") or request.form.get("smtp_port") or ""
        smtp_host = (request.form.get(f"smtp_host_{tab_id}") or request.form.get("smtp_host") or "").strip()
        from_email = (request.form.get(f"from_email_{tab_id}") or "").strip()
        if not smtp_host or not port_raw or safe_int(port_raw,0)<=0 or not from_email:
            return jsonify({"ok": False, "error": "SMTP host/port and From address required."}), 400
        test_to = (request.form.get(f"test_to_{tab_id}") or "").strip()
        if not test_to or "@" not in test_to:
            return jsonify({"ok": False, "error": "Valid test recipient required."}), 400

        meta = build_meta_from_tab(tab_id, recipients_override=[{"email": test_to, "name": ""}])
        r = meta["recipients"][0]
        row = r; repl = lambda m: str(row.get(m.group(1).strip().lower(), ""))
        subject = re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, meta.get("subject_tpl") or "")
        body = re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, meta.get("body_tpl") or "")
        subject = expand_tags(subject, row, tfn=meta.get("tfn",""))
        body = expand_tags(body, row, tfn=meta.get("tfn",""))

        try:
            msg = EmailMessage()
            if meta.get("from_name"): msg["From"] = formataddr((meta["from_name"], meta["from_email"]))
            else: msg["From"] = meta["from_email"]
            msg["To"] = r["email"]
            msg["Subject"] = subject or "(no subject)"
            if meta.get("reply_to"): msg["Reply-To"] = meta["reply_to"]
            msg["X-Mailer"] = "CompliantMailer/3.0"
            if meta.get("send_as_html"):
                plain = re.sub("<[^>]+>", "", body or "")
                msg.set_content(plain or " ")
                msg.add_alternative(body or "<p>(empty)</p>", subtype="html")
            else:
                msg.set_content(body or " ")

            for f in meta.get("upload_files", []):
                filename = secure_filename(f.filename)
                if not filename: continue
                data = f.read()
                ctype, _ = mimetypes.guess_type(filename)
                if ctype is None: maintype, subtype = "application", "octet-stream"
                else: maintype, subtype = ctype.split("/", 1)
                msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

            if meta.get("gen_pdf") and (meta.get("html_tpl") or "").strip():
                html_raw = re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, meta.get("html_tpl") or "")
                content_html = body if meta.get("send_as_html") else (body or "").replace("\n","<br>")
                html = expand_tags(html_raw, row, tfn=meta.get("tfn",""), body_for_html=content_html)
                if "<html" not in html.lower():
                    html = f"<html><head><meta charset='utf-8'></head><body>{html}</body></html>"
                rnd = random_token(15)
                tmp_pdf = os.path.join(TMP_DIR, f"test_{rnd}.pdf")
                html_to_pdf_via_jpg(html, tmp_pdf, width=meta.get('html_width',800), height=meta.get('html_height',1100), quality=meta.get('html_quality',92))
                with open(tmp_pdf, "rb") as fh:
                    fb = fh.read()
                msg.add_attachment(fb, maintype="application", subtype="pdf", filename=f"{rnd}.pdf")

            port = safe_int(port_raw, 0)
            if meta.get("use_ssl"):
                server = smtplib.SMTP_SSL(smtp_host, port, timeout=60)
            else:
                server = smtplib.SMTP(smtp_host, port, timeout=60)
            with server as smtp:
                smtp.ehlo()
                if meta.get("use_tls"): smtp.starttls(); smtp.ehlo()
                if meta.get("smtp_user") or meta.get("smtp_pass"): smtp.login(meta.get("smtp_user",""), meta.get("smtp_pass",""))
                smtp.send_message(msg)
            return jsonify({"ok": True})
        except Exception as e:
            code, emsg, reason = classify_smtp_error(e)
            return jsonify({"ok": False, "error": emsg, "reason": reason, "smtp_code": code}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
