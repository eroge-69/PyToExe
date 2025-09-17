alfabet=[" ","!",'"',"#","$","%","&","'","(",")","*","+",",","-",".","/","0","1","2","3","4","5","6","7","8","9",":",";","<","=",">","?","@","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","[","\\","]","^","_","`","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","{","|","}","~"]
for i in range(66):
    alfabet += [chr(1040+i)]

while True:
    print("1--зашифровать")
    print("2--разшифровать")
    g=input()
    if g==("1"):
        print("Введите сообщение")
        messege=input()
        print("Введите код шифрования")
        kod=input()
        kod=[i for i in kod]
        messege_copy=[i for i in messege]
        for i in range(len(messege_copy)):
            for j in range(len(alfabet)):
                if messege_copy[i]==alfabet[j]:
                    messege_copy[i]=j
                    break
        for i in range(len(kod)):
            for j in range(len(alfabet)):
                if kod[i]==alfabet[j]:
                    kod[i]=j
                    break
        work=0
        for i in range(len(messege_copy)):
            if work<len(kod)-1:
                work=work+1
            else:
                work=0
            messege_copy[i]=messege_copy[i]+kod[work]
        for i in range(len(messege_copy)):
            if messege_copy[i]<(len(alfabet)):
                messege_copy[i]=alfabet[messege_copy[i]]
            else:
                messege_copy[i]=alfabet[messege_copy[i]-(len(alfabet))]
        messege=""
        for i in messege_copy:
            messege=messege+i
        print(messege)
    if g==("2"):
        print("Введите сообщение")
        messege=input()
        print("Введите код шифрования")
        kod=input()
        kod=[i for i in kod]
        messege_copy=[i for i in messege]
        for i in range(len(messege_copy)):
            for j in range(len(alfabet)-1):
                if messege_copy[i]==alfabet[j]:
                    messege_copy[i]=j
                    break
        for i in range(len(kod)):
            for j in range(len(alfabet)):
                if kod[i]==alfabet[j]:
                    kod[i]=j
                    break
        work=0
        for i in range(len(messege_copy)):
            if work<len(kod)-1:
                work=work+1
            else:
                work=0
            messege_copy[i]=messege_copy[i]-kod[work]
        for i in range(len(messege_copy)):
            if messege_copy[i]<len((alfabet))-1:
                messege_copy[i]=alfabet[messege_copy[i]]
            else:
                messege_copy[i]=alfabet[messege_copy[i]-(len(alfabet)-1)]
        messege=""
        for i in messege_copy:
            messege=messege+i
        print(messege)
