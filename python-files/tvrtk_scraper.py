import requests
from bs4 import BeautifulSoup
import csv
import time

# Helper function for requests with retries
def get_with_retries(method, url, max_retries=3, delay=3, **kwargs):
    for attempt in range(max_retries):
        try:
            if method.lower() == 'get':
                return requests.get(url, **kwargs)
            else:
                return requests.request(method.upper(), url, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"Request error on {url}: {e}. Attempt {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise

existing_titles = set()  # Keep this in memory across all pages

def write_results_to_csv(results, existing_titles, filename='tvrtke.hr_.csv'):
    fieldnames = [
        'Title', 'Logo URL', 'Website URL', 'Social URL', 'Street Address', 'Postal Code', 'City', 'Country',
        'Phone Number', 'Phone/Fax', 'Responsible Person', 'Year of Establishment', 'Number of Employees', 'Account Number',
        'Mbs Number', 'Rating Value', 'Description', 'Product/Company Description'
    ]

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for row in results:
            title = row.get('Title')
            if title and title not in existing_titles:
                writer.writerow(row)
                existing_titles.add(title)

def parser(inside_soup, title, existing_titles):
    results = []
    # Description
    try:
        desc_div = inside_soup.find("div", class_="divShortDesc txtCenter rows4")
        desc_text = desc_div.get_text(strip=True)
    except:
        desc_text = ''

    # Logo URL
    logo_url = ''
    try:
        logo_div = inside_soup.find("div", id="FirmaPodaci_divLogo")
        if logo_div:
            img_tag = logo_div.find("amp-img") or logo_div.find("img")
            if img_tag and 'src' in img_tag.attrs:
                logo_src = img_tag['src']
                if '/Images/Web2/no-logo.png' not in logo_src:
                    logo_url = "https://www.tvrtke.hr" + logo_src
    except:
        logo_url = ''

    # Location info
    try:
        location_div = inside_soup.find("div", id="FirmaPodaci_divMjesto")
        postal_code = location_div.find("span", itemprop="postalCode").get_text(strip=True)
        city = location_div.find("span", itemprop="addressLocality").get_text(strip=True)
        country = location_div.find("span", itemprop="addressCountry").get_text(strip=True)
    except:
        postal_code = ''
        city = ''
        country = ''

    # Street address
    try:
        address_div = inside_soup.find("div", id="FirmaPodaci_divAdresa", itemprop="streetAddress")
        street_address = address_div.get_text(strip=True)
    except:
        street_address = ''

    # Phone number
    try:
        phone_a = inside_soup.find("a", class_="linkTel")
        phone_number = phone_a.find("span", itemprop="telephone").get_text(strip=True)
    except:
        phone_number = ''

    try:
        contact_div = inside_soup.find("div", id="FirmaPodaci_divKontaktOsoba")
        responsible_person = contact_div.find("span").get_text(strip=True)
    except:
        responsible_person = ''
    
    try:
        year_div = inside_soup.find("div", id="FirmaPodaci_divGodinaOsnivanja")
        year_of_establishment = year_div.find("span", itemprop="foundingDate").get_text(strip=True)
    except:
        year_of_establishment = ''

    try:
        opis_div = inside_soup.find("div", id="FirmaProizvodi_divOpis", itemprop="description")
        opis_text = opis_div.get_text(strip=True)
    except:
        opis_text = ''

    # Website and Social URLs
    website_url = ''
    social_url = ''
    try:
        web_div = inside_soup.find("div", id="FirmaPodaci_divWeb")
        if web_div:
            link_tags = web_div.find_all("a", class_="linkWWW")
            if link_tags:
                website_url = link_tags[0]['href'] if link_tags[0].has_attr('href') else ''
                if len(link_tags) > 1:
                    social_url = link_tags[1]['href'] if link_tags[1].has_attr('href') else ''
    except:
        website_url = ''
        social_url = ''

    # Number of Employees
    number_of_employees = ''
    try:
        employees_span = inside_soup.find("span", itemprop="numberOfEmployees")
        if employees_span:
            number_of_employees = employees_span.get_text(strip=True)
    except:
        number_of_employees = ''

    # Account Number
    account_number = ''
    try:
        account_div = inside_soup.find("div", id="FirmaPodaci_divBrojRacuna")
        if account_div:
            full_text = account_div.get_text(strip=True)
            if "Broj računa:" in full_text:
                account_number = full_text.replace("Broj računa:", "").strip()
    except:
        account_number = ''

    mbs_number = ''
    try:
        mbs_div = inside_soup.find("div", id="FirmaPodaci_divRegistracijskiBroj")
        if mbs_div:
            full_text = mbs_div.get_text(strip=True)
            if "MBS:" in full_text:
                mbs_number = full_text.replace("MBS:", "").strip()
    except:
        mbs_number = ''

    # Rating Value
    rating_value = ''
    try:
        rating_span = inside_soup.find("span", itemprop="ratingValue")
        if rating_span:
            rating_value = rating_span.get_text(strip=True)
    except:
        rating_value = ''

    # Phone/Fax Number
    phone_fax_number = ''
    try:
        phone_fax_div = inside_soup.find("div", id="FirmaPodaci_divTelFax")
        if phone_fax_div:
            phone_fax_span = phone_fax_div.find("span", itemprop="telephone")
            if phone_fax_span:
                phone_fax_number = phone_fax_span.get_text(strip=True)
    except:
        phone_fax_number = ''

    results.append({
        'Title': title,
        'Logo URL': logo_url,
        'Website URL': website_url,
        'Social URL': social_url,
        'Street Address': street_address,
        'Postal Code': postal_code,
        'City': city,
        'Country': country,
        'Phone Number': phone_number,
        'Phone/Fax': phone_fax_number,
        'Responsible Person': responsible_person,
        'Year of Establishment': year_of_establishment,
        'Number of Employees': number_of_employees,
        'Account Number': account_number,
        'Mbs Number': mbs_number,
        'Rating Value': rating_value,
        'Description': desc_text,
        'Product/Company Description': opis_text
    })
    write_results_to_csv(results, existing_titles)


def get_last_page(soup):
    try:
        pager_div = soup.find("div", class_="divPager txtCenter")
        if not pager_div:
            return 1
        a_tags = pager_div.find_all("a", class_="pager2")
        # The last page number is in the second-to-last <a> (the last one is usually the ">" next button)
        if len(a_tags) < 2:
            return 1
        last_page_a = a_tags[-2]
        last_page_num = int(last_page_a.get_text(strip=True))
        return last_page_num
    except Exception as e:
        return 1


url_template = "https://www.tvrtke.hr/Rezultati-pretrage,PID-4.aspx?M=&Z=0&D=0&P=&F=a&stranica={page}" #"https://www.tvrtke.hr/Rezultati-pretrage,PID-4.aspx?M=&Z=7&D=0&P=&F=&stranica={page}"

payload = {}
headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'priority': 'u=0, i',
#   'referer': 'https://www.tvrtke.hr/Rezultati-pretrage,PID-4.aspx?M=&Z=7&D=0&P=&F=&stranica=2',
  'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}

# Get the first page and determine the last page
response = get_with_retries('get', url_template.format(page=1), headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
last_page = get_last_page(soup)
print(f"Total pages-----: {last_page}")

for page in range(1, last_page + 1):
    print(f"Processing page {page}")
    response = get_with_retries('get', url_template.format(page=page), headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    time.sleep(3)

    # Find all main divs
    main_divs = soup.find_all("div", class_="divItemSlide2 roundCorners2 divShadow divInline txtLeft")
    for main_div in main_divs:
        for a_tag in main_div.find_all("a", href=True, title=True):

            inside_url = "https://www.tvrtke.hr" + a_tag["href"]
            title = a_tag["title"]
            print("-" * 50)
            print(title)
            print("href:", inside_url)

            inside_response = get_with_retries('get', inside_url, headers=headers, data=payload)
            inside_soup = BeautifulSoup(inside_response.text, "html.parser")
            time.sleep(3)
            parser(inside_soup, title, existing_titles)