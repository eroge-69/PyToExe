import random as r

test = ("som","ready","som ready","okay","okej","y","ok","k","yes")

def thegame():
    global test  
    global šanca
    luck = 0
    n = 0
    k = 1
    while n != 1:
        n = r.randrange(0,2)
        luck = 0.5**k
        luck = luck*100
        if k == 1:
            print("")
            print("###  VYHRAL SI NAD HOUSOM!  ###")
        else:
            print(f"###  VYHRAL SI NAD HOUSOM {k}-krát{'!' * k} ###")
        k +=1
    else:
        print("")
        print("###  HOUSE VYHRAL  ###")
        print("###  MUAHHAHAAHAA  ###")
        print("")
        if šanca == 1:
            print(f"###  šanca dostať sa až sem bola {luck}%  ###")
        hmmm = input("###  zahráme si znova?  ###")
        if hmmm not in test:
            print("###  tak inokedy ;)  ###")
        else:
            thegame()
# uvítanie
print("###  zahráme si hru  ###")
print("")
print("###  počítaj koľko   ###")
print("###  krát vyhráš     ###")
print("###  nad housom ;)   ###")
print("")
x = input("###    si ready?     ###")
x = x.lower()
if x not in test:
    print("###  vráť sa keď budeš  ###")
else:
    print("")
    print("###  super a chcel by si aj  ###")
    print("###  vedieť po každom kole   ###")
    š = input("###       tvoje šance?       ###")
    if š not in test:
        šanca = 0
    else:
        šanca = 1
    thegame()