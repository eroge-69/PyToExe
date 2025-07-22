import random
sample_size = 8
at = int(random.randint(1,8))
my_numbers = [48,49,50,51,52,53,54,55,56,57,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122
]
random_numbers = random.sample(my_numbers, sample_size)
if at==1: 
    c1=chr(64) 
else: 
    c1=chr(int(random_numbers[0]))
if at==2: 
    c2=chr(64) 
else: 
    c2=chr(int(random_numbers[1]))
if at==3: 
    c3=chr(64) 
else: 
    c3=chr(int(random_numbers[2]))
if at==4: 
    c4=chr(64) 
else: 
    c4=chr(int(random_numbers[3]))
if at==5: 
    c5=chr(64) 
else: 
    c5=chr(int(random_numbers[4]))
if at==6: 
    c6=chr(64) 
else: 
    c6=chr(int(random_numbers[5]))
if at==7: 
    c7=chr(64) 
else: 
    c7=chr(int(random_numbers[6]))
if at==8: 
    c8=chr(64) 
else: 
    c8=chr(int(random_numbers[7]))
print(c1,c2,c3,c4,c5,c6,c7,c8,sep="")