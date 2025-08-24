import wx
import json
import os
import glob
from datetime import datetime

class ChatBot:
    def __init__(self):
        self.knowledge_base = {}
        self.json_file = "robot_knowledge.json"
        self.load_knowledge()
    
    def load_knowledge(self):
        """Mevcut dizindeki tüm JSON dosyalarından bilgileri yükler"""
        self.knowledge_base = {}
        json_files = glob.glob("*.json")
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.knowledge_base.update(data)
            except (json.JSONDecodeError, FileNotFoundError):
                continue
    
    def save_knowledge(self):
        """Ana JSON dosyasına bilgileri kaydeder"""
        try:
            # Mevcut dosyayı oku
            existing_data = {}
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Yeni bilgileri ekle
            existing_data.update(self.knowledge_base)
            
            # Dosyaya kaydet
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Kayıt hatası: {e}")
    
    def learn(self, question, answer):
        """Yeni soru-cevap çifti öğrenir"""
        self.knowledge_base[question.lower()] = answer
        self.save_knowledge()
        # Öğrenme sonrası tüm dosyaları yeniden yükle
        self.load_knowledge()
    
    def get_answer(self, question):
        """Soruya cevap arar"""
        question_lower = question.lower()
        
        # Tam eşleşme ara
        if question_lower in self.knowledge_base:
            return self.knowledge_base[question_lower]
        
        # Kısmi eşleşme ara
        for q, a in self.knowledge_base.items():
            if question_lower in q or q in question_lower:
                return a
        
        return "Bu konuda henüz bilgim yok. Bana öğretmek ister misin?"
    
    def get_all_qa_pairs(self):
        """Tüm soru-cevap çiftlerini döndürür"""
        return self.knowledge_base

class ChatPanel(wx.Panel):
    def __init__(self, parent, chatbot):
        super().__init__(parent)
        self.chatbot = chatbot
        self.init_ui()
    
    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Sohbet geçmişi
        self.chat_history = wx.TextCtrl(
            self, 
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(500, 300)
        )
        self.chat_history.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        # Mesaj girişi
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.message_input = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.send_button = wx.Button(self, label="Gönder")
        
        input_sizer.Add(self.message_input, 1, wx.EXPAND | wx.RIGHT, 5)
        input_sizer.Add(self.send_button, 0)
        
        sizer.Add(wx.StaticText(self, label="Sohbet:"), 0, wx.ALL, 5)
        sizer.Add(self.chat_history, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(sizer)
        
        # Event bindings
        self.send_button.Bind(wx.EVT_BUTTON, self.on_send)
        self.message_input.Bind(wx.EVT_TEXT_ENTER, self.on_send)
        
        # Hoş geldin mesajı
        self.add_to_chat("Robot", "Merhaba! Benimle sohbet edebilir veya bana yeni şeyler öğretebilirsin.")
    
    def on_send(self, event):
        message = self.message_input.GetValue().strip()
        if not message:
            return
        
        self.add_to_chat("Sen", message)
        self.message_input.SetValue("")
        
        # Robot cevabı
        response = self.chatbot.get_answer(message)
        self.add_to_chat("Robot", response)
    
    def add_to_chat(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_history.AppendText(f"[{timestamp}] {sender}: {message}\n")

class TeachPanel(wx.Panel):
    def __init__(self, parent, chatbot):
        super().__init__(parent)
        self.chatbot = chatbot
        self.init_ui()
        self.refresh_qa_list()
    
    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Sol panel - Öğretme
        left_panel = wx.Panel(self)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        left_sizer.Add(wx.StaticText(left_panel, label="Robota Yeni Şeyler Öğret:"), 0, wx.ALL, 5)
        
        # Soru girişi
        left_sizer.Add(wx.StaticText(left_panel, label="Soru:"), 0, wx.ALL, 5)
        self.question_input = wx.TextCtrl(left_panel, style=wx.TE_MULTILINE, size=(300, 80))
        left_sizer.Add(self.question_input, 0, wx.EXPAND | wx.ALL, 5)
        
        # Cevap girişi
        left_sizer.Add(wx.StaticText(left_panel, label="Cevap:"), 0, wx.ALL, 5)
        self.answer_input = wx.TextCtrl(left_panel, style=wx.TE_MULTILINE, size=(300, 100))
        left_sizer.Add(self.answer_input, 0, wx.EXPAND | wx.ALL, 5)
        
        # Öğret butonu
        self.teach_button = wx.Button(left_panel, label="Öğret")
        left_sizer.Add(self.teach_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        left_panel.SetSizer(left_sizer)
        
        # Sağ panel - Öğrenilen şeyler
        right_panel = wx.Panel(self)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        right_sizer.Add(wx.StaticText(right_panel, label="Öğrenilen Soru-Cevap Çiftleri:"), 0, wx.ALL, 5)
        
        # Liste
        self.qa_list = wx.ListCtrl(right_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.qa_list.AppendColumn("Soru", width=200)
        self.qa_list.AppendColumn("Cevap", width=250)
        
        right_sizer.Add(self.qa_list, 1, wx.EXPAND | wx.ALL, 5)
        
        # Yenile butonu
        self.refresh_button = wx.Button(right_panel, label="Listeyi Yenile")
        right_sizer.Add(self.refresh_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Sil butonu
        self.delete_button = wx.Button(right_panel, label="Seçili Öğeyi Sil")
        right_sizer.Add(self.delete_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        right_panel.SetSizer(right_sizer)
        
        # Ana sizer'a ekle
        main_sizer.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Event bindings
        self.teach_button.Bind(wx.EVT_BUTTON, self.on_teach)
        self.refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh)
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
    
    def on_teach(self, event):
        question = self.question_input.GetValue().strip()
        answer = self.answer_input.GetValue().strip()
        
        if not question or not answer:
            wx.MessageBox("Lütfen hem soru hem de cevap girin!", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        # Öğret
        self.chatbot.learn(question, answer)
        
        # Alanları temizle
        self.question_input.SetValue("")
        self.answer_input.SetValue("")
        
        # Listeyi yenile
        self.refresh_qa_list()
        
        wx.MessageBox("Yeni bilgi başarıyla öğretildi!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
    
    def on_refresh(self, event):
        self.chatbot.load_knowledge()  # Tüm dosyalardan yeniden yükle
        self.refresh_qa_list()
        wx.MessageBox("Liste yenilendi!", "Bilgi", wx.OK | wx.ICON_INFORMATION)
    
    def on_delete(self, event):
        selected = self.qa_list.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Lütfen silinecek bir öğe seçin!", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        question = self.qa_list.GetItemText(selected)
        
        # Onay al
        dlg = wx.MessageDialog(self, f"'{question}' sorusunu silmek istediğinizden emin misiniz?", 
                              "Silme Onayı", wx.YES_NO | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            # Silme işlemi (sadece ana dosyadan)
            try:
                if os.path.exists(self.chatbot.json_file):
                    with open(self.chatbot.json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if question.lower() in data:
                        del data[question.lower()]
                        
                        with open(self.chatbot.json_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        self.chatbot.load_knowledge()
                        self.refresh_qa_list()
                        wx.MessageBox("Öğe başarıyla silindi!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
                    else:
                        wx.MessageBox("Bu öğe ana dosyada bulunamadı!", "Uyarı", wx.OK | wx.ICON_WARNING)
            except Exception as e:
                wx.MessageBox(f"Silme hatası: {e}", "Hata", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def refresh_qa_list(self):
        self.qa_list.DeleteAllItems()
        qa_pairs = self.chatbot.get_all_qa_pairs()
        
        for i, (question, answer) in enumerate(qa_pairs.items()):
            index = self.qa_list.InsertItem(i, question)
            # Cevabı kısalt
            short_answer = answer[:100] + "..." if len(answer) > 100 else answer
            self.qa_list.SetItem(index, 1, short_answer)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Öğrenebilen Sohbet Robotu", size=(800, 600))
        
        self.chatbot = ChatBot()
        self.init_ui()
        self.Center()
    
    def init_ui(self):
        # Notebook (sekmeler)
        notebook = wx.Notebook(self)
        
        # Sohbet sekmesi
        chat_panel = ChatPanel(notebook, self.chatbot)
        notebook.AddPage(chat_panel, "Sohbet")
        
        # Öğretme sekmesi
        teach_panel = TeachPanel(notebook, self.chatbot)
        notebook.AddPage(teach_panel, "Robota Öğret")
        
        # Ana sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        # Menü çubuğu
        self.create_menu()
    
    def create_menu(self):
        menubar = wx.MenuBar()
        
        # Dosya menüsü
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_ABOUT, "&Hakkında")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "&Çıkış")
        
        menubar.Append(file_menu, "&Dosya")
        self.SetMenuBar(menubar)
        
        # Event bindings
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
    
    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("Öğrenebilen Sohbet Robotu")
        info.SetVersion("1.0")
        info.SetDescription("wxPython ile geliştirilmiş öğrenebilen sohbet uygulaması")
        wx.adv.AboutBox(info)
    
    def on_exit(self, event):
        self.Close()

class ChatBotApp(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = ChatBotApp()
    app.MainLoop()