num=int(input("Enter number of family members: "))
#file=open('hellow.txt','w+')
lst=[]
f=open('hellow.txt','w')
for i in range(1,num+1):
        name=input("Enter Name of Family Members: ".format(i))
        f.write("{}\n".format(name))
        lst.append(name)
print("lIST OF FAMILY MAMBERS: ")
print(lst)
f.close()
