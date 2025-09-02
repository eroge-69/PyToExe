def main():
    # Leggi l'input da tastiera
    input_string = input("Inserisci una stringa: ")

    # Definisci la sottostringa da cercare e quella con cui sostituirla
    substring_to_replace = "aa"
    replacement_string = "00000003593"

    # Effettua la sostituzione
    modified_string = input_string.replace(substring_to_replace, replacement_string)

    # Stampare il risultato
    print("Stringa modificata:", modified_string)

if __name__ == "__main__":
    main()
