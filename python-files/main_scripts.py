from datetime import datetime
import os
import csv
import time
import argparse
import requests
import urllib3
import json
import pandas as pd
import concurrent.futures
import concurrent
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Use absolute path for the output file
#OUT_PERSON_DATA_FILE = os.path.join(os.getcwd(), time.strftime('%B%d%H%M.csv'))
ALL_DATA=[]

HEADER = {
    'authority': 'vinelink-mobile.vineapps.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'origin': 'https://vinelink.vineapps.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'x-vine-application': 'VINELINK',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'accept-language': 'en;q=0.9,en-US;q=0.8',
}

MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def get_formatted_date(date_text, age):
    if '*' in date_text:
        month = MONTHS[str(date_text.split()[0]).lower()]
        day = 1
        year = int(datetime.now().strftime("%Y"))-age
        return datetime.now().replace(year, month, day).strftime("%m/%d/%Y")
    else:
        date_text = date_text.lower()
        month, day, year = date_text.split(' ')
        month = int(MONTHS[month])
        day = int(day.strip(','))
        return '{:02}/{:02}/{}'.format(month, day, year)

import functools

# Add a simple cache decorator
def cache_result(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

# Create a session object to reuse connections
session = requests.Session()
session.headers.update(HEADER)
session.verify = False




@cache_result
def _get_bail_amount(person_id):
    d = {}
    url = "https://app5.lasd.org/iic/LoadCaseInfo"

    payload = f"draw=1&columns%5B0%5D%5Bdata%5D=FULL_BCA_CASE_NO&columns%5B0%5D%5Bname%5D=FULL_BCA_CASE_NO&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=BCA_CASE_NO&columns%5B1%5D%5Bname%5D=BCA_CASE_NO&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=COURT_NAME&columns%5B2%5D%5Bname%5D=COURT_NAME&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=COURT_ADDRESS&columns%5B3%5D%5Bname%5D=COURT_ADDRESS&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=COURT_CITY&columns%5B4%5D%5Bname%5D=COURT_CITY&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=BCA_BAIL_AMO1&columns%5B5%5D%5Bname%5D=BCA_BAIL_AMO1&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=BCA_TOT_FINE1&columns%5B6%5D%5Bname%5D=BCA_TOT_FINE1&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=BCA_NEXT_COURT_DATE_1&columns%5B7%5D%5Bname%5D=BCA_NEXT_COURT_DATE_1&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=BCA_DATE_OF_SENTENCE&columns%5B8%5D%5Bname%5D=BCA_DATE_OF_SENTENCE&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=BCH_LENGTH_OF_SENTENCE&columns%5B9%5D%5Bname%5D=BCH_LENGTH_OF_SENTENCE&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B10%5D%5Bdata%5D=BCA_DISP_CODE&columns%5B10%5D%5Bname%5D=BCA_DISP_CODE&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B11%5D%5Bdata%5D=FULL_BCA_CASE_NO&columns%5B11%5D%5Bname%5D=&columns%5B11%5D%5Bsearchable%5D=false&columns%5B11%5D%5Borderable%5D=false&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=-1&search%5Bvalue%5D=&search%5Bregex%5D=false&bkgNum={str(person_id)}"
    headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=d4li1v4rppamfstyt1jmzgrq; __RequestVerificationToken_L2lpYw2=LcdLFkTc5NcBc-kjF0DdkmsMMH8np5do4gfS3GlkT9Rmt316eOOxWQ5JMy8zXJRZrPvGKlS4JYDm8RoVKHT5nqyzPm6i_somBZVP8VCpFBU1; TS0117a92f=01fffec8367a24940a2df8c937dfdb5d664c27b400b45d68859d1cc4b294e9aea90ccf875bc3f349a5418664ef05914a8f99c80e43a5da3baf322bd7295ce5400ab0135406dd7f4110243e657c25d5125fc8216483; TS0117a92f=01fffec8364ec4ea7e81b5ebf889d0bce31456f0d9dc3fbe6dcde74eba37ff033cbc703415eaab79c15891e58f4a35314f7e4c3115c2a831a8cb076fe30bc27c70fac2c097b5a7d24acdef68f2dc75d6d4f8b396ff',
            'DNT': '1',
            'Origin': 'https://app5.lasd.org',
            'Referer': 'https://app5.lasd.org/iic/Details',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        #print(response.text)
        response.raise_for_status()

        if response.status_code == 200:
        
            resp = response.json()
            data = resp['data'][0]
            # print(data)
            bail_amount_str = data['BCA_BAIL_AMO1']
            # bail_amount_sum = float(bail_amount_str.replace(',', ''))

            bail_amount_sum = 0  # Default to 0
                    
            # Handle different possible values for bail amount
            if bail_amount_str and bail_amount_str.strip():
                # Remove commas and try to convert to float
                cleaned_str = bail_amount_str.replace(',', '').strip()
                try:
                    bail_amount_sum = float(cleaned_str)
                except ValueError:
                    # If conversion fails, it's a text value like "NO BAIL"
                    # Store the original string or a specific value based on your requirements
                    bail_amount_sum = bail_amount_str

            d['Bail Amount'] = bail_amount_sum
            return d

        else:
            print(f"Request failed for ID: {person_id}")
            d['Bail Amount'] = ''
            return d

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(e)
        d['Bail Amount'] = ''
        return d




def _get_person_info(person_id, second_person_id):
    d = {}
    header = HEADER.copy()
    header['referer'] = 'https://vinelink.vineapps.com/search/persons;limit=20;offset=0;showPhotos=false;' \
                        'isPartialSearch=false;siteRefId=CASWVINE;personContextRefId={}'.format(person_id)
    params = (
        ('addImageWatermark', 'true'),
        ('includeRegistrantInfo', 'true'),
        ('includeCustomDisplayInfo', 'true'),
        ('includeChargeInfo', 'true'),
    )

    try:
        response = requests.get(
            'https://vinelink-mobile.vineapps.com/api/v1/guest/persons/offenders/' +
            str(second_person_id),
            headers=header, params=params, timeout=10
        )
        
        if response.status_code != 200:
            return d
            
        try:
            data = response.json()
            # print(f'data in _get_person_info(): {data}')
        except ValueError:
            try:
                data = json.loads(response.content.decode('utf-8'))
                # print(f'data in _get_person_info(): {data}')

            except:
                return d

        try:
            d['Book Date'] = data['offenderInfo']['bookedDate']
        except KeyError:
            d['Book Date'] = ''

        try:
            for location in data['locations']:
                if location['locationId'] != 507:
                    d['Location'] = location['locationName']
                    break
            else:
                d['Location'] = ''
        except KeyError:
            d['Location'] = ''
    except requests.exceptions.RequestException:
        pass

    return d

def get_person_info(person_id):
    out_list = []
    params = (
        ('limit', '20'),
        ('offset', '0'),
        ('showPhotos', 'false'),
        ('isPartialSearch', 'false'),
        ('siteRefId', 'CASWVINE'),
        ('personContextRefId', str(person_id)),
        ('includeJuveniles', 'false'),
        ('includeSearchBlocked', 'false'),
        ('includeRegistrantInfo', 'true'),
        ('addImageWatermark', 'true'),
        ('personContextTypes', ['OFFENDER', 'DEFENDANT']),
    )
    header = HEADER.copy()
    header['referer'] = 'https://vinelink.vineapps.com/search/persons;limit=20;offset=0;showPhotos=false;' \
                        'isPartialSearch=false;siteRefId=CASWVINE;personContextRefId={}'.format(person_id)

    try:
        response = requests.get(
            'https://vinelink-mobile.vineapps.com/api/v1/guest/persons',
            headers=header, params=params, verify=False, timeout=10
        )
        
        # print("Response status for ID {}: {}".format(person_id, response.status_code))
        
        if response.status_code != 200:
            return out_list
            
        try:
            person_data = response.json()
            # print(f'person_data: {person_data}')
        except ValueError:
            try:
                person_data = json.loads(response.content.decode('utf-8'))
                # print(f'person_data: {person_data}')
            except:
                return out_list

        for person in person_data['_embedded']['persons']:
            d = {'Booking ID': person_id}
            
            # Extract all person data at once to minimize try/except blocks
            try:
                d['Full Name'] = ' '.join(person['personName'].values()).strip()
                d['Date of Birth'] = get_formatted_date(person['dateOfBirth'], person['age'])
                d['Custody Status'] = person['offenderInfo']['custodyStatus']['name']
                d['Age'] = person['age']
                d['Gender'] = person['gender']['name']
                d['Race'] = person['race']['name']
                d['Custody Status Date'] = person['offenderInfo']['custodyStatusDate']
            except KeyError as e:
                # Just set empty values for missing keys
                missing_field = str(e).strip("'")
                if missing_field not in d:
                    d[missing_field] = ''
            
            # Get second person info and bail amount concurrently
            second_person_id = person['personContext']['contextId']
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                person_info_future = executor.submit(_get_person_info, person_id, second_person_id)
                bail_future = executor.submit(_get_bail_amount, person_id)
                
                d.update(person_info_future.result())
                d.update(bail_future.result())
            
            out_list.append(d)
            
            # Remove these two lines that cause duplication
            # d.update(_get_bail_amount(person_id))
            # out_list.append(d)

    except requests.exceptions.RequestException:
        pass
        
    return out_list



def start(context_id, npages, race=None, range_lower=None, range_high=None):
    ids = []
    for n in range(npages):
        _id = int(context_id) + n
        if context_id.startswith('0'):
            _id = '0' + str(_id)
        ids.append(_id)
    
    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {executor.submit(get_person_info, _id): _id for _id in ids}
        for future in concurrent.futures.as_completed(future_to_id):
            _id = future_to_id[future]
            try:
                person_info = future.result()
                if not person_info:
                    print(f"No Data Found for ID: {_id}")
                    continue
                
                print(f"Data Received: {_id}")
                ALL_DATA.append(person_info)
            except Exception as exc:
                print(f"ID {_id} generated an exception: {exc}")
    
    print("Scraping session is done.")

def generate_csv():
    # Flatten the data more efficiently
    flat_data = []
    for entry in ALL_DATA:
        if entry:  # Check if entry is not empty
            flat_data.extend(entry)
    
    # Define the desired header order
    fieldnames = [
       "Booking ID",
       "Full Name",
        "Date of Birth",
        "Custody Status",
        "Age",
        "Gender",
        "Race",
        "Custody Status Date",
        "Book Date",
        "Location",
        "Bail Amount"
    ]
    
    # Create DataFrame directly from flat_data
    df = pd.DataFrame(flat_data)
    
    # Only reindex if there are columns to reindex
    if not df.empty:
        df = df.reindex(columns=fieldnames)
    
    now = datetime.now()
    filename = now.strftime("%B%d%H%M") + ".csv"
    
    # Use more efficient CSV writing
    df.to_csv(filename, index=False, mode='w')


def main():
    parser = argparse.ArgumentParser(description='Scraping Jail Database')
    parser.add_argument('context_id', metavar='ID',
                       type=str, nargs=1, help='Context ID')
    parser.add_argument('npages', metavar='Pages', type=int,
                       nargs=1, help='Number of pages')
    parser.add_argument('--race', type=str, help='Race')
    parser.add_argument('--age', type=str, help='Age range (like 20-50)')
    args = parser.parse_args()

    if args.age:
        r_low, r_high = map(int, args.age.split('-'))
    else:
        r_low = 0
        r_high = 100

    start(args.context_id[0], args.npages[0], args.race, r_low, r_high)

    if len(ALL_DATA)>0:
        generate_csv()
    else:
        print("No data found")

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


if __name__ == '__main__':

    main()