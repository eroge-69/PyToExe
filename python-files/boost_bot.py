import tls_client, threading, os, requests
from base64 import b64encode
import json
import discord
from discord import app_commands
from discord.ext import commands, tasks
import secrets
import shutil
import shutil
import requests
from datetime import datetime
import yaml
import json
import requests
import tls_client
import threading
from base64 import b64encode
import secrets

from keyauth import api

import sys
import time
import platform
import os
import hashlib
from time import sleep
from datetime import datetime, UTC
from pystyle import Center, Colorate, Colors
import logging
logging.getLogger('discord').setLevel(logging.WARNING)

def clear():
    if platform.system() == 'Windows':
        os.system('cls & title Python Example')  
    elif platform.system() == 'Linux':
        os.system('clear')  
        sys.stdout.write("\033]0;Python Example\007") 
        sys.stdout.flush() 
    elif platform.system() == 'Darwin':
        os.system("clear && printf '\033[3J'")  
        os.system('echo -n -e "\033]0;Python Example\007"') 

print("Loading...")

print("--------------------------------")


red = "\033[91m"
yellow = "\033[93m"
green = "\033[92m"
blue = "\033[94m"
pretty = "\033[95m"
magenta = "\033[35m"
lightblue = "\033[36m"
cyan = "\033[96m"
gray = "\033[37m"
reset = "\033[0m"
pink = "\033[95m"
dark_green = "\033[92m"
yellow_bg = "\033[43m"
clear_line = "\033[K"
                                                     

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest


keyauthapp = api(
    name = "Hercules", 
    ownerid = "cDEG1Zpm9i",
    version = "1.0", 
    hash_to_check = getchecksum()
)

def answer():
    try:
        print(""" ╔════════════╗
 ║ 1.Login    ║         ╔════════════════════╗
 ║ 2.Register ║           discord.gg/hercule      
 ║ 3.Upgrade  ║           @34529 @x0ev @1ru
 ║ 4.License  ║         ╚════════════════════╝  
 ╚════════════╝         
        """)
        ans = input("Select Option: ")
        if ans == "1":
            user = input('Provide username: ')
            password = input('Provide password: ')
            keyauthapp.login(user, password)
        elif ans == "2":
            user = input('Provide username: ')
            password = input('Provide password: ')
            license = input('Provide License: ')
            keyauthapp.register(user, password, license)
        elif ans == "3":
            user = input('Provide username: ')
            license = input('Provide License: ')
            keyauthapp.upgrade(user, license)
        elif ans == "4":
            key = input('Enter your license: ')
            keyauthapp.license(key)
        else:
            print("\nInvalid option")
            sleep(1)
            clear()
            answer()
    except KeyboardInterrupt:
        os._exit(1)


answer()

'''try:
    if os.path.isfile('auth.json'): #Checking if the auth file exist
        if jsond.load(open("auth.json"))["authusername"] == "": #Checks if the authusername is empty or not
            print("""
1. Login
2. Register
            """)
            ans=input("Select Option: ")  #Skipping auto-login bc auth file is empty
            if ans=="1": 
                user = input('Provide username: ')
                password = input('Provide password: ')
                keyauthapp.login(user,password)
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            elif ans=="2":
                user = input('Provide username: ')
                password = input('Provide password: ')
                license = input('Provide License: ')
                keyauthapp.register(user,password,license) 
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            else:
                print("\nNot Valid Option") 
                os._exit(1) 
        else:
            try: #2. Auto login
                with open('auth.json', 'r') as f:
                    authfile = jsond.load(f)
                    authuser = authfile.get('authusername')
                    authpass = authfile.get('authpassword')
                    keyauthapp.login(authuser,authpass)
            except Exception as e: #Error stuff
                print(e)
    else: #Creating auth file bc its missing
        try:
            f = open("auth.json", "a") #Writing content
            f.write("""{
    "authusername": "",
    "authpassword": ""
}""")
            f.close()
            print ("""
1. Login
2. Register
            """)#Again skipping auto-login bc the file is empty/missing
            ans=input("Select Option: ") 
            if ans=="1": 
                user = input('Provide username: ')
                password = input('Provide password: ')
                keyauthapp.login(user,password)
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            elif ans=="2":
                user = input('Provide username: ')
                password = input('Provide password: ')
                license = input('Provide License: ')
                keyauthapp.register(user,password,license)
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            else:
                print("\nNot Valid Option") 
                os._exit(1) 
        except Exception as e: #Error stuff
            print(e)
            os._exit(1) 
except Exception as e: #Error stuff
    print(e)
    os._exit(1)'''

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
clear_console()

intents = discord.Intents.all()
logging.getLogger('discord').setLevel(logging.WARNING)
logging.disable(logging.CRITICAL)

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
      print(
        Center.XCenter(
            Colorate.Vertical(
                Colors.red_to_blue,
            f"""                            HURCLES BOOST BOT  | discord,gg/hercule | @34529 @x0ev @1ru
                          ██╗  ██╗███████╗██████╗  ██████╗██╗   ██╗██╗     ███████╗███████╗
                          ██║  ██║██╔════╝██╔══██╗██╔════╝██║   ██║██║     ██╔════╝██╔════╝
                          ███████║█████╗  ██████╔╝██║     ██║   ██║██║     █████╗  ███████╗
                          ██╔══██║██╔══╝  ██╔══██╗██║     ██║   ██║██║     ██╔══╝  ╚════██║
                          ██║  ██║███████╗██║  ██║╚██████╗╚██████╔╝███████╗███████╗███████║
                          ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝
                                                                                                               
            ██████╗ ██╗  ██╗███████╗██████╗  █████╗     ██╗  ██╗ ██████╗ ███████╗██╗   ██╗     ██╗██████╗ ██╗   ██╗
            ╚════██╗██║  ██║██╔════╝╚════██╗██╔══██╗    ╚██╗██╔╝██╔═████╗██╔════╝██║   ██║    ███║██╔══██╗██║   ██║
             █████╔╝███████║███████╗ █████╔╝╚██████║     ╚███╔╝ ██║██╔██║█████╗  ██║   ██║    ╚██║██████╔╝██║   ██║
             ╚═══██╗╚════██║╚════██║██╔═══╝  ╚═══██║     ██╔██╗ ████╔╝██║██╔══╝  ╚██╗ ██╔╝     ██║██╔══██╗██║   ██║
            ██████╔╝     ██║███████║███████╗ █████╔╝    ██╔╝ ██╗╚██████╔╝███████╗ ╚████╔╝      ██║██║  ██║╚██████╔╝
            ╚═════╝      ╚═╝╚══════╝╚══════╝ ╚════╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝  ╚═══╝       ╚═╝╚═╝  ╚═╝ ╚═════╝ 
                                                                                                       
"""
                ,
                1,
            )
        )
    )
            


# load keys
def load_keys():
    keys = {}
    try:
        with open('keys.txt', 'r') as file:
            for line in file:
                key, owner_id, days = line.strip().split(':')
                keys[key] = (int(owner_id), int(days))
    except FileNotFoundError:
        pass
    return keys

authorized_users = {}

def is_key_expired(activation_date, days_valid):
    expiration_date = activation_date + datetime.timedelta(days=days_valid)
    return datetime.datetime.now() > expiration_date

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
# Extract configurations


WEBHOOK_URL = config['webhook_url']
client_id = config['client_id']
secret = config['client_secret']
tkn = config['bot_token']
redirect = config['redirect_url']
OWNERS = config['owners']

def is_owner(user_id):
    return str(user_id) in OWNERS


@bot.tree.command(name='create-keys', description="Generate keys and send them in a text file to your DM")
@app_commands.describe(
    key_amount="The number of keys to generate", 
    token_amount="The number of tokens per key"
)
@app_commands.choices(typ=[
    app_commands.Choice(name="1 Month", value="1m"),
    app_commands.Choice(name="3 Month", value="3m")
])
async def create_keys(interaction: discord.Interaction, typ: app_commands.Choice[str], key_amount: int, token_amount: int):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("You do not have permission to use this command.")
        return

    filename = '1m.txt' if typ.value == '1m' else '3m.txt'
    generated_keys = []
    genned_stocks_dir = "genned_stocks"

    if not os.path.exists(genned_stocks_dir):
        os.makedirs(genned_stocks_dir)

    with open(filename, 'r') as f:
        lines = f.readlines()

    total_tokens_needed = key_amount * token_amount
    if len(lines) < total_tokens_needed:
        await interaction.response.send_message(f"Not enough tokens in {typ.name} stock to generate {key_amount} keys with {token_amount} tokens each.")
        return

    # Generate each key and save its tokens in the corresponding key folder
    for _ in range(key_amount):
        key = secrets.token_hex(8)  # Generate a unique key
        generated_keys.append(key)  # Store the key
        token_slice = lines[:token_amount]  # Select the tokens for this key
        lines = lines[token_amount:]  # Remove used tokens from the list

        # Create a unique folder for the key
        key_folder = os.path.join(genned_stocks_dir, key)
        os.makedirs(key_folder, exist_ok=True)

        # Save the tokens to a .txt file in the key folder
        token_file_path = os.path.join(key_folder, f"{typ.value}.txt")
        with open(token_file_path, 'w') as f:
            f.writelines(token_slice)

    # Write back the remaining tokens to the stock file
    with open(filename, 'w') as f:
        f.writelines(lines)

    # Write the generated keys to a text file
    keys_file_path = os.path.join(genned_stocks_dir, f"{interaction.user.id}_keys.txt")
    with open(keys_file_path, 'w') as keys_file:
        for key in generated_keys:
            keys_file.write(f"{key}\n")

    # Send the keys file to user
    user = await bot.fetch_user(interaction.user.id)
    try:
        await user.send(file=discord.File(keys_file_path))
        await interaction.response.send_message(f"Generated {key_amount} keys and sent them in a text file to your DM.")
    except discord.Forbidden:
        await interaction.response.send_message("I couldn't DM you. Please make sure your DMs are open.")

    # Optionally, delete the keys file after sending
    os.remove(keys_file_path)

async def restock(interaction: discord.Interaction, typ: app_commands.Choice[str], file: discord.Attachment = None, code: str = None):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("You do not have permission to use this command.")
        return

    if not file and not code:
        await interaction.response.send_message("You need to provide either a file or a Paste.ee link/code!")
        return

    stock_tokens = []

    if file:
        # Reading tokens from the uploaded file
        file_content = await file.read()
        stock_tokens = file_content.decode('utf-8').splitlines()

    elif code:
        # Fetching tokens from the Paste.ee link
        if "paste.ee" in code:
            # Modifying the code to fetch the raw content using the raw URL
            raw_paste_link = code.replace("https://paste.ee/p/", "https://paste.ee/r/")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(raw_paste_link) as response:
                        if response.status == 200:
                            paste_content = await response.text()
                            stock_tokens = paste_content.splitlines()
                        else:
                            await interaction.response.send_message("Failed to retrieve tokens from the provided Paste.ee link.")
                            return
            except Exception as e:
                await interaction.response.send_message(f"Error fetching Paste.ee content: {e}")
                return
        else:
            # Treating code as raw paste content
            stock_tokens = code.splitlines()

    # Determine file to append based on type
    filename = '1m.txt' if typ.value == '1m' else '3m.txt'

    # Writing tokens to the appropriate file
    with open(filename, 'a') as f:
        for token in stock_tokens:
            f.write(f"{token}\n")

    await interaction.response.send_message(f"Successfully added {len(stock_tokens)} tokens to the {typ.name} stock.")

@bot.tree.command(name='stock', description="View the current stock of tokens")
@app_commands.describe(
    typ="Select the type of tokens to view the stock count"
)
@app_commands.choices(typ=[
    app_commands.Choice(name="1 Month", value="1m"),
    app_commands.Choice(name="3 Month", value="3m")
])
async def stock(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("You do not have permission to use this command.")
        return

    # Select the corresponding file based on the choice
    filename = '1m.txt' if typ.value == '1m' else '3m.txt'

    # Check if file exists
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        total_stocks = len(lines)
    else:
        total_stocks = 0

    # Display the stock count
    embed = discord.Embed(title="Stock", color=discord.Color.purple())
    embed.add_field(name=f"{typ.name} Tokens", value=f"{total_stocks} tokens", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='help', description="Get a list of all available bot commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Boost Bot", description="Auto Boost", color=discord.Color.blue())
    embed.add_field(name="For Customers", value="Only For Customer")
    embed.add_field(name="/Redeem", value="Redeem tokens using a key.\nUsage: `/redeem [key] [server_id]`", inline=False)
    embed.add_field(name="Invite Bot", value=f"[Boost bot](https://discord.com/oauth2/authorize?client_id={client_id}&permissions=2049&integration_type=0&scope=bot)", inline=False)
    embed.add_field(name="For Owner", value="Only For Owner")
    embed.add_field(name="/Boost", value="Boost the specified guild with the given amount.\nUsage: `/boost [type: 1m|3m] [guild] [amount] [nickname: optional] [bio: optional]`", inline=False)
    embed.add_field(name="/Gen", value="Generate tokens and send them to your DM.\nUsage: `/gen [amount] [type: 1m|3m]`", inline=False)
    embed.add_field(name="/Restock", value="Restock tokens from an uploaded file.\nUsage: `/restock [file] [type: 1m|3m]`", inline=False)
    embed.add_field(name="/Stock", value="Show the current number of tokens in stock.\nUsage: `/stock`", inline=False)
    await interaction.response.send_message(embed=embed)


# Ping command
@bot.tree.command(name='ping', description="Check the bot's latency ")
async def ping(interaction: discord.Interaction):
    latency = bot.latency * 1000
    embed = discord.Embed(title="Pong!", description=f"Latency: {latency:.2f} ms", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)



import os
import requests
import shutil
import threading
from datetime import datetime
import discord
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
import os
import requests
import shutil
from datetime import datetime

class RedeemModal(Modal):
    def __init__(self):
        super().__init__(title="Redeem Tokens")

        self.key = TextInput(label="Key", placeholder="Enter your redeem key", required=True)
        self.server_id = TextInput(label="Server ID", placeholder="Enter the server ID", required=True)
        self.nickname = TextInput(label="Nickname (Optional)", placeholder="Enter a nickname", required=False)
        self.bio = TextInput(label="Bio (Optional)", placeholder="Enter a bio", required=False)

        self.add_item(self.key)
        self.add_item(self.server_id)
        self.add_item(self.nickname)
        self.add_item(self.bio)

    async def on_submit(self, interaction: discord.Interaction):
        key = self.key.value
        server_id = self.server_id.value
        nickname = self.nickname.value if self.nickname.value else None
        bio = self.bio.value if self.bio.value else None

        await interaction.response.defer()  # Defer to avoid timeout
        await process_redeem(interaction, key, server_id, nickname, bio)

async def process_redeem(interaction: discord.Interaction, key: str, server_id: str, nickname: str = None, bio: str = None):
    key_folder = os.path.join("genned_stocks", key)
    if not os.path.exists(key_folder):
        await interaction.followup.send("Invalid key! Please check and try again.", ephemeral=True)
        return

    token_files = [f for f in os.listdir(key_folder) if f.endswith('.txt')]
    if not token_files:
        await interaction.followup.send("No tokens found for the provided key.", ephemeral=True)
        return

    tokens_used = 0
    successful_boosts = 0
    failed_tokens = 0
    joined_guilds = 0
    failed_token_list = []
    success_boost_list = []

async def redeem_token(token, server_id, nickname=None, bio=None):
    # Check if the token is properly formatted
    parts = token.split(":")
    if len(parts) < 3:
        return "Invalid token format", token  # Return an error message if the format is incorrect

    tk = parts[2]  # Now it's safe to access the third part
    try:
        # Add the main token authorization and boosting logic here
        await authorizer(tk, server_id, nickname, bio)  # Ensure authorizer is also async if it uses await
        headers = get_headers(tk, __properties__, __useragent__)
        client = tls_client.Session(client_identifier="firefox_102")
        client.headers.update(headers)

        r = await client.get(f"{API_ENDPOINT}/users/@me/guilds/premium/subscription-slots")  # Use await here
        idk = await r.json()  # Use await here

        # Check for 2 premium subscription slots to boost 2 times
        boost_count = 0
        for x in idk:
            if boost_count >= 2:
                break  # Limit to 2 boosts per token
            id_ = x['id']
            payload = {"user_premium_guild_subscription_slot_ids": [id_]}
            r = await client.put(f"{API_ENDPOINT}/guilds/{server_id}/premium/subscriptions", json=payload)  # Use await here

            if r.status_code in (200, 201, 204):
                boost_count += 1
            elif r.status_code == 429:
                return "Cooldown", tk
            else:
                return f"Boost failed: {r.status_code} - {r.text}", tk

        if boost_count == 2:
            return "boosted twice", tk
        else:
            return "joined", tk
    except Exception as e:
        return f"Failed: {str(e)}", token

    # Redeem tokens
    for token_file in token_files:
        with open(os.path.join(key_folder, token_file), 'r') as f:
            tokens = f.readlines()

        for token in tokens:
            token = token.strip()
            result, tk = redeem_token(token, server_id, nickname, bio)
            if result == "joined":
                joined_guilds += 1
                successful_tokens.append(tk)
            elif result == "boosted twice":
                successful_boosts += 2  # Count 2 boosts
                success_boost_list.append(tk)
                tokens_used += 1
            elif result == "Cooldown":
                failed_tokens += 1
                failed_token_list.append(f"{tk} - Cooldown active")
            else:
                failed_tokens += 1
                failed_token_list.append(f"{tk} - {result if result else 'Unknown Error'}")

    # Log information
    guild_info = await bot.fetch_guild(server_id)
    server_name = guild_info.name
    user_name = interaction.user.name
    user_id = interaction.user.id
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    failed_tokens_message = '\n'.join(failed_token_list) if failed_token_list else "None"
    success_tokens_message = '\n'.join(success_boost_list) if success_boost_list else "None"

    webhook_payload = {
        "content": "Boost Bot Logs",
        "embeds": [
            {
                "title": "Key Redeemed",
                "color": 0x800080,  # Purple color
                "fields": [
                    {"name": "Key", "value": key, "inline": False},
                    {"name": "Server", "value": f"{server_name} ({server_id})", "inline": False},
                    {"name": "Redeemed by", "value": f"{user_name} ({user_id})", "inline": False},
                    {"name": "Timestamp", "value": timestamp, "inline": False},
                    {"name": "Tokens Used", "value": f"{tokens_used} tokens", "inline": False},
                    {"name": "Joined Guilds", "value": f"{joined_guilds}", "inline": False},
                    {"name": "Successful Boosts", "value": f"{successful_boosts} tokens", "inline": False},
                    {"name": "Failed Tokens", "value": f"{failed_tokens} tokens", "inline": False},
                    {"name": "Failed Token List", "value": failed_tokens_message, "inline": False},
                    {"name": "Successful Boost List", "value": success_tokens_message, "inline": False}
                ]
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=webhook_payload)

    shutil.rmtree(key_folder)
    await interaction.followup.send(f"Tokens have been redeemed and added to server ID: {server_id}", ephemeral=True)

class RedeemView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Non-timeout button
        self.add_item(Button(label="Redeem", style=discord.ButtonStyle.green, custom_id="redeem_button"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        modal = RedeemModal()
        await interaction.response.send_modal(modal)
        return True

@bot.tree.command(name='redeem-panel', description="Set up the redeem panel")
@app_commands.describe(channel="The channel where to send the redeem panel")
async def redeem_panel(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(
        title="Redeem Panel",
        description="Click the button below to redeem your tokens. \n\n**Note:** Ensure you have added our bot to the server before using the key.\nAdd your Server ID and optional Nickname/Bio.",
        color=0x00FF00
    )
    embed.set_footer(text="Boost Bot")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1296557067263414352/1303058690798260394/comet.png?ex=672a5f79&is=67290df9&hm=76225b37a21e4f0a23428806c54bb8223b95e01fe6c9104964a10c18607d6ae0&")  # Add a URL to a custom image/icon

    view = RedeemView()
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Redeem panel sent to {channel.mention}", ephemeral=True)

@bot.tree.command(name='redeem', description="Redeem tokens using a key")
@app_commands.describe(key="The key for redeeming tokens", server_id="The server ID where tokens will join", nickname="Optional nickname for the tokens", bio="Optional bio for the tokens")
async def redeem_tokens(interaction: discord.Interaction, key: str, server_id: str, nickname: str = None, bio: str = None):
    await interaction.response.defer()  # Defer the response to prevent the "application did not respond" error

    key_folder = os.path.join("genned_stocks", key)
    if not os.path.exists(key_folder):
        await interaction.followup.send("Invalid key! Please check and try again.")
        return

    token_files = [f for f in os.listdir(key_folder) if f.endswith('.txt')]
    if not token_files:
        await interaction.followup.send("No tokens found for the provided key.")
        return

    tokens_used = 0
    successful_boosts = 0
    failed_tokens = 0
    joined_guilds = 0
    failed_token_list = []
    successful_tokens = []
    success_boost_list = []

    def redeem_token(token, server_id, nickname=None, bio=None):
        tk = token.split(":")[2]
        try:
            # Call the main function which handles the boosting logic
            authorizer(tk, server_id, nickname, bio) 
            headers = get_headers(tk, __properties__, __useragent__)
            client = tls_client.Session(client_identifier="firefox_102")
            client.headers.update(headers)

            r = client.get(f"{API_ENDPOINT}/users/@me/guilds/premium/subscription-slots")
            slots = r.json()

            # Attempt to redeem two subscription slots per token (if available)
            boost_count = 0
            for slot in slots:
                id_ = slot['id']
                payload = {"user_premium_guild_subscription_slot_ids": [id_]}
                r = client.put(f"{API_ENDPOINT}/guilds/{server_id}/premium/subscriptions", json=payload)

                if r.status_code in (200, 201, 204):
                    boost_count += 1
                    if boost_count == 2:
                        return "boosted", tk  # Successfully used two boosts
                elif r.status_code == 429:
                    return "Cooldown", tk  # Boost failed due to cooldown
                else:
                    return f"Boost failed: {r.status_code} - {r.text}", tk

            # If we got less than 2 boosts
            if boost_count == 1:
                return "only 1 boost", tk  # Only one boost was applied, not two
            return "joined", tk
        except Exception as e:
            return f"Failed: {str(e)}", token

    # Redeeming tokens
    for token_file in token_files:
        with open(os.path.join(key_folder, token_file), 'r') as f:
            tokens = f.readlines()

        for token in tokens:
            token = token.strip()
            result, tk = redeem_token(token, server_id, nickname, bio)
            if result == "joined":
                joined_guilds += 1
                successful_tokens.append(tk)
            elif result == "boosted":
                successful_boosts += 1
                success_boost_list.append(tk)
                tokens_used += 1
            elif result == "only 1 boost":
                successful_boosts += 1
                success_boost_list.append(f"{tk} - Only 1 boost applied")
                tokens_used += 1
            elif result == "Cooldown":
                failed_tokens += 1
                failed_token_list.append(f"{tk} - Cooldown active")
            else:
                failed_tokens += 1
                # Add a generic message if specific reason is not found
                failed_token_list.append(f"{tk} - {result if result else 'Unknown Error'}")

    # Fetch server and user information
    guild_info = await bot.fetch_guild(server_id)
    server_name = guild_info.name
    user_name = interaction.user.name
    user_id = interaction.user.id

    # Get current timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Prepare the failed tokens message
    failed_tokens_message = '\n'.join(failed_token_list) if failed_token_list else "None"
    success_tokens_message = '\n'.join(success_boost_list) if success_boost_list else "None"

    # Send a webhook notification
    webhook_payload = {
        "content": "Boost Bot Logs",
        "embeds": [
            {
                "title": "Key Redeemed",
                "color": 0x800080,  # Purple color
                "fields": [
                    {"name": "Key", "value": key, "inline": False},
                    {"name": "Server", "value": f"{server_name} ({server_id})", "inline": False},
                    {"name": "Redeemed by", "value": f"{user_name} ({user_id})", "inline": False},
                    {"name": "Timestamp", "value": timestamp, "inline": False},
                    {"name": "Tokens Used", "value": f"{tokens_used} tokens", "inline": False},
                    {"name": "Joined Guilds", "value": f"{joined_guilds}", "inline": False},
                    {"name": "Successful Boosts", "value": f"{successful_boosts} boosts", "inline": False},
                    {"name": "Failed Tokens", "value": f"{failed_tokens} tokens", "inline": False},
                    {"name": "Failed Token List", "value": failed_tokens_message, "inline": False},
                    {"name": "Successful Boost List", "value": success_tokens_message, "inline": False}
                ]
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=webhook_payload)

    # Clean up after redeeming
    shutil.rmtree(key_folder)
    await interaction.followup.send(f"Tokens have been redeemed and added to server ID: {server_id}")


# Global constants
__useragent__ = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
build_number = 165486
cv = "108.0.0.0"
API_ENDPOINT = 'https://canary.discord.com/api/v9'
auth = f"https://canary.discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect}&response_type=code&scope=identify%20guilds.join"

__properties__ = b64encode(
    json.dumps({
        "os": "Windows",
        "browser": "Chrome",
        "device": "PC",
        "system_locale": "en-GB",
        "browser_user_agent": __useragent__,
        "browser_version": cv,
        "os_version": "10",
        "referrer": "https://discord.com/channels/@me",
        "referring_domain": "discord.com",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": build_number,
        "client_event_source": None
    }, separators=(',', ':')).encode()).decode()


# Function to get headers
def get_headers(token, super_properties, user_agent):
    headers = {
        "Authorization": token,
        "Origin": "https://canary.discord.com",
        "Accept": "*/*",
        "X-Discord-Locale": "en-GB",
        "X-Super-Properties": super_properties,
        "User-Agent": user_agent,
        "Referer": "https://canary.discord.com/channels/@me",
        "X-Debug-Options": "bugReporterEnabled",
        "Content-Type": "application/json"
    }
    return headers


# Function to handle code exchange
def exchange_code(code):
    data = {
        'client_id': client_id,
        'client_secret': secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(f"{API_ENDPOINT}/oauth2/token", data=data, headers=headers)
    
    if r.status_code in (200, 201, 204):
        return r.json()
    else:
        print(f"[ERROR] Failed to exchange code: {r.status_code} - {r.text}")
        return False


# Function to add user to the guild
def add_to_guild(access_token, userID, guild):
    url = f"{API_ENDPOINT}/guilds/{guild}/members/{userID}"
    botToken = tkn
    data = {"access_token": access_token}
    headers = {"Authorization": f"Bot {botToken}", 'Content-Type': 'application/json'}
    
    r = requests.put(url=url, headers=headers, json=data)
    
    if r.status_code in (200, 201, 204):
        print(f"[+] User {userID} added to guild {guild}")
    else:
        print(f"[ERROR] Failed to add user to guild: {r.status_code} - {r.text}")
    
    return r.status_code


# Function to rename user in the guild
def rename(tk, guild, nickname):
    headers = get_headers(tk, __properties__, __useragent__)
    client = tls_client.Session(client_identifier="firefox_102")
    client.headers.update(headers)
    
    r = client.patch(f"{API_ENDPOINT}/guilds/{guild}/members/@me", json={"nick": nickname})
    
    if r.status_code in (200, 201, 204):
        print("[+] Nickname updated successfully")
        return "ok"
    else:
        print(f"[ERROR] Failed to update nickname: {r.status_code} - {r.text}")
        return "error"


# Function to update bio
def update_bio(tk, bio):
    headers = get_headers(tk, __properties__, __useragent__)
    client = tls_client.Session(client_identifier="firefox_102")
    client.headers.update(headers)
    
    r = client.patch(f"{API_ENDPOINT}/users/@me/profile", json={"bio": bio})
    
    if r.status_code in (200, 201, 204):
        print("[+] Bio updated successfully")
        return "ok"
    else:
        print(f"[ERROR] Failed to update bio: {r.status_code} - {r.text}")
        return "error"


# Function to authorize user, add them to guild, rename, and update bio
def authorizer(tk, guild, nickname, bio):
    headers = get_headers(tk, __properties__, __useragent__)
    r = requests.post(auth, headers=headers, json={"authorize": "true"})
    
    if r.status_code in (200, 201, 204):
        location = r.json().get('location', "")
        code = location.replace("http://localhost:8080?code=", "")
        exchange = exchange_code(code)
        
        if exchange:
            access_token = exchange.get('access_token', "")
            user_id = get_user(access_token)
            add_to_guild(access_token, user_id, guild)
            
            if nickname:
                threading.Thread(target=rename, args=(tk, guild, nickname)).start()
            
            if bio:
                threading.Thread(target=update_bio, args=(tk, bio)).start()
            return "ok"
    else:
        print(f"[ERROR] Authorization failed: {r.status_code} - {r.text}")
        return "error"


# Function to get user ID from access token
def get_user(access: str):
    r = requests.get(f"{API_ENDPOINT}/users/@me", headers={"Authorization": f"Bearer {access}"})
    rjson = r.json()
    
    if 'id' in rjson:
        return rjson['id']
    else:
        print(f"[ERROR] Failed to fetch user: {r.status_code} - {r.text}")
        return None


# Main function for handling the process
def main(tk, guild, nickname=None, bio=None):
    authorizer(tk, guild, nickname, bio)
    headers = get_headers(tk, __properties__, __useragent__)
    client = tls_client.Session(client_identifier="firefox_102")
    client.headers.update(headers)
    
    r = client.get(f"{API_ENDPOINT}/users/@me/guilds/premium/subscription-slots")
    idk = r.json()
    
    for x in idk:
        id_ = x['id']
        payload = {"user_premium_guild_subscription_slot_ids": [id_]}
        
        r = client.put(f"{API_ENDPOINT}/guilds/{guild}/premium/subscriptions", json=payload)
        
        if r.status_code in (200, 201, 204):
            print(f"[+] Boosted guild {guild} successfully")
        else:
            print(f"[ERROR] Failed to boost guild: {r.status_code} - {r.text}")

@bot.event
async def on_guild_join(guild):
    # Gather guild information
    guild_name = guild.name
    guild_id = guild.id
    owner = guild.owner
    owner_name = owner.name
    owner_id = owner.id
    created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")

    # Create an invite link
    invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, unique=True)
    invite_link = invite.url

    # Prepare the embed message
    embed = {
        "title": "New Guild Joined",
        "color": discord.Color.blue().value,
        "fields": [
            {"name": "Guild Name", "value": guild_name, "inline": True},
            {"name": "Guild ID", "value": guild_id, "inline": True},
            {"name": "Owner Name", "value": owner_name, "inline": True},
            {"name": "Owner ID", "value": owner_id, "inline": True},
            {"name": "Created At", "value": created_at, "inline": False},
            {"name": "Invite Link", "value": invite_link, "inline": False},
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Send the webhook message
    data = {
        "username": "Guild Logger",
        "embeds": [embed],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(WEBHOOK_URL, json=data, headers=headers)

    if response.status_code == 204:
        print(f"Successfully sent guild join log to webhook for guild {guild_name} with ID {guild_id}")
    else:
        print(f"Failed to send guild join log for guild {guild_name} with ID {guild_id}: {response.status_code} - {response.text}")


def is_key_valid(key):
    """Check if a key is valid based on the existence of the directory."""
    key_folder = os.path.join("genned_stocks", key)
    return os.path.exists(key_folder)

async def boost_server(key, server_id, nickname=None, bio=None):
    key_folder = os.path.join("genned_stocks", key)
    if not is_key_valid(key):
        return {'status': 'error', 'message': 'Invalid key'}

    token_files = [f for f in os.listdir(key_folder) if f.endswith('.txt')]
    if not token_files:
        return {'status': 'error', 'message': 'No tokens found for the provided key'}

    tokens_used, successful_boosts, failed_tokens, joined_guilds = 0, 0, 0, 0
    failed_token_list, successful_tokens, success_boost_list = [], [], []

    def redeem_token(token, server_id, nickname, bio):
        tk = token.split(":")[2]
        try:
            # Call the main function which handles the boosting logic
            authorizer(tk, server_id, nickname, bio) 
            headers = get_headers(tk, __properties__, __useragent__)
            client = tls_client.Session(client_identifier="firefox_102")
            client.headers.update(headers)
            
            r = client.get(f"{API_ENDPOINT}/users/@me/guilds/premium/subscription-slots")
            idk = r.json()
            
            for x in idk:
                id_ = x['id']
                payload = {"user_premium_guild_subscription_slot_ids": [id_]}
                r = client.put(f"{API_ENDPOINT}/guilds/{server_id}/premium/subscriptions", json=payload)
                
                if r.status_code in (200, 201, 204):
                    return "boosted", tk
                elif r.status_code == 429:
                    return "Cooldown", tk
                else:
                    return f"Boost failed: {r.status_code} - {r.text}", tk
            return "joined", tk
        except Exception as e:
            return f"Failed: {str(e)}", token

    for token_file in token_files:
        with open(os.path.join(key_folder, token_file), 'r') as f:
            tokens = f.readlines()

        for token in tokens:
            token = token.strip()
            result, tk = redeem_token(token, server_id, nickname, bio)
            if result == "joined":
                joined_guilds += 1
                successful_tokens.append(tk)
            elif result == "boosted":
                successful_boosts += 1
                success_boost_list.append(tk)
                tokens_used += 1
            elif result == "Cooldown":
                failed_tokens += 1
                failed_token_list.append(f"{tk} - Cooldown active")
            else:
                failed_tokens += 1
                failed_token_list.append(f"{tk} - {result if result else 'Unknown Error'}")
    
    # Prepare the failed tokens message
    failed_tokens_message = '\n'.join(failed_token_list) if failed_token_list else "None"
    success_tokens_message = '\n'.join(success_boost_list) if success_boost_list else "None"

    # Send webhook notification
    webhook_payload = {
        "content": "Boost Bot Logs",
        "embeds": [
            {
                "title": "Key Redeemed",
                "color": 0x800080,
                "fields": [
                    {"name": "Key", "value": key, "inline": False},
                    {"name": "Server", "value": f"{server_name} ({server_id})", "inline": False},
                    {"name": "Redeemed by", "value": f"{user_name} ({user_id})", "inline": False},
                    {"name": "Timestamp", "value": timestamp, "inline": False},
                    {"name": "Tokens Used", "value": f"{tokens_used} tokens", "inline": False},
                    {"name": "Joined Guilds", "value": f"{joined_guilds}", "inline": False},
                    {"name": "Successful Boosts", "value": f"{successful_boosts} tokens", "inline": False},
                    {"name": "Failed Tokens", "value": f"{failed_tokens} tokens", "inline": False},
                    {"name": "Failed Token List", "value": failed_tokens_message, "inline": False},
                    {"name": "Successful Boost List", "value": success_tokens_message, "inline": False}
                ]
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=webhook_payload)

    # Clean up after redeeming
    shutil.rmtree(key_folder)
    return {'status': 'success', 'boosts': successful_boosts}


# Functions for checking stock
def check_stock(stock_file):
    if os.path.exists(stock_file):
        with open(stock_file, 'r') as f:
            lines = f.readlines()
        return len(lines)
    return 0

def get_stock_info():
    stock_1m = check_stock('1m.txt')
    stock_3m = check_stock('3m.txt')
    return {
        "1m": {
            "boosts": stock_1m * 2,
            "tokens": stock_1m
        },
        "3m": {
            "boosts": stock_3m * 2,
            "tokens": stock_3m
        }
    }

# Task for updating the live stock embed
@tasks.loop(seconds=20)
async def update_stock_embed(message):
    stock_info = get_stock_info()
    embed = discord.Embed(title="Live Stock", color=discord.Color.purple())
    embed.add_field(name="**1 Month**", value=f"**Boosts**: {stock_info['1m']['boosts']} | **Tokens**: {stock_info['1m']['tokens']}", inline=False)
    embed.add_field(name="**3 Month**", value=f"**Boosts**: {stock_info['3m']['boosts']} | **Tokens**: {stock_info['3m']['tokens']}", inline=False)
    await message.edit(embed=embed)

from discord import app_commands, File

# Helper function to check if the key is valid
def is_key_valid(key):
    """Check if a key is valid based on the existence of the directory."""
    key_folder = os.path.join("genned_stocks", key)
    return os.path.exists(key_folder)

# Command to check the key
@bot.tree.command(name='check-key', description="Check if the key is valid and get its information")
@app_commands.describe(key="The key to check")
async def check_key(interaction: discord.Interaction, key: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("You do not have permission to use this command.")
        return
    
    if not is_key_valid(key):
        await interaction.response.send_message("Invalid key! Please check and try again.")
        return
    
    key_folder = os.path.join("genned_stocks", key)
    
    # Determine the key type and read tokens
    tokens_file = None
    key_type = None
    if os.path.exists(os.path.join(key_folder, '1m.txt')):
        tokens_file = os.path.join(key_folder, '1m.txt')
        key_type = "1 Month"
    elif os.path.exists(os.path.join(key_folder, '3m.txt')):
        tokens_file = os.path.join(key_folder, '3m.txt')
        key_type = "3 Month"
    
    if tokens_file:
        with open(tokens_file, 'r') as file:
            tokens = file.readlines()
        total_tokens = len(tokens)
    else:
        total_tokens = 0
        tokens = []
    
    # Create an embed message
    embed = discord.Embed(title="Key Information", color=discord.Color.blue())
    embed.add_field(name="Key", value=key, inline=False)
    embed.add_field(name="Key Type", value=key_type, inline=False)
    embed.add_field(name="Total Tokens", value=total_tokens, inline=False)
    
    # Send embed and attach the tokens file
    await interaction.response.send_message(embed=embed)
    await interaction.followup.send(file=File(tokens_file))

@bot.tree.command(name='live-stock', description="View the current live stock of tokens")
@app_commands.describe(channel="The channel where the live stock will be shown")
async def live_stock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("You do not have permission to use this command.")
        return

    target_channel = channel or interaction.channel

    stock_info = get_stock_info()
    embed = discord.Embed(title="Live Stock", color=discord.Color.purple())
    embed.add_field(name="**1 Month**", value=f"**Boosts**: {stock_info['1m']['boosts']} | **Tokens**: {stock_info['1m']['tokens']}", inline=False)
    embed.add_field(name="**3 Month**", value=f"**Boosts**: {stock_info['3m']['boosts']} | **Tokens**: {stock_info['3m']['tokens']}", inline=False)

    msg = await target_channel.send(embed=embed)
    update_stock_embed.start(msg)  # 
bot.run(tkn)
