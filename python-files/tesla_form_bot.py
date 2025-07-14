
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

fields = {
    "registrationType": "01",
    "firstName": "Hamdi",
    "lastName": "Uçak",
    "email": "hamdiucak@gmail.com",
    "emailConfirm": "hamdiucak@gmail.com",
    "phoneNumber": "532 206 27 68",
    "companyDetails.companyName": "Uçar Tekstil Makinaları ve İnşaat San. Tic. Ltd. Şti.",
    "vatId": "8840086794",
    "companyDetails.taxOfficeName": "Küçükköy",
    "companyDetails.companyAddress1": "Şehit Mustafa Yeşil Cad. No:15",
    "companyDetails.companyCity": "Gaziosmanpaşa",
    "companyDetails.companyState": "İstanbul",
    "companyDetails.companyPostalCode": "34250",
    "PRIVACY_CONSENT": "1",
    "creditCardHolderName": "Muammer Uçak",
    "creditCardNumber": "4043 0868 5261 9014",
    "creditCardExpiryMonth": "02",
    "creditCardExpiryYear": "2026",
    "creditCardCvv": "000",
    "creditCardEmail": "hamdiucak@gmail.com",
    "billingAddress1": "Şehit Mustafa Yeşil Cad. No:15",
    "billingZipCode": "34250",
    "billingCity": "Gaziosmanpaşa",
    "billingState": "İstanbul",
}

def insan_gibi_yaz(driver, element, text):
    actions = ActionChains(driver)
    element.click()
    time.sleep(random.uniform(0.3, 0.6))
    for i, harf in enumerate(text):
        if random.random() < 0.1 and i > 2:
            actions.send_keys(text[i - 1])
            actions.pause(0.2)
            actions.send_keys("\b")
        actions.send_keys(harf)
        actions.pause(random.uniform(0.05, 0.15))
    actions.perform()

def baslat():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)

    stealth(driver,
        languages=["tr-TR", "tr"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL",
        fix_hairline=True,
    )

    driver.get("https://www.tesla.com/tr_tr/inventory/new/my")
    print("🚗 Araç seç → sipariş formuna geç → CAPTCHA varsa çöz → ENTER'a bas")
    input()

    for name, value in fields.items():
        try:
            input_element = driver.find_element(By.NAME, name)
            insan_gibi_yaz(driver, input_element, value)
        except Exception as e:
            print(f"⚠️ {name} alanı yazılamadı: {e}")

    print("✅ Tüm alanlar yazıldı. Siparişi sen tamamla.")

if __name__ == "__main__":
    baslat()
