import requests, csv, datetime, os, time

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

def download_news(csv_path):
    try:
        resp = requests.get(URL, timeout=10)
        data = resp.json()

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=';')
            for ev in data:
                try:
                    dt_str = ev["date"] + " " + ev["time"]
                    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    w.writerow([
                        dt.strftime("%Y.%m.%d %H:%M"),
                        ev.get("title", ""),
                        ev.get("impact", "")
                    ])
                except Exception as e:
                    print("Errore parsing evento:", e)

        print(f"[{datetime.datetime.now()}] news.csv aggiornato in {csv_path}")
    except Exception as e:
        print("Errore download news:", e)


if __name__ == "__main__":
    print("=== Marracuda News Downloader ===")

    # Input interattivi
    mt4_path = input("Percorso cartella MQL4\\Files (es. C:\\Users\\TUO_USER\\AppData\\Roaming\\MetaQuotes\\Terminal\\XXXX\\MQL4\\Files): ").strip()
    if not os.path.exists(mt4_path):
        print("❌ Percorso non valido!")
        exit(1)

    freq_str = input("Frequenza aggiornamento in minuti (default 5): ").strip()
    try:
        update_interval = int(freq_str) * 60 if freq_str else 300
    except:
        update_interval = 300

    csv_path = os.path.join(mt4_path, "news.csv")

    print(f"\n📂 Salvataggio news in: {csv_path}")
    print(f"⏱️ Aggiornamento ogni {update_interval//60} minuti")
    print("Premi CTRL+C per uscire.\n")

    # Loop infinito
    while True:
        download_news(csv_path)
        time.sleep(update_interval)