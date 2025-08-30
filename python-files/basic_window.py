import wx

class KarsilamaPenceresi(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Hoş Geldiniz", size=(300, 200))
        panel = wx.Panel(self)
        
        # Karşılama metni
        karsilama_metni = wx.StaticText(panel, label="Merhaba! Uygulamaya Hoş Geldiniz!", pos=(50, 50))
        
        # Çıkış düğmesi
        cikis_dugmesi = wx.Button(panel, label="Çıkış", pos=(100, 100))
        cikis_dugmesi.Bind(wx.EVT_BUTTON, self.cikis_yap)
        
        self.Centre()  # Pencereyi ekranın ortasına yerleştir
        self.Show()

    def cikis_yap(self, event):
        self.Close()  # Pencereyi kapat

if __name__ == "__main__":
    app = wx.App()
    pencere = KarsilamaPenceresi()
    app.MainLoop()