import sys
import os
def console():
    os.system("clear")

def algoritm(molphy):
    if molphy == "plus":
        console()
        
        num1 = int(input("введи 1 число: "))
        num2 = int(input("введи 2 число: "))
        num3 = num1 + num2
        
        print(f"результат: {num3}")
        input("ентер для выхода в меню")
        console()
    elif molphy == "minus":
        console()
        
        num1 = int(input("введи 1 число: "))
        num2 = int(input("введи 2 число: "))
        num3 = num1 - num2
        print(f"результат: {num3}")
        
        input("введи ентер для выхода в меню")
        console()
        main()
    

def numbes(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            console()
            print("error, enter number: ")

def main():
    print("1 - plus")
    print("2 - minus")
    print("3 - выход")
    print()
    box = numbes("Веди число: ")
    
    if box == 1:
        algoritm("plus")
    elif box == 2:
        algoritm("minus")
    elif box == 3:
        print("пока..")
        sys.exit()
    else:
        print("error..")
        input("введи ентер для выхода: ")
        console()
        main()
    
main()