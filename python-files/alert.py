import requests

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, data=payload)
    return response.status_code, response.text

if __name__ == "__main__":
    bot_token = "8475091849:AAFYHMh_L67UKqJF18cS0DCrg0CdcZTOzWk"
    chat_id = "5697251207"
    message = "Alert: Someone clicked your exe file!"

    status_code, response_text = send_telegram_message(bot_token, chat_id, message)
    if status_code == 200:
        print("Alert sent successfully!")
    else:
        print(f"Failed to send alert. Response: {response_text}")
