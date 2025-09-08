import socket
import threading
import json
import time
import sys
import os
from datetime import datetime
from tkinter import *
from tkinter import messagebox, scrolledtext, ttk
import hashlib
import configparser

class SecureNetworkMessenger:
    def __init__(self):
        # Yapılandırma yükle
        self.load_config()
        
        # Önce kök pencereyi oluştur
        self.root = Tk()
        self.root.withdraw()  # Başlangıçta gizle
        
        # Kullanıcı tipini belirle
        self.is_admin = self.determine_user_type()
        
        if self.is_admin:
            # Yönetici modunda GUI aç
            self.setup_admin_gui()
        else:
            # Normal kullanıcı modunda arka planda çalış
            self.run_in_background()
        
        # Mesaj alıcıyı başlat
        self.start_receiver()
        
        # GUI'yi göster
        if self.is_admin:
            self.root.deiconify()
        else:
            # Arka planda çalışıyorsa ana döngüyü başlat
            self.root.mainloop()

    def determine_user_type(self):
        """Program başladığında kullanıcıya yönetici olup olmadığını sor"""
        choice = messagebox.askquestion("Kullanıcı Tipi", 
                                      "Yönetici olarak mı giriş yapmak istiyorsunuz?\n\n"
                                      "Evet: Mesaj gönderme yetkisi\n"
                                      "Hayır: Sadece mesaj alma", 
                                      icon='question')
        
        if choice == 'yes':
            # Şifre doğrulama
            return self.verify_admin_password()
        return False

    def verify_admin_password(self):
        """Yönetici şifresini doğrula"""
        from tkinter import simpledialog
        
        # 3 deneme hakkı
        for attempt in range(3):
            password = simpledialog.askstring("Yönetici Girişi", 
                                            f"Yönetici Şifresi ({attempt + 1}/3 deneme):",
                                            show='*')
            
            if password is None:  # İptal edildi
                break
                
            if hashlib.sha256(password.encode()).hexdigest() == self.admin_password_hash:
                messagebox.showinfo("Başarılı", "Yönetici olarak giriş yapıldı!")
                return True
            else:
                messagebox.showerror("Hata", "Geçersiz şifre!")
        
        messagebox.showwarning("Uyarı", "Yönetici girişi başarısız. Normal modda açılıyor...")
        return False

    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config_file = "messenger_config.ini"
        
        if not os.path.exists(self.config_file):
            # Varsayılan yapılandırma
            self.config['DEFAULT'] = {
                'port': '9999',
                'admin_password': hashlib.sha256('admin123'.encode()).hexdigest(),
                'run_minimized': 'true',
                'show_notifications': 'true'
            }
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        else:
            self.config.read(self.config_file)
        
        self.server_port = int(self.config['DEFAULT']['port'])
        self.admin_password_hash = self.config['DEFAULT']['admin_password']

    def run_in_background(self):
        """Normal kullanıcı için arka plan çalışma"""
        print("Uygulama arka planda çalışıyor... Mesajlar bekleniyor.")
        # Tepsi ikonu için mesaj
        self.root.title("Ağ Mesajlaşma - Arka Planda")
        self.root.geometry("300x200")
        Label(self.root, text="Uygulama arka planda çalışıyor\n\nGelen mesajlar burada gözükecek", 
              font=("Arial", 10)).pack(pady=50)
        
        # Durum çubuğu
        self.status = Label(self.root, text="Durum: Mesajlar dinleniyor...", relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

    def setup_admin_gui(self):
        """Yönetici için GUI oluştur"""
        self.root.title("Yönetici Mesaj Sistemi - Yönetici Modu")
        self.root.geometry("900x700")
        
        # Başlıkta yönetici olduğunu belirt
        title_frame = Frame(self.root, bg="#2E7D32", height=40)
        title_frame.pack(fill=X)
        Label(title_frame, text="YÖNETİCİ MODU", fg="white", bg="#2E7D32", 
              font=("Arial", 12, "bold")).pack(pady=8)
        
        self.create_admin_interface()

    def create_admin_interface(self):
        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Sekmeleri oluştur
        self.send_frame = Frame(self.notebook)
        self.clients_frame = Frame(self.notebook)
        self.history_frame = Frame(self.notebook)
        self.settings_frame = Frame(self.notebook)
        
        self.notebook.add(self.send_frame, text="📨 Mesaj Gönder")
        self.notebook.add(self.clients_frame, text="📱 Bağlı Cihazlar")
        self.notebook.add(self.history_frame, text="📊 Geçmiş")
        self.notebook.add(self.settings_frame, text="⚙️ Ayarlar")
        
        self.setup_send_tab()
        self.setup_clients_tab()
        self.setup_history_tab()
        self.setup_settings_tab()

    def setup_send_tab(self):
        # IP giriş alanı
        Label(self.send_frame, text="Hedef Bilgisayar IP veya IP Aralığı", 
              font=("Arial", 11, "bold")).pack(pady=5)
        
        ip_frame = Frame(self.send_frame)
        ip_frame.pack(pady=5)
        
        self.ip_range = Entry(ip_frame, width=25)
        self.ip_range.pack(side=LEFT, padx=5)
        self.ip_range.insert(0, "192.168.1.1-10")
        
        Button(ip_frame, text="Ağ Tarası", command=self.scan_network).pack(side=LEFT, padx=5)
        
        # Mesaj alanları
        Label(self.send_frame, text="Mesaj Başlığı").pack(pady=(10, 2))
        self.message_title = Entry(self.send_frame, width=50)
        self.message_title.pack(pady=2)
        self.message_title.insert(0, "Önemli Duyuru!")
        
        Label(self.send_frame, text="Mesaj İçeriği").pack(pady=(10, 2))
        self.message_content = scrolledtext.ScrolledText(self.send_frame, width=60, height=6)
        self.message_content.pack(pady=2)
        self.message_content.insert(END, "Lütfen bu mesajı dikkatle okuyunuz.")
        
        # Gönder butonu
        self.send_button = Button(self.send_frame, text="🚀 Mesajı Gönder", 
                                 command=self.send_messages, bg="#D32F2F", 
                                 fg="white", font=("Arial", 11, "bold"),
                                 height=2)
        self.send_button.pack(pady=15)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(self.send_frame, orient=HORIZONTAL, 
                                       length=500, mode='determinate')
        self.progress.pack(pady=5)
        
        # Log alanı
        Label(self.send_frame, text="Gönderim Logları", font=("Arial", 10, "bold")).pack(pady=5)
        self.send_log = scrolledtext.ScrolledText(self.send_frame, width=80, height=10)
        self.send_log.pack(pady=5)
        self.send_log.config(state=DISABLED)

    def setup_clients_tab(self):
        Label(self.clients_frame, text="Ağdaki Bağlı Cihazlar", 
              font=("Arial", 12, "bold")).pack(pady=5)
        
        Button(self.clients_frame, text="🔍 Cihazları Tara", 
              command=self.scan_network).pack(pady=10)
        
        self.clients_listbox = Listbox(self.clients_frame, width=80, height=20)
        self.clients_listbox.pack(pady=10, padx=10, fill=BOTH, expand=True)
        
        Button(self.clients_frame, text="📤 Seçilene Gönder", 
              command=self.send_to_selected).pack(pady=5)

    def setup_history_tab(self):
        Label(self.history_frame, text="Gönderilen Mesaj Geçmişi", 
              font=("Arial", 12, "bold")).pack(pady=5)
        
        self.history_listbox = Listbox(self.history_frame, width=90, height=25)
        self.history_listbox.pack(pady=10, padx=10, fill=BOTH, expand=True)
        
        self.load_history()

    def setup_settings_tab(self):
        Label(self.settings_frame, text="Sistem Ayarları", 
              font=("Arial", 12, "bold")).pack(pady=5)
        
        # Şifre değiştirme
        pass_frame = Frame(self.settings_frame)
        pass_frame.pack(pady=10, padx=20, fill=X)
        
        Label(pass_frame, text="Yeni Şifre:", font=("Arial", 10)).pack(anchor=W)
        
        pass_subframe = Frame(pass_frame)
        pass_subframe.pack(fill=X, pady=5)
        
        self.new_password = Entry(pass_subframe, width=25, show='*')
        self.new_password.pack(side=LEFT, padx=5)
        
        Button(pass_subframe, text="🔒 Şifreyi Değiştir", 
              command=self.change_password).pack(side=LEFT, padx=5)

    def scan_network(self):
        """Ağ tarama simülasyonu"""
        self.log_send_message("Ağ taranıyor...")
        
        # Simüle edilmiş cihaz listesi
        devices = [
            "192.168.1.1 - Router",
            "192.168.1.2 - Bilgisayar-1 (Çevrimiçi)",
            "192.168.1.3 - Bilgisayar-2 (Çevrimiçi)", 
            "192.168.1.4 - Yazıcı",
            "192.168.1.5 - Bilgisayar-3 (Çevrimdışı)"
        ]
        
        if hasattr(self, 'clients_listbox'):
            self.clients_listbox.delete(0, END)
            for device in devices:
                self.clients_listbox.insert(END, device)
        
        self.log_send_message("Ağ taraması tamamlandı. 5 cihaz bulundu.")

    def send_to_selected(self):
        """Seçilen cihaza mesaj gönder"""
        selection = self.clients_listbox.curselection()
        if selection:
            device = self.clients_listbox.get(selection[0])
            ip = device.split(' - ')[0]
            self.ip_range.delete(0, END)
            self.ip_range.insert(0, ip)
            self.log_send_message(f"{ip} seçildi. Mesajı hazırlayın.")

    def change_password(self):
        new_pass = self.new_password.get()
        if new_pass:
            self.admin_password_hash = hashlib.sha256(new_pass.encode()).hexdigest()
            self.config['DEFAULT']['admin_password'] = self.admin_password_hash
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            messagebox.showinfo("Başarılı", "Şifre başarıyla değiştirildi!")
            self.new_password.delete(0, END)

    def load_history(self):
        sample_data = [
            "2024-01-15 10:30 - Sistem Bakımı (192.168.1.1-10) ✓",
            "2024-01-14 15:45 - Acil Toplantı (192.168.1.5) ✓",
            "2024-01-13 09:20 - Ağ Güncellemesi (192.168.1.2-20) ✓"
        ]
        
        for item in sample_data:
            self.history_listbox.insert(END, item)

    def log_send_message(self, message):
        if hasattr(self, 'send_log'):
            self.send_log.config(state=NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.send_log.insert(END, f"[{timestamp}] {message}\n")
            self.send_log.see(END)
            self.send_log.config(state=DISABLED)

    def send_single_message(self, ip, title, content):
        try:
            message_data = {
                "title": title,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "sender": socket.gethostname(),
                "type": "notification"
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect((ip, self.server_port))
                sock.sendall(json.dumps(message_data).encode('utf-8'))
                
                response = sock.recv(1024)
                return response.decode('utf-8') == "OK"
                
        except Exception as e:
            self.log_send_message(f"✗ {ip} hatası: {str(e)}")
            return False

    def send_messages(self):
        ip_range_text = self.ip_range.get()
        title = self.message_title.get()
        content = self.message_content.get("1.0", END).strip()
        
        if not ip_range_text or not content:
            messagebox.showerror("Hata", "Lütfen IP aralığı ve mesaj girin.")
            return
        
        # IP listesini oluştur
        if '-' in ip_range_text:
            try:
                base_ip = ip_range_text.split('-')[0]
                base_parts = base_ip.split('.')
                range_end = int(ip_range_text.split('-')[1])
                
                ip_list = []
                for i in range(1, range_end + 1):
                    ip = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}"
                    ip_list.append(ip)
            except:
                messagebox.showerror("Hata", "IP aralığı formatı hatalı!")
                return
        else:
            ip_list = [ip_range_text]
        
        total_ips = len(ip_list)
        self.progress['maximum'] = total_ips
        self.progress['value'] = 0
        
        self.log_send_message(f"Toplam {total_ips} IP adresine mesaj gönderiliyor...")
        
        # Her IP için mesaj gönder
        successful = 0
        for ip in ip_list:
            if self.send_single_message(ip, title, content):
                successful += 1
                self.log_send_message(f"✓ {ip} adresine mesaj gönderildi")
            self.progress['value'] += 1
            self.root.update()
        
        self.log_send_message(f"Gönderim tamamlandı. Başarılı: {successful}/{total_ips}")

    def start_receiver(self):
        def receiver_thread():
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                server_socket.bind(('0.0.0.0', self.server_port))
                server_socket.listen(5)
                
                print(f"Mesaj dinleyici {self.server_port} portunda başlatıldı")
                
                while True:
                    try:
                        client_socket, addr = server_socket.accept()
                        client_thread = threading.Thread(
                            target=self.handle_client, 
                            args=(client_socket, addr)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                    except:
                        break
                        
            except Exception as e:
                print(f"Sunucu hatası: {e}")
            finally:
                server_socket.close()
        
        thread = threading.Thread(target=receiver_thread)
        thread.daemon = True
        thread.start()

    def handle_client(self, client_socket, addr):
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if data:
                message_data = json.loads(data)
                
                # Mesajı göster
                if self.is_admin:
                    self.log_send_message(f"Alınan mesaj: {message_data['title']}")
                else:
                    self.show_notification(message_data['title'], message_data['content'])
                
                client_socket.sendall("OK".encode('utf-8'))
                
        except Exception as e:
            print(f"İstemci işleme hatası: {e}")
        finally:
            client_socket.close()

    def show_notification(self, title, message):
        """Mesaj geldiğinde popup göster"""
        popup = Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x200")
        popup.attributes('-topmost', True)
        
        Label(popup, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        Label(popup, text=message, wraplength=380).pack(pady=10, padx=10)
        
        Button(popup, text="Tamam", command=popup.destroy, 
              bg="#2196F3", fg="white", width=10).pack(pady=10)

# Ana çalıştırma
if __name__ == "__main__":
    app = SecureNetworkMessenger()
    app.root.mainloop()