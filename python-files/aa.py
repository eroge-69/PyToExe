print("Bu oyunda iki oyuncu bir sayı(birbirinden farklı) girer(5-10-15-20). Sonra ikisi de 0,5 ya da 10 sayılarından birini seçer. İki oyuncu da sayılarını seçtikten sonra iki sayı toplanır. Toplam iki oyuncunun sayılarından birine eşitse oyunu o oyuncu kazanır değilse devam ederler.")

a = 100

c = [5,10,15,20]
d = [0,5,10]

for k in range (0,a):

    s1 = int(input("Birinci yarışmacı seçilen sayı(5-10-15-20) : "))
    s2 = int(input("İkinci yarışmacı seçilen sayı(5-10-15-20) : "))

    if(s1 != s2 and s1 in c and s2 in c ):
    
     for i in range(0,a):
        
            t1 = int(input("Birinci yarışmacı girilen sayı(0-5-10) : "))
            print("      "*10000)
            t2 = int(input("İkinci yarışmacı girilen sayı (0-5-10) : "))
            print("      "*10000)

            if(t1 in d and t2 in d):
    
                s = t1 + t2

                if(s == s1):
                    print("Birinci yarışmacı oyuncu kazandı!!!")
                    break
                elif(s == s2):
                    print("İkinci yarışmacı oyuncu kazandı!!!")
                    break
                else:
                    print(f"Toplam : {s} ")
                    a += 1
            else:
                print("Hatalı değer girişi... ")
    else:
            print("Hatalı değer girişi... ")
            
    b = str(input("Bir daha oynamak ister misiniz(evet/hayır) : "))
    if(b != "evet"):
        break