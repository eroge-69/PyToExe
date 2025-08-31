import requests
from bs4 import BeautifulSoup
import re
from email.header import decode_header

while True:
    user_input = input("Mail ve Şifreyi Gir: ").strip()
    EMAIL_ACCOUNT, EMAIL_PASSWORD = user_input.split(":", 1)  # mail:password ayrıştırma

    # API isteği
    url = "https://api.firstmail.ltd/v1/mail/one?username="+EMAIL_ACCOUNT+"&password="+EMAIL_PASSWORD
    headers = {
        "accept": "application/json",
        "X-API-KEY": "ed54088b-3645-478f-93b6-0e71bb5bac82"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Mail içeriğini al
        html_content = data.get('html', '')  # HTML içeriği 'html_body' içinde

        if html_content:
            # BeautifulSoup ile HTML'yi parse et
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Doğrulama kodunu alacak bir regex oluşturuyoruz
            # Genellikle doğrulama kodları 6 haneli rakamlar olabilir
            code = None
            match = re.search(r'\b\d{6}\b', html_content)  # 6 haneli doğrulama kodunu bul

            if match:
                code = match.group(0)
                print("Doğrulama Kodu:", code)
            else:
                print("Doğrulama kodu bulunamadı.")
        else:
            print("Mailde HTML içeriği bulunamadı.")
    else:
        print("API isteği başarısız oldu.")
        print(response.text)
