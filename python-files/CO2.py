import keyboard

def calcul_reserve_alcaline(na, k, cl):
    return (na + k) - (17 + cl)

print("=== Calcul de la Réserve Alcaline ===")
print("Appuyez sur [Entrée] pour lancer un calcul.")
print("Appuyez sur [Échap] pour quitter.\n")

while True:
    print("En attente d'une action...")
    # Attend qu'on appuie sur une touche
    keyboard.wait(["enter", "esc"])

    if keyboard.is_pressed("esc"):
        print("\nFermeture du programme. À bientôt !")
        break

    elif keyboard.is_pressed("enter"):
        try:
            na = float(input("\nEntrez la valeur de Na⁺ (en mmol/L) : "))
            k = float(input("Entrez la valeur de K⁺ (en mmol/L) : "))
            cl = float(input("Entrez la valeur de Cl⁻ (en mmol/L) : "))

            ra = calcul_reserve_alcaline(na, k, cl)
            print(f"→ Réserve alcaline estimée : {ra:.2f} mmol/L\n")
        except ValueError:
            print("⚠️ Entrée invalide. Veuillez entrer des nombres.\n")
