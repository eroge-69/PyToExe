import random

zar = 0

while zar != 6:
    input("Zar atmak için Enter'a bas lan Yusufi") 
    zar = random.randint (1, 6) 
    print("Zar", zar, "çıktı Yusufi") 

    if zar == 6:  
        print("Helal lan Yusufi") 
    else:  
        print("Tekrar dene Yusufi") 
zar = 0

input("Enter'a bas ve çık Yusufi")