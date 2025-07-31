import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin, urlparse

BOOKING_PLATFORMS = {
    "mindbodyonline.com": "MindBody",
    "clients.mindbodyonline.com": "MindBody",
    "acuityscheduling.com": "Acuity",
    "acuityschedulingclients.com": "Acuity",
    "squarespacescheduling.com": "Squarespace Scheduling",
    "square.site": "Square Appointments",
    "calendly.com": "Calendly",
    "youcanbook.me": "YouCanBookMe",
    "bookwhen.com": "BookWhen",
    "setmore.com": "Setmore",
    "10to8.com": "10to8",
    "simplybook.me": "SimplyBook.me",
    "bookeo.com": "Bookeo",
    "vagaro.com": "Vagaro",
    "schedulicity.com": "Schedulicity",
    "wellnessliving.com": "WellnessLiving",
    "punchpass.com": "Punchpass",
    "glofox.com": "Glofox",
    "ubindi.com": "Ubindi",
    "fitli.com": "Fitli",
    "zenplanner.com": "Zen Planner",
    "heygoldie.com": "Goldie",
    "teamup.com": "TeamUp",
    "mariana-tek.com": "Mariana Tek",
    "ptminder.com": "PTminder",
    "arketa.com": "Arketa",
    "bsport.io": "Bsport",
    "gymcatch.com": "Gymcatch",
    "zoho.com/bookings": "Zoho Bookings",
    "booksy.com": "Booksy",
    "fresha.com": "Fresha",
    "mytime.com": "MyTime",
    "timelyapp.com": "Timely",
    "appointlet.com": "Appointlet",
    "bookitlive.net": "BookitLive",
    "appointy.com": "Appointy",
    "resurva.com": "Resurva",
    "genbook.com": "Genbook",
    "bookr.co": "Bookr",
    "booked4.us": "Booked4.us",
    "launch27.com": "Launch27",
    "schedulista.com": "Schedulista",
    "bookafy.com": "Bookafy",
    "bookin.net": "Bookin.net",
    "yocale.com": "Yocale",
    "timetrade.com": "TimeTrade",
    "omnify.io": "Omnify",
    "calendarhero.com": "CalendarHero",
    "vcita.com": "Vcita",
    "clickbook.net": "ClickBook",
    "appointfix.com": "Appointfix",
    "superpeer.com": "Superpeer",
    "go.booker.com": "Booker",
    "appointwell.com": "AppointWell"
}

EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_REGEX = re.compile(r'(\+?\d[\d\s\-\(\)]{7,})')
NAME_REGEX = re.compile(r'(Founder|Owner|Director|Manager|Instructor)', re.IGNORECASE)

POTENTIAL_PATHS = ["/about", "/contact", "/team", "/staff", "/schedule", "/classes", "/"]

businesses = [
       {"company": "The HomeSchool Gym", "url": "https://homeschoolgym.com", "address": "11775 Pickerington Rd NW"},
    {"company": "i love my pilates", "url": "https://ilovemypilates.com", "address": "1202 E 20th St Suite C"},
    {"company": "Rhythm Dance & Fitness", "url": "https://dointhemost.com", "address": "520 Castillo St"},
    {"company": "Freedom Elite Fitness", "url": "https://freedomelitefitness.com", "address": "1221 SE Century Dr"},
    {"company": "JD Fitness, Livingston NJ", "url": "https://jdfitness.net", "address": "34 Grand Terrace"},
    {"company": "Russells Yoga", "url": "https://joyflowyoga.com", "address": "1050 N Flowood Dr C-4"},
    {"company": "In Waves Yoga", "url": "https://inwavesyoga.com", "address": "6527 Main St"},
    {"company": "Figue Madera Pilates", "url": "https://figuemadera.com", "address": "9545 Reseda Blvd #6"},
    {"company": "Forever Young Fitness & Zumba", "url": "https://fyfitness.ca", "address": "128 King St E"},
    {"company": "HaganaH Apex", "url": "https://haganahapex.com", "address": "5485 Wiles Rd"},
    {"company": "Breathe Yoga Center", "url": "https://johnsoncityyoga.com", "address": "207 W Unaka Ave"},
    {"company": "Kolar Fitness", "url": "https://kolarfitness.com", "address": "199 W Sunup Ave"},
    {"company": "Live With Spirit Yoga & Fitness Studio", "url": "https://livewithspirit.ca", "address": "101 Mary St W B1"},
    {"company": "Barney.fit Yoga", "url": "https://barney.fit", "address": "1013 Hancock Ave"},
    {"company": "aum yoga school and studio / desert nights belly dance academy", "url": "https://aumyoga.ca", "address": "16 Love Run Rd"},
    {"company": "Prana Pause Yoga", "url": "https://pranapause.com", "address": "3 Fox Hollow Cir"},
    {"company": "Prasada Yoga Studio", "url": "https://prasadayogastudio.com", "address": "705 Broad St"},
    {"company": "South County Fitness", "url": "https://southcountyfitness.com", "address": "2377 S El Camino Real Suite 205"},
    {"company": "Philippi Sports Institute", "url": "https://philippisportsinstitute.com", "address": "7770 Dean Martin Dr"},
    {"company": "Pole Sweets", "url": "https://polesweets.com", "address": "3425 W Cary St 2nd Floor"},
    {"company": "Project.YOU Yoga Studio", "url": "https://redfoxmarket.com", "address": "112 S Michigan Ave"},
    {"company": "Sage Butterfly", "url": "https://sagebutterfly.com", "address": "7806 Birch Bay Dr"},
    {"company": "Sonorous 5D", "url": "https://sonorous5d.com", "address": "915 W Main St"},
    {"company": "Dedham Yoga", "url": "https://book.dedhamspa.com", "address": "115 Eastern Ave"},
    {"company": "DawsonFit", "url": "https://iamdawsonfit.com", "address": "2301 N 9th St"},
    {"company": "One Yoga Morgan Hill by YogaSource", "url": "https://oneyogamorganhill.com", "address": "17305 Depot Street"},
    {"company": "Elevate Cafe", "url": "https://elevateyogacafe.com", "address": "155 Saco Ave"},
    {"company": "Van Exer-tech Services Inc", "url": "https://exer-tech.ca", "address": "4489 62 St"},
    {"company": "at ease Somatics : Carol Meekes", "url": "https://ateasesomatics.com", "address": "3131 Decourcy Dr"},
    {"company": "Aura Align", "url": "https://auraalignpilates.com", "address": "110 W Auglaize St"},
    {"company": "Toluca Lake Pilates", "url": "https://tolucalakepilates.com", "address": "10210 Riverside Dr"},
    {"company": "US Taekwondo Grandmasters Society", "url": "https://usgrandmasters.com", "address": "3030 W Prien Lake Rd"},
    {"company": "Bellingham Yoga Shala", "url": "https://yogaspirals.com", "address": "1412 Cornwall Ave Unit 2"},
    {"company": "Heather Paris Studios", "url": "https://heatherparisstudios.com", "address": "2408 26th Rd S"},
    {"company": "Inspiring Synergy Healing Arts Center", "url": "https://inspiringsynergy.com", "address": "1334 B, Easton Rd"},
    {"company": "KW Fitness", "url": "https://kwfitness.ca", "address": "100 Mountain Avens Crescent"},
    {"company": "Hummingbird Pilates", "url": "https://mammothpilates.com", "address": "168 Willow St Unit D"},
    {"company": "WOLF Fitness", "url": "https://wolfnc.com", "address": "2200 E Millbrook Rd Suite 105"},
    {"company": "Yoga Harmonie", "url": "https://yogaharmonie.com", "address": "2500 Av. Bourgogne"},
    {"company": "Iyengar yoga studio", "url": "https://copleyyoga.com", "address": "2830 Copley Rd"},
    {"company": "Federal Fitness Center", "url": "https://federalfitnesscenters.com", "address": "450 Golden Gate Ave"},
    {"company": "FIT LIFE HEALTH CLUBS", "url": "https://fitlifehc.com", "address": "7400 Rivers Ave #32"},
    {"company": "Tower's Fitness Center", "url": "https://towersfitness.com", "address": "2000 Powell St"},
    {"company": "Functional Fitness Pass Christian", "url": "https://ffpasschristian.com", "address": "28452 Bradley Rd Suite E"},
    {"company": "Flow and Grow Fitness", "url": "https://flowgrowfitness.com", "address": "608 Dresden Dr"},
    {"company": "Revive Yoga", "url": "https://frankfortmma.com", "address": "1100 US-127 SUITE A3"},
    {"company": "Intero Wellness", "url": "https://interokc.com", "address": "22120 Midland Dr #1"},
    {"company": "The Full Lotus Wellness Initiatives", "url": "https://thefulllotus.com", "address": "814 Southwest Pine Island Road"},
    {"company": "WestinWORKOUT", "url": "https://westin.marriott.com", "address": "75 Willow Ridge"},
]

def get_all_text(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return "", ""
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True), res.text
    except:
        return "", ""

def detect_booking_platform(html):
    for domain, name in BOOKING_PLATFORMS.items():
        if domain in html:
            return name
    if "book" in html or "schedule" in html:
        return "book via website"
    return "book via inquiry"

def extract_contacts(html):
    emails = list(set(re.findall(EMAIL_REGEX, html)))
    phones = list(set(re.findall(PHONE_REGEX, html)))
    return emails[0] if emails else "", phones[0] if phones else ""

def estimate_class_count(text):
    text = text.lower()
    count = sum(text.count(day) for day in [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ])
    if "daily" in text or "every day" in text:
        count = max(count, 7)
    if count >= 46:
        return "46+"
    elif count >= 41:
        return "41–45"
    elif count >= 36:
        return "36–40"
    elif count >= 31:
        return "31–35"
    elif count >= 26:
        return "26–30"
    elif count >= 21:
        return "21–25"
    elif count >= 15:
        return "15–20"
    elif count >= 11:
        return "11–14"
    elif count >= 8:
        return "8–10"
    elif count >= 5:
        return "5–7"
    elif count >= 1:
        return "1–4"
    return "0"

def extract_primary_contact(text):
    lines = text.splitlines()
    for line in lines:
        if NAME_REGEX.search(line) and len(line.strip()) < 100:
            return line.strip()
    return ""

def scrape_business_data(businesses):
    results = []
    for biz in businesses:
        all_text = ""
        html_combined = ""
        parsed_url = urlparse(biz["url"])
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        for path in POTENTIAL_PATHS:
            page_url = urljoin(base_url, path)
            page_text, html = get_all_text(page_url)
            all_text += " " + page_text
            html_combined += " " + html

        powered_by = detect_booking_platform(html_combined)
        email, phone = extract_contacts(html_combined)
        avg_classes = estimate_class_count(all_text)
        contact_line = extract_primary_contact(all_text)

        results.append({
            "Company": biz["company"],
            "Powered By": powered_by,
            "Address": biz["address"],
            "Average Weekly Classes": avg_classes,
            "Number of Employees": "",  # Manual or LinkedIn-augmented
            "Primary Contact Name": contact_line,
            "Primary Contact Title": "",  # Optional parsing can be added
            "Primary Contact Mobile Number": phone,
            "Primary Contact Email Address": email,
            "Owner/Founder": contact_line if "founder" in contact_line.lower() or "owner" in contact_line.lower() else ""
        })

    return pd.DataFrame(results)

# Run and export
df = scrape_business_data(businesses)
df.to_csv("full_business_data.csv", index=False)
print("✅ Scraping complete. Output saved to full_business_data.csv")