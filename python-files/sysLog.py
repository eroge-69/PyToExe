from collections import defaultdict

def parse_log_file(log_file_path):
    # Inizializza un dizionario per contenere le sezioni
    sections = defaultdict(list)
    
    with open(log_file_path, 'r') as file:
        for line in file:
            # Trova l'indice di "Vigorfamigliacotarella:"
            start_idx = line.find("Vigorfamigliacotarella:")
            if start_idx == -1:
                continue  # Salta righe che non contengono il marker
            
            # Estrai il resto della riga dopo "Vigorfamigliacotarella:"
            rest_of_line = line[start_idx + len("Vigorfamigliacotarella:"):].strip()
            
            # La sezione è il primo token dopo "Vigorfamigliacotarella:"
            section = rest_of_line.split()[0] if rest_of_line else "UNKNOWN"
            
            # Aggiungi la riga alla sezione corrispondente
            sections[section].append(line.strip())
    
    return sections

def print_sections(sections):
    for section, lines in sections.items():
        print(f"\n=== Sezione: {section} === (Righe: {len(lines)})")
        for line in lines[:3]:  # Stampa solo le prime 3 righe per esempio
            print(line)
        if len(lines) > 3:
            print(f"... ({len(lines) - 3} righe omesse)")

# Esempio di utilizzo
log_file_path = "log.log"  # Sostituisci con il percorso del tuo file
sections = parse_log_file(log_file_path)
print_sections(sections)