import PySimpleGUI as sg
import requests
import whois
import json
from datetime import datetime, timezone
import urllib.parse

# ---------------- CONFIG ----------------
SERPAPI_KEY = ""         # Optional: SerpAPI key (or other search provider). See below.
HIBP_API_KEY = ""        # Optional: HaveIBeenPwned API key for breaches
DRAGON_LOGO_PATH = "dragon_logo.png"
DISCORD_CLIENT_ID = ""   # Optional: For OAuth2 (if you want to get email with user consent)
DISCORD_CLIENT_SECRET = ""
DISCORD_REDIRECT_URI = "http://localhost:5000/callback"  # your redirect URL after registering app
# ----------------------------------------

# ---------- Helper Functions ----------

def ip_lookup(ip_or_hostname):
    """Perform IP lookup using ipapi.co"""
    try:
        # Try to resolve hostname to IP if needed
        import socket
        try:
            ip = socket.gethostbyname(ip_or_hostname)
        except:
            ip = ip_or_hostname
        
        # Get IP info from ipapi.co
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to lookup IP: {response.status_code}"}
    except Exception as e:
        return {"error": f"IP lookup failed: {str(e)}"}

def whois_lookup(domain):
    """Perform WHOIS lookup"""
    try:
        w = whois.whois(domain)
        # Convert whois object to dict for JSON serialization
        result = {}
        if hasattr(w, 'domain_name'):
            result['domain_name'] = w.domain_name
        if hasattr(w, 'registrar'):
            result['registrar'] = w.registrar
        if hasattr(w, 'creation_date'):
            result['creation_date'] = w.creation_date
        if hasattr(w, 'expiration_date'):
            result['expiration_date'] = w.expiration_date
        if hasattr(w, 'name_servers'):
            result['name_servers'] = w.name_servers
        return result
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {str(e)}"}

def hibp_email_check(email):
    """Check email against Have I Been Pwned database"""
    try:
        headers = {'User-Agent': 'DragonMultitool'}
        if HIBP_API_KEY:
            headers['hibp-api-key'] = HIBP_API_KEY
        
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"result": "No breaches found for this email"}
        elif response.status_code == 429:
            return {"error": "Rate limited. Please try again later or use API key"}
        else:
            return {"error": f"HIBP check failed: {response.status_code}"}
    except Exception as e:
        return {"error": f"HIBP check failed: {str(e)}"}

def email_social_search_serpapi(email, api_key):
    """Search for email mentions using SerpAPI"""
    if not api_key:
        return {"error": "SerpAPI key required for social search"}
    
    try:
        params = {
            'engine': 'google',
            'q': f'"{email}"',
            'api_key': api_key,
            'num': 10
        }
        
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"SerpAPI search failed: {response.status_code}"}
    except Exception as e:
        return {"error": f"Social search failed: {str(e)}"}

def discord_snowflake_to_date(snowflake_id):
    """Convert Discord snowflake ID to creation date"""
    try:
        snowflake = int(snowflake_id)
        # Discord epoch is January 1, 2015
        discord_epoch = 1420070400000
        timestamp = ((snowflake >> 22) + discord_epoch) / 1000
        creation_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        return {
            "snowflake_id": snowflake_id,
            "creation_date": creation_date.isoformat(),
            "creation_date_readable": creation_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    except Exception as e:
        return {"error": f"Snowflake conversion failed: {str(e)}"}

def discord_oauth_url(client_id, redirect_uri, scopes=("identify", "email")):
    """Generate Discord OAuth2 URL"""
    base_url = "https://discord.com/api/oauth2/authorize"
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(scopes)
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def discord_exchange_code_for_email(client_id, client_secret, redirect_uri, code):
    """Exchange OAuth code for user info including email"""
    try:
        # Exchange code for access token
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_response = requests.post(
            'https://discord.com/api/oauth2/token',
            data=token_data,
            headers=headers,
            timeout=10
        )
        
        if token_response.status_code != 200:
            return {"error": f"Token exchange failed: {token_response.status_code}"}
        
        token_info = token_response.json()
        access_token = token_info.get('access_token')
        
        if not access_token:
            return {"error": "No access token received"}
        
        # Get user info
        user_headers = {'Authorization': f"Bearer {access_token}"}
        user_response = requests.get(
            'https://discord.com/api/users/@me',
            headers=user_headers,
            timeout=10
        )
        
        if user_response.status_code == 200:
            return user_response.json()
        else:
            return {"error": f"User info request failed: {user_response.status_code}"}
            
    except Exception as e:
        return {"error": f"OAuth exchange failed: {str(e)}"}

# ---------- GUI ----------

# ✅ FIXED CUSTOM THEME
sg.LOOK_AND_FEEL_TABLE['DragonPurple'] = {
    'BACKGROUND': '#2b0b3a',
    'TEXT': '#e6e0ff',
    'INPUT': '#3b1a55',
    'TEXT_INPUT': '#ffffff',
    'SCROLL': '#3b1a55',
    'BUTTON': ('#ffffff', '#6b2fa6'),
    'PROGRESS': ('#D1826B', '#CC8019'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0,
}
sg.theme('DragonPurple')

logo_col = [
    [sg.Image(DRAGON_LOGO_PATH, size=(120, 120), key='-LOGO-', visible=True)],
    [sg.Text("DragonMultitool", font=("Helvetica", 16, "bold"))]
]

tab_ip = [
    [sg.Text("IP or Hostname:"), sg.Input(key='-IP-', size=(30,1)), sg.Button("Lookup IP", key='-DOIP-')],
    [sg.Multiline(key='-IPOUT-', size=(80,10), autoscroll=True)]
]

tab_email = [
    [sg.Text("Email address (public footprint):"), sg.Input(key='-EMAIL-', size=(40,1)), sg.Button("Check Email", key='-DOEMAIL-')],
    [sg.Button("Check breaches (HIBP)", key='-HIBP-'), sg.Button("Search public socials (SerpAPI)", key='-SOCSEARCH-')],
    [sg.Multiline(key='-EMAILOUT-', size=(80,12), autoscroll=True)]
]

# ✅ ONLY ONE CLEANED `tab_disc` REMAINS
tab_disc = [
    [sg.Text("Discord ID / Snowflake:"), sg.Input(key='-DSID-', size=(30,1)), sg.Button("Get Creation Date", key='-DODISC-')],
    [sg.HorizontalSeparator()],
    [sg.Text("Discord OAuth (email only with explicit user consent):", font=("Helvetica", 9, "italic"))],
    [sg.Text("Client ID:"), sg.Input(DISCORD_CLIENT_ID, key='-DCLIENTID-', size=(40,1))],
    [sg.Text("Client Secret:"), sg.Input(DISCORD_CLIENT_SECRET, key='-DCLIENTSECRET-', size=(40,1), password_char='*')],
    [sg.Text("Redirect URI (must match app settings):"), sg.Input(DISCORD_REDIRECT_URI, key='-DREDIR-', size=(60,1))],
    [sg.Button("Generate OAuth URL", key='-SHOWOAUTH-'), sg.Input("", key='-OAUTHURL-', size=(60,1), disabled=True)],
    [sg.Text("Paste returned 'code' here:"), sg.Input(key='-OAUTHCODE-', size=(50,1)), sg.Button("Exchange code", key='-EXCHCODE-')],
    [sg.Multiline(key='-DISCOUT-', size=(80,8), autoscroll=True)]
]

notes = [
    [sg.Text("Disclaimer (LEGAL & EDUCATIONAL):", font=("Helvetica",10,"bold"))],
    [sg.Multiline("This tool is for testing, education, and authorized OSINT only.\n"
                  "DO NOT use it to access devices, accounts, or data without explicit, informed consent.\n"
                  "Unauthorized access, password cracking, or privacy invasion is illegal and unethical.\n"
                  "Use OAuth flows to get private data (like email) only when the account owner explicitly consents.\n"
                  "By using this program you agree to comply with applicable laws and the terms of any APIs you use.",
                  size=(80,6), disabled=True)]
]

layout = [
    [sg.Column(logo_col), sg.Column([[sg.Text("Purple-themed Legal Multitool", font=("Helvetica",18,"bold"))]])],
    [sg.TabGroup([[sg.Tab('IP Lookup', tab_ip), sg.Tab('Email Footprint', tab_email), sg.Tab('Discord', tab_disc)]], key='-TABS-')],
    [sg.HorizontalSeparator()],
    [sg.Column(notes)],
    [sg.Button("Exit")]
]

# ✅ FIXED: made resizable
window = sg.Window("DragonMultitool (Legal/Educational)", layout, size=(1000,700), resizable=True, finalize=True)

# ---------- Event Loop ----------
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # IP Lookup
    if event == '-DOIP-':
        q = values['-IP-'].strip()
        if not q:
            window['-IPOUT-'].update("Please enter an IP or hostname.\n")
        else:
            window['-IPOUT-'].update("Performing IP lookup...\n")
            res = ip_lookup(q)
            pretty = json.dumps(res, indent=2, default=str)
            window['-IPOUT-'].update(pretty)
            if '.' in q or q.replace('.', '').isdigit():
                w = whois_lookup(q)
                window['-IPOUT-'].update(window['-IPOUT-'].get() + "\n---- WHOIS ----\n" + json.dumps(w, indent=2, default=str))

    # Email footprint - basic: breach check or social search
    if event == '-HIBP-':
        email = values['-EMAIL-'].strip()
        if not email:
            window['-EMAILOUT-'].update("Enter an email to check breaches.\n")
        else:
            window['-EMAILOUT-'].update("Checking breaches (HaveIBeenPwned)...\n")
            res = hibp_email_check(email)
            window['-EMAILOUT-'].update(json.dumps(res, indent=2, default=str))

    if event == '-SOCSEARCH-':
        email = values['-EMAIL-'].strip()
        if not email:
            window['-EMAILOUT-'].update("Enter an email to search public social mentions.\n")
        else:
            window['-EMAILOUT-'].update("Searching public social mentions via SerpAPI (requires API key)...\n")
            res = email_social_search_serpapi(email, SERPAPI_KEY)
            window['-EMAILOUT-'].update(json.dumps(res, indent=2, default=str))

    # Discord snowflake -> creation date
    if event == '-DODISC-':
        sid = values['-DSID-'].strip()
        if not sid:
            window['-DISCOUT-'].update("Please enter a Discord ID / snowflake.\n")
        else:
            res = discord_snowflake_to_date(sid)
            window['-DISCOUT-'].update(json.dumps(res, indent=2))

    # Discord OAuth URL generation
    if event == '-SHOWOAUTH-':
        client_id = values['-DCLIENTID-'].strip()
        redirect = values['-DREDIR-'].strip() or DISCORD_REDIRECT_URI
        if not client_id:
            window['-DISCOUT-'].update("Please provide your Discord Client ID (register your app at https://discord.com/developers/applications).\n")
        else:
            url = discord_oauth_url(client_id, redirect, scopes=("email","identify"))
            window['-OAUTHURL-'].update(url)
            window['-DISCOUT-'].update("Open the URL in a browser. The account owner must authorize. After redirect, copy the 'code' param and paste it in the box, then click Exchange code.\n")

    # Exchange OAuth code for user info (email included if scope granted)
    if event == '-EXCHCODE-':
        client_id = values['-DCLIENTID-'].strip()
        client_secret = values['-DCLIENTSECRET-'].strip()
        redirect = values['-DREDIR-'].strip() or DISCORD_REDIRECT_URI
        code = values['-OAUTHCODE-'].strip()
        if not (client_id and client_secret and code):
            window['-DISCOUT-'].update("Please fill Client ID, Client Secret, and paste the returned 'code' before exchanging.\n")
        else:
            window['-DISCOUT-'].update("Exchanging code for token and requesting user info... (only works if the user consented to email scope)\n")
            res = discord_exchange_code_for_email(client_id, client_secret, redirect, code)
            window['-DISCOUT-'].update(json.dumps(res, indent=2, default=str))

window.close()