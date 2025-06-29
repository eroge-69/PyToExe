while True:
    print("Skriv in din text:")
    rader = []
    while True:
        rad = input()
        if rad == "SLUT":
            break
        rader.append(rad)

    UserInput = "".join(rader).lower()

    vokaler = ["a", "e", "i", "o", "u", "y", "å", "ä", "ö"]
    konsonanter = [
        "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"
    ]

    antal_vokaler = 0
    antal_konsonanter = 0

    for bokstav in UserInput:
        if bokstav in vokaler:
            antal_vokaler += 1
        elif bokstav in konsonanter:
            antal_konsonanter += 1

    if UserInput.lower() == "avsluta":
        exit()

    print(f"Antal tecken är {len(UserInput)}")
    print(
        f"Antal tecken exklusive blanksteg är {len(UserInput.replace(' ', ''))}")
    print(f"Antal ord är {len(UserInput.split())}")
    print(
        f"Antal meningar är {UserInput.count('.') + UserInput.count('!') + UserInput.count('?')}")
    print(
        f"Antal vokaler är: {antal_vokaler}")
    print(
        f"Antal konsonanter är: {antal_konsonanter}")
    print(
        f"Övriga tecken är: {len(UserInput) - antal_vokaler - antal_konsonanter}")
