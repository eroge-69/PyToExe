import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests, os, re, time

emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0]+", flags=re.UNICODE)


def download_images(image_urls, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for i, url in enumerate(image_urls):
        response = requests.get(url)
        if response.status_code == 200:
            image_name = f"image_{i+1}.jpg"
            image_path = os.path.join(folder_path, image_name)
            with open(image_path, "wb") as image_file:
                image_file.write(response.content)
            print(f"Downloaded: {image_name}")
        else:
            print(f"Failed to download image from URL: {url}")


options = uc.ChromeOptions()
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

with open('product_urls.txt', 'r') as f:
    product_urls = [line.strip() for line in f.readlines()]

# Navigation zur Ricardo-Website
driver.get('https://www.ricardo.ch/')

for url in product_urls:
    driver.get(url)

    try:
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.style_title__bX9DL'))).text
    except:
        input("Bitte CAPTCHA lösen und Enter drücken...")
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.style_title__bX9DL'))).text

    title_clean = emoji_pattern.sub(r'', title)

    # Preis holen mit alternativen Selektoren
    try:
        price = driver.find_element(By.CSS_SELECTOR, '.style_price__6zEqw').text
    except:
        price = driver.find_element(By.CSS_SELECTOR, '.style_price__Fchy5').text

    # Bilder extrahieren
    images = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.style_thumbnail__u2HE9')))
    img_urls = [img.get_attribute('style').split('url("')[1].split('")')[0].replace('t_100x75', 't_1800x1350') for img in images]

    # Beschreibung extrahieren
    try:
        description = driver.find_element(By.CSS_SELECTOR, '.style_userDescription__ggKeC').text
    except:
        description = "Keine Beschreibung verfügbar."

    folder_title = re.sub(r'["/\\*|?:><]', '', title_clean).strip()
    folder_path = os.path.join(folder_title, "pictures")

    # Bilder herunterladen
    download_images(img_urls, folder_path)

    # Informationen speichern
    info = f'{title_clean}\nPreis: {price}\nBeschreibung:\n{description}'

    os.makedirs(folder_title, exist_ok=True)

    with open(f'{folder_title}/info.txt', 'w', encoding='utf-8') as f:
        f.write(info)

    print(f"Produkt gespeichert: {title_clean}\n")

    time.sleep(2)  # kurzer Delay, um Scraping höflich zu gestalten

# Beenden des Drivers
driver.quit()
