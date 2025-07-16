#!/usr/bin/env python3
"""
Planetario Ottimizzato per EXE
Versione ottimizzata per la conversione in eseguibile Windows
- Gestione errori migliorata
- Interfaccia utente più pulita
- Messaggi di stato durante il caricamento
- Controllo dipendenze automatico
"""

import sys
import os
from datetime import datetime

def check_dependencies():
    """Verifica che tutte le dipendenze siano installate"""
    missing = []
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import skyfield
    except ImportError:
        missing.append("skyfield")
    
    if missing:
        print("ERRORE: Dipendenze mancanti!")
        print(f"Installa: pip install {' '.join(missing)}")
        input("Premi INVIO per uscire...")
        sys.exit(1)

def show_header():
    """Mostra l'header del programma"""
    print("=" * 70)
    print("                        PLANETARIO REAL-TIME")
    print("                   Posizioni Astronomiche Reali")
    print("=" * 70)
    print()

def show_loading(message):
    """Mostra messaggio di caricamento"""
    print(f"⏳ {message}...")

def show_success(message):
    """Mostra messaggio di successo"""
    print(f"✅ {message}")

def show_error(message):
    """Mostra messaggio di errore"""
    print(f"❌ {message}")

def main():
    """Funzione principale del programma"""
    
    # Verifica dipendenze
    check_dependencies()
    
    # Importa le librerie dopo la verifica
    try:
        import numpy as np
        from skyfield.api import load, wgs84
        show_success("Librerie caricate correttamente")
    except Exception as e:
        show_error(f"Errore nel caricamento delle librerie: {e}")
        input("Premi INVIO per uscire...")
        sys.exit(1)
    
    # Mostra header
    show_header()
    
    # Caricamento dati astronomici
    show_loading("Caricamento dati astronomici")
    try:
        eph = load('de421.bsp')
        ts = load.timescale()
        show_success("Dati astronomici caricati")
    except Exception as e:
        show_error(f"Errore nel caricamento dati: {e}")
        print("Verifica la connessione internet per il primo avvio")
        input("Premi INVIO per uscire...")
        sys.exit(1)
    
    # Definizione corpi celesti
    BODIES = {
        'Luna': eph['moon'],
        'Mercurio': eph['mercury'],
        'Venere': eph['venus'],
        'Sole': eph['sun'],
        'Marte': eph['mars'],
        'Giove': eph['jupiter barycenter'],
        'Saturno': eph['saturn barycenter'],
        'Urano': eph['uranus barycenter'],
        'Nettuno': eph['neptune barycenter'],
        'Plutone': eph['pluto barycenter'],
    }
    
    # Funzioni di utilità
    def format_italian_datetime(dt):
        """Formatta datetime in italiano"""
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
        
        giorno_eng = dt.strftime("%A")
        mese_eng = dt.strftime("%B")
        
        giorno_settimana = giorni_it.get(giorno_eng, giorno_eng)
        mese = mesi_it.get(mese_eng, mese_eng)
        
        return f"{dt.strftime('%H:%M')}, {giorno_settimana} {dt.day} {mese} {dt.year}"
    
    def parse_datetime(s):
        """Parser per data e ora con gestione errori"""
        if not s.strip():
            now = datetime.now()
            return now.year, now.month, now.day, now.hour, now.minute
        
        s = s.strip()
        default_h, default_m = 20, 30
        
        formats = [
            "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M",
            "%Y-%m-%d", "%Y/%m/%d",
            "%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M",
            "%d-%m-%Y", "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                if ":" not in s:  # Se non c'è orario, usa default
                    return dt.year, dt.month, dt.day, default_h, default_m
                return dt.year, dt.month, dt.day, dt.hour, dt.minute
            except ValueError:
                continue
        
        raise ValueError(f"Formato data non riconosciuto: {s}")
    
    def parse_coordinates(lat_str, lon_str):
        """Parser per coordinate geografiche"""
        default_lat = 41.3167  # Bari
        default_lon = 16.2833
        
        lat = default_lat
        lon = default_lon
        
        if lat_str.strip():
            try:
                lat = float(lat_str.replace(',', '.'))
                if not (-90 <= lat <= 90):
                    raise ValueError("Latitudine fuori range")
            except ValueError:
                show_error(f"Latitudine non valida '{lat_str}', uso default: {default_lat}")
        
        if lon_str.strip():
            try:
                lon = float(lon_str.replace(',', '.'))
                if not (-180 <= lon <= 180):
                    raise ValueError("Longitudine fuori range")
            except ValueError:
                show_error(f"Longitudine non valida '{lon_str}', uso default: {default_lon}")
        
        return lat, lon
    
    def radec_to_azimut(ra_hours, dec_degrees, lat_degrees, lon_degrees, t):
        """Converte RA/Dec in azimut"""
        try:
            jd = t.tt
            T = (jd - 2451545.0) / 36525.0
            gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 
                   0.000387933 * T * T - T * T * T / 38710000.0) % 360
            
            lst = (gmst + lon_degrees) % 360
            
            ra_rad = np.radians(ra_hours * 15)
            dec_rad = np.radians(dec_degrees)
            lat_rad = np.radians(lat_degrees)
            lst_rad = np.radians(lst)
            
            ha = lst_rad - ra_rad
            
            azimut = np.arctan2(np.sin(ha), 
                               np.cos(ha) * np.sin(lat_rad) - np.tan(dec_rad) * np.cos(lat_rad))
            
            azimut = (azimut + np.pi) % (2 * np.pi)
            return azimut
        except Exception as e:
            show_error(f"Errore nel calcolo azimut: {e}")
            return 0
    
    # INPUT UTENTE
    print("CONFIGURAZIONE:")
    print("💡 Lascia vuoto per usare i valori di default")
    print("💡 Esempi data: 2024-12-25, 2024/12/25 20:30, 25/12/2024")
    print()
    
    # Input con validazione
    while True:
        try:
            date_str = input("📅 Data (YYYY-MM-DD [HH:MM]) [oggi]: ")
            if not date_str.strip():
                now = datetime.now()
                print(f"   → Usando: {format_italian_datetime(now)}")
            
            y0, m0, d0, h0, min0 = parse_datetime(date_str)
            dt_selected = datetime(y0, m0, d0, h0, min0)
            break
        except ValueError as e:
            show_error(f"Data non valida: {e}")
            print("   Riprova con formato: YYYY-MM-DD o DD/MM/YYYY")
    
    lat_str = input("🌍 Latitudine [41.3167 - Bari]: ")
    lon_str = input("🌍 Longitudine [16.2833 - Bari]: ")
    
    lat, lon = parse_coordinates(lat_str, lon_str)
    
    # Validazione finale
    print(f"\n📍 PARAMETRI CONFERMATI:")
    print(f"   Data/Ora: {format_italian_datetime(dt_selected)}")
    print(f"   Coordinate: Lat {lat:.4f}°, Lon {lon:.4f}°")
    print()
    
    # Calcoli astronomici
    show_loading("Calcolo posizioni planetarie")
    
    try:
        t0 = ts.utc(y0, m0, d0, h0, min0)
        earth = eph['earth']
        observer = earth + wgs84.latlon(lat, lon)
        
        # Calcola posizione del Sole
        sun_astrometric = observer.at(t0).observe(eph['sun'])
        sun_apparent = sun_astrometric.apparent()
        sun_ra, sun_dec, sun_distance = sun_apparent.radec()
        sun_azimut = radec_to_azimut(sun_ra.hours, sun_dec.degrees, lat, lon, t0)
        sun_deg = np.degrees(sun_azimut) % 360
        
        show_success("Calcoli completati")
        
    except Exception as e:
        show_error(f"Errore nei calcoli: {e}")
        input("Premi INVIO per uscire...")
        sys.exit(1)
    
    # Calcola posizioni di tutti i pianeti
    body_positions = {}
    labels10 = ['BA','CA','FI','GE','MI','NA','PA','RO','TO','VE']
    
    for name, body in BODIES.items():
        try:
            astrometric = observer.at(t0).observe(body)
            apparent = astrometric.apparent()
            ra, dec, distance = apparent.radec()
            
            azimut = radec_to_azimut(ra.hours, dec.degrees, lat, lon, t0)
            
            body_positions[name] = {
                'azimut_rad': azimut,
                'azimut_deg': np.degrees(azimut) % 360,
                'ra': ra.hours,
                'dec': dec.degrees,
                'distance': distance.au
            }
        except Exception as e:
            show_error(f"Errore nel calcolo di {name}: {e}")
            body_positions[name] = {
                'azimut_rad': 0, 'azimut_deg': 0,
                'ra': 0, 'dec': 0, 'distance': 0
            }
    
    # RISULTATI
    print("\n" + "=" * 70)
    print("                           RISULTATI")
    print("=" * 70)
    print(f"📅 Data/Ora: {format_italian_datetime(dt_selected)}")
    print(f"🌍 Posizione: Lat {lat:.4f}°, Lon {lon:.4f}°")
    print(f"☀️  Azimut Sole: {sun_deg:.2f}°")
    print()
    print(f"{'Pianeta':<10s} {'Azimut°':>8s} {'Settore90':>9s} {'Settore10':>10s}")
    print("-" * 42)
    
    # Aggregazione per settori
    agg = {lbl: [] for lbl in labels10}
    
    for name, body in BODIES.items():
        azimut_deg = body_positions[name]['azimut_deg']
        
        # Settore 90 (fisso da su in alto, antiorario)
        rel90_fixed = (90 - azimut_deg) % 360
        s90_fixed = int(rel90_fixed // 4) + 1
        
        # Settore 10 (BA in alto)
        rel10 = (azimut_deg - 90) % 360
        idx10 = int(rel10 // 36)
        s10 = labels10[idx10]
        
        agg[s10].append(s90_fixed)
        print(f"{name:<10s} {azimut_deg:8.1f} {s90_fixed:9d} {s10:>10s}")
    
    print("\n" + "=" * 70)
    print("                    TABELLA AGGREGATA PER SIGLA")
    print("=" * 70)
    print(f"{'Sigla':<5s} {'Settori90'}")
    print("-" * 25)
    for lbl in labels10:
        nums = agg[lbl]
        if not nums:
            nums_str = "---"
        else:
            nums_str = ' '.join(str(n) for n in sorted(nums))
        print(f"{lbl:<5s} {nums_str}")
    
    print("\n" + "=" * 70)
    print("                    DETTAGLI ASTRONOMICI")
    print("=" * 70)
    print(f"{'Pianeta':<10s} {'RA (h)':<8s} {'Dec (°)':<8s} {'Dist (AU)':<10s}")
    print("-" * 42)
    for name, pos in body_positions.items():
        print(f"{name:<10s} {pos['ra']:8.2f} {pos['dec']:8.1f} {pos['distance']:10.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Calcolo completato con successo!")
    print("💾 Puoi salvare questi risultati copiando il testo dalla finestra")
    print("🔄 Per un nuovo calcolo, riavvia il programma")
    print("=" * 70)
    
    input("\nPremi INVIO per uscire...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programma interrotto dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")
        print("Contatta il supporto se il problema persiste")
        input("Premi INVIO per uscire...")
        sys.exit(1)
