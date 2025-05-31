import requests
import openpyxl
from pandas import DataFrame

COOKIES = {'skid': '3146347771748693488'}
HEADERS = {'content-type': 'application/json', 'sk': 's1235c529d2beb19f1620308c6e107f7d',}
YA_LINK = 'https://market.yandex.ru/api/resolve/?r=src/resolvers/search/__future/resolveSearchAllFilterValues:resolveSearchAllFilterValues'

def read_file(file:str) -> list[str]:
    urls:list[str] = []

    workbook = openpyxl.load_workbook(filename=file)
    work_sheet = workbook.active
    
    for num in range(1, 100):
        value:str = work_sheet[f'A{num}'].value
        if value != None:
            urls.append(value)
    
    return urls

def parse_urls(urls:list[str]):
    parsed_urls:list[list] = []

    for url in urls:
        path:str = url.replace('https://market.yandex.ru', '')
        nid:int = path.split('/')[2]
        parsed_urls.append([nid, path])
    
    return parsed_urls

def get_json_data(nid:int, path:str) -> dict:
    json_data:dict = { 'params': [{'nid': nid}], 'path': path}
    response = requests.post(YA_LINK, cookies=COOKIES, headers=HEADERS, json=json_data).json()

    return response['results'][0]['data']['collections']['filterValue']

def main():
    data_frame:dict = {}
    urls = read_file(file='links.xlsx')
    lists = parse_urls(urls=urls)

    for list_data in lists:
        collection_name:str = list_data[1].split('/')[1].replace('catalog--', '')
        data = get_json_data(nid=list_data[0], path=list_data[1])
        brands:list[str] = []

        for key in data.keys():
            brands.append(data[key]['value'])
        
        data_frame[collection_name] = brands
    
    DataFrame(data_frame).to_excel('result.xlsx')

if __name__ == "__main__":
    main()