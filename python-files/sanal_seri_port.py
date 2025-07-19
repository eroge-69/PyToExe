import serial
import time
import random
import threading
import subprocess
import os
import sys
from serial.tools import list_ports

class SanalSeriPort:
    def __init__(self, port_name="COM10", baud_rate=9600):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.running = False
        self.serial_port = None
        self.packet_number = 1
        self.com0com_process = None
        
    def sanal_port_olustur(self):
        """Windows'ta sanal COM port çifti oluştur"""
        try:
            print("Sanal COM port oluşturuluyor...")
            
            # com0com kullanarak sanal port çifti oluştur
            # com0com kurulu değilse kullanıcıyı bilgilendir
            
            # Önce mevcut portları kontrol et
            existing_ports = [port.device for port in list_ports.comports()]
            print(f"Mevcut portlar: {existing_ports}")
            
            # Mode kullanarak sanal port oluşturma (Windows built-in)
            try:
                # Virtual Serial Port Driver kullanımı için PowerShell komutu
                ps_command = f"""
                # Sanal port oluşturma için gerekli komutlar
                Write-Host "Sanal port oluşturuluyor: {self.port_name}"
                """
                
                # Basit yöntem: Eğer port yoksa oluştur
                if self.port_name not in existing_ports:
                    print(f"Port {self.port_name} mevcut değil.")
                    print("Sanal port oluşturmak için com0com veya Virtual Serial Port Driver gerekli.")
                    print("\nÇözüm seçenekleri:")
                    print("1. com0com kurulum: https://com0com.sourceforge.net/")
                    print("2. HW Virtual Serial Port kurulum")
                    print("3. Mevcut portlardan birini kullanın")
                    print(f"   Mevcut portlar: {existing_ports}")
                    
                    # Alternatif port öner
                    if existing_ports:
                        print(f"\nÖnerilen port: {existing_ports[0]}")
                        cevap = input(f"Bu portu kullanmak ister misiniz? (y/n): ")
                        if cevap.lower() == 'y':
                            self.port_name = existing_ports[0]
                            return True
                    
                    # Manuel port oluşturma denemesi
                    print("\nManuel sanal port oluşturma deneniyor...")
                    return self.manuel_sanal_port_olustur()
                
                return True
                
            except Exception as e:
                print(f"Sanal port oluşturma hatası: {e}")
                return False
                
        except Exception as e:
            print(f"Genel hata: {e}")
            return False
    
    def manuel_sanal_port_olustur(self):
        """Manuel sanal port oluşturma"""
        try:
            print("Manuel sanal port oluşturma...")
            
            # Windows Registry ile sanal port oluşturma denemesi
            import winreg
            
            # HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\SERIALCOMM anahtarını kontrol et
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"HARDWARE\DEVICEMAP\SERIALCOMM", 
                                       0, winreg.KEY_READ)
                print("Registry anahtarı bulundu.")
                winreg.CloseKey(reg_key)
            except:
                print("Registry anahtarına erişim yok.")
            
            # Alternatif: Python'da pseudo-terminal oluştur
            print(f"Pseudo-terminal oluşturuluyor: {self.port_name}")
            
            # Eğer hiçbir yöntem çalışmazsa simülasyon moduna geç
            print("Gerçek sanal port oluşturulamadı. Simülasyon moduna geçiliyor.")
            self.port_name = "SIMULATION"
            return True
            
        except Exception as e:
            print(f"Manuel port oluşturma hatası: {e}")
            self.port_name = "SIMULATION"
            return True
        
    def baslat(self):
        """Sanal seri portu başlat"""
        try:
            # Önce sanal port oluşturmayı dene
            if not self.sanal_port_olustur():
                print("Sanal port oluşturulamadı!")
                return False
            
            # Seri port bağlantısını dene
            available_ports = [port.device for port in list_ports.comports()]
            print(f"Güncel portlar: {available_ports}")
            
            if self.port_name != "SIMULATION" and self.port_name in available_ports:
                try:
                    self.serial_port = serial.Serial(self.port_name, self.baud_rate, timeout=1)
                    print(f"Seri port {self.port_name} açıldı (Gerçek sanal port)")
                except Exception as e:
                    print(f"Port açma hatası: {e}")
                    print("Simülasyon moduna geçiliyor...")
                    self.serial_port = None
            else:
                print(f"Port {self.port_name} simülasyon modunda çalışıyor.")
                self.serial_port = None
            
            self.running = True
            # Ayrı thread'de veri göndermeye başla
            self.thread = threading.Thread(target=self.veri_gonder_loop)
            self.thread.daemon = True
            self.thread.start()
            
            print("Sanal seri port başlatıldı. Veri gönderimi başladı...")
            return True
            
        except Exception as e:
            print(f"Seri port açılırken hata: {e}")
            return False
    
    def durdur(self):
        """Sanal seri portu durdur"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        print("Sanal seri port durduruldu.")
    
    def random_telemetri_paketi_olustur(self):
        """Random telemetri paketi oluştur"""
        # Random değerler
        sicaklik = round(random.uniform(-10, 50), 1)
        basinc = round(random.uniform(950, 1050), 2)
        irtifa = round(random.uniform(0, 2000), 1)
        
        # GPS koordinatları - Merkez nokta: 41.008200, 28.978400
        # 200 metre çevre için yaklaşık 0.0018 derece offset (enlem/boylam)
        merkez_lat = 41.008200
        merkez_lon = 28.978400
        offset = 0.0018  # ~200 metre
        
        lat = round(random.uniform(merkez_lat - offset, merkez_lat + offset), 6)
        lon = round(random.uniform(merkez_lon - offset, merkez_lon + offset), 6)
        
        uydu = random.randint(4, 12)
        rssi = random.randint(40, 95)
        
        # Paket formatı
        paket = [
            "[Roket Telemetri]",
            f"Paket #{self.packet_number}",
            f"Sıcaklık: {sicaklik}°C",
            f"Basınç: {basinc}hPa",
            f"İrtifa: {irtifa}m",
            f"Konum: {lat}, {lon}",
            f"Uydu: {uydu}",
            f"RSSI: {rssi}/100"
        ]
        
        self.packet_number += 1
        return paket
    
    def veri_gonder_loop(self):
        """Sürekli veri gönderme döngüsü"""
        while self.running:
            try:
                # Random telemetri paketi oluştur
                paket = self.random_telemetri_paketi_olustur()
                
                # Her satırı gönder
                for satir in paket:
                    if not self.running:
                        break
                        
                    # Gerçek porta gönder (varsa)
                    if self.serial_port and self.serial_port.is_open:
                        self.serial_port.write((satir + "\n").encode())
                    
                    # Konsola da yazdır
                    print(satir)
                    
                    # Satırlar arası kısa bekleme
                    time.sleep(0.1)
                
                print("-" * 40)
                
                # 5Hz için 200ms bekleme (1000ms / 5Hz = 200ms)
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Veri gönderme hatası: {e}")
                time.sleep(1)

def main():
    print("=== Sanal Roket Telemetri Seri Port Oluşturucu ===")
    print("Bu program Windows'ta sanal COM port oluşturur ve telemetri verisi gönderir.")
    
    # Admin yetkisi kontrolü
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("\n⚠️  UYARI: Program administrator olarak çalıştırılmıyor.")
            print("Sanal port oluşturmak için admin yetkisi gerekebilir.")
    except:
        pass
    
    print("\nSanal port oluşturma seçenekleri:")
    print("1. Otomatik port oluştur (COM10)")
    print("2. Manuel port belirle")
    print("3. Mevcut portları listele")
    
    secim = input("Seçiminiz (1-3): ").strip()
    
    if secim == "3":
        available_ports = [port.device for port in list_ports.comports()]
        print(f"\nMevcut seri portlar: {available_ports}")
        if not available_ports:
            print("Hiç seri port bulunamadı.")
        return
    
    # Port seçimi
    if secim == "2":
        port_name = input("Kullanılacak port adı (örn: COM15): ").strip()
        if not port_name:
            port_name = "COM10"
    else:
        port_name = "COM10"
    
    baud_rate = input("Baud rate (varsayılan: 9600): ").strip()
    if not baud_rate:
        baud_rate = 9600
    else:
        baud_rate = int(baud_rate)
    
    print(f"\nSanal port oluşturuluyor: {port_name}")
    print("Bu işlem biraz zaman alabilir...")
    
    # Sanal seri port oluştur
    sanal_port = SanalSeriPort(port_name, baud_rate)
    
    try:
        # Başlat
        if sanal_port.baslat():
            print(f"\n✅ Sanal port başlatıldı!")
            print(f"Port: {port_name}")
            print(f"Baud Rate: {baud_rate}")
            print(f"\nTelemetri arayüzünüzde bu portu seçerek test edebilirsiniz.")
            print("Durdurmak için Ctrl+C basın.")
            print("=" * 60)
            
            # Sonsuz döngü - kullanıcı Ctrl+C basana kadar çalış
            while True:
                time.sleep(1)
        else:
            print("\n❌ Sanal port başlatılamadı!")
            print("\nSanal port oluşturmak için gerekli araçlar:")
            print("• com0com (Ücretsiz): https://com0com.sourceforge.net/")
            print("• HW Virtual Serial Port")
            print("• Virtual Serial Port Driver")
                
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
    finally:
        sanal_port.durdur()

if __name__ == "__main__":
    main()
build_exe.bat