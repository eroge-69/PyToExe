from telethon import TelegramClient, events, utils, sync, types
from random import choice
from datetime import datetime, timedelta
from asyncio import sleep
import time
import re
import requests
import time
import sys
from bs4 import BeautifulSoup
import os
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.types import Channel
from telethon.tl.functions.messages import ImportChatInviteRequest
from urllib.parse import urlparse
from telethon.errors import ChatAdminRequiredError
import asyncio
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
import psutil
from telethon.tl.functions.contacts import GetContactsRequest, DeleteContactsRequest

menutext = "<b>{}</b>\n\n⛧ команды спама\n<code>.Zenoath</code> + time + media + reply — спам в чат\n<code>.znh</code> + chat_id + time + media — спам по chat id\n<code>.tagger</code> + user_id + time + media + reply — теггер\n<code>.Zeno</code> + chat_id + user_id + time + media — теггер по chat id\n<code>.znv</code> + time + media + reply — календарь\n<code>.znnw</code> + chat_id + time + media — календарь по чат айди\n<code>.reply</code> + user_id + time + media // reply  — автоответчик\n<code>.rchange</code> + [shapka,media,time] + user_id — замена аргументов автоответчика\n<code>.cl</code> — выключить автоответчик на всех\n\n⛧ остальные команды\n<code>.list</code> + media // nothing — список роботы бота\n<code>.count</code> + reply — сколько слов в сообщении\n<code>.change</code> + reply на тхт — замена шаблонов в боте\n<code>.file</code> — шаблоны бота\n<code>.uptime</code> — узнать время роботы бота на хосте\n<code>.ping</code> — узнать пинг бота\n<code>.afk</code> + 1(on)/2(off) \ media \ reason — управление АФК статусом\n<code>.id</code> — узнать чат/юзер айди\n<code>.x0</code> + reply — сохранить ссылку на фото/видео\n\nthis chat id: <code>{}</code>\nyour user id: <code>{}</code>\nyour name: <code>{}</code>\nyour username: @{}</b>\n — <a href='tg://user?id=71598393'></a></b>"
shablon = ["\n"]

afk_photo = "https://i.pinimg.com/736x/c0/a8/81/c0a881647d4f9e6da6cc4974b5a3be51.jpg"
state = None
spam_state = {}
spam_state1 = {}
user_list = []
chatreply_list = []
start_time = time.time()
chats_to_greet = []
chats = {}
active_forwards = {} 
autoreply_list = []
autoreply_time = {}
last_reply_time = {}
autoreply_photo = {}
autoreply_shpk = {}
autoreply_shpk_chat = {}
autoreply_time_chat = {}
autoreply_list_chat = []
autoreply_photo_chat = {}
start = 10
tagger_chats = {}
tag_chats = {}
reason = "во славу кавалерии"
start1 = datetime.now()
lists = {}
mid = 'https://i.pinimg.com/736x/c0/a8/81/c0a881647d4f9e6da6cc4974b5a3be51.jpg'
name = "Zenoath bot cmd"
mh = 'https://i.pinimg.com/736x/c0/a8/81/c0a881647d4f9e6da6cc4974b5a3be51.jpg'
mlist = 'https://i.pinimg.com/736x/c0/a8/81/c0a881647d4f9e6da6cc4974b5a3be51.jpg'
State = {}

class Userbot():
    def __init__(self):
        self.api_id = 21523809
        self.api_hash = "577c0b97ee6a853cd08cda0d7b448508"
        self.client = TelegramClient('Grandeur', self.api_id, self.api_hash)
        self.client.start()
        self.forwarding_enabled = {}
        
        
        
        
    async def start(self):
        await self.client.start()

    async def get_args(self, msg):
        try:
            args = msg.message.message.split(maxsplit=1)[1]
            return args
        except IndexError:
            return None
    
    async def watcher(self, client, msg):
        if state is True:
            global user_list
            user_id = msg.sender_id
            if user_id not in user_list:
                if msg.is_private:
                    user_list.append(user_id)
                    time_now = datetime.now()
                    timing = time_now - start
                    time_string = str(timing)
                    time_result = time_string.split('.')[0]
                    await msg.reply(
                        "я в АФК уже <code>{}</code>\nпо причине: <code>{}</code>".format(time_result, reason),
                        file=afk_photo,
                        parse_mode='html'
                    )
                else:
                    pass
        
        user_id = msg.sender_id
        if user_id in autoreply_list:
            if user_id not in last_reply_time or time.time() - last_reply_time[user_id] >= autoreply_time[user_id]:
                last_reply_time[user_id] = time.time()
                await sleep(autoreply_time[user_id])
                if autoreply_shpk.get(user_id, ''):
                    await msg.reply(
                        autoreply_shpk[user_id] + " " + choice(shablon),
                        file=autoreply_photo[user_id]
                    )
                else:
                    await msg.reply(
                        choice(shablon),
                        file=autoreply_photo[user_id]
                    )
            else:
                pass
        else:
            pass
        

    async def afk_handler(self, client, msg):  
        try:
            global state, user_list, start, reason, afk_photo
            me = await self.client.get_me()  
            if msg.sender_id == me.id:  
                args = msg.text.split()[1:] 
                if not args:  
                    if state:  
                        status = "включен" 
                    else:  
                        status = "выключен" 
                    if afk_photo:  
                        media = f"медиа востановлено: <code>{afk_photo}</code>" 
                    else:  
                        media = "медиа не востановлено" 
                    return await msg.edit(f"статус афк: <code>{status}</code>\n{media}\nпричина перебування в АФК: <code>{reason}</code>", parse_mode='html')  
            
                if args[0] == '1':  
                    state = True  
                    start = datetime.now()
                    me = await self.client.get_me()  
                    user_list.append(
                        int(
                            me.id
                        )
                    )
                    return await msg.edit("<b>афк включен.</b>", parse_mode='html')  
                    b
            
                elif args[0] == '2':  
                    state = False  
                    start = 10  
                    user_list = []  
                    return await msg.edit("<b>афк выключен</b>", parse_mode='html')  
            
                elif 'https' in args[0]:   
                    afk_photo = args[0]   
                    return await msg.edit("<b>фото для афк заменено</b>", parse_mode='html')   
                     
                reason = ' '.join(args[0:])   
                return await msg.edit(f'причина прибываения в АФК заменено на: <code>{reason}</code>', parse_mode='html')   
        
            async def reason(msg): 
                try: 
                    global reason 
                    args = msg.text.split()[1:] 
                    if not args: 
                        return await msg.edit("причина прибывания в АФК: <code>{}</code>".format(reason), parse_mode='html') 
        
                    reason = ' '.join(args) 
                    await msg.edit('причина прибывания в АФК заменена на: <code>{}</code>'.format(reason), parse_mode='html') 
        
                except Exception as e: 
                    print(e) 
        
            async def set_photo(msg): 
                try: 
                    global afk_photo 
                    args = msg.text.split()[1:] 
                    if not args: 
                        return await msg.edit("<b>укажите аргументы (ссылка)</b>", parse_mode='html') 
        
                    afk_photo = args[0] 
                    await msg.edit("<b>фото для афк встановлено</b>", parse_mode='html') 
        
                except Exception as e: 
                    print(e)

        except Exception as e: 
            print(e)


    async def kalendar_handler(self, client, msg):
        try:
            reply = await msg.get_reply_message()
            args = await self.get_args(msg)
            if args is None:
                return await msg.edit(
                    "<b>команда введенна без аргументов.\nвикористовуйте rnw {time} {media}.</b>",
                    parse_mode='html'
                )
            time = int(args.split()[0])
            photo = str(args.split()[1])
            shapka = ' '.join(args.split()[2:])
            reply_id = None
            chat_id = msg.chat_id
            if not reply and 'https' not in photo:
                photo = None
            elif not reply and 'https' in photo:
                reply_id = None
            elif reply and 'https' not in photo:
                reply_id = reply.id
                photo = None
            elif reply and 'https' in photo:
                reply_id = reply.id

            orig_time = time
            await msg.edit(
                "{} {}".format(shapka, choice(shablon)),
                parse_mode='html'
            )
            for i in range(99):
                schedule_date = datetime.now() + timedelta(minutes=time)
                await msg.respond(
                    f"{shapka} {choice(shablon)}",
                    file=photo,
                    reply_to=reply_id,
                    schedule=schedule_date.timestamp()
                )
                time += orig_time
                await sleep(0)

            last_schedule_date = datetime.now() + timedelta(minutes=time)
            await msg.respond(
                f"{msg.text}",
                file=photo,
                reply_to=reply_id,
                schedule=last_schedule_date.timestamp()
            )
        except Exception as e:
            print(e)


    async def renewal_handler(self, client, msg):
        try:
            global spam_state
            args = await self.get_args(msg)
            if args is None:
                return await msg.edit("<b>аргументы не указаны</b>", parse_mode='html')
    
            reply = await msg.get_reply_message()
            chat_id = msg.chat_id
            time = int(args.split()[0])
    
            photo = str(args.split()[1]) if len(args.split()) > 1 else None
            shapka = ' '.join(args.split()[2:]) if len(args.split()) > 2 else ''
            spam_state[chat_id] = True
            await msg.edit('<b>запущено\nчтобы выключить пиши <code>.stop {}</code></b>'.format(chat_id), parse_mode='html')
    
            if chat_id in spam_state and spam_state[chat_id] is True:
                while True:
                    if chat_id not in spam_state or not spam_state[chat_id]:
                        del spam_state[chat_id]
                        break
                    if chat_id in spam_state:
                        if reply:
                            if photo:
                                try:
                                    await msg.respond(shapka + " " + choice(shablon), file=photo, reply_to=reply.id, parse_mode='html' )
                                except Exception as e:
                                    await msg.respond(shapka + " " + choice(shablon), reply_to=reply.id, parse_mode='html' )
                            else:
                                await msg.respond(shapka + " " + choice(shablon), reply_to=reply.id, parse_mode='html' )
                        else:
                            if photo:
                                try:
                                    await msg.respond(shapka + " " + choice(shablon), file=photo, parse_mode='html' )
                                except Exception as e:
                                    await msg.respond(shapka + " " + choice(shablon), parse_mode='html' )
                            else:
                                await msg.respond(shapka + " " + choice(shablon), parse_mode='html' )  
                    
                    await asyncio.sleep(time)
        except Exception as e:
            pass


    async def spam_handler(self, client, msg):  
        try:  
            global spam_state1  
            args = await self.get_args(msg)  
            
            if args is None:   
                return await msg.edit("<b>аргументы не указаны</b>", parse_mode='html')  
            
            chat_id = int(args.split()[0])  
            time = int(args.split()[1])  
            
            if len(args.split()) < 2:  
                return await msg.edit("<b>недостаточно аргументов</b>", parse_mode='html')  
            
            photo = args.split()[2] if len(args.split()) > 2 and 'https' in args.split()[2] else None  
            shapka = ' '.join(args.split()[3:]) if len(args.split()) > 3 else '' 
            
            spam_state1[chat_id] = True  
            await msg.edit('<b>запущено в чате {}\nчтобы выключить пиши <code>.rstop {}</code></b>'.format(chat_id, chat_id), parse_mode='html')  
            
            if chat_id in spam_state1 and spam_state1[chat_id] is True:  
                while True:  
                    if chat_id not in spam_state1 or not spam_state1[chat_id]:  
                        del spam_state1[chat_id]  
                        break  
                    
                    if chat_id in spam_state1:  
                        if photo:  
                            await self.client.send_file(chat_id, file=photo, caption=shapka + " " + choice(shablon), parse_mode='html' )  
                        else:  
                            await self.client.send_message(chat_id, shapka + " " + choice(shablon), parse_mode='html' )  
    
                    await asyncio.sleep(time) 
        except Exception as e: 
            pass


    async def autoreply_handler(self, client, msg):
        try:
            global autoreply_photo, autoreply_list, autoreply_time, autoreply_shpk
            args = msg.message.message.split(maxsplit=0)[0]
            
            if str(args.split()[0]) == '.reply':
                if msg.is_reply:
                    user_id = (await msg.get_reply_message()).sender_id
                    autoreply_list.append(user_id)
                    autoreply_shpk[user_id] = ' '.join(args.split()[1:]) 
                    autoreply_time[user_id] = 8
                    autoreply_photo[user_id] = None
                    await msg.edit(
                        '<b>запущено на пользователя <code>{}</code>\nчтоб выключить пиши <code>.creply</code></b>'.format(user_id),
                        parse_mode='html'
                    )
                else:
                    user_id = int(args.split()[1])
                    autoreply_list.append(user_id)
                    autoreply_time[user_id] = int(args.split()[2])
                    autoreply_photo[user_id] = str(args.split()[3]) if 'https' in args.split()[3] else None
                    autoreply_shpk[user_id] = ' '.join(args.split()[4:]) 
                    await msg.edit(
                        '<b>запущено\nчтоб выключить пиши <code>.creply {}</code></b>'.format(user_id),
                        parse_mode='html'
                    )
        
            elif str(args.split()[0]) == '.creply':
                if msg.is_reply:
                    reply_msg = await msg.get_reply_message() 
                    user_id = reply_msg.sender_id 
                    if user_id in autoreply_list:
                        autoreply_list.remove(user_id)
                        del autoreply_time[user_id]
                        del autoreply_photo[user_id]
                        await msg.edit(
                            f'<b>автоответчик выключен на пользователя <code>{user_id}</code></b>',
                            parse_mode='html'
                        )
                    else:
                        await msg.edit('<b>пользователь <code>{}</code> не находиться в списке</b>'.format(user_id), parse_mode='html')
                else:
                    args = msg.message.message
                    if args.startswith('.creply'):
                        if len(args.split()) > 1:
                            user_id = int(args.split()[1])
                            autoreply_list.remove(user_id)
                            del autoreply_time[user_id]
                            del autoreply_photo[user_id]
                            await msg.edit(
                                f'<b>Автоответчик выключен для пользователя <code>{user_id}</code></b>',
                                parse_mode='html'
                            )
                            del autoreply_shpk[user_id]
    

        except KeyError as e: 
            print(f"KeyError occurred: {e}")
        
        except ValueError as e:
            print(f"ValueError occurred: {e}")



    async def kalend_handler(self, event, msg):
        try:
            args = await self.get_args(msg)
            chat_id = int(args.split()[0])
            time = int(args.split()[1])
            photo = str(args.split()[2]) if len(args) > 2 else None
            shapka = ' '.join(args.split()[3:])
            orig_time = time
            
            if 'https' not in photo:
                photo = None
            await msg.edit(  
                f"календарь начал заполняться, чтобы повторить введите <code>{msg.text}</code>".format(shapka, choice(shablon)),  
                parse_mode='html'  
            )  
            initial_message = f"{shapka} {choice(shablon)}"
            if photo is not None:
                await self.client.send_file(chat_id, photo, caption=initial_message)
            else:
                await self.client.send_message(chat_id, initial_message)
            
            # Далее идет ваш код для заполнения календаря
            for i in range(100):
                schedule_date = datetime.now() + timedelta(minutes=time)
                if photo is not None:
                    await self.client.send_file(chat_id, photo, caption=shapka + " " + choice(shablon), schedule=schedule_date.timestamp())
                    time += orig_time
                    await sleep(0)
                else:
                    await self.client.send_message(chat_id, shapka + " " + choice(shablon), schedule=schedule_date.timestamp())
                    time += orig_time
                    await sleep(0)
    
            for i in range(1):
                schedule_date = datetime.now() + timedelta(minutes=time)
                await msg.respond(
                    f"{msg.text}",
                    file=photo,
                    schedule=schedule_date.timestamp()
                )
        except Exception as e:
            pass



    async def rchange_handler(self, client, msg):
        try:
            global autoreply_photo, autoreply_list, autoreply_time, autoreply_shpk
            args = msg.message.message.split(maxsplit=0)[0]
            
            if str(args.split()[0]) == '.rchange':
                action = str(args.split()[1])
                user_id = int(args.split()[2])
    
                if action == 'shapka':
                    autoreply_shpk[user_id] = ' '.join(args.split()[3:])
                    await msg.edit(
                        f'<b>Шапка для пользователя {user_id} змінена</b>',
                        parse_mode='html'
                    )
    
                elif action == 'media':
                    autoreply_photo[user_id] = str(args.split()[3]) if 'https' in args.split()[3] else None
                    await msg.edit(
                        f'<b>Медиа для пользователя {user_id} змінена на: {autoreply_photo[user_id]}</b>',
                        parse_mode='html'
                    )
    
                elif action == 'time':
                    autoreply_time[user_id] = int(args.split()[3])
                    await msg.edit(
                        f'<b>Задержка для пользователя {user_id} змінена на: {autoreply_time[user_id]} секунд</b>',
                        parse_mode='html'
                    )
    
        except KeyError as e:
            print(f"KeyError occurred: {e}")
    
        except ValueError as e:
            print(f"ValueError occurred: {e}")


    def run(self):
        @self.client.on(events.NewMessage(pattern=r'\.rrnw')) 
        async def kalend_handler_event(msg): 
            me = await self.client.get_me() 
            if msg.sender_id == me.id: 
                await self.kalend_handler(self.client, msg)
        
        @self.client.on(events.NewMessage(pattern=r'\.afk'))  
        async def afk_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                await self.afk_handler(self.client, msg)

        @self.client.on(events.NewMessage(pattern=r'\.renewal'))
        async def renewalspam_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                await self.renewal_handler(self.client, msg)
                
        @self.client.on(events.NewMessage(pattern=r'\.rsp'))
        async def spam_rhandler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                await self.spam_handler(self.client, msg)
            

        @self.client.on(events.NewMessage(pattern=r'\.rnw'))
        async def kalendar_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                await self.kalendar_handler(self.client, msg)

        @self.client.on(events.NewMessage(pattern=r'\.reply|\.creply'))
        async def autoreply_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                await self.autoreply_handler(self.client, msg)

        @self.client.on(events.NewMessage(pattern=r'\.rchange'))
        async def rchange_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                await self.rchange_handler(self.client, msg)

        @self.client.on(events.NewMessage(pattern=r'\.stop'))
        async def stop_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                global spam_state
                args = await self.get_args(msg)
                if args:
                    chat_id = int(args.split()[0])
                else:
                    chat_id = msg.chat_id
                if chat_id in spam_state:
                    spam_state[chat_id] = False
                    del spam_state[chat_id]
                    await msg.edit(
                        "<b>остановлено в чате <code>{}</code></b>".format(chat_id),
                        parse_mode='html'
                    )
                else:
                    await msg.edit(
                        "<b>чат с айди <code>{}</code> не найдено в словаре</b>".format(chat_id),
                        parse_mode='html'
                    )


        @self.client.on(events.NewMessage(pattern=r'\.off'))
        async def off_handler(msg): 
            me = await self.client.get_me() 
            if msg.sender_id == me.id: 
                global tagger_chats 
                args = await self.get_args(msg) 
                if args:
                    chat_id = int(args.split()[0]) 
                else:
                    chat_id = msg.chat_id
                if chat_id in tagger_chats: 
                    del tagger_chats[chat_id] 
                    await msg.edit( 
                        "<b>остановлено в чате <code>{}</code></b>".format(chat_id), 
                        parse_mode='html' 
                    ) 
                else: 
                    await msg.edit( 
                        "<b>чат с айди <code>{}</code> не найдено в словаре</b>".format(chat_id), 
                        parse_mode='html' 
                    )
        
        @self.client.on(events.NewMessage(pattern=r'\.rstop')) 
        async def stop_handler(msg): 
            me = await self.client.get_me() 
            if msg.sender_id == me.id: 
                global spam_state1 
                args = await self.get_args(msg) 
                if args:
                    chat_id = int(args.split()[0]) 
                else:
                    chat_id = msg.chat_id
                if chat_id in spam_state1: 
                    del spam_state1[chat_id] 
                    await msg.edit( 
                        "<b>остановлено в чате <code>{}</code></b>".format(chat_id), 
                        parse_mode='html' 
                    ) 
                else: 
                    await msg.edit( 
                        "<b>чат с айди <code>{}</code> не найдено в словаре</b>".format(chat_id), 
                        parse_mode='html' 
                    )


        @self.client.on(events.NewMessage(pattern=r'\.id|\.chatid|\.userid')) 
        async def id_handler(event): 
            global mid   
            me = await self.client.get_me() 
            msg = event.message 
            if msg.sender_id == me.id: 
                try: 
                    if msg.is_reply: 
                        reply_msg = await msg.get_reply_message() 
                        user_id = reply_msg.sender_id 
                        reply_id = reply_msg.id 
                        reply_to = reply_msg.id 
                        reply_msg.id = None 
                        caption = '<b>user id: <code>{}</code></b>'.format(user_id) 
                    elif len(msg.text.split()) > 1 and msg.text.split()[1].startswith('@'):  
                        entity = await self.client.get_entity(msg.text.split()[1])  
                        user_id = entity.id  
                        caption = '<b>user id: <code>{}</code></b>'.format(user_id)  
                    elif len(msg.text.split()) > 1 and msg.text.split()[1].startswith('t.me/'):  
                        entity = await self.client.get_entity(msg.text.split()[1])  
                        chat_id = entity.id
                        caption = '<b>chat id: <code>-100{}</code></b>'.format(chat_id)  
                    elif len(msg.text.split()) > 1 and msg.text.split()[1].startswith('https://t.me/'):  
                        entity = await self.client.get_entity(msg.text.split()[1])  
                        chat_id = entity.id
                        caption = '<b>chat id: <code>-100{}</code></b>'.format(chat_id)  
                    else:  
                        chat_id = msg.chat_id  
                        caption = '<b>chat id: <code>{}</code></b>'.format(chat_id)  
        
                    if msg.is_reply: 
                        if mid is not None:   
                            try: 
                                await self.client.send_file( 
                                    msg.chat_id, 
                                    file=mid, 
                                    caption=caption, 
                                    reply_to=reply_to, 
                                    parse_mode='html' 
                                ) 
                                await self.client.delete_messages(msg.chat_id, msg.id) 
                            except: 
                                sent_msg = await self.client.edit_message( 
                                    msg.chat_id, 
                                    msg.id, 
                                    text=caption, 
                                    parse_mode='html' 
                                ) 
                        else: 
                            sent_msg = await self.client.edit_message( 
                                msg.chat_id, 
                                msg.id, 
                                text=caption, 
                                parse_mode='html' 
                            ) 
                    elif len(msg.text.split()) > 1 and not any(link in msg.text.split()[1] for link in ['@', 'https://t.me/', 't.me/']):  
                        mid = msg.text.split()[1]   
                        await self.client.edit_message(  
                            msg.chat_id,  
                            msg.id,  
                            text="<b>медиа встановлено</b>",  
                            parse_mode='html'  
                        )
                        return 
                    if mid is not None and not msg.is_reply:   
                        await self.client.send_file(                
                            msg.chat_id,                
                            file=mid,              
                            caption=caption,             
                            parse_mode='html'                
                        )          
                        await self.client.delete_messages(msg.chat_id, msg.id)          
                    else:   
                        sent_msg = await self.client.edit_message( 
                            msg.chat_id,            
                            msg.id,           
                            text=caption,        
                            parse_mode='html'        
                        )   
                except Exception as e:   
                    sent_msg = await self.client.edit_message(
                        msg.chat_id,            
                        msg.id,           
                        text=caption,
                        parse_mode='html'        
                    )



        @self.client.on(events.NewMessage(pattern=r'\.uptime|\.ping')) 
        async def handle_commands(msg): 
            me = await self.client.get_me() 
            if msg.sender_id == me.id: 
                # Отримуємо аптайм бота 
                bot_runtime = int(time.time() - start_time) 
                bot_runtime_formatted = str(timedelta(seconds=bot_runtime)) 
        
                # Получение аптайм ПК 
                try: 
                    pc_runtime = int(time.time() - psutil.boot_time()) 
                    pc_runtime_formatted = str(timedelta(seconds=pc_runtime)) 
                except Exception as e: 
                    pc_runtime_formatted = "неизвестно" 
                
                ping_now = time.perf_counter_ns()  # Измеряем час перед выключением
                response = ( 
                    f'аптайм бота: <code>{bot_runtime_formatted}</code>\n' 
                    f'аптайм ПК: <code>{pc_runtime_formatted}</code>\n' 
                    '<b>пінг: <code>Измеряется..</code> ms</b>'
                )
                
                # Відправляємо початкове повідомлення
                message = await msg.edit(response, parse_mode='html')
        
                ping_time = round((time.perf_counter_ns() - ping_now) / 10**6, 2)  # Обчислюємо пінг
                # Оновлюємо повідомлення з фактичним значенням пінгу
                await message.edit(response.replace('вимірюється..', str(ping_time)), parse_mode='html')

        @self.client.on(events.NewMessage(pattern=r'\.tagger'))
        async def tagger_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                text = msg.message.message.split(maxsplit=1)[1]
                args = text.split()
                if args is None: 
                    return await msg.edit("<b>аргументы не указаны</b>", 
                    parse_mode='html')
                chat_id = msg.chat_id
                user_id = int(args[0])
                time_sleep = int(args[1])
                
                
                photo = args[2] if len(args) > 2 and 'https' in args[2] else None
                caption = ' '.join(args[3:]) if len(args) > 3 else ''
                reply_to_msg = await msg.get_reply_message()
                if reply_to_msg:
                    chat_id = reply_to_msg.chat_id
                
                await msg.edit('<b>Запущено\nЧтобы выключить пиши <code>.off {}</code></b>'.format(chat_id), parse_mode='html')
                
                tagger_chats[chat_id] = True
                while chat_id in tagger_chats:
                    if photo:
                        await self.client.send_file(
                            chat_id,
                            file=photo,
                            caption=f"{caption} <a href='tg://user?id={user_id}'>{choice(shablon)}</a>",
                            parse_mode='html',
                            reply_to=reply_to_msg.id if reply_to_msg else None
                        )
                        await sleep(int(time_sleep))
                    else:
                        await self.client.send_message(
                            chat_id,
                            f"{caption} <a href='tg://user?id={user_id}'>{choice(shablon)}</a>",
                            parse_mode='html',
                            reply_to=reply_to_msg.id if reply_to_msg else None
                        )
                        await sleep(int(time_sleep))
        
        @self.client.on(events.NewMessage(pattern=r'\.renta'))
        async def tag_handler(msg):
            me = await self.client.get_me()
            if msg.sender_id == me.id:
                text = msg.message.message.split(maxsplit=1)[1]
                args = text.split()
                if args is None: 
                    return await msg.edit("<b>аргументы не указаны</b>", 
                    parse_mode='html')
                
                chat_id = int(args[0])
                user_id = int(args[1])
                time_sleep = int(args[2])
                
                photo = args[3] if 'https' in args[3] else None
                caption = ' '.join(args[4:]) if len(args) > 4 else ''
                
                await msg.edit('<b>Запущено\nЧтобы выключить пиши <code>.goff {}</code></b>'.format(chat_id), parse_mode='html')
                
                tag_chats[chat_id] = True
                while chat_id in tag_chats:
                    if photo:
                        await self.client.send_file(
                            chat_id,
                            file=photo,
                            caption=f"{caption} <a href='tg://user?id={user_id}'>{choice(shablon)}</a>",
                            parse_mode='html'
                        )
                        await sleep(int(time_sleep))
                    else:
                        await self.client.send_message(
                            chat_id,
                            f"{caption} <a href='tg://user?id={user_id}'>{choice(shablon)}</a>",
                            parse_mode='html'
                        )
                        await sleep(int(time_sleep))


        @self.client.on(events.NewMessage(pattern=r'\.goff')) 
        async def off_handler(msg): 
            me = await self.client.get_me() 
            if msg.sender_id == me.id: 
                global tag_chats 
                args = await self.get_args(msg) 
                if args:
                    chat_id = int(args.split()[0]) 
                else:
                    chat_id = msg.chat_id
                if chat_id in tag_chats: 
                    del tag_chats[chat_id] 
                    await msg.edit( 
                        "<b>остановлено в чате <code>{}</code></b>".format(chat_id), 
                        parse_mode='html' 
                    ) 
                else: 
                    await msg.edit( 
                        "<b>чат с айди <code>{}</code> не знайдено в словарике</b>".format(chat_id), 
                        parse_mode='html' 
                    )


        @self.client.on(events.NewMessage(pattern=r'\.cl'))
        async def clear_autoreply_list_handler(event):
            me = await self.client.get_me()
            msg = event.message
            if msg.sender_id == me.id:  
                autoreply_list.clear()
                autoreply_time.clear()
                autoreply_photo.clear()
                autoreply_shpk.clear()
                await msg.edit("список автоответчиков успешно очищено")
            else:
                pass


        @self.client.on(events.NewMessage(pattern=r'\.c_flood'))
        async def clear_autoreply_list_handler(event):
            me = await self.client.get_me()
            msg = event.message
            if msg.sender_id == me.id:  
                spam_state.clear()
                spam_state1.clear()
                tag_chats.clear()
                tagger_chats.clear()
                await msg.edit("все флудеры были выключены")
            else:
                pass
    

        @self.client.on(events.NewMessage(pattern=r'\.list'))
        async def show_lists_handler(event):
            me = await self.client.get_me()
            if event.sender_id == me.id:
                args = event.raw_text.split(' ')
                if len(event.raw_text.split()) > 1:   
                    args = event.raw_text.split(maxsplit=1)[1]   
                    global mlist
                    if args.lower() == "None":   
                        mlist = None   
                    else:   
                        mlist = args   
                    await event.edit("<b>медиа встановлено</b>", parse_mode='html')   
                    return   
                else:
                    reply_to = None
                    reply_msg = await event.get_reply_message()
                    if reply_msg:
                        reply_to = reply_msg.id
                    response = "чаты в каких работает renewal:\n"
                    response += str(spam_state) + "\n\n"
                    response += "чати в каких работает rsp:\n"
                    response += str(spam_state1) + "\n\n"
                    response += "люди на которых реагирует reply:\n"
                    response += str(autoreply_list) + "\n\n"
                    response += "чати в каких работает tagger:\n"
                    response += str(tagger_chats) + "\n\n"
                    response += "чати в каких работает renta:\n"
                    response += str(tag_chats) 
                try:
                    await event.respond(response, file=mlist, reply_to=reply_to)
                    await event.delete()
                except:
                    await event.edit(response)
            else:
                if mlist is not None:
                    await event.edit(response, file=mlist)
                    await event.delete()
                else:
                    await event.edit(response)


        @self.client.on(events.NewMessage(pattern='\.help|\.menu|\.cmd'))      
        async def command_help_commands(event):      
            me = await self.client.get_me()      
            msg = event.message     
            namee = name 
            if msg.sender_id == me.id:      
                chat_id = event.chat_id      
                args = await self.get_args(event)     
                if len(event.raw_text.split()) > 1:   
                    args = event.raw_text.split(maxsplit=1)[1]   
                    global mh   
                    if args.lower() == "None":   
                        mh = None   
                    else:   
                        mh = args   
                    await event.edit("<b>медиа востановлено</b>", parse_mode='html')   
                    return   
                reply_msg = await msg.get_reply_message()        
                if reply_msg:  
                    reply_to = reply_msg.id      
                    try:
                        await self.client.send_file(chat_id, mh, caption=menutext.format(namee, chat_id, me.id, me.first_name, me.username), reply_to=reply_to, parse_mode='html')  
                        await msg.delete()
                    except:
                        await event.edit(menutext.format(namee, chat_id, me.id, me.first_name, me.username), parse_mode='html')
                else:  
                    if mh is not None:
                        try:
                            await self.client.send_file(chat_id, mh, caption=menutext.format(namee, chat_id, me.id, me.first_name, me.username), parse_mode='html')
                            await msg.delete()
                        except:
                            await event.edit(menutext.format(namee, chat_id, me.id, me.first_name, me.username), parse_mode='html')
                    else:
                        await event.edit(menutext.format(namee, chat_id, me.id, me.first_name, me.username), parse_mode='html')



        async def upload_to_x0_http(file_path): 
            url = 'https://x0.at/' 
            files = {'file': open(file_path, 'rb')} 
        
            try: 
                response = requests.post(url, files=files) 
                if response.status_code == 200:
                    os.remove(file_path) 
                    return response.text   
                else: 
                    return f"Ошибка загрузки: {response.status_code} {response.reason}" 
            except Exception as e: 
                return str(e) 
        
        
        @self.client.on(events.NewMessage(pattern='\.x0'))
        async def handle_x0_command(event):
            me = await self.client.get_me()
            msg = event.message
        
            if msg.sender_id == me.id:
                if event.is_reply:
                    reply_msg = await event.get_reply_message()
                    if reply_msg.media:
                        await event.edit("<b>начинаю загрузку этого медиа</b>", parse_mode='html')
                        media = reply_msg.media
                        file = await self.client.download_media(media)
                        x0_link = await upload_to_x0_http(file)
                        reply_id = reply_msg.id
                        try:
                            await event.client.send_file(event.chat_id, media, caption=f"<code>{x0_link}</code>", reply_to=reply_id, parse_mode='html')
                            await event.delete()
                        except Exception as e:
                            await event.edit(f"<code>{x0_link}</code>", parse_mode='html')
                    else:
                        await event.edit("<b>Ошибка: сообщение не содержит медиафайл</b>", parse_mode='html')
                else:
                    await event.edit("<b>Ошибка: это сообщение не является ответом на другое сообщение</b>", parse_mode='html')
    

        @self.client.on(events.NewMessage(pattern=r'\.count'))  
        async def count_handler(msg):  
            if msg.is_reply:  
                try: 
                    reply_msg = await msg.get_reply_message()
                    words = reply_msg.message.split()  
                    total_words = len(words)  
                    total_chars = len(reply_msg.message)  
                    total_lines = reply_msg.message.count('\n') + 1  
                    result_message = (  
                        f"<b>Результат подсчёта для этого сообщения :</b>\n"  
                        f"Общее количество слов: {total_words}\n"  
                        f"Общее количество символов: {total_chars}\n"  
                        f"Общее количество знаков: {total_lines}"  
                    )  
                    await msg.edit(result_message, parse_mode='html') 
                except Exception as e: 
                    print(e)

        @self.client.on(events.NewMessage(pattern=r'\.change'))  
        async def change_handler(msg):  
            me = await self.client.get_me()  
            if msg.sender_id == me.id:  
                if msg.is_reply:  
                    reply_msg = await msg.get_reply_message()  
                    if reply_msg.file:  
                        try:  
                            file = await reply_msg.download_media()  
                            with open(file, 'r', encoding='utf-8') as f:  
                                lines = f.readlines()  
                                shablon.clear()  
                                for line in lines:  
                                    shablon.append(line.strip())  
                            os.remove(file) 
                            await msg.edit("Шаблоны успешно зменены!") 
                        except Exception as e: 
                            print(f"Ошибка: {e}") 
                            await msg.delete() 
                        finally:
                            os.remove(file)
                    else: 
                        await msg.edit("Укажите реплай на файл") 
                else: 
                    await msg.edit("Укажите реплай на файл") 
                    
                    
        @self.client.on(events.NewMessage(pattern=r'\.file'))  
        async def file_handler(msg):  
            me = await self.client.get_me()  
            if msg.sender_id == me.id:  
                try:  
                    with open('texts.txt', 'w', encoding='utf-8') as f:  
                        for line in shablon:  
                            f.write(line + '\n')  
                    await self.client.send_file(msg.chat_id, 'texts.txt') 
                    os.remove('texts.txt') 
                    await msg.delete()
                except Exception as e: 
                    print(f"Ошибка: {e}") 

        @self.client.on(events.NewMessage(pattern=r'\.name'))
        async def name_handler(msg):
            me = await self.client.get_me()  
            if msg.sender_id == me.id:  
                text = msg.message.message.split(maxsplit=1)[1]
                global name
                name = str(text)
                await msg.edit('<b>Название бота заменена на {}</b>'.format(text), parse_mode='html')


        @self.client.on(events.NewMessage(pattern='\.forward'))
        async def forward_message(event):
            me = await self.client.get_me()
            msg = event.message
            if msg.sender_id == me.id:
                args = event.message.text.split()
                if len(args) == 2:
                    time = int(args[1])
                    reply_msg = await event.get_reply_message()
                    delay = time
                    if reply_msg:
                        self.forwarding_enabled[event.chat_id] = True
                        await self.forward_messages(event.chat_id, reply_msg, time)
                    else:
                        await event.edit("надо ответить на сообщение которое будет пересылаться")
                else:
                    await event.edit("надо указать задержку в секундах")

        @self.client.on(events.NewMessage(pattern='\.fstop'))
        async def stop_forwarding_message(event):
            me = await self.client.get_me()
            msg = event.message
            if msg.sender_id == me.id:
                chat_id = event.chat_id
                await self.stop_forwarding(chat_id)
                await event.edit("Пересылка остановлена")

        @self.client.on(events.NewMessage())
        async def watcher_handler(msg):
            await self.watcher(self.client, msg)
            


    def start(self):
        self.client.run_until_disconnected()



if __name__ == "__main__":
    bot = Userbot()
    bot.run()
    bot.start()



