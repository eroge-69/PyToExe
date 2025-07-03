from bsp import BSP
from utils import decode_token
from ui import banner, slowprint, success, error, info, highlight
from datetime import datetime
import json, time, os

def main():
    banner()
    u = input(highlight("=> Username: ")).strip()
    if not u.startswith("PL|"): u = f"PL|{u}"
    p = input(highlight("=> Password: ")).strip()

    b = BSP()
    res = b.login(u, p)
    if not res or "access_token" not in res:
        print(error("[!] Login failed.."))
        return

    token, refresh_token = res["access_token"], res.get("refresh_token")
    login_id = decode_token(token).get("loginId")
    if not login_id:
        print(error("[!] Login ID not not found"))
        return

    profiles = b.profinfo(login_id, token)
    if not profiles:
        print(error("[!] Profile error"))
        return

    profile = profiles[0]
    convs, token, refresh_token = b.get_conversations(profile["id"], token, refresh_token)
    if not convs:
        print(error("[!] Conversations error"))
        return

    print(info("\n--- Active Conversations ---"))
    for c in convs:
        try:
            msg_obj = json.loads(c.get("latestMessage", "{}"))
            body = msg_obj.get("MessageBody", "<no content>")
        except:
            body = c.get("latestMessage", "<no content>")
        print(f"{highlight('ID')} {c['conversationId']} | {c['conversationType']} | {c['conversationStatus']}")
        print(f"  Name: {c.get('conversationName','')} | Created: {c['created']}")
        print(f"  Last: {body} | Unread: {c.get('numberOfUnreadMessages',0)}\n")

    conv_id = input(highlight("=> Enter conversationId to spam: ")).strip()

    os.system('cls' if os.name == 'nt' else 'clear')
    banner()

    body = {"Xp": 999999999999}

    while True:
        status, resp = b.send_message(conv_id, profile["id"], token, body)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {highlight('Status')}: {status}")
        if status == 200:
            time.sleep(1)
        elif status == 429:
            print(error("[!] Limit api error. Sleeping 30s..."))
            time.sleep(30)
            res = b.login(u, p)
            if not res or "access_token" not in res:
                print(error("[!] Re-auth failed"))
                break
            token = res["access_token"]
            refresh_token = res.get("refresh_token")
            convs_new, token, refresh_token = b.get_conversations(profile["id"], token, refresh_token)
            if not any(c['conversationId'] == conv_id for c in convs_new):
                print(error("[!] Target conversation not found "))
                break
        else:
            print(error("[!] Sending failed."))
            break

if __name__ == "__main__":
    main()