import requests
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)


def rest(user_email):
    try:
        ua = UserAgent()
        user_agent = ua.random
        
        headers = {
            'X-Pigeon-Session-Id': '50cc6861-7036-43b4-802e-fb4282799c60',
            'X-Pigeon-Rawclienttime': '1700251574.982',
            'X-IG-Connection-Speed': '-1kbps',
            'X-IG-Bandwidth-Speed-KBPS': '-1.000',
            'X-IG-Bandwidth-TotalBytes-B': '0',
            'X-IG-Bandwidth-TotalTime-MS': '0',
            'X-Bloks-Version-Id': 'c80c5fb30dfae9e273e4009f03b18280bb343b0862d663f31a3c63f13a9f31c0',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Capabilities': '3brTvw==',
            'X-IG-App-ID': '567067343352427',
            'User-Agent': user_agent,
            'Accept-Language': 'en-GB, en-US',
            'Cookie': 'mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'i.instagram.com',
            'X-FB-HTTP-Engine': 'Liger',
            'Connection': 'keep-alive',
            'Content-Length': '356',
        }
        
        data = {
            'signed_body': '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.{"_csrftoken":"9y3N5kLqzialQA7z96AMiyAKLMBWpqVj","adid":"0dfaf820-2748-4634-9365-c3d8c8011256","guid":"1f784431-2663-4db9-b624-86bd9ce1d084","device_id":"android-b93ddb37e983481c","query":"'+user_email+'"}',
            'ig_sig_key_version': '4',
        }

        response = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/', headers=headers, data=data).json()

        if response.get('email'):
            return "available"
        else:
            return "bad"
    
    except Exception as e:
        return f'Error occurred: {e}'


with open('emails.txt', 'r') as file:
    emails = file.readlines()

emails = [email.strip() for email in emails if email.strip()]
emails = list(set(emails))  


def check_emails():
    with open('available_accounts.txt', 'a') as available_file:
        with ThreadPoolExecutor(max_workers=10) as executor:
            for result in executor.map(rest, emails):
                email = emails.pop(0)
                if result == "available":
                    print(f"{Fore.GREEN}{email} available")
                    available_file.write(f"{email}\n")
                elif result == "bad":
                    print(f"{Fore.RED}{email} bad")
                else:
                    print(f"{email} {result}")

if __name__ == "__main__":
    check_emails()

input("Press Enter to exit...")
