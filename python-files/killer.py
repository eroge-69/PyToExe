import subprocess
import sys
import requests

IG_CURRENT_USER = "https://i.instagram.com/api/v1/accounts/current_user/"
IG_LOGOUT = "https://i.instagram.com/api/v1/accounts/logout/"
DEFAULT_USER_AGENT = "Instagram 219.0.0.12.117 Android"

def get_session_from_co():
    """Run co.exe and capture the session ID from its output"""
    try:
        # Run co.exe and get its stdout
        result = subprocess.run(["co.exe"], capture_output=True, text=True, check=True)
        session_id = result.stdout.strip()
        if not session_id:
            print("No session ID found in co.exe output")
            sys.exit(1)
        return session_id
    except Exception as e:
        print("Error running co.exe:", e)
        sys.exit(1)

def kill_session(session_id: str):
    s = requests.Session()
    s.cookies.set("sessionid", session_id, domain=".instagram.com")
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "*/*",
        "X-IG-App-ID": "567067343352427",
    }

    try:  
        # Check current user info  
        resp = s.get(IG_CURRENT_USER, headers=headers, timeout=10)  
        if resp.status_code != 200:  
            print("Invalid session or already logged out")  
            return  

        data = resp.json()  
        username = data.get("user", {}).get("username", "Unknown")  
        print(f"User login: {username}")  

        # Logout  
        s.post(IG_LOGOUT, headers=headers, timeout=10)  
        print("***Session Killed***")  

    except Exception as e:  
        print("Error:", e)

if __name__ == "__main__":
    session_id = get_session_from_co()
    kill_session(session_id)