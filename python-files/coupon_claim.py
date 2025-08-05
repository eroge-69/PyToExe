import requests

useCoupon = "https://event.withhive.com/ci/smon/evt_coupon/useCoupon"
checkUser = "https://event.withhive.com/ci/smon/evt_coupon/checkUser"
 
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://event.withhive.com",
    "Referer": "https://event.withhive.com/ci/smon/evt_coupon",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

with open("hiveid.txt", "r") as file:
    hiveids = file.read().splitlines()


with open("codes.txt", "r") as file:
    codes = file.read().splitlines()    

for hiveid in hiveids:
    for code in codes:
        payload = {
            "lang": "en",
            "server": "global",
            "hiveid": hiveid,
            "coupon": code
        }
        response = requests.post(useCoupon, headers=headers, data=payload)

        json_data = response.json()
        ret_msg = json_data.get("retMsg")
        print(f"HiveID: {payload['hiveid']}")
        print(f"Message: {ret_msg}")

