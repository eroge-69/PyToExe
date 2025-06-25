import datetime

def calculeaza_elite(plain_initial):
    plain = plain_initial
    simple = plain // 4
    plain = plain % 4

    rare = simple // 4
    simple = simple % 4

    elite = rare // 4
    rare = rare % 4

    return elite, rare, simple, plain

def salveaza_in_istoric(plain_initial, elite, rare, simple, plain_ramase):
    timestamp = datetime.datetime.now().strftime("[%d-%m-%Y %H:%M]")
    linie = f"{timestamp} {plain_initial} Plain ? {elite} Elite, {rare} Rare, {simple} Simple, {plain_ramase} Plain\n"
    with open("istoric.txt", "a", encoding="utf-8") as f:
        f.write(linie)

def main():
    print("=== CONVERTOR PLAIN ? ELITE ===")
    print("Scrie 'exit' pentru a ie?i.\n")

    while True:
        intrare = input("Introdu numar de Plain: ")
        if intrare.lower() in ["exit", "iesire", "stop"]:
            break
        if not intrare.isdigit():
            print("?? Te rog sa introduci un numar valid.")
            continue

        plain_initial = int(intrare)
        elite, rare, simple, plain_ramase = calculeaza_elite(plain_initial)

        print(f"Rezultat: {elite} Elite, {rare} Rare, {simple} Simple, {plain_ramase} Plain")
        salveaza_in_istoric(plain_initial, elite, rare, simple, plain_ramase)
        print("Rezultatul a fost salvat �n 'istoric.txt'.\n")

    print("Program �ncheiat. Mul?umim!")

if __name__ == "__main__":
    main()
