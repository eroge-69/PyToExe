
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

BASE_URL = "https://www.slrb.bg"
LIST_URL = f"{BASE_URL}/chlenstvo/sdruzheniya/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_sdr_pages():
    response = requests.get(LIST_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select(".entry-title > a")
    return [link["href"] for link in links]

def extract_details(url):
    result = {"Име": "", "Град": "", "Телефон": "", "Имейл": ""}
    full_url = url if url.startswith("http") else BASE_URL + url

    try:
        r = requests.get(full_url, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")

        title = soup.select_one("h1.entry-title")
        if title:
            result["Име"] = title.text.strip()

        city_info = soup.select_one(".post-content p")
        if city_info:
            result["Град"] = city_info.text.strip()

        content = soup.get_text().lower()
        for word in content.split():
            if "@" in word and "." in word:
                result["Имейл"] = word.strip(".,;()")

        for line in content.splitlines():
            if "тел" in line or "gsm" in line or "моб" in line:
                result["Телефон"] = line.strip()

    except Exception as e:
        result["Име"] = f"Error: {e}"

    return result

def main():
    print("Стартиране на извличането на контактите от slrb.bg...")
    pages = get_sdr_pages()
    data = []
    for i, page in enumerate(pages, 1):
        print(f"[{i}/{len(pages)}] Обработка: {page}")
        data.append(extract_details(page))
        time.sleep(1.5)

    df = pd.DataFrame(data)
    output_file = os.path.join(os.getcwd(), "sdr_contacti.xlsx")
    df.to_excel(output_file, index=False)
    print(f"✅ Файлът е записан като {output_file}")
    input("Натисни Enter за изход...")

if __name__ == "__main__":
    main()
