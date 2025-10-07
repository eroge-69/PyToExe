import math

print("--- Beräkna din omkrets kungen ---\nAnge '0' för att avsluta programmet\n")

def beraknaOmkrets():
    userInput = float(input("Hur bred är den?\n>"))
    if userInput == 0:
        return userInput
    omkrets = (userInput/2)*math.pi
    omkrets = round(omkrets, 2)
    print(f"-----------------------\nDin omkrets är {omkrets}cm\n-----------------------\n")
    return userInput

check = None
while check != 0:
    check = beraknaOmkrets()

print("Hejdå, vi ses snart igen ;)")