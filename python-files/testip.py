import sys, os, time, threading, socket, psutil, ipaddress, requests, math, random, webbrowser
from collections import defaultdict, deque
from scapy.all import sniff, IP, TCP, UDP
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLabel, QSplitter,
    QPushButton, QStyledItemDelegate, QFrame, QGridLayout, QStackedLayout, QSizePolicy,
    QWidget as QtWidget, QStyle
)
from PySide6.QtCore import Qt, QAbstractTableModel, QTimer, QModelIndex, QRect, QSize
from PySide6.QtGui import QPalette, QColor, QFont, QPixmap, QPainter
from PySide6.QtMultimedia import QAudioFormat, QAudioSink
from PySide6.QtCore import QBuffer, QByteArray, QIODevice

import pyqtgraph as pg

try:
    from ipwhois import IPWhois
    _have_rdap = True
except:
    _have_rdap = False

# ----------- State
peers = defaultdict(lambda: {
    "pkts":0,"bytes":0,"tx":0,"rx":0,"udp":0,"tcp":0,
    "lports":defaultdict(int),"rports":defaultdict(int),
    "last":0.0,"gta":False,"ip":"",
    "seen_mark":False,
    "presence":deque([False]*10, maxlen=10),  # stabilité 10s
    "delta_bytes_last":0.0,
    "first_seen":0.0,
})
stop_flag = False
local_ips = set()
gta_sockets = set()
gta_remotes = set()
gta_names = {"gta5.exe","gta5_enhanced.exe","gta5_enhanced_be.exe"}

geo_cache = {}      # ip -> "FR"
flag_cache = {}     # "fr" -> QPixmap
resolve_q = set()
flag_q = set()
q_lock = threading.Lock()

iface_name = ""
local_ip_detected = "—"
interval_ui = 1.0
tick_secs   = 1.0
start_time = time.time()

# boot total (10s) — 9s animation rouge, 1s drapeau FR
BOOT_WAIT = 10.0

udp_bytes_total = 0
prev_bytes = {}               # ip -> bytes

you_public_ip = ""

COUNTRY_NAMES = {
    "AF": "Afghanistan",
    "AX": "Åland Islands",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "CV": "Cabo Verde",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia",
    "KM": "Comoros",
    "CG": "Congo",
    "CD": "Congo, Democratic Republic of the",
    "CK": "Cook Islands",
    "CR": "Costa Rica",
    "CI": "Côte d'Ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Curaçao",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "SZ": "Eswatini",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (Malvinas)",
    "FO": "Faroe Islands",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories",
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "North Korea",
    "KR": "South Korea",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia",
    "MD": "Moldova",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MK": "North Macedonia",
    "MP": "Northern Mariana Islands",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine, State of",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RU": "Russia",
    "RW": "Rwanda",
    "BL": "Saint Barthélemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin (French part)",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic",
    "TW": "Taiwan",
    "TJ": "Tajikistan",
    "TZ": "Tanzania",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom",
    "US": "United States",
    "UM": "United States Minor Outlying Islands",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela",
    "VN": "Viet Nam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe"
}

INTRO_LINES = [
	"Booting admin tools… don’t fuckin’ alt-tab now. 💻",
	"Connecting to Rockstar’s shitty cloud… pray it works. ☁️",
	"Patching firewall holes… stop leaking like Trevor’s pants. 🔥",
	"Injecting packets straight up your ass… 🧨",
	"Decrypting Social Club bullshit… hold tight. 🔓",
	"Spawning armored Kuruma… because you suck at driving. 🚗",
	"Flooding LSPD servers… fuck the pigs. 🚔",
	"Loading snacks & ammo… don’t choke on that P&Q bar. 🍫",
	"Bribing Lester… this fat fuck better deliver. 🕶️",
	"Launching orbital cannon… aim at your mom’s house. 💣",
	"Reticulating splines… and your shitty KD ratio. 📉",
	"Spinning up VPNs… hide your sorry ass from Rockstar. 🕵️",
	"Checking heist masks… don’t forget you look like a clown. 🤡",
	"Overclocking routers… melting plastic faster than Trevor’s brain. 🔥",
	"Encrypting dick pics… nobody cares, dude. 📡",
	"Syncing with Blaine County meth labs… Walter White approves. ⚗️",
	"Downloading cheats… nah, just banning your dumb ass. 🚫",
	"Shoving UDP packets down your throat… enjoy the lag. 🌐",
	"Calibrating orbital strike… hope you paid your bills, bitch. 💀",
	"Scanning modders… 99% of you are assholes. 🎯",
	"Injecting scripts… cleaner than your browsing history. 🧹",
	"Deploying drones… don’t wave at ‘em, dickhead. 🚁",
	"Rebooting Rockstar servers… lol, they’re still shit. 💩",
	"Fetching admin coffee… fuck off, it’s cold. ☕",
	"Running anti-lag ritual… Lamar’s still roasting your ass. 🔥",
]

# 256 prénoms (indexés 0..255)
IP_NAMES = [
	"Rick", "Morty", "Bender", "Homer", "Bart", "Marge", "Maggie", "Stewie",
	"Peter", "Lois", "Brian", "Meg", "Cleveland", "Quagmire", "Joe", "Stan",
	"Roger", "Klaus", "Hayley", "Francine", "RickSanchez", "PickleRick", "BirdPerson", "Squanchy",
	"Jerry", "Summer", "Kratos", "Atreus", "Zeus", "Ares", "Hades", "Hercules",
	"Sparta", "Leonidas", "Geralt", "Ciri", "Yennefer", "Dandelion", "Roach", "Triss",
	"Trevor", "Michael", "Franklin", "CJ", "BigSmoke", "Ryder", "Sweet", "Tenpenny",
	"Niko", "Roman", "Luis", "Tony", "Tommy", "Vercetti", "Claude", "Lester",
	"ClintEastwood", "DirtyHarry", "JohnWayne", "ChuckNorris", "BruceLee", "JackieChan", "JetLi", "VanDamme",
	"Rambo", "Rocky", "Balboa", "Apollo", "IvanDrago", "ClubberLang", "Mickey", "Adrian",
	"JohnSnow", "Arya", "Sansa", "Bran", "NedStark", "Catelyn", "Robb", "Benjen",
	"Tyrion", "Jaime", "Cersei", "Joffrey", "Hound", "Mountain", "Bronn", "Varys",
	"Daenerys", "Drogon", "Viserion", "Rhaegal", "Drogo", "Jorah", "GreyWorm", "Missandei",
	"Gandalf", "Frodo", "Samwise", "Merry", "Pippin", "Legolas", "Gimli", "Boromir",
	"Aragorn", "Sauron", "Saruman", "Gollum", "Bilbo", "Thorin", "Balin", "Kili",
	"Thanos", "IronMan", "TonyStark", "CaptainAmerica", "Thor", "Loki", "Hulk", "BlackWidow",
	"Hawkeye", "SpiderMan", "Venom", "Carnage", "DoctorStrange", "Wanda", "Vision", "Ultron",
	"Batman", "Robin", "Joker", "HarleyQuinn", "Penguin", "Riddler", "Bane", "TwoFace",
	"Superman", "LexLuthor", "WonderWoman", "Flash", "Aquaman", "Cyborg", "GreenLantern", "Shazam",
	"DarthVader", "Luke", "Leia", "HanSolo", "Chewbacca", "Yoda", "ObiWan", "Anakin",
	"Palpatine", "Maul", "KyloRen", "Rey", "Finn", "Poe", "BB8", "Mando",
	"Grogu", "BobaFett", "Jango", "Dooku", "Grievous", "JarJar", "Padmé", "Lando",
	"MasterChief", "Cortana", "Arbiter", "Johnson", "Grunt", "Elite", "Brute", "Flood",
	"MarcusFenix", "Dom", "ColeTrain", "Baird", "QueenMyrrah", "Skorge", "RAAM", "Kait",
	"Ezio", "Altair", "Connor", "EdwardKenway", "Bayek", "Kassandra", "Eivor", "Basim",
	"Krillin", "Goku", "Vegeta", "Piccolo", "Frieza", "Cell", "MajinBuu", "Gohan",
	"Trunks", "Bulma", "ChiChi", "Beerus", "Whis", "Jiren", "Hit", "Broly",
	"AshKetchum", "Pikachu", "Misty", "Brock", "TeamRocket", "Jessie", "James", "Meowth",
	"Charizard", "Mewtwo", "Lugia", "HoOh", "Snorlax", "Eevee", "Squirtle", "Bulbasaur",
	"Link", "Zelda", "Ganon", "Sheik", "Tingle", "Midna", "Epona", "Darunia",
	"Sonic", "Tails", "Knuckles", "Shadow", "Eggman", "Amy", "MetalSonic", "Silver",
	"PacMan", "MsPacMan", "DonkeyKong", "DiddyKong", "KingKRool", "Bowser", "Mario", "Luigi",
	"Peach", "Toad", "Yoshi", "Wario", "Waluigi", "Koopa", "Daisy", "Rosalina",
	"HomerSimpson", "Moe", "Barney", "Skinner", "Milhouse", "Nelson", "Flanders", "Lenny"
]

while len(IP_NAMES) < 256:
    IP_NAMES.append(f"Name{len(IP_NAMES)}")
IP_NAMES = IP_NAMES[:256]

def ip_to_index_name(ip: str) -> str:
    try:
        parts = ip.split(".")
        if len(parts) >= 3:
            idx = int(parts[2]) % 256
            return IP_NAMES[idx]
    except:
        pass
    return "Anon"

# ----------- Net helpers
def get_public_ip():
    for url in ("https://api.ipify.org","https://ifconfig.me/ip","https://ipinfo.io/ip"):
        try:
            r = requests.get(url, timeout=2)
            if r.ok:
                ip = r.text.strip()
                socket.inet_aton(ip)
                return ip
        except:
            pass
    return outbound_ip()

def outbound_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 53))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def iface_by_ip(ipv4):
    for name, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            if a.family == socket.AF_INET and a.address == ipv4:
                return name
    return None

def detect_iface_with_fallback():
    try:
        out_ip_local = outbound_ip()
        name = iface_by_ip(out_ip_local)
        if name:
            return name, out_ip_local
    except:
        pass
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for ifname, st in stats.items():
            if not st.isup: continue
            for a in addrs.get(ifname, []):
                if a.family == socket.AF_INET:
                    ip = a.address
                    if ip.startswith("127."): continue
                    return ifname, ip
    except:
        pass
    return None, None

def refresh_local():
    local_ips.clear()
    for a in psutil.net_if_addrs().get(iface_name, []):
        if a.family == socket.AF_INET:
            local_ips.add(a.address)

def refresh_gta():
    global gta_sockets, gta_remotes
    gta_sockets = set(); gta_remotes = set()
    pids = set()
    for p in psutil.process_iter(["name","pid"]):
        n = (p.info.get("name") or "").lower()
        if n in gta_names:
            pids.add(p.info["pid"])
    if not pids: return
    for c in psutil.net_connections(kind="inet"):
        if c.pid in pids and c.laddr:
            tt = c.type
            gta_sockets.add((c.laddr.ip, c.laddr.port, tt))
            if c.raddr:
                gta_remotes.add((c.raddr.ip, c.raddr.port, tt))

def is_priv(ip):
    try: return ipaddress.ip_address(ip).is_private
    except: return False

def is_mc(ip):
    try: return ipaddress.ip_address(ip).is_multicast
    except: return False

def is_player(m, now):
    if m["gta"] and m["udp"]>0 and now-m["last"]<=10:
        return True
    if not m["ip"] or is_priv(m["ip"]) or is_mc(m["ip"]):
        return False
    if now-m["last"]>10:
        return False
    if m["udp"] < 5:
        return False
    sym = (m["tx"]+1)/(m["rx"]+1)
    if not (0.2 <= sym <= 5):
        return False
    return True

def bytes_to_kb_str_2dec(n):
    return f"{(float(n)/1024.0):.2f}KB"

def bytes_to_mb_str_2dec(n):
    return f"{(float(n)/(1024.0**2)):.2f}MB"

def top_port(d1, d2):
    if d1: return max(d1.items(), key=lambda x: x[1])[0]
    if d2: return max(d2.items(), key=lambda x: x[1])[0]
    return "-"

def ts_to_hms(ts):
    if not ts: return "-"
    try:
        return time.strftime("%H:%M:%S", time.localtime(ts))
    except:
        return "-"

# ----------- Geo + Flags
def enqueue_geo(ip):
    if is_priv(ip) or is_mc(ip) or ip in geo_cache or not _have_rdap:
        return
    with q_lock:
        resolve_q.add(ip)

def rdap_country_code(ip):
    try:
        r = IPWhois(ip).lookup_rdap(asn_methods=["dns","whois","http"])
        c = r.get("network",{}).get("country") or r.get("asn_country_code") or "?"
        return c.upper()
    except:
        return "?"

def resolver_loop():
    while not stop_flag:
        ip = None
        with q_lock:
            if resolve_q: ip = resolve_q.pop()
        if ip:
            cc = rdap_country_code(ip)
            geo_cache[ip] = cc
            if cc and cc not in ("LAN","MC","?"):
                with q_lock: flag_q.add(cc.lower())
            time.sleep(0.3)
        else:
            time.sleep(0.2)

def fetch_flag_png(cc_lower):
    url = f"https://flagcdn.com/24x18/{cc_lower}.png"
    try:
        r = requests.get(url, timeout=3)
        if r.ok:
            pm = QPixmap()
            pm.loadFromData(r.content)
            if not pm.isNull():
                flag_cache[cc_lower] = pm
    except:
        pass

def flag_loader_loop():
    while not stop_flag:
        cc = None
        with q_lock:
            if flag_q: cc = flag_q.pop()
        if cc:
            if cc not in flag_cache:
                fetch_flag_png(cc)
        else:
            time.sleep(0.2)

# ----------- Sniffer
def sniffer():
    global udp_bytes_total
    def h(p):
        if IP not in p:
            return
        ip = p[IP]; tcp = TCP in p; udp = UDP in p
        if udp:
            try:
                udp_bytes_total += len(p)
            except:
                pass

        if ip.src in local_ips:
            peer = ip.dst; local = True
            lp = p[UDP].sport if udp else (p[TCP].sport if tcp else None)
            rp = p[UDP].dport if udp else (p[TCP].dport if tcp else None)
        elif ip.dst in local_ips:
            peer = ip.src; local = False
            lp = p[UDP].dport if udp else (p[TCP].dport if tcp else None)
            rp = p[UDP].sport if udp else (p[TCP].sport if tcp else None)
        else:
            return

        m = peers[peer]
        if not m["first_seen"]:
            m["first_seen"] = time.time()
        m["pkts"] += 1
        sz = len(p); m["bytes"] += sz; m["last"] = time.time(); m["ip"] = peer; m["seen_mark"] = True

        if local: m["tx"] += sz
        else: m["rx"] += sz
        if udp: m["udp"] += 1
        if tcp: m["tcp"] += 1
        if lp: m["lports"][lp] += 1
        if rp: m["rports"][rp] += 1
        if udp or tcp:
            tt = socket.SOCK_DGRAM if udp else socket.SOCK_STREAM
            lip = ip.src if local else ip.dst
            rip = ip.dst if local else ip.src
            if (lip, lp, tt) in gta_sockets or (rip, rp, tt) in gta_remotes:
                m["gta"] = True
        if peer not in geo_cache:
            enqueue_geo(peer)
    sniff(prn=h, store=False, iface=iface_name, filter="ip and (tcp or udp)", stop_filter=lambda x: stop_flag)

# ----------- ticker 1s
def ticker():
    while not stop_flag:
        for m in peers.values():
            m["presence"].append(m["seen_mark"])
            m["seen_mark"] = False
        time.sleep(tick_secs)

# ----------- Helpers échelle Y (KB/s)
def nice_step(max_val, target_ticks=6):
    if max_val <= 0: return 1.0
    raw = max_val / max(1, target_ticks)
    exp = math.floor(math.log10(raw)) if raw>0 else 0
    frac = raw / (10**exp) if raw>0 else 1
    step = None
    for m in (1.0, 2.0, 2.5, 5.0):
        if frac <= m:
            step = m * (10**exp); break
    if step is None:
        step = 10.0 * (10**exp)
    if step < 1.0: step = 1.0
    return step

def lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    r = int(c1.red()   + (c2.red()   - c1.red())   * t)
    g = int(c1.green() + (c2.green() - c1.green()) * t)
    b = int(c1.blue()  + (c2.blue()  - c1.blue())  * t)
    return QColor(r, g, b)

# ----------- Qt model + delegate (définis AVANT App)
class CountryDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        val = index.data(Qt.DisplayRole) or ""
        parts = val.split(" ", 1)
        cc = parts[0] if parts else ""
        name = parts[1] if len(parts) > 1 else ""
        rect = option.rect

        painter.save()
        cc_color = QColor("#7ad1ff")
        name_color = QColor("#cdd3dd")

        painter.setPen(cc_color)
        painter.drawText(QRect(rect.left()+8, rect.top(), rect.width()-60, rect.height()),
                         Qt.AlignVCenter|Qt.AlignLeft, cc)

        metrics_width = painter.fontMetrics().horizontalAdvance(cc + " ")
        painter.setPen(name_color)
        painter.drawText(QRect(rect.left()+8+metrics_width, rect.top(), rect.width()-60-metrics_width, rect.height()),
                         Qt.AlignVCenter|Qt.AlignLeft, name)

        pm = flag_cache.get(cc.lower())
        if pm:
            w = min(24, pm.width()); h = min(18, pm.height())
            x = rect.right()-w-8; y = rect.top() + (rect.height()-h)//2
            painter.drawPixmap(x, y, w, h, pm)
        painter.restore()

class PeersModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        # IP | PORT | DATA | COUNTRY | IP NAME | ADDED | DATA TOTAL | ACTION
        self.cols = ["IP","PORT","DATA","COUNTRY","IP NAME","ADDED","DATA TOTAL","ACTION"]
        self.rows = []
    def rowCount(self, parent=QModelIndex()): return len(self.rows)
    def columnCount(self, parent=QModelIndex()): return len(self.cols)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole):
            return self.rows[index.row()][index.column()]
        if role == Qt.TextAlignmentRole:
            if index.column() in (1,2,6): return Qt.AlignRight|Qt.AlignVCenter
            return Qt.AlignLeft|Qt.AlignVCenter
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole: return None
        return self.cols[section] if orientation==Qt.Horizontal else section+1
    def flags(self, index): return Qt.ItemIsSelectable|Qt.ItemIsEnabled
    def sort(self, column, order):
        reverse = (order==Qt.DescendingOrder)
        def kb_key(s):
            try: return float((s or "0").replace("KB",""))
            except: return 0.0
        def mb_key(s):
            try: return float((s or "0").replace("MB",""))
            except: return 0.0
        kmap = {
            "IP":lambda r:r[0],
            "PORT":lambda r:(-1 if r[1]=='-' else int(r[1])) if str(r[1]).isdigit() else -1,
            "DATA":lambda r:kb_key(r[2]),
            "COUNTRY":lambda r:r[3],
            "IP NAME":lambda r:r[4],
            "ADDED":lambda r:r[5],
            "DATA TOTAL":lambda r:mb_key(r[6]),
            "ACTION":lambda r:0
        }
        k = kmap[self.cols[column]]
        self.layoutAboutToBeChanged.emit(); self.rows.sort(key=k, reverse=reverse); self.layoutChanged.emit()
    def setRows(self, rows):
        self.layoutAboutToBeChanged.emit(); self.rows = rows; self.layoutChanged.emit()

# ----------- App
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vinewood Butcher")
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning))
        self.resize(1500, 880)

        # dark theme
        p = QPalette()
        p.setColor(QPalette.Window, QColor(18,20,24))
        p.setColor(QPalette.Base, QColor(24,26,32))
        p.setColor(QPalette.AlternateBase, QColor(28,30,36))
        p.setColor(QPalette.Text, QColor(236,236,240))
        p.setColor(QPalette.WindowText, QColor(236,236,240))
        p.setColor(QPalette.Button, QColor(34,36,42))
        p.setColor(QPalette.ButtonText, QColor(240,240,245))
        self.setPalette(p)
        self.setStyleSheet("""
            QTableView { gridline-color:#2e3138; selection-background-color:#3a7afe; selection-color:#fff; font-size:14px;
                background:#181a1e; alternate-background-color:#1e2026; border:1px solid #2a2d34; border-radius:12px; }
            QHeaderView::section { background:#20232a; color:#dfe3ea; padding:10px 12px; border:0; border-right:1px solid #2e3138; font-weight:600; }
            QLabel { color:#cdd3dd; font-size:13px; }
            QPushButton { background:#2b2f38; color:#e9edf5; padding:6px 12px; border:0; border-radius:10px; }
            QPushButton:hover { background:#364156; } QPushButton:pressed { background:#2a3447; }
            QFrame#Card { background:#1b1e24; border:1px solid #2a2d34; border-radius:14px; }
            QLabel#Metric { color:#e9edf5; font-size:24px; font-weight:700; }
            QLabel#MetricLabel { color:#9aa3b2; font-size:12px; }
            QLabel#Desc { color:#aeb6c3; font-size:12.5px; }
            QLabel#Pill { background:#222730; border:1px solid #2c3340; border-radius:8px; padding:4px 8px; color:#dfe6f3; font-weight:600; }
            QLabel#Overlay { color:#dfe6f3; font-size:15px; }
        """)

        # ===== Header
        self.card = QFrame(); self.card.setObjectName("Card")
        grid = QGridLayout(self.card); grid.setContentsMargins(14,14,14,14); grid.setHorizontalSpacing(18); grid.setVerticalSpacing(10)

        self.lblUptimeVal = QLabel("0s"); self.lblUptimeVal.setObjectName("Metric")
        self.lblUptimeKey = QLabel("UPTIME"); self.lblUptimeKey.setObjectName("MetricLabel")

        self.lblPlayersVal= QLabel("0"); self.lblPlayersVal.setObjectName("Metric")
        self.lblPlayersKey= QLabel("PLAYERS IN GAME"); self.lblPlayersKey.setObjectName("MetricLabel")

        self.lblIfaceVal  = QLabel("—"); self.lblIfaceVal.setObjectName("Metric")
        self.lblIfaceKey  = QLabel("INTERFACE"); self.lblIfaceKey.setObjectName("MetricLabel")

        self.lblLocalKey = QLabel("LOCAL IP"); self.lblLocalKey.setObjectName("MetricLabel")
        self.lblLocalVal = QLabel("—");        self.lblLocalVal.setObjectName("Metric")

        self.lblPubKey = QLabel("PUBLIC IP");  self.lblPubKey.setObjectName("MetricLabel")
        self.lblPubVal = QLabel("—");          self.lblPubVal.setObjectName("Metric")

        intro_text = random.choice(INTRO_LINES)
        self.lblDesc = QLabel(f"Live monitor des pairs (GTA p2p) — {intro_text}")
        self.lblDesc.setObjectName("Desc"); self.lblDesc.setWordWrap(True)

        grid.addWidget(self.lblUptimeVal, 0, 0); grid.addWidget(self.lblUptimeKey, 1, 0)
        grid.addWidget(self.lblPlayersVal, 0, 1); grid.addWidget(self.lblPlayersKey, 1, 1)
        grid.addWidget(self.lblIfaceVal, 0, 2);   grid.addWidget(self.lblIfaceKey, 1, 2)
        grid.addWidget(self.lblLocalVal, 0, 3);   grid.addWidget(self.lblLocalKey, 1, 3)
        grid.addWidget(self.lblPubVal,   0, 4);   grid.addWidget(self.lblPubKey,   1, 4)
        grid.addWidget(self.lblDesc, 2, 0, 1, 5)

        # ===== Tableau + overlay
        self.model = PeersModel()
        self.table = QTableView(); self.table.setModel(self.model)
        self.table.setSortingEnabled(True); self.table.setAlternatingRowColors(True)
        hh = self.table.horizontalHeader(); hh.setStretchLastSection(True); hh.setSectionsMovable(True); hh.setSectionsClickable(True)
        self.table.setItemDelegateForColumn(3, CountryDelegate())  # COUNTRY
        self.table.setColumnWidth(0, 260); self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 120); self.table.setColumnWidth(3, 260)
        self.table.setColumnWidth(4, 160)  # IP NAME
        self.table.setColumnWidth(5, 120)  # ADDED
        self.table.setColumnWidth(6, 130)  # DATA TOTAL
        self.table.setColumnWidth(7, 120)  # ACTION

        self.stack = QStackedLayout(); self.stack.setContentsMargins(0,0,0,0)
        self.stack.addWidget(self.table)
        self.overlay = QFrame(); self.overlay.setObjectName("Card")
        ov = QVBoxLayout(self.overlay); ov.setContentsMargins(24,24,24,24)
        self.lblOverlay = QLabel("Connection established…\n« Encrypting your sister’s nudes for extra bandwidth. » 🔐")
        self.lblOverlay.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter); self.lblOverlay.setObjectName("Overlay")
        ov.addStretch(1); ov.addWidget(self.lblOverlay); ov.addStretch(2)
        self.stack.addWidget(self.overlay)

        # ===== Graph
        self.chart = pg.PlotWidget()
        self.chart.setBackground("#13151a")
        self.chart.getAxis("left").setPen(pg.mkPen("#8992a3"))
        self.chart.getAxis("bottom").setPen(pg.mkPen("#8992a3"))
        self.chart.getAxis("left").setTextPen("#cdd3dd")
        self.chart.getAxis("bottom").setTextPen("#cdd3dd")
        self.chart.setTitle("Close players", color="#dfe3ea", size="12pt")
        self.chart.setLabel('left', 'Data (KB/s)')
        vb = self.chart.getViewBox(); vb.setMenuEnabled(False); vb.setMouseEnabled(False, False)
        self.chart.setMouseEnabled(x=False, y=False); self.chart.hideButtons()

        # Y max persistant
        self.ymax_hold = 0.0
        self.ymax_last_reset = time.time()
        self.ymax_reset_period = 30.0

        # Barres + animation
        self.bar_xs = list(range(5))
        self.bars = []
        self.current_y = [0.0]*5
        self.vel_y     = [0.0]*5
        self.target_y  = [0.0]*5
        self.wobble_phase = [random.uniform(0, 2*math.pi) for _ in range(5)]
        self.anim_enabled = True

        for i in range(5):
            b = pg.BarGraphItem(x=[i], height=[0.0], width=0.8, brush="#3a7afe")
            self.chart.addItem(b)
            self.bars.append(b)

        # animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._tick_anim)
        self.anim_timer.start(16)
        self.last_anim_ts = time.time()

        # ===== Layout principal
        split = QSplitter(Qt.Vertical)
        w_top = QtWidget(); lt = QVBoxLayout(w_top); lt.setContentsMargins(0,0,0,0); lt.setSpacing(12)
        lt.addWidget(self.card)
        body = QFrame(); body.setObjectName("Card")
        bodyLay = QVBoxLayout(body); bodyLay.setContentsMargins(10,10,10,10); bodyLay.addLayout(self.stack)
        lt.addWidget(body)
        w_bot = QtWidget(); lb = QVBoxLayout(w_bot); lb.setContentsMargins(0,0,0,0); lb.addWidget(self.chart)
        split.addWidget(w_top); split.addWidget(w_bot); split.setSizes([520,240])

        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.addWidget(split)

        # ===== Timers
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.setInterval(int(interval_ui*1000)); self.timer.start()
        self.model.layoutChanged.connect(self.install_action_buttons)

        self._boot_phase = True
        self.stack.setCurrentIndex(1)

    def _make_pcm_qbytearray(self, melody, sr=44100):
        import math, struct
        buf = bytearray()
        amp = 0.45
        for freq, dur in melody:
                n = int(sr * dur)
                if freq <= 0:
                        buf.extend(b"\x00\x00" * n)
                        continue
                phase = 0.0
                incr = (2*math.pi*freq)/sr
                for _ in range(n):
                        phase += incr
                        # onde triangle légère pour un côté 8-bit
                        s = (2/math.pi) * math.asin(math.sin(phase))
                        v = int(max(-1.0, min(1.0, s*amp)) * 32767)
                        buf.extend(struct.pack("<h", v))
        return QByteArray(bytes(buf))

    def play_startup_music(self):
        self._audio_format = QAudioFormat()
        self._audio_format.setSampleRate(44100)
        self._audio_format.setChannelCount(1)
        self._audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        # petite signature "GTA admin": trois notes + montée rapide
        melody = [
                (659.25,0.16),(622.25,0.16),(659.25,0.16),(622.25,0.16),(659.25,0.16),(493.88,0.12),(587.33,0.12),(523.25,0.16),(440.00,0.24),
                (0,0.04),
                (261.63,0.12),(329.63,0.12),(440.00,0.12),(493.88,0.20),
                (0,0.04),
                (329.63,0.12),(415.30,0.12),(493.88,0.12),(523.25,0.20),
                (0,0.04),
                (329.63,0.12),(659.25,0.16),(622.25,0.16),(659.25,0.16),(622.25,0.16),(659.25,0.16),(493.88,0.12),(587.33,0.12),(523.25,0.16),(440.00,0.28),
                (0,0.04),
                (329.63,0.12),(523.25,0.12),(493.88,0.12),(440.00,0.20),
                (0,0.04),
                (261.63,0.12),(329.63,0.12),(440.00,0.12),(493.88,0.20),
                (0,0.04),
                (329.63,0.12),(415.30,0.12),(493.88,0.12),(523.25,0.20),
                (0,0.04),
                (329.63,0.12),(659.25,0.16),(622.25,0.16),(659.25,0.16),(622.25,0.16),(659.25,0.16),(493.88,0.12),(587.33,0.12),(523.25,0.16),(440.00,0.24),
                (0,0.08),
                (523.25,0.16),(493.88,0.16),(440.00,0.18),
                (0,0.06),
                (329.63,0.18),(440.00,0.22),(261.63,0.20),(220.00,0.32),
                (0,0.08)
        ]


        qba = self._make_pcm_qbytearray(melody, sr=44100)
        self._audio_buf = QBuffer()
        self._audio_buf.setData(qba)
        self._audio_buf.open(QIODevice.ReadOnly)

        self._audio_out = QAudioSink(self._audio_format, self)
        self._audio_out.setVolume(0.55)
        self._audio_out.start(self._audio_buf)


    # ========= helpers UI =========
    def on_action(self, ip):
        webbrowser.open("https://www.google.com", new=2)

    def _centered_action_widget(self, ip):
        container = QtWidget()
        hb = QHBoxLayout(container); hb.setContentsMargins(0,0,0,0); hb.setAlignment(Qt.AlignCenter)
        btn = QPushButton("💀 Slap it")
        btn.setCursor(Qt.PointingHandCursor); btn.setFixedHeight(28)
        btn.clicked.connect(lambda _, ip=ip: self.on_action(ip))
        hb.addWidget(btn)
        return container

    def install_action_buttons(self):
        for row in range(self.model.rowCount()):
            idx = self.model.index(row, 7)  # ACTION
            ip = self.model.index(row, 0).data()
            w = self._centered_action_widget(ip)
            self.table.setIndexWidget(idx, w)

    def _color_for_value_blue(self, y: float, ymax: float):
        if ymax <= 0:
            return pg.mkBrush("#3a7afe")
        t = max(0.0, min(1.0, y / ymax))
        c_low  = QColor(58, 122, 254)   # #3a7afe
        c_high = QColor(30, 58, 138)    # #1e3a8a
        col = lerp_color(c_low, c_high, t)
        return pg.mkBrush(col)

    def _color_for_value_red(self, y: float, ymax: float):
        if ymax <= 0:
            return pg.mkBrush("#7f1424")
        t = max(0.0, min(1.0, y / ymax))
        c_low  = QColor(127, 20, 36)    # sombre
        c_high = QColor(225, 29, 72)    # #e11d48
        col = lerp_color(c_low, c_high, t)
        return pg.mkBrush(col)

    def _tick_anim(self):
        if not self.anim_enabled:
            return

        now = time.time()
        dt = max(0.001, min(0.05, now - self.last_anim_ts))
        self.last_anim_ts = now

        k = 12.0
        c = 2.5 * math.sqrt(k)

        wobble_freq = 0.7
        wobble_amp_factor = 0.04

        updated_heights = []
        for i in range(5):
            y  = self.current_y[i]
            v  = self.vel_y[i]
            yt = self.target_y[i]

            acc = k * (yt - y) - c * v
            v += acc * dt
            y += v * dt

            self.wobble_phase[i] += 2 * math.pi * wobble_freq * dt
            wobble = (yt * wobble_amp_factor) * math.sin(self.wobble_phase[i])
            y_display = max(0.0, y + wobble)

            self.current_y[i] = y
            self.vel_y[i]     = v
            updated_heights.append(y_display)

        now_global = time.time()
        elapsed = now_global - start_time
        intro_anim = elapsed < (BOOT_WAIT - 1.0)  # 0..9s

        ymax_color = max(1.0, max(self.target_y) if self.target_y else 1.0)
        for i, b in enumerate(self.bars):
            brush = self._color_for_value_red(updated_heights[i], ymax_color) if intro_anim else self._color_for_value_blue(updated_heights[i], ymax_color)
            b.setOpts(height=[updated_heights[i]], brush=brush)

    # ========= refresh =========
    def refresh(self):
        now = time.time()
        refresh_gta()

        # boot phase (10s)
        self._boot_phase = (now - start_time) < BOOT_WAIT
        self.stack.setCurrentIndex(1 if self._boot_phase else 0)

        # header
        uptime = int(now - start_time)
        self.lblUptimeVal.setText(f"{uptime}s")
        self.lblIfaceVal.setText(iface_name or "—")
        self.lblLocalVal.setText(local_ip_detected or "—")
        self.lblPubVal.setText(you_public_ip or "—")

        # candidats
        cands = {}
        for ipk, m in list(peers.items()):
            if not m["presence"] or not m["presence"][-1]: continue
            if sum(m["presence"]) < 8: continue
            if not is_player(m, now): continue
            cands[ipk] = m

        rows = []
        deltas_kb = {}
        for ipk, m in cands.items():
            prev = prev_bytes.get(ipk, m["bytes"])
            delta = max(0.0, m["bytes"] - prev)
            prev_bytes[ipk] = m["bytes"]
            m["delta_bytes_last"] = delta

            port = top_port(m["rports"], m["lports"])
            cc = geo_cache.get(ipk, "?")
            name = COUNTRY_NAMES.get(cc, cc) if cc not in ("LAN","MC","?") else cc
            country_text = f"{cc} {name}" if cc not in ("LAN","MC","?") else cc
            added_str = ts_to_hms(m.get("first_seen", 0.0))
            data_kb = bytes_to_kb_str_2dec(delta)
            data_total_mb = bytes_to_mb_str_2dec(m["bytes"])
            ip_name = ip_to_index_name(ipk)

            rows.append([ipk, str(port), data_kb, country_text, ip_name, added_str, data_total_mb, ""])
            deltas_kb[ipk] = (delta / 1024.0)

        rows.sort(key=lambda x: (float(x[2].replace("KB","")), x[0]), reverse=True)

        if not self._boot_phase:
            self.model.setRows(rows)
            try:
                self.table.sortByColumn(2, Qt.DescendingOrder)
            except:
                pass
        else:
            self.model.setRows([])

        players_in_game = (len(rows) if not self._boot_phase else 0) + 1
        self.lblPlayersVal.setText(str(players_in_game))

        # ===== Graph =====
        elapsed = now - start_time
        remaining = BOOT_WAIT - elapsed

        if self._boot_phase:
            if remaining > 1.0:
                # 0..9s : animation rouge "pulse"
                self.anim_enabled = True
                t = elapsed
                phases = [0.0, 0.7, 1.4, 2.1, 2.8]
                base_amp = 90.0
                vals = []
                for i in range(5):
                    v = math.sin(2*math.pi*(0.9)*t + phases[i])
                    v = v*v
                    vals.append(base_amp * v + (8*i))

                self.target_y = vals[:]

                current_peak = max(vals) if vals else 1.0
                major = nice_step(current_peak, target_ticks=6)
                max_y_aligned = max(major, math.ceil(current_peak/major)*major)
                self.chart.getAxis("left").setTickSpacing(major, max(major*0.5, 1.0))
                self.chart.setYRange(0, max_y_aligned)

                self.chart.getAxis("bottom").setTicks([[(i, "") for i in range(5)]])
                return

            else:
                # dernière seconde : drapeau FR figé
                self.anim_enabled = False
                vals = [0.0, 100.0, 100.0, 100.0, 0.0]  # KB/s
                cols = [None, "#1e3a8a", "#ffffff", "#e11d48", None]
                self.current_y = vals[:]
                self.target_y  = vals[:]
                for i, b in enumerate(self.bars):
                    col = cols[i]; h = vals[i]
                    if col and h > 0:
                        b.setOpts(height=[h], brush=col)
                    else:
                        b.setOpts(height=[0.0], brush="#3a7afe")
                major = nice_step(100.0, target_ticks=6)
                max_y_aligned = max(major, math.ceil(100.0/major)*major)
                self.chart.getAxis("left").setTickSpacing(major, max(major*0.5, 1.0))
                self.chart.setYRange(0, max_y_aligned)
                self.chart.getAxis("bottom").setTicks([[(i, "") for i in range(5)]])
                return

        # Post-intro
        if not self.anim_enabled:
            self.anim_enabled = True

        # labels bas: IP · [CC]
        top_peers = sorted(deltas_kb.items(), key=lambda x: x[1], reverse=True)[:5]
        while len(top_peers) < 5:
            top_peers.append(("", 0.0))

        end_vals = []
        labels = []
        for ipk, val in top_peers:
            end_vals.append(val)
            if not ipk:
                labels.append("")
            else:
                cc = geo_cache.get(ipk, "?")
                labels.append(f"{ipk} · {cc}")
        self.chart.getAxis("bottom").setTicks([[(i, labels[i]) for i in range(5)]])

        # cibles
        self.target_y = end_vals[:]

        # Y max persistant + reset 30s
        if (now - self.ymax_last_reset) >= self.ymax_reset_period:
            self.ymax_hold = 0.0
            self.ymax_last_reset = now

        current_peak = max(end_vals) if end_vals else 0.0
        if current_peak > self.ymax_hold:
            self.ymax_hold = current_peak

        effective_max = max(1.0, self.ymax_hold)
        major = nice_step(effective_max, target_ticks=6)
        max_y_aligned = max(major, math.ceil(effective_max / major) * major)
        self.chart.getAxis("left").setTickSpacing(major, max(major * 0.5, 1.0))
        self.chart.setYRange(0, max_y_aligned)

# ----------- Bootstrap
def main():
    global iface_name, local_ip_detected, you_public_ip

    app = QApplication(sys.argv)
    w = App()
    w.show()
    QTimer.singleShot(0, w.play_startup_music)
    QApplication.processEvents()

    def boot_net():
        global iface_name, local_ip_detected, you_public_ip

        try:
            pub_ip = get_public_ip()
        except:
            pub_ip = outbound_ip()
        you_public_ip = pub_ip

        def ui_set_pub():
            w.lblPubVal.setText(you_public_ip or "—")
        QTimer.singleShot(0, ui_set_pub)

        name, local = detect_iface_with_fallback()
        iface_name_local = name or ""
        local_ip_detected_local = local or "—"

        def ui_set_iface():
            w.lblIfaceVal.setText(iface_name_local or "—")
            w.lblLocalVal.setText(local_ip_detected_local or "—")
        QTimer.singleShot(0, ui_set_iface)

        if not iface_name_local:
            return

        globals()['iface_name'] = iface_name_local
        globals()['local_ip_detected'] = local_ip_detected_local
        refresh_local()
        refresh_gta()

        if _have_rdap:
            threading.Thread(target=resolver_loop, daemon=True).start()
            threading.Thread(target=flag_loader_loop, daemon=True).start()
        threading.Thread(target=sniffer, daemon=True).start()
        threading.Thread(target=ticker, daemon=True).start()

    threading.Thread(target=boot_net, daemon=True).start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
