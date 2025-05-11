
import time
import requests
from requests.packages.urllib3.util.retry import Retry 
from requests.adapters import HTTPAdapter
import random
import string
import os
from colorama import Fore, Style, init
import base64
init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_intro():
    clear_screen()
    print(r"""
 __  __    _    ___ ____   ___  _   _  
|  \/  |  / \  |_ _/ ___| / _ \| \ | | 
| |\/| | / _ \  | |\___ \| | | |  \| | 
| |  | |/ ___ \ | | ___) | |_| | |\  | 
|_|  |_/_/   \_\___|____/ \___/|_| \_| 

            by @enx69 | 3$ 
""")
    time.sleep(3)
    clear_screen()

show_intro()

def main():
    user_id, user, id, request_count, chosen_complaint_type = get_user_input( )
    proxies = [
    {"http": "http://78.110.195.242:7080"},
    {"http": "http://54.198.154.165:9999"},
    {"http": "http://172.104.30.222:8080"},
    {"http": "http://167.235.154.74:8080"},
    {"http": "http://37.252.7.112:3128"},
    {"http": "http://64.225.4.63:9990"},
    {"http": "http://158.69.73.79:9300"},
    {"http": "http://178.209.51.218:7829"},
    {"http": "http://145.40.68.197:9443"},
    {"http": "http://18.143.215.49:80"},
    {"http": "http://20.247.97.62:3129"},
    {"http": "http://111.178.11.20:8088"},
    {"http": "http://64.225.4.63:9988"},
    {"http": "http://129.232.134.107:4443"},
    {"http": "http://64.225.4.29:9815"},
    {"http": "http://202.86.138.18:8080"},
    {"http": "http://186.121.235.222:8080"},
    {"http": "http://147.135.54.182:3128"},
    {"http": "http://102.213.87.52:8080"},
    {"http": "http://47.90.82.199:3128"},
    {"http": "http://8.219.97.248:80"},
    {"http": "http://39.105.33.197:7890"},
    {"http": "http://185.98.23.229:3128"},
    {"http": "http://20.200.218.239:8080"},
    {"http": "http://64.225.8.121:9979"},
    {"http": "http://185.191.236.162:3128"},
    {"http": "http://200.105.215.22:33630"},
    {"http": "http://103.83.159.225:8443"},
    {"http": "http://184.181.217.220:4145"},
    {"http": "http://132.148.75.242:20781"},
    {"http": "http://174.77.111.197:4145"},
    {"http": "http://72.210.221.197:4145"},
    {"http": "http://142.54.239.1:4145"},
    {"http": "http://192.111.137.37:18762"},
    {"http": "http://72.210.252.137:4145"},
    {"http": "http://67.201.33.10:25283"},
    {"http": "http://72.49.49.11:31034"},
    {"http": "http://192.111.130.2:4145"},
    {"http": "http://138.68.109.12:7077"},
    {"http": "http://125.227.225.157:3389"},
    {"http": "http://184.178.172.11:4145"},
    {"http": "http://106.13.4.250:9000"},
    {"http": "http://91.121.48.221:38711"},
    {"http": "http://178.33.162.89:59490"},
    {"http": "http://218.64.255.198:7302"},
    {"http": "http://24.249.199.12:4145"},
    {"http": "http://195.39.233.14:44567"},
    {"http": "http://98.162.25.7:31653"},
    {"http": "http://1.180.0.242:7302"},
    {"http": "http://67.201.59.70:4145"},
    {"http": "http://107.152.98.5:4145"},
    {"http": "http://46.36.70.104:46964"},
    {"http": "http://98.170.57.249:4145"},
    {"http": "http://192.111.137.34:18765"},
    {"http": "http://38.242.143.44:1779"},
    {"http": "http://68.71.249.153:48606"},
    {"http": "http://199.58.185.9:4145"},
    {"http": "http://72.195.34.60:27391"},
    {"http": "http://141.94.161.174:8764"},
    {"http": "http://64.227.108.25:31908"},
    {"http": "http://222.71.131.131:1080"},
    {"http": "http://192.111.130.5:17002"},
    {"http": "http://174.77.111.198:49547"},
    {"http": "http://45.136.244.245:44531"},
    {"http": "http://174.77.111.196:4145"},
    {"http": "http://184.178.172.13:15311"},
    {"http": "http://68.1.210.189:4145"},
    {"http": "http://72.195.114.169:4145"},
    {"http": "http://206.220.175.2:4145"},
    {"http": "http://93.185.74.214:9080"},
    {"http": "http://192.111.138.29:4145"},
    {"http": "http://31.217.221.74:8192"},
    {"http": "http://98.188.47.150:4145"},
    {"http": "http://72.195.34.42:4145"},
    {"http": "http://98.181.137.83:4145"},
    {"http": "http://70.166.167.38:57728"},
    {"http": "http://142.54.235.9:4145"},
    {"http": "http://72.206.181.105:64935"},
    {"http": "http://184.181.217.201:4145"},
    {"http": "http://184.178.172.18:15280"},
    {"http": "http://104.37.135.145:4145"},
    {"http": "http://8.142.3.145:3306"},
    {"http": "http://192.111.139.163:19404"},
    {"http": "http://72.37.216.68:4145"},
    {"http": "http://117.251.103.186:8080"},
    {"http": "http://199.102.104.70:4145"},
    {"http": "http://68.183.55.211:37775"},
    {"http": "http://58.222.132.164:7300"},
    {"http": "http://51.83.190.248:19050"},
    {"http": "http://199.116.114.11:4145"},
    {"http": "http://98.162.25.4:31654"},
    {"http": "http://162.253.68.97:4145"},
    {"http": "http://104.200.135.46:4145"},
    {"http": "http://192.252.220.92:17328"},
    {"http": "http://31.220.4.240:18967"},
    {"http": "http://70.35.199.99:53984"},
    {"http": "http://68.71.247.130:4145"},
    {"http": "http://51.91.144.39:59191"},
    {"http": "http://185.86.5.162:8975"},
    {"http": "http://72.210.221.223:4145"},
    {"http": "http://142.54.232.6:4145"},
    {"http": "http://74.119.144.60:4145"},
    {"http": "http://69.61.200.104:36181"},
    {"http": "http://199.102.106.94:4145"}
]

    for i in range(request_count):
        random_site = random.choice(sites)
        if 'tg_feedback_appeal' in random_site['data']:
            random_site['data']['tg_feedback_appeal'] = random.choice(complaint_types[chosen_complaint_type]).format(user_id=user_id, user=user, id=id) 
            random_site['data']['tg_feedback_email'] = generate_random_email() 
            random_site['data']['tg_feedback_phone'] = generate_random_phone()
        else: 
            random_site['data']['name'] = user 
            random_site['data']['email'] = f"{user_id}@example.com" 
            random_site['data']['message'] = random.choice(complaint_types[chosen_complaint_type]).format(user_id=user_id, user=user, id=id)
        send_data_to_server(random_site, proxies, random_site['data'].get('tg_feedback_appeal') or random_site['data']['message'], random_site['data'].get('tg_feedback_email') or random_site['data']['email'], random_site['data'].get('tg_feedback_phone', ''))
        animate_sending(i + 1, request_count)
    input("Нажмите Enter для выхода...")   

def generate_random_phone():
    return f"+79{ ''.join( random.choice( '0123456789' ) for _ in range ( 9 ) ) }"

def generate_random_email():
    domains = [ "gmail.com", "mail.ru", "rambler.ru", "ya.ru" ]
    name_length = random.randint( 5, 10 )
    letters = "abcdefghijklmnopqrstuvwxyz1234567890"
    email_name = ''.join( random.choice( letters ) for _ in range (name_length ) )
    return f"{ email_name }@{random.choice( domains ) }"

def generate_random_string( length ):
    letters = string.ascii_lowercase
    return ''.join( random.choice(letters) for i in range( length ) )
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

complaint_types = {
    "Спам": [
        "Пользователь {user} ID: {user_id} использует чат для рассылки рекламы и спама, что нарушает правила сообщества. Прошу удалить его сессию и заблокировать возможность отправки нежелательных сообщений.",
        "Здравствуйте, хочу пожаловаться на {user} ID: {user_id}, он использует спам для продвижения своего канала из-за чего невозможно общаться в группе, прошу принять меры по удалению аккаунта. Спасибо",
        "Доброго времени суток, прошу принять меры по рассылке спама. ID: {user_id} пользователя.",
        "Жалоба на рассылку рекламы. Пользователь {user} с ID: {user_id} спамит по группам, прошу принять меры",
        "Hello, I want to complain about ID: {user_id}, he uses spam to promote his channel, which makes it impossible to communicate in the group, please take steps to delete the account. Thank you",
        "Good day, I ask you to take measures to send spam. ID: {user_id} of the user.",
        "Complaint about sending advertisements. User with ID: {user_id} is spamming groups, please take action"
    ],
    "Порнография": [
        "Добрый день, прошу заблокировать доступ к порнографическому контенту. Акаунту {user} с  ID: {user_id}. Проблема в том что он занимается продажей детской порнографией",
        "Здравствуйте, хочу подать жалобу на порнографию.  Пользиватель {user} с  ID: {user_id} продает детскую порнографию, прошу принять меры по удалению акаунта. Спасибо",
        "Данный пользиватель {user} с ID: {user_id} растространяет запрешеный детский контент (дп,цп) прошу вас удалить данный акаунт. Спасибо",
        "Good afternoon, please block access to pornographic content. Account with ID: {user_id}. The problem is that it sells child pornography",
         "Hello, I want to file a complaint about pornography. User ID: {user_id} sells child pornography, please take steps to delete the account. Thank you",
         "This user with ID: {user_id} distributes prohibited children's content (dp, cp), I ask you to delete this account. Thank you",
         "Пользователь {user_id} распространяет порнографические материалы. Прошу заблокировать его аккаунт за нарушение правил платформы. Ссылка на материалы: {id}",
                "Обнаружено распространение порнографии пользователем {user_id}. Прошу принять меры. Ссылка на материалы: {id}",
                "Добрый день, прошу заблокировать аккаунт с  ID: {user_id}. Проблема в том,что он занимается продажей детской порнографией, вот ссылка на нарушение: {id}",
                "Здравствуйте, хочу подать жалобу на порнографию.  Пользователь с  ID: {user_id} продает детскую порнографию,вот ссылка на нарушение:{id},прошу принять меры по удалению акаунта. Спасибо",
                "Данный пользователь с ID: {user_id} растространяет запрещеный детский контент (дп,цп) прошу вас удалить данный акаунт.Также ссылка на нарушение:{id}.Спасибо",
                "Добрый день, прошу заблокировать аккунт с айди: {user_id} за распространение порнографии, точнее этот человек размещает порнографию, а также детскую порнографию в чатах ({id}) и так далее, что может повлиять на психику людей, которые находятся в этих чатах, а также это нарушает вашу политику, прошу заблокировать данного человека, также на момент жалобы у этого человека на аватарке было неприличное фото, поэтому прошу вас отреагировать на это быстро и четко. Заранее спасибо!",
                         "Hello, I want to file a complaint about pornography. User with ID: {user_id} sells child pornography,link to violation: {id},please take steps to delete the account. Thank you",
                "Good afternoon, please block the account with ID: {user_id}. The problem is that he is selling child pornography.Link to violation: {violation_link}.",
                "This user with ID: {user_id} distributes prohibited children's content (dp, cp),and link to violation: {id},I ask you to delete this account. Thank you",
                "Good afternoon, I ask you to block the account with ID: {user_id} for distributing pornography, more precisely, this person posts pornography, as well as child pornography in chats and so on,link to violation: {id},which can affect the psyche of people who are in these chats, and also violates your policy, I ask you to block this person, also at the time of the complaint this person had an indecent photo on his avatar, so I ask you to respond to this quickly and clearly. Thank you in advance!" 
    ],
    "Фишинг": [
       "Здравствуйте, сообщаю о подозрительной попытке фишинга. Акк: {user} ID: {user_id}.",
        "Добрый день, прошу обратить внимание на пользивателя {user} с ID: {user_id} он создает фишинг сылки, прошу принять меры по удалению данного акаунта",
        "Жалоба на фишинг. Пожалуйста, примите меры. {user} с ID: {user_id} использует фишинг для получения личных данных других пользывателей, прошу принять меры по удалению акаунта. Спасибо",
        "Hello, I'm reporting a suspicious phishing attempt. ID: {user_id}.",
         "Good afternoon, please pay attention to the user with ID: {user_id}, he creates phishing links, please take measures to delete this account",
         "Phishing complaint. Please take action. ID: {user_id} uses phishing to obtain personal information of other users, please take action to delete the account. Thank you"    
    ],
    "Дианон": [
       "Здравствуйте уважаемая поддержка телеграмм,хочу пожаловаться на пользователя {user} с ID:{user_id} дело в том что он нарушает правила телеграмм, он продает услули деанона, занимается терроризмом , а еще хочу сообщить что он оскорбляет чужие личности! ",
    "Здравствуйте уважаемая поддержка. Пользователь {user} вашей платформы Telegram с ID: {user_id}, угрожает дean0минuзациеё и свaтuнг0м. Требую удалить его аккаунт для безопасности других пользователей.",
    "Telegram, деактивируйте аккаунт {user} с ID: {user_id}, так как с него мне поступают многочисленные угрозы дean0н0м и сват0м, пугает также моих друзей, говорит, что сольёт их данные в сеть",
    "Данный пользователь {user} с ID: {user_id}, угрожает мне д0kсинг0м и свaтuнг0м. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопастности",
    "Telegram, деактивируйте аккаунт {user}, Id:  {user_id}, так как с него мне поступают многочисленные угрозы дean0н0м и сват0м, пугает также моих друзей, говорит, что сольёт их данные в сеть",
    "Данный пользователь {user}, id: {user_id}, угрожает мне     д0kсинг0м и свaтuнг0м. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопастности.",
       "Здравствуйте уважаемая поддержка. Пользователь {user} вашей платформы Telegram с id: {user_id}, угрожает дean0минuзациеё и свaтuнг0м. Требую удалить его аккаунт для безопасности других пользователей.",
       "Привествую Вас. Я являюсь родителем моего ребёнка и ему поступют угрозы об сливе данных с данного аккаунта {user}, id:{user_id}. Прошу удалить его аккаунт, так как теперь у моего ребёнка нарушена психика!",
       "Мне сказали, что телеграм самый безопасный мессенджер, только сейчас этот пользователь {user} id: {user_id} хочет слить мои данные.",
       "Hello, dear telegram moderator, I want to complain to you about a channel that sells doxing and swatting services ID: {user_id}, I ask you to take measures to delete the account.",
         "Good day, I ask you to take action on my complaint. The telegram user under ID: {id} is engaged in selling the services of Doxing and Swatting, I ask you to take action. Thank you.",
         "This account under ID: {user_id} is engaged in doxing and swatting, please take measures to delete the account."
    ],
    "Мошенничество": [
    "Уважаемая служба поддержки!Хочу сообщить о случае мошенничества. Пользователь {user} с ID: {user_id} пишет людям и предлагает услугу по выводу Notcoin на карту. После перевода Notcoin пользователь добавляет в черный список и отказывается переводить Notcoin. Прошу принять меры по удалению аккаунта. Спасибо!",
    "Добрый день!Прошу рассмотреть жалобу на мошенничество. Пользователь {user} с ID: {user_id} занимается мошенничеством, прошу принять меры по блокировке аккаунта.",
    "Обращаюсь к вам с жалобой на пользователя {user} с ID: {user_id}. Данный пользователь обманным путем получил от меня Notcoin, пообещав вывод на карту, но после получения средств заблокировал меня. Прошу принять меры и вернуть мои средства.",
    "Прошу обратить внимание на действия пользователя {user} с ID: {user_id}.Он предлагает услуги по выводу Notcoin, но после получения оплаты отказывается выполнять свои обязательства и блокирует пользователей. Это мошенник!",
    "ВНИМАНИЕ! Мошенник!Пользователь {user} с ID: {user_id} обманывает людей, предлагая несуществующие услуги. Будьте бдительны и не переводите ему свои средства!",
    "Я стал жертвой мошенничества со стороны пользователя {user} с ID: {user_id}.Прошу принять меры по блокировке его аккаунта и возврату моих средств.",
    "Требую наказать мошенника {user} с ID: {user_id}!Он обманул меня и многих других пользователей. Прошу принять меры!",
    "Обращаюсь к вам с просьбой о помощи.Пользователь {user} с ID: {user_id} обманным путем завладел моими средствами. Прошу вернуть мои Notcoin и заблокировать мошенника.",
    "Сколько можно терпеть мошенников на вашей платформе? Пользователь с ID: {user_id} продолжает обманывать людей. Прошу принять срочные меры!",
    "Dear support service, I want to report a case of fraud. A user with ID: {user_id} writes to people and offers a service to help them withdraw notcoin to a card. After transferring the notcoin, the user is blacklisted and refuses to transfer the notcoin, I ask you to take measures to delete the account.  Thank you",
         "Good afternoon, I ask you to consider a complaint about fraud. The user with ID: {user_id} is engaged in fraud, I ask you to take measures to assign the account.",
         "Fraud complaint against user ID: {user_id}. Please take action."
    ],
        "Премиум": [
        "Good afternoon Telegram support! Account ID: {user_id} purchased premium in your messenger to send spam messages and bypass Telegram restrictions. Please check this complaint and take action!"        
        ],
        "Домогательство": [
        "I ask you to delete user ID: {user_id}, he writes to my friends and asks them to send their intimate photos, please take action",
         "I ask you to delete user ID: {user_id}, he writes to my friend who is 15 years old and asks for intimate photos, I ask you to take punitive measures.  Thank you",
         "User ID: {user_id}, writes to minors and asks for intimate photographs, please take punitive measures.",
         "User ID: {user_id}, writes to my underage friends and asks for intimate photos, please take punitive measures.",
         "User ID: {user_id}, writes to my underage friends and asks them to send him intimate photos, I ask them to take punitive measures.",
         "User ID: {user_id}, writes to my friends and asks them to send him intimate photos, I ask them to take punitive measures.  Thank you"
            ],
            "Религия": [
            "User ID: {user_id} provokes people into conflicts, and also affects religion for the sake of conflict, I ask you to take action against this user",
         "User ID: {user_id} provokes people into conflicts, please take action.  Thank you",
         "User ID: {user_id} provokes people into conflicts by affecting religions, please take measures to remove this user",
         "I ask you to delete user {user} ID: {user_id}, he provokes other users into conflicts by touching on religions and this is obscene behavior. Please treat with understanding and take punitive measures"],
         "Канал": [
         "Hello, Telegram support! I want to file a complaint against the Telegram channel link: {id}, this channel distributes methods of doxing, hacking, and swatting. Please remove this channel. Thank you.",
        "Good afternoon, I want to complain about the telegram channel link: {id}, this channel publishes personal information of users, please take measures to delete the channel. Thanks.",
        "This channel: channel link {id} published my personal information without my consent. Please take action!",
        "I want to complain about the channel: channel link {id}. In the post from the date of publication, my photos and full name were published without my knowledge and consent. I ask you to remove the publication and take action against the channel that violates the confidentiality of users.",
        "Channel link {id} violates the rules of the Telegram platform by publishing personal information of users without their consent. I demand action!"],
        "Группа": [
        "Hello, Telegram Support, I want to file a complaint against the group with ID: {id} for the reason: distribution of prohibited content. Please take action to block the group!",
        "Good day, I ask you to take action on my complaint. Group ID: {id} is used to distribute illegal materials, please block the group. Thanks!"
        "I want to complain about group ID: {id} for violating community guidelines, please take action."
        ],
        "Вирт" : [
        "Good afternoon, Telegram support! Account {user} ID: {user_id} uses a virtual number purchased on the website for number activation. It has nothing to do with the number, the number has nothing to do with it. Please sort this out. Thanks in advance!",
        ],
        "Насилие": [        
        "Hello, Telegram support! I want to report a case of animal cruelty. User ID: {id} has shared content depicting animal abuse. I urge you to take immediate action and remove the content/block the user.",
        "I am writing to report a disturbing instance of animal abuse that I encountered on Telegram. User ID: {id} is responsible for sharing this content. I kindly request you to investigate this matter and take appropriate action to prevent further harm to animals."],
        "Сессия": [
        "Здраствуйте,меня взломали и выкинули с аккаунта {user}. Теперь Я не могу зайти на аккаунт так как мгновенно выкидывают меня с аккаунта. Прошу помогите, удалите аккаунт или обнулите сессии, там было очень много важной информации. Вот мой ID: {user_id}",
                "Здраствуйте, я попался на фишинг ссылку и меня как то взломали, на моем аккаунте {user} было очень много важных вещей, поэтому прошу вас обнулите пожалуйста сессию или же удалите аккаунт.Вот мой айди: {user_id}",
                "Здравствуйте, у меня украли аккаунт {user} с айди {user_id}, при попытке зайти на него, тот кто украл аккаунт не даёт мне зайти и отключает мою сессию, прошу вас пожалуйста отключить все сессии на данном аккаунте.",
                "Hello, I fell for a phishing link and somehow got hacked, there were a lot of important things on my account {user}, so I ask you to reset the session or delete the account. Here is my ID: {user_id}",
                "Hello, my account {user} with ID {user_id} was stolen, when I try to log into it, the one who stole the account does not allow me to log in and disables my session, I ask you to please disable all sessions on this account.",
                "Здраствуйте,меня взломали и выкинули с аккаунта {user}. Теперь Я не могу зайти на аккаунт так как мгновенно выкидывают меня с аккаунта. Прошу помогите, удалите аккаунт или обнулите сессии, там было очень много важной информации. Вот мой ID: {user_id}"
        ],
}       

def get_user_input ():
    clear_screen ()
    user_id = input( Fore.CYAN + "   Введите ID: " + Style.RESET_ALL )
    user = input( Fore.CYAN + "   Введите @: " + Style.RESET_ALL ) 
    id = input( Fore.CYAN + "   Введите cсылку на нарушение ( или для сноса канала/группы): " + Style.RESET_ALL )
    request_count = int( input( Fore.CYAN + "   Введите количество отправок: " + Style.RESET_ALL ) )
    print(Fore.CYAN + "   Выберите тип жалобы:" + Style.RESET_ALL)
    for i, complaint_type in enumerate(complaint_types.keys()):
        print(f"   {i+1}. {complaint_type}")
    choice = int( input( Fore.CYAN + "   Выберите номер типа жалобы: " + Style.RESET_ALL ) ) - 1 
    chosen_complaint_type = list( complaint_types.keys() )[choice]
    return user_id, user, id, request_count, chosen_complaint_type 

RETRY_STRATEGY = Retry (
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1,
    respect_retry_after_header=True,
)

sites = [
    {
        'url': 'https://telegram.org/support?setln=ru',
        'data': {
            'tg_feedback_appeal': '...',  
            'tg_feedback_email': '...',
            'tg_feedback_phone': '...'
        }
    },
    {
        'url': 'https://telegram.org/support',
        'data': {
            'name': '...',
            'email': '...',
            'message': '...'
        }
    }       
]

def send_data_to_server( data, proxies, cause, email, phone ):
    session = requests.Session()
    session.mount( "https://", HTTPAdapter( max_retries=RETRY_STRATEGY ) )
    headers = {

           #XD

    }
    try:
        proxy = random.choice( proxies )
        response = session.post( data['url'], headers=headers, data=data['data'], proxies=proxy, timeout=10 )
        response.raise_for_status()
        phone_info = f", phone: {phone}" if phone else ""
        print( f"[{Fore.GREEN}+{Style.RESET_ALL}] Запрос отправлен на {data['url']}  с причиной: {cause}, email: {email}{phone_info} отправлен через прокси {proxy}!" )
    except requests.exceptions.RequestException as e:
        print( f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка при отправке запроса на {data['url']} через прокси {proxy}: {e}" )

def animate_sending( current, total ):
    print( f"Идет отправка {current} из {total}", end="\r" )
 

if __name__ == "__main__":
    main()
