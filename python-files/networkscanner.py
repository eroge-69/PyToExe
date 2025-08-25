import os
import time
from datetime import datetime

class SimpleNetworkMonitor:
    def __init__(self):
        self.activities = []
        
    def monitor_network(self):
        """Egyszerű hálózati monitor"""
        print("🌐 Egyszerű hálózati monitor")
        print("=" * 40)
        
        try:
            while True:
                # Szimulált adatok (valós implementáció helyett)
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Képernyő törlése
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print(f"🕒 Idő: {current_time}")
                print("=" * 40)
                print("📱 Aktív eszközök és tevékenységek:")
                print("⎯" * 40)
                
                # Szimulált eszközök
                devices = [
                    {"name": "Android-Telefon", "site": "google.com", "time": "45s"},
                    {"name": "Laptop", "site": "youtube.com", "time": "12m"},
                    {"name": "Tablet", "site": "facebook.com", "time": "3m"},
                    {"name": "OkosTV", "site": "netflix.com", "time": "1h"}
                ]
                
                for device in devices:
                    print(f"• {device['name']}: {device['site']} ({device['time']})")
                
                print("\n" + "=" * 40)
                print("ℹ️  Valós implementációhoz admin jogosultság szükséges")
                print("⏹️  Ctrl+C a kilépéshez")
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n✅ Monitorozás leállítva")

# Futtatás
if __name__ == "__main__":
    monitor = SimpleNetworkMonitor()
    monitor.monitor_network()