import time
import random
from fake_useragent import UserAgent
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def get_random_user_agent():
    """Generate a random user agent."""
    ua = UserAgent()
    return ua.random

def create_driver(proxy=None):
    """Create a WebDriver instance with stealth settings and optional proxy."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={get_random_user_agent()}")
    
    options.add_argument('--headless')  # Run Chrome in headless mode (remove to see the window)
    
    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')
    
    driver = webdriver.Chrome(options=options)
    
    # Apply stealth mode to bypass detection
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    
    return driver

def load_session(url, proxy=None):
    """Load a YouTube session using the specified proxy."""
    try:
        driver = create_driver(proxy)
        print(f"Opening YouTube URL with proxy: {proxy if proxy else 'No proxy'}")
        driver.get(url)
        
        # Simulate human-like actions with random sleep time
        action = ActionChains(driver)
        action.move_by_offset(0, 100).click().perform()  # Simulate scrolling
        time.sleep(random.uniform(10, 30))  # Simulate watching the video
        
        print("Session completed successfully.")
        
        driver.quit()
    except Exception as e:
        print(f"Error occurred with proxy {proxy if proxy else 'No proxy'}: {e}")

def load_proxies(file_path):
    """Load proxies from a file."""
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        if not proxies:
            print("No proxies found in the file.")
            return []
        return proxies
    except FileNotFoundError:
        print(f"Proxy file not found: {file_path}")
        return []

if __name__ == "__main__":
    # Inputs from the user
    youtube_url = input("Enter YouTube URL: ").strip()
    refresh_rate = float(input("Enter refresh rate (seconds): ").strip())
    view_count = int(input("Enter number of views: ").strip())
    
    # Load proxies from the file
    proxy_file = './proxies.txt'
    proxies = load_proxies(proxy_file)
    use_proxies = bool(proxies)
    
    if use_proxies:
        print(f"Loaded {len(proxies)} proxies.")
    else:
        print("No proxies available. Proceeding without proxies.")
    
    # Start sessions
    print("Starting YouTube view automation...")
    counter = 0
    while counter < view_count:
        proxy = random.choice(proxies) if use_proxies else None
        load_session(youtube_url, proxy)
        counter += 1
        time.sleep(refresh_rate)
    
    print(f"Completed {view_count} views.")
