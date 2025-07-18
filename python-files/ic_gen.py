import tls_client
import threading
import traceback
import subprocess
import logging
import ezgmail
import random
import names 
import json
import uuid
import time
import sys
from nextcaptcha import NextCaptchaAPI

version = "1.1"

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

# Only do automatic updates if running the executable.
file_name = sys.argv[0]
if file_name.endswith(".exe"):
    command = ['update.exe', version]
    subprocess.run(command)

with open('config.json') as jfile:
    data = json.load(jfile)

with open('promo_use.json') as jfile:
    promo_data = json.load(jfile)

nextcaptcha_api_key = data['nextcaptcha_key']
num_threads = data['num_threads']
catchall = data['catchall']
email = data['gmail']
# change_email = data['change_email']
enable_referrals = data['enable_referrals']
redemption_limit = data['referrals_limit']
non_referral_promos = data['non_referral_promos']
error_delay = data["error_delay"]

if email == "" and catchall == "":
    print("You must add an email address or a catchall to the config.")
    exit()

if num_threads >= 1000:
    print("You may run the risk of account suspension with captcha solving services!")

api = NextCaptchaAPI(client_key=f"{nextcaptcha_api_key}")
accounts = 0 

def generate_proxy():
    with open("proxies.txt") as f:
        lines = f.readlines()
        if lines == []:
            return "" # No proxy
        end = int(len(lines)) - 1
        number = random.randint(0, end)
        try:
            ip, port, user, passw = lines[number].strip("\n").split(":")
            proxy = f"{user}:{passw}@{ip}:{port}"
        except:
            print("There appears to be a formatting error in your proxies.txt file.")
            return ""
    return proxy

def get_promos():
    all_promos = []
    if non_referral_promos != []:
        all_promos.extend(non_referral_promos)
    if enable_referrals:
        while True:
            with open("promo_codes.txt") as f:
                lines = f.readlines()
            end = len(lines) - 1
            if lines == []:
                return ""
            number = random.randint(0, end)
            promo = lines[number].strip("\n")
            if promo in promo_data:
                if promo_data[promo] >= redemption_limit:
                    print("Promo code has reached max uses, getting another one...")
                    new_lines = [line for line_num, line in enumerate(lines) if line_num != number]
                    with open('promo_codes.txt', 'w') as file:
                        file.writelines(new_lines)
                else:     
                    all_promos.append(promo)
                    break
            else:
                promo_data[promo] = 0
                all_promos.append(promo)
                break
    return all_promos

def generateAccount():
    global accounts
    global catchall
    global email
    while True:
        try:
            session = tls_client.Session(client_identifier='chrome138')

            proxy = generate_proxy()
            if proxy == "":
                print("No proxy is present, using local IP.")
            else:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                session.proxies = proxies

            headers = {
                'Host': 'www.instacart.com',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=0, i'
            }
            session.headers.update(headers)

            response = session.get('https://www.instacart.com/', headers=headers)
            
            random_first_name = names.get_first_name() + names.get_last_name()
            random_num = random.randint(1, 9999)
            if catchall == "":
                prefix, suffix = email.split("@")
                random_email = f"{prefix}+" + random_first_name.lower() + str(random_num) + f"@{suffix}"
                full_email_prefix = f"{prefix}+" + random_first_name.lower() + str(random_num) 
            else:
                if "@" not in catchall:
                    catchall = "@" + catchall
                random_email = f"{random_first_name}{random_num}{catchall}"
                full_email_prefix = f"{random_first_name}{random_num}"
            random_email = random_email.lower()
                
            headers = {
                'Host': 'www.instacart.com',
                'sec-ch-ua-platform': '"Windows"',
                'x-client-identifier': 'web',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'accept': '*/*',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'content-type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.instacart.com/',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=1, i'
            }

            params = {
            'operationName': 'GetEmailAvailability',
            'variables': f'{{"email": "{random_email}"}}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"0f4b8230f05abb604608e860138ecd141de07075d94a1730c56f6342fd9ad149"}}'
            }

            response = session.get('https://www.instacart.com/graphql', params=params, headers=headers)
            response_json = response.json()
            # print(response_json)
            if response_json['data']['getEmailAvailability']['availability'] != 'available':
                print("Generated email was unavailable, trying again.")
                continue

              
            """solution = capsolver.solve(
            {
                "type": "ReCaptchaV2TaskProxyLess",
                "websiteKey": "6LeN0vMZAAAAAIKVl68OAJQy3zl8mZ0ESbkeEk1m",
                "websiteURL": "https://www.instacart.com",
                "isInvisible": True,
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
            )["gRecaptchaResponse"]
            print(solution)"""

            result = api.recaptchav2enterprise(website_url="https://www.instacart.com", website_key="6LeN0vMZAAAAAIKVl68OAJQy3zl8mZ0ESbkeEk1m", is_invisible=True)
            solution = result['solution']['gRecaptchaResponse']

            headers = {
                'Host': 'www.instacart.com',
                'sec-ch-ua-platform': '"Windows"',
                'x-client-identifier': 'web',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'accept': '*/*',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'content-type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'origin': 'https://www.instacart.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.instacart.com/',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=1, i'
            }

            json_data = {
                'operationName': 'SendVerificationCode',
                'variables': {
                    'identifier': f'{random_email}',
                    'identifier_type': 'email',
                    'recaptcha': f'{solution}',
                    'requestType': 'signupRequestInitiated'
                },
                'extensions': {
                    'persistedQuery': {
                        'version': 1,
                        'sha256Hash': 'bd4977087761e2699642f0536902eac2c9673aec6c262893ba549073301b6316'
                    },
                },
            }

            response = session.post('https://www.instacart.com/graphql', headers=headers, json=json_data)
            response_json = response.json()
            # print(response_json)
            if "errorTypes" in str(response_json):
                if response_json['data']['sendVerificationCode']['errorTypes'] == ['forbidden']:
                    print("Captcha token error, trying again...")
                    continue

            unverified = True
            loops = 0
            while unverified and loops != 60:
                unreadThreads = ezgmail.search(f'label:UNREAD from:no-reply@instacart.com subject:is your Instacart verification code to:{random_email}')
                if unreadThreads != []:
                    for thread in unreadThreads:
                        for msg in thread.messages:
                            if msg.recipient == random_email:
                                msg_subject = msg.subject
                                verification_code = msg_subject.split(" is your Instacart verification code")[0]
                                thread.markAsRead()
                                unverified = False
                else:
                    print("Waiting for verification email...")
                    loops += 1
                    time.sleep(2)

            if loops == 60:
                print("Exceeded 2 minute wait, retrying...")
                continue 


            headers = {
                'Host': 'www.instacart.com',
                'sec-ch-ua-platform': '"Windows"',
                'x-client-identifier': 'web',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'accept': '*/*',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'content-type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'origin': 'https://www.instacart.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.instacart.com/',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=1, i'
            }

            json_data = {
                'operationName': 'CreateUserFromVerificationCode',
                'variables': {
                    'identifier': f'{random_email}',
                    'identifier_type': 'email',
                    'verification_code': f'{verification_code}',
                    'email': f'{random_email}',
                    'utm_params': {
                        'utmSource': 'auth_v4_modal',
                    },
                    'postalCode': '20001',
                },
                'extensions': {
                    'persistedQuery': {
                        'version': 1,
                        'sha256Hash': 'dce24ecd9b9a3152f9a230621416c173723112c4781f5f0c4dcdf0fd4eb60b26',
                    },
                },
            }

            response = session.post('https://www.instacart.com/graphql', headers=headers, json=json_data)

            try:
                response_json = response.json()
                # print(response_json)
            except:
                print("No JSON returned from account creation request.")
                continue
            if response.status_code == 403:
                print("This proxy was blocked, trying again.")
            elif "errorTypes" in str(response_json):
                # print(response_json["data"]["createUser"]["errorTypes"])
                if response_json["data"]["createUserFromVerificationCode"]["errorTypes"] == ["forbidden"]:
                    print("Captcha token error, trying again...")
            else:
                account_token = response_json['data']['createUserFromVerificationCode']['authToken']['token']
                promo_codes = get_promos()
                redeemed_promos = []
                used_promo_amounts = []
                if promo_codes != []:
                    for promo in promo_codes: 
                        promo = promo.lower()

                        headers = {
                            'Host': 'www.instacart.com',
                            'sec-ch-ua-platform': '"Windows"',
                            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                            'sec-ch-ua-mobile': '?0',
                            'x-page-view-id': '783c6829-6b47-51fb-a98f-44d1cf22b78c',
                            'x-client-identifier': 'web',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                            'accept': '*/*',
                            'content-type': 'application/json',
                            'origin': 'https://www.instacart.com',
                            'sec-fetch-site': 'same-origin',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-dest': 'empty',
                            'referer': 'https://www.instacart.com/store/account/credits',
                            'accept-language': 'en-US,en;q=0.9',
                            'priority': 'u=1, i'
                        }

                        json_data = {
                            'operationName': 'RedeemPublicCouponOrGiftCard',
                            'variables': {
                                'code': f'{promo}',
                            },
                            'extensions': {
                                'persistedQuery': {
                                    'version': 1,
                                    'sha256Hash': 'a232d37ba44a92d53f5e382e1d024a296d458de5d97b09c9f80aaf448ba95a41',
                                },
                            },
                        }

                        response = session.post('https://www.instacart.com/graphql', headers=headers, json=json_data)      
                        response_json = response.json()
                        # print(response_json)
                        if "error" in str(response_json).lower():
                            error_message = response_json["data"]["promotionCodesRedemption"]["message"]
                            if error_message in ["This promotion can't be redeemed because it has either expired or reached its redemption limit."]:
                                with open("promo_codes.txt") as file:
                                    referral_promos = file.readlines()
                                if promo in referral_promos:
                                    print("Referral is invalid, removing from promo_codes.txt")
                                    new_lines = [line.strip("\n") for line in referral_promos if line.strip("\n") != promo]
                                    with open('promo_codes.txt', 'w') as file:
                                        file.writelines('\n'.join(new_lines))
                                else:
                                    print(f"Promo code: {promo} is invalid, please remove it from config.json")
                                promo = "Not Applied"
                                used_promo_amounts = []
                            elif "Unauthorized" in error_message:
                                print("User token missing...")
                                continue
                            else:
                                print(f"Error occurred while applying promo code: {error_message}")
                        else:
                            used_promo_amounts.append(response_json["data"]["promotionCodesRedemption"]["subLabel"])
                            if promo in promo_data:
                                promo_data[promo] += 1
                            else:
                                promo_data[promo] = 1
                                
                            redeemed_promos.append(promo)
                            with open('promo_use.json', 'w') as file:
                                json.dump(promo_data, file)
                else:
                    # print("No promo codes have been applied.")
                    used_promo_amounts = []
                

                page_view_id = str(uuid.uuid4())

                headers = {
                    'Host': 'www.instacart.com',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                    'sec-ch-ua-mobile': '?0',
                    'x-page-view-id': f'{page_view_id}',
                    'x-client-identifier': 'web',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'referer': 'https://www.instacart.com/store/referrals',
                    'accept-language': 'en-US,en;q=0.9',
                    'priority': 'u=1, i'
                }

                params = {
                    'operationName': 'ReferralPage',
                    'variables': '{"zoneId":"1652"}',
                    'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"486dac795ae59b539d8552ab80660946d21534b239300bf10e58820f68301794"}}',
                }

                response = session.get('https://www.instacart.com/graphql', params=params, headers=headers)
                # print(response.json())
                response_json = response.json()
                acc_promo = response_json['data']['referralDetails']['shareCode']
                ref_amount = response_json['data']['referralDetails']['viewSection']['offerDetails']['headerString'].split("\n")[1].strip(" for a friend")
   
                accounts += 1
                file = open('accounts.txt', "a", encoding="utf-8")
                file.write(f"{random_email}:{account_token}:{random_first_name}:{redeemed_promos} - {used_promo_amounts}:{acc_promo} - {ref_amount}")
                file.write("\n")
                file.close()
                print(f"Generated {accounts} accounts. Promos applied: {redeemed_promos}")
                   
        except json.decoder.JSONDecodeError as e:
            print(traceback.print_exc())
            print(f"JSON Decode Error: {e}\nLikely due to banned IP.")
            time.sleep(error_delay)
            
        except Exception as e:
            print(f"Request failed: {e}, retrying...")
            time.sleep(error_delay)

if __name__ == "__main__": 
    for x in range(num_threads):
        t1 = threading.Thread(target=generateAccount)
        t1.start()
            


