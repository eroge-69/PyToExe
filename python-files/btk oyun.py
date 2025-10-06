
a = input("İsim ve soyisminizi girin: ")


b = "ertasdopklşnmö"

sonuc = ""
for harf in a:
    if harf.lower() not in b:
        sonuc += harf

print("Son hali:", sonuc)
if a.strip().lower() == "ege diker":
    print("Tebrikler! 🎉")