# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 12:39:27 2025

@author: j.zeuschner
"""

from bs4 import BeautifulSoup
from xlsxwriter import Workbook
from datetime import timedelta, datetime
from requests import get

def weekend(date, last_day):
    for day in reversed(range(1, date.day-last_day)):
        plusdate = date
        plusdate -= timedelta(days=day)
        daten.append({
            'date': datetime.strftime(plusdate, "%Y-%m-%d"),
            'gbp': 0,
            'jpy': 0,
            'usd': 0
            })  
    return date.isocalendar().week
    
def new_month(date):
    daten.append({
        'date': 'Neuer Monat',
        'gbp': 'Neuer Monat',
        'jpy': 'Neuer Monat',
        'usd': 'Neuer Monat'
    })
    return date.month

def download(currency):
    url = f'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/{currency}.xml'
    r = get(url)
    print(r.text)
    with open(f"{currency}.xml", "w+") as f:
        f.write(r.text)
        f.close()

for i in ('gbp', 'jpy', 'usd'):
    download(i)

with open('gbp.xml', 'r', encoding='utf-8') as f:
    gbp = f.read()

with open('jpy.xml', 'r', encoding='utf-8') as f:
    jpy = f.read()

with open('usd.xml', 'r', encoding='utf-8') as f:
    usd = f.read()

gbp_soup = BeautifulSoup(gbp, 'xml').DataSet.Series.find_all()
jpy_soup = BeautifulSoup(jpy, 'xml').DataSet.Series.find_all()
usd_soup = BeautifulSoup(usd, 'xml').DataSet.Series.find_all()

daten = []
last_day = datetime.strptime('1999-01-04', '%Y-%m-%d').day
last_week = datetime.strptime('1999-01-04', '%Y-%m-%d').isocalendar().week
last_month = datetime.strptime('1999-01-04', '%Y-%m-%d').month
for num, eintrag in enumerate(gbp_soup):
    date = datetime.strptime(eintrag.attrs['TIME_PERIOD'], '%Y-%m-%d')
    print("date", date)
    gbp_rate = gbp_soup[num].attrs['OBS_VALUE']
    jpy_rate = jpy_soup[num].attrs['OBS_VALUE']
    usd_rate = usd_soup[num].attrs['OBS_VALUE']
    if date != datetime.strptime(jpy_soup[num].attrs['TIME_PERIOD'], '%Y-%m-%d'):
        print(f"{date} ist nicht gleich {jpy_soup[num].attrs['TIME_PERIOD']}")
    if date != datetime.strptime(usd_soup[num].attrs['TIME_PERIOD'], '%Y-%m-%d'):
        print(f"{date} ist nicht gleich {usd_soup[num].attrs['TIME_PERIOD']}")
    if date.day > last_day + 1:
    # if date.isocalendar().week != last_week:
        if date.month != last_month:
            last_week = weekend(date, last_day)
            last_month = new_month(date)
        last_week = weekend(date, last_day)
    elif date.month != last_month:
        last_month = new_month(date)
        if date.day > 1:
            last_week = weekend(date, 0)
    if date:
        daten.append({
            'date': datetime.strftime(date, "%Y-%m-%d"),
            'gbp': gbp_rate.replace(".",","),
            'jpy': jpy_rate.replace(".",","),
            'usd': usd_rate.replace(".",",")
        })
    last_day = date.day
# In Excel-Datei schreiben
today = datetime.today().strftime('%Y-%m-%d')

workbook = Workbook(f'Wechselkurse USD, GBP, JPY_{today}.xlsx')
worksheet = workbook.add_worksheet('Wechselkurse')

spalten = ['Datum', 'gbp', 'jpy', 'usd']

bold = workbook.add_format({'bold':True})

worksheet.set_column(0, 1, 12)

worksheet.write_row(0,0,spalten, bold)
for num, line in enumerate(daten):
    print([i[1] for i in line.items()])
    worksheet.write_row(num+1,0,[i[1] for i in line.items()])

workbook.close()


print(f"Export abgeschlossen: Wechselkurse USD, GBP, JPY_{today}.xlsx")