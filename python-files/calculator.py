import subprocess
import sys
import time
def restart_program():
    print("Restarting the program...")
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()

print("running calculator.py")
time.sleep(1.7)
chce = int(input("Choose:   Addition(1)    Subtraction(2)    Multiplication(3)    Division(4)"))

if chce == 1:
    print("x + y = z")
    x = float(input("x = "))
    y = float(input("y = "))
    z = x+y
    print("Answer =",float(z))
    c = int(input("Do you wish to use app again?        Yes(1)  No(0)"))
    if c == 1:
        restart_program()
elif chce == 2:
    print("x - y = z")
    x = float(input("x = "))
    y = float(input("y = "))
    z = x-y
    print("Answer =",float(z))
    c = int(input("Do you wish to use app again?        Yes(1)  No(0)"))
    if c == 1:
        restart_program()
elif chce == 3:
    print("x * y = z")
    x = float(input("x = "))
    y = float(input("y = "))
    z = x*y
    print("Answer =",float(z))
    c = int(input("Do you wish to use app again?        Yes(1)  No(0)"))
    if c == 1:
        restart_program()
elif chce == 4:
    print("x / y = z")
    x = float(input("x = "))
    y = float(input("y = "))
    if y == 0:
        print("Cannot divide by zero!")
        c = int(input("Do you wish to use app again?        Yes(1)  No(0)"))
        if c == 1:
            restart_program()
    z = x/y
    print("Answer =",float(z))
    c = int(input("Do you wish to use app again?        Yes(1)  No(0)"))
    if c == 1:
        restart_program()
else:
    c = int(input("ERROR:Invalid selection. Choose number from 1 to 4. Do you wish to use app again?        Yes(1)  No(0)"))
    if c == 1:
        restart_program()
        restart_program()