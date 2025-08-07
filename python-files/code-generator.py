import random

with open("prices.txt") as file:
    for i in file:
        i=float(i)
        i=i*100
        code=str()
        while i >= 1:
            cd=ord(str(int(i % 10)))
            if cd == 48:
                code=code+"O"
            else:
                code=code+chr(cd+16)
            i=i/10
        code=code[::-1]
        if code[-2:]=="OO":
            code= code[:-2]+"##"
        lastcode=["#","#","#","#","#","#","#","#"]
        lastcode[7]=code[-1:]
        lastcode[6]=code[-2:-1]
        code=code[:-2]
        while code!="":
            lastcode[random.randint(len(code)*2-2,len(code)*2-1)]=code[-1:]
            code=code[:-1]
        for i in range(len(lastcode)):
            if(lastcode[i]=="#"):
                lastcode[i]=random.choice(["J","K","L","M","N","P","Q","R","S","T","U","V","W","X","Y","Z"])
        end=""
        for i in lastcode:
            end=end+i
        print(end)


input()
