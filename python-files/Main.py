import requests
import json
import time
from recap_token import RecaptchaSolver
from datetime import datetime

class TicketBooking:
    def __init__(self, user_data_file, recaptcha_token):
        self.s = requests.Session()
        self.recaptcha_token = recaptcha_token
        self.load_user_data(user_data_file)
        self.teams = self.initialize_teams()
        self.notified_matches = set()

    def load_user_data(self, user_data_file):
        with open(user_data_file, encoding="utf-8") as f:
            lines = f.read().splitlines()
            self.username = lines[0]
            self.password = lines[1]
            self.search_word = lines[2]

    def initialize_teams(self):
        return {
            'هل': {'team_name': 'الأهلى', 'eng_team': 'Al Ahly FC', 'categoryName': 'Ahly', 'teamid': '77'}
        }

    def find_team_info(self):
        team_info = self.teams['هل']  # نركز على الأهلي فقط
        self.team_name = team_info['team_name']
        self.eng_team = team_info['eng_team']
        self.category_name = team_info['categoryName']
        self.team_id = team_info['teamid']

    def get_headers(self):
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://tazkarti.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }

    def login(self):
        headers = self.get_headers()
        headers.update({'Content-Type': 'application/json'})
        json_data = {
            'Username': self.username,
            'Password': self.password,
            'recaptchaResponse': self.recaptcha_token,
        }
        r = self.s.post('https://tazkarti.com/home/Login', headers=headers, json=json_data).text
        if 'access_token' not in r:
            print("❌ فشل تسجيل الدخول!")
            return False
        return True

    def check_matches_and_notify(self):
        try:
            res = self.s.get('https://tazkarti.com/data/matches-list-json.json', headers=self.get_headers()).text
            matches = json.loads(res)
            for match in matches:
                if (match["teamName1"] == self.eng_team or match["teamName2"] == self.eng_team) and match.get('matchStatus') == 1:
                    match_id = match["matchId"]
                    match_key = f"{match['teamName1']} vs {match['teamName2']}"
                    if match_key in self.notified_matches:
                        continue  # تم الإبلاغ عنه سابقاً

                    r1 = self.s.get(f'https://tazkarti.com/data/TicketPrice-AvailableSeats-{match_id}.json', headers=self.get_headers()).text
                    r1_data = json.loads(r1)

                    available_tickets = []
                    for category in r1_data['data']:
                        if int(self.team_id) == category['teamId'] and category['availableSeats'] > 0:
                            available_tickets.append(category)

                    if available_tickets:
                        message = f"🎟️ تذاكر مباراة الأهلي متاحة الآن!\n"
                        message += f"🆚 {match['teamName1']} vs {match['teamName2']}\n\n"
                        for ticket in available_tickets:
                            message += f"• فئة: {ticket['categoryName']} - عدد المقاعد: {ticket['availableSeats']} - السعر: {ticket['price']} جنيه\n"
                        print(message)
                        self.send_telegram_notification(message)
                        self.notified_matches.add(match_key)
        except Exception as e:
            print(f"⚠️ خطأ أثناء الفحص: {e}")

    def send_telegram_notification(self, message):
        telegram_token = '7914202337:AAH7_T9TNFoMa3X8SfyvzmGFjah3lMhhPAA'  # استبدل بتوكن البوت
        chat_id = '-1002572258171'              # استبدل بـ chat_id للجروب
        url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
        payload = {'chat_id': chat_id, 'text': message}
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("✅ تم إرسال التنبيه عبر Telegram.")
            else:
                print("❌ فشل إرسال التنبيه عبر Telegram.")
        except Exception as e:
            print(f"❌ فشل إرسال التنبيه عبر Telegram: {e}")

if __name__ == '__main__':
    solver = RecaptchaSolver('https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LeypS8dAAAAAGWYer3FgEpGtmlBWBhsnGF0tCGZ&co=aHR0cHM6Ly90YXprYXJ0aS5jb206NDQz&hl=en&v=9pvHvq7kSOTqqZusUzJ6ewaF&size=invisible&cb=376av9ky8egv')
    token = solver.get_token()
    booking = TicketBooking('data.txt', token)

    booking.find_team_info()

    if booking.login():
        last_keep_alive = time.time()
        while True:
            booking.check_matches_and_notify()

            # رسالة اطمئنان كل 3 ساعات
            if time.time() - last_keep_alive >= 3 * 3600:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    booking.send_telegram_notification(f"✅ السكربت يعمل بدون مشاكل.\n🕒 الوقت الحالي: {now}")
                    print("✅ تم إرسال رسالة تأكيد بأن السكربت شغال.")
                except Exception as e:
                    print(f"❌ فشل إرسال رسالة الاطمئنان: {e}")
                last_keep_alive = time.time()

            time.sleep(10)
