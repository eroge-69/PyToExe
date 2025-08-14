# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 09:41:24 2025

@author: EBRA KANKILIÇ
"""


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import datetime
now = datetime.datetime.now()
later = now + datetime.timedelta(minutes=5)
import random 
import json 
import os


KAYITLI_KULLANICI = "ardacandan"
KAYITLI_SIFRE = "12345"
oabt_sorular = [
    {"soru":"Aşağıdaki cümlelerden hangisinde anlatım bozukluğu vardır?","secenekler":["A) Kitapları raftan aldım ve okumaya başladım.","B) Evime geldiğimde annem yemek yapıyordu.","C) Bugün okula giderken yağmur yağıyordu ama şemsiye almadım.","D) Dün sinemaya gittiğimde arkadaşlarımı görmemiştim."],"dogru":"D"},
    {"soru":"Hangisi doğru yazılmıştır?","secenekler":["A) Kitapları raftan aldım.","B) Kitapları raftan aldim.","C) Kitapları raftan aldim.","D) Kitapları raftan aldim."],"dogru":"A"},
    {"soru":"Aşağıdakilerden hangisi fiilimsidir?","secenekler":["A) Koşmak","B) Güzel","C) Kitap","D) Masa"],"dogru":"A"},
    {"soru":"Hangi cümlede ‘-ki’ eki yerinde kullanılmıştır?","secenekler":["A) Biliyorum ki o gelecek.","B) Kitap ki masanın üstünde.","C) Geldi ki o çok mutlu oldu.","D) Hava ki çok soğuk."],"dogru":"A"},
    {"soru":"Aşağıdaki cümlelerden hangisinde noktalama hatası vardır?","secenekler":["A) Ali gel, kitapları al.","B) Hava çok güzel bugün.","C) Kitapları aldım ve eve gittim.","D) Dün sinemaya gittim ve film izledim"],"dogru":"D"},
    {"soru":"Aşağıdakilerden hangisi isim tamlamasıdır?","secenekler":["A) Ev kapısı","B) Koşmak","C) Güzelce yazdı","D) Hızlı koşuyor"],"dogru":"A"},
    {"soru":"Aşağıdaki cümlelerden hangisinde anlatım bozukluğu vardır?","secenekler":["A) O, çok çalışıyor ve başarılı.","B) Kitap okumak, benim hobimdir.","C) Ali, sınıfta öğretmenle tartıştı ama kimse görmedi.","D) Dün sinemaya gittim ve arkadaşlarımı gördüm."],"dogru":"C"},
    {"soru":"Hangisi yanlış yazılmıştır?","secenekler":["A) Öğrenci sınava hazırlandı.","B) Öğrenci sınava hazirlandi.","C) Öğrenci sınava hazırlandı.","D) Öğrenci sınava hazırlandı."],"dogru":"B"},
    {"soru":"Aşağıdaki cümlelerden hangisi olumludur?","secenekler":["A) Ali okula gitmedi.","B) Hava çok kötüydü.","C) Ben sinemaya gidiyorum.","D) O, hiçbir zaman gelmez."],"dogru":"C"},
    {"soru":"Aşağıdaki cümlelerden hangisi soru cümlesidir?","secenekler":["A) Ali dün sinemaya gitti.","B) Hangi kitabı okuyorsun?","C) Bugün çok güzel bir gün.","D) O, kitaplarını aldı."],"dogru":"B"},
    {"soru":"‘Bu sabah çok erken kalktım.’ cümlesinde zaman zarfı hangisidir?","secenekler":["A) Bu sabah","B) Çok","C) Erken","D) Kalktım"],"dogru":"A"},
    {"soru":"Aşağıdaki cümlelerden hangisinde çelişki vardır?","secenekler":["A) Ali hem çalıştı hem de dinlendi.","B) Hava hem sıcak hem soğuktu.","C) Kitabı okuyup bitirdi.","D) Film çok güzeldi."],"dogru":"B"},
    {"soru":"Aşağıdakilerden hangisi fiildir?","secenekler":["A) Kitap","B) Koşuyor","C) Güzel","D) Masa"],"dogru":"B"},
    {"soru":"‘Ali çok hızlı koştu.’ cümlesinde yüklem hangisidir?","secenekler":["A) Ali","B) Çok hızlı","C) Koştu","D) Hızlı"],"dogru":"C"},
    {"soru":"Aşağıdakilerden hangisi sıfattır?","secenekler":["A) Güzel","B) Koşmak","C) Kitap","D) Koştu"],"dogru":"A"},
    {"soru":"‘Kitabı masaya koydum.’ cümlesinde nesne hangisidir?","secenekler":["A) Kitabı","B) Masaya","C) Koydum","D) Masaya koydum"],"dogru":"A"},
    {"soru":"‘Ahmet hızlı koşuyor, fakat yorgun.’ cümlesinde bağlaç hangisidir?","secenekler":["A) Ahmet","B) Fakat","C) Hızlı","D) Yorgun"],"dogru":"B"},
    {"soru":"‘Ali dün sinemaya gitti mi?’ cümlesi hangi türdedir?","secenekler":["A) Olumlu","B) Olumsuz","C) Soru","D) Ünlem"],"dogru":"C"},
    {"soru":"‘O, kitap okuyor.’ cümlesinde özne hangisidir?","secenekler":["A) O","B) Kitap","C) Okuyor","D) Kitap okuyor"],"dogru":"A"},
    {"soru":"‘Benim arabam yeni.’ cümlesinde sahiplik eki hangisidir?","secenekler":["A) Benim","B) Arabam","C) Yeni","D) Arabam yeni"],"dogru":"B"},
    {"soru":"‘Ders çalışmak çok önemli.’ cümlesinde yüklem hangisidir?","secenekler":["A) Ders","B) Çalışmak","C) Çok önemli","D) Önemli"],"dogru":"C"},
    {"soru":"‘Hava çok soğuktu.’ cümlesinde nitelik belirten sözcük hangisidir?","secenekler":["A) Hava","B) Çok","C) Soğuktu","D) Hava çok soğuktu"],"dogru":"B"},
    {"soru":"‘Kitabı okudum ama anlamadım.’ cümlesinde hangi bağlaç kullanılmıştır?","secenekler":["A) Ama","B) Ve","C) Çünkü","D) Fakat"],"dogru":"A"},
    {"soru":"‘Ali, kitapları masaya koydu.’ cümlesinde nesne hangisidir?","secenekler":["A) Ali","B) Kitapları","C) Masaya","D) Koydu"],"dogru":"B"},
    {"soru":"‘Okuldan sonra eve gideceğim.’ cümlesinde zarf tümleci hangisidir?","secenekler":["A) Okuldan sonra","B) Eve","C) Gideceğim","D) Sonra"],"dogru":"A"},
    {"soru":"‘O, çok çalışıyor.’ cümlesinde belirten sözcük hangisidir?","secenekler":["A) O","B) Çok","C) Çalışıyor","D) Çalışıyor çok"],"dogru":"B"},
    {"soru":"‘Ali, sınıfta kitap okuyor.’ cümlesinde yer belirten sözcük hangisidir?","secenekler":["A) Ali","B) Sınıfta","C) Kitap","D) Okuyor"],"dogru":"B"},
    {"soru":"‘Dün sinemaya gittim.’ cümlesinde zaman zarfı hangisidir?","secenekler":["A) Dün","B) Sinemaya","C) Gittim","D) Dün sinemaya"],"dogru":"A"},
    {"soru":"‘Ali hem çalıştı hem de dinlendi.’ cümlesinde bağlaç hangisidir?","secenekler":["A) Hem…hem…","B) Ve","C) Ama","D) Fakat"],"dogru":"A"},
    {"soru":"‘Kitabı masaya koydum.’ cümlesinde yönelme durumu eki hangisidir?","secenekler":["A) Kitabı","B) Masaya","C) Koydum","D) Masaya koydum"],"dogru":"B"},
    {"soru":"‘Okula gidiyor musun?’ cümlesinde kip eki hangisidir?","secenekler":["A) Gidiyor","B) Musun","C) Okula","D) Gidiyor musun"],"dogru":"B"},
    {"soru":"‘Ali kitap okuyor mu?’ cümlesinde soru eki hangisidir?","secenekler":["A) Ali","B) Mu","C) Kitap","D) Okuyor"],"dogru":"B"},
    {"soru":"‘Benim adım Ahmet.’ cümlesinde özne hangisidir?","secenekler":["A) Benim","B) Adım","C) Ahmet","D) Ben"],"dogru":"D"},
    {"soru":"‘Okula gitmek istiyorum.’ cümlesinde mastar eki hangi sözcüktedir?","secenekler":["A) Okula","B) Gitmek","C) İstiyorum","D) Okula gitmek"],"dogru":"B"},
    {"soru":"‘Ali çok hızlı koşuyor.’ cümlesinde zarf hangisidir?","secenekler":["A) Ali","B) Çok","C) Hızlı","D) Koşuyor"],"dogru":"B"},
    {"soru":"‘Kitabı aldım.’ cümlesinde yüklem hangisidir?","secenekler":["A) Kitabı","B) Aldım","C) Kitabı aldım","D) Aldım kitabı"],"dogru":"B"},
    {"soru":"‘Ahmet çalışkan bir öğrencidir.’ cümlesinde sıfat hangisidir?","secenekler":["A) Ahmet","B) Çalışkan","C) Öğrencidir","D) Bir"],"dogru":"B"},
    {"soru":"‘Ders çalışmak gerekli.’ cümlesinde hangi sözcük yüklemdir?","secenekler":["A) Ders","B) Çalışmak","C) Gerekli","D) Ders çalışmak"],"dogru":"C"},
    {"soru":"‘Ali, kitap okuyor ve yazıyor.’ cümlesinde bağlaç hangisidir?","secenekler":["A) Ali","B) Ve","C) Okuyor","D) Yazıyor"],"dogru":"B"},
    {"soru":"‘Ben sinemaya gideceğim.’ cümlesinde gelecek zaman eki hangi sözcüktedir?","secenekler":["A) Ben","B) Gidiyorum","C) Gideceğim","D) Sinemaya"],"dogru":"C"},
    {"soru":"‘Kitap okuyorum.’ cümlesinde şimdiki zaman eki hangi sözcüktedir?","secenekler":["A) Kitap","B) Okuyorum","C) Kitap okuyorum","D) Okuyorum kitap"],"dogru":"B"},
    {"soru":"‘Ali, çok çalıştı.’ cümlesinde belirten sözcük hangisidir?","secenekler":["A) Ali","B) Çok","C) Çalıştı","D) Ali çok"],"dogru":"B"},
    {"soru":"‘Benim kalemim kırmızı.’ cümlesinde sahiplik eki hangisidir?","secenekler":["A) Benim","B) Kalemim","C) Kırmızı","D) Kalem"],"dogru":"B"},
    {"soru":"‘Hemen gel!’ cümlesinde ünlem cümlesi hangi türdür?","secenekler":["A) Soru","B) Olumlu","C) Olumsuz","D) Emir"],"dogru":"D"},
    {"soru":"‘Ali okula gidiyor, fakat geç kaldı.’ cümlesinde bağlaç hangisidir?","secenekler":["A) Ve","B) Fakat","C) Ama","D) Çünkü"],"dogru":"B"},
    {"soru":"‘Bu sabah erken kalktım.’ cümlesinde zaman zarfı hangisidir?","secenekler":["A) Bu sabah","B) Erken","C) Kalktım","D) Sabah"],"dogru":"A"},
    {"soru":"‘Ali, kitap okuyor mu?’ cümlesinde soru eki hangisidir?","secenekler":["A) Ali","B) Mu","C) Kitap","D) Okuyor"],"dogru":"B"},
    {"soru":"‘Benim adım Ahmet.’ cümlesinde özne hangisidir?","secenekler":["A) Benim","B) Adım","C) Ahmet","D) Ben"],"dogru":"D"},
    {"soru":"‘Ders çalışmak çok önemli.’ cümlesinde yüklem hangisidir?","secenekler":["A) Ders","B) Çalışmak","C) Çok önemli","D) Önemli"],"dogru":"C"},
    {"soru":"‘Kitabı okudum ama anlamadım.’ cümlesinde bağlaç hangisidir?","secenekler":["A) Ama","B) Ve","C) Çünkü","D) Fakat"],"dogru":"A"},
    {"soru":"‘Ali hem çalıştı hem de dinlendi.’ cümlesinde bağlaç hangisidir?","secenekler":["A) Hem…hem…","B) Ve","C) Ama","D) Fakat"],"dogru":"A"}
]

sözel_sayısal_sorular = [
    {"soru": "Ali 5 elma, Ayşe 3 elma yedi. Toplam kaç elma yediler?", "secenekler": ["6", "7", "8", "9"], "cevap": "8"},
    {"soru": "Bir sayı 12 ile çarpıldığında 144 elde ediliyor. Bu sayı kaçtır?", "secenekler": ["10", "11", "12", "13"], "cevap": "12"},
    {"soru": "3, 6, 9, ? , 15. ? yerine hangi sayı gelmelidir?", "secenekler": ["10", "11", "12", "13"], "cevap": "12"},
    {"soru": "Bir odadaki sandalyelerin sayısı 24'tür. 8 kişi her biri bir sandalye kullanacak. Kaç sandalye boş kalır?", "secenekler": ["12", "16", "18", "24"], "cevap": "16"},
    {"soru": "Bir kelimeyi tersten okuduğunda aynı kalan kelime hangisidir?", "secenekler": ["ANANAS", "KAPI", "OKUL", "Masa"], "cevap": "ANANAS"},
    {"soru": "Aşağıdaki kelimelerden hangisi zıt anlamlıdır? Hızlı – ?", "secenekler": ["Yavaş", "Çabuk", "Acele", "Süratli"], "cevap": "Yavaş"},
    {"soru": "Bir dikdörtgenin alanı 48 m², kısa kenarı 6 m. Uzun kenar kaç metredir?", "secenekler": ["6", "7", "8", "9"], "cevap": "8"},
    {"soru": "4 + 3 × 2 işleminin sonucu kaçtır?", "secenekler": ["10", "14", "12", "8"], "cevap": "10"},
    {"soru": "Kelimeleri alfabetik sıraya koyunuz: Elma, Armut, Muz, Kiraz", "secenekler": ["Armut, Elma, Kiraz, Muz", "Elma, Armut, Kiraz, Muz", "Muz, Kiraz, Armut, Elma", "Kiraz, Elma, Muz, Armut"], "cevap": "Armut, Elma, Kiraz, Muz"},
    {"soru": "Bir havuz 5 saatte doluyor. Aynı havuz 2 saat daha hızlı dolsa, kaç saatte dolar?", "secenekler": ["3", "3.5", "4", "4.5"], "cevap": "3"},
    {"soru": "5 × 4 + 6 ÷ 3 işleminin sonucu kaçtır?", "secenekler": ["20", "22", "21", "23"], "cevap": "22"},
    {"soru": "Ali'nin yaşı 12, Ayşe Ali’den 3 yaş küçük. İkisi yaşları toplamı kaçtır?", "secenekler": ["21", "22", "23", "24"], "cevap": "21"},
    {"soru": "Hangi sayı çift değildir? 2, 4, 7, 8", "secenekler": ["2", "4", "7", "8"], "cevap": "7"},
    {"soru": "Bir küpün tüm yüzleri boyanıyor. Küp 8 küçük küpe bölünüyor. Kaç küçük küpün hiç yüzü boyanmaz?", "secenekler": ["0", "1", "2", "4"], "cevap": "0"},
    {"soru": "Bir sayı 5 arttırıldığında 20 oluyor. Sayı kaçtır?", "secenekler": ["10", "12", "15", "16"], "cevap": "15"},
    {"soru": "Hangi kelime eş anlamlıdır? Mutlu – ?", "secenekler": ["Sevinçli", "Üzgün", "Kızgın", "Sinirli"], "cevap": "Sevinçli"},
    {"soru": "Bir çiftlikte 12 tavuk ve 8 inek var. Toplam ayak sayısı kaçtır?", "secenekler": ["40", "44", "48", "50"], "cevap": "56"},
    {"soru": "Bir sayının yarısı 10 ise sayı kaçtır?", "secenekler": ["10", "15", "20", "25"], "cevap": "20"},
    {"soru": "Aşağıdakilerden hangisi bir üçgenin özelliklerinden değildir?", "secenekler": ["Üç kenarı vardır", "Üç açısı vardır", "Kenarları eşit olmalıdır", "İç açıları toplamı 180°"], "cevap": "Kenarları eşit olmalıdır"},
    {"soru": "8 × 3 ÷ 4 işleminin sonucu kaçtır?", "secenekler": ["4", "5", "6", "7"], "cevap": "6"}
]

tarih_sorular = [
    {"soru": "Türklerin Orta Asya'daki en eski devleti hangisidir?", "secenekler": ["Göktürkler", "Uygurlar", "Hunlar", "Selçuklular"], "cevap": "Hunlar"},
    {"soru": "Osmanlı Devleti'nin kuruluş tarihi hangisidir?", "secenekler": ["1299", "1453", "1071", "1330"], "cevap": "1299"},
    {"soru": "Malazgirt Meydan Muharebesi hangi yılda yapılmıştır?", "secenekler": ["1071", "1453", "1243", "1361"], "cevap": "1071"},
    {"soru": "İstanbul'un Fethi hangi padişah döneminde gerçekleşmiştir?", "secenekler": ["Fatih Sultan Mehmet", "II. Beyazıt", "Yavuz Sultan Selim", "Sultan Abdülhamid"], "cevap": "Fatih Sultan Mehmet"},
    {"soru": "Tanzimat Fermanı hangi yılda ilan edilmiştir?", "secenekler": ["1839", "1856", "1876", "1921"], "cevap": "1839"},
    {"soru": "Lozan Antlaşması hangi yıl imzalanmıştır?", "secenekler": ["1923", "1919", "1920", "1930"], "cevap": "1923"},
    {"soru": "Mustafa Kemal Atatürk'ün doğum yılı nedir?", "secenekler": ["1881", "1876", "1890", "1885"], "cevap": "1881"},
    {"soru": "Saltanatın kaldırılması hangi yıl gerçekleşmiştir?", "secenekler": ["1922", "1920", "1923", "1924"], "cevap": "1922"},
    {"soru": "Cumhuriyetin ilanı hangi yıl olmuştur?", "secenekler": ["1923", "1920", "1921", "1922"], "cevap": "1923"},
    {"soru": "İlk Türk kadın milletvekilleri hangi yıl seçilmiştir?", "secenekler": ["1935", "1927", "1930", "1945"], "cevap": "1935"},
    {"soru": "II. Meşrutiyet hangi yılda ilan edilmiştir?", "secenekler": ["1908", "1876", "1912", "1920"], "cevap": "1908"},
    {"soru": "Saltanat ve Hilafet hangi padişah döneminde kaldırılmıştır?", "secenekler": ["Vahdettin", "Abdülmecid", "II. Mahmud", "Mehmet Reşat"], "cevap": "Vahdettin"},
    {"soru": "Kurtuluş Savaşı hangi yıllar arasında yapılmıştır?", "secenekler": ["1919-1923", "1914-1918", "1920-1922", "1918-1922"], "cevap": "1919-1923"},
    {"soru": "Sakarya Meydan Muharebesi hangi yıl olmuştur?", "secenekler": ["1921", "1920", "1922", "1923"], "cevap": "1921"},
    {"soru": "Lozan Antlaşması ile hangi ülkenin sınırları kesinleşmiştir?", "secenekler": ["Türkiye", "Yunanistan", "İtalya", "Fransa"], "cevap": "Türkiye"},
    {"soru": "Atatürk'ün eğitim alanında yaptığı ilk inkılap hangisidir?", "secenekler": ["Tevhid-i Tedrisat Kanunu", "Medreselerin açılması", "Maarif teşkilatı", "Latin alfabesi"], "cevap": "Tevhid-i Tedrisat Kanunu"},
    {"soru": "Osmanlı Devleti hangi savaşla parçalanma sürecine girmiştir?", "secenekler": ["I. Dünya Savaşı", "II. Balkan Savaşı", "Çanakkale Savaşı", "Kurtuluş Savaşı"], "cevap": "I. Dünya Savaşı"},
    {"soru": "Anadolu ve Rumeli Müdafaa-i Hukuk Cemiyeti hangi yıl kurulmuştur?", "secenekler": ["1919", "1918", "1920", "1921"], "cevap": "1919"},
    {"soru": "İzmir’in işgali hangi tarihte gerçekleşmiştir?", "secenekler": ["1919", "1920", "1918", "1921"], "cevap": "1919"},
    {"soru": "Sevr Antlaşması hangi yılda imzalanmıştır?", "secenekler": ["1920", "1918", "1919", "1921"], "cevap": "1920"}
]

turkiye_sorular = [
    {"soru": "Türkiye’nin en uzun nehri hangisidir?", "secenekler": ["Kızılırmak", "Fırat", "Dicle", "Yeşilırmak"], "cevap": "Kızılırmak"},
    {"soru": "Türkiye’nin en yüksek dağı hangisidir?", "secenekler": ["Ağrı Dağı", "Erciyes", "Kaçkar", "Süphan"], "cevap": "Ağrı Dağı"},
    {"soru": "Türkiye hangi kıtalarda yer alır?", "secenekler": ["Avrupa ve Asya", "Sadece Asya", "Sadece Avrupa", "Avrupa ve Afrika"], "cevap": "Avrupa ve Asya"},
    {"soru": "Türkiye’nin en büyük gölü hangisidir?", "secenekler": ["Van Gölü", "Tuz Gölü", "Beyşehir Gölü", "Eğirdir Gölü"], "cevap": "Van Gölü"},
    {"soru": "İç Anadolu Bölgesi hangi iklim özelliğine sahiptir?", "secenekler": ["Kara iklimi", "Akdeniz iklimi", "Karadeniz iklimi", "Marmara iklimi"], "cevap": "Kara iklimi"},
    {"soru": "Türkiye’nin en büyük adası hangisidir?", "secenekler": ["Gökçeada", "Bozcaada", "Burgaz", "Heybeliada"], "cevap": "Gökçeada"},
    {"soru": "Karadeniz Bölgesi’nde tarımda en çok hangi ürün yetişir?", "secenekler": ["Fındık", "Buğday", "Arpa", "Pamuk"], "cevap": "Fındık"},
    {"soru": "Türkiye’nin başkenti neresidir?", "secenekler": ["Ankara", "İstanbul", "İzmir", "Bursa"], "cevap": "Ankara"},
    {"soru": "Marmara Bölgesi’nin yüzölçümü açısından en büyük ili hangisidir?", "secenekler": ["Bursa", "İstanbul", "Edirne", "Kocaeli"], "cevap": "Bursa"},
    {"soru": "Akdeniz Bölgesi’nin tipik bitki örtüsü hangisidir?", "secenekler": ["Makilik", "Step", "Orman", "Çayır"], "cevap": "Makilik"},
    {"soru": "Türkiye’nin en uzun kıyı şeridine sahip bölgesi hangisidir?", "secenekler": ["Ege", "Akdeniz", "Karadeniz", "Marmara"], "cevap": "Ege"},
    {"soru": "Türkiye’nin en sıcak bölgesi hangisidir?", "secenekler": ["Güneydoğu Anadolu", "İç Anadolu", "Karadeniz", "Marmara"], "cevap": "Güneydoğu Anadolu"},
    {"soru": "Doğu Anadolu Bölgesi’nde yer alan göl hangisidir?", "secenekler": ["Van Gölü", "Tuz Gölü", "Beyşehir", "Eğirdir"], "cevap": "Van Gölü"},
    {"soru": "Türkiye’de en fazla yağış alan bölge hangisidir?", "secenekler": ["Karadeniz", "Akdeniz", "Ege", "İç Anadolu"], "cevap": "Karadeniz"},
    {"soru": "Türkiye’de tarım alanı en fazla olan ürün hangisidir?", "secenekler": ["Buğday", "Pamuk", "Mısır", "Çeltik"], "cevap": "Buğday"},
    {"soru": "İstanbul Boğazı hangi iki denizi birbirine bağlar?", "secenekler": ["Marmara ve Karadeniz", "Marmara ve Ege", "Ege ve Akdeniz", "Karadeniz ve Akdeniz"], "cevap": "Marmara ve Karadeniz"},
    {"soru": "Türkiye’nin en kuzey noktası nerededir?", "secenekler": ["Sinop", "İğneada", "Kars", "Edremit"], "cevap": "Sinop"},
    {"soru": "Türkiye’nin en güney noktası nerededir?", "secenekler": ["Hatay", "Mersin", "Adana", "Şanlıurfa"], "cevap": "Hatay"},
    {"soru": "Türkiye’nin en batı noktası nerededir?", "secenekler": ["Gökçeada", "Çanakkale", "İzmir", "Muğla"], "cevap": "Gökçeada"},
    {"soru": "Türkiye’nin en doğu noktası nerededir?", "secenekler": ["Iğdır", "Ağrı", "Van", "Hakkari"], "cevap": "Iğdır"}
]

egitimin_temelleri_sorular = [
    {"soru": "Eğitim kavramı hangi yaş grubunu kapsar?", "secenekler": ["Bütün yaş grupları", "Sadece çocuklar", "Sadece gençler", "Sadece yetişkinler"], "cevap": "Bütün yaş grupları"},
    {"soru": "Formel eğitim nedir?", "secenekler": ["Okullarda sistemli eğitim", "Evde eğitim", "Deneyim yoluyla eğitim", "Oyun yoluyla eğitim"], "cevap": "Okullarda sistemli eğitim"},
    {"soru": "Eğitimin amaçları arasında aşağıdakilerden hangisi yoktur?", "secenekler": ["Bireyi topluma kazandırmak", "Kültürel mirası aktarmak", "Kâr elde etmek", "Bilgi ve beceri kazandırmak"], "cevap": "Kâr elde etmek"},
    {"soru": "Eğitimde bireysel farklılıkları dikkate alma yaklaşımı hangisidir?", "secenekler": ["Farklılaştırılmış öğretim", "Tek tip öğretim", "Ezberci eğitim", "Sınav odaklı eğitim"], "cevap": "Farklılaştırılmış öğretim"},
    {"soru": "Eğitimin toplumsal işlevlerinden biri nedir?", "secenekler": ["Toplumsal uyumu sağlamak", "Bireyi izole etmek", "Kârı artırmak", "Sadece sınav kazandırmak"], "cevap": "Toplumsal uyumu sağlamak"},
    {"soru": "Montessori eğitim yaklaşımı hangi yaş grubu için uygundur?", "secenekler": ["Okul öncesi çocuklar", "Lise öğrencileri", "Üniversite öğrencileri", "Yetişkinler"], "cevap": "Okul öncesi çocuklar"},
    {"soru": "Eğitim programı geliştirmede ilk adım nedir?", "secenekler": ["Amaçları belirlemek", "Sınav hazırlamak", "Öğrenci seçmek", "Müfredatı seçmek"], "cevap": "Amaçları belirlemek"},
    {"soru": "Öğretim yöntemlerinden hangisi öğrenci merkezlidir?", "secenekler": ["Problem çözme yöntemi", "Anlatım yöntemi", "Ezber yöntemi", "Soru-cevap yöntemi"], "cevap": "Problem çözme yöntemi"},
    {"soru": "Bireyi topluma kazandıran eğitim anlayışı hangisidir?", "secenekler": ["Sosyal eğitim", "Bireysel eğitim", "Ev eğitimi", "Deneysel eğitim"], "cevap": "Sosyal eğitim"},
    {"soru": "Eğitimde teknoloji kullanımının amacı nedir?", "secenekler": ["Öğrenmeyi kolaylaştırmak", "Sadece eğlence sağlamak", "Sınav yapmak", "Ezberci öğrenmeyi artırmak"], "cevap": "Öğrenmeyi kolaylaştırmak"},
    {"soru": "Hayat boyu öğrenme yaklaşımı hangi eğitim anlayışına uygundur?", "secenekler": ["Bütünsel eğitim", "Sadece okul eğitimi", "Sadece özel ders", "Ezberci eğitim"], "cevap": "Bütünsel eğitim"},
    {"soru": "Eğitimde ölçme ve değerlendirme hangi amaçla yapılır?", "secenekler": ["Öğrenme düzeyini belirlemek", "Sadece cezalandırmak", "Kâr elde etmek", "Sadece not vermek"], "cevap": "Öğrenme düzeyini belirlemek"},
    {"soru": "İçerik, yöntem ve ölçme aracını planlayan süreç hangisidir?", "secenekler": ["Öğretim tasarımı", "Sınav hazırlığı", "Ödev dağıtımı", "Sosyal etkinlik"], "cevap": "Öğretim tasarımı"},
    {"soru": "Eğitimde farklı öğrenme stillerini dikkate almak hangi yaklaşımı gösterir?", "secenekler": ["Bireysel farklılıklar", "Tek tip öğretim", "Ezberci yöntem", "Oyun odaklı eğitim"], "cevap": "Bireysel farklılıklar"},
    {"soru": "Eğitimde sosyal becerilerin kazandırılması hangi alanla ilgilidir?", "secenekler": ["Sosyal ve duygusal gelişim", "Akademik başarı", "Teknik beceriler", "Ezberleme"], "cevap": "Sosyal ve duygusal gelişim"},
    {"soru": "Eğitim psikolojisi hangi konuyu inceler?", "secenekler": ["Öğrenme ve öğretme süreçlerini", "Sadece biyolojik gelişimi", "Sadece kültürü", "Sadece sınavları"], "cevap": "Öğrenme ve öğretme süreçlerini"},
    {"soru": "Okul öncesi eğitim kaç yaş grubunu kapsar?", "secenekler": ["3-6 yaş", "6-12 yaş", "12-18 yaş", "0-2 yaş"], "cevap": "3-6 yaş"},
    {"soru": "Eğitimde hedef davranışların belirlenmesine ne denir?", "secenekler": ["Amaç ve hedef belirleme", "Ödev planlama", "Sınav tasarlama", "Notlandırma"], "cevap": "Amaç ve hedef belirleme"},
    {"soru": "Yapılandırmacı yaklaşımın temel ilkesi nedir?", "secenekler": ["Öğrencinin aktif öğrenmesi", "Ezberci öğrenme", "Sadece öğretmenin anlatması", "Not vermek"], "cevap": "Öğrencinin aktif öğrenmesi"},
    {"soru": "Bilişsel, duyuşsal ve psikomotor alanlar hangi eğitim kuramına aittir?", "secenekler": ["Bloom Taksonomisi", "Montessori", "Piaget", "Vygotsky"], "cevap": "Bloom Taksonomisi"}
]

mevzuat_sorular = [
    {"soru": "Milli Eğitim Bakanlığı hangi yıl kurulmuştur?", "secenekler": ["1920", "1923", "1930", "1921"], "cevap": "1920"},
    {"soru": "Türkiye’de zorunlu eğitim kaç yıldır?", "secenekler": ["12 yıl", "8 yıl", "10 yıl", "5 yıl"], "cevap": "12 yıl"},
    {"soru": "Tevhid-i Tedrisat Kanunu neyi sağlamıştır?", "secenekler": ["Eğitim birliğini", "Sadece okullar açmayı", "Özel okulları kapatmayı", "Üniversiteyi kurmayı"], "cevap": "Eğitim birliğini"},
    {"soru": "Milli Eğitim Temel Kanunu hangi yıl çıkarılmıştır?", "secenekler": ["1973", "1961", "1982", "1924"], "cevap": "1973"},
    {"soru": "Eğitim sisteminde müfredatı belirleme yetkisi kime aittir?", "secenekler": ["MEB", "Okul müdürü", "Öğretmenler", "Valilik"], "cevap": "MEB"},
    {"soru": "Ortaöğretimde seçmeli derslerin belirlenmesi hangi ilkeye dayanır?", "secenekler": ["Öğrenci ilgi ve yeteneklerine", "Rastgele", "Öğretmen kararına", "MEB kararı dışında"], "cevap": "Öğrenci ilgi ve yeteneklerine"},
    {"soru": "Okul öncesi eğitim hangi kanuna göre düzenlenir?", "secenekler": ["Milli Eğitim Temel Kanunu", "Anayasa", "Türk Medeni Kanunu", "İş Kanunu"], "cevap": "Milli Eğitim Temel Kanunu"},
    {"soru": "Milli Eğitim Bakanlığı merkezi yönetim birimi hangi kurumdur?", "secenekler": ["MEB Genel Müdürlükleri", "Valilik", "Belediye", "Özel okul"], "cevap": "MEB Genel Müdürlükleri"},
    {"soru": "Özel okulların denetimi hangi kuruma aittir?", "secenekler": ["MEB", "Valilik", "Belediye", "Özel kurum"], "cevap": "MEB"},
    {"soru": "Temel eğitimdeki kademeler nelerdir?", "secenekler": ["İlkokul ve ortaokul", "Sadece ilkokul", "Ortaokul ve lise", "Sadece lise"], "cevap": "İlkokul ve ortaokul"},
    {"soru": "Lise eğitimi kaç yıl sürer?", "secenekler": ["4 yıl", "3 yıl", "5 yıl", "6 yıl"], "cevap": "4 yıl"},
    {"soru": "MEB’in temel görevi nedir?", "secenekler": ["Eğitimi planlamak ve yürütmek", "Sadece öğretmen atamak", "Sadece sınav yapmak", "Okul açmak"], "cevap": "Eğitimi planlamak ve yürütmek"},
    {"soru": "Eğitimde mevzuatın amacı nedir?", "secenekler": ["Hukuki düzen sağlamak", "Öğrenci seçmek", "Sınav yapmak", "Maaş belirlemek"], "cevap": "Hukuki düzen sağlamak"},
    {"soru": "Anadolu liseleri hangi amaçla kurulmuştur?", "secenekler": ["Üstün yetenekli öğrencileri yetiştirmek", "Herkese açık eğitim", "Meslek eğitimi", "Sadece sınav hazırlığı"], "cevap": "Üstün yetenekli öğrencileri yetiştirmek"},
    {"soru": "İlköğretim okullarında zorunlu derslerden biri hangisidir?", "secenekler": ["Türkçe", "Resim", "Müzik", "Beden"], "cevap": "Türkçe"},
    {"soru": "MEB’in taşra teşkilatı hangi birimlerden oluşur?", "secenekler": ["İl ve ilçe milli eğitim müdürlükleri", "Sadece il müdürlükleri", "Sadece ilçe müdürlükleri", "Okul müdürlükleri"], "cevap": "İl ve ilçe milli eğitim müdürlükleri"},
    {"soru": "Özel eğitim kurumları hangi kanuna tabidir?", "secenekler": ["MEB kanunları", "Türk Ceza Kanunu", "Medeni Kanun", "İş Kanunu"], "cevap": "MEB kanunları"},
    {"soru": "Mesleki eğitimde uygulama derslerinin amacı nedir?", "secenekler": ["Beceri kazandırmak", "Sadece teori anlatmak", "Sınav yapmak", "Okulu denetlemek"], "cevap": "Beceri kazandırmak"},
    {"soru": "MEB’in eğitimle ilgili stratejik planlarını kim hazırlar?", "secenekler": ["MEB merkez teşkilatı", "Okul müdürleri", "Öğretmenler", "Valilik"], "cevap": "MEB merkez teşkilatı"},
    {"soru": "Eğitimde kaliteyi denetlemek için hangi mekanizma kullanılır?", "secenekler": ["Teftiş ve denetim birimleri", "Sadece sınav", "Öğretmen raporu", "Veliler"], "cevap": "Teftiş ve denetim birimleri"}
]

anayasa_sorular = [
    {"soru": "Türkiye Cumhuriyeti’nin yönetim şekli nedir?", "secenekler": ["Cumhuriyet", "Monarşi", "Oligarşi", "Diktatörlük"], "cevap": "Cumhuriyet"},
    {"soru": "Anayasa değişikliği kaç milletvekili oyuyla yapılır?", "secenekler": ["3/5 çoğunluk", "1/2 çoğunluk", "2/3 çoğunluk", "4/5 çoğunluk"], "cevap": "3/5 çoğunluk"},
    {"soru": "Türkiye’de yasama yetkisi kime aittir?", "secenekler": ["TBMM", "Cumhurbaşkanı", "Yargıtay", "Danıştay"], "cevap": "TBMM"},
    {"soru": "Anayasa hangi yıl kabul edilmiştir?", "secenekler": ["1982", "1961", "1921", "1971"], "cevap": "1982"},
    {"soru": "Türkiye Cumhuriyeti temel nitelikleri arasında hangisi vardır?", "secenekler": ["Demokratik", "Feodal", "Monarşik", "Totaliter"], "cevap": "Demokratik"},
    {"soru": "Temel hak ve hürriyetlerin korunmasından kim sorumludur?", "secenekler": ["Devlet", "Vatandaş", "Belediye", "Polis"], "cevap": "Devlet"},
    {"soru": "Cumhurbaşkanı seçimi kaç yılda bir yapılır?", "secenekler": ["5 yıl", "4 yıl", "6 yıl", "3 yıl"], "cevap": "5 yıl"},
    {"soru": "Türkiye’de yürütme yetkisi kime aittir?", "secenekler": ["Cumhurbaşkanı ve Bakanlar Kurulu", "TBMM", "Anayasa Mahkemesi", "Yargıtay"], "cevap": "Cumhurbaşkanı ve Bakanlar Kurulu"},
    {"soru": "Yargı bağımsızlığı hangi ilke ile sağlanır?", "secenekler": ["Bağımsız mahkemeler", "TBMM kontrolü", "Cumhurbaşkanı denetimi", "Bakanlar Kurulu denetimi"], "cevap": "Bağımsız mahkemeler"},
    {"soru": "Temel hak ve özgürlükler hangi hukuk sistemi ile güvence altına alınır?", "secenekler": ["Anayasa", "Medeni Kanun", "Ceza Kanunu", "Ticaret Kanunu"], "cevap": "Anayasa"},
    {"soru": "Türkiye’de hukuk devleti ilkesini hangi belge garanti eder?", "secenekler": ["Anayasa", "MEB Kanunu", "Türk Ceza Kanunu", "İş Kanunu"], "cevap": "Anayasa"},
    {"soru": "Anayasa değişikliği kanunu TBMM’de kabul edilirse ne yapılır?", "secenekler": ["Cumhurbaşkanı onayı ve halkoyuna sunulabilir", "Sadece yürürlüğe girer", "Sadece Cumhurbaşkanı yürütür", "Mahkemeye gönderilir"], "cevap": "Cumhurbaşkanı onayı ve halkoyuna sunulabilir"},
    {"soru": "Temel hakların sınırlanması hangi koşulla mümkündür?", "secenekler": ["Kanun ile ve ölçülü şekilde", "İstediği zaman", "Sadece mahkeme kararıyla", "Bakanlar Kurulu kararıyla"], "cevap": "Kanun ile ve ölçülü şekilde"},
    {"soru": "Anayasa Mahkemesi’nin görevi nedir?", "secenekler": ["Kanunların anayasaya uygunluğunu denetlemek", "Sadece yargı yapmak", "Sınav düzenlemek", "Okul açmak"], "cevap": "Kanunların anayasaya uygunluğunu denetlemek"},
    {"soru": "Cumhuriyetin temel ilkelerinden biri değildir?", "secenekler": ["Monarşi", "Laiklik", "Demokrasi", "Hukuk devleti"], "cevap": "Monarşi"},
    {"soru": "Seçme ve seçilme hakkı hangi anayasal hak kapsamında yer alır?", "secenekler": ["Siyasi haklar", "Kültürel haklar", "Ekonomik haklar", "Sosyal haklar"], "cevap": "Siyasi haklar"},
    {"soru": "Anayasa değişikliği teklifi hangi oranda kabul edilmelidir?", "secenekler": ["3/5 çoğunluk", "1/2 çoğunluk", "2/3 çoğunluk", "4/5 çoğunluk"], "cevap": "3/5 çoğunluk"},
    {"soru": "Türkiye Cumhuriyeti’nde kuvvetler ayrılığı ilkesini kim sağlar?", "secenekler": ["Yasama, yürütme ve yargı organları", "Sadece yürütme", "Sadece yasama", "Sadece yargı"], "cevap": "Yasama, yürütme ve yargı organları"},
    {"soru": "Anayasa’da belirtilen sosyal haklardan biri hangisidir?", "secenekler": ["Eğitim hakkı", "Trafik hakkı", "İşletme hakkı", "Spor hakkı"], "cevap": "Eğitim hakkı"},
    {"soru": "Cumhurbaşkanının görev süresi nedir?", "secenekler": ["5 yıl", "4 yıl", "6 yıl", "3 yıl"], "cevap": "5 yıl"}
]

DATA_FILE = "pomodoro_data.json"

# İlk veri dosyası yoksa oluştur
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"days": {}, "points": 0, "level": 1, "carry_minutes": 0}, f, indent=4, ensure_ascii=False)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # geriye dönük uyumluluk
    if "carry_minutes" not in data:
        data["carry_minutes"] = 0
    if "points" not in data:
        data["points"] = 0
    if "level" not in data:
        data["level"] = 1
    if "days" not in data:
        data["days"] = {}
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _today_str(offset_days=0):
    return (datetime.datetime.now() - datetime.timedelta(days=offset_days)).strftime("%Y-%m-%d")


def add_pomodoro(seconds=None, hours=None):
    """Çalışma ekle. seconds tercih edilir; yoksa hours kullanılır.
       Günlük saatler float saat olarak tutulur.
       Puan: her TAM 120 dakika için +10; artan dakika carry'de birikir.
    """
    assert seconds is not None or hours is not None, "add_pomodoro: seconds veya hours vermelisin"
    if seconds is None:
        seconds = int(hours * 3600)

    minutes = seconds // 60  # puan için tam dakikalar
    hours_inc = seconds / 3600.0  # günlük toplam için

    data = load_data()
    today = _today_str()

    # günlük toplam (saat)
    data["days"][today] = float(data["days"].get(today, 0.0)) + hours_inc

    # puan biriktirme (2 saat = 120 dk → +10 puan)
    total_minutes = int(data.get("carry_minutes", 0)) + int(minutes)
    gained_blocks = total_minutes // 120
    if gained_blocks > 0:
        data["points"] += gained_blocks * 10
    data["carry_minutes"] = total_minutes % 120

    # seviye kontrolü
    check_levels(data)

    save_data(data)

def get_total_last_days(data, days_count):
    total = 0.0
    for i in range(days_count):
        day_str = _today_str(i)
        total += float(data["days"].get(day_str, 0.0))
    return total

def _consecutive_days_at_least(data, threshold_hours, needed_days):
    """Bugünden geriye doğru, ardışık >=threshold_hours çalışılan gün sayısını verir (maks. needed_days)."""
    streak = 0
    for i in range(0, needed_days):
        h = float(data["days"].get(_today_str(i), 0.0))
        if h >= threshold_hours:
            streak += 1
        else:
            break
    return min(streak, needed_days)

def check_levels(data):
    # LEVEL 1 → 2 : 2 gün üst üste >= 5 saat
    if data["level"] == 1:
        if _consecutive_days_at_least(data, 5, 2) >= 2:
            data["level"] = 2
            try:
                messagebox.showinfo("Terfi", "Tebrikler! Fenerbahçe Altyapısına terfi ettin! Seni seviyorum.")
            except:
                print("Tebrikler! Fenerbahçe Altyapısına terfi ettin! Seni seviyorum.")

    # LEVEL 2 → 3 : son 7 gün toplamı >= 55 saat
    if data["level"] == 2:
        last_7 = get_total_last_days(data, 7)
        if last_7 >= 55:
            data["level"] = 3
            try:
                messagebox.showinfo("Terfi", "Tebrikler! Fenerbahçe A Takımı'na Yükseldin! Seni seviyorum.")
            except:
                print("Tebrikler! Fenerbahçe A Takımı'na Yükseldin! Seni seviyorum.")
        elif last_7 < 30:
            data["level"] = 1
            try:
                messagebox.showwarning("Düşüş", "Maalesef bu hafta yeterli çalışmadın. Sökespor'a geri gönderildin. Şimdi daha sıkı çalışma zamanı!")
            except:
                print("Maalesef bu hafta yeterli çalışmadın. Sökespor'a geri gönderildin. Şimdi daha sıkı çalışma zamanı!")

    # LEVEL 3 → 2 : dün hiç çalışma yoksa
    if data["level"] == 3:
        yesterday = _today_str(1)
        if float(data["days"].get(yesterday, 0.0)) == 0.0:
            data["level"] = 2
            try:
                messagebox.showwarning("Düşüş", "Dün ders çalışmadığın için altyapıya geri gönderildin. Telafi etmeye bak!")
            except:
                print("Dün ders çalışmadığın için altyapıya geri gönderildin. Telafi etmeye bak!")

def get_title(points):
    if points < 30:
        return "Amatör"
    elif points < 100:
        return "Yıldız Adayı"
    elif points < 200:
        return "Vazgeçilmez"
    else:
        return "Efsanevi"



# ---------------------- GİRİŞ EKRANI ----------------------
root = tk.Tk()
root.title("Giriş Ekranı")
root.geometry("720x400")
root.configure(bg="#ADD8E6")

label_username = tk.Label(root, text="Kullanıcı Adı:", bg="#ADD8E6", font=("Helvetica", 12, "bold"))
label_username.grid(row=0, column=0, padx=10, pady=10)

label_password = tk.Label(root, text="Şifre:", bg="#ADD8E6", font=("Helvetica", 12, "bold"))
label_password.grid(row=1, column=0, padx=10, pady=10)

entry_username = tk.Entry(root, font=("Helvetica", 12))
entry_username.grid(row=0, column=1, padx=10, pady=10)

entry_password = tk.Entry(root, font=("Helvetica", 12), show="*")
entry_password.grid(row=1, column=1, padx=10, pady=10)

def kalan_gun():
    sinav_tarihi = datetime.date(2026, 7, 15)
    bugun = datetime.date.today()
    return (sinav_tarihi - bugun).days

# ---------------------- ALT KATEGORİ PENCERELERİ ----------------------
def alt_kategori_pencere(isim, mesajlar):
    yeni_pencere = tk.Toplevel()
    yeni_pencere.title(isim)
    yeni_pencere.geometry("500x400")
    yeni_pencere.configure(bg="#FFF0F5")

    lbl = tk.Label(yeni_pencere, text=random.choice(mesajlar), font=("Helvetica", 14, "bold"),
                   bg="#FFF0F5", fg="#800000", wraplength=400, justify="center")
    lbl.pack(pady=50)

    def geri_don():
        yeni_pencere.destroy()
        kendini_kotu_hisset()
    btn = tk.Button(yeni_pencere, text="Geri Dön", font=("Helvetica", 12, "bold"),
                    bg="#00BFFF", fg="white", command=geri_don)
    btn.pack(pady=20)
    
# ---------------------- Beni Özlediğinde (Fotoğraf Galerisi) ----------------------
def beni_ozlediginde():
    mesajlar = ["Ben hep yanındayım, merak etme.", "Sevgi uzaklık tanımaz, unutma."]
    pencerem = tk.Toplevel()
    pencerem.title("Beni Özlediğinde")
    pencerem.geometry("600x500")
    pencerem.configure(bg="#FFF0F5")

    lbl_mesaj = tk.Label(pencerem, text=random.choice(mesajlar), font=("Helvetica", 14, "bold"),
                         bg="#FFF0F5", fg="#800000", wraplength=500, justify="center")
    lbl_mesaj.pack(pady=10)

    foto_list = [f"fotograf{i}.jpg" for i in range(1,7)]
    foto_index = [0]

    img = Image.open(foto_list[foto_index[0]])
    img = img.resize((400, 300))
    photo = ImageTk.PhotoImage(img)

    lbl_foto = tk.Label(pencerem, image=photo, bg="#FFF0F5")
    lbl_foto.image = photo
    lbl_foto.pack(pady=10)

    def saga():
        foto_index[0] = (foto_index[0] + 1) % len(foto_list)
        yeni_img = Image.open(foto_list[foto_index[0]]).resize((400,300))
        photo_new = ImageTk.PhotoImage(yeni_img)
        lbl_foto.configure(image=photo_new)
        lbl_foto.image = photo_new

    def sola():
        foto_index[0] = (foto_index[0] - 1) % len(foto_list)
        yeni_img = Image.open(foto_list[foto_index[0]]).resize((400,300))
        photo_new = ImageTk.PhotoImage(yeni_img)
        lbl_foto.configure(image=photo_new)
        lbl_foto.image = photo_new

    btn_sola = tk.Button(pencerem, text="←", font=("Helvetica", 14, "bold"), command=sola, width=5)
    btn_sola.pack(side="left", padx=20, pady=10)

    btn_saga = tk.Button(pencerem, text="→", font=("Helvetica", 14, "bold"), command=saga, width=5)
    btn_saga.pack(side="right", padx=20, pady=10)

    def geri_don():
        pencerem.destroy()
        kendini_kotu_hisset()
    btn_geri = tk.Button(pencerem, text="Geri Dön", font=("Helvetica", 12, "bold"),
                         bg="#00BFFF", fg="white", command=geri_don)
    btn_geri.pack(pady=10, side="bottom")

# ---------------------- KENDİNİ KÖTÜ HİSSETTİĞİNDE ----------------------
def kendini_kotu_hisset():
    app.destroy()
    alt_pencere = tk.Tk()
    alt_pencere.title("Kendini Kötü Hissettiğinde")
    alt_pencere.geometry("600x400")
    alt_pencere.configure(bg="#FFE4E1")

    baslik = tk.Label(alt_pencere, text="Kendini Kötü Hissettiğinde...",
                      font=("Helvetica", 18, "bold"), bg="#FFE4E1", fg="#800000")
    baslik.pack(pady=20)

    kategoriler = {
        "Grip Olduğunda": ["Ateş ve ağrın varsa Parasetamol içebilirsin. Ayrıca Theraflu iç, kalınca giyin ve bir battaniyenin altında terle. Böylece ateşin düşecek."],
        "Yalnız Hissettiğinde": ["Bazen, çevremizde ne kadar çok insan olsa da kendimizi yalnız hissederiz. Sana yalnız değilsin, ben varım, o var şu var klişesi yapmayacağım ki sen bunu çok iyi biliyorsun. Ama şunu da unutma, ben senin ne kadar uzağında da olsam bir o kadar da yakınım sana. Sen yalnız hissediyorsan ben de seninle yalnız hissederim. Yalnız olalım, ama beraber de olalım."],
        "Yetersiz Hissettiğinde": ["Bugün uyandığın, kalkıp elini yüzünü yıkadığın için seninle gurur duyuyorum Arda. Motivasyonun düşebilir, netlerin kötü gelebilir ama hiçbir zaman yetersiz olamayacaksın çünkü sen bana fazlasıyla yetersin."],
        "Beni Özlediğinde": []
    }

    y_pos = 100
    for kat, mesajlar in kategoriler.items():
        if kat == "Beni Özlediğinde":
            cmd = beni_ozlediginde
        else:
            cmd = lambda m=mesajlar, k=kat: alt_kategori_pencere(k, m)

        btn = tk.Button(alt_pencere, text=kat, font=("Helvetica", 14), bg="#FFB6C1",
                        fg="#800000", width=25, command=cmd)
        btn.place(x=150, y=y_pos)
        y_pos += 50

    def geri_don():
        alt_pencere.destroy()
        ana_pencere()

    geri_btn = tk.Button(alt_pencere, text="Geri Dön", font=("Helvetica", 12, "bold"),
                         bg="#00BFFF", fg="white", command=geri_don)
    geri_btn.pack(pady=20, side="bottom")
    alt_pencere.mainloop()
    
# ---------------------- ÖRNEK SORULAR PENCERESİ ----------------------
def test_penceresi(konu, sorular):
    pencerem = tk.Toplevel()
    pencerem.title(f"{konu} - Test")
    pencerem.geometry("600x500")
    pencerem.configure(bg="#FFF0F5")

    baslik = tk.Label(pencerem, text=konu, font=("Helvetica", 18, "bold"),
                      bg="#FFF0F5", fg="#800000")
    baslik.pack(pady=10)

    soru_index = [0]
    secilen = tk.StringVar()
    sonuc_label = tk.Label(pencerem, text="", font=("Helvetica", 12),
                           bg="#FFF0F5", fg="green")
    sonuc_label.pack(pady=5)

    soru_label = tk.Label(pencerem, text="", font=("Helvetica", 14),
                          bg="#FFF0F5", fg="#800000", wraplength=550, justify="left")
    soru_label.pack(pady=10)

    secenekler_frame = tk.Frame(pencerem, bg="#FFF0F5")
    secenekler_frame.pack()

    def guncelle_soru():
        secilen.set(None)
        s = sorular[soru_index[0]]
        soru_label.config(text=s["soru"])
        for widget in secenekler_frame.winfo_children():
            widget.destroy()
        for sec in s["secenekler"]:
            rb = tk.Radiobutton(secenekler_frame, text=sec, variable=secilen, value=sec,
                                font=("Helvetica", 12), bg="#FFF0F5", anchor="w", justify="left")
            rb.pack(anchor="w")
        ilerleme_label.config(text=f"{soru_index[0]+1}/{len(sorular)}")
        sonuc_label.config(text="")

    def kontrol():
        s = sorular[soru_index[0]]
        if secilen.get() == s["dogru"]:
            sonuc_label.config(text="Doğru!", fg="green")
        else:
            sonuc_label.config(text=f"Yanlış! Doğru cevap: {s['dogru']}", fg="red")

    def ileri():
        if soru_index[0] < len(sorular)-1:
            soru_index[0] += 1
            guncelle_soru()

    def geri():
        if soru_index[0] > 0:
            soru_index[0] -= 1
            guncelle_soru()

    ilerleme_label = tk.Label(pencerem, text="", font=("Helvetica",12),
                              bg="#FFF0F5", fg="#800000")
    ilerleme_label.pack(pady=5)

    btn_frame = tk.Frame(pencerem, bg="#FFF0F5")
    btn_frame.pack(pady=10)

    btn_geri_soru = tk.Button(btn_frame, text="← Geri", command=geri, font=("Helvetica",12))
    btn_geri_soru.pack(side="left", padx=20)
    btn_ileri_soru = tk.Button(btn_frame, text="İleri →", command=ileri, font=("Helvetica",12))
    btn_ileri_soru.pack(side="right", padx=20)

    btn_kontrol = tk.Button(pencerem, text="Cevabı Kontrol Et", command=kontrol, font=("Helvetica",12))
    btn_kontrol.pack(pady=10)

    def geri_don():
        pencerem.destroy()
        ders_konulari()
    btn_geri = tk.Button(pencerem, text="Ders Konularına Dön", font=("Helvetica",12,"bold"),
                         bg="#00BFFF", fg="white", command=geri_don)
    btn_geri.pack(pady=10, side="bottom")

    guncelle_soru()
    
# ---------------------- DERS KONULARI + SORULAR ----------------------
def ders_konulari():
    pencerem = tk.Toplevel()
    pencerem.title("Ders Konuları")
    pencerem.geometry("600x500")
    pencerem.configure(bg="#FFF0F5")

    baslik = tk.Label(pencerem, text="Ders Konuları", font=("Helvetica", 18, "bold"),
                      bg="#FFF0F5", fg="#800000")
    baslik.pack(pady=10)

    canvas = tk.Canvas(pencerem, bg="#FFF0F5")
    frame = tk.Frame(canvas, bg="#FFF0F5")
    vsb = tk.Scrollbar(pencerem, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0,0), window=frame, anchor="nw")

    def onFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", onFrameConfigure)

    # AGS sorularını ekle (örnek: Tarih için 20, Coğrafya için 20 vs.)
    ags_sorular = {
    "Tarih": tarih_sorular,
    "Türkiye Coğrafyası": turkiye_sorular,
    "Eğitimin Temelleri": egitimin_temelleri_sorular,
    "Türk Milli Eğitim Sistemi ve Mevzuatı": mevzuat_sorular,
    "Anayasa": anayasa_sorular
    }

    lbl_ags = tk.Label(frame, text="AGS Konuları", font=("Helvetica", 16, "bold"),
                       bg="#FFE4E1", fg="#800000")
    lbl_ags.pack(pady=5, fill="x")

    for konu, sorular in ags_sorular.items():
        lbl = tk.Label(frame, text=konu, font=("Helvetica", 14, "bold"),
                       bg="#FFF0F5", fg="#800000")
        lbl.pack(anchor="w", padx=20, pady=2)
        btn = tk.Button(frame, text="Örnek Sorular", font=("Helvetica", 12),
                        bg="#FFB6C1", fg="#800000", command=lambda k=konu, s=sorular: [pencerem.destroy(), test_penceresi(k, s)])
        btn.pack(anchor="w", padx=40, pady=2)

    # ÖABT Türkçe

    lbl_oabt = tk.Label(frame, text="ÖABT Konuları", font=("Helvetica", 16, "bold"),
                        bg="#FFE4E1", fg="#800000")
    lbl_oabt.pack(pady=5, fill="x")

    lbl = tk.Label(frame, text="Türkçe", font=("Helvetica", 14, "bold"),
                   bg="#FFF0F5", fg="#800000")
    lbl.pack(anchor="w", padx=20, pady=2)
    btn = tk.Button(frame, text="Örnek Sorular", font=("Helvetica", 12),
                    bg="#FFB6C1", fg="#800000", command=lambda: [pencerem.destroy(), test_penceresi("ÖABT Türkçe", oabt_sorular)])
    btn.pack(anchor="w", padx=40, pady=2)

    def geri_don():
        pencerem.destroy()
    btn_geri = tk.Button(pencerem, text="Geri Dön", font=("Helvetica", 12, "bold"),
                         bg="#00BFFF", fg="white", command=geri_don)
    btn_geri.pack(pady=10, side="bottom")
    
def pomodoro():
    pencerem = tk.Toplevel()
    pencerem.title("Pomodoro Kronometresi")
    pencerem.geometry("500x380")
    pencerem.configure(bg="#FFF0F5")

    # Sayaç (0'dan yukarı)
    elapsed_seconds = [0]
    running = [False]

    # UI
    label = tk.Label(pencerem, text="00:00:00", font=("Helvetica", 48), bg="#FFF0F5", fg="#800000")
    label.pack(pady=10)

    toplam_label = tk.Label(pencerem, text="", font=("Helvetica", 12), bg="#FFF0F5", fg="#800000")
    toplam_label.pack(pady=5)

    # Bugün toplam çalışma (JSON'dan)
    def refresh_today_total():
        data = load_data()
        today_hours = float(data["days"].get(_today_str(), 0.0))
        total_seconds = int(today_hours * 3600)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        toplam_label.config(text=f"Bugün toplam çalışma: {h} saat {m} dk {s} sn")

    refresh_today_total()

    def tick():
        if running[0]:
            elapsed_seconds[0] += 1
            es = elapsed_seconds[0]
            h = es // 3600
            m = (es % 3600) // 60
            s = es % 60
            label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            pencerem.after(1000, tick)

    def baslat():
        if not running[0]:
            running[0] = True
            tick()

    def durdur():
        running[0] = False

    def sifirla():
        running[0] = False
        elapsed_seconds[0] = 0
        label.config(text="00:00:00")

    def bitir():
        # Süreyi kaydet, puan/level güncelle
        nonlocal elapsed_seconds
        if elapsed_seconds[0] > 0:
            add_pomodoro(seconds=elapsed_seconds[0])
            try:
                h = elapsed_seconds[0] // 3600
                m = (elapsed_seconds[0] % 3600) // 60
                s = elapsed_seconds[0] % 60
                messagebox.showinfo("Kaydedildi", f"Çalışma süresi kaydedildi: {h} saat {m} dk {s} sn")
            except:
                pass
        sifirla()
        refresh_today_total()

    # Butonlar
    btn_frame = tk.Frame(pencerem, bg="#FFF0F5")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Başlat", command=baslat, bg="#FFB6C1", fg="#800000", width=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Durdur", command=durdur, bg="#FFB6C1", fg="#800000", width=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Sıfırla", command=sifirla, bg="#FFB6C1", fg="#800000", width=10).pack(side="left", padx=5)
    tk.Button(pencerem, text="Bitir ve Kaydet", command=bitir, bg="#00BFFF", fg="white", width=20).pack(pady=10)

def mini_oyun_ac():
    data = load_data()
    # Açılışta seviye/mesajlar güncellensin:
    check_levels(data); save_data(data)
    data = load_data()

    oyun = tk.Toplevel()
    oyun.title("Mini Oyun - Futbolcu Kariyeri")
    oyun.geometry("800x500")
    oyun.configure(bg="#e8ffe8")

    # Sağ panel: görevler ve durum
    right = tk.Frame(oyun, bg="#e8ffe8")
    right.pack(side="right", fill="y", padx=10, pady=10)

    # Canvas: karakter
    canvas = tk.Canvas(oyun, width=600, height=500, bg="green")
    canvas.pack(side="left", fill="both", expand=True)

    level = int(data["level"])
    points = int(data["points"])
    title = get_title(points)

    # Ünvan etiketi (karakter üstünde)
    title_var = tk.StringVar(value=title)
    title_label = tk.Label(canvas, textvariable=title_var, font=("Helvetica", 14, "bold"), bg="yellow", fg="black")
    title_label_window = canvas.create_window(300, 40, window=title_label)

    # Sprite yükleme (level{n}_{direction}.png)
    sprite_cache = {}
    def load_sprite(lvl, direction):
        key = (lvl, direction)
        if key in sprite_cache:
            return sprite_cache[key]
        path = f"sprites/level{lvl}_{direction}.png"  # front/back/left/right
        try:
            img = Image.open(path).resize((64, 64))
            pic = ImageTk.PhotoImage(img)
        except Exception:
            # placeholder: sarı daire
            img = Image.new("RGBA", (64,64), (255,255,0,255))
            pic = ImageTk.PhotoImage(img)
        sprite_cache[key] = pic
        return pic

    direction = "front"
    sprite_img = load_sprite(level, direction)
    sprite_id = canvas.create_image(300, 250, image=sprite_img)

    # Konum/boundary
    pos = {"x": 300, "y": 250}
    speed = 10
    W, H = 600, 500

    def redraw():
        canvas.itemconfig(sprite_id, image=load_sprite(level, direction))
        canvas.coords(sprite_id, pos["x"], pos["y"])
        canvas.coords(title_label_window, pos["x"], pos["y"]-60)

    def key_press(event):
        nonlocal direction
        k = event.keysym.lower()
        if k == "w":
            pos["y"] = max(32, pos["y"] - speed); direction = "back"
        elif k == "s":
            pos["y"] = min(H-32, pos["y"] + speed); direction = "front"
        elif k == "a":
            pos["x"] = max(32, pos["x"] - speed); direction = "left"
        elif k == "d":
            pos["x"] = min(W-32, pos["x"] + speed); direction = "right"
        redraw()

    oyun.bind("<KeyPress>", key_press)

    # ---- Görev çubukları ----
    tk.Label(right, text="Görevler", font=("Helvetica", 16, "bold"), bg="#e8ffe8", fg="#004400").pack(anchor="w", pady=(0,8))

    # Görev 1: 2 gün üst üste 5+ saat
    streak = _consecutive_days_at_least(data, 5, 2)  # 0..2
    g1_percent = int((streak / 2) * 100)
    tk.Label(right, text="Görev 1: 2 gün üst üste 5+ saat", bg="#e8ffe8", font=("Helvetica", 11, "bold")).pack(anchor="w")
    g1 = ttk.Progressbar(right, orient="horizontal", length=160, mode="determinate", maximum=100)
    g1.pack(pady=(2,8), anchor="w")
    g1["value"] = g1_percent

    # Görev 2: Son 7 gün toplam 55+ saat
    last_7 = get_total_last_days(data, 7)  # saat
    g2_percent = int(min(100, (last_7 / 55.0) * 100))
    tk.Label(right, text="Görev 2: 1 hafta toplam 55+ saat", bg="#e8ffe8", font=("Helvetica", 11, "bold")).pack(anchor="w")
    g2 = ttk.Progressbar(right, orient="horizontal", length=160, mode="determinate", maximum=100)
    g2.pack(pady=(2,8), anchor="w")
    g2["value"] = g2_percent

    # Durum satırları
    tk.Label(right, text=f"Seviye: {level}", bg="#e8ffe8", font=("Helvetica", 12)).pack(anchor="w", pady=(8,0))
    status_points = tk.Label(right, text=f"Puan: {points}  ({title})", bg="#e8ffe8", font=("Helvetica", 12, "bold"))
    status_points.pack(anchor="w")

    # Canlı güncel tutmak için küçük bir yenile butonu
    def refresh_panel():
        d = load_data()
        nonlocal level, points, title, direction
        # level değiştiyse sprite da değişsin
        if d["level"] != level:
            level = d["level"]
            redraw()
        points = d["points"]
        title = get_title(points)
        title_var.set(title)
        status_points.config(text=f"Puan: {points}  ({title})")
        # görevler
        s = _consecutive_days_at_least(d, 5, 2)
        g1["value"] = int((s/2)*100)
        l7 = get_total_last_days(d, 7)
        g2["value"] = int(min(100, (l7/55.0)*100))

    ttk.Button(right, text="Yenile", command=refresh_panel).pack(anchor="w", pady=6)
    
def not_defteri():
    pencerem = tk.Toplevel()
    pencerem.title("Not Defteri")
    pencerem.geometry("600x500")
    pencerem.configure(bg="#FFF0F5")

    baslik = tk.Label(pencerem, text="Not Defteri", font=("Helvetica", 18, "bold"),
                      bg="#FFF0F5", fg="#800000")
    baslik.pack(pady=10)

    # Metin alanı
    text_area = tk.Text(pencerem, wrap="word", font=("Helvetica", 12), bg="#FFF8DC", fg="#000000")
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    # Butonlar çerçevesi
    btn_frame = tk.Frame(pencerem, bg="#FFF0F5")
    btn_frame.pack(pady=10)

    def kaydet():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Dosyası", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text_area.get(1.0, "end-1c"))
                messagebox.showinfo("Başarılı", "Not kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydedilemedi: {str(e)}")

    def temizle():
        if messagebox.askyesno("Onay", "Tüm notlar silinsin mi?"):
            text_area.delete(1.0, "end")

    btn_kaydet = tk.Button(btn_frame, text="Kaydet", command=kaydet, bg="#FFB6C1", fg="#800000", width=10)
    btn_kaydet.pack(side="left", padx=5)

    btn_temizle = tk.Button(btn_frame, text="Temizle", command=temizle, bg="#FFB6C1", fg="#800000", width=10)
    btn_temizle.pack(side="left", padx=5)

    def geri_don():
        pencerem.destroy()

    btn_geri = tk.Button(pencerem, text="Ana Menüye Dön", font=("Helvetica",12,"bold"),
                         bg="#00BFFF", fg="white", command=geri_don)
    btn_geri.pack(pady=10, side="bottom")

# ---------------------- ANA PENCERE ----------------------
def ana_pencere():
    global app
    app = tk.Tk()
    app.title("AGS Hazırlık Uygulaması")
    app.geometry("800x500")

    canvas = tk.Canvas(app, width=800, height=500)
    canvas.pack(fill="both", expand=True)

    try:
        bg_img = Image.open("arka_plan.jpg").resize((800, 500))
        bg_photo = ImageTk.PhotoImage(bg_img)
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except:
        canvas.configure(bg="#FFF0F5")

    canvas.create_rectangle(100, 30, 700, 120, fill="#FFE4E1", stipple="gray25", outline="")
    canvas.create_text(400, 75, text="Hoşgeldin Arda",
                       font=("Helvetica", 24, "bold"), fill="#800000")
    canvas.create_rectangle(250, 150, 550, 200, fill="#FFF0F5",
                            stipple="gray25", outline="")
    canvas.create_text(400, 175, text=f"Sınava Kalan Gün: {kalan_gun()}",
                       font=("Helvetica", 16, "bold"), fill="#C71585")

    etiketler = ["Kendini Kötü Hissettiğinde", "Ders Konuları", "Pomodoro", "Mini Oyun", "Not Kısmı"]
    y_pos = 250
    for etiket in etiketler:
        btn = tk.Button(app, text=etiket, font=("Helvetica", 14),
                        bg="#FFB6C1", fg="#800000", cursor="hand2", width=25)
        btn.place(x=275, y=y_pos)
        y_pos += 50

        if etiket == "Kendini Kötü Hissettiğinde":
            btn.config(command=kendini_kotu_hisset)
        if etiket == "Ders Konuları":
            btn.config(command=ders_konulari)
        if etiket == "Pomodoro":
            btn.config(command=pomodoro)
        if etiket == "Mini Oyun":
            btn.config(command=mini_oyun_ac)
        if etiket == "Not Kısmı":
            btn.config(command=not_defteri)
    app.mainloop()

# ---------------------- GİRİŞ KONTROL ----------------------
def login():
    username = entry_username.get()
    password = entry_password.get()
    if username == KAYITLI_KULLANICI and password == KAYITLI_SIFRE:
        messagebox.showinfo("Başarılı", "Giriş başarılı! Hoş geldiniz.")
        root.destroy()
        ana_pencere()
    else:
        messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

button_login = tk.Button(root, text="Giriş Yap", font=("Helvetica", 12, "bold"),
                         bg="#00BFFF", fg="white", width=15, command=login)
button_login.grid(row=2, column=0, columnspan=2, pady=20)

def on_enter(e):
    e.widget['background'] = '#87CEFA'
def on_leave(e):
    e.widget['background'] = '#00BFFF'
button_login.bind("<Enter>", on_enter)
button_login.bind("<Leave>", on_leave)

root.mainloop()





