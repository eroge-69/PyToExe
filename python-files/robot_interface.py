# -*- coding: utf-8 -*-
import wx
import json
import os


class RobotInterface(wx.Frame):
    def __init__(self, parent, title):
        super(RobotInterface, self).__init__(parent, title=title, size=(900, 600))

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
        self.agac = wx.TreeCtrl(self.panel, size=(220, 200), style=wx.TR_DEFAULT_STYLE)
        kok = self.agac.AddRoot("Kategoriler")
        self.sohbet_item = self.agac.AppendItem(kok, "Sohbet Arayüzü")
        self.ogret_item = self.agac.AppendItem(kok, "Robota Öğret")
        self.ayarlar_item = self.agac.AppendItem(kok, "Ayarlar")
        self.agac.ExpandAll()
        vbox_sol.Add(self.agac, proportion=0, flag=wx.ALL | wx.EXPAND, border=10)

        # Ağaç görünümüne tıklama eventi bağla
        self.agac.Bind(wx.EVT_TREE_SEL_CHANGED, self.agac_secildi)

        # Başlık ve kontrol düğmeleri
        baslik = wx.StaticText(self.panel, label="Robot Kontrol Paneli")
        font = baslik.GetFont()
        font.PointSize += 2
        font = font.Bold()
        baslik.SetFont(font)
        vbox_sol.Add(baslik, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.ileri_btn = wx.Button(self.panel, label="İleri", size=(100, 36))
        self.geri_btn = wx.Button(self.panel, label="Geri", size=(100, 36))
        self.sol_btn = wx.Button(self.panel, label="Sol", size=(100, 36))
        self.sag_btn = wx.Button(self.panel, label="Sağ", size=(100, 36))
        self.dur_btn = wx.Button(self.panel, label="Dur", size=(100, 36))

        # Düğmeleri dikey sizer'a ekle
        for b in (self.ileri_btn, self.geri_btn, self.sol_btn, self.sag_btn, self.dur_btn):
            vbox_sol.Add(b, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        # Sağ taraf: Dinamik içerik için bir panel
        self.sag_panel = wx.Panel(self.panel)
        self.sag_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sag_panel.SetSizer(self.sag_sizer)

        # Varsayılan olarak durum metin alanı göster
        self.durum = wx.TextCtrl(self.sag_panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.sag_sizer.Add(self.durum, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)

        # Yatay sizer'a sol sizer ve sağ paneli ekle
        self.hbox.Add(vbox_sol, proportion=0, flag=wx.ALL | wx.EXPAND, border=10)
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

        # Açılışta Sohbet ekranını göster
        self.sohbet_arayuzunu_goster()
        self.agac.SelectItem(self.sohbet_item)

    # ==================== VERİLER ====================
    def verileri_yukle(self):
        try:
            if os.path.exists("ayarlar.json"):
                with open("ayarlar.json", "r", encoding="utf-8") as f:
                    ayarlar = json.load(f)
                    self.robot_adi = ayarlar.get("robot_adi", "Otomat")
                    self.kullanici_adi = ayarlar.get("kullanici_adi", "")
                    self.kullanici_soyadi = ayarlar.get("kullanici_soyadi", "")
                    self.hitap_sekli = ayarlar.get("hitap_sekli", "Hiçbir Şekilde Hitap Etmesin")
                    self.mesajlari_goster = ayarlar.get("mesajlari_goster", True)
                    self.bilgiler = ayarlar.get("bilgiler", [])
        except Exception as e:
            wx.LogError(f"Ayarlar yüklenemedi: {e}")

        try:
            if os.path.exists("mesajlar.json"):
                with open("mesajlar.json", "r", encoding="utf-8") as f:
                    self.mesajlar = json.load(f)
                    self.tum_mesajlar = self.mesajlar.copy()
        except Exception as e:
            wx.LogError(f"Mesajlar yüklenemedi: {e}")
            self.mesajlar = []
            self.tum_mesajlar = []

    def kapatirken_kaydet(self, event):
        try:
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
        finally:
            event.Skip()

    # ==================== AĞAÇ SEÇİMİ ====================
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

    # ==================== ROBOT HAREKET KONTROLÜ ====================
    def ileri_yap(self, event):
        self.durum.AppendText("Robot ileri gidiyor...\n")

    def geri_yap(self, event):
        self.durum.AppendText("Robot geri gidiyor...\n")

    def sol_yap(self, event):
        self.durum.AppendText("Robot sola dönüyor...\n")

    def sag_yap(self, event):
        self.durum.AppendText("Robot sağa dönüyor...\n")

    def dur_yap(self, event):
        self.durum.AppendText("Robot duruyor...\n")

    # ==================== SOHBET ====================
    def sohbet_arayuzunu_goster(self):
        self.sag_sizer.Clear(True)

        self.sohbet_scrolled = wx.ScrolledWindow(self.sag_panel, style=wx.VSCROLL)
        self.sohbet_scrolled.SetScrollRate(0, 20)
        self.mesaj_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sohbet_scrolled.SetSizer(self.mesaj_sizer)

        if self.mesajlari_goster and self.mesajlar:
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
            if not self.mesajlar:
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

    def mesaj_gonder(self, event):
        metin = self.mesaj_giris.GetValue().strip()
        if not metin:
            return
        # Kullanıcı mesajını ekle
        kullanici_etiket = f"Kullanıcı: {metin}"
        lbl_k = wx.StaticText(self.sohbet_scrolled, label=kullanici_etiket)
        self.mesaj_sizer.Add(lbl_k, 0, wx.ALL | wx.EXPAND, 5)
        self.mesajlar.append(kullanici_etiket)
        self.tum_mesajlar.append(kullanici_etiket)

        # Basit bir cevap üret (bilgi tabanını tarayarak, eşleşen anahtar kelime varsa)
        cevap = self.basit_yanit_uret(metin)
        robot_etiket = f"{self.robot_adi}: {cevap}"
        lbl_r = wx.StaticText(self.sohbet_scrolled, label=robot_etiket)
        self.mesaj_sizer.Add(lbl_r, 0, wx.ALL | wx.EXPAND, 5)
        self.mesajlar.append(robot_etiket)
        self.tum_mesajlar.append(robot_etiket)

        self.mesaj_giris.SetValue("")
        self.sohbet_scrolled.Layout()
        self.sohbet_scrolled.Scroll(0, self.sohbet_scrolled.GetScrollRange(wx.VERTICAL))

    def basit_yanit_uret(self, metin):
        # Çok basit bir kural: bilgi girdileri arasında metni içeren varsa onları döndür
        metin_l = metin.lower()
        eslesmeler = [b for b in self.bilgiler if metin_l in b.lower()]
        if eslesmeler:
            return "İlgili bulgular: " + "; ".join(eslesmeler[:3])
        # Aksi halde sabit bir yanıt
        hitap = self.get_hitap()
        return f"{hitap}Mesajını aldım. Daha fazla bilgi için 'Robota Öğret' bölümünden veri ekleyebilirsin."

    def mesaj_ara(self, event):
        arama_diyalog = wx.Dialog(self, title="Mesaj Ara", size=(420, 170))
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

    # ==================== HİTAP ====================
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

    # ==================== AYARLAR ====================
    def ayarlar_arayuzunu_goster(self):
        self.sag_sizer.Clear(True)

        ayarlar_sizer = wx.BoxSizer(wx.VERTICAL)

        ayarlar_metni = wx.StaticText(self.sag_panel, label="Robot Dili: Türkçe")
        ayarlar_sizer.Add(ayarlar_metni, proportion=0, flag=wx.ALL, border=10)

        self.robot_adi_metni = wx.StaticText(self.sag_panel, label=f"Robot Adı: {self.robot_adi}")
        self.robot_adi_duzenle_btn = wx.Button(self.sag_panel, label="Robot Adını Düzenle")
        ayarlar_sizer.Add(self.robot_adi_metni, proportion=0, flag=wx.ALL, border=10)
        ayarlar_sizer.Add(self.robot_adi_duzenle_btn, proportion=0, flag=wx.ALL, border=10)

        self.kullanici_girisi_btn = wx.Button(self.sag_panel, label="Kullanıcı Girişi")
        ayarlar_sizer.Add(self.kullanici_girisi_btn, proportion=0, flag=wx.ALL, border=10)

        self.mesajlari_goster_cb = wx.CheckBox(self.sag_panel, label="Sohbet Mesajlarını Göster (kayıt)")
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

                    if hasattr(self, 'robot_adi_metni'):
                        self.robot_adi_metni.SetLabel(f"Robot Adı: {self.robot_adi}")

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

    def robot_adi_duzenle(self, event):
        dlg = wx.TextEntryDialog(self, "Yeni robot adını giriniz:", "Robot Adı Düzenle", value=self.robot_adi)
        if dlg.ShowModal() == wx.ID_OK:
            yeni_ad = dlg.GetValue().strip()
            if yeni_ad:
                self.robot_adi = yeni_ad
                if hasattr(self, 'robot_adi_metni'):
                    self.robot_adi_metni.SetLabel(f"Robot Adı: {self.robot_adi}")
                wx.MessageBox("Robot adı güncellendi.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    # ==================== KULLANICI GİRİŞİ ====================
    def kullanici_girisi(self, event):
        kullanici_diyalog = wx.Dialog(self, title="Kullanıcı Girişi", size=(420, 280))
        dialog_panel = wx.Panel(kullanici_diyalog)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)

        ad_label = wx.StaticText(dialog_panel, label="Adınız:")
        self.ad_input = wx.TextCtrl(dialog_panel, value=self.kullanici_adi)

        soyad_label = wx.StaticText(dialog_panel, label="Soyadınız:")
        self.soyad_input = wx.TextCtrl(dialog_panel, value=self.kullanici_soyadi)

        hitap_label = wx.StaticText(dialog_panel, label="Hitap Şekli:")
        hitap_secenekleri = [
            "Hiçbir Şekilde Hitap Etmesin",
            "Adımla ve Soyadımla",
            "Sadece Adımla",
            "Sadece Soyadımla",
            "Soyadımla ve Adımla"
        ]
        self.hitap_choice = wx.Choice(dialog_panel, choices=hitap_secenekleri)
        if self.hitap_sekli in hitap_secenekleri:
            self.hitap_choice.SetSelection(hitap_secenekleri.index(self.hitap_sekli))
        else:
            self.hitap_choice.SetSelection(0)

        kaydet_btn = wx.Button(dialog_panel, label="Kaydet")
        iptal_btn = wx.Button(dialog_panel, label="İptal")

        dialog_sizer.Add(ad_label, 0, wx.ALL, 5)
        dialog_sizer.Add(self.ad_input, 0, wx.ALL | wx.EXPAND, 5)
        dialog_sizer.Add(soyad_label, 0, wx.ALL, 5)
        dialog_sizer.Add(self.soyad_input, 0, wx.ALL | wx.EXPAND, 5)
        dialog_sizer.Add(hitap_label, 0, wx.ALL, 5)
        dialog_sizer.Add(self.hitap_choice, 0, wx.ALL | wx.EXPAND, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(kaydet_btn, 0, wx.ALL, 5)
        hbox.Add(iptal_btn, 0, wx.ALL, 5)
        dialog_sizer.Add(hbox, 0, wx.CENTER)

        kaydet_btn.Bind(wx.EVT_BUTTON, lambda evt: self.kullanici_kaydet(evt, kullanici_diyalog))
        iptal_btn.Bind(wx.EVT_BUTTON, lambda evt: kullanici_diyalog.EndModal(wx.ID_CANCEL))

        dialog_panel.SetSizer(dialog_sizer)
        kullanici_diyalog.Centre()
        kullanici_diyalog.ShowModal()
        kullanici_diyalog.Destroy()

    def kullanici_kaydet(self, event, diyalog):
        self.kullanici_adi = self.ad_input.GetValue().strip()
        self.kullanici_soyadi = self.soyad_input.GetValue().strip()
        self.hitap_sekli = self.hitap_choice.GetStringSelection()
        diyalog.EndModal(wx.ID_OK)
        wx.MessageBox("Kullanıcı bilgileri kaydedildi!", "Başarılı", wx.OK | wx.ICON_INFORMATION)

    # ==================== ROBOTA ÖĞRET ====================
    def ogret_arayuzunu_goster(self):
        self.sag_sizer.Clear(True)

        ana_sizer = wx.BoxSizer(wx.VERTICAL)

        # Bilgi listesi
        self.bilgi_liste = wx.ListBox(self.sag_panel, choices=self.bilgiler, style=wx.LB_SINGLE)
        ana_sizer.Add(self.bilgi_liste, 1, wx.ALL | wx.EXPAND, 10)

        # Düzenleme alanı
        editor_label = wx.StaticText(self.sag_panel, label="Bilgi (metin):")
        self.bilgi_editor = wx.TextCtrl(self.sag_panel, style=wx.TE_MULTILINE)
        ana_sizer.Add(editor_label, 0, wx.LEFT | wx.RIGHT, 10)
        ana_sizer.Add(self.bilgi_editor, 0, wx.ALL | wx.EXPAND, 10)

        # Düğmeler
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        ekle_btn = wx.Button(self.sag_panel, label="Ekle")
        guncelle_btn = wx.Button(self.sag_panel, label="Güncelle")
        sil_btn = wx.Button(self.sag_panel, label="Sil")
        temizle_btn = wx.Button(self.sag_panel, label="Temizle")
        hbox.Add(ekle_btn, 0, wx.ALL, 5)
        hbox.Add(guncelle_btn, 0, wx.ALL, 5)
        hbox.Add(sil_btn, 0, wx.ALL, 5)
        hbox.Add(temizle_btn, 0, wx.ALL, 5)
        ana_sizer.Add(hbox, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        # Eventler
        self.bilgi_liste.Bind(wx.EVT_LISTBOX, self.bilgi_secildi)
        ekle_btn.Bind(wx.EVT_BUTTON, self.bilgi_ekle)
        guncelle_btn.Bind(wx.EVT_BUTTON, self.bilgi_guncelle)
        sil_btn.Bind(wx.EVT_BUTTON, self.bilgi_sil)
        temizle_btn.Bind(wx.EVT_BUTTON, lambda e: self.bilgi_editor.SetValue(""))

        self.sag_sizer.Add(ana_sizer, 1, wx.ALL | wx.EXPAND, 5)
        self.sag_panel.Layout()

    def bilgi_secildi(self, event):
        idx = self.bilgi_liste.GetSelection()
        if idx != wx.NOT_FOUND:
            self.secili_bilgi_index = idx
            self.bilgi_editor.SetValue(self.bilgiler[idx])

    def bilgi_ekle(self, event):
        metin = self.bilgi_editor.GetValue().strip()
        if not metin:
            wx.MessageBox("Boş bilgi eklenemez.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        if metin not in self.bilgiler:
            self.bilgiler.append(metin)
            self.bilgi_listesini_guncelle()
            self.bilgi_editor.SetValue("")
        else:
            wx.MessageBox("Bu bilgi zaten mevcut.", "Bilgi", wx.OK | wx.ICON_INFORMATION)

    def bilgi_guncelle(self, event):
        idx = self.bilgi_liste.GetSelection()
        if idx == wx.NOT_FOUND:
            wx.MessageBox("Güncellenecek bir bilgi seçiniz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        metin = self.bilgi_editor.GetValue().strip()
        if not metin:
            wx.MessageBox("Boş bilgi kaydedilemez.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        self.bilgiler[idx] = metin
        self.bilgi_listesini_guncelle()

    def bilgi_sil(self, event):
        idx = self.bilgi_liste.GetSelection()
        if idx == wx.NOT_FOUND:
            wx.MessageBox("Silinecek bir bilgi seçiniz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        silinecek = self.bilgiler[idx]
        dlg = wx.MessageDialog(self, f"Silmek istediğinize emin misiniz?\n\n{silinecek}", "Onay",
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            del self.bilgiler[idx]
            self.bilgi_listesini_guncelle()
            self.bilgi_editor.SetValue("")
        dlg.Destroy()

    def bilgi_listesini_guncelle(self):
        if hasattr(self, "bilgi_liste"):
            self.bilgi_liste.Set(self.bilgiler)

    # ==================== YARDIMCI ====================
    def robot_adi_guncel_metin(self):
        return f"{self.robot_adi}"


# ==================== PROGRAM BAŞLAT ====================
if __name__ == "__main__":
    app = wx.App(False)
    frame = RobotInterface(None, "Robot Arayüzü")
    app.MainLoop()
