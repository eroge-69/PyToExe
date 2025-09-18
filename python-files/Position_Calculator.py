import math
import time

while True:
    x_dev = float(input("Enter x deviation: "))
    number = round(x_dev, 4)
    x_squared = number ** 2

    y_dev = float(input("Enter y deviation: "))
    number = round(y_dev, 4)
    y_squared = number ** 2

    z_dev = float(input("Enter z deviation: "))
    number = round(z_dev, 4)
    z_squared = number ** 2

    print("Position Error")
    print(2 * math.sqrt(x_squared + y_squared + z_squared))
    

