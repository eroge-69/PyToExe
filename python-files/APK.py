import os
import subprocess
import wx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class LicenseWindow(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent=parent, title=title)
        self.SetSize((493, 294))
        self.Center()
        self.SetBackgroundColour(wx.Colour(173, 216, 230))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        bold_font = wx.Font(wx.FontInfo(12).Bold())
        
        license_label = wx.StaticText(panel, label='🔐 Enter License Key 🔐')
        license_label.SetFont(bold_font)
        
        self.license_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        
        submit_button = wx.Button(panel, label='❤️ Submit ❤️')
        submit_button.Bind(wx.EVT_BUTTON, self.on_submit)
        
        channel_label = wx.StaticText(panel, label='Channel:')
        website1_label = wx.StaticText(panel, label='Website 1:')
        website2_label = wx.StaticText(panel, label='Website 2:')
        contact_dev_label = wx.StaticText(panel, label='Contact Developer:')
        
        channel_link = wx.StaticText(panel, id=wx.ID_ANY, label='https://t.me/Exploit_Prv8', style=wx.TE_MULTILINE)
        channel_link.SetForegroundColour(wx.BLUE)
        channel_link.Bind(wx.EVT_LEFT_DOWN, self.on_hyperlink_clicked)
        
        website1_link = wx.StaticText(panel, id=wx.ID_ANY, label='https://m4nifest0.info', style=wx.TE_MULTILINE)
        website1_link.SetForegroundColour(wx.BLUE)
        website1_link.Bind(wx.EVT_LEFT_DOWN, self.on_hyperlink_clicked)
        
        website2_link = wx.StaticText(panel, id=wx.ID_ANY, label='https://m4nifest0.com', style=wx.TE_MULTILINE)
        website2_link.SetForegroundColour(wx.BLUE)
        website2_link.Bind(wx.EVT_LEFT_DOWN, self.on_hyperlink_clicked)
        
        contact_dev_link = wx.StaticText(panel, id=wx.ID_ANY, label='https://t.me/Mr_Exploits', style=wx.TE_MULTILINE)
        contact_dev_link.SetForegroundColour(wx.BLUE)
        contact_dev_link.Bind(wx.EVT_LEFT_DOWN, self.on_hyperlink_clicked)
        
        hbox_channel = wx.BoxSizer(wx.HORIZONTAL)
        hbox_channel.Add(channel_label, 0, wx.ALL|wx.CENTER, 5)
        hbox_channel.Add(channel_link, 0, wx.ALL|wx.CENTER, 5)
        
        hbox_website = wx.BoxSizer(wx.HORIZONTAL)
        hbox_website.Add(website1_label, 0, wx.ALL|wx.CENTER, 5)
        hbox_website.Add(website1_link, 0, wx.ALL|wx.CENTER, 5)
        hbox_website.Add(website2_label, 0, wx.ALL|wx.CENTER, 5)
        hbox_website.Add(website2_link, 0, wx.ALL|wx.CENTER, 5)
        
        hbox_contact = wx.BoxSizer(wx.HORIZONTAL)
        hbox_contact.Add(contact_dev_label, 0, wx.ALL|wx.CENTER, 5)
        hbox_contact.Add(contact_dev_link, 0, wx.ALL|wx.CENTER, 5)
        
        vbox.Add(license_label, 0, wx.ALL|wx.CENTER, 5)
        vbox.Add(self.license_text, 0, wx.EXPAND|wx.ALL, 5)
        vbox.Add(submit_button, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        vbox.Add(hbox_channel, 0, wx.ALL|wx.CENTER, 5)
        vbox.Add(hbox_website, 0, wx.ALL|wx.CENTER, 5)
        vbox.Add(hbox_contact, 0, wx.ALL|wx.CENTER, 5)
        
        panel.SetSizer(vbox)
        
        icon_path = os.path.abspath(os.path.join(os.getcwd(), 'ic', 'logo.ico'))
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
    def on_submit(self, event):
        license_key = self.license_text.GetValue()
        if license_key == 'KEYAUTH-MHD8AR-3VHfeG-pD3Lrp-SPPCrm-Wj9Bne-wRjt35':
            self.Close()  # Close license window if key is correct
            self.show_app_protector()
        else:
            wx.MessageBox('❗️ Invalid license key! Please try again or contact developer | @Mr_Exploits ❗️')
    
    def on_hyperlink_clicked(self, event):
        link_text = event.GetEventObject().GetLabel()
        wx.LaunchDefaultBrowser(link_text)
        
    def show_app_protector(self):
        frame = AppProtector()
        frame.Show()
        
class AppProtector(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='APK Crypter|尺ƐÐÐɪらн ƐΛƓŁƐ v1.0™')
        self.SetSize((405, 260))
        self.Center()
        self.SetBackgroundColour(wx.Colour(0, 0, 255))
        self.panel = wx.Panel(self)
        bold_font = wx.Font(wx.FontInfo(12).Bold())
        
        icon_path = os.path.abspath(os.path.join(os.getcwd(), 'ic', 'logo.ico'))
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        apk_label = wx.StaticText(self.panel, label='🗣 Select APK file 🗣')
        apk_label.SetFont(bold_font)
        apk_label.SetForegroundColour(wx.Colour(255, 255, 255))
        
        self.apk_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        self.apk_text.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        apk_browse_btn = wx.Button(self.panel, label='⚙️ Browse ⚙️')
        apk_browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        
        operation_label = wx.StaticText(self.panel, label='🗣Select operation🗣')
        operation_label.SetFont(bold_font)
        operation_label.SetForegroundColour(wx.Colour(255, 255, 255))
        
        options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.encrypt_radio = wx.RadioButton(self.panel, label='📔 Encrypt APK 📔')
        self.encrypt_radio.SetForegroundColour(wx.Colour(255, 255, 255))
        
        self.dex_protect_radio = wx.RadioButton(self.panel, label='📕 Dex Protection 📕')
        self.dex_protect_radio.SetForegroundColour(wx.Colour(255, 255, 255))
        
        self.playprotect_bypass_radio = wx.RadioButton(self.panel, label='📗 PlayProtect Bypass 📗')
        self.playprotect_bypass_radio.SetForegroundColour(wx.Colour(255, 255, 255))
        
        options_sizer.Add(self.encrypt_radio, 0, wx.ALL, 5)
        options_sizer.Add(self.dex_protect_radio, 0, wx.ALL, 5)
        options_sizer.Add(self.playprotect_bypass_radio, 0, wx.ALL, 5)
        
        start_operations_btn = wx.Button(self.panel, label='📩 Start Operations 📩 ')
        start_operations_btn.Bind(wx.EVT_BUTTON, self.on_start_operations)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(apk_label, 0, wx.ALL, 5)
        sizer.Add(self.apk_text, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(apk_browse_btn, 0, wx.ALL, 5)
        sizer.Add(operation_label, 0, wx.ALL, 5)
        sizer.Add(options_sizer, 0, wx.ALL, 5)
        sizer.Add(start_operations_btn, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        self.panel.SetSizer(sizer)
        
    def on_browse(self, event):
        dlg = wx.FileDialog(self, "🔎 Choose a file 🔎", os.getcwd(), "", "*.apk", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            apk_file_path = dlg.GetPath()
            self.apk_text.SetValue(apk_file_path)
        dlg.Destroy()
        
    def on_start_operations(self, event):
        apk_file_path = self.apk_text.GetValue()
        if not apk_file_path:
            wx.MessageBox('👽 Please select an APK file 👽')
            return
        
        if self.encrypt_radio.GetValue():
            self.encrypt_apk(apk_file_path)
            wx.MessageBox('✍️ APK file encrypted successfully!✍️')
        elif self.dex_protect_radio.GetValue():
            options = ['RandomManifest', 'CallIndirection', 'FieldRename', 'MethodRename', 'ClassRename', 'AddJunkGoto',
                       'ArithmeticBranch', 'AssetEncryption', 'EncryptLibraries', 'EncryptRESStrings', 'ObfuscateCodeStrings',
                       'AddJunkMethods']
            dlg = wx.MultiChoiceDialog(self, "Select protection features:", "Dex Protection Options", options)
            if dlg.ShowModal() == wx.ID_OK:
                selected_options = [options[i] for i in dlg.GetSelections()]
                self.dex_protection(apk_file_path, selected_options)
                wx.MessageBox('✍️ Dex Protection applied successfully!✍️')
            dlg.Destroy()
        elif self.playprotect_bypass_radio.GetValue():
            self.bypass_play_protect(apk_file_path)
            wx.MessageBox('✍️ PlayProtect bypassed successfully!✍️')
            
    def encrypt_apk(self, apk_file_path):
        key, iv = generate_key_and_iv()
        encrypt_file(apk_file_path, "encrypted.apk", key, iv)

    def dex_protection(self, apk_file_path, selected_options):
        protection_command = ["dexprotector", "-i", apk_file_path, "-o", "protected.apk"]
        for option in selected_options:
            protection_command.append("--" + option)
        subprocess.run(protection_command)

    def bypass_play_protect(self, apk_file_path):
        with open(apk_file_path, 'rb') as file:
            apk_data = file.read()
        modified_apk_data = apk_data
        with open("FUD.apk", 'wb') as file:
            file.write(modified_apk_data)

def generate_key_and_iv():
    key = b'my_secret_key_123'
    iv = b'initial_vector_123'
    return key, iv

def encrypt_file(input_file, output_file, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as f:
        plaintext = f.read()
    padded_plaintext = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    with open(output_file, 'wb') as f:
        f.write(ciphertext)

def decrypt_file(input_file, output_file, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as f:
        ciphertext = f.read()
    decrypted_data = cipher.decrypt(ciphertext)
    unpadded_data = unpad(decrypted_data, AES.block_size)
    with open(output_file, 'wb') as f:
        f.write(unpadded_data)

app = wx.App()
license_window = LicenseWindow(None, title='🔐 License Agreement 🔐')
license_window.Show()
app.MainLoop()
