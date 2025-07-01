def add():
    try:
        print("This is for addition only")
        xa = float(input("Enter x: "))
        ya = float(input("Enter y: "))
        za = xa + ya
        print(za)
    except:
        print("Please enter a valid number")

def sub():
    try:
        print("This is for subtraction only")
        xs = float(input("Enter x: "))
        ys = float(input("Enter y: "))
        zs = xs - ys
        print(zs)
    except:
        print("Please enter a valid number")

def mul():
    try:
        print("This is for multiplication only")
        xm = float(input("Enter x: "))
        ym = float(input("Enter y: "))
        zm = xm * ym
        print(zm)
    except:
        print("Please enter a valid number")

def div():
    try:
        print("This is for division only")
        xd = float(input("Enter x: "))
        yd = float(input("Enter y: "))
        zd = xd / yd
        print(zd)
    except:
        print("Please enter a valid number")

print("Heya!! Please choose the mode for calculation")
print("   Type add for addition")
print("   Type sub for subtraction")
print("   Type mul for multiplication")
print("   Type div for division")
while True:
 value = input("Mode: ")

 if value == "add":
    add()
    break
 elif value == "sub":
    sub()
    break
 elif value == "mul":
    mul()
    break
 elif value == "div":
    div()
    break
 else:
    print("Invalid mode")