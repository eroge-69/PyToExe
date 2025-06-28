import requests

ACCESS_TOKEN = "YOUR_INSTAGRAM_ACCESS_TOKEN"
BUSINESS_ACCOUNT_ID = "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID"  # Not username

def get_followers_count(account_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{account_id}?fields=followers_count,username&access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Username: {data['username']}")
        print(f"Followers: {data['followers_count']:,}")
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    get_followers_count(BUSINESS_ACCOUNT_ID, ACCESS_TOKEN)
