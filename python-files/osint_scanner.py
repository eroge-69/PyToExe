import requests, validators, socket, re, base64, dns.resolver, json, time, threading, configparser
from fpdf import FPDF
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from duckduckgo_search import DDGS
from io import BytesIO
import webbrowser

# API KEYS
VIRUSTOTAL_API_KEY = "8ef077ddaffa4638eb343750826f86c5ec048a04527b0eec60d77af85a78a26e"
IPINFO_TOKEN = "7035cf7dcbb289"
SHODAN_API_KEY = "N08K1xJxvSWzZdDvnvvdAWJoR2kmDwQZ"

cfg = configparser.ConfigParser()
dark_mode = True

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper

def safe_insert(text):
    output.after(0, lambda: output.insert(END, text + "\n"))

def set_status(msg):
    status_bar.after(0, lambda: status_bar.config(text=msg))

def encode_url_for_vt(url): return base64.urlsafe_b64encode(url.encode()).decode().strip("=")

def scan_vt(url):
    try:
        enc = encode_url_for_vt(url)
        with requests.Session() as s:
            headers = {"x-apikey": VIRUSTOTAL_API_KEY}
            r = s.get(f"https://www.virustotal.com/api/v3/urls/{enc}", headers=headers)
        return r.json() if r.ok else {"error": "VT scan failed"}
    except Exception as e:
        return {"error": str(e)}

def ipinfo(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}")
        return r.json() if r.ok else {"error": "Failed to fetch IP info"}
    except Exception as e:
        return {"error": f"IPInfo Error: {str(e)}"}

def get_dns(domain):
    out = {}
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 4.0
    for rtype in ['A', 'MX', 'NS', 'TXT']:
        try:
            out[rtype] = [r.to_text() for r in resolver.resolve(domain, rtype)]
        except:
            continue
    return out

def get_headers(url):
    try: return dict(requests.head(url, timeout=5).headers)
    except: return {}

def shodan_scan(ip):
    try:
        r = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}")
        return r.json() if r.ok else {"error": "Shodan lookup failed"}
    except Exception as e:
        return {"error": f"Shodan Error: {str(e)}"}

def crtsh_subdomains(domain):
    try:
        r = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=10)
        if r.ok:
            names = set()
            for entry in r.json():
                for item in entry['name_value'].splitlines():
                    names.add(item.strip())
            return list(names)
        return []
    except Exception as e:
        return [f"Error: {str(e)}"]

def github_dorks(domain):
    return {
        "Secrets": f"https://github.com/search?q={domain}+password+OR+apikey+OR+token&type=code",
        "Emails": f"https://github.com/search?q=@{domain}&type=code",
        "Configs": f"https://github.com/search?q={domain}+filename:.env&type=code"
    }

def google_dorks(domain):
    return {
        "Login Pages": f"https://www.google.com/search?q=site:{domain}+inurl:login",
        "Index Of": f"https://www.google.com/search?q=site:{domain}+intitle:index+of",
        "Sensitive Files": f"https://www.google.com/search?q=site:{domain}+ext:env+OR+ext:log"
    }

def parse_email_headers(raw):
    headers = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers

def analyze_email_headers(headers):
    verdict = "Safe"
    red_flags = []
    for key in ["X-Spam-Status", "X-Spam-Flag", "Received-SPF", "Authentication-Results"]:
        value = headers.get(key, "")
        if any(x in value.lower() for x in ["fail", "softfail", "bad", "yes"]):
            red_flags.append(f"{key}: {value}")
            verdict = "Suspicious"
    return verdict, red_flags

def generate_pdf(results, path="report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="XD3Labs OSINT Report", ln=True, align="C")
    pdf.ln(10)
    for section, data in results.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt=f"{section}:", ln=True)
        pdf.set_font("Arial", size=10)
        if isinstance(data, dict):
            for k, v in data.items():
                line = f"{k}: {v}"
                pdf.multi_cell(200, 10, txt=(line[:180] + "..." if len(line) > 180 else line))
        elif isinstance(data, list):
            for item in data:
                line = str(item)
                pdf.multi_cell(200, 10, txt=(line[:180] + "..." if len(line) > 180 else line))
        else:
            line = str(data)
            pdf.multi_cell(200, 10, txt=(line[:180] + "..." if len(line) > 180 else line))
        pdf.ln(5)
    pdf.output(path)
    return path

def export_json(results):
    with open("report.json", "w") as f:
        json.dump(results, f, indent=4)
    return "report.json"

def save_theme():
    cfg['settings'] = {'dark': str(dark_mode)}
    with open('config.ini', 'w') as f:
        cfg.write(f)

def load_theme():
    global dark_mode
    try:
        cfg.read('config.ini')
        dark_mode = cfg.getboolean('settings', 'dark')
    except:
        dark_mode = True

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    save_theme()
    apply_theme()

def apply_theme():
    bg, fg = ("#1e1e1e", "white") if dark_mode else ("white", "black")
    root.configure(bg=bg)

    def update_widget_colors(widget):
        cls = widget.winfo_class()
        if cls in ("Label", "Button", "Entry", "Text", "TFrame"):
            try:
                widget.configure(bg=bg, fg=fg)
                if isinstance(widget, (Entry, Text, scrolledtext.ScrolledText)):
                    widget.configure(insertbackground=fg)
            except:
                pass
        for child in widget.winfo_children():
            update_widget_colors(child)

    update_widget_colors(root)
    status_bar.configure(bg=bg, fg=fg)

# GUI SETUP
root = Tk()
root.title("XD3Labs Advanced OSINT Scanner")
root.geometry("1150x880")
load_theme()

Label(root, text="Enter URL:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
entry_url = Entry(root, width=100); entry_url.grid(row=0, column=1, columnspan=5, pady=5)

Label(root, text="Search Name:").grid(row=1, column=0, sticky=W, padx=10)
entry_name = Entry(root, width=100); entry_name.grid(row=1, column=1, columnspan=5, pady=5)

Label(root, text="Paste Email Headers:").grid(row=2, column=0, sticky=NW, padx=10)
email_input = scrolledtext.ScrolledText(root, height=4, width=110); email_input.grid(row=2, column=1, columnspan=5, pady=5)

btn_frame = Frame(root); btn_frame.grid(row=3, column=0, columnspan=6, pady=10)
Button(btn_frame, text="Run Advanced Scan", command=lambda: threaded_scan()).grid(row=0, column=0, padx=5)
Button(btn_frame, text="Email Header Check", command=lambda: threaded_email_check()).grid(row=0, column=1, padx=5)
Button(btn_frame, text="Search Name OSINT", command=lambda: threaded_name_search()).grid(row=0, column=2, padx=5)
Button(btn_frame, text="Scan QR Code", command=lambda: threaded_qr_scan()).grid(row=0, column=3, padx=5)
Button(btn_frame, text="Clear All", command=lambda: clear_all()).grid(row=0, column=4, padx=5)
Button(btn_frame, text="Switch Theme", command=toggle_theme).grid(row=0, column=5, padx=5)

Label(root, text="Output:").grid(row=4, column=0, sticky=W, padx=10)
output = scrolledtext.ScrolledText(root, height=25, width=130)
output.grid(row=5, column=0, columnspan=6, padx=10)

status_bar = Label(root, text="Ready", bd=1, relief=SUNKEN, anchor=W)
status_bar.grid(row=6, column=0, columnspan=6, sticky=EW)
apply_theme()

# THREADING SCAN HANDLERS
@threaded
def threaded_scan():
    url = entry_url.get().strip()
    name = entry_name.get().strip()
    email_raw = email_input.get("1.0", END).strip()
    output.delete("1.0", END)
    set_status("Running scan... please wait.")
    report = {}

    if not validators.url(url):
        messagebox.showerror("Invalid URL", "Enter valid URL (http/https)")
        set_status("Error: Invalid URL")
        return

    try:
        domain = re.findall(r"https?://([^/]+)", url)[0]
        ip = socket.gethostbyname(domain)

        safe_insert("--- Starting scan ---")
        report["VirusTotal"] = scan_vt(url)
        report["Verdict"] = "Malicious" if report["VirusTotal"].get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0) > 0 else "Safe"
        report["IP Info"] = ipinfo(ip)
        report["Shodan"] = shodan_scan(ip)
        report["DNS Records"] = get_dns(domain)
        report["Headers"] = get_headers(url)
        report["Subdomains"] = crtsh_subdomains(domain)
        report["GitHub Dorks"] = github_dorks(domain)
        report["Google Dorks"] = google_dorks(domain)

        if name:
            report["Name OSINT"] = {"Google": f"https://www.google.com/search?q={'+'.join(name.split())}+osint"}

        if email_raw:
            headers = parse_email_headers(email_raw)
            verdict, flags = analyze_email_headers(headers)
            report["Email Header Verdict"] = verdict
            report["Email Headers"] = headers
            report["Email Red Flags"] = flags

        for section, data in report.items():
            safe_insert(f"\n--- {section} ---")
            if isinstance(data, dict):
                for k, v in data.items(): safe_insert(f"{k}: {v}")
            elif isinstance(data, list):
                for i in data: safe_insert(f"- {i}")
            else:
                safe_insert(str(data))

        file = generate_pdf(report)
        safe_insert(f"\n[✓] PDF Generated: {file}")
        json_path = export_json(report)
        safe_insert(f"[✓] JSON Exported: {json_path}")
        set_status("Scan complete ✔")

    except Exception as e:
        messagebox.showerror("Scan Error", str(e))
        set_status("Error occurred ❌")

@threaded
def threaded_email_check():
    raw = email_input.get("1.0", END).strip()
    output.delete("1.0", END)
    set_status("Analyzing email headers...")
    if not raw:
        messagebox.showerror("Error", "Paste email headers.")
        set_status("Error: Empty headers")
        return
    headers = parse_email_headers(raw)
    verdict, red_flags = analyze_email_headers(headers)
    safe_insert(f"--- Email Verdict: {verdict} ---")
    safe_insert("\n".join(f"[!] {flag}" for flag in red_flags) or "[✓] No suspicious headers.\n")
    set_status("Email header analysis complete")

@threaded
def threaded_qr_scan():
    path = filedialog.askopenfilename(title="Select QR Code Image")
    if not path: return
    try:
        img = Image.open(path)
        decoded = decode(img)
        if decoded:
            content = decoded[0].data.decode()
            entry_url.delete(0, END)
            entry_url.insert(0, content)
            messagebox.showinfo("QR Result", f"QR Code contains:\n{content}")
        else:
            messagebox.showwarning("QR", "No QR code found.")
    except Exception as e:
        messagebox.showerror("QR Error", str(e))

@threaded
def threaded_name_search():
    name = entry_name.get().strip()
    output.delete("1.0", END)
    if not name:
        messagebox.showerror("Input Required", "Enter a name to search.")
        set_status("Name input missing ❌")
        return

    set_status(f"Searching OSINT for: {name}")
    safe_insert(f"--- Live OSINT Search for: {name} ---\n")

    try:
        text_results, image_results = [], []
        query = f"{name} site:facebook.com OR site:linkedin.com OR site:github.com OR site:instagram.com"

        with DDGS() as ddgs:
            for r in ddgs.text(query, region='in-en', safesearch='Moderate', max_results=10):
                text_results.append({"title": r['title'], "link": r['href'], "desc": r['body']})

            for img in ddgs.images(name, region='in-en', safesearch='Moderate', max_results=4):
                image_results.append(img['image'])

        if text_results:
            for r in text_results:
                safe_insert(f"[+] {r['title']}\n{r['link']}\n{r['desc']}\n")
        else:
            safe_insert("No text results found.")

        if image_results:
            show_osint_images(image_results)
        else:
            safe_insert("No image results.")

        set_status("Name OSINT Search Done ✅")

    except Exception as e:
        safe_insert(f"Error: {str(e)}")
        set_status("Error during name search ❌")

def show_osint_images(image_urls):
    img_frame = Frame(root, bg=root["bg"])
    img_frame.grid(row=7, column=0, columnspan=6, pady=5)
    for url in image_urls:
        try:
            img_data = requests.get(url, timeout=5).content
            img = Image.open(BytesIO(img_data)).resize((100, 100))
            tk_img = ImageTk.PhotoImage(img)
            lbl = Label(img_frame, image=tk_img, bg=root["bg"], cursor="hand2")
            lbl.image = tk_img
            lbl.pack(side=LEFT, padx=5)
            lbl.bind("<Button-1>", lambda e, link=url: webbrowser.open(link))
        except:
            continue

def clear_all():
    entry_url.delete(0, END)
    entry_name.delete(0, END)
    email_input.delete("1.0", END)
    output.delete("1.0", END)
    set_status("Cleared")

root.mainloop()
