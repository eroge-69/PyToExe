import random
import time
import os
import json

class KelimeOgrenmeProgrami:
    def __init__(self):
        # Varsayılan kelimeler
        self.varsayilan_kelimeler = {
            "revision": "genel tekrar",
            "lesson": "ders", 
            "favorite": "en sevdiğim",
            "get up": "uyanmak",
            "news paper": "gazete",
            "question": "soru",
            "club": "okul kulübü",
            "participate": "katılmak",
            "talent": "yetenek",
            "learning": "öğrenmek"
        }

        # Kelime dosyasını yükle veya oluştur
        self.kelime_dosyasi = "kelimelerim.json"
        self.kelimeler = self.kelimeleri_yukle()

        self.dogru_sayisi = 0
        self.yanlis_sayisi = 0
        self.ogrenilenler = set()

    def kelimeleri_yukle(self):
        """Kelime dosyasından kelimeleri yükle"""
        try:
            if os.path.exists(self.kelime_dosyasi):
                with open(self.kelime_dosyasi, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # İlk çalıştırmada varsayılan kelimeleri kaydet
                self.kelimeleri_kaydet(self.varsayilan_kelimeler)
                return self.varsayilan_kelimeler.copy()
        except:
            return self.varsayilan_kelimeler.copy()

    def kelimeleri_kaydet(self, kelimeler=None):
        """Kelimeleri dosyaya kaydet"""
        try:
            kayit_kelimeler = kelimeler if kelimeler else self.kelimeler
            with open(self.kelime_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(kayit_kelimeler, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def ekrani_temizle(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def menu_goster(self):
        self.ekrani_temizle()
        print("\n" + "="*55)
        print("🎓 İNGİLİZCE KELİME ÖĞRENME PROGRAMI 🎓")
        print("="*55)
        print("1. Tüm kelimeleri görüntüle")
        print("2. Kelime testi (İngilizce → Türkçe)")
        print("3. Ters test (Türkçe → İngilizce)")
        print("4. Çoktan seçmeli test")
        print("5. Rastgele kelime öğren")
        print("6. 🆕 YENİ KELİME EKLE")
        print("7. 🗑️ KELİME SİL")
        print("8. 📊 İstatistikleri görüntüle")
        print("9. Çıkış")
        print("-"*55)
        print(f"📚 Toplam kelime sayısı: {len(self.kelimeler)}")
        print("-"*55)

    def yeni_kelime_ekle(self):
        """Yeni kelime ekleme menüsü"""
        self.ekrani_temizle()
        print("\n🆕 YENİ KELİME EKLEME")
        print("="*30)
        print("Yeni İngilizce kelimeler ekleyebilirsiniz!")
        print("(Ana menüye dönmek için 'q' yazın)")
        print("-"*30)

        while True:
            print("\n📝 Yeni kelime ekleyin:")

            # İngilizce kelime al
            ing_kelime = input("İngilizce kelime: ").strip()
            if ing_kelime.lower() == 'q':
                break

            if not ing_kelime:
                print("⚠️ Boş kelime girilemez!")
                continue

            # Kelime zaten var mı kontrol et
            if ing_kelime.lower() in [k.lower() for k in self.kelimeler.keys()]:
                print(f"⚠️ '{ing_kelime}' kelimesi zaten mevcut!")
                print(f"Mevcut anlamı: {self.kelimeler[ing_kelime]}")

                guncelle = input("Anlamını güncellemek ister misiniz? (e/h): ").strip().lower()
                if guncelle != 'e':
                    continue

            # Türkçe anlamı al
            tr_anlam = input("Türkçe anlamı: ").strip()
            if not tr_anlam:
                print("⚠️ Boş anlam girilemez!")
                continue

            # Kelimeyi ekle
            self.kelimeler[ing_kelime] = tr_anlam

            # Dosyaya kaydet
            if self.kelimeleri_kaydet():
                print(f"✅ '{ing_kelime} → {tr_anlam}' başarıyla eklendi!")
            else:
                print("⚠️ Kelime kaydedilirken hata oluştu!")

            # Devam etmek istiyor mu?
            devam = input("\nBaşka kelime eklemek ister misiniz? (e/h): ").strip().lower()
            if devam != 'e':
                break

        print("\n🎉 Kelime ekleme tamamlandı!")
        input("Ana menüye dönmek için Enter'a basın...")

    def kelime_sil(self):
        """Hızlı kelime silme menüsü"""
        while True:
            self.ekrani_temizle()
            print("\n🗑️ HIZLI KELİME SİLME")
            print("="*30)

            if len(self.kelimeler) == 0:
                print("❌ Silinecek kelime bulunamadı!")
                print("💡 Menüden '6. YENİ KELİME EKLE' seçeneğini kullanarak kelime ekleyebilirsiniz.")
                input("Ana menüye dönmek için Enter'a basın...")
                return

            print("📚 Mevcut kelimeler:")
            print("-"*50)
            kelime_listesi = list(self.kelimeler.items())
            for i, (ing, tr) in enumerate(kelime_listesi, 1):
                print(f"{i:2d}. {ing:<18} → {tr}")
            print("-"*50)
            print(f"📊 Toplam: {len(kelime_listesi)} kelime")
            print("-"*50)

            print("\n🎯 Kelime numarası girin veya 'tümü' yazın")
            print("(Ana menüye dönmek için Enter'a basın)")

            secim = input("\nSeçiminiz: ").strip()

            # Ana menüye dön (boş giriş)
            if secim == '':
                break

            # Tüm kelimeleri sil
            elif secim.lower() == 'tümü' or secim.lower() == 'tumu':
                if self.tum_kelimeleri_sil():
                    break  # Tüm kelimeler silindiyse ana menüye dön

            # Tek kelime sil
            else:
                try:
                    kelime_no = int(secim)
                    if 1 <= kelime_no <= len(kelime_listesi):
                        self.tek_kelime_sil(kelime_listesi, kelime_no - 1)
                    else:
                        print(f"⚠️ Geçersiz numara! 1-{len(kelime_listesi)} arası bir sayı girin.")
                        time.sleep(2)
                except ValueError:
                    print("⚠️ Geçersiz giriş! Lütfen bir sayı, 'tümü' yazın veya Enter'a basın.")
                    time.sleep(2)

    def tek_kelime_sil(self, kelime_listesi, index):
        """Tek bir kelimeyi hızlıca sil"""
        silinecek_kelime = kelime_listesi[index][0]
        silinecek_anlam = kelime_listesi[index][1]

        # Direkt sil
        del self.kelimeler[silinecek_kelime]

        if self.kelimeleri_kaydet():
            print(f"\n✅ '{silinecek_kelime} → {silinecek_anlam}' silindi!")
            print(f"📊 Kalan kelime sayısı: {len(self.kelimeler)}")
        else:
            print("\n⚠️ Kelime silinirken hata oluştu!")

        time.sleep(1.5)  # Kısa bekleme

    def tum_kelimeleri_sil(self):
        """Tüm kelimeleri sil (sadece tümü için onay)"""
        print(f"\n⚠️ DİKKAT: {len(self.kelimeler)} kelimeyi silmek üzeresiniz!")
        print("Bu işlem GERİ ALINAMAZ!")

        onay = input("\nTüm kelimeleri silmek istediğinizden emin misiniz? (EVET/hayır): ").strip()
        if onay != "EVET":
            print("❌ İşlem iptal edildi.")
            time.sleep(1.5)
            return False

        # Tüm kelimeleri sil
        silinen_sayi = len(self.kelimeler)
        self.kelimeler.clear()

        if self.kelimeleri_kaydet():
            print(f"\n✅ Tüm kelimeler silindi! ({silinen_sayi} kelime)")
            print("📚 Artık hiç kelime kalmadı. Yeni kelimeler ekleyebilirsiniz.")
        else:
            print("\n⚠️ Silme işlemi sırasında hata oluştu!")

        input("\nAna menüye dönmek için Enter'a basın...")
        return True

    def tum_kelimeleri_goster(self):
        self.ekrani_temizle()
        print("\n📚 TÜM KELİMELER:")
        print("-"*40)

        if len(self.kelimeler) == 0:
            print("❌ Henüz kelime eklenmemiş!")
            print("💡 Menüden '6. YENİ KELİME EKLE' seçeneğini kullanarak kelime ekleyebilirsiniz.")
        else:
            for i, (ing, tr) in enumerate(self.kelimeler.items(), 1):
                print(f"{i:2d}. {ing:<15} → {tr}")

        print("-"*40)
        print(f"📊 Toplam: {len(self.kelimeler)} kelime")
        input("\nDevam etmek için Enter'a basın...")

    def kelime_testi(self):
        if len(self.kelimeler) == 0:
            print("❌ Test için kelime bulunamadı! Önce kelime ekleyin.")
            input("Ana menüye dönmek için Enter'a basın...")
            return

        self.ekrani_temizle()
        print("\n🧠 KELİME TESTİ (İngilizce → Türkçe)")
        print("(Çıkmak için 'q' yazın)")
        print("-"*35)

        kelime_listesi = list(self.kelimeler.items())
        random.shuffle(kelime_listesi)

        for ing_kelime, dogru_cevap in kelime_listesi:
            print(f"\n📝 '{ing_kelime}' kelimesinin Türkçesi nedir?")
            cevap = input("Cevabınız: ").strip().lower()

            if cevap == 'q':
                break

            if cevap == dogru_cevap.lower():
                print("✅ Doğru! Tebrikler!")
                self.dogru_sayisi += 1
                self.ogrenilenler.add(ing_kelime)
            else:
                print(f"❌ Yanlış! Doğru cevap: {dogru_cevap}")
                self.yanlis_sayisi += 1

            time.sleep(2)

        input("\nAna menüye dönmek için Enter'a basın...")

    def ters_kelime_testi(self):
        if len(self.kelimeler) == 0:
            print("❌ Test için kelime bulunamadı! Önce kelime ekleyin.")
            input("Ana menüye dönmek için Enter'a basın...")
            return

        self.ekrani_temizle()
        print("\n🔄 TERS KELİME TESTİ (Türkçe → İngilizce)")
        print("(Çıkmak için 'q' yazın)")
        print("-"*35)

        kelime_listesi = list(self.kelimeler.items())
        random.shuffle(kelime_listesi)

        for ing_kelime, tr_kelime in kelime_listesi:
            print(f"\n📝 '{tr_kelime}' kelimesinin İngilizcesi nedir?")
            cevap = input("Cevabınız: ").strip().lower()

            if cevap == 'q':
                break

            if cevap == ing_kelime.lower():
                print("✅ Doğru! Harika!")
                self.dogru_sayisi += 1
                self.ogrenilenler.add(ing_kelime)
            else:
                print(f"❌ Yanlış! Doğru cevap: {ing_kelime}")
                self.yanlis_sayisi += 1

            time.sleep(2)

        input("\nAna menüye dönmek için Enter'a basın...")

    def coktan_secmeli_test(self):
        if len(self.kelimeler) < 4:
            print("❌ Çoktan seçmeli test için en az 4 kelime gerekli!")
            input("Ana menüye dönmek için Enter'a basın...")
            return

        self.ekrani_temizle()
        print("\n🎯 ÇOKTAN SEÇMELİ TEST")
        print("(Çıkmak için 'q' yazın)")
        print("-"*25)

        kelime_listesi = list(self.kelimeler.items())
        random.shuffle(kelime_listesi)

        test_sayisi = min(5, len(kelime_listesi))

        for ing_kelime, dogru_cevap in kelime_listesi[:test_sayisi]:
            # Yanlış seçenekler oluştur
            yanlis_cevaplar = [tr for ing, tr in self.kelimeler.items() if tr != dogru_cevap]
            secenekler = random.sample(yanlis_cevaplar, min(3, len(yanlis_cevaplar))) + [dogru_cevap]
            random.shuffle(secenekler)

            print(f"\n📝 '{ing_kelime}' kelimesinin Türkçesi hangisidir?")
            for i, secenek in enumerate(secenekler, 1):
                print(f"{i}. {secenek}")

            cevap = input("Seçiminiz (1-4): ").strip()

            if cevap == 'q':
                break

            try:
                secilen_index = int(cevap) - 1
                if 0 <= secilen_index < len(secenekler):
                    if secenekler[secilen_index] == dogru_cevap:
                        print("✅ Doğru! Mükemmel!")
                        self.dogru_sayisi += 1
                        self.ogrenilenler.add(ing_kelime)
                    else:
                        print(f"❌ Yanlış! Doğru cevap: {dogru_cevap}")
                        self.yanlis_sayisi += 1
                else:
                    print("⚠️ Geçersiz seçim!")
                    continue
            except ValueError:
                print("⚠️ Lütfen geçerli bir sayı girin!")
                continue

            time.sleep(2)

        input("\nAna menüye dönmek için Enter'a basın...")

    def rastgele_kelime_ogren(self):
        if len(self.kelimeler) == 0:
            print("❌ Öğrenilecek kelime bulunamadı! Önce kelime ekleyin.")
            input("Ana menüye dönmek için Enter'a basın...")
            return

        self.ekrani_temizle()
        print("\n🎲 RASTGELE KELİME ÖĞRENME")
        print("(Çıkmak için 'q' yazın)")
        print("-"*30)

        while True:
            ing_kelime = random.choice(list(self.kelimeler.keys()))
            tr_kelime = self.kelimeler[ing_kelime]

            print(f"\n🔤 {ing_kelime}")
            cevap = input("Türkçesini görmek için Enter'a basın (çıkmak için 'q'): ").strip().lower()

            if cevap == 'q':
                break

            print(f"💡 Türkçesi: {tr_kelime}")
            self.ogrenilenler.add(ing_kelime)

            devam = input("\nBaşka kelime öğrenmek ister misiniz? (e/h): ").strip().lower()
            if devam != 'e':
                break

        input("\nAna menüye dönmek için Enter'a basın...")

    def istatistikleri_goster(self):
        self.ekrani_temizle()
        print("\n📊 İSTATİSTİKLER")
        print("-"*30)
        print(f"✅ Doğru cevaplar: {self.dogru_sayisi}")
        print(f"❌ Yanlış cevaplar: {self.yanlis_sayisi}")
        print(f"📚 Öğrenilen kelimeler: {len(self.ogrenilenler)}")
        print(f"📈 Toplam kelime sayısı: {len(self.kelimeler)}")

        if self.dogru_sayisi + self.yanlis_sayisi > 0:
            basari_orani = (self.dogru_sayisi / (self.dogru_sayisi + self.yanlis_sayisi)) * 100
            print(f"🎯 Başarı oranı: %{basari_orani:.1f}")

        if len(self.kelimeler) > 0:
            # İlerleme çubuğu
            ogrenme_orani = (len(self.ogrenilenler) / len(self.kelimeler)) * 100
            print(f"📈 Öğrenme oranı: %{ogrenme_orani:.1f}")

            # İlerleme çubuğu görsel
            bar_length = 20
            filled_length = int(bar_length * len(self.ogrenilenler) // len(self.kelimeler))
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"[{bar}] {len(self.ogrenilenler)}/{len(self.kelimeler)}")

        if self.ogrenilenler:
            print(f"\n🌟 Öğrendiğiniz kelimeler:")
            for kelime in sorted(self.ogrenilenler):
                if kelime in self.kelimeler:
                    print(f"   • {kelime} → {self.kelimeler[kelime]}")

        input("\nDevam etmek için Enter'a basın...")

    def calistir(self):
        print("🎉 Hızlı Kelime Öğrenme Programına Hoş Geldiniz!")
        print("Bu programda kelimelerinizi hızlıca yönetebilirsiniz! ⚡")
        input("Başlamak için Enter'a basın...")

        while True:
            self.menu_goster()
            secim = input("Seçiminizi yapın (1-9): ").strip()

            if secim == '1':
                self.tum_kelimeleri_goster()
            elif secim == '2':
                self.kelime_testi()
            elif secim == '3':
                self.ters_kelime_testi()
            elif secim == '4':
                self.coktan_secmeli_test()
            elif secim == '5':
                self.rastgele_kelime_ogren()
            elif secim == '6':
                self.yeni_kelime_ekle()
            elif secim == '7':
                self.kelime_sil()
            elif secim == '8':
                self.istatistikleri_goster()
            elif secim == '9':
                print("\n👋 Görüşmek üzere! İyi çalışmalar!")
                print(f"Final skorunuz: {self.dogru_sayisi} doğru, {self.yanlis_sayisi} yanlış")
                input("Çıkmak için Enter'a basın...")
                break
            else:
                print("\n⚠️ Geçersiz seçim! Lütfen 1-9 arası bir sayı girin.")
                time.sleep(2)

# Programı başlat
if __name__ == "__main__":
    try:
        program = KelimeOgrenmeProgrami()
        program.calistir()
    except KeyboardInterrupt:
        print("\n\nProgram kapatıldı. İyi günler!")
    except Exception as e:
        print(f"\nBir hata oluştu: {e}")
        input("Çıkmak için Enter'a basın...")
