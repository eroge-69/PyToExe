import random
file=open(r"username.txt")

now=file.readline()
l=now.split(";")        #each name as seperate element

for i in range(1):  #no. of names
    b=random.randint(0,len(l)-1)
    print(l[b])