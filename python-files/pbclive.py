import vlc
import time
import requests
from bs4 import BeautifulSoup

def scrape_streams(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    stm_urls = soup.find_all('a', class_='jp-playlist-item')
    radio_dict = dict()
    for url in stm_urls:
        radio_dict[url.string] = url.get('href')
    return radio_dict

print('Scraping streams...')
# Replace with the URL of the live radio stream
stations = scrape_streams('https://radio.gov.pk/live-streaming')


print('Available streams from PBC')
print('====================================')
for station in list(stations.keys()):
	print(station)

print('====================================')
station = input('Enter stream to play as it appears in the list: ')

print('Acquiring resources...')
# Create a VLC instance
instance = vlc.Instance()

# Create a media player object
player = instance.media_player_new()

# Create a media object from the stream URL
media = instance.media_new(stations[station])

# Set the media for the player
player.set_media(media)

print('If there is no audio, may be there is error on server side')
#
input('Press enter to play.')
# Play the stream
player.play()
print('Playing...')
input('Press enter to play.')
player.stop()
# Keep the script running to allow playback
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    player.stop()
    print("Radio stream stopped.")