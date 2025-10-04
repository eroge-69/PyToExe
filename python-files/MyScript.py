import subprocess
from playwright.sync_api import sync_playwright
from cryptography.fernet import Fernet

# تثبيت المتصفحات تلقائيًا
try:
    subprocess.run(["playwright", "install"], check=True)
except Exception as e:
    print("❌ فشل في تثبيت المتصفحات:", e)
    exit(1)

# بيانات الدخول المشفّرة
key = b'EAKKEF8MsJ8D7dkN8zc0LKNBaxTJFVU6EIy0DmIv8F4='
cipher = Fernet(key)

encrypted_user = b'gAAAAABow9tdq-gU5ravLGBiLjEf6gfXwu7RmZMA-KkJCJMeBnzb4GrxWiNjA7bKq5x-9-YVKsgQ6dnG5-9pGW8xsSehrUxEjQ=='
encrypted_pass = b'gAAAAABow9tdXBAHVUmjXqBVJBX3jBNRN-O-BL9dXNPDqa5p43R1_XztmNSWvOD2gbqpPyTRpa7L6v2bDwQt5uzBvFdgg9wSDg=='

user = cipher.decrypt(encrypted_user).decode()
password = cipher.decrypt(encrypted_pass).decode()

# تشغيل Playwright
def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://login.eres.qnl.qa/login?qurl=https://search.emarefa.net%2fen")
    page.locator("input[name=\"user\"]").fill(user)
    page.locator("input[name=\"pass\"]").fill(password)
    page.get_by_role("button", name="Login/دخول").click()
    page.wait_for_timeout(5000)

    print("✅ تم تسجيل الدخول:", page.url)
    input("📌 اضغط Enter لإغلاق المتصفح...")
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)