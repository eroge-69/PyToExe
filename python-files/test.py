import csv
import requests
from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re
import pandas as pd

#cp949 에러 발생시 csv파일 인코딩을 메모장에서 ANSI로 변경
## file_name : 파워링크 검색 키워드 목록
## find : 탐색할 업체
file_name = "keyword.csv"
find = "치킨"

f = open(file_name,'r', encoding="utf-8")
df = pd.read_csv(f)
keywords = df['이름']

## PC 버전 크롤링
data = []

url = 'https://ad.search.naver.com/search.naver?where=ad&x=0&y=0&query='

for keyword in keywords:
    base_url = url+quote_plus(keyword)

    response = requests.get(base_url)

    if response.status_code == 200:
      soup = BeautifulSoup(response.content, 'html.parser')

    items = soup.find_all(attrs={'class':'lnk_tit'})

    rank = 1
    temp = 0

    for item in items[:10]:#10위까지만 탐색
      serial = item.get_text()
      #print(serial[:10])
      if "네네치킨" in serial:
          temp = rank
      rank = rank+1

    data.append([keyword,temp])
    

# 결과 저장
result = pd.DataFrame(data, columns=['Name','Rank'])
print(result)
result.to_csv('result.csv', encoding='euc-kr')