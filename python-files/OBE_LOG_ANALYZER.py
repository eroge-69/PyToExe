import re
import sys
import pandas as pd

# File di input/output
tc_list_file = 'input/tc_list.txt'
obe_log_file = 'input/obe_log.txt'
tc_obt_output_file = 'output/logAnalysis.txt'
log_commentato_file = 'output/obe_log_commentato.txt'

# Carica i tc_tag
with open(tc_list_file, 'r', encoding='utf-8') as f:
    tc_list = [line.strip() for line in f if line.strip()]

results = []
new_lines = []

with open(obe_log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

obe_obt = None
tc_processed_list = []

for line in lines:
    new_lines.append(line)  # aggiungi sempre la riga originale

    if 'TM(1,7)' in line and '[' in line and ']' in line:
        obe_obt = line.split('[')[1].split(']')[0]

    if 'DNT01611' in line:
        try:
            obe_tc_tag = line.split('"')[1].split('-')[0]
            obe_tc_descr = line.split('"')[1].split('-')[1]
        except IndexError:
            continue  # salta se il formato non è valido

        for idx, tc in enumerate(tc_list):
            if tc in line and idx not in tc_processed_list:
                results.append({
                    'TC_TAG': obe_tc_tag,
                    'TC_DESCR': obe_tc_descr,
                    'OBE_TM_1_7_OBT': obe_obt
                })

                tc_full_descr = obe_tc_tag + ' ' + obe_tc_descr
                commento = f"[--------] User Comment =========== Execution completion of {tc_full_descr}\n"
                new_lines.append(commento)

                # Salva l’indice del TC processato
                tc_processed_list.append(idx)
                break  # evita match multipli per la stessa riga

if len(tc_processed_list) != len(tc_list):
    for index, item in enumerate(tc_list):
            if index in tc_processed_list:
                print(f"\t✅ {item} in position {index} processed correctly")
            else:
                print(f"\t❌ {item} in position {index} NOT founded in OBE log")

    print(f"❌ Mismatch tra TC attesi e trovati: attesi {len(tc_list)}, trovati {len(tc_processed_list)}.")
    sys.exit(-1)
else:
    if sorted(tc_processed_list) != tc_processed_list:
        print("Lista delle posizioni nella tc_list dei TC processati: ",tc_processed_list)
    
        print(f"\t🟡 Attenzione, i telecomandi non sono stati processati nell'ordine previsto")

        val = input("Vuoi continuare? [Y/N] ")

        if val in ["N", "n", "no"]:
            sys.exit(-2) 



with open(log_commentato_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print(f"✅ OBE commentato salvato in {log_commentato_file}")    
# Salva il CSV
with open(tc_obt_output_file, 'w', encoding='utf-8') as f:
    for row in results:
        riga = f"TC_TAG: {row['TC_TAG']} | TC_DESCR: {row['TC_DESCR']} | OBE_TM_1_7_OBT: {row['OBE_TM_1_7_OBT']}\n"
        f.write(riga)
print(f"✅ Corrispondenza TC-OBT salvata in {tc_obt_output_file}")  






