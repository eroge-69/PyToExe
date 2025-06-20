import discord
import asyncio
import os
import sys
import random
from pystyle import Colors, Write, Colorate

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def set_title():
    os.system("title [ YASSINE'S PRESSURE ]" if os.name == "nt" else "")

def print_ascii_art():
    print(Colorate.Horizontal(Colors.white_to_red, """
██████╗░██████╗░███████╗░██████╗░██████╗██╗░░░██╗██████╗░███████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██║░░░██║██╔══██╗██╔════╝
██████╔╝██████╔╝█████╗░░╚█████╗░╚█████╗░██║░░░██║██████╔╝█████╗░░
██╔═══╝░██╔══██╗██╔══╝░░░╚═══██╗░╚═══██╗██║░░░██║██╔══██╗██╔══╝░░
██║░░░░░██║░░██║███████╗██████╔╝██████╔╝╚██████╔╝██║░░██║███████╗
╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚═════╝░╚═════╝░░╚═════╝░╚═╝░░╚═╝╚══════╝
"""))

def print_menu():
    print(Colorate.Horizontal(Colors.white_to_red, """
╔════════════════════════════════════════════════════════╗
║  Type 'dude' followed by a user mention to start spam  ║
║  Type '.stop' in any channel for the spam to stop      ║
╚════════════════════════════════════════════════════════╝
"""))

# Content pools
weapons = ["Glock", "38", "bat", "knife", "axe", "chainsaw", "machete"]
disabilities = ["hearing disability", "seeing disability", "breathing disability"]
actions = ["drop kicked", "body slammed", "punched on"]
bodies = ["nose", "knuckles", "kneecaps", "nipple"]
names = ["VAL", "CK", "REQ", "AMINE"]
adjectives = ["fat", "stupid", "ugly"]
objects = ["bucket", "brick", "shoe"]
families = ["mom", "dad", "uncle"]
animals = ["dog", "cat", "rat"]

def generate_message():
    template = random.choice([
        "YO {adj} {obj} with {disab}",
        "ILL KILL YOUR {fam} with a {obj} to the {body}",
        "YOUR GIRL WAS FUCKED BY A {anim} in the {body}",
        "you got a {obj} {body}",
        "THAT DUDE GOT {act} by a {obj}",
        "LOL, {name} KILLED YOUR DAD"
    ])
    return template.format(
        adj=random.choice(adjectives),
        obj=random.choice(objects + weapons),
        disab=random.choice(disabilities),
        fam=random.choice(families),
        body=random.choice(bodies),
        anim=random.choice(animals),
        name=random.choice(names),
        act=random.choice(actions)
    )

async def spam_messages(client, channel, user_id):
    global spam_running
    spam_running = True
    slow_rate = 1.7
    ping = f"<@{user_id}>"
    while spam_running:
        message = f"{ping} {generate_message()}"
        try:
            await channel.send(message)
        except discord.errors.HTTPException as e:
            if e.status == 429:
                await asyncio.sleep(slow_rate)
            else:
                raise e
        else:
            await asyncio.sleep(slow_rate)

async def main():
    set_title()
    clear_screen()
    print_ascii_art()
    token = input(Colorate.Horizontal(Colors.white_to_red, "[>] User Token --->: ")).strip()
    clear_screen()
    print_ascii_art()
    global spam_running
    spam_running = False

    client = discord.Client()  # ✅ No intents for discord.py-self
    global owner_id
    owner_id = None

    @client.event
    async def on_ready():
        global owner_id
        owner_id = client.user.id
        clear_screen()
        print_ascii_art()
        print_menu()

    @client.event
    async def on_message(message):
        global spam_running
        if message.author.id != owner_id:
            return
        if message.content.lower().startswith("dude"):
            if not message.mentions:
                await message.channel.send("Mention a user to spam.")
                return
            if spam_running:
                await message.channel.send("Already spamming. Type `.stop` to stop.")
                return
            user_id = message.mentions[0].id
            await spam_messages(client, message.channel, user_id)
        elif message.content.lower() == ".stop":
            spam_running = False
            Write.Print("Spam stopped!", Colors.white_to_red, interval=0.05)

    try:
        await client.start(token)  
    except discord.LoginFailure:
        Write.Print("Token invalid.", Colors.white_to_red, interval=0.05)
    except Exception as e:
        Write.Print(f"An error occurred: {e}", Colors.white_to_red, interval=0.05)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        input("Press Enter to exit...")
        sys.exit()
