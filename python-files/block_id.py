import requests, time, json, os, secrets
from concurrent.futures import ThreadPoolExecutor, as_completed

# Made by MasterP
# Made by MasterP
# Made by MasterP

MAX_WORKERS = 3
COUNTER     = 0
session     = requests.Session()

def random_digits(n=16):
    return ''.join(secrets.choice('0123456789') for _ in range(n))


def load_account_cache():
    try:
        with open("account_cache.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading Roblox sessions: {e}")
        return {}

def save_account_cache(SECURITY_TOKEN, userid):
    try:
        file_path = 'account_cache.json'
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
            
        data[SECURITY_TOKEN] = {"userid": userid}
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving Roblox session: {e}")

def get_user_id(SECURITY_TOKEN):
    
    headers = {
        'Cookie': '.ROBLOSECURITY=' + str(SECURITY_TOKEN),
    }

    response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=headers)
    
    return response.json().get('id', None)

def get_csrf_token(SECURITY_TOKEN):

    headers = {
        'Cookie': '.ROBLOSECURITY=' + str(SECURITY_TOKEN),
    }

    response = requests.post(
        'https://auth.roblox.com/v1/authentication-ticket',
    headers=headers)
    
    return response.headers.get('x-csrf-token', None)

def block_account(SECURITY_TOKEN, USER_ID):

    try:

        cookies = {
            '.ROBLOSECURITY': SECURITY_TOKEN,
            'RBXEventTrackerV2': f'browserid={random_digits(16)}'
        }
        
        CSRF_TOKEN = get_csrf_token(SECURITY_TOKEN)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'th-TH,th;q=0.9,en;q=0.8',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'x-roblox-browsertracker-id': "0234dfgdgf2343",
            'X-CSRF-TOKEN': str(CSRF_TOKEN),
        }
        
        make_request = session.post(f'https://apis.roblox.com/user-blocking-api/v1/users/{USER_ID}/block-user', headers=headers, cookies=cookies)

        if make_request.status_code == 200:
            print(f" -> Successfully blocked user ID {USER_ID}")
        else:
            result = make_request.json()
            status_code = make_request.status_code
            if result == 1:
                print(f" -> User ID {USER_ID} is already blocked")
            elif status_code == 429:
                print(f" -> Rate limited while blocking user ID {USER_ID}")
            else:
                print(f" -> Failed to block user ID {USER_ID}: {make_request.status_code} - {make_request.json()}")

    except Exception as e:
        print(f" -> Error blocking user: {e}")

with open('cookie.txt', "r", encoding='utf-8') as file:
    accounts = [line.strip() for line in file if line.strip()]

futures = []
print(f" -> # Made by MasterP <-")
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
    for i in range(len(accounts)):
        user1 = accounts[i]
        for j in range(len(accounts)):
            user2 = accounts[j]
            if user1 == user2:
                continue
            
            cached = load_account_cache()

            if not user2 in cached:

                userid = get_user_id(user2)

                if userid:
                    save_account_cache(user2, userid)

            target_id = cached.get(user2, {}).get("userid")

            if not target_id and userid:
                target_id = userid
            
            
            COUNTER += 1
            
            if COUNTER >= len(accounts) +1 :
                time.sleep(10)
                COUNTER = 0

            futures.append(ex.submit(block_account, user1, target_id))

        print(f" -> Queue for account {i+1}/{len(accounts)}")
            
    for fut in as_completed(futures):
        try:
            fut.result()
        except Exception as e:
            print(f" -> Error in thread: {e}")


# Made by MasterP