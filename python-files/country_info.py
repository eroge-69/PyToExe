
import requests

def get_country_info(country):
    url = f"https://restcountries.com/v3.1/name/{country}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()[0]
    info = {
        "Название страны": data.get("name", {}).get("common", "Не найдено"),
        "Столица": ", ".join(data.get("capital", ["Не указана"])),
        "Регион": data.get("region", "Не указан"),
        "Население": f"{data.get('population', 0):,}",
        "Валюта": ", ".join(data.get("currencies", {}).keys()),
        "Флаг": data.get("flags", {}).get("png", "Не найден")
    }
    return info

def main():
    print("🌍 Введите название страны (на английском):")
    country = input(">>> ").strip()
    info = get_country_info(country.lower())
    if not info:
        print("❌ Страна не найдена. Попробуйте ещё раз.")
        return
    print("
📌 Информация о стране:")
    for key, value in info.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
