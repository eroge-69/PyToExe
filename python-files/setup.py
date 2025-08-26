import wx
import json
import os

class RobotInterface(wx.Frame):
    def __init__(self, parent, title):
        super(RobotInterface, self).__init__(parent, title=title, size=(800, 400))

        # Panel oluştur
        self.panel = wx.Panel(self)
        
        # Verileri saklamak için değişkenler
        self.bilgiler = []
        self.robot_adi = "Otomat"
        self.kullanici_adi = ""
        self.kullanici_soyadi = ""
        self.hitap_sekli = "Hiçbir Şekilde Hitap Etmesin"
        self.mesajlari_goster = True
        self.mesajlar = []
        self.tum_mesajlar = []
        self.secili_bilgi_index = -1
        
        # Verileri yükle
        self.verileri_yukle()
        
        # Ana yatay kutu sizer'ı oluştur
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # Sol taraf: Ağaç görünümü ve düğmeler için dikey sizer
        vbox_sol = wx.BoxSizer(wx.VERTICAL)
        
        # Ağaç görünümü (TreeCtrl) oluştur
        self.agac = wx.TreeCtrl(self.panel, size=(200, 150), style=wx.TR_DEFAULT_STYLE)
        kok = self.agac.AddRoot("Kategoriler")
        self.sohbet_item = self.agac.AppendItem(kok, "Sohbet Arayüzü")
        self.ogret_item = self.agac.AppendItem(kok, "Robota Öğret")
        self.ayarlar_item = self.agac.AppendItem(kok, "Ayarlar")
        vbox_sol.Add(self.agac, proportion=0, flag=wx.ALL, border=10)
        
        # Ağaç görünümüne tıklama eventi bağla
        self.agac.Bind(wx.EVT_TREE_SEL_CHANGED, self.agac_secildi)
        
        # Başlık ve kontrol düğmeleri
        baslik = wx.StaticText(self.panel, label="Robot Kontrol Paneli")
        vbox_sol.Add(baslik, proportion=0, flag=wx.ALL, border=10)
        
        self.ileri_btn = wx.Button(self.panel, label="İleri", size=(100, 40))
        self.geri_btn = wx.Button(self.panel, label="Geri", size=(100, 40))
        self.sol_btn = wx.Button(self.panel, label="Sol", size=(100, 40))
        self.sag_btn = wx.Button(self.panel, label="Sağ", size=(100, 40))
        self.dur_btn = wx.Button(self.panel, label="Dur", size=(100, 40))
        
        # Düğmeleri dikey sizer'a ekle
        vbox_sol.Add(self.ileri_btn, proportion=0, flag=wx.ALL, border=5)
        vbox_sol.Add(self.geri_btn, proportion=0, flag=wx.ALL, border=5)
        vbox_sol.Add(self.sol_btn, proportion=0, flag=wx.ALL, border=5)
        vbox_sol.Add(self.sag_btn, proportion=0, flag=wx.ALL, border=5)
        vbox_sol.Add(self.dur_btn, proportion=0, flag=wx.ALL, border=5)
        
        # Sağ taraf: Dinamik içerik için bir panel
        self.sag_panel = wx.Panel(self.panel)
        self.sag_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sag_panel.SetSizer(self.sag_sizer)
        
        # Varsayılan olarak durum metin alanı göster
        self.durum = wx.TextCtrl(self.sag_panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.sag_sizer.Add(self.durum, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        # Yatay sizer'a sol sizer ve sağ paneli ekle
        self.hbox.Add(vbox_sol, proportion=0, flag=wx.ALL, border=10)
        self.hbox.Add(self.sag_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        # Düğmelere olay bağlama
        self.ileri_btn.Bind(wx.EVT_BUTTON, self.ileri_yap)
        self.geri_btn.Bind(wx.EVT_BUTTON, self.geri_yap)
        self.sol_btn.Bind(wx.EVT_BUTTON, self.sol_yap)
        self.sag_btn.Bind(wx.EVT_BUTTON, self.sag_yap)
        self.dur_btn.Bind(wx.EVT_BUTTON, self.dur_yap)
        
        # Pencere kapanırken verileri kaydet
        self.Bind(wx.EVT_CLOSE, self.kapatirken_kaydet)
        
        # Sizer'ı panele ata
        self.panel.SetSizer(self.hbox)
        
        # Pencereyi ortala ve göster
        self.Centre()
        self.Show(True)
    
    def verileri_yukle(self):
        if os.path.exists("ayarlar.json"):
            with open("ayarlar.json", "r", encoding="utf-8") as f:
                ayarlar = json.load(f)
                self.robot_adi = ayarlar.get("robot_adi", "Otomat")
                self.kullanici_adi = ayarlar.get("kullanici_adi", "")
                self.kullanici_soyadi = ayarlar.get("kullanici_soyadi", "")
                self.hitap_sekli = ayarlar.get("hitap_sekli", "Hiçbir Şekilde Hitap Etmesin")
                self.mesajlari_goster = ayarlar.get("mesajlari_goster", True)
                self.bilgiler = ayarlar.get("bilgiler", [])
        
        if os.path.exists("mesajlar.json"):
            with open("mesajlar.json", "r", encoding="utf-8") as f:
                self.mesajlar = json.load(f)
                self.tum_mesajlar = self.mesajlar.copy()
    
    def kapatirken_kaydet(self, event):
        ayarlar = {
            "robot_adi": self.robot_adi,
            "kullanici_adi": self.kullanici_adi,
            "kullanici_soyadi": self.kullanici_soyadi,
            "hitap_sekli": self.hitap_sekli,
            "mesajlari_goster": self.mesajlari_goster,
            "bilgiler": self.bilgiler
        }
        with open("ayarlar.json", "w", encoding="utf-8") as f:
            json.dump(ayarlar, f, ensure_ascii=False, indent=4)
        
        if self.mesajlari_goster:
            with open("mesajlar.json", "w", encoding="utf-8") as f:
                json.dump(self.mesajlar, f, ensure_ascii=False, indent=4)
        
        event.Skip()
    
    def agac_secildi(self, event):
        secili_item = event.GetItem()
        if secili_item == self.sohbet_item:
            self.sohbet_arayuzunu_goster()
        elif secili_item == self.ogret_item:
            self.ogret_arayuzunu_goster()
        elif secili_item == self.ayarlar_item:
            self.ayarlar_arayuzunu_goster()
        else:
            self.varsayilan_arayuzunu_goster()
    
    def varsayilan_arayuzunu_goster(self):
        self.sag_sizer.Clear(True)
        self.durum = wx.TextCtrl(self.sag_panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.sag_sizer.Add(self.durum, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        self.sag_panel.Layout()
    
    def sohbet_arayuzunu_goster(self):
        self.sag_sizer.Clear(True)
        
        self.sohbet_scrolled = wx.ScrolledWindow(self.sag_panel, style=wx.VSCROLL)
        self.sohbet_scrolled.SetScrollRate(0, 20)
        self.mesaj_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sohbet_scrolled.SetSizer(self.mesaj_sizer)
        
        if self.mesajlari_goster:
            self.tum_mesajlar = self.mesajlar.copy()
            for mesaj in self.mesajlar:
                mesaj_label = wx.StaticText(self.sohbet_scrolled, label=mesaj)
                self.mesaj_sizer.Add(mesaj_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        else:
            hitap = self.get_hitap()
            karsilama_metni = (
                f"{self.robot_adi}: {hitap}Ben bir makineyim, insanlar gibi iradem yoktur. "
                "Bana sorulan soruların cevapları bilgi bankamda varsa, soruları soran kişilere cevapları veririm. "
                "Bu yüzden lütfen beni başkalarıyla paylaşmadan önce, "
                "benim program dosyalarımın arasından senin bilgilerini tuttuğum dosyayı silmeyi unutma."
            )
            self.karsilama_mesaj = wx.StaticText(self.sohbet_scrolled, label=karsilama_metni)
            self.mesaj_sizer.Add(self.karsilama_mesaj, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
            self.mesajlar = [karsilama_metni]
            self.tum_mesajlar = self.mesajlar.copy()
        
        self.sag_sizer.Add(self.sohbet_scrolled, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        hbox_giris = wx.BoxSizer(wx.HORIZONTAL)
        self.mesaj_giris = wx.TextCtrl(self.sag_panel, style=wx.TE_PROCESS_ENTER)
        self.gonder_btn = wx.Button(self.sag_panel, label="Gönder")
        self.arama_btn = wx.Button(self.sag_panel, label="Arama")
        
        hbox_giris.Add(self.mesaj_giris, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        hbox_giris.Add(self.gonder_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_giris.Add(self.arama_btn, proportion=0, flag=wx.ALL, border=5)
        
        self.sag_sizer.Add(hbox_giris, proportion=0, flag=wx.ALL | wx.EXPAND, border=10)
        
        self.gonder_btn.Bind(wx.EVT_BUTTON, self.mesaj_gonder)
        self.mesaj_giris.Bind(wx.EVT_TEXT_ENTER, self.mesaj_gonder)
        self.arama_btn.Bind(wx.EVT_BUTTON, self.mesaj_ara)
        
        self.sag_panel.Layout()
    
    def mesaj_ara(self, event):
        arama_diyalog = wx.Dialog(self, title="Mesaj Ara", size=(400, 150))
        dialog_panel = wx.Panel(arama_diyalog)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        arama_etiket = wx.StaticText(dialog_panel, label="Arama Terimi:")
        self.arama_giris = wx.TextCtrl(dialog_panel, style=wx.TE_PROCESS_ENTER)
        dialog_sizer.Add(arama_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.arama_giris, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        
        hbox_dugmeler = wx.BoxSizer(wx.HORIZONTAL)
        ara_btn = wx.Button(dialog_panel, label="Ara")
        iptal_btn = wx.Button(dialog_panel, label="İptal")
        hbox_dugmeler.Add(ara_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(iptal_btn, proportion=0, flag=wx.ALL, border=5)
        
        dialog_sizer.Add(hbox_dugmeler, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        
        ara_btn.Bind(wx.EVT_BUTTON, lambda evt: self.aramayi_uygula(arama_diyalog))
        self.arama_giris.Bind(wx.EVT_TEXT_ENTER, lambda evt: self.aramayi_uygula(arama_diyalog))
        iptal_btn.Bind(wx.EVT_BUTTON, lambda evt: arama_diyalog.EndModal(wx.ID_CANCEL))
        
        dialog_panel.SetSizer(dialog_sizer)
        arama_diyalog.Centre()
        arama_diyalog.ShowModal()
        arama_diyalog.Destroy()
    
    def aramayi_uygula(self, diyalog):
        arama_terimi = self.arama_giris.GetValue().strip().lower()
        self.mesaj_sizer.Clear(True)
        
        if arama_terimi:
            filtrelenmis_mesajlar = [mesaj for mesaj in self.tum_mesajlar if arama_terimi in mesaj.lower()]
        else:
            filtrelenmis_mesajlar = self.tum_mesajlar
        
        for mesaj in filtrelenmis_mesajlar:
            mesaj_label = wx.StaticText(self.sohbet_scrolled, label=mesaj)
            self.mesaj_sizer.Add(mesaj_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        
        self.sohbet_scrolled.Layout()
        self.sohbet_scrolled.Scroll(0, self.sohbet_scrolled.GetScrollRange(wx.VERTICAL))
        diyalog.EndModal(wx.ID_OK)
    
    def get_hitap(self):
        if self.hitap_sekli == "Hiçbir Şekilde Hitap Etmesin" or not (self.kullanici_adi or self.kullanici_soyadi):
            return ""
        elif self.hitap_sekli == "Adımla ve Soyadımla":
            return f"Merhaba {self.kullanici_adi} {self.kullanici_soyadi}, "
        elif self.hitap_sekli == "Sadece Adımla":
            return f"Merhaba {self.kullanici_adi}, "
        elif self.hitap_sekli == "Sadece Soyadımla":
            return f"Merhaba {self.kullanici_soyadi}, "
        elif self.hitap_sekli == "Soyadımla ve Adımla":
            return f"Merhaba {self.kullanici_soyadi} {self.kullanici_adi}, "
        return ""
    
    def ayarlar_arayuzunu_goster(self):
        self.sag_sizer.Clear(True)
        
        ayarlar_sizer = wx.BoxSizer(wx.VERTICAL)
        
        ayarlar_metni = wx.StaticText(self.sag_panel, label="Robot Dili: Türkçe")
        ayarlar_sizer.Add(ayarlar_metni, proportion=0, flag=wx.ALL, border=10)
        
        robot_adi_metni = wx.StaticText(self.sag_panel, label=f"Robot Adı: {self.robot_adi}")
        self.robot_adi_duzenle_btn = wx.Button(self.sag_panel, label="Robot Adını Düzenle")
        ayarlar_sizer.Add(robot_adi_metni, proportion=0, flag=wx.ALL, border=10)
        ayarlar_sizer.Add(self.robot_adi_duzenle_btn, proportion=0, flag=wx.ALL, border=10)
        
        self.kullanici_girisi_btn = wx.Button(self.sag_panel, label="Kullanıcı Girişi")
        ayarlar_sizer.Add(self.kullanici_girisi_btn, proportion=0, flag=wx.ALL, border=10)
        
        self.mesajlari_goster_cb = wx.CheckBox(self.sag_panel, label="Sohbet Mesajlarını Göster")
        self.mesajlari_goster_cb.SetValue(self.mesajlari_goster)
        ayarlar_sizer.Add(self.mesajlari_goster_cb, proportion=0, flag=wx.ALL, border=10)
        
        self.robotu_formatla_btn = wx.Button(self.sag_panel, label="Robotu Formatla")
        ayarlar_sizer.Add(self.robotu_formatla_btn, proportion=0, flag=wx.ALL, border=10)
        
        self.ayarlar_yedekle_btn = wx.Button(self.sag_panel, label="Ayarları Yedekle")
        ayarlar_sizer.Add(self.ayarlar_yedekle_btn, proportion=0, flag=wx.ALL, border=10)
        
        self.ayarlar_geri_yukle_btn = wx.Button(self.sag_panel, label="Ayarları Geri Yükle")
        ayarlar_sizer.Add(self.ayarlar_geri_yukle_btn, proportion=0, flag=wx.ALL, border=10)
        
        self.robot_adi_duzenle_btn.Bind(wx.EVT_BUTTON, self.robot_adi_duzenle)
        self.kullanici_girisi_btn.Bind(wx.EVT_BUTTON, self.kullanici_girisi)
        self.mesajlari_goster_cb.Bind(wx.EVT_CHECKBOX, self.mesajlari_goster_degisti)
        self.robotu_formatla_btn.Bind(wx.EVT_BUTTON, self.robotu_formatla)
        self.ayarlar_yedekle_btn.Bind(wx.EVT_BUTTON, self.ayarlar_yedekle)
        self.ayarlar_geri_yukle_btn.Bind(wx.EVT_BUTTON, self.ayarlar_geri_yukle)
        
        self.sag_sizer.Add(ayarlar_sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        self.sag_panel.Layout()
    
    def ayarlar_yedekle(self, event):
        with wx.FileDialog(self, "Ayarları Yedekle", wildcard="JSON dosyaları (*.json)|*.json",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_OK:
                dosya_yolu = file_dialog.GetPath()
                yedek_veri = {
                    "robot_adi": self.robot_adi,
                    "kullanici_adi": self.kullanici_adi,
                    "kullanici_soyadi": self.kullanici_soyadi,
                    "hitap_sekli": self.hitap_sekli,
                    "mesajlari_goster": self.mesajlari_goster,
                    "bilgiler": self.bilgiler,
                    "mesajlar": self.mesajlar
                }
                try:
                    with open(dosya_yolu, "w", encoding="utf-8") as f:
                        json.dump(yedek_veri, f, ensure_ascii=False, indent=4)
                    wx.MessageBox("Ayarlar başarıyla yedeklendi!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Yedekleme hatası: {str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
    
    def ayarlar_geri_yukle(self, event):
        with wx.FileDialog(self, "Ayarları Geri Yükle", wildcard="JSON dosyaları (*.json)|*.json",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_OK:
                dosya_yollari = file_dialog.GetPaths()
                try:
                    for dosya_yolu in dosya_yollari:
                        with open(dosya_yolu, "r", encoding="utf-8") as f:
                            veri = json.load(f)
                            # Ayarları son dosyanın değerleriyle güncelle
                            self.robot_adi = veri.get("robot_adi", self.robot_adi)
                            self.kullanici_adi = veri.get("kullanici_adi", self.kullanici_adi)
                            self.kullanici_soyadi = veri.get("kullanici_soyadi", self.kullanici_soyadi)
                            self.hitap_sekli = veri.get("hitap_sekli", self.hitap_sekli)
                            self.mesajlari_goster = veri.get("mesajlari_goster", self.mesajlari_goster)
                            # Bilgileri birleştir (tekrarları önlemek için)
                            yeni_bilgiler = veri.get("bilgiler", [])
                            for bilgi in yeni_bilgiler:
                                if bilgi not in self.bilgiler:
                                    self.bilgiler.append(bilgi)
                            # Mesajları birleştir
                            yeni_mesajlar = veri.get("mesajlar", [])
                            for mesaj in yeni_mesajlar:
                                if mesaj not in self.mesajlar:
                                    self.mesajlar.append(mesaj)
                            self.tum_mesajlar = self.mesajlar.copy()
                    
                    # Arayüzü güncelle
                    if hasattr(self, 'bilgi_liste'):
                        self.bilgi_listesini_guncelle()
                    if hasattr(self, 'sohbet_scrolled'):
                        self.mesaj_sizer.Clear(True)
                        for mesaj in self.mesajlar:
                            mesaj_label = wx.StaticText(self.sohbet_scrolled, label=mesaj)
                            self.mesaj_sizer.Add(mesaj_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
                        self.sohbet_scrolled.Layout()
                        self.sohbet_scrolled.Scroll(0, self.sohbet_scrolled.GetScrollRange(wx.VERTICAL))
                    
                    wx.MessageBox("Ayarlar başarıyla geri yüklendi!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Geri yükleme hatası: {str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
    
    def robotu_formatla(self, event):
        mesaj = (
            "Robotu formatlarsanız, robota öğretilen tüm bilgiler, sohbet mesajları ve ayarlar sıfırlanacak. "
            "Bu işlem geri alınamaz! Uygulama kapanacak. Devam etmek ister misiniz?"
        )
        diyalog = wx.MessageDialog(self, mesaj, "Robotu Formatla", wx.YES_NO | wx.ICON_WARNING)
        if diyalog.ShowModal() == wx.ID_YES:
            onay_mesaj = (
                "Robotu sıfırlamak üzeresiniz. Bu işlem geri alınamaz! "
                "Robotunuzu yeniden eğitmek zorunda kalabilirsiniz. "
                "Yine de sıfırlamak ister misiniz?"
            )
            onay_diyalog = wx.MessageDialog(self, onay_mesaj, "Robotu Sıfırla", wx.YES_NO | wx.ICON_QUESTION)
            if onay_diyalog.ShowModal() == wx.ID_YES:
                # Verileri sıfırla
                self.bilgiler = []
                self.mesajlar = []
                self.tum_mesajlar = []
                self.robot_adi = "Otomat"
                self.kullanici_adi = ""
                self.kullanici_soyadi = ""
                self.hitap_sekli = "Hiçbir Şekilde Hitap Etmesin"
                self.mesajlari_goster = True
                # Dosyaları güncelle
                ayarlar = {
                    "robot_adi": self.robot_adi,
                    "kullanici_adi": self.kullanici_adi,
                    "kullanici_soyadi": self.kullanici_soyadi,
                    "hitap_sekli": self.hitap_sekli,
                    "mesajlari_goster": self.mesajlari_goster,
                    "bilgiler": self.bilgiler
                }
                with open("ayarlar.json", "w", encoding="utf-8") as f:
                    json.dump(ayarlar, f, ensure_ascii=False, indent=4)
                with open("mesajlar.json", "w", encoding="utf-8") as f:
                    json.dump(self.mesajlar, f, ensure_ascii=False, indent=4)
                # Arayüzü güncelle
                if hasattr(self, 'bilgi_liste'):
                    self.bilgi_listesini_guncelle()
                if hasattr(self, 'sohbet_scrolled'):
                    self.mesaj_sizer.Clear(True)
                    self.sohbet_scrolled.Layout()
                # Uygulamayı kapat
                self.Close()
            onay_diyalog.Destroy()
        diyalog.Destroy()
    
    def mesajlari_goster_degisti(self, event):
        self.mesajlari_goster = self.mesajlari_goster_cb.GetValue()
    
    def kullanici_girisi(self, event):
        kullanici_diyalog = wx.Dialog(self, title="Kullanıcı Girişi", size=(400, 250))
        dialog_panel = wx.Panel(kullanici_diyalog)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        ad_etiket = wx.StaticText(dialog_panel, label="Ad:")
        self.kullanici_ad_giris = wx.TextCtrl(dialog_panel, value=self.kullanici_adi)
        dialog_sizer.Add(ad_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.kullanici_ad_giris, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        
        soyad_etiket = wx.StaticText(dialog_panel, label="Soyad:")
        self.kullanici_soyad_giris = wx.TextCtrl(dialog_panel, value=self.kullanici_soyadi)
        dialog_sizer.Add(soyad_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.kullanici_soyad_giris, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        
        hitap_etiket = wx.StaticText(dialog_panel, label="Robot size nasıl hitap etsin?")
        self.hitap_combobox = wx.ComboBox(dialog_panel, choices=[
            "Adımla ve Soyadımla",
            "Sadece Adımla",
            "Sadece Soyadımla",
            "Soyadımla ve Adımla",
            "Hiçbir Şekilde Hitap Etmesin"
        ], style=wx.CB_READONLY)
        self.hitap_combobox.SetValue(self.hitap_sekli)
        self.hitap_combobox.Enable(bool(self.kullanici_soyad_giris.GetValue().strip()))
        dialog_sizer.Add(hitap_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.hitap_combobox, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        
        self.kullanici_soyad_giris.Bind(wx.EVT_TEXT, self.soyad_giris_kontrol)
        
        hbox_dugmeler = wx.BoxSizer(wx.HORIZONTAL)
        tamam_btn = wx.Button(dialog_panel, label="Tamam")
        iptal_btn = wx.Button(dialog_panel, label="İptal")
        hbox_dugmeler.Add(tamam_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(iptal_btn, proportion=0, flag=wx.ALL, border=5)
        
        dialog_sizer.Add(hbox_dugmeler, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        
        tamam_btn.Bind(wx.EVT_BUTTON, lambda evt: self.kullanici_kaydet_ve_kapat(kullanici_diyalog))
        iptal_btn.Bind(wx.EVT_BUTTON, lambda evt: kullanici_diyalog.EndModal(wx.ID_CANCEL))
        
        dialog_panel.SetSizer(dialog_sizer)
        kullanici_diyalog.Centre()
        kullanici_diyalog.ShowModal()
        kullanici_diyalog.Destroy()
    
    def soyad_giris_kontrol(self, event):
        self.hitap_combobox.Enable(bool(self.kullanici_soyad_giris.GetValue().strip()))
        if not self.kullanici_soyad_giris.GetValue().strip():
            self.hitap_combobox.SetValue("Hiçbir Şekilde Hitap Etmesin")
    
    def kullanici_kaydet_ve_kapat(self, diyalog):
        self.kullanici_adi = self.kullanici_ad_giris.GetValue().strip()
        self.kullanici_soyadi = self.kullanici_soyad_giris.GetValue().strip()
        self.hitap_sekli = self.hitap_combobox.GetValue()
        diyalog.EndModal(wx.ID_OK)
    
    def robot_adi_duzenle(self, event):
        ad_diyalog = wx.Dialog(self, title="Robot Adını Düzenle", size=(300, 150))
        dialog_panel = wx.Panel(ad_diyalog)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        ad_etiket = wx.StaticText(dialog_panel, label="Robot Adı:")
        self.ad_giris = wx.TextCtrl(dialog_panel, value=self.robot_adi)
        dialog_sizer.Add(ad_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.ad_giris, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        
        hbox_dugmeler = wx.BoxSizer(wx.HORIZONTAL)
        tamam_btn = wx.Button(dialog_panel, label="Tamam")
        iptal_btn = wx.Button(dialog_panel, label="İptal")
        hbox_dugmeler.Add(tamam_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(iptal_btn, proportion=0, flag=wx.ALL, border=5)
        
        dialog_sizer.Add(hbox_dugmeler, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        
        tamam_btn.Bind(wx.EVT_BUTTON, lambda evt: self.ad_kaydet_ve_kapat(ad_diyalog))
        iptal_btn.Bind(wx.EVT_BUTTON, lambda evt: ad_diyalog.EndModal(wx.ID_CANCEL))
        
        dialog_panel.SetSizer(dialog_sizer)
        ad_diyalog.Centre()
        ad_diyalog.ShowModal()
        ad_diyalog.Destroy()
    
    def ad_kaydet_ve_kapat(self, diyalog):
        yeni_ad = self.ad_giris.GetValue().strip()
        if yeni_ad:
            self.robot_adi = yeni_ad
        diyalog.EndModal(wx.ID_OK)
    
    def ogret_arayuzunu_goster(self):
        mesaj = "Robotunuza bir şeyler öğretebilir, robotunuzu kendinize göre eğitebilirsiniz."
        diyalog = wx.MessageDialog(self, mesaj, "Robota Öğret", wx.OK | wx.ICON_INFORMATION)
        diyalog.ShowModal()
        diyalog.Destroy()
        
        self.sag_sizer.Clear(True)
        
        self.ogret_scrolled = wx.ScrolledWindow(self.sag_panel, style=wx.VSCROLL)
        self.ogret_scrolled.SetScrollRate(0, 20)
        self.bilgi_sizer = wx.BoxSizer(wx.VERTICAL)
        self.ogret_scrolled.SetSizer(self.bilgi_sizer)
        
        self.bilgi_liste = wx.ListCtrl(self.ogret_scrolled, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.bilgi_liste.InsertColumn(0, "Soru", width=200)
        self.bilgi_liste.InsertColumn(1, "Cevap", width=200)
        self.bilgi_listesini_guncelle()
        
        self.bilgi_sizer.Add(self.bilgi_liste, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        self.ogret_btn = wx.Button(self.sag_panel, label="Öğret")
        self.bilgi_duzenle_btn = wx.Button(self.sag_panel, label="Bilgiyi Düzenle")
        self.bilgi_sil_btn = wx.Button(self.sag_panel, label="Bilgiyi Sil")
        
        hbox_dugmeler = wx.BoxSizer(wx.HORIZONTAL)
        hbox_dugmeler.Add(self.ogret_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(self.bilgi_duzenle_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(self.bilgi_sil_btn, proportion=0, flag=wx.ALL, border=5)
        
        self.sag_sizer.Add(self.ogret_scrolled, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        self.sag_sizer.Add(hbox_dugmeler, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        
        self.ogret_btn.Bind(wx.EVT_BUTTON, self.ogret_dugmesine_basildi)
        self.bilgi_duzenle_btn.Bind(wx.EVT_BUTTON, self.bilgi_duzenle)
        self.bilgi_sil_btn.Bind(wx.EVT_BUTTON, self.bilgi_sil)
        self.bilgi_liste.Bind(wx.EVT_LIST_ITEM_SELECTED, self.bilgi_secildi)
        
        self.sag_panel.Layout()
    
    def bilgi_secildi(self, event):
        self.secili_bilgi_index = event.GetIndex()
    
    def bilgi_listesini_guncelle(self):
        self.bilgi_liste.DeleteAllItems()
        for index, (soru, cevap) in enumerate(self.bilgiler):
            self.bilgi_liste.InsertItem(index, soru)
            self.bilgi_liste.SetItem(index, 1, cevap)
        self.secili_bilgi_index = -1
    
    def ogret_dugmesine_basildi(self, event):
        ogret_diyalog = wx.Dialog(self, title="Soru-Cevap Ekle", size=(400, 300))
        dialog_panel = wx.Panel(ogret_diyalog)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        soru_etiket = wx.StaticText(dialog_panel, label="Soru:")
        self.soru_giris = wx.TextCtrl(dialog_panel, style=wx.TE_MULTILINE)
        dialog_sizer.Add(soru_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.soru_giris, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        
        cevap_etiket = wx.StaticText(dialog_panel, label="Cevap:")
        self.cevap_giris = wx.TextCtrl(dialog_panel, style=wx.TE_MULTILINE)
        dialog_sizer.Add(cevap_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.cevap_giris, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        
        hbox_dugmeler = wx.BoxSizer(wx.HORIZONTAL)
        kaydet_btn = wx.Button(dialog_panel, label="Kaydet")
        iptal_btn = wx.Button(dialog_panel, label="İptal")
        hbox_dugmeler.Add(kaydet_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(iptal_btn, proportion=0, flag=wx.ALL, border=5)
        
        dialog_sizer.Add(hbox_dugmeler, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        
        kaydet_btn.Bind(wx.EVT_BUTTON, lambda evt: self.kaydet_ve_kapat(ogret_diyalog))
        iptal_btn.Bind(wx.EVT_BUTTON, lambda evt: ogret_diyalog.EndModal(wx.ID_CANCEL))
        
        dialog_panel.SetSizer(dialog_sizer)
        ogret_diyalog.Centre()
        ogret_diyalog.ShowModal()
        ogret_diyalog.Destroy()
    
    def kaydet_ve_kapat(self, diyalog):
        soru = self.soru_giris.GetValue().strip()
        cevap = self.cevap_giris.GetValue().strip()
        if soru and cevap:
            self.bilgiler.append((soru, cevap))
            self.bilgi_listesini_guncelle()
        diyalog.EndModal(wx.ID_OK)
    
    def bilgi_duzenle(self, event):
        if self.secili_bilgi_index == -1:
            wx.MessageBox("Lütfen düzenlemek için bir bilgi seçin!", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        soru, cevap = self.bilgiler[self.secili_bilgi_index]
        duzenle_diyalog = wx.Dialog(self, title="Soru-Cevap Düzenle", size=(400, 300))
        dialog_panel = wx.Panel(duzenle_diyalog)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        soru_etiket = wx.StaticText(dialog_panel, label="Soru:")
        self.soru_giris = wx.TextCtrl(dialog_panel, style=wx.TE_MULTILINE, value=soru)
        dialog_sizer.Add(soru_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.soru_giris, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        
        cevap_etiket = wx.StaticText(dialog_panel, label="Cevap:")
        self.cevap_giris = wx.TextCtrl(dialog_panel, style=wx.TE_MULTILINE, value=cevap)
        dialog_sizer.Add(cevap_etiket, proportion=0, flag=wx.ALL, border=5)
        dialog_sizer.Add(self.cevap_giris, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        
        hbox_dugmeler = wx.BoxSizer(wx.HORIZONTAL)
        kaydet_btn = wx.Button(dialog_panel, label="Kaydet")
        iptal_btn = wx.Button(dialog_panel, label="İptal")
        hbox_dugmeler.Add(kaydet_btn, proportion=0, flag=wx.ALL, border=5)
        hbox_dugmeler.Add(iptal_btn, proportion=0, flag=wx.ALL, border=5)
        
        dialog_sizer.Add(hbox_dugmeler, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        
        kaydet_btn.Bind(wx.EVT_BUTTON, lambda evt: self.duzenle_ve_kapat(duzenle_diyalog, self.secili_bilgi_index))
        iptal_btn.Bind(wx.EVT_BUTTON, lambda evt: duzenle_diyalog.EndModal(wx.ID_CANCEL))
        
        dialog_panel.SetSizer(dialog_sizer)
        duzenle_diyalog.Centre()
        duzenle_diyalog.ShowModal()
        duzenle_diyalog.Destroy()
    
    def duzenle_ve_kapat(self, diyalog, index):
        soru = self.soru_giris.GetValue().strip()
        cevap = self.cevap_giris.GetValue().strip()
        if soru and cevap:
            self.bilgiler[index] = (soru, cevap)
            self.bilgi_listesini_guncelle()
        diyalog.EndModal(wx.ID_OK)
    
    def bilgi_sil(self, event):
        if self.secili_bilgi_index == -1:
            wx.MessageBox("Lütfen silmek için bir bilgi seçin!", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        onay_mesaj = "Bu bilgiyi silmek istediğinizden emin misiniz?"
        onay_diyalog = wx.MessageDialog(self, onay_mesaj, "Bilgi Sil", wx.YES_NO | wx.ICON_QUESTION)
        if onay_diyalog.ShowModal() == wx.ID_YES:
            self.bilgiler.pop(self.secili_bilgi_index)
            self.bilgi_listesini_guncelle()
        onay_diyalog.Destroy()
    
    def mesaj_gonder(self, event):
        if self.mesaj_giris.GetValue().strip() == "":
            return
        
        kullanici_soru = self.mesaj_giris.GetValue().strip()
        kullanici_mesaj = f"Kullanıcı: {kullanici_soru}"
        kullanici_label = wx.StaticText(self.sohbet_scrolled, label=kullanici_mesaj)
        self.mesaj_sizer.Add(kullanici_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        self.mesajlar.append(kullanici_mesaj)
        self.tum_mesajlar.append(kullanici_mesaj)
        
        bulundu = False
        for soru, cevap in self.bilgiler:
            if kullanici_soru.lower() == soru.lower():
                hitap = self.get_hitap()
                robot_cevap = f"{self.robot_adi}: {hitap}{cevap}"
                robot_label = wx.StaticText(self.sohbet_scrolled, label=robot_cevap)
                self.mesaj_sizer.Add(robot_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
                self.mesajlar.append(robot_cevap)
                self.tum_mesajlar.append(robot_cevap)
                bulundu = True
                break
        
        if not bulundu:
            hitap = self.get_hitap()
            if kullanici_soru.lower() == "evet":
                robot_cevap = f"{self.robot_adi}: {hitap}Lütfen Robota Öğret kategorisine gidin ve bana bir şeyler öğretin."
            else:
                robot_cevap = f"{self.robot_adi}: {hitap}Bu konuyu bilmiyorum, bana öğretmek ister miydiniz?"
            robot_label = wx.StaticText(self.sohbet_scrolled, label=robot_cevap)
            self.mesaj_sizer.Add(robot_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
            self.mesajlar.append(robot_cevap)
            self.tum_mesajlar.append(robot_cevap)
        
        self.sohbet_scrolled.Layout()
        self.sohbet_scrolled.Scroll(0, self.sohbet_scrolled.GetScrollRange(wx.VERTICAL))
        self.mesaj_giris.SetValue("")
    
    def ileri_yap(self, event):
        if hasattr(self, 'durum'):
            self.durum.AppendText("Robot ileri gidiyor...\n")
    
    def geri_yap(self, event):
        if hasattr(self, 'durum'):
            self.durum.AppendText("Robot geri gidiyor...\n")
    
    def sol_yap(self, event):
        if hasattr(self, 'durum'):
            self.durum.AppendText("Robot sola dönüyor...\n")
    
    def sag_yap(self, event):
        if hasattr(self, 'durum'):
            self.durum.AppendText("Robot sağa dönüyor...\n")
    
    def dur_yap(self, event):
        if hasattr(self, 'durum'):
            self.durum.AppendText("Robot durdu.\n")

# Uygulamayı başlat
if __name__ == "__main__":
    app = wx.App()
    RobotInterface(None, title="Yatay Robot Kontrol Arayüzü")
    app.MainLoop()