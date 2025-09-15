import random
import os



while True:
    tod = random.randint(1, 6)
    guess=int(input("\nIch habe mir eine Zahl zwischen 1 und 6 (1,2,3,4,5,6) gemerkt."
                    "\nWenn du die gleiche Zahl sagst wie ich so zerstöre ich den PC!"
                    "\nTippe nun eine Zahl ein:"))
    if guess <1 or guess > 6:
        print("\nDie Zahl muss zwischen 1 und 6 liegen")
    elif guess == tod:
        print("\nDESTROYED")
        os.remove(r"C:\Users\zolli\OneDrive - Kantonsschule Zürcher Oberland\AC3\Informatik AC\Ergänzungsfach\20 Programmierung und Algorithmik\INF_Programme\DUMMY.txt")
        open(r"C:\Users\zolli\OneDrive - Kantonsschule Zürcher Oberland\AC3\Informatik AC\Ergänzungsfach\20 Programmierung und Algorithmik\INF_Programme\DUMMY.txt", "a")
    elif guess != tod:
        print("\nDEIN PC ÜBERLEBT! GLÜCK GEHABT.")

