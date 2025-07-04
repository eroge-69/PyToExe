#Taking input of what to do
F = input("Welcome to Deva's calculator please type in which operation you would like to do (+,-,/,*): ")
fl = ["+","-","/","*"]
while F not in fl:
    F = input("Please enter one of the given operations (+,-,/,*): ")
#Taking first number
N1 = (input("Enter the first number: "))
while not N1.isdigit():
    N1 = (input("Please enter a number: "))
N1=int(N1)
#Taking second number
N2 = input("Enter the second number: ")
while not N2.isdigit():
    N2 = (input("Please enter a number"))
N2=int(N2)
#Solving part
if F == "+" :
    R = N1 + N2
elif F == "-" :
    R = N1-N2
elif N1==0 and N2==0 and F=="/":
    R ="Undefined:)"
elif N1>N2 and N2==0 :
    R = "Undefined:)"
elif  F == "/" :
    R = N1/N2
elif F == "*" :
    R = N1 * N2
#Result
print(f"The answer of {N1}{F}{N2} is : {R}")