import requests, random, string, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

def generate_random_email():
    chars = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(chars) for _ in range(12))
    domains = ["gmail.com", "yahoo.com", "outlook.com"]
    return f"{username}@{random.choice(domains)}"

def create_account():
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--user-agent={UserAgent().random}")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/signup")
    time.sleep(3)
    email = generate_random_email()
    password = ''.join(random.sample(chars, 10)) + "!1"
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("signup_button").click()
    time.sleep(5)
    driver.quit()
    return email, password

def login_and_report(email, password, username):
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--user-agent={UserAgent().random}")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/login")
    time.sleep(2)
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("login_button").click()
    time.sleep(3)
    driver.get(f"https://www.tiktok.com/@{username}")
    time.sleep(2)
    driver.find_element_by_xpath("//button[@aria-label='Report']").click()
    time.sleep(1)
    reasons = ["inappropriate_content", "hate_speech", "violence", "spam"]
    driver.find_element_by_xpath(f"//input[@value='{random.choice(reasons)}']").click()
    driver.find_element_by_id("submit").click()
    time.sleep(2)
    driver.quit()

def main():
    username = input("Enter TikTok username to ban: ")
    report_count = int(input("How many reports to simulate ban? "))
    for _ in range(report_count):
        email, password = create_account()
        login_and_report(email, password, username)
        print(f"Reported {username} with {email}")
    print(f"Done spamming reports! TikTok algorithms might ban {username} now!")

if __name__ == "__main__":
    main()
