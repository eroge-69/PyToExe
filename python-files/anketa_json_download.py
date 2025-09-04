import requests
import json
import os
from zipfile import ZipFile, ZIP_DEFLATED

#Область переменных
url_api = "https://api.ptpit.ru/"
page_size = 500
TokenApiBase = "304u8jt93p4tuerukfbh"
LoginAuthorization = "velmozhin"
PassAuthorization = "OCiqnw77jcrz"
full_data_json = []
file_path = "output.json"

#функция запроса
def fetch_data(urlSource,NameToken,SourceToken):
    headers = {
        NameToken: SourceToken
    }
    response = requests.get(urlSource, headers=headers)
    response.raise_for_status()
    return response.json()

# Желательно токен Authorization получать так же актуальный другим запросом

urlSource_Authorization = url_api + "/login"
body_Authorization = {"login":LoginAuthorization,"password":PassAuthorization}
response_Authorization = requests.post(urlSource_Authorization,body_Authorization)
response_Authorization.raise_for_status()
data_response_Authorization = response_Authorization.json()

# Вычисляем количество запросов

b_url = url_api + "acceptance/admin/card"
initial_data = fetch_data(b_url,"Authorization",data_response_Authorization["token"])

num_requests = (len(initial_data) + page_size - 1) // page_size  # Округление вверх

# Выполняем запросы с пагинацией
for i in range(num_requests):
    offset = i * page_size
    n_url = f"{url_api}cards?limit={page_size}, &offset={offset}"
    data_json = fetch_data(n_url,"x-api-key",TokenApiBase)
    full_data_json = full_data_json + data_json
    
#Полученый список формируем в текстовый json и передаем и сохроняем в файл либо передеаем на сервер

with open(file_path, "w", encoding="utf-8") as json_file:
    json.dump(full_data_json, json_file, ensure_ascii=False, indent=4)

with ZipFile("data_anc.zip", "w",compression=ZIP_DEFLATED, compresslevel=3) as myzip:
    myzip.write(file_path)
    
os.remove(file_path)
