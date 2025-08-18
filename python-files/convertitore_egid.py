import requests
import math

# --- Funzioni di conversione da coordinate svizzere (LV95) a WGS84 ---
# Queste formule sono necessarie perché l'API restituisce coordinate nel sistema svizzero.

def CHtoWGSlat(y, x):
    """Converte le coordinate y/x (LV95) in latitudine WGS84."""
    y_aux = (y - 2600000) / 1000000
    x_aux = (x - 1200000) / 1000000
    lat = (16.9023892 + 3.238272 * x_aux - 0.270978 * y_aux**2 
           - 0.002528 * x_aux**2 - 0.0447 * y_aux**2 * x_aux 
           - 0.0140 * x_aux**3)
    return lat * 100 / 36

def CHtoWGSlng(y, x):
    """Converte le coordinate y/x (LV95) in longitudine WGS84."""
    y_aux = (y - 2600000) / 1000000
    x_aux = (x - 1200000) / 1000000
    lng = (2.6779094 + 4.728982 * y_aux + 0.791484 * y_aux * x_aux
           + 0.1306 * y_aux * x_aux**2 - 0.0436 * y_aux**3)
    return lng * 100 / 36

def get_coordinates_from_egid(egid):
    """
    Interroga l'API di GeoAdmin per un singolo EGID e restituisce le coordinate WGS84.
    """
    # L'URL dell'API per la ricerca di edifici tramite EGID
    api_url = f"https://api3.geo.admin.ch/rest/services/api/MapServer/find?layer=ch.bfe.gebäude-und-wohnungsregister&searchText={egid}&searchField=egid&contains=false"
    
    try:
        # Esegui la richiesta GET
        response = requests.get(api_url, timeout=10)
        # Controlla se la richiesta ha avuto successo (codice 200)
        response.raise_for_status()
        
        data = response.json()
        
        # Controlla se sono stati trovati risultati
        if data['results']:
            # Estrai le coordinate LV95 (E = y, N = x)
            attributes = data['results'][0]['attributes']
            coord_y_lv95 = attributes['gkode'] 
            coord_x_lv95 = attributes['gkodn']
            
            # Converti le coordinate in WGS84
            lat_wgs84 = CHtoWGSlat(coord_y_lv95, coord_x_lv95)
            lng_wgs84 = CHtoWGSlng(coord_y_lv95, coord_x_lv95)
            
            return lat_wgs84, lng_wgs84
        else:
            return None # Nessun risultato trovato per questo EGID

    except requests.exceptions.RequestException as e:
        print(f"Errore di rete per EGID {egid}: {e}")
        return None
    except (KeyError, IndexError):
        print(f"Errore: la risposta dell'API per EGID {egid} non ha il formato atteso.")
        return None


def main():
    """
    Funzione principale che legge il file e avvia il processo.
    """
    try:
        # Chiede all'utente il nome del file
        file_path = input("Inserisci il percorso del file di testo con gli EGID (es: lista_egid.txt): ")
        
        # Apre e legge il file
        with open(file_path, 'r') as f:
            # Crea una lista di EGID, rimuovendo spazi e righe vuote
            egids = [line.strip() for line in f if line.strip()]

        if not egids:
            print("Il file è vuoto o non contiene EGID validi.")
            return

        print(f"\n--- Inizio la conversione per {len(egids)} EGID ---\n")

        # Itera su ogni EGID e recupera le coordinate
        for egid in egids:
            coordinates = get_coordinates_from_egid(egid)
            if coordinates:
                lat, lon = coordinates
                print(f"EGID: {egid} -> Latitudine: {lat:.6f}, Longitudine: {lon:.6f}")
            else:
                print(f"EGID: {egid} -> Coordinate non trovate o errore.")
        
        print("\n--- Conversione completata ---")

    except FileNotFoundError:
        print(f"Errore: il file '{file_path}' non è stato trovato. Assicurati che sia nella stessa cartella dello script o inserisci il percorso completo.")
    except Exception as e:
        print(f"Si è verificato un errore imprevisto: {e}")


# Avvia la funzione principale quando lo script viene eseguito
if __name__ == "__main__":
    main()