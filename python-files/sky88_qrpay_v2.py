import shutil
import requests
import base64
import random
from PIL import Image
from io import BytesIO
import webview, time
import os

def generate_username():
    first_names = [
        "ly", "vu", "ha", "truong", "luu", "trinh", "cao", "tang", "doan", "luong", 
        "mai", "to", "ho", "lai", "ta", "mac", "kieu", "phung", "tong", "quach"
    ]

    mid_names = [
        "hong", "anh", "thuy", "huong", "phuong", "van", "duc", "thi", "dinh", "tuan", 
        "quoc", "thai", "duc", "tan", "thi", "gia", "hoang", "manh", "duy", "trung", 
        "vu", "quang", "huu", "minh", "tien", "dai", "xuan", "cam"
    ]

    last_names = [
        "hung", "tuong", "khanh", "han", "bich", "thien", "khang", "bach", "dung", "vinh", 
        "loan", "thang", "kim", "nhung", "lan", "khue", "binh", "nga", "long", "quan", 
        "trang", "duc", "mai", "kiet", "minh", "tuan", "nhi", "thuy", "truong", "minh"
    ]

    last_name = random.choice(last_names)
    mid_name = random.choice(mid_names)
    first_name = random.choice(first_names)
    number = random.randint(100, 9999)
    username_patterns = [
        f"{last_name}{mid_name}{number}",
        f"{last_name}{first_name}{number}",
        f"{first_name}{mid_name}{number}",
        f"{first_name}{last_name}{number}",
        f"{mid_name}{first_name}{number}",
        f"{mid_name}{last_name}{number}"
    ]
    username = random.choice(username_patterns)
    return username[:14]

def generate_phone():
    prefixes = ["09", "03", "07", "08", "05"]
    prefix = random.choice(prefixes) + str(random.randint(0, 9))
    number = "".join(str(random.randint(0, 9)) for _ in range(7))
    return prefix + number

with open("pass.txt", "r") as file:
    password = file.read()
    
def on_loaded(window):

    time.sleep(10)
    js_code = '''
        const container = document.createElement("div");
        container.id = "cf-login-turnstile";
        container.className = "cf-turnstile";
        container.setAttribute("data-sitekey", "0x4AAAAAAA_kx307YPqrEuNE");
        document.body.appendChild(container);
    '''
    window.evaluate_js(js_code)

    amount = int(input("Nhập số tiền muốn nạp (50=50k,60=60k,70=70k...) : ")) * 1000

    if os.path.exists("qr_code"):
        shutil.rmtree("qr_code")

    with open("proxies.txt", "r") as file:
        proxies_list = [line.strip() for line in file if line.strip()]  
    for proxy in proxies_list:
        try:

            with open("key.txt", "r") as file:
                key = file.read()
            print(f"Đang giải capcha")
            token = get_token(window)
            username = generate_username()
            print(f"Đang đăng ký tài khoản {username} ...")

            payload = {
                "key": key,
                "username": username,
                "password": password,
                "phone_number": generate_phone(),
                "fullname": generate_username(),
                "amount": amount,
                "token": token,
                "proxy": proxy
            }
            response = requests.post("http://127.0.0.1:1000/reg-acc-sky88", json=payload)
            if response.text == "INVALID":
                print("Key ko hợp lệ, vui lòng kiểm tra lại.")
                input("Nhấn Enter để thoát...")
                exit()
            data = response.json()
            if data.get('status') == 'success':
                with open("taikhoan.txt", "a") as f:
                    f.write(f"{data.get('username', '')}|{data.get('password', '')}|{data.get('token', '')}|{data.get('gptoken', '')}|{data.get('invoice_code', '')}\n")
                qr_code_base64 = data.get('qr_code_base64', None)
                if qr_code_base64:
                    image_data = base64.b64decode(qr_code_base64)
                    image = Image.open(BytesIO(image_data))
                    os.makedirs("qr_code", exist_ok=True)
                    image_path = os.path.join("qr_code", f"{data.get('username', '')}_{data.get('bank_code', '')}.png")
                    image.save(image_path)
                    print('Đã lưu QR nạp tiền !')

        except:
            print(response.text)

    input("Đã tạo xong")

def get_token(window):
    js_code = '''
        window.token = null;
        turnstile.render("#cf-login-turnstile", {
            sitekey: "0x4AAAAAAA_kx307YPqrEuNE",
            callback: function(t) {
                console.log("Token nhận được: ", t);
                window.token = t;
            }
        });
    '''
    window.evaluate_js(js_code)

    for _ in range(30):
        token = window.evaluate_js("window.token")
        if token:
            return token
        time.sleep(1)

if __name__ == "__main__":
    with open("key.txt", "r") as file:
        key = file.read()
    payload = {
        "key": key
    }
    response = requests.post("http://127.0.0.1:1000/verify-key-sky88", json=payload)
    if response.text == "VALID":
        print("Đang chuẩn bị ...")
        window = webview.create_window("sky88.com", "https://sky88.com/", hidden=False, width=10, height=10, x=0, y=0)
        webview.start(on_loaded, window)
    else:
        print("Key ko hợp lệ, vui lòng kiểm tra lại.")
        input("Nhấn Enter để thoát...")
        exit()