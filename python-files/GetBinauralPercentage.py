rf = []
lf = []

print("Enter frequency of 500k, 1000k, 2000k and 4000k of Right")
for i in range(4):
    rd = int(input())
    rf.append(rd)

print("Enter frequency of 500k, 1000k, 2000k and 4000k of Left")
for i in range(4):
    ld = int(input())
    lf.append(ld)
    
rdb = sum(rf)/4;
ldb = sum(lf)/4;

rmp = (rdb-25)*1.5;
lmp = (ldb-25)*1.5;

print("*********Monaural Percentage of both*********")
print(f"Right = {rmp}%")
print(f"Left = {lmp}%")

minimum = min([rmp,lmp])
maximum = max([rmp,lmp])

bn = (5*minimum)+maximum;
bp = bn/6;
print("\n")
print("*********Binaural Percentage of hearing loss*********")
print(f"You have {bp}% of hearing loss.")