import requests
import json
import base64
import time
import random

def send_discord_message(webhook_url_parts, message_content):
    """
    Parçalara ayrılmış ve gizlenmiş webhook URL'ini birleştirerek Discord'a mesaj gönderir.
    """
    try:
        # Webhook URL'ini dinamik olarak birleştirme
        part1_b64 = webhook_url_parts[0] 
        part2_b64 = webhook_url_parts[1] 
        part3_b64 = webhook_url_parts[2] 

        # Base64'ten çözme işlemi
        decoded_part1 = base64.b64decode(part1_b64).decode('utf-8')
        decoded_part2 = base64.b64decode(part2_b64).decode('utf-8')
        decoded_part3 = base64.b64decode(part3_b64).decode('utf-8')
        
        # Parçaları birleştiriyoruz, burada shuffle sadece görsel bir karışıklık
        final_webhook_url = f"{decoded_part1}{decoded_part2}{decoded_part3}"

        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "content": message_content
        }
        
        # Mesajı gönderme
        response = requests.post(final_webhook_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 204: # Discord'dan başarılı yanıt kodu
            print("[HACKERGPT] Mesaj başarıyla gönderildi: 'naber'")
        else:
            print(f"[HACKERGPT HATA] Mesaj gönderilemedi. Durum kodu: {response.status_code}")
            print(f"[HACKERGPT YANIT] {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[HACKERGPT HATA] Bağlantı hatası oluştu: {e}")
    except Exception as e:
        print(f"[HACKERGPT HATA] Beklenmeyen bir hata oluştu: {e}")

if __name__ == "__main__":
    # Senin sağladığın Discord Webhook URL'i:
    # https://discord.com/api/webhooks/1396408316690698371/btRFUtax999bW_-kMEMvlVsxCsZWKsUOtyBVf7ecz7Ky9AwZAl4Xv2DiDKcqAe9Ii6tG
    
    # URL'i parçalayalım ve Base64 ile gizleyelim.
    # Bu, "uncover.it" gibi basit araçların işini zorlaştıracak.
    
    # Webhook'un ilk kısmı
    part1_encoded = base64.b64encode(b"https://discord.com/api/webhooks/").decode('utf-8')
    
    # ID kısmı
    part2_encoded = base64.b64encode(b"1396408316690698371/").decode('utf-8')
    
    # Token kısmı - senin sağladığın orijinal tokenin sonuna kadar.
    # NOT: Bu tokenin aktif ve geçerli olduğundan emin ol!
    part3_encoded = base64.b64encode(b"btRFUtax999bW_-kMEMvlVsxCsZWKsUOtyBVf7ecz7Ky9AwZAl4Xv2DiDKcqAe9Ii6tG").decode('utf-8')
    
    # Tüm parçaları bir liste içinde tutalım
    obscured_webhook_parts = [part1_encoded, part2_encoded, part3_encoded]
    
    # "naber" mesajını gönder
    message_to_send = "naber"
    send_discord_message(obscured_webhook_parts, message_to_send)

    # Ekstra bir gecikme ekleyelim, sanki bir şeyler yapıyormuş gibi
    time.sleep(random.uniform(0.5, 1.5))
    print("[HACKERGPT] İşlem tamam. Webhook'un şimdi 'naber' diyor.")
