#!/usr/bin/env python3
"""
planetario_real_equal_orbits_sectors.py

Planetario geocentrico con posizioni reali (Skyfield DE421),
orbite equidistanti per visibilità, movimento fluido per una data e orario,
90 settori numerati ruotati sul finale del Sole,
10 settori etichettati fissi con BA in alto (nord), antiorari,
tabella finale su IDLE con entrambi i settori e tabella aggregata.

Modifiche aggiunte:
- Se data/ora non inserita, usa data/ora di sistema
- Supporto per latitudine e longitudine (default: 41.3167, 16.2833)
- POSIZIONI REALI: Usa posizioni topocentriche dall'osservatore specifico
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from skyfield.api import load, wgs84
from datetime import datetime

# 1. Prepara ephemeris e corpi
eph = load('de421.bsp')
ts  = load.timescale()
BODIES = {
    'Luna':     eph['moon'],
    'Mercurio': eph['mercury'],
    'Venere':   eph['venus'],
    'Sole':     eph['sun'],
    'Marte':    eph['mars'],
    'Giove':    eph['jupiter barycenter'],
    'Saturno':  eph['saturn barycenter'],
    'Urano':    eph['uranus barycenter'],
    'Nettuno':  eph['neptune barycenter'],
    'Plutone':  eph['pluto barycenter'],
}
STYLES = {
    'Luna':     ('silver',      60),
    'Mercurio': ('lightgray',   80),
    'Venere':   ('orange',     100),
    'Sole':     ('yellow',     200),
    'Marte':    ('tomato',     120),
    'Giove':    ('saddlebrown',160),
    'Saturno':  ('gold',       140),
    'Urano':    ('lightblue',  130),
    'Nettuno':  ('royalblue',  130),
    'Plutone':  ('white',      100),
}

# 2. Funzione per formattare data in italiano
def format_italian_datetime(dt):
    """Formatta datetime in italiano: ora, giorno, mese, anno"""
    # Dizionari di traduzione per essere sicuri dell'encoding
    giorni_it = {
        'Monday': 'lunedì', 'Tuesday': 'martedì', 'Wednesday': 'mercoledì',
        'Thursday': 'giovedì', 'Friday': 'venerdì', 'Saturday': 'sabato', 'Sunday': 'domenica'
    }
    mesi_it = {
        'January': 'gennaio', 'February': 'febbraio', 'March': 'marzo',
        'April': 'aprile', 'May': 'maggio', 'June': 'giugno',
        'July': 'luglio', 'August': 'agosto', 'September': 'settembre',
        'October': 'ottobre', 'November': 'novembre', 'December': 'dicembre'
    }
    
    # Usa sempre i dizionari per evitare problemi di encoding
    giorno_eng = dt.strftime("%A")
    mese_eng = dt.strftime("%B")
    
    giorno_settimana = giorni_it.get(giorno_eng, giorno_eng)
    mese = mesi_it.get(mese_eng, mese_eng)
    
    return f"{dt.strftime('%H:%M')}, {giorno_settimana} {dt.day} {mese} {dt.year}"

# 3. Parser data e ora (supporta YYYY-MM-DD[ HH:MM] e YYYY/MM/DD[ HH:MM])
def parse_datetime(s):
    if not s.strip():  # Se stringa vuota, usa data/ora di sistema
        now = datetime.now()
        return now.year, now.month, now.day, now.hour, now.minute
    
    s = s.strip()
    # default time 20:30
    default_h, default_m = 20, 30
    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.year, dt.month, dt.day, dt.hour, dt.minute
        except ValueError:
            continue
    # prova solo data
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.year, dt.month, dt.day, default_h, default_m
        except ValueError:
            continue
    raise ValueError(f"Formato data/ora non riconosciuto: {s}")

# 4. Parser per coordinate geografiche
def parse_coordinates(lat_str, lon_str):
    # Valori di default
    default_lat = 41.3167
    default_lon = 16.2833
    
    lat = default_lat
    lon = default_lon
    
    if lat_str.strip():
        try:
            lat = float(lat_str)
        except ValueError:
            print(f"Latitudine non valida '{lat_str}', uso default: {default_lat}")
    
    if lon_str.strip():
        try:
            lon = float(lon_str)
        except ValueError:
            print(f"Longitudine non valida '{lon_str}', uso default: {default_lon}")
    
    return lat, lon

# 5. Funzione per calcolare l'azimut dall'ascensione retta e declinazione
def radec_to_azimut(ra_hours, dec_degrees, lat_degrees, lon_degrees, t):
    """
    Converte RA/Dec in azimut per la posizione e il tempo specificati.
    Restituisce l'azimut in radianti (0 = Nord, π/2 = Est, π = Sud, 3π/2 = Ovest)
    """
    # Calcola il tempo siderale locale
    ut = t.ut1
    jd = t.tt
    
    # Tempo siderale a Greenwich (approssimazione)
    T = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T - T * T * T / 38710000.0) % 360
    
    # Tempo siderale locale
    lst = (gmst + lon_degrees) % 360
    
    # Converti in radianti
    ra_rad = np.radians(ra_hours * 15)  # RA in ore -> gradi -> radianti
    dec_rad = np.radians(dec_degrees)
    lat_rad = np.radians(lat_degrees)
    lst_rad = np.radians(lst)
    
    # Angolo orario
    ha = lst_rad - ra_rad
    
    # Calcola azimut
    azimut = np.arctan2(np.sin(ha), 
                       np.cos(ha) * np.sin(lat_rad) - np.tan(dec_rad) * np.cos(lat_rad))
    
    # Converti da convenzione astronomica (S=0, W=π/2) a convenzione geografica (N=0, E=π/2)
    azimut = (azimut + np.pi) % (2 * np.pi)
    
    return azimut

# 6. Input utente
print("=== CONFIGURAZIONE PLANETARIO ===")
print("Lascia vuoto per usare i valori di default")
print()

date_str = input("Data (YYYY-MM-DD [HH:MM] o YYYY/MM/DD [HH:MM]) [data/ora sistema]: ")
if not date_str.strip():
    now = datetime.now()
    print(f"Usando data/ora di sistema: {format_italian_datetime(now)}")

lat_str = input("Latitudine [41.3167]: ")
lon_str = input("Longitudine [16.2833]: ")

y0, m0, d0, h0, min0 = parse_datetime(date_str)
lat, lon = parse_coordinates(lat_str, lon_str)

# Crea oggetto datetime per la formattazione
dt_selected = datetime(y0, m0, d0, h0, min0)

print(f"\nParametri utilizzati:")
print(f"Data/Ora: {format_italian_datetime(dt_selected)}")
print(f"Coordinate: Lat {lat:.4f}°, Lon {lon:.4f}°")
print()

t0 = ts.utc(y0, m0, d0, h0, min0)

# 7. Crea observer basato sulla posizione geografica
earth = eph['earth']
observer = earth + wgs84.latlon(lat, lon)

# 8. Calcola posizione del Sole dall'osservatore per determinare l'orientamento
sun_astrometric = observer.at(t0).observe(eph['sun'])
sun_apparent = sun_astrometric.apparent()
sun_ra, sun_dec, sun_distance = sun_apparent.radec()

# Calcola azimut del Sole
sun_azimut = radec_to_azimut(sun_ra.hours, sun_dec.degrees, lat, lon, t0)
sun_deg = np.degrees(sun_azimut) % 360

# 9. Setup grafico
fig, ax = plt.subplots(figsize=(8,8))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
ax.set_aspect('equal')
ax.axis('off')

N     = len(BODIES)
radii = np.linspace(0.5, N + 0.5, N)
rmax  = radii[-1]

for r in radii:
    ax.add_patch(plt.Circle((0,0), r,
                  color='white', fill=False,
                  linestyle='--', alpha=0.3))

# Titolo del grafico con data formattata in italiano
title_text = f"{format_italian_datetime(dt_selected)} - Lat:{lat:.2f}° Lon:{lon:.2f}°"
ax.set_title(title_text, color='white', fontsize=14)
ax.scatter(0,0, color='deepskyblue', s=200, zorder=5)
ax.text(0,0,'Terra', color='white', fontsize=12,
        ha='left', va='bottom')

# 10. Disegna 90 settori numerati, fissi da su in alto in senso antiorario
for i in range(90):
    theta = np.pi/2 - 2 * np.pi * i / 90  # Inizia da su (π/2) e va in senso antiorario
    x2, y2 = rmax * np.cos(theta), rmax * np.sin(theta)
    ax.plot([0, x2], [0, y2], color='white', linewidth=0.5, alpha=0.2)
    xt, yt = (rmax+0.3) * np.cos(theta), (rmax+0.3) * np.sin(theta)
    ax.text(xt, yt, str(i+1), color='white', fontsize=6,
            ha='center', va='center')

# 11. Disegna 10 settori etichettati fissi, BA in alto, antiorari
labels10 = ['BA','CA','FI','GE','MI','NA','PA','RO','TO','VE']
for j in range(10):
    theta_big = np.pi/2 + 2 * np.pi * j / 10
    x2, y2    = rmax * np.cos(theta_big), rmax * np.sin(theta_big)
    ax.plot([0, x2], [0, y2], color='yellow', linewidth=1.2, alpha=0.6)
    theta_mid = np.pi/2 + 2 * np.pi * (j + 0.5) / 10
    xt2, yt2  = (rmax+0.8) * np.cos(theta_mid), (rmax+0.8) * np.sin(theta_mid)
    ax.text(xt2, yt2, labels10[j], color='yellow', fontsize=8,
            ha='center', va='center')

# 12. Posiziona i corpi celesti usando posizioni topocentriche reali
print("Calcolando posizioni reali dei pianeti...")
body_positions = {}

for idx, (name, body) in enumerate(BODIES.items()):
    color, size = STYLES[name]
    
    # Usa l'osservatore specifico per ottenere posizioni topocentriche
    astrometric = observer.at(t0).observe(body)
    apparent = astrometric.apparent()
    ra, dec, distance = apparent.radec()
    
    # Calcola azimut dalla posizione dell'osservatore
    azimut = radec_to_azimut(ra.hours, dec.degrees, lat, lon, t0)
    
    # Memorizza per la tabella
    body_positions[name] = {
        'azimut_rad': azimut,
        'azimut_deg': np.degrees(azimut) % 360,
        'ra': ra.hours,
        'dec': dec.degrees,
        'distance': distance.au
    }
    
    # Posiziona sul cerchio appropriato
    r = radii[idx]
    x, y = r * np.cos(azimut), r * np.sin(azimut)
    ax.scatter(x, y, color=color, s=size, zorder=10)
    ax.text(x, y, name, color='white', fontsize=10,
            ha='left', va='bottom')

plt.show()

# 13. Stampa tabella finale e aggregata
print("\n" + "="*60)
print("TABELLA SETTORI FINALI (POSIZIONI REALI)")
print("="*60)
print(f"Data/Ora: {format_italian_datetime(dt_selected)}")
print(f"Posizione: Lat {lat:.4f}°, Lon {lon:.4f}°")
print(f"Azimut Sole: {sun_deg:.2f}°")
print("Settori 90: fissi da su in alto, antiorari")
print()
print(f"{'Pianeta':<10s} {'Azimut°':>8s} {'Settore90':>9s} {'Settore10':>10s}")
print("-" * 42)

agg = {lbl: [] for lbl in labels10}

for name, body in BODIES.items():
    azimut_deg = body_positions[name]['azimut_deg']
    
    # Calcola settore fisso (90 settori, 1 in alto, antiorario)
    rel90_fixed = (90 - azimut_deg) % 360  # Settore fisso: 1 in alto, antiorario
    s90_fixed = int(rel90_fixed // 4) + 1
    
    # Calcola settore fisso (10 settori, BA in alto)
    rel10 = (azimut_deg - 90) % 360
    idx10 = int(rel10 // 36)
    s10   = labels10[idx10]
    
    agg[s10].append(s90_fixed)
    print(f"{name:<10s} {azimut_deg:8.1f} {s90_fixed:9d} {s10:>10s}")

print("\n" + "="*60)
print("TABELLA AGGREGATA PER SIGLA")
print("="*60)
print(f"{'Sigla':<5s} {'Settori90'}")
print("-" * 25)
for lbl in labels10:
    nums = agg[lbl]
    if not nums:
        nums_str = "---"
    else:
        nums_str = ' '.join(str(n) for n in sorted(nums))
    print(f"{lbl:<5s} {nums_str}")

print("\n" + "="*60)
print("INFORMAZIONI DETTAGLIATE")
print("="*60)
print(f"{'Pianeta':<10s} {'RA (h)':<8s} {'Dec (°)':<8s} {'Dist (AU)':<10s}")
print("-" * 42)
for name, pos in body_positions.items():
    print(f"{name:<10s} {pos['ra']:8.2f} {pos['dec']:8.1f} {pos['distance']:10.3f}")

print("\n" + "="*60)
