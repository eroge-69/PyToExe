import httpx
import re
import time
import random

def check_if_account_is_alive(username):
    url = f"https://api.digitalbyte.cc/instagram/tucktools2.com/{username}"
    try:
        res = httpx.get(url, timeout=10)
        if res.status_code == 200 and "user_followers" in res.text:
            data = res.json()
            print("\n🟢 Account is Live!")
            print(f"👤 Name: {data.get('user_fullname')}")
            print(f"📸 Pic: {data.get('user_profile_pic')}")
            print(f"👥 Followers: {data.get('user_followers')}")
            print(f"➡️ Following: {data.get('user_following')}")
            print(f"📄 Posts: {data.get('total_posts')}")
            print(f"📝 Bio: {data.get('user_description')}")
        else:
            print(f"\n⚠️ Account `{username}` may not be live or is private/unindexed.")
    except Exception as e:
        print(f"\n❌ Error checking `{username}`: {e}")

def extract_usernames_from_file(filename):
    usernames = []
    pattern = r"👤 Username\s*:\s*(\S+)"
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                usernames.append(match.group(1))
    return usernames

def main():
    input_file = "acc-organized.txt"
    print(f"🔍 Loading usernames from {input_file}...\n")
    usernames = extract_usernames_from_file(input_file)

    if not usernames:
        print("❌ No usernames found in acc-organized.txt.")
        return

    for i, username in enumerate(usernames, 1):
        print(f"\n🔎 Checking Account {i}: {username}")
        check_if_account_is_alive(username)
        time.sleep(random.uniform(2.5, 4.5))  # small delay to avoid API spam

if __name__ == "__main__":
    main()
