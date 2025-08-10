import requests  # scraping / API
import re  # regex for scraping
from currency_converter import CurrencyConverter  # currency conversion
from getpass import getpass  # input passwords securely

rb_user_token = None
def gen_rb_usertoken() -> str:
	if not rb_user_token:
		gen_user_token = input('User token (leave blank to generate): ')
		if not gen_user_token.strip():  # generate user token
			print('Info: This data will only get sent to Rebrickable')
			username = input('Rebrickable username or email: ')
			password = getpass('Rebrickable password: ')
			url = 'https://rebrickable.com/api/v3/users/_token/?key=' + rb_api_key
			data = {'username':username, 'password':password}
			response = requests.post(url, data = data)
			if response.status_code == 200:
				try:
					gen_user_token = str(response.json()['user_token'])
				except KeyError:
					print('RB Error: Could not generate user token (Bad data returned, data: ' + response.json() + ').')
					exit()
			else:
				print('RB Error: Could not generate user token (Bad HTTP status code:' + str(response.status_code) + ').')
				exit()
		return gen_user_token
	else:
		return str(rb_user_token)

currency_converter = CurrencyConverter()

rb_api_key = input('Enter your Rebrickable API key: ').strip()

# Input

set_num = input('Set Number (w/o -1 suffix): ')
price = input('Price; Syntax: CUR 1234.567 (e.g. USD 27.99) (default EUR): ')
try:
	price = currency_converter.convert(float(price.split(' ')[1]), price.split(' ')[0], 'USD')  # convert price to USD
except IndexError:  # assume EUR
	try:
		price = currency_converter.convert(price, 'EUR', 'USD')  # convert price to USD, assume EUR
	except ValueError:
		print('Error: Could not convert price input.')
		exit()
print('Your Price: USD ' + str(round(price, 2)) + '$')

# ppp (price per piece)

pcs = input('Number of pieces (type \'r\' to get from Rebrickable (requires Rebrickable account): ')
if pcs == 'r':
	print('\nGetting number of pieces...')
	url = 'https://rebrickable.com/api/v3/lego/sets/' + set_num + '-1/?key=' + rb_api_key
	response = requests.get(url)
	if response.status_code == 200:
		try:
			pcs = int(response.json()['num_parts'])
		except KeyError:
			print('RB Error: Could not get number of pieces (Bad data returned, data: ' + response.json() + ').')
	else:
		print('RB Error: Could not get number of pieces (Bad HTTP status code:' + str(response.status_code) + ').')
else:
	try:
		pcs = int(pcs)
	except ValueError:
		print('Error: Could not convert pieces input.')
print('Calculating ppp (price per piece)...')
print('Average ppp is USD' + str(round(price/int(pcs),2)) + '$')


# BL PartOut Value

# as the BrickLink API is only available to sellers (I've written support about this issue), a crawler needs to be used to crawl the prices out of the user-accessible page.
print('\nGetting BrickLink Part Out Value...')
url = 'https://www.bricklink.com/catalogPOV.asp?itemType=S&itemNo=' + set_num + '&itemSeq=1&itemQty=1&breakType=M&itemCondition=U&breakSets=Y#'  # construct url
response = requests.get(url, headers = {'User-Agent':'py requests lib'})  # get the html body
if response.status_code == 200:  # 200 means success
	html = response.content.decode()  # get html content
	bl_partout_value = float(re.findall('(US \$)(.*?)(<)', html)[0][1])  # regex to find the price, price will always be displayed in USD
	print('BrickLink Part Out Value: $' + str(bl_partout_value) + ' USD')
	print('BrickLink Part Out Value is ' + str(round(bl_partout_value / price, 2)) + '× your price')
else:  # quit as something has gone wrong
	print('Error ' + str(response.status_code) + ': Could not get BrickLink Part Out Value.')
	exit()

# BL sales average

# as the BrickLink API is only available to sellers (I've written support about this issue), a crawler needs to be used to crawl the prices out of the user-accessible page.
print('\nGetting BrickLink sales average...')
url = 'https://www.bricklink.com/catalogPG.asp?S=' + set_num + '-1'
response = requests.get(url, headers = {'User-Agent':'py requests lib'})
if response.status_code == 200:  # success
	html = response.content.decode()  # whole website
	bl_sales_average_raw = list(re.findall('(>Avg Price:)(.*?)([A-Z]{3})(.*?\.[0-9]{2,4})', html)[1][2:4])  # regex to find all average prices, then filter out the correct match, converted to an array for editing; [2:4]: results 2 to 3
	bl_sales_average_raw[1] = re.sub(',', '', bl_sales_average_raw[1])  # remove thousands separation
	bl_sales_average_raw[1] = bl_sales_average_raw[1].removeprefix('&nbsp;')  # remove leading non-breaking space
	print('BrickLink sales average: ' + bl_sales_average_raw[0] + ' ' + bl_sales_average_raw[1])
	bl_sales_average = currency_converter.convert(bl_sales_average_raw[1], bl_sales_average_raw[0], 'USD')  # convert raw data into USD
	print('BrickLink sales average: USD ' + str(round(bl_sales_average, 2)) + '$')
	print('BrickLink sales average is ' + str(round(bl_sales_average / price, 2)) + '× your price')
else:
	print('Error ' + str(response.status_code) + ': Could not get BrickLink sales average.')

# RB build calculation

answer = input('\nGet Rebrickable build results (requires Rebrickable account) (Y/n)? ')
if not answer.lower().strip('\n y'):  # answer: y or blank
	print('Getting Rebrickable build calculation...')
	rb_user_token = gen_rb_usertoken()
	url = 'https://rebrickable.com/api/v3/users/' + rb_user_token + '/build/' + set_num + '-1/?key=' + rb_api_key
	response = requests.get(url)
	if response.status_code == 200:
		try:
			rb_pct_owned = float(response.json()['pct_owned'])
			rb_missing = int(response.json()['num_missing'])
		except KeyError:
			print('RB Error: Could not retrieve build results (Bad data returned, data: ' + response.json() + ').')
			exit()
	else:
		print('RB Error: Could not retrieve build results (Bad HTTP status code:' + str(response.status_code) + ').')
		exit()
	print('You already own ' + str(round(rb_pct_owned,2)) + '% of the pieces in this set.')
	print('You are missing ' + str(round(100-rb_pct_owned,2)) + '% of the pieces in this set.')
	print('You are missing ' + str(rb_missing) + ' pieces from this set.')
else:
	print('Skipping Rebrickable build calculation...')

# RB ALTERNATE BUILDS

answer = input('\nGet Rebrickable alternate builds (MOCs) (requires Rebrickable account) (Y/n)? ')
if not answer.lower().strip('\n y'): # answer: y or blank
	print('Getting Rebrickable alternate builds (MOCs)...')
	url = 'https://rebrickable.com/api/v3/lego/sets/' + set_num + '-1/alternates/?key=' + rb_api_key
	response = requests.get(url)
	if response.status_code == 200:
		try:
			rb_num_alternates = int(response.json()['count'])
		except KeyError:
			print('RB Error: Could not get alternate builds (Bad data returned, data: ' + response.json() + ').')
			exit()
	else:
		print('RB Error: Could not get alternate builds (Bad HTTP status code:' + str(response.status_code) + ').')
		exit()
	print('There are ' + str(rb_num_alternates) + ' alternative models for this set on Rebrickable')
else:
	print('Skipping Rebrickable alternate builds calculation...')

print()
print()
print('Disclaimer:')
print()
print('This tool is used at your own risk. I do not guarantee that it is correct.')
print('All data is sourced from BrickLink or Rebrickable')
print()
print('Rebrickable® is a trademarked term owned by Rebrickable Pty Ltd.')
print('BrickLink is a trademark of the LEGO Group. © 2025 The LEGO Group. All rights reserved')
print('LEGO® is a trademark of the LEGO Group of companies which does not sponsor, authorize or endorse this tool')