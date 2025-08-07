
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import re
import dns.resolver
import time
import csv
from unidecode import unidecode
import smtplib
import socket

CONFIG = {
    "smtp_timeout": 10,
    "rate_limit_delay": 1.0
}

def normalize(name):
    return re.sub(r'[^a-z]', '', unidecode(name.lower()))

def generate_patterns(vorname, nachname, position, domain):
    v = vorname[0]
    patterns = [
        f"{vorname}.{nachname}@{domain}",
        f"{v}.{nachname}@{domain}",
        f"{vorname}@{domain}",
        f"{nachname}@{domain}",
        f"{vorname}_{nachname}@{domain}",
        f"{vorname}{nachname}@{domain}",
        f"{v}-{nachname}@{domain}",
        f"{vorname}-{nachname}@{domain}",
        f"info@{domain}",
        f"kontakt@{domain}",
        f"{v}{nachname}@{domain}",
        f"{nachname}{v}@{domain}"
    ]

    if "marketing" in position.lower():
        patterns += [f"marketing@{domain}", f"{v}.{nachname}@{domain}"]
    if "geschäftsführer" in position.lower() or "ceo" in position.lower():
        patterns += [f"gf@{domain}", f"geschaeftsfuehrung@{domain}", f"ceo@{domain}"]

    return list(set(patterns))

def get_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return str(sorted(answers, key=lambda x: x.preference)[0].exchange)
    except:
        return None

def smtp_check(email, mx_host):
    try:
        server = smtplib.SMTP(timeout=CONFIG["smtp_timeout"])
        server.connect(mx_host)
        server.helo()
        server.mail("test@example.com")
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except (socket.timeout, smtplib.SMTPException, Exception):
        return False

def run_email_finder():
    vorname = normalize(entry_vorname.get())
    nachname = normalize(entry_nachname.get())
    position = entry_position.get()
    firma = entry_firma.get()
    domain = entry_domain.get()

    if not all([vorname, nachname, domain]):
        messagebox.showerror("Fehler", "Bitte alle Pflichtfelder ausfüllen!")
        return

    emails = generate_patterns(vorname, nachname, position, domain)
    mx_host = get_mx_record(domain)
    results = []

    for email in emails:
        if mx_host:
            valid = smtp_check(email, mx_host)
            status = "valid" if valid else "invalid"
        else:
            status = "no_mx_record"
        results.append({
            "email": email,
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        time.sleep(CONFIG["rate_limit_delay"])

    filename = f"smartemailfinder_result_{vorname}_{nachname}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "status", "timestamp"])
        writer.writeheader()
        writer.writerows(results)

    messagebox.showinfo("Fertig", f"{len(results)} E-Mail-Adressen getestet. Ergebnisse gespeichert in: {filename}")

# GUI Setup
root = tk.Tk()
root.title("SmartEmailFinder")

tk.Label(root, text="Vorname:").grid(row=0, column=0, sticky="e")
tk.Label(root, text="Nachname:").grid(row=1, column=0, sticky="e")
tk.Label(root, text="Position:").grid(row=2, column=0, sticky="e")
tk.Label(root, text="Unternehmen:").grid(row=3, column=0, sticky="e")
tk.Label(root, text="Domain:").grid(row=4, column=0, sticky="e")

entry_vorname = tk.Entry(root, width=30)
entry_nachname = tk.Entry(root, width=30)
entry_position = tk.Entry(root, width=30)
entry_firma = tk.Entry(root, width=30)
entry_domain = tk.Entry(root, width=30)

entry_vorname.grid(row=0, column=1)
entry_nachname.grid(row=1, column=1)
entry_position.grid(row=2, column=1)
entry_firma.grid(row=3, column=1)
entry_domain.grid(row=4, column=1)

btn_start = tk.Button(root, text="Start", command=run_email_finder)
btn_start.grid(row=5, columnspan=2, pady=10)

root.mainloop()
