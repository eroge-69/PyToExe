import win32evtlog

def lire_evenements_bsod():
    serveur = 'localhost'
    journal = 'System'
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    sources_cibles = ['BugCheck', 'Kernel-Power', 'WHEA-Logger', 'EventLog']

    try:
        handle = win32evtlog.OpenEventLog(serveur, journal)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du journal : {e}")
        return

    print("📋 Événements système liés aux BSOD :\n")
    total = 0
    while True:
        events = win32evtlog.ReadEventLog(handle, flags, 0)
        if not events:
            break
        for ev in events:
            if ev.SourceName in sources_cibles:
                total += 1
                print(f"--- Événement {total} ---")
                print(f"Date : {ev.TimeGenerated}")
                print(f"Source : {ev.SourceName}")
                print(f"ID : {ev.EventID}")
                print(f"Type : {ev.EventType}")
                print(f"Message :\n{ev.StringInserts}\n")

    if total == 0:
        print("Aucun événement BSOD trouvé dans le journal système.")

if __name__ == "__main__":
    lire_evenements_bsod()
