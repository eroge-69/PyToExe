from apiclient.discovery import build
import asyncio
import discord
from discord.ext import tasks
import ffmpeg
import io
import json
import os
from PIL import Image
import random
import re
import requests
import sys
import urllib
from yt_dlp import YoutubeDL

def jsopen(func,file,mode='r',*,obj=None,buffering=-1,encoding='utf-8',errors=None,newline=None,closefd=True,opener=None):

    try:

        if func == 'load' and not os.path.isfile(file):
            return None
        with open(file,mode,buffering,encoding,errors,newline,closefd,opener) as fp:
            if func == 'load':
                data = json.load(fp)
                return data
            elif func == 'dump':
                json.dump(obj,fp,indent=4)

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\n{file}\033[0m')
        return None

client = discord.Client(intents=discord.Intents.all())
slash = discord.app_commands.CommandTree(client)
colour = jsopen('load','develop/status.json')['colour']
nomention = discord.AllowedMentions.none()
discord_avatar = 'https://cdn.discordapp.com/embed/avatars/0.png'
game_system = jsopen('load','develop/status.json')['dicebot']
command_pattern = requests.get(f'https://{jsopen("load","develop/interface.json")["bcdice"]}/game_system/{game_system}').json()['command_pattern']

playlist = []
players = []

def develop(interaction:discord.Interaction):
    return interaction.user.id == jsopen('load','develop/client.json')['develop']

class refembed():

    try:

        def __init__(self,embeds):
            self.authors = [refembed.authors(i.author) for i in embeds if hasattr(i,'author')]

        class authors():

            def __init__(self,author):
                self.display_name = author.name
                self.display_avatar = refembed.display_avatar(author)

        class display_avatar():

            def __init__(self,author):
                self.author = author

            async def read(self):
                return urllib.request.urlopen(urllib.request.Request(self.author.icon_url,headers=jsopen('load','develop/useragent.json'))).read()

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')

class contents(discord.ui.View):

    try:

        def __init__(self,file,**form):
            super().__init__(timeout=None)
            self.cont = paginate(file,form)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='🔙',custom_id='contents.prev')
        async def prev(self,interaction:discord.Interaction,button:discord.ui.Button):
            page = int(re.findall(f'{client.user.name}　(\\d+) / \\d+',interaction.message.embeds[0].title)[0])-1
            if page < 1:page = len(self.cont)
            embed = discord.Embed(title=f'**{client.user.name}　{page} / {len(self.cont)}**',description=self.cont[page-1],colour=interaction.message.embeds[0].colour)
            await interaction.response.edit_message(embed=embed)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='✔️',custom_id='contents.clos')
        async def clos(self,interaction:discord.Interaction,button:discord.ui.Button):
            await interaction.response.edit_message(delete_after=0)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='🔜',custom_id='contents.next')
        async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
            page = int(re.findall(f'{client.user.name}　(\\d+) / \\d+',interaction.message.embeds[0].title)[0])+1
            if page > len(self.cont):page = 1
            embed = discord.Embed(title=f'**{client.user.name}　{page} / {len(self.cont)}**',description=self.cont[page-1],colour=interaction.message.embeds[0].colour)
            await interaction.response.edit_message(embed=embed)

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')

class closebtn(discord.ui.View):

    try:

        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='✔️',custom_id='closebtn.clos')
        async def clos(self,interaction:discord.Interaction,button:discord.ui.Button):
            await interaction.message.delete()
            await interaction.response.edit_message(delete_after=0)

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')

class controls(discord.ui.View):

    try:

        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='⏮️',custom_id='controls.prev')
        async def prev(self,interaction:discord.Interaction,button:discord.ui.Button):
            if interaction.user.id in jsopen('load','develop/status.json')['verified']['player'] and interaction.guild.voice_client:
                if interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
                    if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                        playlist.insert(0,playlist.pop(-1))
                        playlist.insert(0,playlist.pop(-1))
                        interaction.guild.voice_client.stop()
                        await interaction.response.send_message(content='⏮️',ephemeral=True)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='⏯️',custom_id='controls.play')
        async def play(self,interaction:discord.Interaction,button:discord.ui.Button):
            if interaction.user.id in jsopen('load','develop/status.json')['verified']['player'] and interaction.guild.voice_client:
                    if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                        if interaction.guild.voice_client.is_playing():interaction.guild.voice_client.pause()
                        elif interaction.guild.voice_client.is_paused():interaction.guild.voice_client.resume()
                        await interaction.response.send_message(content='⏯️',ephemeral=True)

        @discord.ui.button(style=discord.ButtonStyle.secondary,emoji='⏭️',custom_id='controls.next')
        async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
            if interaction.user.id in jsopen('load','develop/status.json')['verified']['player'] and interaction.guild.voice_client:
                if interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
                    if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                        interaction.guild.voice_client.stop()
                        await interaction.response.send_message(content='⏭️',ephemeral=True)

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')

def paginate(file,form):

    try:

        page = []
        text = []
        with open(str(file),encoding='utf-8') as fp:
            for rl in fp.readlines():
                i = rl.replace('\n','')
                if len('\n'.join(text)+'\n'+(eval(f'f"{i}"',{},form) if form else i)) > 500:
                    page.append('\n'.join(text))
                    text = []
                text.append(eval(f'f"{i}"',{},form) if form else i)
            if text:
                page.append('\n'.join(text))
        return page

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')
        return ['** **']

@slash.command(name='vrfy')
@discord.app_commands.user_install()
@discord.app_commands.check(develop)
@discord.app_commands.choices(type=[discord.app_commands.Choice(name=i,value=i) for i in jsopen('load','develop/status.json')['verified'].keys()])
async def on_vrfy(interaction:discord.Interaction,type:str,user:discord.Member):
    sts = jsopen('load','develop/status.json')
    if user.id in sts['verified'][type]:sts['verified'][type].remove(user.id)
    else:sts['verified'][type].append(user.id)
    jsopen('dump','develop/status.json','wt',obj=sts)
    embed = discord.Embed(title=f'**{client.user.name}**',description=f'{user.mention} has been {"" if user.id in sts["verified"][type] else "un"}verified from "{type}".',colour=colour)
    embed.set_author(name=interaction.user.display_name,icon_url=interaction.user.display_avatar.url or discord_avatar)
    await interaction.response.send_message(embed=embed,ephemeral=True)

@slash.command(name='help',description='コマンドヘルプを表示します。')
@discord.app_commands.guild_install()
async def on_help(interaction:discord.Interaction):
    pf = jsopen('load','develop/status.json')['prefix']
    help = paginate('develop/command.txt',{'pf':pf})
    await interaction.response.send_message(embed=discord.Embed(title=f'**{client.user.name}　1 / {len(help)}**',description=help[0],colour=colour),view=contents('develop/command.txt',pf=pf))

@slash.command(name='ping',description='ボットの応答速度を計測します。')
@discord.app_commands.guild_install()
async def on_ping(interaction:discord.Interaction):
    await interaction.response.send_message(f'🏓pong! **{round(client.latency*1000)}ms**')

@client.event
async def on_ready():

    try:

        if os.path.isfile('storage/playing.mp3'):os.remove('storage/playing.mp3')

        sts = jsopen('load','develop/status.json')
        api = jsopen('load','develop/interface.json')
        for i in [contents('develop/command.txt',pf=sts['prefix']),closebtn(),controls()]:client.add_view(i)
        await slash.sync()
        await client.change_presence(activity=discord.Game(name=f'{sts["prefix"]}help'),status=discord.Status.online)

        global playlist
        pageToken = ''
        await client.get_channel(sts['player']['channelId']).connect(self_deaf=True)
        await client.get_channel(sts['player']['channelId']).purge(limit=1000,oldest_first=True)
        voice_client = client.get_guild(sts['player']['guildId']).voice_client
        youtube = build('youtube','v3',developerKey=api['youtube'])

        while True:

            await asyncio.sleep(1)
            while voice_client.is_playing() or voice_client.is_paused():await asyncio.sleep(1)
            if not voice_client.is_connected():
                await client.get_channel(sts['player']['channelId']).connect()
                voice_client = client.get_guild(sts['player']['guildId']).voice_client
            if playlist:
                with YoutubeDL(sts['player']['ydl_opts']) as ydl:info = ydl.extract_info('https://youtu.be/'+playlist[0],download=True)
                voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('storage/playing.mp3'),volume=0.1),signal_type='voice')
                embed = discord.Embed(title=info["title"],url='https://youtu.be/'+playlist[0],colour=0xFF0033)
                embed.set_author(name=info['channel'])
                embed.set_image(url=info['thumbnail'])
                await client.get_channel(sts['player']['channelId']).send(embed=embed,allowed_mentions=nomention)
                playlist.append(playlist.pop(0))
                for i in list(players):
                    try:await i.edit(embed=embed,view=controls(),allowed_mentions=nomention)
                    except:players.remove(i)
            else:
                while True:
                    request = youtube.playlistItems().list(part='snippet',maxResults=50,playlistId=sts['player']['playlistId'],fields="nextPageToken,items/snippet/resourceId/videoId",pageToken=pageToken)
                    response = request.execute()
                    playlist += list(map(lambda item:item['snippet']['resourceId']['videoId'],response['items']))
                    if not 'nextPageToken' in response:break
                    pageToken = response['nextPageToken']
                random.shuffle(playlist)

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')

@client.event
async def on_message(msg):

    try:

        if msg.flags.ephemeral:
            return

        cmd = msg.content.lower().split(' ') or []

        ref = msg.reference.resolved if msg.reference else None
        usr = msg.author
        men = []
        if hasattr(ref,'webhook_id'):men = [ref.author]
        if msg.mentions:men = msg.mentions
        # if ref and ref.author == client.user and ref.embeds:men = refembed(ref.embeds).authors

        if usr.bot:return

        sts = jsopen('load','develop/status.json')
        api = jsopen('load','develop/interface.json')

        pf = sts['prefix']

        if srv := msg.guild or None:

            if msg.content == 's' and usr.id in sts['verified']['player']:
                if srv.voice_client and srv.voice_client.is_playing():
                    if usr.voice.channel == srv.voice_client.channel:
                        await msg.add_reaction('⏭️')
                        srv.voice_client.stop()

            if cmd[0].startswith(sts['prefix']) or cmd[0].startswith(pf):

                if cmd[0] == f'{sts["prefix"]}help' or cmd[0] == f'{pf}help':
                    help = paginate('develop/command.txt',{'pf':pf})
                    await msg.reply(embed=discord.Embed(title=f'**{client.user.name}　1 / {len(help)}**',description=help[0],colour=colour),view=contents('develop/command.txt',pf=pf),allowed_mentions=nomention)
                    return

                elif cmd[0] == f'{sts["prefix"]}ping' or cmd[0] == f'{pf}ping':
                    await msg.reply(f'🏓pong! **{round(client.latency*1000)}ms**',allowed_mentions=nomention)
                    return

                elif cmd[0] == f'{sts["prefix"]}ctrl' or cmd[0] == f'{pf}ctrl':
                    with YoutubeDL(sts['player']['ydl_opts']) as ydl:info = ydl.extract_info('https://youtu.be/'+playlist[-1],download=False)
                    embed = discord.Embed(title=info["title"],url='https://youtu.be/'+playlist[-1],colour=0xFF0033)
                    embed.set_author(name=info['channel'])
                    embed.set_image(url=info['thumbnail'])
                    players.append(await msg.channel.send(embed=embed,view=controls(),allowed_mentions=nomention))

                elif cmd[0] == f'{sts["prefix"]}dead' or cmd[0] == f'{pf}dead':
                    photo = Image.open(io.BytesIO(await [*men,usr][0].display_avatar.read()))
                    sheet = Image.new('RGBA',(512,512),(255,255,255,0))
                    photo = photo.convert('LA')
                    photo = photo.resize((512,512))
                    frame = Image.open('storage/died.png')
                    sheet.paste(photo,(0,48),photo)
                    sheet.paste(frame,(0,0),frame)
                    sheet.save('storage/dead.png')
                    embed = discord.Embed(title=f'**{client.user.name}**',description=f'{[*men,usr][0].display_name}さんを殺しました。',colour=0xFFCF77)
                    embed.set_author(name=usr.display_name,icon_url=usr.display_avatar.url or discord_avatar)
                    file = discord.File(fp='storage/dead.png',filename='dead.png')
                    embed.set_image(url='attachment://dead.png')
                    await msg.channel.send(file=file,embed=embed,view=closebtn(),allowed_mentions=nomention)

        if hasattr(msg.channel,'topic') and msg.channel.topic:

            if 'diceroll' in msg.channel.topic:

                die = msg.content.replace('\n',' ')
                if cmd[0] == f'{sts["prefix"]}rano' or cmd[0] == f'{pf}rano':
                    with open('storage/joyokanji.txt',encoding='utf-8') as fp:
                        await msg.reply(f'# 〈{random.choice(fp.read())}〉',allowed_mentions=nomention)
                if die and not re.match(r':.*',die):
                    cmd = []
                    if re.match(r'(s|S)',die):
                        cmd.append('S')
                        die = re.sub(r'^(s|S)','',die)
                    if re.match(r'(repeat|rep|x|X)\d+ ?',die):
                        cmd.append(re.sub(r'^(repeat|rep|x|X)(\d+) ?.+',r'\2',die))
                        cmd[-1] = 'x25 ' if int(cmd[-1]) > 25 else f'x{cmd[-1]} '
                        die = re.sub(r'^(repeat|rep|x|X)\d+ ?','',die)
                    for i in range(2-len(cmd)):cmd.append('')
                    die = re.sub(r'^c','C',die)
                    if not re.search(r'[<=>]',die):die = re.sub(r' (\d+)',r'<=\1',die,1)
                    die = ''.join(cmd[:1])+die
                    if re.match(command_pattern,die):
                        roll = requests.get(f'https://{api["bcdice"]}/game_system/{game_system}/roll',params={'command':die}).json()
                        if roll['ok']:
                            die = die.replace('*','\*')
                            roll['text'] = re.sub(r'#\d+\n[^＞]+' if re.match(r's?x\d+',die) else r'^[^＞]+','',roll['text'].replace('*','\*')).replace('\n\n','\n')
                            embeds = []
                            embed = discord.Embed(title=f'**{die}**',description=f'**{roll["text"]}**',colour=0x2196F3 if roll['success'] else 0xDC004E if roll['failure'] else 0xBFBFBF)
                            embed.set_author(name=usr.display_name,icon_url=usr.display_avatar.url or discord_avatar)
                            if roll['secret']:
                                await msg.delete()
                                await usr.send(embed=embed,view=closebtn())
                                embed = discord.Embed(title='**Secret dice 🎲**',colour=0xBFBFBF)
                                embed.set_author(name=usr.display_name,icon_url=usr.display_avatar.url or discord_avatar)
                            await msg.channel.send(embed=embed)

    except Exception as e:

        print(f'\033[31mFile client.py, line {sys.exc_info()[2].tb_lineno}: {e}\033[0m')

client.run(jsopen('load','develop/client.json')['token'])