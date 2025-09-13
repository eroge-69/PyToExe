import requests
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, RequestException
import time
import sqlite3

# SKONFIGURUJ TELEGRAMA: Wpisz tutaj swój token i ID czatu
# Aby uzyskać token, napisz na Telegramie do @BotFather.
# Aby uzyskać ID czatu, dodaj bota do grupy i napisz na czacie.
TELEGRAM_BOT_TOKEN = "8228370867:AAFAcXooJOWsbirFi7oEvcwrhBTowMd1n1I"
TELEGRAM_CHAT_ID = "-1002961356429"

def send_telegram_notification(message):
    """
    Wysyła wiadomość tekstową do określonego czatu na Telegramie.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Powiadomienie wysłane do Telegrama.")
    except RequestException as e:
        print(f"Błąd wysyłania powiadomienia do Telegrama: {e}")

def save_to_db(events):
    """
    Zapisuje listę wydarzeń (kursów) do bazy danych SQLite o nazwie bets.db.
    Tworzy tabelę 'sts_odds', jeśli jeszcze nie istnieje.
    """
    conn = None
    try:
        conn = sqlite3.connect('bets.db')
        cursor = conn.cursor()
        
        # Tworzenie tabeli, jeśli nie istnieje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sts_odds (
                id INTEGER PRIMARY KEY,
                event_name TEXT NOT NULL,
                odds_1 REAL NOT NULL,
                odds_2 REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Wstawianie danych do tabeli
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        for event in events:
            cursor.execute('''
                INSERT INTO sts_odds (event_name, odds_1, odds_2, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (event['name'], event['odds_1'], event['odds_2'], current_time))
            
        conn.commit()
        print(f"Pomyślnie zapisano {len(events)} wydarzeń do bazy danych bets.db.")
        
    except sqlite3.Error as e:
        print(f"Błąd bazy danych: {e}")
    finally:
        if conn:
            conn.close()

def fetch_pinnacle_odds():
    """
    Pobiera dane o kursach z bukmachera Pinnacle za pomocą prostego zapytania HTTP.
    """
    url = 'https://www.pinnacle.com/'
    
    print(f"Rozpoczynam pobieranie danych z Pinnacle: {url}")
    
    events = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Sprawdza, czy zapytanie zakończyło się sukcesem
        
        print("Zapytanie udane. Przetwarzam kod HTML.")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        event_selector = 'div.event-row'
        event_name_selector = 'span.event-name'
        odd_selector = 'span.odd'
        
        for event_row in soup.select(event_selector):
            event_name_tag = event_row.select_one(event_name_selector)
            odds_tags = event_row.select(odd_selector)
            
            if event_name_tag and len(odds_tags) == 2:
                try:
                    event_name = event_name_tag.text.strip()
                    odds = [float(odd.text) for odd in odds_tags]
                    
                    events.append({
                        "name": event_name,
                        "odds_1": odds[0],
                        "odds_2": odds[1]
                    })
                except (ValueError, IndexError) as e:
                    print(f"Błąd przetwarzania danych dla wiersza zdarzenia: {e}")
                    continue

        print(f"Pobrano {len(events)} wydarzeń z Pinnacle.")
        
    except (RequestException, Timeout) as e:
        print(f"Błąd podczas pobierania danych z Pinnacle: {e}")
    
    return events

def fetch_polish_odds():
    """
    Symuluje pobieranie danych o kursach od polskiego bukmachera (STS).
    Generuje przykładowe dane, zapisuje je do bazy i wysyła powiadomienia do Telegrama.
    """
    print(f"Trwa pobieranie danych z STS")
    
    # Przykładowe dane do symulacji
    events = [
        {"name": "Legia Warszawa vs Lech Poznań", "odds_1": 2.15, "odds_2": 3.40},
        {"name": "Wisła Kraków vs Cracovia", "odds_1": 1.90, "odds_2": 4.10},
        {"name": "Pogoń Szczecin vs Jagiellonia Białystok", "odds_1": 2.50, "odds_2": 2.90}
    ]
    
    print(f"Wyszukuje dane z STS")
    
    # Zapisywanie do bazy danych i wysyłanie powiadomień
    if events:
        save_to_db(events)
        for event in events:
            message = f"Nowy zakład znaleziony na STS!\n---\nMecz: {event['name']}\nKursy: {event['odds_1']} vs {event['odds_2']}"
            send_telegram_notification(message)
    else:
        # Wysyłanie powiadomienia w przypadku braku zakładów
        send_telegram_notification("Brak zakładów do wyświetlenia na stronie STS.")
        
    return events

