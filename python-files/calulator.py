'''num1=int(input("enter the number 1 : "))
num2=int(input("enter the number 2 : "))
operation= input("tell me the operation you want perform : sum , subs, mul, div : ")
if (operation == "sum") :
    print("the sum is" , num1 + num2)
if (operation == "subs"):
    print("the Difference is" , num1 - num2)
if (operation == "mul"):
    print("the product is" , num1 * num2)
if (num2==0 and operation == "div"):
    print("the Division is not possible" )
else :
    print("the Division is" , num1 / num2)'''


num1=int(input("enter the number 1 : "))
num2=int(input("enter the number 2 : "))
operation= input("tell me the operation you want perform : \n + , -, *, /,rem : ")
if (operation == "+"or "add") :
    print("the sum is" , num1 + num2)
elif (operation == "rem"):
    print("the remainder is" , num1 % num2)
elif (operation == "-"):
    print("the Difference is" , num1 - num2)
elif (operation == "*"):
    print("the product is" , num1 * num2)

elif (num2==0 ):
    print("the Division is not possible" )
elif (operation == "/"):
    print("the Division is" , num1 / num2)
else :
    print("invalid operator")




