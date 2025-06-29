import os
from datetime import datetime

# Fájlnév beállítások
prime_file = "Prím számok.txt"
last_file = "utolso_szam.txt"

# Betöltjük az utolsó sorszámot
if os.path.exists(last_file):
    with open(last_file, "r", encoding="utf-8") as f:
        last_index = int(f.read().strip())
else:
    last_index = 0

# Kiolvassuk az utolsó prím értékét
last_prime = 1
if os.path.exists(prime_file):
    with open(prime_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(":")
                if len(parts) == 2:
                    last_prime = int(parts[1].split()[0].strip())

# Prím ellenőrző függvény
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

# Végtelen ciklusban prímek keresése (CTRL+C megszakítással leállítható)
found = 0
current = last_prime + 1

print("🔍 Végtelen prímkeresés indult. Nyomj CTRL+C-t a leállításhoz.\n")

try:
    with open(prime_file, "a", encoding="utf-8") as pf:
        while True:
            if is_prime(current):
                last_index += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                line = f"{last_index}: {current} [{timestamp}]\n"
                pf.write(line)
                pf.flush()
                with open(last_file, "w", encoding="utf-8") as f:
                    f.write(str(last_index))
                print(line.strip())
                found += 1
            current += 1
except KeyboardInterrupt:
    print("\n⏹️ Prímkeresés megszakítva. Utolsó sorszám:", last_index)

