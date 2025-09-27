import wx

class AnaPencere(wx.Frame):
    def __init__(self, parent, title):
        super(AnaPencere, self).__init__(parent, title=title, size=(300, 200))
        
        # Ana pencere düzeni
        panel = wx.Panel(self)
        self.button = wx.Button(panel, label="İslemi Tamamla", pos=(10, 10))
        
        # Düğme olayını bağla
        self.button.Bind(wx.EVT_BUTTON, self.on_islem_tamamla)
        
        self.Show()

    def on_islem_tamamla(self, event):
        # Mesaj kutusu oluştur
        dialog = wx.MessageDialog(self, "İşlem tamamlandı", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        dialog.Bind(wx.EVT_BUTTON, self.on_dialog_tamam)
        dialog.ShowModal()

    def on_dialog_tamam(self, event):
        # Tamam düğmesine basıldığında programı kapat
        self.Close()

# Uygulamayı başlat
app = wx.App()
frame = AnaPencere(None, "Basit Pencere")
app.MainLoop()