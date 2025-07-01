#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import webbrowser
import os
import time

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Ozellestirilmis HTTP istek isleyicisi"""
    
    def end_headers(self):
        # CORS basliklarini ekle
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Laser Control Program HTML dosyasini calistir"""
    
    PORT = 8000
    HTML_FILE = "laser_control_program.html"
    
    # HTML dosyasinin varligini kontrol et
    if not os.path.exists(HTML_FILE):
        print(f"HATA: '{HTML_FILE}' dosyasi bulunamadi!")
        print(f"Mevcut dizin: {os.getcwd()}")
        print(f"Lutfen {HTML_FILE} dosyasinin bu dizinde oldugunden emin olun.")
        return
    
    print("Laser Control Program Baslatiliyor...")
    print(f"Dosya: {HTML_FILE}")
    print(f"Port: {PORT}")
    
    try:
        # HTTP sunucusunu baslat
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            server_url = f"http://localhost:{PORT}/{HTML_FILE}"
            
            print(f"\nSunucu basariyla baslatildi!")
            print(f"URL: {server_url}")
            print("\nSunucuyu durdurmak icin Ctrl+C tushlarina basin")
            
            # 1 saniye bekle ve tarayicide ac
            print(f"Tarayici aciliyor...")
            time.sleep(1)
            webbrowser.open(server_url)
            
            print("\n" + "="*60)
            print("LASER CONTROL PROGRAM CALISIYOR")
            print("="*60)
            
            # Sunucuyu calistir
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"HATA: Port {PORT} zaten kullanimda!")
            print(f"Baska bir port icin kodu duzenleyin veya calisan sunucuyu durdurun.")
        else:
            print(f"Sunucu hatasi: {e}")
    except KeyboardInterrupt:
        print("\n\nLaser Control Program durduruldu!")
        print("Guvenli bir sekilde cikis yapildi.")

if __name__ == "__main__":
    main()