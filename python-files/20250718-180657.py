print("задача")
print()
spisok = []
meny = ["добавит задачу n1",
        "посмотр есть задача n2",
        "выход n3c"]

for menu in meny:
    print(menu + "\n")
    
while True:
    pihi = input("пиши номер задачы: ")
    
    if pihi == "n1":
        pih = input("пиши  задачу: ")
        spisok.append(pih)
    
    elif pihi == "n2":
        print(spisok)
        
    elif pihi == "n3c":
        break  
        
        
    
    
    
    
    
    