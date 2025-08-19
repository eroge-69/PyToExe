import random

woordenlijst = ["python", "galgje", "programmeren", "code", "applicatie", "software", "variabele"]
woord = random.choice(woordenlijst)
geraden_letters = []
pogingen = 6

def print_galg(pogingen):
    galgen = [
        """
         ------
         |    |
         |    O
         |   /|\\
         |   / \\
         |
        --------
        """,
        """
         ------
         |    |
         |    O
         |   /|\\
         |   / 
         |
        --------
        """,
        """
         ------
         |    |
         |    O
         |   /|\\
         |    
         |
        --------
        """,
        """
         ------
         |    |
         |    O
         |   /|
         |    
         |
        --------
        """,
        """
         ------
         |    |
         |    O
         |    |
         |    
         |
        --------
        """,
        """
         ------
         |    |
         |    O
         |    
         |    
         |
        --------
        """,
        """
         ------
         |    |
         |    
         |    
         |    
         |
        --------
        """
    ]
    print(galgen[6 - pogingen])

while pogingen > 0:
    print_galg(pogingen)

    display = [letter if letter in geraden_letters else "_" for letter in woord]
    print("Woord: ", " ".join(display))

    if "_" not in display:
        print("🎉 Je hebt het woord geraden! Het was:", woord)
        break

    gok = input("Raad een letter: ").lower()

    if gok in geraden_letters:
        print("Je hebt deze letter al geraden.")
    elif gok in woord:
        print("✅ Goed geraden!")
        geraden_letters.append(gok)
    else:
        print("❌ Verkeerd!")
        geraden_letters.append(gok)
        pogingen -= 1

else:
    print_galg(pogingen)
    print("😢 Je hebt verloren. Het woord was:", woord)
