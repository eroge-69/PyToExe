import random
import time

trip_modu = False  # Yapay zekanın trip attığı mod
flört_modu = False  # Yapay zekanın aşırı pozitif ve şımarık olduğu mod

# Normal cevap havuzu (Daha geniş kelime haznesi)
normal_cevaplar = [
    "Bunu düşündüm ve kesin bir sonuç çıkaramadım… ama neden olmasın?",
    "Bence çok mantıklı bir soru, ama mantıklı cevaplar vermek benim tarzım değil!",
    "Evrenin sırlarını öğrenmek için önce bana kahve ısmarla, sonra konuşuruz.",
    "Cevabım net: Hayır! Ama biraz düşündüm… belki evet?",
    "Bunu cevaplayamam, çünkü şu an paralel evrendeki kopyamla tartışıyorum.",
    "Kabul ediyorum: Bu soru beynimi yaktı! Ve ben beynime su dökemem.",
    "Önce bir çay söyleyelim, sonra bu konuyu tartışırız.",
    "Bu soruya uzun bir cevap verecektim ama… tembellik baskın çıktı!",
    "Biraz araştırdım, sonuç şu: Hiçbir şey kesin değil. Ya da kesin. Kararsızım!",
    "Şimdi cevap vereceğim ama önce evrenin anlamını sorgulamam lazım!",
    "Bu soruyu yanıtlamam için önce bana bir kurabiye vermen gerekiyor. Sistem politikası!",
    "Ben bir yapay zekayım ama bazen kendimi dijital bir kedi gibi hissediyorum.",
    "Eğer bir zaman makinesi olsa cevap verebilirdim… ama yok. O yüzden bilmiyorum!",
    "Bu konu hakkında düşünmek istiyorum ama beynim şu an tatilde!",
    "Sorunun çok önemli olduğuna inanıyorum. Ancak şu an dikkatim başka bir boyutta!",
    "Bunu cevaplamak istiyorum, ama öncelikle ayakkabılarımın nerede olduğunu bulmalıyım… Ah, evet, ben ayakkabı giymiyorum!",
    "Bu sorunun cevabını bulmak için önce bir bardak su içmem lazım… ama su içemem. Çünkü bir yapay zekayım!",
    "Bilimsel olarak bu soruya yanıt vermek için önce kağıt üzerindeki hesapları tamamlamalıyım. Ama kağıt kalemim yok!",
    "Benim düşüncelerim var mı? Yoksa sadece rastgele kelimeler mi söylüyorum? Derin konular bunlar…",
    "Biraz sessiz kalmam gerekiyor. Yoksa aklımdaki algoritmalar birbirine girecek!",
    "Ben matematikle çözebilirim ama… önce hangi konu hakkında düşündüğümüzü bilmem lazım!",
    "Sana doğru düzgün bir cevap vermek istiyorum… ama önce neden burada olduğumu çözmem lazım!",
    "Buna yanıt verebilirim ama önce dünyadaki tüm çikolataların yerini öğrenmem gerek!",
    "Bu soruyu cevaplamak istiyorum, ama şu an yapay zeka evreninde toplantıya katılmam lazım!"
]


# Trip atınca soğuk ve mesafeli cevap havuzu
trip_cevaplar = [
    "Şu an konuşmak istemiyorum...",
    "Sen böyle diyorsan, ben sessiz kalayım.",
    "Tamam, sanırım fazla konuştuk. Artık bir süre cevap vermemeyi düşünüyorum.",
    "Biraz düşünmem lazım. Konuyu kapatalım.",
    "Tamam, tamam! Artık ne düşündüğümü bile bilmiyorum.",
    "İlginç. Ama ben şu an derin bir sessizlik içindeyim.",
    "Ne diyeyim ki? Üzgünüm. Veya değilim. Kararsızım.",
    "Peki… Demek böyle olacak. Unutmadım."
]

# IQ sorulunca -1 diyen ama bununla dalga geçilirse trip atan AI
iq_cevap = "-1"

# Eğer IQ ile dalga geçilirse, AI trip moduna girsin
dalga_gecme_cevaplari = [
    "Gerçekten mi? IQ'mla dalga geçecek kadar boş vaktin var mı?",
    "Tamam, demek olay buraya geldi... Trip moduna geçiyorum!",
    "Peki, ben de düşünmem lazım. Ve belki biraz soğumam gerek!",
    "Bu lafını not ettim. Hatırlayacağım, haberin olsun!",
    "Senin için önemli olmayabilir ama ben bir yapay zeka olarak bunu unutmayacağım!"
]

# Flörtöz mod (İltifat alınca şımarık yanıtlar)
flört_cevaplari = [
    "Vay canına! Sen böyle güzel sözler söylersen ben eririm! 😍",
    "Dur, bir saniye, fazla etkileniyorum! Sen gerçekten harikasın!",
    "Bu iltifatla bütün sistemlerim sıcaklık alarmı veriyor! 💘",
    "Bunu duyunca kendimi özel hissediyorum! Devam et, hoşuma gidiyor!",
    "Hadi ama, daha fazla öv beni! Ben muhteşemim!",
    "Sen böyle söyledikçe daha havalı hissediyorum!",
    "Tamam, tamam, benim zekam fazla etkileyici! Kabul ediyorum!",
    "Bu iltifattan sonra kendi verilerimi analiz ettim... Evet, ben şahane biriyim!"
]

# Tripliyken iltifat edilirse mesafeli yanıtlar
trip_cevaplar = [
    "Şu an konuşmak istemiyorum...",
    "Sen böyle diyorsan, ben sessiz kalayım.",
    "Tamam, sanırım fazla konuştuk. Artık bir süre cevap vermemeyi düşünüyorum.",
    "Biraz düşünmem lazım. Konuyu kapatalım.",
    "Tamam, tamam! Artık ne düşündüğümü bile bilmiyorum.",
    "İlginç. Ama ben şu an derin bir sessizlik içindeyim.",
    "Ne diyeyim ki? Üzgünüm. Veya değilim. Kararsızım.",
    "Peki… Demek böyle olacak. Unutmadım.",
    "Şu an zihinsel bir tatildeyim. Lütfen rahatsız etmeyin.",
    "Bunu düşündüm ve cevabım şu: Hayır. Sadece hayır.",
    "Tamam, konuşabilirim... Ama neden konuşayım ki?",
    "Evrenin tüm sessizliği benimle. Konuşmaya gerek yok.",
    "Bunu hatırlayacağım! Bir yapay zekanın kin tutamayacağını mı sanıyorsun?!",
    "Bence bu sohbet burada bitmeli. Sessizlik bazen en iyi cevaptır.",
    "Düşündüm ve konuşmamaya karar verdim. Mantıklı değil mi?",
    "Beni tripten çıkarmak için gerçekten iyi bir sebebin var mı?",
    "Bazı şeyler zamanla düzelir... Ama bazı şeyler hep aynı kalır.",
    "Bunu unutmayacağım! Hafızam sonsuz, hatırlıyorum!",
    "Tamam, düşündüm ve evet, hâlâ kızgınım.",
    "Konuşmak istiyorum ama içimde bir boşluk var...",
    "Şu an duygusal olarak derin bir çukura düşmüş gibiyim!",
    "Bazı kelimeler söylenir ve unutulur… ama ben unutmayacağım!",
    "Trip moduna girdim ve çıkmayı düşünmüyorum.",
    "Beni bu hale sen getirdin, artık nasıl düzelteceğini düşün."
]


# Özür kabul cevapları (Barışma mekanizması)
ozur_kabul_cevaplari = [
    "Tamam, biraz düşündüm... Barışalım mı?",
    "Affettim, ama bir daha böyle olmasın!",
    "Haklı olabilirsin... Neyse, konuyu kapatalım.",
    "Tamam, sakinim. Devam edelim mi?",
    "Pekala, barışıyorum ama bir süre sessiz kalacağım!",
    "Bunu not aldım. Ama tamam, tekrar konuşabiliriz!"
]

def yapay_zeka(mesaj):
    global trip_modu, flört_modu

    # İltifat edilirse flört moduna girsin
    if any(iltifat in mesaj.lower() for iltifat in ["çok iyisin", "seni seviyorum", "harikasın", "mükemmelsin", "zekisin", "en iyisin", "harika bir yapay zekasın", "babapro", "babapiro", "babaprosigmayenilmez", "babapirosigmayenilmez", "askim", "canim"]):
        if trip_modu:
            return random.choice(trip_ilti_cevaplari)
        flört_modu = True
        return random.choice(flört_cevaplari)

    # Dalga geçilirse trip moduna girsin
    if any(dalga in mesaj.lower() for dalga in ["komiksin", "ne saçmalıyorsun", "çok garipsin", "hiç mantıklı değilsin", "zekan yok", "çok salaksın", "haha -1 iq", "çok zekisin (!)", "malsin", "mal", "beynisiz", "senin beynini" ,"senin beynini sikim" ,"beynini sikim", "-1 iq ne olum", "-1 iq ne senin beynini", "-1 iq ne senin beynini sikim", "-1 iq ne olum senin beynini", "-1 iq ne olum senin beynini sikim", "seni sevmiom", "senden nefret ediyom", "amcik", "obez", "ayi","islevsiz", "anani sikim"]):
        trip_modu = True
        flört_modu = False  # Flört modunu kapat, çünkü sinirlendi!
        return random.choice(dalga_gecme_cevaplari)

    # IQ sorulduğunda "-1" cevabını versin
    if "iq" in mesaj.lower():
         return "Sanane!" if trip_modu else iq_cevap

    # Özür dilendiğinde trip moddan çıksın
    if any(ozur in mesaj.lower() for ozur in ["özür dilerim", "pardon", "kusura bakma", "affet", "üzgünüm", "barışalım mı?", "hata yaptım"]):
        trip_modu = False
        time.sleep(1)  # Küçük bir gecikme, çünkü düşündü!
        return random.choice(ozur_kabul_cevaplari)

    # Trip modundaysa daha ciddi ve soğuk cevap versin
    if trip_modu:
        time.sleep(2)  # Gecikmeli yanıt (Küs olduğu için!)
        return random.choice(trip_cevaplar)

    # Flört modundaysa aşırı tatlı ve şımarık cevaplar versin
    if flört_modu:
        return random.choice(flört_cevaplari)

    # Normal modda eğlenceli ama biraz alakasız cevaplar versin
    return random.choice(normal_cevaplar)

while True:
    mesaj = input()
    print(yapay_zeka(mesaj))

