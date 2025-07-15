Matematik= int( input('Mat notunu gir: '))
Turkce = int(input('TR notunu gir: '))
Fen = int(input('Fen notunu gir: '))
Ortalama = (Matematik + Turkce + Fen)/3
print("Ortalaman: ",Ortalama)
if Ortalama > 100:
    print("Sallama ya böyle not olamazz")
elif Ortalama == 100:
    print("Muhteşem!")
elif Ortalama >=85:
    print("Hiç fena değil")
elif Ortalama >=70:
    print("Fena değil")
elif Ortalama >=50:
    print("Geçtin")
elif 1< Ortalama <50:
    print("KALDIN!")
else:
 print("Ciddi misin? ", Ortalama ," bu puan ne?!?")