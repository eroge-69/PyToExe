
#!/usr/bin/env python3
"""
Flight Block Generator (full hardcoded airport list)
- Base airports allowed: Heathrow (EGLL), Gatwick (EGKK) or London City (EGLC)
- London City only allowed for short-haul blocks (4 or 6 legs)
- Legs: 2 (long-haul only), 4 (short-haul only), 6 (short-haul only)
- No duplicate airports within a generated block
- Full airport list hardcoded and assigned to ShortHaul or LongHaul categories
- GUI built with Tkinter. Includes option to save the generated block to a text file
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

# ------------------------
# Airports by region type (all hardcoded)
# ------------------------
AIRPORTS = {
    "ShortHaul": [
        ("LIRI", "Salerno Costa d'Amalfi, Italy"),
        ("EGPD", "Aberdeen, United Kingdom"),
        ("LEAL", "Alicante, Spain"),
        ("EHAM", "Amsterdam, Netherlands"),
        ("LTAI", "Antalya, Turkey"),
        ("LGAV", "Athens, Greece"),
        ("GMAD", "Agadir Al-Massira International Airport, Morocco"),
        ("LEBL", "Barcelona-El Prat, Spain"),
        ("LIBD", "Bari, Italy"),
        ("LFSB", "Basel (BSL), France/Switzerland"),
        ("EGAC", "Belfast City Airport, United Kingdom"),
        ("LFBE", "Bergerac, France"),
        ("LIRN", "Naples, Italy"),
        ("LIML", "Milan Linate, Italy"),
        ("LIMC", "Milan Malpensa, Italy"),
        ("LIEO", "Olbia Costa Smeralda, Italy"),
        ("LIPR", "Rimini, Italy"),
        ("LIRP", "Pisa International, Italy"),
        ("LIRZ", "Perugia, Italy"),
        ("LEMG", "Málaga, Spain"),
        ("LEPA", "Palma de Mallorca, Spain"),
        ("LEMH", "Menorca, Spain"),
        ("LGIR", "Heraklion, Greece"),
        ("LGSR", "Santorini, Greece"),
        ("LGKF", "Kefalonia, Greece"),
        ("LGKR", "Corfu, Greece"),
        ("LGKO", "Kos, Greece"),
        ("LGZA", "Zakynthos, Greece"),
        ("LGTS", "Thessaloniki, Greece"),
        ("LGSA", "Chania, Greece"),
        ("LCPH", "Paphos, Cyprus"),
        ("LCLK", "Larnaca, Cyprus"),
        ("EPWA", "Warsaw Chopin, Poland"),
        ("EPKK", "Kraków John Paul II, Poland"),
        ("EVRA", "Riga, Latvia"),
        ("LDSP", "Split, Croatia"),
        ("LDDU", "Dubrovnik, Croatia"),
        ("LDZA", "Zagreb, Croatia"),
        ("LDPL", "Pula, Croatia"),
        ("LKPR", "Prague, Czech Republic"),
        ("LHBP", "Budapest, Hungary"),
        ("LYBE", "Belgrade Nikola Tesla, Serbia"),
        ("LBSF", "Sofia, Bulgaria"),
        ("LATI", "Tirana, Albania"),
        ("EDDS", "Stuttgart, Germany"),
        ("EDDK", "Cologne/Bonn, Germany"),
        ("EDDV", "Hannover, Germany"),
        ("EHRD", "Rotterdam The Hague, Netherlands"),
        ("EBBR", "Brussels, Belgium"),
        ("ELLX", "Luxembourg, Luxembourg"),
        ("LFLL", "Lyon-Saint Exupéry, France"),
        ("LFMT", "Montpellier, France"),
        ("LFBO", "Toulouse-Blagnac, France"),
        ("LFMN", "Nice Côte d'Azur, France"),
        ("GCLP", "Las Palmas, Gran Canaria, Spain"),
        ("GCRR", "Lanzarote, Spain"),
        ("LSZH", "Zurich, Switzerland"),
        ("LIMF", "Turin, Italy")
    ],
    "LongHaul": [
        ("KJFK", "John F Kennedy International, USA"),
        ("KEWR", "Newark Liberty International, USA"),
        ("KBOS", "Boston Logan, USA"),
        ("KLAX", "Los Angeles International, USA"),
        ("KSFO", "San Francisco International, USA"),
        ("KSEA", "Seattle-Tacoma Intl, USA"),
        ("KATL", "Hartsfield-Jackson Atlanta, USA"),
        ("KDFW", "Dallas/Fort Worth, USA"),
        ("KIAH", "George Bush Intercontinental, USA"),
        ("KMIA", "Miami International, USA"),
        ("KORD", "Chicago O'Hare, USA"),
        ("KBWI", "Baltimore/Washington, USA"),
        ("KPHL", "Philadelphia, USA"),
        ("KPHX", "Phoenix, USA"),
        ("KPDX", "Portland, USA"),
        ("KPIT", "Pittsburgh, USA"),
        ("KIAD", "Washington Dulles, USA"),
        ("KCVG", "Cincinnati, USA"),
        ("KTPA", "Tampa, USA"),
        ("KMCO", "Orlando, USA"),
        ("KBNA", "Nashville, USA"),
        ("KMSY", "New Orleans, USA"),
        ("CYUL", "Montréal–Trudeau, Canada"),
        ("CYYZ", "Toronto Pearson, Canada"),
        ("CYVR", "Vancouver Intl, Canada"),
        ("SAEZ", "Buenos Aires Ezeiza, Argentina"),
        ("SCEL", "Santiago Arturo Merino Benítez, Chile"),
        ("SBGR", "São Paulo–Guarulhos, Brazil"),
        ("SBGL", "Rio de Janeiro–Galeão, Brazil"),
        ("OMDB", "Dubai International, UAE"),
        ("OMAA", "Abu Dhabi International, UAE"),
        ("OTHH", "Doha Hamad International, Qatar"),
        ("OEJN", "Jeddah King Abdulaziz, Saudi Arabia"),
        ("OERK", "King Khalid International, Riyadh, Saudi Arabia"),
        ("OKBK", "Kuwait International"),
        ("OPIS", "Islamabad Intl, Pakistan"),
        ("VIDP", "Indira Gandhi International, Delhi, India"),
        ("VABB", "Mumbai Chhatrapati Shivaji, India"),
        ("VOBL", "Bengaluru Kempegowda, India"),
        ("VOMM", "Chennai, India"),
        ("VOHS", "Hyderabad, India"),
        ("WSSS", "Singapore Changi, Singapore"),
        ("WMKK", "Kuala Lumpur Intl, Malaysia"),
        ("RJTT", "Tokyo Haneda, Japan"),
        ("ZSPD", "Shanghai Pudong, China"),
        ("ZBAD", "Beijing Daxing, China"),
        ("VHHH", "Hong Kong Intl, China"),
        ("FAOR", "O. R. Tambo International, Johannesburg, South Africa"),
        ("FACT", "Cape Town International, South Africa"),
        ("DNMM", "Murtala Muhammed International, Lagos, Nigeria"),
        ("DGAA", "Kotoka International, Accra, Ghana"),
        ("FIMP", "Sir Seewoosagur Ramgoolam Intl, Mauritius"),
        ("VRMM", "Malé Velana, Maldives"),
        ("YSSY", "Sydney Kingsford Smith, Australia"),
        ("TBPB", "Grantley Adams Intl, Barbados"),
        ("TTPP", "Piarco Intl, Trinidad & Tobago"),
        ("TAPA", "V.C. Bird Intl, Antigua and Barbuda"),
        ("MBPV", "Providenciales Intl, Turks & Caicos"),
        ("MDPC", "Punta Cana Intl, Dominican Republic"),
        ("TGPY", "Maurice Bishop Intl, Grenada")
    ]
}

# Remove duplicates
def dedupe_list(pairs):
    seen = set()
    out = []
    for icao, name in pairs:
        if icao not in seen:
            seen.add(icao)
            out.append((icao, name))
    return out

AIRPORTS["ShortHaul"] = dedupe_list(AIRPORTS["ShortHaul"])
AIRPORTS["LongHaul"] = dedupe_list(AIRPORTS["LongHaul"])

# ------------------------
# Base airports: LHR, LGW, LCY (LCY short-haul only)
# ------------------------
BASE_AIRPORTS = {
    "Heathrow (LHR)": ("EGLL", "London Heathrow"),
    "Gatwick (LGW)": ("EGKK", "London Gatwick"),
    "London City (LCY)": ("EGLC", "London City")
}

# ------------------------
# Generate Flight Block
# ------------------------
def generate_block(base_choice, legs):
    # London City check
    if base_choice == "London City (LCY)" and legs == 2:
        return None, "London City is short-haul only. Choose 4 or 6 legs."

    base_icao, base_name = BASE_AIRPORTS[base_choice]
    used = {base_icao}
    block = []

    def pick_from(region_list):
        options = [a for a in region_list if a[0] not in used]
        if not options:
            return None
        dest = random.choice(options)
        used.add(dest[0])
        return dest

    if legs == 2:
        pattern = ["LongHaul", "Base"]
    elif legs == 4:
        pattern = ["ShortHaul", "Base", "ShortHaul", "Base"]
    elif legs == 6:
        pattern = ["ShortHaul", "Base", "ShortHaul", "Base", "ShortHaul", "Base"]
    else:
        return None, "Unsupported number of legs"

    for p in pattern:
        if p == "Base":
            block.append((base_icao, base_name))
        elif p == "ShortHaul":
            dest = pick_from(AIRPORTS["ShortHaul"])
            if not dest:
                break
            block.append(dest)
        elif p == "LongHaul":
            dest = pick_from(AIRPORTS["LongHaul"])
            if not dest:
                break
            block.append(dest)

    return block, None

# ------------------------
# GUI
# ------------------------
def make_app():
    root = tk.Tk()
    root.title("Flight Block Generator - Full List")
    root.geometry("700x500")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm, text="Base Airport:").grid(row=0, column=0, sticky=tk.W)
    base_choice = ttk.Combobox(frm, values=list(BASE_AIRPORTS.keys()), state="readonly", width=30)
    base_choice.grid(row=0, column=1, sticky=tk.W, padx=6, pady=6)
    base_choice.current(0)

    ttk.Label(frm, text="Number of Legs:").grid(row=1, column=0, sticky=tk.W)
    legs_choice = ttk.Combobox(frm, values=["2", "4", "6"], state="readonly", width=10)
    legs_choice.grid(row=1, column=1, sticky=tk.W, padx=6, pady=6)
    legs_choice.current(1)

    output_box = tk.Text(frm, width=80, height=18)
    output_box.grid(row=2, column=0, columnspan=3, pady=10)

    def on_generate():
        base = base_choice.get()
        legs = int(legs_choice.get())
        flights, error = generate_block(base, legs)
        output_box.delete("1.0", tk.END)
        if error:
            messagebox.showerror("Error", error)
            return
        for i, (icao, name) in enumerate(flights, 1):
            output_box.insert(tk.END, f"Leg {i}: {icao} - {name}\n")

    def on_save():
        content = output_box.get("1.0", tk.END).strip()
        if not content:
            tk.messagebox.showinfo("Save block", "No block to save. Generate a block first.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if not fn:
            return
        with open(fn, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        messagebox.showinfo("Saved", f"Block saved to: {fn}")

    gen_btn = ttk.Button(frm, text="Generate Flights", command=on_generate)
    gen_btn.grid(row=3, column=0, pady=6, sticky=tk.W)

    save_btn = ttk.Button(frm, text="Save Block...", command=on_save)
    save_btn.grid(row=3, column=1, pady=6, sticky=tk.W)

    ttk.Label(frm, text="Notes: 2 = long-haul only. 4/6 = short-haul only. London City = short-haul only. No duplicates per block.").grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=8)

    root.mainloop()

if __name__ == "__main__":
    make_app()
