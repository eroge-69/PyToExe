import discord
import asyncio
import os
import sys
import keyboard
import json

SAVE_FILE = "saved.json"

PURPLE = "\033[95m"
RED = "\033[91m"
ORANGE = "\033[38;5;208m"
YELLOW = "\033[93m"
RESET = "\033[0m"

stop_program = False

def save_settings(token, channel, message, delay):
    data = {"token": token, "channel": channel, "message": message, "delay": delay}
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"{YELLOW}[NOTE]: Settings saved to {SAVE_FILE}.{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR]: Failed to save settings: {e}{RESET}")

def get_and_process_inputs():
    token, channel_id, message, delay = None, None, None, None

    if os.path.exists(SAVE_FILE):
        use_saved = input(f"{YELLOW}Saved settings file '{SAVE_FILE}' found. Use it? (y/n): {RESET}").lower()
        if use_saved in ['y', 'yes']:
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    token = data['token']
                    channel_id = int(data['channel'])
                    message = data['message']
                    delay = float(data.get('delay', 2.0)) # Default to 2s if not in file
                print(f"{YELLOW}[NOTE]: Loaded settings from {SAVE_FILE}.{RESET}")
                return token, channel_id, message, delay
            except Exception as e:
                print(f"{RED}[ERROR]: Could not read '{SAVE_FILE}'. It may be corrupted. ({e}){RESET}")
    
    print("----------------------------")
    token = input("USER TOKEN: ")
    message = input("MESSAGE: ")
    channel_id = int(input("CHANNEL ID: "))
    delay = float(input("TIME BETWEEN MESSAGES (seconds): "))
    print("----------------------------")

    save_choice = input(f"{YELLOW}Save these settings to '{SAVE_FILE}' for next time? (y/n): {RESET}").lower()
    if save_choice in ['y', 'yes']:
        save_settings(token, channel_id, message, delay)

    return token, channel_id, message, delay

print(PURPLE + "▗▖  ▗▖▗▄▄▖▗▄▄▖▗▄▄▖")
print("▐▛▚▞▜▐▌  ▐▌  ▐▌")
print("▐▌  ▐▌▝▀▚▐▌▝▜▌▝▀▚▖")
print("▐▌  ▐▗▄▄▞▝▚▄▞▗▄▄➍ discord message spammer"+ RESET + "\n")
print("created by errorrail!")
print(f"\n{YELLOW}[NOTE]: Press the 'ESC' key at any time to stop the script.{RESET}\n\n")

USER_TOKEN, CHANNEL_ID, MESSAGE, DELAY = get_and_process_inputs()

client = discord.Client()

message_counter = 1

async def send_messages():
    global message_counter, stop_program
    
    channel = None
    try:
        channel = await client.fetch_channel(CHANNEL_ID)
    except discord.NotFound:
        print(f"{RED}[ERROR]: Channel with ID {CHANNEL_ID} was not found.{RESET}")
        return
    except discord.Forbidden:
        print(f"{RED}[ERROR]: You don't have permission to view or send messages in channel {CHANNEL_ID}.{RESET}")
        return
    except Exception as e:
        print(f"{RED}[ERROR]: An unexpected error occurred while fetching the channel: {e}{RESET}")
        return

    while not stop_program:
        try:
            message_content = f"{MESSAGE} ({message_counter})"
            await channel.send(message_content)
            print(f"Sent message #{message_counter} to channel {channel.name}")
            message_counter += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.retry_after
                print(f"{ORANGE}[WARNING]: We are being rate limited! Waiting for {retry_after:.2f} seconds...{RESET}")
                await asyncio.sleep(retry_after)
                continue # Retry sending the message after waiting
            else:
                print(f"{RED}[ERROR]: An HTTP error occurred: {e.status} {e.text}{RESET}")
                break
        except discord.Forbidden:
            print(f"{ORANGE}[WARNING]: Can't send message. You are likely timed out or muted. Retrying...{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR]: An unexpected error occurred while sending a message: {e}{RESET}")
            break
            
        # Wait for the user-defined delay, while also checking for the ESC key
        wait_interval = 0.1
        steps = int(DELAY / wait_interval)
        for _ in range(steps):
            if stop_program:
                break
            await asyncio.sleep(wait_interval)

    print(f"\n{YELLOW}[NOTE]: 'ESC' key pressed. Shutting down...{RESET}")
    await client.close()

@client.event
async def on_ready():
    print("----------------------------")
    print(f'{YELLOW}[NOTE]: Logged in as {client.user}{RESET}')
    print(f'{YELLOW}[NOTE]: Starting to send messages with a {DELAY} second delay.{RESET}')
    await send_messages()

def shutdown():
    global stop_program
    stop_program = True

keyboard.add_hotkey('esc', shutdown)

try:
    client.run(USER_TOKEN)
except discord.LoginFailure:
    print(f"{RED}[ERROR]: Login failed. The token you provided is invalid.{RESET}")
except Exception as e:
    print(f"{RED}[ERROR]: An error occurred while running the client: {e}{RESET}")

print(f"{YELLOW}[NOTE]: Program has been terminated.{RESET}")