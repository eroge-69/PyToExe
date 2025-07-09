import requests
import webbrowser

CLIENT_ID = "00000000402b5328"
REDIRECT_URI = "https://login.live.com/oauth20_desktop.srf"
SCOPE = "XboxLive.signin offline_access"

def get_code():
    url = (
        f"https://login.live.com/oauth20_authorize.srf?"
        f"client_id={CLIENT_ID}&response_type=code&"
        f"redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    )
    print("🔗 Open this URL in your browser and sign in:\n")
    print(url + "\n")
    webbrowser.open(url)
    code = input("🔑 Copy and paste here the code contained in the redirect URL (format: https://login.live.com/oauth20_desktop.srf?code=  THECODETOCOPYHERE  &lc=1036):\n> ").strip()
    return code

def get_access_token(code):
    url = "https://login.live.com/oauth20_token.srf"
    data = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code,
    }
    return requests.post(url, data=data).json()

def xbox_authenticate(access_token):
    url = "https://user.auth.xboxlive.com/user/authenticate"
    headers = {"Content-Type": "application/json"}
    json_data = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={access_token}"
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }
    return requests.post(url, json=json_data, headers=headers).json()

def xbox_xsts(xbl_token):
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    headers = {"Content-Type": "application/json"}
    json_data = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbl_token]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }
    return requests.post(url, json=json_data, headers=headers).json()

def minecraft_authenticate(uhs, xsts_token):
    url = "https://api.minecraftservices.com/authentication/login_with_xbox"
    headers = {"Content-Type": "application/json"}
    json_data = {
        "identityToken": f"XBL3.0 x={uhs};{xsts_token}"
    }
    return requests.post(url, json=json_data, headers=headers).json()

def get_profile(mc_token):
    url = "https://api.minecraftservices.com/minecraft/profile"
    headers = {"Authorization": f"Bearer {mc_token}"}
    return requests.get(url, headers=headers).json()

def main():
    code = get_code()
    print("\n🔐 Exchanging code for a Microsoft access_token...")
    token = get_access_token(code)
    access_token = token["access_token"]

    print("🎮 Xbox Live authentication...")
    xbl = xbox_authenticate(access_token)
    xbl_token = xbl["Token"]
    uhs = xbl["DisplayClaims"]["xui"][0]["uhs"]

    print("🔑 XSTS authentication...")
    xsts = xbox_xsts(xbl_token)
    xsts_token = xsts["Token"]

    print("🟩 Minecraft authentication...")
    mc = minecraft_authenticate(uhs, xsts_token)
    mc_token = mc["access_token"]

    print("\n✅ Your Minecraft Access Token:")
    print(mc_token)

    print("\n🧾 Your Minecraft profile:")
    profile = get_profile(mc_token)
    print(profile)

if __name__ == "__main__":
    main()
