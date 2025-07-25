import time
urun_fiyatlari = {
    "elma": 15,
    "muz": 25,
    "domates": 18,
    "patates": 10,
    "üzüm": 35,
}

print("kayıtlı ürünler:")
for urun in urun_fiyatlari:
    print("-", urun.capitalize())

urun_adi = input("ürün adını giriniz: ").lower()
if urun_adi in urun_fiyatlari:
    birim_fiyat = urun_fiyatlari[urun_adi]
    print(f"{urun_adi.capitalize()} için birim fiyat olarak belirlendi: {birim_fiyat} TL")
else:
    birim_fiyat = float(input("Bu ürün tanımlı değil. Lütfen birim fiyatı girin: "))
miktar = float(input("Miktarı giriniz "))
tutar = birim_fiyat * miktar
print("\n---------- FİŞİNİZ ----------")
print(f"Ürün: {urun_adi.capitalize()}")
print(f"miktar: {miktar} kg")
print(f"Toplam Tutar {tutar:.2f} TL")

indirim_orani = 0.15
if tutar > 200:
    indirim_tutari = tutar * indirim_orani
    tutar_indirimli = tutar - indirim_tutari
    print(f"İndirim: %{int(indirim_orani * 100)} - {indirim_tutari:.2f} TL")
    print(f"İndirimli Tutar: {tutar_indirimli:.2f} TL")
    print("İndirim kazandınızz")
else:
    print("Toplam tutar bu kadardır.")
time.sleep(15)


