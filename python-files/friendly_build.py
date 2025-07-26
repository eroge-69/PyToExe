import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import sys
from pass_captcha import infer_image
import json
import re
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="OWMz9mP3oZAxNdBWgxkR"
)
def infer_image(path):
    
    result = CLIENT.infer(path, model_id="my-first-project-vhm2p/1")
    return result['top']

intents = discord.Intents.default()
intents.members = True

if hasattr(intents, 'message_content'):
    intents.message_content = True

if hasattr(intents, 'presences'):
    intents.presences = True

if not open('settings.json', 'r').read():
    prefix=input("Enter your bot's prefix: ")
    token=input("Enter your bot's token: ")
    settings = {'prefix': prefix,'token':token}
    with open('settings.json', 'w') as f:
        json.dump(settings, f)
else:
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    prefix = settings.get('prefix')
    token = settings.get('token')

client = commands.Bot(command_prefix=prefix, self_bot=True, fetch_offline_members=True,intents=intents)

registered = False
jail=False
commands_list = {}
training_list = {'first':1, 'second':2, 'third':3, 'fourth':4, 'fifth':5, 'sixth':6, 'seventh':7, 'eighth':8, 'ninth':9, 'tenth':10}
@client.event
async def on_ready():
    print('Logged in as:',client.user.name)

@client.event
async def on_message(message):
    global jail
    if message.author.id == client.user.id:
        await client.process_commands(message)
    if message.author.id == 1397558119873384629 and message.content =='Registered successfully!':
        global registered
        registered = True

    if message.author.id == 555955826880413696:
        if len(message.attachments) > 0:
            await message.channel.send(infer_image(message.attachments[0].url))
    # if message.author.id==client.user.id and message.content.startswith(prefix):
    #     await client.process_commands(message)
    #     channel=message.channel.id

    elif message.author.id==1397558119873384629 and isinstance(message.channel, discord.DMChannel):  
        guild = client.get_guild(1397262290570707065)  
        channel = get(guild.text_channels, name=str(client.user.id))
        if 'training' in message.content.lower() and 'Get in the car' not in message.content:
            emoji_list = re.findall(r":(.*?):", message.content.lower())
            if emoji_list:
                for name in emoji_list:
                    if 'letter' in message.content.lower():
                        for x in training_list.keys():
                            # print(x, message.content.split(' '))
                            if x in message.content.replace('*', '').split(' '):
                                # print('yes')
                                await channel.send(name.replace(':', '')[training_list[x]-1])
                                break
                    elif 'name' in message.content.lower(): #fixxx
                        
                        options=message.content.split('-')[1:]
                        
                        for i in options:
                            x=i
                            if '?' in i:
                                i = i.partition('?')[2]
                            elif 'Answer' in i:
                                i = i.partition('Answer')[0]
                            if i.isdigit():
                                continue
                            i = i.replace('\n','').strip().replace(':', '').replace('*', '')
                            options[options.index(x)] = i
                        
                        for name in emoji_list:
                            for i in options:
                                if i.replace('1', '').replace('2', '').replace('3', '').replace('\n', '').replace(' ','').replace('*', '') == name.replace(':', '').replace('\n', ''):
                                    await channel.send(options.index(i) + 1)
                                    break
                                
                        counter = 0
                        for name in emoji_list:
                            if name == emoji_list[-1]:
                                counter += 1
                        await channel.send(counter-1)
                        break
                    elif 'is this' in message.content.lower():
                        emoji_name=emoji_list[-1].replace(':', '')
                        if emoji_name in message.content.lower().partition(':'+emoji_name+':')[0]:
                            await channel.send('Yes')
                            break
                        else:
                            await channel.send('No')
                            break
                    elif 'do you have' in message.content.lower():
                        await channel.send('No')
                        break
                    else:
                        print("Didn't get training task", message.content)
                        await asyncio.sleep(10)
        elif 'Get in the car' in message.content: 
            await asyncio.sleep(1)
            await channel.send('rpg jail')
            await asyncio.sleep(1)  
            await channel.send('protest')  
            await asyncio.sleep(1)

    # elif message.author.id!=client.user.id and (message.author.id==1023926153129492500 or message.author.id==796018481425416244):
    #     if message.content.startswith(prefix):
    #         await client.process_commands(message)
    #         await client.get_command(message.content[1:])(message)
    #     else:
    #         guild = client.get_guild(1397262290570707065)  
    #         channel = get(guild.text_channels, name=str(client.user.id))
    #         await channel.send(message.content)
@client.command()
async def close(ctx):
    await ctx.message.delete()
    sys.exit()

@client.command()
async def wait(ctx,time:int):
    await ctx.message.delete()
    await asyncio.sleep(time)
@client.command()
async def stop(ctx, *, text=None):
    global commands_list
    await ctx.message.delete()
    if text is None:
        for i in commands_list.keys():
            commands_list[i] = False
            print(f"Stopping the command: {text}")
    else:
        if text in commands_list:
            print(f"Stopping the command: {text}")
            commands_list[text] = False
        else:
            await ctx.send("Command not found in the list.")

@client.command()
async def h(ctx, time:int, *, text=None):
    global registered
    global commands_list
    global jail
    jail = False
    await ctx.message.delete()
    if not registered:
        print("You are not registered. Please register first.")
        return
    
    if text in commands_list and commands_list[text] == False:
        commands_list[text] = time
    if text is None:
        print('Insert text to send')
    else:
        try:
            time = int(time)
        except:
            print('Time delay must be an integer (in second) and goes first')
        while True:
            if jail:
                break
            if text in commands_list and commands_list[text] == False:
                break
            else:
                async with ctx.typing():  # Показывает "печатает..." в чате
                    await asyncio.sleep(len(text) * 0.05)  # Пауза зависит от длины текста
                    await ctx.send(text)
                commands_list[text] = time
                await asyncio.sleep(time)
@client.command()
async def code(ctx,m:str): 
    try:   
        exec(m)    
    except:
        raise
client.run(token,bot=False)
