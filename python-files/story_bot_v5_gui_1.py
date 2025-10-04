import time, threading
import tkinter as tk
from tkinter import ttk
from colorama import Fore, Style, init

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from ixbrowser_local_api import IXBrowserClient

# INIT colorama
init(autoreset=True)

# CONFIG
WIN_W, WIN_H = 200, 200
WAIT_TIMEOUT = 3
WAIT_POLL = 0.5

# Global stop flag
stop_flag = False

# ================= Selenium helpers =================
def try_click(driver, selectors):
    for by, sel in selectors:
        try:
            el = WebDriverWait(driver, WAIT_TIMEOUT, poll_frequency=WAIT_POLL).until(
                EC.element_to_be_clickable((by, sel))
            )
            el.click()
            return True
        except TimeoutException:
            continue
    return False

def loop_stories(driver, idx, loops, profile_url, log_callback):
    global stop_flag
    log_callback(f"{Fore.CYAN}[{idx}] 🔄 Starting story loop for {loops} times{Style.RESET_ALL}")

    avatar_selectors = [
        (By.XPATH, "//a[contains(@href,'/stories/') or contains(@href,'/story.php')]"),
        (By.XPATH, "//a[contains(@aria-label,'Profile picture')]"),
        (By.XPATH, "//img[contains(@alt,'profile picture')]"),
    ]
    story_btns = [
        (By.XPATH, "//*[text()='View story']"),
        (By.XPATH, "//*[contains(text(),'View story')]"),
        (By.XPATH, "//a[contains(@href,'/stories/')]"),
    ]
    next_btns = [
        (By.XPATH, "//div[@role='button' and @aria-label='Next']"),
        (By.XPATH, "//a[contains(@href,'next')]"),
        (By.CSS_SELECTOR, "div[aria-label='Next story']"),
    ]

    for round_num in range(1, loops+1):
        if stop_flag:
            log_callback(f"{Fore.MAGENTA}[{idx}] ⏹️ Stopped by user{Style.RESET_ALL}")
            break
        try:
            driver.get(profile_url)
            time.sleep(2)

            if not try_click(driver, avatar_selectors):
                log_callback(f"{Fore.YELLOW}[{idx}] ⚠️ No story bubble found (loop {round_num}){Style.RESET_ALL}")
                time.sleep(3)
                continue

            time.sleep(2)
            try_click(driver, story_btns)
            log_callback(f"{Fore.GREEN}[{idx}] ▶ Viewing stories... Round {round_num}/{loops}{Style.RESET_ALL}")

            while True:
                if stop_flag:
                    log_callback(f"{Fore.MAGENTA}[{idx}] ⏹️ Stopped during stories{Style.RESET_ALL}")
                    return
                time.sleep(1)
                if not try_click(driver, next_btns):
                    log_callback(f"{Fore.CYAN}[{idx}] ⏹️ End of stories (round {round_num}), restarting...{Style.RESET_ALL}")
                    break

        except Exception as e:
            log_callback(f"{Fore.RED}[{idx}] ❌ Error: {e}{Style.RESET_ALL}")
            time.sleep(3)

    log_callback(f"{Fore.GREEN}[{idx}] ✅ Finished {loops} loops of stories.{Style.RESET_ALL}")

def view_story_in_profile(pid, idx, loops, profile_url, log_callback):
    client = IXBrowserClient()
    result = client.open_profile(pid, cookies_backup=False, load_profile_info_page=False)
    if not result:
        log_callback(f"{Fore.RED}[{idx}] ❌ Error opening profile{Style.RESET_ALL}")
        return

    dbg = result.get("debugging_address")
    chromedriver = result.get("webdriver")
    opts = Options()
    opts.add_experimental_option("debuggerAddress", dbg)
    driver = Chrome(service=Service(chromedriver), options=opts)

    xpos = (idx % 5) * (WIN_W + 10)
    ypos = (idx // 5) * (WIN_H + 50)
    driver.set_window_size(WIN_W, WIN_H)
    driver.set_window_position(xpos, ypos)

    loop_stories(driver, idx, loops, profile_url, log_callback)

def run_task(profile_url, how_many, loop_count, log_callback):
    global stop_flag
    client = IXBrowserClient()
    profiles = client.get_profile_list()
    if not profiles:
        log_callback(f"{Fore.RED}❌ No profiles found.{Style.RESET_ALL}")
        return

    threads = []
    for idx, prof in enumerate(profiles[:how_many]):
        if stop_flag:
            break
        pid = prof.get("profile_id") or prof.get("id")
        t = threading.Thread(
            target=view_story_in_profile,
            args=(pid, idx, loop_count, profile_url, log_callback),
            daemon=True
        )
        threads.append(t)
        t.start()
        time.sleep(1)

    for t in threads:
        t.join()

# ================= Dark Tkinter GUI =================
def main_gui():
    global stop_flag
    root = tk.Tk()
    root.title("Facebook Story Viewer | Dark Mode")
    root.geometry("800x650")
    root.configure(bg="#1e1e1e")

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 11))
    style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff")
    style.configure("TButton", background="#3a3a3a", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
    style.map("TButton", background=[("active", "#5a5a5a")])

    ttk.Label(root, text="Profile URL:").pack(pady=5)
    url_entry = ttk.Entry(root, width=60)
    url_entry.insert(0, "https://www.facebook.com/rjsheeshbd")
    url_entry.pack(pady=5)

    ttk.Label(root, text="How Many Profiles:").pack(pady=5)
    how_entry = ttk.Entry(root, width=10)
    how_entry.insert(0, "5")
    how_entry.pack(pady=5)

    ttk.Label(root, text="Loop Count:").pack(pady=5)
    loop_entry = ttk.Entry(root, width=10)
    loop_entry.insert(0, "10")
    loop_entry.pack(pady=5)

    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(pady=10, expand=True)
    log_box = tk.Text(frame, height=20, width=90, bg="#252526", fg="#d4d4d4",
                      insertbackground="white", font=("Consolas", 10))
    log_box.pack()

    def log_callback(msg):
        clean_msg = msg.replace(Fore.RED, "").replace(Fore.GREEN, "").replace(Fore.YELLOW, "").replace(Fore.CYAN, "").replace(Fore.MAGENTA, "").replace(Style.RESET_ALL, "")
        log_box.insert(tk.END, clean_msg + "\n")
        log_box.see(tk.END)
        root.update_idletasks()
        print(msg)

    def start():
        global stop_flag
        stop_flag = False
        profile_url = url_entry.get().strip()
        how_many = int(how_entry.get())
        loop_count = int(loop_entry.get())
        log_callback(f"{Fore.CYAN}🚀 Starting with {how_many} profiles, {loop_count} loops each, URL={profile_url}{Style.RESET_ALL}")
        threading.Thread(
            target=run_task,
            args=(profile_url, how_many, loop_count, log_callback),
            daemon=True
        ).start()

    def stop():
        global stop_flag
        stop_flag = True
        log_callback(f"{Fore.MAGENTA}⏹️ Stop requested by user.{Style.RESET_ALL}")

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=10)
    start_btn = ttk.Button(btn_frame, text="▶ Start", command=start)
    start_btn.grid(row=0, column=0, padx=10)
    stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=stop)
    stop_btn.grid(row=0, column=1, padx=10)

    # Footer
    footer = tk.Label(root, text="Tools Created By: RJ Sheesh",
                      bg="#1e1e1e", fg="#888888", font=("Segoe UI", 10, "italic"))
    footer.pack(side="bottom", pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
