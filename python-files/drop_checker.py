
import csv
import os

def carica_drops(file_csv):
    drops = {}
    with open(file_csv, newline='', encoding='utf-8') as csvfile:
        lettore = csv.reader(csvfile)
        next(lettore)  # salta l'intestazione
        for riga in lettore:
            mob = riga[0].strip().lower()
            drop = riga[1].strip()
            if mob in drops:
                drops[mob].append(drop)
            else:
                drops[mob] = [drop]
    return drops

def main():
    path_csv = os.path.join(os.path.dirname(__file__), "drops.csv")
    drops = carica_drops(path_csv)
    print("Benvenuto nel programma drop checker di Shaiya Fawkes!")
    while True:
        nome_mob = input("\nInserisci il nome del mob (o 'esci' per uscire): ").strip().lower()
        if nome_mob == 'esci':
            break
        if nome_mob in drops:
            print(f"\nIl mob '{nome_mob.title()}' può droppare:")
            for oggetto in drops[nome_mob]:
                print(f"- {oggetto}")
        else:
            print("Mob non trovato. Prova a controllare il nome.")

if __name__ == "__main__":
    main()
