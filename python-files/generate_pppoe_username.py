
def generate_pppoe_username(anschlusskennung, zugangsnummer):
    if len(zugangsnummer) < 12:
        username = f"{anschlusskennung}{zugangsnummer}#0001@t-online.de"
    else:
        username = f"{anschlusskennung}{zugangsnummer}0001@t-online.de"
    return username

def main():
    anschlusskennung = input("Bitte geben Sie die Anschlusskennung ein: ")
    zugangsnummer = input("Bitte geben Sie die Zugangsnummer ein: ")
    
    pppoe_username = generate_pppoe_username(anschlusskennung, zugangsnummer)
    print(f"PPPoE Username: {pppoe_username}")

if __name__ == "__main__":
    main()
