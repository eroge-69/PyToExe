import discord
import asyncio
import os
from discord.ext import commands
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

class DiscordTool:
    def __init__(self, token):
        self.token = token
        self.bot = commands.Bot(command_prefix='!', self_bot=True, intents=discord.Intents.all())
        
        @self.bot.event
        async def on_ready():
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'\n\n{Fore.GREEN}Logged in as {Style.BRIGHT}{self.bot.user}{Style.RESET_ALL}')
            await self.main_menu()
    
    def print_header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""
{Fore.CYAN}
                                            • ▌ ▄ ·. ▄• ▄▌·▄▄▄▄• ▄▄▄·  ▐ ▄ 
                                            ·██ ▐███▪█▪██▌▪▀·.█▌▐█ ▀█ •█▌▐█
                                            ▐█ ▌▐▌▐█·█▌▐█▌▄█▀▀▀•▄█▀▀█ ▐█▐▐▌
                                            ██ ██▌▐█▌▐█▄█▌█▌▪▄█▀▐█ ▪▐▌██▐█▌
                                            ▀▀  █▪▀▀▀ ▀▀▀ ·▀▀▀ • ▀  ▀ ▀▀ █▪
{Style.RESET_ALL}""")
        print(f"{Fore.YELLOW}\n                                       The Power Of .gg/muzaan{Style.RESET_ALL}\n")
    
    async def main_menu(self):
        while True:
            self.print_header()
            print(f"{Fore.CYAN}                                        <1> Rename Server")
            print(f"                                        <2> Change Custom Invite Link")
            print(f"                                        <3> Change All Text Channel Names")
            print(f"                                        <4> Change All Voice Channel Names")
            print(f"                                        <5> Mass Ban Members")
            print(f"                                        <6> Delete All Messages in Server")
            print(f"                                        <0> Exit{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}                                        [~] Your Choice:{Style.RESET_ALL}")
            
            choice = input("                    ").strip()
            
            if choice == "1":
                await self.rename_server()
            elif choice == "2":
                await self.change_invite_link()
            elif choice == "3":
                await self.change_text_channels()
            elif choice == "4":
                await self.change_voice_channels()
            elif choice == "5":
                if await self.confirm_action("mass ban"):
                    await self.mass_ban()
            elif choice == "6":
                if await self.confirm_action("delete all messages"):
                    await self.delete_all_messages()
            elif choice == "0":
                print(f"\n{Fore.YELLOW}                                        Exiting...{Style.RESET_ALL}")
                await self.bot.close()
                return
            else:
                print(f"\n{Fore.RED}                                        Invalid choice. Please try again.{Style.RESET_ALL}")
                await asyncio.sleep(2)
    
    async def confirm_action(self, action):
        confirm = input(f"\n{Fore.RED}                                        WARNING: This will {action.upper()}. Are you sure? (y/n): {Style.RESET_ALL}")
        if confirm.lower() != 'y':
            print(f"{Fore.YELLOW}                                        Action cancelled.{Style.RESET_ALL}")
            await asyncio.sleep(2)
            return False
        return True
    
    async def rename_server(self):
        self.print_header()
        guild_id = input(f"\n{Fore.CYAN}                                        Enter server ID: {Style.RESET_ALL}")
        new_name = input(f"{Fore.CYAN}                                        Enter new server name: {Style.RESET_ALL}")
        
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            try:
                await guild.edit(name=new_name)
                print(f"\n{Fore.GREEN}                                        Server renamed to '{Style.BRIGHT}{new_name}{Style.RESET_ALL}{Fore.GREEN}' successfully!{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}                                        Error renaming server: {e}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}                                        Server not found or bot doesn't have permission.{Style.RESET_ALL}")
        await asyncio.sleep(3)
    
    async def change_invite_link(self):
        self.print_header()
        guild_id = input(f"\n{Fore.CYAN}                                        Enter server ID: {Style.RESET_ALL}")
        new_code = input(f"{Fore.CYAN}                                        Enter new invite code (leave empty to reset): {Style.RESET_ALL}")
        
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            try:
                if new_code:
                    await guild.vanity_invite.edit(code=new_code)
                    print(f"\n{Fore.GREEN}                                        Custom invite link changed to {Style.BRIGHT}discord.gg/{new_code}{Style.RESET_ALL}")
                else:
                    await guild.vanity_invite.delete()
                    print(f"\n{Fore.GREEN}                                        Custom invite link reset to default.{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}                                        Error changing invite link: {e}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}                                        Server not found or bot doesn't have permission.{Style.RESET_ALL}")
        await asyncio.sleep(3)
    
    async def change_text_channels(self):
        self.print_header()
        guild_id = input(f"\n{Fore.CYAN}                                        Enter server ID: {Style.RESET_ALL}")
        new_name = input(f"{Fore.CYAN}                                        Enter new name for all text channels: {Style.RESET_ALL}")
        
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            try:
                for channel in guild.text_channels:
                    await channel.edit(name=f"{new_name}-{channel.position}")
                    print(f"{Fore.YELLOW}                                        Renamed #{channel.name}{Style.RESET_ALL}")
                print(f"\n{Fore.GREEN}                                        All text channels renamed successfully!{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}                                        Error renaming channels: {e}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}                                        Server not found or bot doesn't have permission.{Style.RESET_ALL}")
        await asyncio.sleep(3)
    
    async def change_voice_channels(self):
        self.print_header()
        guild_id = input(f"\n{Fore.CYAN}                                        Enter server ID: {Style.RESET_ALL}")
        new_name = input(f"{Fore.CYAN}                                        Enter new name for all voice channels: {Style.RESET_ALL}")
        
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            try:
                for channel in guild.voice_channels:
                    await channel.edit(name=f"{new_name}-{channel.position}")
                    print(f"{Fore.YELLOW}                                        Renamed 🔊 {channel.name}{Style.RESET_ALL}")
                print(f"\n{Fore.GREEN}                                        All voice channels renamed successfully!{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}                                        Error renaming channels: {e}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}                                        Server not found or bot doesn't have permission.{Style.RESET_ALL}")
        await asyncio.sleep(3)
    
    async def mass_ban(self):
        self.print_header()
        guild_id = input(f"\n{Fore.CYAN}                                        Enter server ID: {Style.RESET_ALL}")
        reason = input(f"{Fore.CYAN}                                        Enter ban reason: {Style.RESET_ALL}")
        
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            try:
                for member in guild.members:
                    if member != self.bot.user and not member.guild_permissions.administrator:
                        try:
                            await member.ban(reason=reason)
                            print(f"{Fore.RED}                                        Banned {Style.BRIGHT}{member.name}{Style.RESET_ALL}")
                        except:                    
                            print(f"{Fore.YELLOW}                    Couldn't ban {member.name}{Style.RESET_ALL}")
                print(f"\n{Fore.GREEN}                                        Mass ban completed!{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}                                        Error during mass ban: {e}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}                                        Server not found or bot doesn't have permission.{Style.RESET_ALL}")
        await asyncio.sleep(3)
    
    async def delete_all_messages(self):
        self.print_header()
        guild_id = input(f"\n{Fore.CYAN}                                        Enter server ID: {Style.RESET_ALL}")
        guild = self.bot.get_guild(int(guild_id))
        
        if guild:
            try:
                for channel in guild.text_channels:
                    try:
                        async for message in channel.history(limit=None):
                            try:
                                await message.delete()
                                print(f"{Fore.YELLOW}                                        Deleted message in #{channel.name}{Style.RESET_ALL}")
                            except:
                                continue
                    except:
                        continue
                print(f"\n{Fore.GREEN}                                        All messages deleted successfully!{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}                                        Error deleting messages: {e}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}                                        Server not found or bot doesn't have permission.{Style.RESET_ALL}")
        await asyncio.sleep(3)
    
    def run(self):
        try:
            self.bot.run(self.token, bot=False)
        except discord.LoginFailure:
            print(f"\n{Fore.RED}                                        Invalid token. Please check your token and try again.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}                                        An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    token = input(f"{Fore.RED}Enter your Discord token: {Style.RESET_ALL}")
    tool = DiscordTool(token)
    tool.run()