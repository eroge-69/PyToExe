#!/usr/bin/env python3
import sys, socket, json, argparse, time, re, platform, subprocess
from typing import Optional
from getpass import getpass

try:
    import requests
except Exception:
    requests = None

T_TCP_HOST = "192.168.4.1"
T_TCP_PORT = 1000
V2_HTTP_BASE = "http://192.168.20.1"
V2_LIST_PATH = "/devsetupread"
V2_SETUP_PATH = "/setup"

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    C1, C2, C3, C4, CR, B = Fore.MAGENTA, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Style.RESET_ALL, Style.BRIGHT
except Exception:
    C1 = C2 = C3 = C4 = CR = B = ""

BANNER = f"""
{B}{C1}╔═══════════════════════════════════════════════════════════════╗
║               vtimer Ρύθμιση από Υπολογιστή (v2/v3)                  ║
╠══════════════════════════════════════════════════════════════════════╣
║           Created By George Georgiou For Divico Security             ║
╠══════════════════════════════════════════════════════════════════════╣
║  Βήματα:                                                             ║
║   1) Συνδέσου στο Wi-Fi AP της συσκευής.                             ║
║      • v2: 192.168.20.1                                              ║
║      • v3: 192.168.4.1                                               ║
║   2) Μόλις ανιχνευθεί, θα επιλέξεις SSID και θα σταλεί η ρύθμιση.    ║
╚══════════════════════════════════════════════════════════════════════╝{CR}
"""

def ping_once(host: str, timeout_s: float = 1.5) -> bool:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout_s * 1000)), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(int(max(1, round(timeout_s)))), host]
    try:
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_s + 1)
        return r.returncode == 0
    except Exception:
        return False

def probe_v2(timeout: float = 2.0) -> bool:
    if requests is None:
        return False
    url = V2_HTTP_BASE + V2_LIST_PATH
    try:
        import requests as _r
        r = _r.post(url, data={"pr": "1"}, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

def probe_v3(timeout: float = 2.0) -> bool:
    s = None
    try:
        s = socket.create_connection((T_TCP_HOST, T_TCP_PORT), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False
    finally:
        if s:
            try: s.close()
            except Exception: pass

def fetch_wifi_list_v2(timeout: float = 10.0):
    if requests is None:
        raise RuntimeError("Απαιτείται το πακέτο 'requests' για v2.")
    import requests as _r
    url = V2_HTTP_BASE + V2_LIST_PATH
    r = _r.post(url, data={"pr": "1"}, timeout=timeout)
    r.raise_for_status()
    ssids = []
    try:
        js = r.json()
    except Exception:
        try:
            js = json.loads(r.text)
        except Exception:
            js = r.text

    def extract_any(obj):
        if isinstance(obj, list):
            for item in obj:
                extract_any(item)
        elif isinstance(obj, dict):
            for _, v in obj.items():
                if isinstance(v, (list, dict)):
                    extract_any(v)
                elif isinstance(v, str):
                    ssids.append(v)
        elif isinstance(obj, str):
            for token in re.split(r"[\r\n,;]+", obj):
                token = token.strip().strip('"').strip()
                if token and len(token) <= 32:
                    ssids.append(token)

    extract_any(js)
    clean, seen = [], set()
    for s in ssids:
        s = s.strip().strip('"')
        if 0 < len(s) <= 32 and s not in seen:
            seen.add(s)
            clean.append(s)
    return clean

def fetch_wifi_list_v3(timeout_total: float = 30.0):
    ssids = []
    s = socket.create_connection((T_TCP_HOST, T_TCP_PORT), timeout=5.0)
    try:
        s.settimeout(2.0)
        # Πολλά firmware περιμένουν CR/LF
        s.sendall(b"ASKAPS\r\n")
        start = time.time()
        buf = b""
        pattern = re.compile(r'\+CWLAP:\("(?P<ssid>.*?)"\)')
        while time.time() - start < timeout_total:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                try:
                    decoded = buf.decode("utf-8", errors="ignore")
                except Exception:
                    decoded = None
                if decoded:
                    for m in pattern.finditer(decoded):
                        ssid = m.group("ssid")
                        if ssid and ssid not in ssids and len(ssid) <= 32:
                            ssids.append(ssid)
            except socket.timeout:
                pass
        return ssids
    finally:
        try: s.close()
        except Exception: pass

def send_config_v2(ssid: str, password: str, timeout: float = 10.0) -> bool:
    if requests is None:
        raise RuntimeError("Απαιτείται το πακέτο 'requests' για v2.")
    import requests as _r
    url = V2_HTTP_BASE + V2_SETUP_PATH
    payload = {"SSID": ssid, "Pasw": password, "LIP": "168", "GLIP": "192.168.20.1", "TMOF": "2", "EMAIL": ""}
    r = _r.post(url, data=payload, timeout=timeout)
    return r.status_code == 200

def _escape_at_arg(s: str) -> str:
    # Απλό escaping για AT-like πρωτόκολλο: " και \
    return s.replace("\\", "\\\\").replace('"', r'\"')

def send_config_v3(ssid: str, password: str) -> bool:
    # Προσθήκη CR/LF και escaping
    cmd = f'APCON"{_escape_at_arg(ssid)}","{_escape_at_arg(password)}"\r\n'
    s = socket.create_connection((T_TCP_HOST, T_TCP_PORT), timeout=5.0)
    try:
        s.settimeout(3.0)
        s.sendall(cmd.encode("utf-8"))
        try:
            _ = s.recv(256)  # δεν βασιζόμαστε στην απάντηση, απλά «στραγγίζουμε» το socket
        except socket.timeout:
            pass
        time.sleep(2.0)
        return True
    except Exception:
        return False
    finally:
        try: s.close()
        except Exception: pass

def choose_from_list(options):
    if not options:
        return None
    print(f"\n{B}{C4}Διαθέσιμα Wi-Fi από τη συσκευή:{CR}")
    for i, ssid in enumerate(options, 1):
        print(f"  {i:2d}) {ssid}")
    while True:
        raw = input("Επιλογή αριθμού (Enter για χειροκίνητη εισαγωγή SSID): ").strip()
        if raw == "":
            manual = input("Δώσε SSID: ").strip()
            return manual if manual else None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        print(f"{C3}Μη έγκυρη επιλογή, προσπάθησε ξανά.{CR}")

def prompt_yes_no(prompt: str, default_yes: bool = True) -> bool:
    enter_hint = "Ναι" if default_yes else "Όχι"
    suffix = "[Ναι/Όχι]"
    ans = input(f"{prompt} {suffix} (↵ Enter = {enter_hint}): ").strip().lower()
    if ans == "" and default_yes: return True
    if ans == "" and not default_yes: return False
    if ans in ("y", "yes", "ν", "ναι"): return True
    if ans in ("n", "no", "ο", "οχι", "όχι"): return False
    return default_yes

def wait_for_device(max_wait: Optional[int] = None, show_spinner: bool = True) -> Optional[str]:
    spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    start = time.time()
    print(f"{BANNER}\n{C4}Αναζήτηση συσκευής vtimer (v2: 192.168.20.1, v3: 192.168.4.1)…{CR}")
    while True:
        v2_seen = ping_once("192.168.20.1", timeout_s=1.2)
        v3_seen = ping_once("192.168.4.1", timeout_s=1.2)
        version = None
        if v3_seen and probe_v3(1.5):
            version = "3"
        elif v2_seen and probe_v2(1.5):
            version = "2"
        if version:
            print(f"\n{C2}Βρέθηκε συσκευή: v{version}{CR}")
            return version
        if show_spinner:
            sys.stdout.write("\r" + C1 + spinner[i % len(spinner)] + CR + " Περιμένω… σύνδεσε τον υπολογιστή στο AP της συσκευής ")
            sys.stdout.flush()
            i += 1
        time.sleep(0.6)
        if max_wait is not None and (time.time() - start) > max_wait:
            print(f"\n{C3}Λήξη χρόνου αναμονής.{CR}")
            return None

def run_setup_flow(force_version: Optional[str], retries: int) -> int:
    """
    Επιλογή 1: Auto Detect & Setup (manual SSID/password).
    Ανιχνεύει v2/v3, δίνει λίστα SSID και ζητά κωδικό.
    """
    version = force_version or wait_for_device()
    if not version:
        print(f"{C3}Δεν ανιχνεύτηκε συσκευή. Επιστροφή στο μενού.{CR}")
        return 2
    ssids = []
    for attempt in range(1, retries + 1):
        try:
            print(f"{C4}Ανάκτηση δικτύων (προσπάθεια {attempt}/{retries}) …{CR}")
            if version == "2":
                ssids = fetch_wifi_list_v2()
            else:
                ssids = fetch_wifi_list_v3()
            break
        except Exception as e:
            print(f"{C3}Αποτυχία ανάκτησης: {e}{CR}")
            time.sleep(1.0)
    if not ssids:
        print(f"{C3}Δεν επιστράφηκαν SSID· μπορείς να πληκτρολογήσεις χειροκίνητα.{CR}")
    ssid = choose_from_list(ssids)
    if not ssid:
        print(f"{C3}Δεν επιλέχθηκε SSID. Επιστροφή στο μενού.{CR}")
        return 1
    password = getpass("Κωδικός Wi-Fi (κενό για ανοικτά δίκτυα): ").strip()
    print(f'\n{C1}Πρόκειται να ρυθμιστεί: SSID="{ssid}" (κωδικός {"<κρυφός>" if password else "<κανένας>"}).{CR}')
    if not prompt_yes_no("Συνέχεια;", True):
        print(f"{C3}Ακυρώθηκε από τον χρήστη.{CR}")
        return 0
    ok = False
    for attempt in range(1, retries + 1):
        print(f"{C4}Αποστολή ρυθμίσεων (προσπάθεια {attempt}/{retries}) …{CR}")
        if version == "2":
            try:
                ok = send_config_v2(ssid, password)
            except Exception as e:
                print(f"{C3}Σφάλμα αποστολής: {e}{CR}")
                ok = False
        else:
            ok = send_config_v3(ssid, password)
        if ok:
            break
        time.sleep(1.0)
    if ok:
        print(f"{C2}Επιτυχία: οι ρυθμίσεις στάλθηκαν στη συσκευή.{CR}")
        if version == "3":
            print(f"{C4}Η συσκευή ίσως επανεκκινήσει/αποσυνδεθεί. Επανέλαβε σύνδεση στο κανονικό σου Wi-Fi.{CR}")
        return 0
    else:
        print(f"{C3}Αποτυχία αποστολής. Βεβαιώσου ότι είσαι συνδεδεμένος στο AP της συσκευής και ότι SSID/κωδικός είναι σωστά.{CR}")
        return 3

def run_auto_fixed_setup(ssid: str, password: str, retries: int = 2) -> int:
    """
    Επιλογή 2: Auto Detect & Auto Set.
    Ανιχνεύει αυτόματα v2/v3 και στέλνει απευθείας τις σταθερές ρυθμίσεις (χωρίς ερωτήσεις).
    """
    version = wait_for_device()
    if not version:
        print(f"{C3}Δεν ανιχνεύτηκε συσκευή. Επιστροφή στο μενού.{CR}")
        return 2
    print(f'{C4}Αποστολή ρυθμίσεων για SSID="{ssid}" (προκαθορισμένο)…{CR}')
    ok = False
    for attempt in range(1, retries + 1):
        print(f"{C4}Αποστολή (προσπάθεια {attempt}/{retries}) …{CR}")
        if version == "2":
            try:
                ok = send_config_v2(ssid, password)
            except Exception as e:
                print(f"{C3}Σφάλμα αποστολής (v2): {e}{CR}")
                ok = False
        else:
            ok = send_config_v3(ssid, password)
        if ok:
            break
        time.sleep(1.0)
    if ok:
        print(f"{C2}Επιτυχία: οι ρυθμίσεις στάλθηκαν στη συσκευή (v{version}).{CR}")
        if version == "3":
            print(f"{C4}Η συσκευή ίσως επανεκκινήσει/αποσυνδεθεί. Επανέλαβε σύνδεση στο κανονικό σου Wi-Fi.{CR}")
        return 0
    else:
        print(f"{C3}Αποτυχία αποστολής. Βεβαιώσου ότι είσαι συνδεδεμένος στο AP της συσκευής.{CR}")
        return 3

def pause(msg: str = "\nΠατήστε Enter για συνέχεια…"):
    try:
        input(msg)
    except KeyboardInterrupt:
        print("")

MENU = f"""
{B}{C4}=== vtimer Menu ==={CR}
  1) Auto Detect & Setup (manual SSID/password)
  2) Auto Detect & Auto Set (Plug And Play Solution) (SSID='VTimerWIFI', Pass='VTimer1982@')
  q) Exit
"""

def interactive_menu(default_retries: int = 2):
    while True:
        print(MENU)
        try:
            choice = input("Επιλογή (↵ Enter = 1): ").strip() or "1"
        except EOFError:
            choice = "1"
        if choice == "1":
            _ = run_setup_flow(None, default_retries)
            pause("\nΟλοκλήρωση διαδικασίας. Πατήστε Enter για επιστροφή στο μενού…")
        elif choice == "2":
            rc = run_auto_fixed_setup(ssid="VTimerWIFI", password="VTimer1982@", retries=default_retries)
            pause("\νΟλοκλήρωση διαδικασίας. Πατήστε Enter για επιστροφή στο μενού…")
        elif choice.lower() in ("q", "quit", "exit"):
            print(f"{C1}Αντίο!{CR}")
            break
        else:
            print(f"{C3}Άγνωστη επιλογή. Προσπάθησε ξανά.{CR}")

def main(argv=None):
    p = argparse.ArgumentParser(description="Απλή εφαρμογή vtimer: μενού, αναμονή συσκευής και ρύθμιση.")
    p.add_argument("--version", choices=["2", "3"], help="Εξαναγκασμός έκδοσης συσκευής (παράκαμψη ανίχνευσης).")
    p.add_argument("--retry", type=int, default=2, help="Προσπάθειες για ανάκτηση/αποστολή.")
    p.add_argument("--max-wait", type=int, default=None, help="Μέγιστος χρόνος αναμονής σε δευτερόλεπτα (προεπιλογή: άπειρο).")
    p.add_argument("--menu", action="store_true", help="Εκκίνηση σε διαδραστικό μενού (προεπιλογή όταν δεν δίνονται παράμετροι).")
    args = p.parse_args(argv)

    # Αν δεν δοθούν flags, μπες σε διαδραστικό μενού για να μείνει «ζωντανό» το παράθυρο
    no_args = (argv is None and len(sys.argv) == 1)
    if args.menu or no_args:
        interactive_menu(default_retries=args.retry)
        return 0

    # Μη διαδραστική ροή
    if args.version:
        rc = run_setup_flow(args.version, args.retry)
    else:
        version = wait_for_device(max_wait=args.max_wait)
        if not version:
            print(f"{C3}Δεν ανιχνεύτηκε συσκευή.{CR}")
            rc = 2
        else:
            rc = run_setup_flow(version, args.retry)

    # Μετά τη μη-διαδραστική ροή, απλά κλείσε.
    return rc

if __name__ == "__main__":
    sys.exit(main())
