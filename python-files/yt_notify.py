import requests
import time
from win10toast import ToastNotifier

API_KEY = "AIzaSyDKxfRtogNvvK1CpjNcAntF71XVbloBZL4"
CHANNEL_ID = "UCnmGIkw-KdI0W5siakKPKog"

def get_latest_video_id():
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=1"
    )
    response = requests.get(url).json()
    return response['items'][0]['id']['videoId']

last_video_id = None
notifier = ToastNotifier()

while True:
    try:
        current_video_id = get_latest_video_id()
        if current_video_id != last_video_id:
            print("New Ryan Trahan Video Uploaded!")
            notifier.show_toast("New Video Alert", "Ryan Trahan has uploaded a new video!", duration=10)
            last_video_id = current_video_id
        time.sleep(10)  # Wait for 10 seconds before checking again
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(60)  # Wait for 1 minute before retrying