import os
import argparse
import mimetypes
from datetime import datetime
from urllib.parse import quote
from flask import Flask, request, send_from_directory, abort, Response, redirect

app = Flask(__name__)
SHARE_DIR = os.getcwd()
REQUIRE_KEY = None
TITLE = "Self Hoster"
ALLOW_BROWSE_PARENT = False

def format_bytes(num: int) -> str:
    for unit in ["B","KB","MB","GB","TB"]:
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"

def html_escape(s: str) -> str:
    return (s.replace("&","&amp;")
             .replace("<","&lt;")
             .replace(">","&gt;")
             .replace('"',"&quot;")
             .replace("'","&#39;"))

def gate_ok(req: request) -> bool:
    if not REQUIRE_KEY:
        return True
    # allow ?key=... or header X-Access-Key: ...
    key = req.args.get("key") or req.headers.get("X-Access-Key")
    return key == REQUIRE_KEY

@app.before_request
def protect():
    if gate_ok(request):
        return
    # Show a tiny lock screen
    return Response("""<!doctype html>
<html><head><meta charset="utf-8"><title>Locked</title>
<style>body{font-family:system-ui,Segoe UI,Arial;margin:2rem}form{display:flex;gap:.5rem}</style></head>
<body><h2>🔒 Access Key Required</h2>
<form method="get"><input name="key" placeholder="Enter key" autofocus>
<button>Unlock</button></form></body></html>""", status=401, mimetype="text/html")

@app.route("/")
def index():
    base = SHARE_DIR
    if not os.path.isdir(base):
        abort(404)

    rows = []
    # Optional link to parent (disabled by default for safety)
    if ALLOW_BROWSE_PARENT:
        rows.append(f'<tr><td colspan="4"><a href="/tree?path={quote("..")}">⬆️ Parent</a></td></tr>')

    # Top-level listing
    for name in sorted(os.listdir(base), key=str.lower):
        full = os.path.join(base, name)
        try:
            st = os.stat(full)
        except OSError:
            continue
        is_dir = os.path.isdir(full)
        size = "-" if is_dir else format_bytes(st.st_size)
        when = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
        if is_dir:
            href = f"/tree?path={quote(name)}"
            link = f'<a href="{href}">📁 {html_escape(name)}</a>'
        else:
            href = f"/download/{quote(name)}"
            link = f'<a href="{href}">⬇️ {html_escape(name)}</a>'
        rows.append(f"<tr><td>{link}</td><td>{size}</td><td>{when}</td><td>{'Folder' if is_dir else (mimetypes.guess_type(name)[0] or 'file')}</td></tr>")

    key_hint = f"&key={quote(REQUIRE_KEY)}" if REQUIRE_KEY else ""
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>{html_escape(TITLE)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:system-ui,Segoe UI,Arial;margin:24px;max-width:1100px}}
h1{{margin:0 0 8px}}
table{{width:100%;border-collapse:collapse;margin-top:12px}}
th,td{{padding:8px 10px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}}
tr:hover td{{background:#fafafa}}
.small{{color:#666;font-size:.9em}}
.header{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}}
.badge{{background:#efefef;padding:2px 8px;border-radius:999px}}
</style></head>
<body>
<div class="header">
  <h1>{html_escape(TITLE)}</h1>
  <div class="small">Serving: <span class="badge">{html_escape(os.path.abspath(base))}</span></div>
</div>

<table>
  <thead><tr><th>Name</th><th>Size</th><th>Modified</th><th>Type</th></tr></thead>
  <tbody>
    {''.join(rows) if rows else '<tr><td colspan="4"><em>(empty)</em></td></tr>'}
  </tbody>
</table>

<div class="small" style="margin-top:16px;">
  Tip: you can also browse subfolders at <code>/tree?path=&lt;folder&gt;{key_hint}</code>
</div>
</body></html>"""

@app.route("/tree")
def tree():
    rel = request.args.get("path","").strip().replace("\\","/")
    # Normalise and keep inside share dir
    safe = os.path.normpath(os.path.join(SHARE_DIR, rel))
    if not safe.startswith(os.path.abspath(SHARE_DIR)):
        abort(403)
    if not os.path.isdir(safe):
        abort(404)

    rows = []
    # Add parent link
    rel_parent = os.path.relpath(os.path.join(safe, ".."), SHARE_DIR)
    if rel_parent != ".":
        rows.append(f'<tr><td colspan="4"><a href="/tree?path={quote(rel_parent)}">⬆️ Parent</a></td></tr>')
    else:
        rows.append(f'<tr><td colspan="4"><a href="/">🏠 Home</a></td></tr>')

    for name in sorted(os.listdir(safe), key=str.lower):
        full = os.path.join(safe, name)
        try:
            st = os.stat(full)
        except OSError:
            continue
        is_dir = os.path.isdir(full)
        size = "-" if is_dir else format_bytes(st.st_size)
        when = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
        rel_child = os.path.relpath(full, SHARE_DIR).replace("\\","/")
        if is_dir:
            href = f"/tree?path={quote(rel_child)}"
            link = f'<a href="{href}">📁 {html_escape(name)}</a>'
        else:
            href = f"/download/{quote(rel_child)}"
            link = f'<a href="{href}">⬇️ {html_escape(name)}</a>'
        rows.append(f"<tr><td>{link}</td><td>{size}</td><td>{when}</td><td>{'Folder' if is_dir else (mimetypes.guess_type(name)[0] or 'file')}</td></tr>")

    return f"""<!doctype html><meta charset="utf-8">
<title>Browse – {html_escape(TITLE)}</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial;margin:24px;max-width:1100px}}
table{{width:100%;border-collapse:collapse;margin-top:12px}}
th,td{{padding:8px 10px;border-bottom:1px solid #eee;text-align:left}}
tr:hover td{{background:#fafafa}}
.small{{color:#666;font-size:.9em}}
</style>
<h2>📂 {html_escape(os.path.relpath(safe, SHARE_DIR))}</h2>
<table>
  <thead><tr><th>Name</th><th>Size</th><th>Modified</th><th>Type</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<div class="small" style="margin-top:16px;"><a href="/">🏠 Back to root</a></div>
"""

@app.route("/download/<path:relpath>")
def download(relpath):
    # Normalise and ensure path stays inside share dir
    safe = os.path.normpath(os.path.join(SHARE_DIR, relpath))
    if not safe.startswith(os.path.abspath(SHARE_DIR)):
        abort(403)
    if not os.path.isfile(safe):
        abort(404)
    dirpart = os.path.dirname(os.path.relpath(safe, SHARE_DIR))
    filename = os.path.basename(safe)
    directory = os.path.join(SHARE_DIR, dirpart) if dirpart != "." else SHARE_DIR
    return send_from_directory(directory, filename, as_attachment=True)

def main():
    global SHARE_DIR, REQUIRE_KEY, TITLE, ALLOW_BROWSE_PARENT
    parser = argparse.ArgumentParser(description="Self-host a folder with downloadable links.")
    parser.add_argument("--dir", "-d", default=os.getcwd(), help="Folder to share (default: current directory)")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--title", "-t", default="Self Hoster", help="Page title")
    parser.add_argument("--key", default=os.environ.get("SELFHOSTER_KEY", ""), help="Optional access key (also read from env SELFHOSTER_KEY)")
    parser.add_argument("--allow-parent", action="store_true", help="Allow parent folder link on root")
    args = parser.parse_args()

    SHARE_DIR = os.path.abspath(args.dir)
    TITLE = args.title
    ALLOW_BROWSE_PARENT = bool(args.allow_parent)
    REQUIRE_KEY = args.key if args.key else None

    if not os.path.isdir(SHARE_DIR):
        raise SystemExit(f"Not a directory: {SHARE_DIR}")

    print(f"[SelfHoster] Serving '{SHARE_DIR}' on http://127.0.0.1:{args.port}/")
    if REQUIRE_KEY:
        print("[SelfHoster] Access key enabled. Add ?key=YOUR_KEY to URLs or send header X-Access-Key: YOUR_KEY")
    app.run(host="0.0.0.0", port=args.port, threaded=True)

if __name__ == "__main__":
    main()
