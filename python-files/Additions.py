import random
from contextlib import nullcontext

print('On va faire des additions simples')
print('chaque bonne réponse te rapporte 1 point ')
print('mais si tu rates, tu perds un point')
a = 0
b = 0
userScore = 0
userInput = nullcontext
def InputHandler():
    global a
    global b
    a = random.randint(0, 10)
    b = random.randint(0, 10)
    userInput = input(f"Combient font {a} + {b} ? = ")
    try : userInput = int(userInput)
    except ValueError : print("Entre ta réponse sous fome de nombre pour la valider");
    return userInput
#don't use directly


def Laucher():
    userInput = InputHandler()
    global a
    global b
    global userScore
    if isinstance(userInput, int) :
        if userInput == a + b :
            print(f"Bravo ! {userInput} est la bonne réponse ! +1 point")
            userScore += 1
        if userInput != a + b :
            print(f"Et non ! {userInput} n'est pas la bonne réponse ! la bonne réponse est {a + b}")
            userScore += -1
    if userScore < 0 :
        userScore = 0
    print(f"points = {userScore} Continue !")

while userScore < 10:
    Laucher()
    print("yay ! tu as 10 points! mtn dégage")





