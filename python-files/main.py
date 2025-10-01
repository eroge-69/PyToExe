import wx
import wx.html2 as webview

class BrowserFrame(wx.Frame):
    def __init__(self, parent, url="https://www.google.com"):
        super().__init__(parent, title="SM Browser", size=(800, 600))
        
        # Создаем вертикальный бокс-лаппет (разметку)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Создаем панель для навигации
        nav_panel = wx.Panel(self)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Адресная строка
        self.url_ctrl = wx.TextCtrl(nav_panel, style=wx.TE_PROCESS_ENTER)
        self.url_ctrl.SetValue(url)
        self.url_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_go)
        
        # Кнопка "Go"
        go_button = wx.Button(nav_panel, label="Go")
        go_button.Bind(wx.EVT_BUTTON, self.on_go)
        
        # Кнопки "Back" и "Forward"
        back_button = wx.Button(nav_panel, label="Back")
        back_button.Bind(wx.EVT_BUTTON, self.on_back)
        forward_button = wx.Button(nav_panel, label="Forward")
        forward_button.Bind(wx.EVT_BUTTON, self.on_forward)
        
        # Добавляем элементы навигационной панели
        nav_sizer.Add(back_button, 0, wx.ALL, 2)
        nav_sizer.Add(forward_button, 0, wx.ALL, 2)
        nav_sizer.Add(self.url_ctrl, 1, wx.EXPAND | wx.ALL, 2)
        nav_sizer.Add(go_button, 0, wx.ALL, 2)
        nav_panel.SetSizer(nav_sizer)
        
        vbox.Add(nav_panel, 0, wx.EXPAND)
        
        # Создаем компонент для отображения веб-страниц
        self.browser = webview.WebView.New(self)
        self.browser.LoadURL(url)
        vbox.Add(self.browser, 1, wx.EXPAND)
        
        self.SetSizer(vbox)
        
        # Обновляем адресную строку при изменении страницы
        self.browser.Bind(webview.EVT_WEBVIEW_NAVIGATED, self.on_navigate)
        
    def on_go(self, event):
        url = self.url_ctrl.GetValue()
        self.browser.LoadURL(url)
        
    def on_back(self, event):
        self.browser.GoBack()
        
    def on_forward(self, event):
        self.browser.GoForward()
        
    def on_navigate(self, event):
        url = self.browser.GetCurrentURL()
        self.url_ctrl.SetValue(url)

class MyApp(wx.App):
    def OnInit(self):
        frame = BrowserFrame(None)
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()