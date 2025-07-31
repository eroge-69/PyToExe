import phonenumbers
from phonenumbers import timezone, carrier, geocoder
from datetime import datetime
import pytz

def get_kz_number_info(phone_number):
    number = phonenumbers.parse(phone_number, "KZ")

    # Оператор
    operator_name = carrier.name_for_number(number, "ru")

    # Регион
    region = geocoder.description_for_number(number, "ru")

    # Часовой пояс
    timezones = timezone.time_zones_for_number(number)
    current_times = {}
    for tz in timezones:
        current_time = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S")
        current_times[tz] = current_time

    return {
        "номер": phone_number,
        "регион": region,
        "оператор": operator_name,
        "время": current_times
    }

# Пример использования:
info = get_kz_number_info("+77015551234")
for key, value in info.items():
    print(f"{key}: {value}")
