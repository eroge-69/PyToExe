# -*- coding: utf-8 -*-
# pip install PySide6
import sys
import os
import secrets
import random
import string
import json  # <-- [AUTOZAPIS] DODANE
from dataclasses import dataclass
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPalette, QColor
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QFrame, QGridLayout, QMessageBox  # <-- [AUTOZAPIS] DODANE QMessageBox
)

# ---------------------- Icons (inline SVG) ----------------------
COPY_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
 <path fill="currentColor"
  d="M16 1H4a2 2 0 0 0-2 2v12h2V3h12V1Zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Zm0 16H8V7h11v14Z"/>
</svg>
""".strip()

CHECK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
 <path fill="currentColor" d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/>
</svg>
""".strip()


def make_icon(svg: str) -> QIcon:
    pix = QPixmap()
    pix.loadFromData(svg.encode("utf-8"), "SVG")
    return QIcon(pix)


COPY_ICON: QIcon | None = None  # init after QApplication
CHECK_ICON: QIcon | None = None

CODES_FILE = "codes.txt"
AUTOSAVE_FILE = "autosave.json"  # <-- [AUTOZAPIS] DODANE

# ---------------------- Predefined snippets to copy ----------------------
TITLE_RU = "ChatGPT Plus  ( 3 месяца )  –  чистый аккаунт с полным доступом и почтой"
TITLE_EN = "ChatGPT Plus  ( 3 Months )  –  clean account with complete access and mail"
DESCRIPTION_TEXT = """Account details
 • ChatGPT Plus subscription on account is active for exactly 3 months from the date of purchase. The plan is fully paid for the entire 3-month period.
 • The account was created and activated by me personally.

Imporatnt note
 • If you cancel your subscription, switch to another plan or break the OpenAI Rules, no refunds will be issued. 

Mail site: https://outlook.live.com/
"""


# ---------------------- Data & profile generation ----------------------
@dataclass
class Dataset:
    country: str
    names: list[str]
    surnames: list[str]
    streets: list[str]
    cities: list[str]
    nickbits: list[str]


@dataclass
class Profile:
    name: str
    surname: str
    street: str
    city: str
    postal: str
    email: str
    password: str
    dob: str  # YYYY-MM-DD


# ---- Helpers ----
def ensure_codes_file():
    """Create codes.txt if missing and try to open it in Notepad (Windows)."""
    created = False
    if not os.path.exists(CODES_FILE):
        with open(CODES_FILE, "w", encoding="utf-8") as f:
            f.write("")
        created = True
        try:
            os.startfile(CODES_FILE)  # type: ignore[attr-defined]
        except Exception:
            pass
    return created


def load_codes() -> list[str]:
    try:
        with open(CODES_FILE, "r", encoding="utf-8") as f:
            return [ln.strip() for ln in f.readlines() if ln.strip()]
    except FileNotFoundError:
        ensure_codes_file()
        return []


def save_codes(codes: list[str]):
    with open(CODES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(codes) + ("\n" if codes else ""))



def title_case(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    out = []
    for w in s.split():
        parts = w.split("-")
        parts = ["".join([p[:1].upper(), p[1:].lower()]) if p else p for p in parts]
        out.append("-".join(parts))
    return " ".join(out)


def build_email(nick: str, domain: str = "outlook.com") -> str:
    suffix = f"{random.randint(0, 9999):04d}"
    max_local = 18
    if len(nick) + len(suffix) > max_local:
        cutoff = max(3, max_local - len(suffix))
        nick = nick[:cutoff]
    return f"{nick}{suffix}@{domain}"


def secure_password(length: int = 12) -> str:
    length = max(length, 12)
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{},.?/"   # no ':'
    allchars = lower + upper + digits + symbols
    pw = [
        secrets.choice(lower),
        secrets.choice(upper),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]
    while len(pw) < length:
        pw.append(secrets.choice(allchars))
    random.shuffle(pw)
    return "".join(pw)


def random_postal5() -> str:
    return f"{random.randint(10000, 99999):05d}"


def random_dob_18_30() -> str:
    today = datetime.now()
    youngest = today - timedelta(days=18*365 + 5)
    oldest = today - timedelta(days=30*365 + 8)
    total_days = (youngest - oldest).days
    if total_days < 0:
        total_days = 0
    d = oldest + timedelta(days=random.randint(0, total_days))
    return d.strftime("%Y-%m-%d")


def random_dob_18_34() -> str:
    """DOB 18–34 (inclusive-ish), formatted YYYY-MM-DD."""
    today = datetime.now()
    youngest = today - timedelta(days=18*365 + 5)
    oldest = today - timedelta(days=34*365 + 8)
    total_days = (youngest - oldest).days
    if total_days < 0:
        total_days = 0
    d = oldest + timedelta(days=random.randint(0, total_days))
    return d.strftime("%Y-%m-%d")


def pick(arr: list[str]) -> str:
    return random.choice(arr)


def build_nick(bits: list[str]) -> str:
    parts = [
        pick(bits).lower().replace(" ", ""),
        pick(bits).lower().replace(" ", ""),
    ]
    if random.randint(0, 1) == 0:
        parts.append(pick(bits).lower().replace(" ", ""))
    return "".join(parts)


def gen_names(prefixes: list[str], cores: list[str], suffixes: list[str], seeds: list[str], limit: int = 240) -> list[str]:
    """Randomly mixes prefix/core/suffix to produce a large unique pool of names."""
    seen = set()
    out = []
    for s in seeds:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            out.append(title_case(s))
    tries = limit * 25
    while len(out) < limit and tries > 0:
        n = f"{pick(prefixes)}{pick(cores)}{pick(suffixes)}".strip()
        n = title_case(n.replace("  ", " "))
        if n and n.lower() not in seen:
            out.append(n)
            seen.add(n.lower())
        tries -= 1
    return out


def gen_profile(ds: Dataset, domain: str = "outlook.com") -> Profile:
    name = pick(ds.names)
    surname = pick(ds.surnames)
    street = f"{pick(ds.streets)} {random.randint(1, 200)}"
    city = pick(ds.cities)
    postal = random_postal5()
    nick = build_nick(ds.nickbits)
    email = build_email(nick, domain)   # <-- tu używamy wybranej domeny
    password = secure_password(12)
    dob = random_dob_18_34()
    return Profile(
        name=name, surname=surname, street=street, city=city, postal=postal,
        email=email, password=password, dob=dob
    )


# ---------------------- Datasets (expanded) ----------------------
# --- Vietnam ---
VN_SEED = [
    "Anh","Bao","Binh","Chau","Cong","Danh","Duc","Duy","Giang","Hai",
    "Han","Hanh","Hao","Hieu","Hoa","Hoang","Hue","Hung","Khanh","Khoa",
    "Kien","Lam","Lan","Linh","Long","Mai","Minh","My","Nam","Nga","Ngoc",
    "Nghia","Nhi","Phong","Phuc","Phuong","Quang","Quyen","Son","Tam","Tan",
    "Thao","Thi","Thien","Thinh","Thuy","Tien","Tuan","Tung","Van","Vy",
]
VN_PREFIX = [
    "An","Bao","Bich","Cam","Chi","Cong","Dai","Dang","Dao","Diem","Dieu","Doan","Duc","Dung","Duong",
    "Gia","Giang","Hai","Han","Hanh","Hao","Ha","Hieu","Hoa","Hoai","Hoang","Hong","Huong","Hue","Huy","Huyen",
    "Khanh","Khang","Khoa","Khue","Kim","Kien","Lam","Lan","Le","Linh","Loan","Long","Luu","Ly","Mai","Manh",
    "Minh","My","Nam","Ngan","Nga","Ngoc","Nghia","Nhi","Nhu","Nhan","Phan","Phat","Phong","Phu","Phuc","Phuong",
    "Quang","Quoc","Quyen","Quynh","Son","Tam","Tan","Thanh","Thao","Thien","Thinh","Thi","Thoa","Thuan","Thuy",
    "Tien","Tin","Tinh","Toan","Trang","Trieu","Trinh","Truc","Trung","Tuan","Tu","Tung","Uy","Van","Vi","Viet","Vinh","Vy","Xuan","Yen"
]
VN_CORE = [
    "","a","ai","am","an","anh","ao","ap","at","au","ay","e","em","en","eu","ha","han","hao","hien","hoa","hoang","hue","huong",
    "ien","i","im","inh","io","iu","khanh","khoa","lam","lan","linh","long","mai","minh","my","nam","ngan","nghia","nhi","nhu",
    "phong","phuc","phuong","quang","quyen","son","tam","tan","thao","thien","thinh","thuy","tien","tuan","tung","van","viet","vinh","xuan","yen"
]
VN_SUFFIX = [
    ""," An"," Anh"," Bao"," Binh"," Chau"," Chi"," Dung"," Giang"," Ha"," Hai"," Han"," Hanh"," Hao"," Hieu"," Hoa"," Hoai"," Hoang"," Hong",
    " Hue"," Hung"," Khanh"," Khoa"," Kim"," Lam"," Lan"," Linh"," Long"," Mai"," Minh"," My"," Nam"," Nga"," Ngoc"," Nghia"," Nhi"," Nhu",
    " Phong"," Phuc"," Phuong"," Quang"," Quyen"," Son"," Tam"," Tan"," Thanh"," Thao"," Thi"," Thien"," Thinh"," Thuy"," Tien"," Trang"," Trung",
    " Tuan"," Tung"," Van"," Viet"," Vinh"," Vy"," Xuan"," Yen"
]
VN_SURNAMES = [
    "Nguyen","Tran","Le","Pham","Hoang","Huynh","Phan","Vu","Vo","Dang","Bui","Do","Ho","Ngo","Duong","Ly","Truong","Dinh","Mai","Trinh",
    "Cao","Chau","Dao","Luu","Dang Khoa","Quach","Quang","Quoc","Vuong","Phung","Phuong","Son","Tam","Tan","Thanh","Thao","Thi","Thien","Thinh",
    "Thuy","Tien","Trang","Trung","Tuan","Tung","Van","Viet","Vinh","Xuan","Yen"
]
VN_STREETS = [
    "Le Loi","Nguyen Trai","Tran Hung Dao","Pham Ngu Lao","Hai Ba Trung","Dien Bien Phu","Ly Thuong Kiet","Vo Van Tan","Nguyen Hue","Nam Ky Khoi Nghia",
    "Bach Dang","Hoang Dieu","Le Thanh Ton","Ton Duc Thang","Cach Mang Thang Tam","Pasteur","Pham Van Dong","Vo Nguyen Giap","Tran Phu","Le Duan",
    "Nguyen Thi Minh Khai","Nguyen Van Cu","Pham Hung","Pham Huu Lau","Tran Quoc Toan","Tran Nhan Tong","Cao Thang","Mac Dinh Chi","Ba Trieu","Le Quy Don",
    "Ly Chinh Thang","Nguyen Thai Hoc","Dang Van Ngu","Truong Dinh","Hoang Van Thu","Phan Dinh Phung","Phan Xich Long","Nguyen Huu Canh","Nguyen Van Linh","Le Van Sy"
]
VN_CITIES = [
    "Hanoi","Ho Chi Minh City","Da Nang","Hai Phong","Can Tho","Hue","Nha Trang","Vung Tau","Bien Hoa","Da Lat","Quy Nhon","Buon Ma Thuot",
    "Hai Duong","Thanh Hoa","Vinh","Thai Nguyen","Nam Dinh","Rach Gia","Long Xuyen","Soc Trang","Vinh Long","Phan Thiet","Phan Rang–Thap Cham",
    "Cam Ranh","Ha Long","Uong Bi","Bac Ninh","Bac Giang","Lang Son","Lao Cai","Yen Bai","Son La","Hoa Binh","Thai Binh","Quang Ngai","Quang Nam",
    "Tam Ky","Kon Tum","Pleiku","Tuy Hoa","My Tho","Ben Tre","Tra Vinh","Cao Lanh","Sa Dec","Tay Ninh","Moc Chau","Dong Hoi","Dong Ha"
]
VN_NICKBITS = [
    "viet","saigon","hanoi","mekong","pho","banh","dragon","lotus","rice","delta","bamboo","ao dai","tet","coffee","nuocmam","cyclo"
]

# --- Indonesia ---
ID_SEED = [
    "Adi","Agus","Aji","Andi","Ayu","Bagus","Bambang","Bayu","Budi","Citra","Dewi","Dian","Dimas","Dwi","Eka","Fajar","Fitri","Gita","Hadi","Hana",
    "Hendra","Indah","Intan","Irfan","Joko","Kartika","Lestari","Made","Mega","Nanda","Putra","Putri","Rama","Rani","Rizky","Satya","Sari","Sinta","Teguh",
    "Tika","Tono","Utami","Wahyu","Wawan","Yanto","Yuni"
]
ID_PREFIX = [
    "Adi","Agus","Aji","Ayu","Arya","Ari","Anak","Andi","Anik","Anita","Ardi","Arga","Bagus","Banyu","Bima","Budi","Cahya","Citra","Dedi","Dewi","Dian",
    "Dika","Dimas","Dinda","Doni","Dwi","Eko","Eka","Fajar","Fani","Fitri","Galang","Gita","Gilang","Hadi","Hana","Hendra","Indah","Intan","Iqbal","Irfan",
    "Jati","Joko","Kadek","Kartika","Kusuma","Lestari","Made","Mahendra","Mega","Nanda","Naufal","Nia","Nur","Putra","Putri","Raden","Rama","Rani","Rizky",
    "Rizal","Sari","Satria","Satya","Shinta","Siska","Sri","Surya","Teguh","Tika","Tirta","Tito","Tri","Utami","Wahyu","Wawan","Wira","Yanto","Yoga","Yogi","Yulia","Yuni","Zaki"
]
ID_CORE = [
    "","a","adi","aka","ana","ani","ara","ari","arto","awan","ayu","eka","endra","gita","giri","guna","ika","ima","ina","ing","inta","ira","ita",
    "ono","ona","rama","rani","ria","rio","riza","rizky","sari","sono","surya","tama","tami","tomo","tri","yanto","yudha","yoga"
]
ID_SUFFIX = [
    ""," Adi"," Agus"," Aji"," Andi"," Arya"," Ayu"," Bagus"," Bambang"," Bayu"," Budi"," Cahya"," Citra"," Dedi"," Dewi"," Dian"," Dimas"," Dwi"," Eka",
    " Fajar"," Fitri"," Galang"," Gita"," Hadi"," Hana"," Hendra"," Indah"," Intan"," Iqbal"," Irfan"," Joko"," Kartika"," Lestari"," Made"," Mega"," Nanda",
    " Putra"," Putri"," Rama"," Rani"," Rizky"," Satya"," Sari"," Sinta"," Teguh"," Tika"," Tono"," Utami"," Wahyu"," Wawan"," Yanto"," Yuni"
]
ID_SURNAMES = [
    "Santoso","Wijaya","Saputra","Pratama","Nugroho","Hidayat","Setiawan","Wibowo","Permata","Ramadhan","Putra","Putri",
    "Siregar","Nasution","Simanjuntak","Sihombing","Situmorang","Hutabarat","Hutagalung","Siagian","Panjaitan","Tampubolon","Harahap","Hasibuan","Lubis","Gultom",
    "Sinaga","Nainggolan","Hutasoit","Tambunan","Sipayung","Mahendra","Kusuma","Kurniawan","Suprapto","Subroto","Ardian","Pamungkas","Firmansyah","Prasetyo","Rahman",
    "Syahputra","Kurnia","Sari","Gunawan","Angkasa","Wahyuni","Puspasari","Rahayu","Yulianto","Handayani"
]
ID_STREETS = [
    "Jalan Sudirman","Jalan Thamrin","Gatot Subroto","Asia Afrika","Malioboro","Diponegoro","Ahmad Yani","Imam Bonjol","Mangga Dua","Veteran",
    "Gajah Mada","Merdeka","Pahlawan","Rajawali","Cendana","Kenanga","Melati","Anggrek","Cemara","Kelapa",
    "Kamboja","Flamboyan","Sawo","Durian","Semangka","Rambutan","Jeruk","Nangka","Sirsak","Pepaya",
    "Merpati","Elang","Rajawali Timur","Rajawali Barat","Cendrawasih","Kenari","Maleo","Jalak","Trunojoyo","Kertajaya"
]
ID_CITIES = [
    "Jakarta","Surabaya","Bandung","Medan","Semarang","Makassar","Palembang","Bogor","Depok","Tangerang","Bekasi","Yogyakarta","Denpasar","Malang","Padang",
    "Pekanbaru","Pontianak","Samarinda","Balikpapan","Banjarmasin","Manado","Ambon","Jayapura","Kupang","Mataram","Bandar Lampung","Palangkaraya","Palu","Kendari",
    "Ternate","Tanjung Pinang","Batam","Cirebon","Solo","Magelang","Tasikmalaya","Cimahi","Serang","Karawang","Cianjur","Garut","Purwokerto","Salatiga","Kediri","Blitar"
]
ID_NICKBITS = [
    "indo","nusantara","garuda","java","bali","sumatra","borneo","batik","sate","kopi","wayang","angklung","monas","borobudur","komodo","rendang"
]

# --- Thailand ---
TH_SEED = [
    "Anan","Anong","Apichai","Apinya","Arthit","Boonmee","Chai","Chanya","Chavalit","Chompoo","Kanya","Kamon","Krit","Lalana","Malee","Mintra","Natee","Niran","Nisa","Nong",
    "Pailin","Paweena","Ploy","Prasert","Rak","Ratchanok","Rung","Sakda","Somsak","Somchai","Somjit","Suda","Sukanya","Supaporn","Tanin","Thana","Thanya","Tida","Wannee","Warit","Wipa","Wiriya","Yada","Ying","Yupa"
]
TH_PREFIX = [
    "Anan","Anong","Api","Apin","Arth","Boon","Chai","Chan","Chanya","Charoen","Chaval","Chom","Decha","Kanya","Kamon","Krit","Lala","Malee","Min","Natee","Niran","Nisa","Nong",
    "Pailin","Pawee","Ploy","Pras","Prasit","Prasert","Ratcha","Rung","Sak","Somsak","Somchai","Somjit","Suda","Sukanya","Supha","Tanin","Thana","Thanya","Tida","Wan","Warit","Wipa","Wiriya","Yada","Ying","Yupa","Phan","Phat","Phon","Phrai","Phu","Than","Wor","Wit"
]
TH_CORE = [
    "","a","ai","am","an","ap","ar","at","aya","chai","chaiya","chon","chot","da","dee","don","fon","ika","il","in","ira","isa","ith","korn","krit","kri","krai",
    "lak","lal","lam","lan","lin","lert","lop","lue","mai","man","manee","metha","nart","natee","nee","nisa","nont","pan","phat","phon","phong","pong","prasert","rat","ratt","rit","rom","ruk","sak","san","siri","som","sri","suk","sup","tada","tana","tarn","thorn","thong","thip","thit","wan","warit","wit","wut","ya","yod"
]
TH_SUFFIX = [
    ""," Anan"," Anong"," Apichai"," Apinya"," Arthit"," Boonmee"," Chai"," Chanya"," Chavalit"," Chompoo"," Kanya"," Kamon"," Krit"," Lalana"," Malee"," Mintra"," Natee"," Niran"," Nisa"," Nong",
    " Pailin"," Paweena"," Ploy"," Prasert"," Rak"," Ratchanok"," Rung"," Sakda"," Somsak"," Somchai"," Somjit"," Suda"," Sukanya"," Supaporn"," Tanin"," Thana"," Thanya"," Tida"," Wannee"," Warit"," Wipa"," Wiriya"," Yada"," Ying"," Yupa"
]
TH_SURNAMES = [
    "Srisai","Sukprasert","Wongchai","Sittichai","Boonsong","Rattanakorn","Thongchai","Suksan","Chaisiri","Kittisak","Pradchaphet","Sangtong","Praphan","Srisawat","Pongchai",
    "Khamsuk","Chantarangsu","Panyachon","Dechawong","Inthanon","Phromphong","Srivicha","Sripong","Srisuk","Srisuwan","Srithep","Suriyapong","Suriyawong","Yuttana","Nithisak","Phanuphong",
    "Anuwat","Boonmee","Boonprasit","Boonthong","Charoen","Chavalit","Chompoonuch","Jirachot","Jirasak","Kachasong","Khamin","Khattiya","Kittikhun","Kongdej","Laopracha","Lertwong",
    "Metha","Mongkol","Nattapong","Niran","Pannasak","Phantharak","Phayap","Phromsak","Punyawong","Ratchapol","Rattanapong","Rungsak","Sawatdee","Siripong","Songkram","Suthida"
]
TH_STREETS = [
    "Sukhumvit","Silom","Rama I","Rama II","Rama III","Rama IV","Rama IX","Ratchada","Phetchaburi","Lat Phrao","Charoen Krung","Yaowarat","Phahonyothin","Vibhavadi",
    "Sathorn","Asok","Ekkamai","Thonglor","Chang Klan","Nimmanhaemin","Huay Kaew","Sirindhorn","Ratchaphruek","Ratchadamri","Phra Athit","Siphraya","Chan Road","Nawamin",
    "Kaset-Nawamin","Ratchadaphisek","Bang Na-Trat","Krung Thon Buri","Charoen Nakhon","Borommaratchachonnani","Pracha Uthit","Ram Inthra","Ratchawithi","Samsen","Udom Suk"
]
TH_CITIES = [
    "Bangkok","Chiang Mai","Chiang Rai","Phuket","Pattaya","Hat Yai","Nakhon Ratchasima","Udon Thani","Khon Kaen","Ayutthaya","Surat Thani","Krabi","Lampang","Nakhon Sawan",
    "Nakhon Si Thammarat","Songkhla","Nakhon Pathom","Nonthaburi","Pathum Thani","Samut Prakan","Rayong","Chonburi","Trat","Chanthaburi","Prachuap Khiri Khan","Hua Hin","Chiang Saen",
    "Mae Sot","Loei","Sukhothai","Ubon Ratchathani","Uthai Thani","Lopburi","Suphanburi","Phitsanulok","Phichit","Nakhon Nayok","Ranong","Satun","Trang","Yala","Narathiwat"
]
TH_NICKBITS = [
    "thai","siam","bangkok","muay","mango","chao","khun","chang","sabai","smile","krungthep","tuk","songkran","tomyum","thaitea","isaan","wai","ramakien","gulf"
]


def vn_dataset() -> Dataset:
    names = gen_names(VN_PREFIX, VN_CORE, VN_SUFFIX, VN_SEED, limit=260)
    return Dataset(
        country="Vietnam",
        names=names,
        surnames=[title_case(s) for s in VN_SURNAMES],
        streets=[title_case(s) for s in VN_STREETS],
        cities=[title_case(s) for s in VN_CITIES],
        nickbits=VN_NICKBITS,
    )


def id_dataset() -> Dataset:
    names = gen_names(ID_PREFIX, ID_CORE, ID_SUFFIX, ID_SEED, limit=260)
    return Dataset(
        country="Indonesia",
        names=names,
        surnames=[title_case(s) for s in ID_SURNAMES],
        streets=[title_case(s) for s in ID_STREETS],
        cities=[title_case(s) for s in ID_CITIES],
        nickbits=ID_NICKBITS,
    )


def th_dataset() -> Dataset:
    names = gen_names(TH_PREFIX, TH_CORE, TH_SUFFIX, TH_SEED, limit=260)
    return Dataset(
        country="Thailand",
        names=names,
        surnames=[title_case(s) for s in TH_SURNAMES],
        streets=[title_case(s) for s in TH_STREETS],
        cities=[title_case(s) for s in TH_CITIES],
        nickbits=TH_NICKBITS,
    )


DATASETS: dict[str, Dataset] = {
    "Vietnam": vn_dataset(),
    "Indonesia": id_dataset(),
    "Thailand": th_dataset(),
}


# ---------------------- UI ----------------------
class CopyLabelRow(QFrame):
    def __init__(self, label_text: str, value_text: str, copy_payload: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("CopyLabelRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.key = QLabel(label_text)
        self.key.setObjectName("RowKey")
        self.val = QLabel(value_text)
        self.val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.val.setObjectName("RowValue")

        layout.addWidget(self.key)
        layout.addStretch(1)
        layout.addWidget(self.val)

        btn = QPushButton()
        btn.setIcon(COPY_ICON)
        btn.setFixedSize(QSize(28, 28))
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: QGuiApplication.clipboard().setText(copy_payload or value_text))
        btn.setObjectName("CopyBtn")
        layout.addWidget(btn)

    def set_value(self, value: str):
        self.val.setText(value)


class PlainLabelRow(QFrame):
    """Row without a copy button (for DOB)."""
    def __init__(self, label_text: str, value_text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("CopyLabelRow")  # reuse styles
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.key = QLabel(label_text)
        self.key.setObjectName("RowKey")
        self.val = QLabel(value_text)
        self.val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.val.setObjectName("RowValue")

        layout.addWidget(self.key)
        layout.addStretch(1)
        layout.addWidget(self.val)


class ProfileCard(QFrame):
    def __init__(self, profile: Profile, country: str, index: int, promo_code: str, on_done, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.promo_code = promo_code
        self.on_done = on_done
        self.profile = profile              # <-- [MASS UPLOAD/AUTOZAPIS] DODANE
        self.is_done = False                # <-- [MASS UPLOAD] DODANE

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)

        header = QLabel(f"Profile #{index} — {country}")
        header.setObjectName("CardHeader")
        lay.addWidget(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        def add_row(r, label, value, payload=None):
            row = CopyLabelRow(label, value, payload, self)
            grid.addWidget(row, r, 0)
            return row

        full_name = f"{profile.name} {profile.surname}"
        addr_line = f"{profile.street}"  # address first line only
        combo_val = f"{profile.email}:{profile.password}"
        nick = profile.email.split("@")[0]

        self.mail_row   = add_row(0, "Email", profile.email)
        self.pass_row   = add_row(1, "Password", profile.password)
        self.combo_row  = add_row(2, "Combo", combo_val, combo_val)  # email:password
        self.nick_row   = add_row(3, "Nick", nick, nick)             # NEW: Nick with copy
        self.name_row   = add_row(4, "Full name", full_name, full_name)
        self.addr_row   = add_row(5, "Address", addr_line, addr_line)
        self.zip_row    = add_row(6, "ZIP", profile.postal)
        self.city_row   = add_row(7, "City", profile.city)
        self.dob_row    = PlainLabelRow("Date of birth", profile.dob)  # NEW: DOB no copy
        grid.addWidget(self.dob_row, 8, 0)
        self.promo_row  = add_row(9, "Promo code", promo_code if promo_code else "(none)")

        lay.addLayout(grid)

        # Done button – removes assigned promo code from file
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.done_btn = QPushButton("Done")
        self.done_btn.setIcon(CHECK_ICON)
        self.done_btn.setCursor(Qt.PointingHandCursor)
        self.done_btn.clicked.connect(self.handle_done)
        btn_row.addWidget(self.done_btn)
        lay.addLayout(btn_row)

    def handle_done(self):
        if not self.promo_code:
            self.done_btn.setEnabled(False)
            return
        ok = self.on_done(self.promo_code)
        if ok:
            self.promo_code = ""
            self.promo_row.set_value("(used)")
            self.done_btn.setEnabled(False)
            self.is_done = True           # <-- [MASS UPLOAD] DODANE


class MainWindow(QWidget):
    OUTLOOK_URL = "https://outlook.live.com/mail/0/?prompt=create_account"
    CHATGPT_URL = "https://chatgpt.com/"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Data Generator v1.0.0 @oxygenic")
        self.resize(1120, 820)
        self.setObjectName("Root")

        self.current_profiles: list[Profile] = []
        self.codes: list[str] = []

        ensure_codes_file()
        self.codes = load_codes()

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.country = QComboBox()
        self.country.addItems(list(DATASETS.keys()))
        self.country.setObjectName("Combo")
        toolbar.addWidget(QLabel("Country:"))
        toolbar.addWidget(self.country)

        gen_btn = QPushButton("Generate")
        gen_btn.setCursor(Qt.PointingHandCursor)
        gen_btn.clicked.connect(self.generate_profiles)
        gen_btn.setObjectName("Primary")
        toolbar.addWidget(gen_btn)

        mass_btn = QPushButton("Mass upload")
        mass_btn.setIcon(COPY_ICON)
        mass_btn.setCursor(Qt.PointingHandCursor)
        mass_btn.setToolTip("Copy email:password:email:password for DONE profiles only")  # <-- [MASS UPLOAD] ZMIANA PODPOWIEDZI
        mass_btn.clicked.connect(self.copy_massdata)
        toolbar.addWidget(mass_btn)

        self.email_domain = QComboBox()
        self.email_domain.addItems(["outlook.com", "int.pl"])
        self.email_domain.setObjectName("Combo")
        toolbar.addWidget(QLabel("Email domain:"))
        toolbar.addWidget(self.email_domain)

        toolbar.addStretch(1)

        btn_outlook = QPushButton("Outlook")
        btn_outlook.setIcon(COPY_ICON)
        btn_outlook.setCursor(Qt.PointingHandCursor)
        btn_outlook.setToolTip(self.OUTLOOK_URL)
        btn_outlook.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.OUTLOOK_URL))
        toolbar.addWidget(btn_outlook)

        btn_chatgpt = QPushButton("ChatGPT")
        btn_chatgpt.setIcon(COPY_ICON)
        btn_chatgpt.setCursor(Qt.PointingHandCursor)
        btn_chatgpt.setToolTip(self.CHATGPT_URL)
        btn_chatgpt.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.CHATGPT_URL))
        toolbar.addWidget(btn_chatgpt)

        # New snippet copy buttons (RU/EN titles + description)
        btn_title_ru = QPushButton("Title (RU)")
        btn_title_ru.setIcon(COPY_ICON)
        btn_title_ru.setCursor(Qt.PointingHandCursor)
        btn_title_ru.setToolTip("Copy Russian title")
        btn_title_ru.clicked.connect(lambda: QGuiApplication.clipboard().setText(TITLE_RU))
        toolbar.addWidget(btn_title_ru)

        btn_title_en = QPushButton("Title (EN)")
        btn_title_en.setIcon(COPY_ICON)
        btn_title_en.setCursor(Qt.PointingHandCursor)
        btn_title_en.setToolTip("Copy English title")
        btn_title_en.clicked.connect(lambda: QGuiApplication.clipboard().setText(TITLE_EN))
        toolbar.addWidget(btn_title_en)

        btn_descr = QPushButton("Description")
        btn_descr.setIcon(COPY_ICON)
        btn_descr.setCursor(Qt.PointingHandCursor)
        btn_descr.setToolTip("Copy description text")
        btn_descr.clicked.connect(lambda: QGuiApplication.clipboard().setText(DESCRIPTION_TEXT))
        toolbar.addWidget(btn_descr)

        self.codes_label = QLabel("")
        toolbar.addWidget(self.codes_label)

        root.addLayout(toolbar)

        # Cards area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("Scroll")

        container = QWidget()
        self.cards_layout = QVBoxLayout(container)
        self.cards_layout.setContentsMargins(2, 2, 2, 2)
        self.cards_layout.setSpacing(10)
        self.scroll.setWidget(container)

        root.addWidget(self.scroll)

        # Codes counter timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_codes)
        self.timer.start(2000)

        # Generate 6 on start
        self.generate_profiles()

        self.apply_modern_style()
        self.update_codes_label()

        # ---------- [AUTOZAPIS] AUTOSAVE TIMER + PRÓBA PRZYWRÓCENIA ----------
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.save_session)
        self.autosave_timer.start(30000)  # 30 sekund

        self.try_restore_session()
        # --------------------------------------------------------------------

    # ----- Codes mgmt -----
    def refresh_codes(self):
        self.codes = load_codes()
        self.update_codes_label()

    def update_codes_label(self):
        self.codes_label.setText(f"Available promo codes: {len(self.codes)}")

    def consume_code(self, code: str) -> bool:
        """Removes a specific code from file (called by card)."""
        if code not in self.codes:
            self.codes = load_codes()
            if code not in self.codes:
                return False
        self.codes.remove(code)
        save_codes(self.codes)
        self.update_codes_label()
        return True

    # ----- Actions -----
    def copy_massdata(self):
        # <-- [MASS UPLOAD] ZMIANA: tylko z kart, gdzie kliknięto Done
        lines = []
        for i in range(self.cards_layout.count()):
            item = self.cards_layout.itemAt(i)
            w = item.widget()
            if w and isinstance(w, ProfileCard) and getattr(w, "is_done", False):
                email = w.mail_row.val.text()
                password = w.pass_row.val.text()
                lines.append(f"{email}:{password}:{email}:{password}")
        if lines:
            QGuiApplication.clipboard().setText("\n".join(lines))

    def generate_profiles(self):
        # clear view & list
        self.current_profiles.clear()
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        ds = DATASETS[self.country.currentText()]
        selected_domain = self.email_domain.currentText()  # <-- nowość

        snapshot_codes = self.codes[:6]

        for i in range(6):
            p = gen_profile(ds, selected_domain)           # <-- przekazujemy domenę
            self.current_profiles.append(p)
            code = snapshot_codes[i] if i < len(snapshot_codes) else ""
            card = ProfileCard(
                p, ds.country, i + 1, code,
                on_done=self.consume_code,
                parent=self,
            )
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch(1)

    # ---------- [AUTOZAPIS] FUNKCJE SESJI ----------
    def save_session(self):
        """Zapisuje pełny stan sesji do AUTOSAVE_FILE."""
        try:
            cards = []
            for i in range(self.cards_layout.count()):
                item = self.cards_layout.itemAt(i)
                w = item.widget()
                if not w or not isinstance(w, ProfileCard):
                    continue
                p = w.profile
                cards.append({
                    "index": i + 1,
                    "country_on_card": self.country.currentText(),
                    "promo_code": w.promo_code,
                    "is_done": w.is_done,
                    "profile": {
                        "name": p.name,
                        "surname": p.surname,
                        "street": p.street,
                        "city": p.city,
                        "postal": p.postal,
                        "email": p.email,
                        "password": p.password,
                        "dob": p.dob,
                    }
                })
            data = {
                "country_choice": self.country.currentText(),
                "email_domain_choice": self.email_domain.currentText(),
                "cards": cards,
                "codes_label": self.codes_label.text(),
                "timestamp": datetime.now().isoformat()
            }
            with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            # cichy fallback – nie psuje aplikacji jeśli zapis się nie powiedzie
            pass

    def try_restore_session(self):
        """Jeśli istnieje autosave, zapytaj czy przywrócić."""
        if not os.path.exists(AUTOSAVE_FILE):
            return
        try:
            with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Odzyskiwanie sesji")
        msg.setText("Wykryto poprzednią sesję.\nCzy chcesz kontynuować starą sesję?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        choice = msg.exec()
        if choice == QMessageBox.Yes:
            self.load_session(data)
        else:
            try:
                os.remove(AUTOSAVE_FILE)
            except Exception:
                pass

    def load_session(self, data: dict):
        """Odtwarza widok z zapisanej sesji."""
        try:
            # ustawienia wyborów
            country_choice = data.get("country_choice", self.country.currentText())
            email_domain_choice = data.get("email_domain_choice", self.email_domain.currentText())
            idx_country = self.country.findText(country_choice)
            if idx_country >= 0:
                self.country.setCurrentIndex(idx_country)
            idx_dom = self.email_domain.findText(email_domain_choice)
            if idx_dom >= 0:
                self.email_domain.setCurrentIndex(idx_dom)

            # wyczyść i wczytaj karty
            self.current_profiles.clear()
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

            cards = data.get("cards", [])
            for i, c in enumerate(cards):
                prof = c.get("profile", {})
                p = Profile(
                    name=prof.get("name",""),
                    surname=prof.get("surname",""),
                    street=prof.get("street",""),
                    city=prof.get("city",""),
                    postal=prof.get("postal",""),
                    email=prof.get("email",""),
                    password=prof.get("password",""),
                    dob=prof.get("dob",""),
                )
                self.current_profiles.append(p)
                promo_code_saved = c.get("promo_code","")
                is_done_saved = bool(c.get("is_done", False))
                # jeśli było Done, promo_code na karcie jest już zużyty, więc przekażemy pusty
                code_for_ctor = "" if is_done_saved else promo_code_saved
                card = ProfileCard(
                    p,
                    country_choice,
                    i + 1,
                    code_for_ctor,
                    on_done=self.consume_code,
                    parent=self,
                )
                if is_done_saved:
                    card.is_done = True
                    card.promo_row.set_value("(used)")
                    card.done_btn.setEnabled(False)
                self.cards_layout.addWidget(card)

            self.cards_layout.addStretch(1)
        except Exception:
            # jeśli coś pójdzie nie tak, po prostu nic nie przywracamy
            pass
    # ---------------------------------------------------------------

    # ----- Style -----
    def apply_modern_style(self):
        QApplication.setStyle("Fusion")
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#0f1115"))
        pal.setColor(QPalette.ColorRole.WindowText, Qt.white)
        pal.setColor(QPalette.ColorRole.Base, QColor("#1a1d24"))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#161920"))
        pal.setColor(QPalette.ColorRole.ToolTipBase, Qt.white)
        pal.setColor(QPalette.ColorRole.ToolTipText, Qt.black)
        pal.setColor(QPalette.ColorRole.Text, Qt.white)
        pal.setColor(QPalette.ColorRole.Button, QColor("#1a1d24"))
        pal.setColor(QPalette.ColorRole.ButtonText, Qt.white)
        pal.setColor(QPalette.ColorRole.BrightText, Qt.red)
        pal.setColor(QPalette.ColorRole.Highlight, QColor("#3b4251"))
        pal.setColor(QPalette.ColorRole.HighlightedText, Qt.black)
        self.setPalette(pal)

        self.setStyleSheet("""
            #Root {
                background: #0f1115;
                color: #e6e6e6;
                font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 14px;
            }
            QLabel { color: #e6e6e6; }
            QComboBox#Combo {
                background: #1a1d24; padding: 8px 10px; border: 1px solid #2a2f3a; border-radius: 10px;
            }
            QPushButton {
                background: #1a1d24; border: 1px solid #2a2f3a; padding: 8px 12px; border-radius: 12px;
            }
            QPushButton:hover { border-color: #3b4251; }
            QPushButton#Primary {
                background: #2f6fed; border-color: #2f6fed; color: white; font-weight: 600;
            }
            QPushButton#Primary:hover { filter: brightness(1.08); }
            QScrollArea#Scroll { border: none; }
            QFrame#Card {
                background: #141821; border: 1px solid #232838; border-radius: 18px;
            }
            QLabel#CardHeader { font-size: 16px; font-weight: 700; color: #f0f2f6; margin-bottom: 4px; }
            QFrame#CopyLabelRow { background: transparent; }
            QLabel#RowKey { color: #9aa4b2; }
            QLabel#RowValue { color: #e8ebf3; font-weight: 600; }
            QPushButton#CopyBtn { background: #1a1f2b; border: 1px solid #2b3242; border-radius: 8px; }
            QPushButton#CopyBtn:hover { border-color: #475063; }
        """)

    # [AUTOZAPIS] delikatne domknięcie – zapis przy zamknięciu okna
    def closeEvent(self, event):
        try:
            self.save_session()
        except Exception:
            pass
        super().closeEvent(event)


def main():
    random.seed()
    app = QApplication(sys.argv)
    global COPY_ICON, CHECK_ICON
    COPY_ICON = make_icon(COPY_SVG)
    CHECK_ICON = make_icon(CHECK_SVG)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
