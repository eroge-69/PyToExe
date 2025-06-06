import pandas as pd
import random

# Betöltés
file_path = 'kerdesek_kvizhez.csv'
df = pd.read_csv(file_path)

# Szűrés: csak azokat, ahol van kérdés és legalább 2 válasz
valid_rows = df.dropna(subset=['kerdes', 'valasz_1', 'valasz_2'])
questions = valid_rows.sample(n=60, random_state=random.randint(0, 10000))

score = 0

print("Kvíz kezdődik!\n")
for i, row in enumerate(questions.itertuples(), 1):
    kerdes = row.kerdes
    valaszok = []
    helyes_valasz = None

    for idx in range(6):
        valasz = getattr(row, f'valasz_{idx+1}', None)
        if pd.notna(valasz):
            valaszok.append((valasz, idx))

    random.shuffle(valaszok)

    print(f"{i}. kérdés: {kerdes}")
    valasz_betuk = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    valasz_dict = {}
    for j, (valasz, eredeti_idx) in enumerate(valaszok):
        betu = valasz_betuk[j]
        print(f"  {betu}) {valasz}")
        valasz_dict[betu] = eredeti_idx

    user_valasz = input("Válasz betűjele: ").strip().upper()
    helyes_index = row.helyes_valasz_index

    if user_valasz in valasz_dict and valasz_dict[user_valasz] == helyes_index:
        print("✅  Helyes!\n")
        score += 1
    else:
        helyes_valasz_szoveg = getattr(row, f'valasz_{helyes_index+1}')
        print(f"❌  Helytelen! A helyes válasz: {helyes_valasz_szoveg}\n")

print(f"Végeredmény: {score} / 60 jó válasz")
print(f"Ez {score / 60 * 100:.2f}%")
input("\nNyomj Entert a kilépéshez...")
