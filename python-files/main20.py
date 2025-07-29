import requests
from bs4 import BeautifulSoup
import re, csv, random, logging

rnd = random.randint(1000,100000)
logging.basicConfig(
    level=logging.INFO
)

def save_data(d):
    with open(f"{rnd}.csv",mode="a",encoding='utf-8') as f:
        cs = csv.writer(f)
        cs.writerow(d.values())

def get_message(username, message_id) -> dict | None:
    try:
        base_url = 'https://eitaa.com'
        url = f"https://eitaa.com/{username}?before={message_id + 1}"

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        tag = soup.find("div", id=str(message_id))

        if not tag:
            return None

        message = {}

        owner_tag = tag.find("a", class_="etme_widget_message_owner_name")
        if owner_tag and owner_tag.get_text(strip=True):
            message["owner_name"] = owner_tag.get_text(strip=True)

        if owner_tag and owner_tag.has_attr('href'):
            message["channel_url"] = base_url + owner_tag['href']

        message["message_url"] = f"https://eitaa.com/s/{username}/{message_id}"

        msg_text_tag = tag.find("div", class_="etme_widget_message_text")
        if msg_text_tag and msg_text_tag.get_text(strip=True):
            message["message_text"] = msg_text_tag.text.strip()
            views_tag = tag.find("span", class_="etme_widget_message_views")
        # if views_tag and views_tag.get("data-count") and views_tag.get("data-count").isdigit():
        #     message["views"] = int(views_tag.get("data-count"))

        date_tag = tag.find("time", class_="time")
        if date_tag and date_tag.get("datetime"):
            message["date"] = date_tag.get("datetime")

        author_name_tag = tag.find("a", class_="etme_widget_message_author_name")
        if author_name_tag and author_name_tag.get_text(strip=True):
            message["author_name"] = author_name_tag.get_text(strip=True)

        service_date_tag = tag.find("div", class_="etme_widget_message_service_date")
        if service_date_tag and service_date_tag.get_text(strip=True):
            message["service_date"] = service_date_tag.get_text(strip=True)

        video_time_tag = tag.find("time", class_="message_video_duration")
        if video_time_tag and video_time_tag.get_text(strip=True):
            message["video_time"] = video_time_tag.get_text(strip=True)

        if message["message_text"]:
            save_data(message)
    except:
        return


channel_id = input("Enter The Channel Username : ")
msg_id = int(input("From Which Message ID Do You Want To Start ? "))
while True:
    logging.info(f"Data Saving To {rnd}.csv file")
    get_message(channel_id,msg_id)
    msg_id-=1