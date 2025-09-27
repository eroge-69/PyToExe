import requests
from datetime import datetime
import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        print('''
    :::     :::    ::: ::::::::::: :::    ::: ::::    ::::  
  :+: :+:   :+:    :+:     :+:     :+:    :+: +:+:+: :+:+:+ 
 +:+   +:+   +:+  +:+      +:+     +:+    +:+ +:+ +:+:+ +:+ 
+#++:++#++:   +#++:+       +#+     +#+    +:+ +#+  +:+  +#+ 
+#+     +#+  +#+  +#+      +#+     +#+    +#+ +#+       +#+ 
#+#     #+# #+#    #+#     #+#     #+#    #+# #+#       #+# 
###     ### ###    ### ###########  ########  ###       ###                              
    ''')
        
        print("="*50)
        
        username = input("[*] Enter a username: ").strip()
            
        if not username:
            print("[-] Please enter a valid username.")
            input("[*] Press Enter to continue...")
            continue
        
        user_info = get_user_info(username)
        
        if user_info is not None:
            display_user_info(user_info, username)
        
        continue_choice = input("[+] Restart? [y/n]: ").strip().lower()
        
        if continue_choice in ['n', 'no']:
            break

def get_user_info(username):
    try:
        user_lookup_url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username]}
        
        user_response = requests.post(user_lookup_url, json=payload)
        
        if user_response.status_code != 200:
            print(f"[-] Failed to lookup user: {user_response.status_code}")
            return None
        
        user_data = user_response.json()
        
        if not user_data['data']:
            print(f"[-] User '{username}' not found")
            return None
        
        user_id = user_data['data'][0]['id']
        print(f"[+] Found user ID: {user_id}")
        
        user_info_url = f"https://users.roblox.com/v1/users/{user_id}"
        
        headers = {
            'accept': 'application/json'
        }
        
        info_response = requests.get(user_info_url, headers=headers)
        
        if info_response.status_code != 200:
            print(f"[-] Failed to get user data: {info_response.status_code}")
            return None
        
        user_info = info_response.json()
        return user_info
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Network error: {e}")
        return None
    except Exception as e:
        print(f"[-] An error occurred: {e}")
        return None

def format_date(iso_date):
    if iso_date:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "Unknown"

def display_user_info(user_info, username):
    print("="*50)
    
    print(f"[+] Username: {user_info.get('name', 'N/A')}")
    print(f"[+] Display Name: {user_info.get('displayName', 'N/A')}")
    print(f"[+] User ID: {user_info.get('id', 'N/A')}")
    
    created_date = format_date(user_info.get('created', ''))
    print(f"[+] Account Created: {created_date}")
    
    print(f"[+] Banned: {'Yes' if user_info.get('isBanned', False) else 'No'}")
    print(f"[+] Verified Badge: {'Yes' if user_info.get('hasVerifiedBadge', False) else 'No'}")
    print(f"[+] External App: {user_info.get('externalAppDisplayName', 'None')}")
    
    print(f"[+] Description:")
    print("="*50)
    description = user_info.get('description', 'No description available')
    print(description if description else "No description available")
    print("="*50)

if __name__ == "__main__":
    main()