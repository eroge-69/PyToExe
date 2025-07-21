inp = input("Shenaseh Ghabz: ")

x = inp[1]
Ramz = 0

if x == '0':
    Ramz = inp[2:8]
elif inp[1] == '1':
    Ramz = inp[2:8] 
else:
    Ramz = "Null"
    
print("Shenaseh Ghabz:",inp,"Ramz Rayaneh: ",Ramz)