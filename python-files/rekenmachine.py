import re
import sys

MAX_GETAL = 999_000_000_000_000_000_000_000  # 999 sextiljoen

def welkom():
    print("="*60)
    print("🧮 SUPÊR REKENMACHINE — Ondersteunt + en - tot 999 sextiljoen")
    print("Typ je berekening zoals: 123456789 + 987654321. Gebruik kommas als je wil.")
    print("Typ 'exit' om te stoppen.")
    print("="*60)

def parseer_invoer(invoer):
    # Verwijder spaties
    invoer = invoer.replace(" ", "")
    
    # Regex voor + of -
    patroon = r'^([-+]?\d*\.?\d+)([\+\-])([-+]?\d*\.?\d+)$'
    match = re.match(patroon, invoer)
    
    if not match:
        return None, None, None
    
    getal1 = match.group(1)
    operator = match.group(2)
    getal2 = match.group(3)
    
    try:
        if '.' in getal1 or '.' in getal2:
            getal1 = float(getal1)
            getal2 = float(getal2)
        else:
            getal1 = int(getal1)
            getal2 = int(getal2)
    except ValueError:
        return None, None, None

    return getal1, operator, getal2

def controleer_bereik(getal1, getal2):
    if abs(getal1) > MAX_GETAL or abs(getal2) > MAX_GETAL:
        print(f"🚫 Fout: Getallen mogen niet groter zijn dan {MAX_GETAL:,}")
        return False
    return True

def bereken(getal1, operator, getal2):
    if operator == '+':
        return getal1 + getal2
    elif operator == '-':
        return getal1 - getal2
    else:
        return None

def hoofdprogramma():
    welkom()
    while True:
        invoer = input("🔢 Voer je berekening in: ").strip()
        
        if invoer.lower() == 'exit':
            print("👋 Tot ziens! Rekenmachine afgesloten.")
            sys.exit()

        getal1, operator, getal2 = parseer_invoer(invoer)
        
        if getal1 is None or operator is None or getal2 is None:
            print("⚠️ Ongeldige invoer. Gebruik het formaat: getal + getal of getal - getal")
            continue

        if not controleer_bereik(getal1, getal2):
            continue

        resultaat = bereken(getal1, operator, getal2)
        if resultaat is not None:
            print(f"✅ Resultaat: {getal1} {operator} {getal2} = {resultaat}")
        else:
            print("⚠️ Onbekende fout bij berekening.")

# Start het programma
hoofdprogramma()
