menu=["1. Yanacaq", "2. Market", "3. odenis", "4. Cixis"]
print("NA//FF YDM", "Xos geldiniz", sep="\n")
total=0
exitpoint=0

while True:
        if exitpoint>0:
            if total==0:
                for item in menu:
                    print(item, sep="\n")
                k=int(input("Zehmet olmasa menyudan secim edin: \n"))
        else:
            for item in menu:
                print(item, sep="\n")
            k=int(input("Zehmet olmasa menyudan secim edin (1-4): \n"))
        if k==1:
            bb1=["1. Super/premium/Ai-98: 2.30", "2. Ai-95: 1.60", "3. Ai-92: 1.10", "4. Diesel(dizel): 1.00"]
            bb2=[2.3, 1.6, 1.1, 1]
            while True:
                print("Yanacaq qiymetleri:")
                for item in bb1:
                    print(item)
                choice = int(input("Zehmet olmasa yanacaq secin (1-4): "))
                if choice >0 and choice <= 4:
                    print(bb2[choice-1], "AZN")
                    we=float(input("Nece litr yanacaq alacaqsiniz? "))
                    while True:
                        if we > 0:
                            break
                        else:
                            we=float(input("Yanacaq miqdarini duzgun daxil edin: "))
                    print("Alinan yanacaq: ", we, "litr")
                    total=total+bb2[choice-1]*we
                    print("Toplam qiymet: ", total, "AZN")
                else:
                    print("Zehmet olmasa duzgun secim edin!!!", "Cixmaq ucun 0 daxil edin", sep="\n")
                    if choice == 0:
                        print("Cixis etdim")
                        break
        elif k==2:
            b=["Su: 1.00 AZN","kofe: 1.50 AZN","cay: 0.50 AZN"]
            b1=[1.00,1.50,0.50]
            while True:
                for i in range(len(b)):
                    print(b[i])
                m=input("Ne alacaqsiniz? (1. Su/2. kofe/3. cay). Cixmaq ucun '0' yazin: ")
                if m=="1":
                    total+=b1[0]
                    print("Su alindi. Toplam: ", total, "AZN")       
                elif m=="2":
                    total+=b1[1]
                    print("Kofe alindi. Toplam: ", total, "AZN")
                elif m=="3":
                    total+=b1[2]
                    print("Cay alindi. Toplam: ", total, "AZN")
                elif m=="0":
                    print("Cixis edirsiniz. Toplam odeme: ", total, "AZN")
                    break
                else:
                    print("Yanlis secim!")
                    continue
        elif k==3:
            paymentmethod = input("Odenis metodunu secin (nagdsiz/nagd): ").lower()
            if paymentmethod == "nagdsiz":
                pass
            elif paymentmethod == "nagd":
                print("Nagd odenis edilecek","Toplam: ", total, "AZN", sep="\n")
                while True:
                    pay=float(input("Nece AZN odeneceyinizi daxil edin: "))
                    if pay >= total:
                        change = pay - total
                        print("Odenis ugurlu! Qaliq: ", change, "AZN")
                        total = 0
                        break
                    else:
                        print("Odenis kifayet deyil! Yeniden cəhd edin.")
        elif k==4:
            exitpoint=exitpoint+1
            if total == 0:
                print("Cixis edirsiniz. Toplam borcunuz yoxdur.")
                break
            else:
                k=3
                print("Zehmet olmasa borcunuzu odeyin! Borcunuz: ", total, "AZN")
                continue                
            
print("Tesekkur edirik, gorusmek umidiyle!")