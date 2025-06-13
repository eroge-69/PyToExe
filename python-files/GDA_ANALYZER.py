import re
import sys

# File di input/output
tc_list_file = 'input/tc_list.txt'
obe_log_file = 'input/obe_log.txt'
tc_obt_output_file = 'output/logAnalysis.txt'
log_commentato_file = 'output/obe_log_commentato.txt'

# Carica i tc_tag
try:
    with open(tc_list_file, 'r', encoding='utf-8') as f:
        tc_list = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Errore: Il file '{tc_list_file}' non è stato trovato. Assicurati che esista nella cartella 'input'.")
    sys.exit(1)

results = []
new_lines = []

try:
    with open(obe_log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Errore: Il file '{obe_log_file}' non è stato trovato. Assicurati che esista nella cartella 'input'.")
    sys.exit(1)


obe_obt = None
tc_processed_list = []

for line in lines:
    new_lines.append(line)  # aggiungi sempre la riga originale

    # Cerca l'OBE_TM_1_7_OBT
    if 'TM(1,7)' in line and '[' in line and ']' in line:
        try:
            obe_obt = line.split('[')[1].split(']')[0]
        except IndexError:
            # Continua se il formato non è quello atteso per l'OBT
            continue

    # Cerca la riga con DNT01611 per estrarre TC_TAG e TC_DESCR
    if 'DNT01611' in line:
        obe_tc_tag = None
        obe_tc_descr = None
        try:
            # Estrae la stringa tra virgolette
            match = re.search(r'"([^"]*)"', line)
            if match:
                tc_string = match.group(1)
                parts = tc_string.split('-', 1) # Splitta solo al primo '-'
                if len(parts) == 2:
                    obe_tc_tag = parts[0]
                    obe_tc_descr = parts[1]
        except Exception:
            # Salta se il formato non è valido o si verifica un errore nell'estrazione
            continue

        if obe_tc_tag and obe_tc_descr: # Assicurati che l'estrazione sia andata a buon fine
            for idx, tc in enumerate(tc_list):
                # Controlla se il tc è nella riga e non è già stato processato
                if tc in line and idx not in tc_processed_list:
                    results.append({
                        'TC_TAG': obe_tc_tag,
                        'TC_DESCR': obe_tc_descr,
                        'OBE_TM_1_7_OBT': obe_obt
                    })

                    tc_full_descr = obe_tc_tag + ' ' + obe_tc_descr
                    commento = f"[--------] User Comment =========== Execution completion of {tc_full_descr}\n"
                    new_lines.append(commento)

                    # Salva l’indice del TC processato per evitare duplicati
                    tc_processed_list.append(idx)
                    break  # Evita match multipli per la stessa riga del log con lo stesso TC

# Verifica la corrispondenza dei TC processati
if len(tc_processed_list) != len(tc_list):
    print("\n--- Riassunto TC ---")
    for index, item in enumerate(tc_list):
        if index in tc_processed_list:
            print(f"\t(Successo) {item} in posizione {index} processato correttamente")
        else:
            print(f"\t(Errore) {item} in posizione {index} NON trovato nel log OBE")

    print(f"\n(Errore) Mismatch tra TC attesi e trovati: attesi {len(tc_list)}, trovati {len(tc_processed_list)}.")
    sys.exit(-1)
else:
    if sorted(tc_processed_list) != tc_processed_list:
        print("\nLista delle posizioni nella tc_list dei TC processati: ", tc_processed_list)
        print(f"\t(Avviso) Attenzione, i telecomandi non sono stati processati nell'ordine previsto.")

        val = input("Vuoi continuare? [Y/N] ")

        if val.lower() in ["n", "no"]:
            sys.exit(-2)

# Scrivi il log commentato
try:
    with open(log_commentato_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"(Successo) OBE commentato salvato in {log_commentato_file}")
except IOError:
    print(f"Errore: Impossibile scrivere il file '{log_commentato_file}'. Controlla i permessi.")
    sys.exit(1)

# Salva il file dei risultati
try:
    with open(tc_obt_output_file, 'w', encoding='utf-8') as f:
        # Scrive un'intestazione per chiarezza
        f.write("Analisi Log - Corrispondenze TC-OBT\n")
        f.write("-------------------------------------\n")
        for row in results:
            riga = f"TC_TAG: {row['TC_TAG']} | TC_DESCR: {row['TC_DESCR']} | OBE_TM_1_7_OBT: {row['OBE_TM_1_7_OBT']}\n"
            f.write(riga)
    print(f"(Successo) Corrispondenza TC-OBT salvata in {tc_obt_output_file}")
except IOError:
    print(f"Errore: Impossibile scrivere il file '{tc_obt_output_file}'. Controlla i permessi.")
    sys.exit(1)

