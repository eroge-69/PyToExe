import time

print("Hello")
time.sleep(1)

username = input("Username:")
print(" ")
print("Welcome, " + username)
time.sleep(0.5)

while True:
    password = input("Password:")
    
    if password == "111":
        time.sleep(0.5)
        print("Login Successful")
        break  
    
    else:
        print("Wrong Password. Try Again")
        

print(" ")
print("Welcome to the Goverements Top Secret Calculator")

num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))


print("Select an operation:")
print("1 - addition")
print("2 - subtraction")
print("3 - multiplication")
print("4 - division")

choice = input("Enter 1, 2, 3, or 4: ")

if choice == "1":
    result = num1 + num2
    operation = "addition"
elif choice == "2":
    result = num1 - num2
    operation = "subtraction"
elif choice == "3":
    result = num1 * num2
    operation = "multiplication"
elif choice == "4":
    if num2 == 0:
        result = "Cannot divide by 0!"
    else:
        result = num1 / num2
        operation = "division"
else:
    result = "Invalid choice!"

print("Result (" + str(operation) + "): " + str(result))

time.sleep(1)

print(" ")
print("thanks for using the goverement's top secret calculator. have a good day.")