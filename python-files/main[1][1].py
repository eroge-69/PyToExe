prenom = input("prénom : ")
nom = input("nom : ")
age = input("age : ")
print("tu t'appelle " + prenom + "  et ton nom de famille est " + nom )
# Vérifier si la personne est majeure ou mineure
if age >= "18":
    print("tu est majeur car tu as " + age + " ans.")
else:
    print("tu est mineur car tu as " + age + " ans.")
print("marque ce que tu veux tu a 20 seconde:")
import os
import time
# Délai en secondes
délai = 20

# Attendre le délai
time.sleep(délai)

# Effacer l'écran selon le système d'exploitation
if os.name == 'nt':  # Windows
    os.system('cls')
else:  # Linux, macOS, etc.
    os.system('clear')
print("       Bonjour, " + prenom + " " + nom + " " + age + " !")
print()
print()
print("             Au revoir  " + prenom + " !")
