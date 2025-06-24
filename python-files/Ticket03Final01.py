#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13


import os
import time
import requests
import PySimpleGUI as sg
import subprocess

# === Konfiguration ===
API_TOKEN      = "c65gl1ehfyvradmmnewfjw26izcbzucckjwbug8c1uz6pu6s0nlxkhmzmpibsquk"
ORGANIZER      = "schliersbergalm"
EVENT          = "seilbahn-2"
SETTINGS_FILE  = "settings.txt"

# === Einstellungen laden ===
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"layout": "MiniTicket", "printer": ""}
    lines = open(SETTINGS_FILE).read().splitlines()
    return {"layout": lines[0], "printer": lines[1] if len(lines)>1 else ""}

# === Einstellungen speichern ===
def save_settings(layout, printer):
    with open(SETTINGS_FILE,"w") as f:
        f.write(f"{layout}\n{printer}\n")

# === Drucker ermitteln ===
def get_printers():
    try:
        out = subprocess.check_output(["lpstat","-a"], text=True)
        return [l.split()[0] for l in out.splitlines() if l]
    except:
        return ["Default"]

# === PDF drucken mit fit-to-page ===
def print_pdf(path, printer):
    cmd = ["lp","-o","fit-to-page"]
    if printer: cmd += ["-d",printer]
    cmd.append(path)
    subprocess.run(cmd)

# === Tickets holen & drucken ===
def get_and_print_tickets(code, layout, printer, debug):
    hdr = {"Authorization": f"Token {API_TOKEN}"}
    order_api = f"https://pretix.eu/api/v1/organizers/{ORGANIZER}/events/{EVENT}/orders/{code}/"

    # 1) Bestellung laden
    try:
        r = requests.get(order_api, headers=hdr); r.raise_for_status()
        data = r.json()
        debug.update(f"✅ Bestellung {code} geladen")
    except Exception as e:
        debug.update(f"❌ Bestellung fehlerhaft: {e}")
        return

    save_dir = os.path.expanduser("~/Tickets"); os.makedirs(save_dir, exist_ok=True)

    # 2) MiniTicket via API-Endpoint
    if layout == "MiniTicket":
        mini_api = f"https://pretix.eu/api/v1/organizers/{ORGANIZER}/events/{EVENT}/orders/{code}/download/miniticket/"
        try:
            r = requests.get(mini_api, headers=hdr); r.raise_for_status()
            fn = os.path.join(save_dir, f"{code}_MiniTicket.pdf")
            with open(fn,"wb") as f: f.write(r.content)
            debug.update(f"{debug.get()}\n📥 MiniTicket heruntergeladen: {fn}")
            time.sleep(0.5)
            print_pdf(fn, printer)
            debug.update(f"{debug.get()}\n🖨 Gedruckt: {fn}")
            return
        except requests.exceptions.HTTPError as he:
            if he.response.status_code == 404:
                debug.update(f"{debug.get()}\n⚠️ MiniTicket nicht verfügbar, wechsle zu PDF")
                layout = "pdf"
            else:
                debug.update(f"{debug.get()}\n❌ MiniTicket-Fehler: {he}")
                return
        except Exception as e:
            debug.update(f"{debug.get()}\n❌ MiniTicket-Fehler: {e}")
            return

    # 3) Alle Positionen als gewünschtes Layout
    count = 0
    for pos in data.get("positions", []):
        for dl in pos.get("downloads", []):
            if dl["output"] == layout.lower():
                try:
                    r = requests.get(dl["url"], headers=hdr); r.raise_for_status()
                    fn = os.path.join(save_dir, f"{code}_{pos['positionid']}.pdf")
                    with open(fn,"wb") as f: f.write(r.content)
                    debug.update(f"{debug.get()}\n📥 Ticket {pos['positionid']}: {fn}")
                    time.sleep(0.5)
                    print_pdf(fn, printer)
                    debug.update(f"{debug.get()}\n🖨 Gedruckt: {fn}")
                    count += 1
                except Exception as e:
                    debug.update(f"{debug.get()}\n❌ Pos {pos['positionid']}: {e}")
    if count == 0:
        debug.update(f"{debug.get()}\n⚠️ Keine Tickets für Layout '{layout}' gefunden")

# === GUI ===
settings = load_settings()
layouts = ["pdf","mobile_pdf","passbook","MiniTicket"]
printers = get_printers()

layout_gui = [
    [sg.Text("Bestellcode:"), sg.Input(key="-CODE-")],
    [sg.Text("Layout:"),       sg.Combo(layouts, default_value=settings["layout"], key="-LAYOUT-")],
    [sg.Text("Drucker:"),      sg.Combo(printers, default_value=settings["printer"], key="-PRINTER-")],
    [sg.Button("Drucken"), sg.Button("Beenden")],
    [sg.Multiline(size=(80,12), key="-DEBUG-", autoscroll=True)]
]

win = sg.Window("Pretix Ticketdrucker", layout_gui)
while True:
    ev, vals = win.read()
    if ev in (sg.WINDOW_CLOSED,"Beenden"): break
    if ev == "Drucken":
        save_settings(vals["-LAYOUT-"], vals["-PRINTER-"])
        win["-DEBUG-"].update("⏳ Druck läuft…")
        get_and_print_tickets(vals["-CODE-"].strip(),
                              vals["-LAYOUT-"],
                              vals["-PRINTER-"],
                              win["-DEBUG-"])
win.close()