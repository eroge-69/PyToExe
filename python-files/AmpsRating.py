"""

                            Online Python Compiler.
                Code, Compile, Run and Debug python program online.
Write your code in this editor and press "Run" button to execute it.

"""

# calculate busbar Current Values
metalDensity = [0.8, 1.2]
Aluminum, copper = metalDensity
width = float(input("Enter the value of width? "))
thick = float(input("Enter the value os thick? "))
Aluamps = float((width * thick * Aluminum))
CuAmps = float(width * thick * copper)
PercentDiff = float(Aluamps / CuAmps)
print("Current Density of :","Aluminium: ",Aluminum,"Copper: ",copper)
print("Alu Busbar Size", width, "mm X", thick, "mm =", Aluamps, "Amps")
print("Cu Busbar Size", width, "mm X", thick, "mm =", CuAmps, "Amps")
print("% Difference between copper and aluminium is:", format(PercentDiff, ".2%"))
