#!/usr/bin/env python3
"""
acunetix_like_scanner_windows.py

Windows 10 friendly version of the Acunetix-like open-source scanner prototype.
This single-file tool keeps the same GUI layout but avoids Linux-only external
commands where possible. It will use pure-Python techniques (requests-based
crawling and heuristics) and *optionally* call nmap/nikto/whatweb/gobuster if
they are installed on Windows (or available via WSL) and present on PATH.

Important safety note: This tool is for authorized defensive testing only.
Do NOT scan systems you do not have explicit written permission to test.

Features for Windows:
- PySimpleGUI desktop GUI (works on Windows with Python 3.8+)
- Passive crawling and parameter discovery using `requests` + simple HTML parsing
- Optional Selenium screenshots (requires Chrome + matching chromedriver on PATH)
- Will call external tools (nmap/nikto/whatweb/gobuster) if they are installed
  and available in PATH (useful if you installed them on Windows or via WSL)
- Vulnerability-only HTML report export
- Local JSON storage in `%APPDATA%\ACUX_Lite` (Windows-friendly)
- Test harness accessible via `--test`

Dependencies on Windows 10 (recommended):
1. Install Python 3.10+ from python.org and check "Add Python to PATH" during
   installation.
2. Open CMD/PowerShell and install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install PySimpleGUI requests selenium weasyprint
   ```
3. Install Google Chrome and download a matching Chromedriver from
   https://chromedriver.chromium.org/ and put `chromedriver.exe` somewhere on PATH
   (for example C:\Windows or C:\tools\chromedriver). Alternatively use
   the `webdriver-manager` package to auto-download drivers.
4. Optional: Install nmap for Windows if you want to use nmap integration.

Packaging (optional): create an executable with PyInstaller:
```powershell
pip install pyinstaller
pyinstaller --onefile --windowed acunetix_like_scanner_windows.py
```

Run:
- GUI: `python acunetix_like_scanner_windows.py`
- Tests: `python acunetix_like_scanner_windows.py --test`

"""

from __future__ import annotations
import os
import sys
import json
import time
import threading
import queue
import html
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional

# GUI
try:
    import PySimpleGUI as sg
except Exception:
    print('Please install PySimpleGUI: python -m pip install PySimpleGUI')
    sys.exit(1)

# Networking
try:
    import requests
except Exception:
    requests = None

# Selenium (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False

# XML parser (optional for nmap output)
try:
    import xml.etree.ElementTree as ET
except Exception:
    ET = None

# Windows AppData storage
if os.name == 'nt':
    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
else:
    APPDATA = os.path.expanduser('~')

DATA_DIR = os.path.join(APPDATA, 'ACUX_Lite')
os.makedirs(DATA_DIR, exist_ok=True)
TARGETS_FILE = os.path.join(DATA_DIR, 'targets.json')
SCANS_FILE = os.path.join(DATA_DIR, 'scans.json')
CACHE_FILE = os.path.join(DATA_DIR, 'cache.json')

# Load helpers

def load_json(path: str, default: Any):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path: str, obj: Any):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=2)
    except Exception:
        pass

TARGETS = load_json(TARGETS_FILE, [])
SCANS = load_json(SCANS_FILE, [])
CACHE = load_json(CACHE_FILE, {})

# Tool catalog: commands are Windows/WSL-aware (but tool may not exist)
TOOL_CATALOG = {
    'nmap': 'nmap -sV -Pn -oX - {target}',
    'whatweb': 'whatweb --no-errors {target}',
    'nikto': 'nikto -h {target} -output -',
    'gobuster': 'gobuster dir -u {target} -w common.txt -q -e'
}

# Utilities

def now_ts() -> str:
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def sanitize(s: str) -> str:
    return html.escape(s or '')


def run_cmd(cmd: str, timeout: Optional[int] = None) -> (int, str, str):
    """Run shell/command. On Windows this runs through cmd.exe; on WSL the
    user can install tools and add them to PATH."""
    try:
        proc = __import__('subprocess').run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout or '', proc.stderr or ''
    except Exception as e:
        return -1, '', str(e)

# Lightweight HTTP fetch & passive parsers (pure-Python)

def fetch_url(url: str, timeout: int = 10) -> str:
    if not requests:
        return ''
    try:
        r = requests.get(url, timeout=timeout, verify=False)
        return r.text or ''
    except Exception:
        return ''


def extract_params_from_text(text: str) -> List[str]:
    params = set()
    # crude: find ?key= occurrences
    for idx in range(len(text)):
        if text[idx] == '?':
            seg = text[idx:idx+200]
            if '=' in seg:
                seg = seg.split()[0]
                for kv in seg.lstrip('?').split('&'):
                    if '=' in kv:
                        k = kv.split('=')[0]
                        if k:
                            params.add(k)
    return list(params)

# Screenshot helper using Chrome/Chromedriver (Windows-compatible)

def take_screenshot_datauri(url: str, timeout: int = 12) -> Optional[str]:
    key = f'ss:{url}'
    if key in CACHE:
        return CACHE[key]
    if not SELENIUM_AVAILABLE:
        return None
    driver = None
    try:
        options = ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # On Windows, chromedriver.exe must be on PATH or in the same dir
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        time.sleep(1.2)
        png = driver.get_screenshot_as_png()
        driver.quit()
        import base64
        b64 = base64.b64encode(png).decode('ascii')
        datauri = 'data:image/png;base64,' + b64
        CACHE[key] = datauri
        save_json(CACHE_FILE, CACHE)
        return datauri
    except Exception:
        try:
            if driver is not None:
                driver.quit()
        except Exception:
            pass
        return None

# Orchestrator: uses pure-Python checks and optionally external tools
class Orchestrator:
    def __init__(self, output_q: queue.Queue):
        self.output_q = output_q
        self.threads: List[threading.Thread] = []
        self.results: Dict[str, Any] = {}

    def start_scan(self, target: str, selected_tools: List[str], enable_screenshots: bool = False):
        self.results = {}
        for tool_key in selected_tools:
            self.results[tool_key] = {'cmd': '', 'output': '', 'rc': None, 'findings': [], 'screenshot': None}
            cmd_template = TOOL_CATALOG.get(tool_key)
            # if external tool present, run it; otherwise perform Python-based passive check
            def worker(tk=tool_key, tmpl=cmd_template):
                self.output_q.put(f'[STARTED] {tk}\n')
                if tmpl:
                    cmd = tmpl.format(target=target)
                    self.results[tk]['cmd'] = cmd
                    rc, out, err = run_cmd(cmd)
                    self.results[tk]['rc'] = rc
                    self.results[tk]['output'] = out + ('\nERR:\n' + err if err else '')
                    # If nmap xml, attempt to parse
                    if tk == 'nmap' and out.strip().startswith('<') and ET:
                        try:
                            root = ET.fromstring(out)
                            for port in root.findall('.//port'):
                                pid = port.attrib.get('portid')
                                proto = port.attrib.get('protocol')
                                svc = port.find('service')
                                svc_info = svc.attrib if svc is not None else {}
                                title = f'Open port {pid}/{proto} - {svc_info.get("name","")}'
                                self.results[tk]['findings'].append({'title': title, 'severity': 'info', 'description': str(svc_info)})
                        except Exception:
                            pass
                    else:
                        # fallback passive parsing
                        params = extract_params_from_text(out)
                        if params:
                            self.results[tk]['findings'].append({'title':'Discovered parameters','severity':'info','description':str(params)})
                else:
                    # pure-Python passive check: fetch the homepage and look for params
                    content = fetch_url(target)
                    if content:
                        self.results[tk]['output'] = content
                        params = extract_params_from_text(content)
                        if params:
                            self.results[tk]['findings'].append({'title':'Discovered parameters','severity':'info','description':str(params)})
                if enable_screenshots:
                    ss = take_screenshot_datauri(target)
                    if ss:
                        self.results[tk]['screenshot'] = ss
                        for f in self.results[tk]['findings']:
                            if (f.get('severity') or '').lower() != 'info':
                                f['screenshot'] = ss
                self.output_q.put(f'[DONE] {tk}\n')

            t = threading.Thread(target=worker, daemon=True)
            t.start()
            self.threads.append(t)

# Report generation (vulnerability-only)

def generate_vuln_report_html(target: str, results: Dict[str, Any]) -> str:
    title = f'Vulnerability Report — {sanitize(target)}'
    parts: List[str] = []
    parts.append('<!doctype html>')
    parts.append('<html><head><meta charset="utf-8"><title>' + sanitize(title) + '</title>')
    parts.append('<style>body{font-family:Arial;background:#f7f7fb;color:#111;padding:20px}.card{background:#fff;padding:12px;border-radius:6px;margin-bottom:12px;box-shadow:0 1px 2px rgba(0,0,0,0.05)}h1{color:#4b2b7f}</style>')
    parts.append('</head><body>')
    parts.append('<h1>' + sanitize(title) + '</h1>')
    parts.append('<p>Generated: ' + now_ts() + ' UTC</p>')
    vulns: List[Dict[str, Any]] = []
    for tk, data in results.items():
        for f in data.get('findings', []) or []:
            sev = (f.get('severity') or '').lower()
            if sev and sev != 'info':
                entry = f.copy()
                entry.setdefault('source', tk)
                if not entry.get('screenshot') and data.get('screenshot'):
                    entry['screenshot'] = data.get('screenshot')
                vulns.append(entry)
    parts.append('<div class="card"><h2>Vulnerabilities (' + str(len(vulns)) + ')</h2></div>')
    if not vulns:
        parts.append('<div class="card"><h3>No vulnerabilities found (non-informational)</h3></div>')
    else:
        for v in vulns:
            parts.append('<div class="card">')
            parts.append('<h3>' + sanitize(v.get('title','Unnamed')) + '</h3>')
            parts.append('<p><strong>Severity:</strong> ' + sanitize(str(v.get('severity',''))) + ' | <strong>Source:</strong> ' + sanitize(str(v.get('source',''))) + '</p>')
            parts.append('<pre>' + sanitize(str(v.get('description',''))) + '</pre>')
            if v.get('screenshot'):
                parts.append('<img src="' + v.get('screenshot') + '" style="max-width:100%;border-radius:6px"/>')
            parts.append('</div>')
    parts.append('</body></html>')
    return '
'.join(parts)

# GUI

def build_window():
    sg.theme('LightGray1')
    nav = [[sg.Button('Overview', key='-NAV-Overview', size=(18,1))],
           [sg.Button('Discovery', key='-NAV-Discovery', size=(18,1))],
           [sg.Button('Targets', key='-NAV-Targets', size=(18,1))],
           [sg.Button('Scans', key='-NAV-Scans', size=(18,1))],
           [sg.Button('Vulnerabilities', key='-NAV-Vulns', size=(18,1))],
           [sg.Button('Reports', key='-NAV-Reports', size=(18,1))],
           [sg.Button('Settings', key='-NAV-Settings', size=(18,1))]]

    overview_col = [[sg.Text('ACUX-Lite (Windows)', font=('Segoe UI',16))],[sg.Text('Prototype scanner for Windows 10')]]
    discovery_col = [[sg.Text('Discovery')],[sg.Input(key='-DISC-TARGET-', size=(40,1)), sg.Button('Add Target', key='-DISC-ADD')],[sg.Listbox(values=[t.get('url') for t in TARGETS], size=(60,10), key='-DISC-LIST')]]
    targets_col = [[sg.Text('Targets')],[sg.Input(key='-TGT-URL-', size=(40,1)), sg.Button('Add Target', key='-ADD-TGT')],[sg.Listbox(values=[t.get('url') for t in TARGETS], size=(60,10), key='-TGT-LIST')]]
    scans_col = [[sg.Text('Scans')],[sg.Input(key='-SCAN-TARGET-', size=(40,1)), sg.Combo(values=list(TOOL_CATALOG.keys()), key='-SCAN-TOOLS', default_value='nmap'), sg.Button('Start Scan', key='-START-SCAN')],[sg.Checkbox('Enable screenshots (chromedriver on PATH)', key='-SCAN-SS')],[sg.Text('Live Log:')],[sg.Multiline('', size=(80,20), key='-LOG-', disabled=True)]]
    vulns_col = [[sg.Text('Vulnerabilities')],[sg.Listbox(values=[], size=(80,15), key='-VULN-LIST')],[sg.Button('Export Report (HTML)', key='-EXPORT-HTML')]]
    reports_col = [[sg.Text('Reports')],[sg.Button('Open last report', key='-OPEN-REPORT')]]
    settings_col = [[sg.Text('Settings')],[sg.Button('Save Data'), sg.Button('Clear Cache')]]

    layout = [[sg.Column([[sg.Column(nav, vertical_alignment='top')]], element_justification='left'), sg.VSeperator(), sg.Column(overview_col, key='-PAGE-Overview'), sg.Column(discovery_col, visible=False, key='-PAGE-Discovery'), sg.Column(targets_col, visible=False, key='-PAGE-Targets'), sg.Column(scans_col, visible=False, key='-PAGE-Scans'), sg.Column(vulns_col, visible=False, key='-PAGE-Vulns'), sg.Column(reports_col, visible=False, key='-PAGE-Reports'), sg.Column(settings_col, visible=False, key='-PAGE-Settings')]]

    window = sg.Window('ACUX-Lite — Windows Scanner Prototype', layout, finalize=True, resizable=True)
    return window

# Main

def main():
    window = build_window()
    output_q: queue.Queue = queue.Queue()
    orch = Orchestrator(output_q)

    def log_consumer():
        while True:
            try:
                line = output_q.get(timeout=0.2)
                try:
                    cur = window['-LOG-'].get()
                    window['-LOG-'].update(cur + line)
                except Exception:
                    pass
            except queue.Empty:
                if not any(t.is_alive() for t in orch.threads):
                    time.sleep(0.1)
                continue

    t = threading.Thread(target=log_consumer, daemon=True)
    t.start()

    while True:
        event, values = window.read(timeout=200)
        if event == sg.WIN_CLOSED:
            break
        if event and event.startswith('-NAV-'):
            page = event.replace('-NAV-','')
            for p in ('Overview','Discovery','Targets','Scans','Vulns','Reports','Settings'):
                key = f'-PAGE-{p}'
                try:
                    window[key].update(visible=(p==page))
                except Exception:
                    pass
        if event == '-DISC-ADD' or event == '-ADD-TGT':
            url = values.get('-DISC-TARGET-') or values.get('-TGT-URL-')
            if url:
                TARGETS.append({'url': url, 'created': now_ts()})
                save_json(TARGETS_FILE, TARGETS)
                window['-DISC-LIST'].update([t.get('url') for t in TARGETS])
                window['-TGT-LIST'].update([t.get('url') for t in TARGETS])
        if event == '-START-SCAN':
            target = values.get('-SCAN-TARGET-')
            tool = values.get('-SCAN-TOOLS')
            enable_ss = bool(values.get('-SCAN-SS'))
            if not target:
                sg.popup_error('Enter target to scan')
            else:
                selected = [tool] if tool else list(TOOL_CATALOG.keys())
                orch.start_scan(target, selected, enable_screenshots=enable_ss)
                scan_entry = {'target': target, 'tools': selected, 'started': now_ts()}
                SCANS.append(scan_entry)
                save_json(SCANS_FILE, SCANS)
        if event == '-EXPORT-HTML':
            report_html = generate_vuln_report_html('last-scan', orch.results if hasattr(orch,'results') else {})
            tmp = os.path.join(tempfile.gettempdir(), f'acunetix_like_report_{int(time.time())}.html')
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(report_html)
            sg.popup('Report saved to: ' + tmp)
        if event == 'Save Data':
            save_json(TARGETS_FILE, TARGETS)
            save_json(SCANS_FILE, SCANS)
            save_json(CACHE_FILE, CACHE)
            sg.popup('Data saved')
        if event == 'Clear Cache':
            CACHE.clear()
            save_json(CACHE_FILE, CACHE)
            sg.popup('Cache cleared')

    window.close()

# Tests

def test_extract_params():
    s = 'http://example.com/page?user=alice&id=123&empty='
    got = extract_params_from_text(s)
    assert 'user' in got and 'id' in got


def test_report_empty():
    r = generate_vuln_report_html('example', {})
    assert isinstance(r, str) and 'Vulnerabilities' in r


def run_all_tests() -> List[str]:
    fails: List[str] = []
    try:
        test_extract_params()
    except AssertionError as e:
        fails.append('test_extract_params failed: ' + str(e))
    try:
        test_report_empty()
    except AssertionError as e:
        fails.append('test_report_empty failed: ' + str(e))
    return fails

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        f = run_all_tests()
        if f:
            print('FAILURES:')
            for x in f:
                print('-', x)
            sys.exit(2)
        print('All tests passed')
        sys.exit(0)
    main()
