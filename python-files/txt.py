a=open("a.txt","r+")
l=a.readlines()
s='y'
while s=='y':
    n=int(input("enter no of bill "))
    for i in range(0,n):
        name=input("enter your bill")
        a.write(name)
        a.write("\n")
        a.flush()
    s=input("do you want more")
a.close()
print("over")
