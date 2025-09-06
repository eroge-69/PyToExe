voltage = int(input("Vin: "))
resistance_one = int(input("Resistance 1: "))
resistance_two = int(input("Resistance 2: "))

Vout = voltage*(resistance_two/(resistance_one+resistance_two))

print("Vin: "+ str(voltage) + " volts")
print("R1: " + str(resistance_one) +" ohms")
print("R2: "+ str(resistance_two)+" ohms")


print("Vout: " + str(Vout)+" volts")