import math

materialcost = float(input("Enter material cost: "))
hours = float(input("Enter hours: "))
labourhours = float(input("Enter labour hours: "))
price = materialcost * 1.1 + hours * 0.036 + labourhours * 5
rounded_up_price = math.ceil(price * 100) / 100.0

print("Price: ", rounded_up_price)