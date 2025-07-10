
#Ui

print('                      Welcome To My Calculator')

while True:

    print('')

    Num1 = input('Enter First Num : ')
    operation = input('Enter (+, -, *, /) : ')
    Num2 = input('Enter Second Num : ')

#int Nums

    if not Num1.isdigit() or not Num2.isdigit():
        print("Error")
        continue

    Num1 = int(Num1)
    Num2 = int(Num2)


#Coding

    while True:    

        if operation == '+':
            print("")
            print("Result = ",Num1 + Num2)
            break

        elif operation == '-':
            print("")
            print("Result = ",Num1 - Num2)
            break

        elif operation == '*':
            print("")
            print("Result = ",Num1 * Num2)
            break

        elif operation == '/':
            print("")
            print("Result = ",Num1 / Num2)
            break

        else:
            print("")
            print('Error')
            break

    again = input("Do You want Another operation (Yes, No) : ")

    if again == "Yes":
        continue

    elif again == "No":
        break
