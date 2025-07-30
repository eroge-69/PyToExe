# Problem 1

print("String Reversal")
STRING = input(str("Type anything: "))


def reverse_str(text):
    return text[::-1]


reversed_str = reverse_str(STRING)
print(reversed_str)
#
# Problem 2

print("")
print("Finding the highest value from input values. ")

x = eval(input("Enter the first number: "))
y = eval(input("Enter the second number: "))
z = eval(input("Enter the third number: "))

highest = max(x, y, z)
print("The highest number is: ", highest)

# Problem 3

print("")
print("Factorial of entered number.")

x = eval(input("Enter a number: "))
factorial = 1
if x < 0:
    print('Factorial cannot be computed because the entered number is negative')
else:
    for i in range(1, x + 1):
        factorial *= i
    print("The factorial of", x, "is:", factorial)


# Problem 4

print("")
print("Calculating total cost")

try:
    items = eval(input("How many items you want to buy: "))
    print("The total items is", items)
except ValueError:
    print("Error: You must enter a valid whole number.")


if items < 10:
    cost = items * 12
    print("The cost of each item is 12$ ")
    print("The total cost is:", cost, "$")
elif items in range(10, 99):
    cost1 = items * 10
    print("The cost of each item is 10$ ")
    print("The total cost is:", cost1, "$")
elif items > 99:
    cost2 = items * 7
    print("The cost of each item is 7$ ")
    print("The total cost is:", cost2, "$")


# Problem 5:

print("")
print("Fibonacci Sequence")

a, b = 0, 1
fib = eval(input("How many terms in Fibonacci sequence do you want to see? "))
print("Fibonacci Sequence:")
for i in range(fib):
    print(a, end="")
    a, b = b, a + b
print("")

# Problem 6:

print("")
print("Password Authentication")
correct_pass = "123456"
max_attempts = 3

for attempt in range(1, max_attempts + 1):
    pass_word = input("Password: ")
    if pass_word == correct_pass:
        print("Logged in!!")
        break
    else:
        print("Incorrect password. attempt", attempt, "of", max_attempts)
else:
    print("Too many failed attempts, The user is kicked off in the system")
