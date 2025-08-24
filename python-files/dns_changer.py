import subprocess
import sys
import time
import atexit

class DNSChanger:
    def __init__(self):
        self.interface = self.get_active_interface()
        self.original_dns = self.get_current_dns()
        
    def get_active_interface(self):
        """Lấy interface mạng đang hoạt động"""
        try:
            result = subprocess.run('netsh interface show interface', 
                                  shell=True, capture_output=True, text=True, encoding='utf-8')
            
            for line in result.stdout.split('\n'):
                if 'Connected' in line and 'Loopback' not in line:
                    parts = line.split()
                    if parts and not parts[0].isdigit():
                        return parts[-1]
            
            return "Ethernet"
        except:
            return "Ethernet"
    
    def get_current_dns(self):
        """Lấy DNS hiện tại"""
        try:
            result = subprocess.run(f'netsh interface ipv4 show config name="{self.interface}"', 
                                  shell=True, capture_output=True, text=True, encoding='utf-8')
            
            for line in result.stdout.split('\n'):
                if 'DNS Servers' in line and ':' in line:
                    dns = line.split(':', 1)[1].strip()
                    if dns and dns != 'None':
                        return dns
            return None
        except:
            return None
    
    def set_dns(self, primary_dns, secondary_dns=None):
        """Đặt DNS server"""
        try:
            # Xóa DNS cũ
            subprocess.run(f'netsh interface ipv4 delete dnsservers "{self.interface}" all', 
                          shell=True, capture_output=True)
            
            # Đặt DNS chính
            subprocess.run(f'netsh interface ipv4 set dns name="{self.interface}" static {primary_dns} primary', 
                          shell=True, capture_output=True)
            
            # Đặt DNS phụ nếu có
            if secondary_dns:
                subprocess.run(f'netsh interface ipv4 add dns name="{self.interface}" {secondary_dns} index=2', 
                              shell=True, capture_output=True)
            
            # Flush DNS
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
            
            print(f"✓ DNS: {primary_dns}" + (f", {secondary_dns}" if secondary_dns else ""))
            return True
            
        except Exception as e:
            print(f"✗ Lỗi: {e}")
            return False
    
    def restore_original_dns(self):
        """Khôi phục DNS gốc"""
        if not self.original_dns:
            # Nếu không có DNS gốc, set về DHCP
            subprocess.run(f'netsh interface ipv4 set dns name="{self.interface}" dhcp', 
                          shell=True, capture_output=True)
            print("✓ Đã khôi phục DHCP")
        else:
            # Khôi phục DNS gốc
            self.set_dns(self.original_dns)
            print(f"✓ Đã khôi phục DNS gốc: {self.original_dns}")
        
        # Flush DNS
        subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)

def main():
    # Tạo DNS changer
    changer = DNSChanger()
    
    # Đăng ký hàm restore khi thoát
    atexit.register(changer.restore_original_dns)
    
    # Đặt DNS Cloudflare
    changer.set_dns("1.1.1.1", "1.0.0.1")
    
    print(f"Đang chạy trên {changer.interface}...")
    print("Đóng cửa sổ để khôi phục DNS gốc")
    
    # Giữ chương trình chạy
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐang thoát...")

if __name__ == "__main__":
    main()