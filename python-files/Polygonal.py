print("Welcome to Polygonal - Made by Newton")

print("---------------------------------------")

answer = input("What Polygon Will You Calculate Today? (C/S/T/P/H): ").upper()

if answer == "S":
    print("---------------------------------------")

    a = float(input("Width:  "))
    b = float(input("Height "))

    area = a * b
    perimeter = 2 * (a + b)

    if a == b:
        print("Shape: Square")
    else:
        print("Shape: Rectangle")
    
    print("---------------------------------------")
    print(f"Area: {round(area, 2)}")
    print(f"Perimeter: {round(perimeter, 2)}")

elif answer == "C":
    # A Circle isn't A Polygon, But It Doesn't Matter
    print("---------------------------------------")

    r = float(input("Radius: "))
    pi = 3.14159265

    diameter = 2 * r
    area = pi * r ** 2
    circumference = 2 * pi * r

    print("---------------------------------------")
    print(f"Diameter: {diameter} ")
    print(f"Area: {round(area, 2)}")
    print(f"Circumference: {round(circumference, 2)}")

elif answer == "T":
    print("---------------------------------------")

    a = float(input("Side A: "))
    b = float(input("Side B: "))
    c = float(input("Side C: "))

    sides = sorted([a, b, c])

    if sides[0] + sides[1] <= sides[2]:
        print("Shape: Not Triangle")
    else:
        a2 = sides[0] ** 2
        b2 = sides[1] ** 2
        c2 = sides[2] ** 2

        if a2 + b2 == c2:
            print("Shape: Right Triangle")
        elif a2 + b2 > c2:
            print("Shape: Acute Triangle")
        else:
            print("Shape: Obtuse Triangle")

        perimeter = sum(sides)
        s = perimeter / 2
        area = (s * (s - sides[0]) * (s - sides[1]) * (s - sides[2])) ** 0.5

        print("---------------------------------------")
        print(f"Area: {round(area, 2)}")
        print(f"Perimeter: {round(perimeter, 2)}")
    
elif answer == "P":
    print("---------------------------------------")

    a = float(input("Side A: "))

    area = 1.72 * (a ** 2)
    iag = (5 - 2) * 180

    print("---------------------------------------")
    print(f"Area: {area}")
    print(f"Interior Angle: {iag}°")

elif answer == "H":
    print("---------------------------------------")

    a = float(input("Side A: "))

    area = ((3 * (3 ** 0.5)) / 2) * (a ** 2)
    iag = (6 - 2) * 180

    print("---------------------------------------")
    print(f"Area: {area}")
    print(f"Interior Angle: {iag}°ํ")
else:
    print("---------------------------------------")
    print("Shape: Invalid")