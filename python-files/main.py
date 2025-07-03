# Generarea unui lot de 1 milion de citate și proverbe
lot_citate = []
for i in range(1, 1000001):
    citat = f"{i}. Zâmbetul este cheia care deschide inimile închise."
    lot_citate.append(citat)

# Salvăm citatele într-un fișier text
file_path = "citate_1_milion.txt"
with open(file_path, "w") as file:
    file.write("\n".join(lot_citate))

print("Fișierul text cu 1 milion de citate a fost generat cu succes!")
