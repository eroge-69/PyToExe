'''
in this version i added session
the way requests is made is completely different
requesting url logics goes like this:
1- make a request to the login page
2- extract the cookies from the response
3- create a session and add the cookies to it
4- make a request to the url you want to check
5- close the session


'''

import colorama , requests , time
import concurrent.futures

colorama.init(autoreset=True)

print('''
███████╗ █████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
█████╗  ███████║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██╔══╝  ██╔══██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
███████╗██║  ██║    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚══════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
''')

print('\n\n')






sleepTime = int(input("Enter waiting time : "))
link = 'https://signin.ea.com/p/ajax/user/checkEmailExisted?requestorId=portal&email='

def CheckEmail(email):
    while True:
        invalid = 0
        try:

            origin_url = "https://signin.ea.com/p/ajax/user/checkEmailExisted?requestorId=portal&email="
            useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'

            while True:
                try :
                    response = requests.get(origin_url + email, headers={'User-Agent': useragent} )
                    res = requests.Session()
                    res.headers['Cookie'] = f'''JSESSIONID={response.cookies.get('JSESSIONID')}; signin-cookie={response.cookies.get('signin-cookie')}'''
                    res.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                    while True:
                        try :
                            response = res.get(origin_url + email, headers={'User-Agent': useragent})
                            res.close()
                            if len(response.text) > 5:
                                json_data = response.json()
                                break
                            else:
                                #print('Error 1')
                                pass
                        except :
                            #print('Error 2')
                            pass
                    break


                except Exception as e:
                    #print('Error 3')
                    #print(e)
                    pass
            #print(json_data)
            if json_data['message'] == "register_email_existed":
                print(f'{colorama.Fore.GREEN}Email is Linked: {email}')
                with open('linked_emails.txt', 'a') as f:
                    f.write(f'{email}\n')
                break
            elif json_data['message'] == "register_email_invalid":
                #print("invalid email")
                invalid += 1
                if invalid > 10:
                    with open('invalid_emails.txt', 'a') as f:
                        f.write(f'{email}\n')
                    break
                pass

            elif json_data['message'] == "register_email_not_existed":
                #print("not existed")

                break

            else:
                #print(json_data)
                #print(f'{colorama.Fore.RED}Email is not Linked: {email}')
                print('Error 10')
                pass
        except Exception as e:
            if 'value: line 1 column 1 (char 0)' in str(e):
                #print('Error 11')
                pass
                
            else:
                #print(f'{colorama.Fore.RED}Error: {e}')
                print('Error 12')
                pass

            #print(f'{colorama.Fore.RED}Error: {e}')

            # with open('error.txt', 'a') as f:
            #     f.write(f'{email}\n')

# Generator function to read emails from file
def read_emails():
    with open('emails.txt', 'r') as f:
        for line in f:
            email = line.strip()
            yield email


emails = read_emails()
max_concurrent_requests = int(input("threads : "))
#interval = float(input("interval (in seconds): "))

while True:
    emailsList = []
    for i in range(max_concurrent_requests):
        try:
            emailsList.append(next(emails).strip())
        except StopIteration:
            iterationIsDone = True
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(emailsList)) as executor:
        executor.map(CheckEmail, emailsList)
    print(f'{colorama.Fore.CYAN}Done checking {len(emailsList)} emails.')
    # print last email checked
    print(f'{colorama.Fore.CYAN}Last email checked: {emailsList[-1]}')
    time.sleep(sleepTime)


