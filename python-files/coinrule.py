import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import logging
import asyncio

# -------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WELCOME_CHANNEL_ID = 973618525522497538

ICON_URL = "https://yourdomain.com/icon.png"
BANNER_URL = "https://s3.coinmarketcap.com/static-gravity/image/e13849d0c8ff4c20b221c1593176974c.jpg"
AUTHOR_ICON_URL = "https://yourdomain.com/coinrule_logo.png"
CUSTOM_BANNER_URL = BANNER_URL
EMOJI_URL = "https://cdn.discordapp.com/emojis/1404084074183659564.webp?size=96"
DISCORD_EMOJI = "<:syspbd:1404084074183659564>"

# -------------------------
# LOGGING & BOT SETUP
# -------------------------
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# SECURITY MEASURES
# -------------------------

@bot.event
async def on_command_error(ctx, error):
    logging.warning(f"Unhandled command error: {error}")
    try:
        await ctx.send("An error occurred. Please contact an admin if this persists.", ephemeral=True)
    except Exception as e:
        logging.warning(f"Failed to send error message to user: {e}")

def global_cooldown():
    return commands.cooldown(1, 5, commands.BucketType.user)

original_add_command = bot.add_command
def add_command_with_cooldown(command):
    if not getattr(command, 'has_cooldown', False):
        command = global_cooldown()(command)
        command.has_cooldown = True
    original_add_command(command)
bot.add_command = add_command_with_cooldown

GUILD_ID = 973618525522497536
MEMBER_COUNT_CHANNEL_ID = 1404117609930297476
BOT_COUNT_CHANNEL_ID = 1404118906674610286

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="VIP", style=discord.ButtonStyle.secondary, row=0, custom_id="welcome_vip")
    async def vip(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="VIP Access & Benefits",
            description=(
                "💎 **How to Access the VIP Channels**\n\n"
                f"{DISCORD_EMOJI} VIP access is available to all users on paid plans, unlocking:\n"
                f"{DISCORD_EMOJI} Exclusive trading tips from community members\n"
                f"{DISCORD_EMOJI} Additional support from the Coinrule team\n"
                f"{DISCORD_EMOJI} Strategy discussions with experienced traders\n\n"
                "🔗 **Steps to Join VIP Channels:**\n"
                "1️⃣ Go to the Coinrule Dashboard → Settings → Account\n"
                "2️⃣ Look for a new VIP banner in your Coinrule account\n"
                "3️⃣ Click **Join** to connect your account to Discord\n"
                "4️⃣ Once linked, you’ll automatically receive the **Premium VIP** role and gain access to all locked channels\n\n"
                "✨ Joining Coinrule’s VIP Discord is an incredible way to enhance your trading journey with expert insights and a supportive community. If you're on a paid plan, don’t miss out!"
            ),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=ICON_URL)
        embed.set_image(url=CUSTOM_BANNER_URL)
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            logging.error("Interaction expired before response could be sent (VIP button).")
        except Exception as e:
            logging.error(f"Failed to send VIP embed: {e}")

    @discord.ui.button(label="Official Links", style=discord.ButtonStyle.secondary, row=0, custom_id="welcome_links")
    async def official_links(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Official Links",
            description=(
                "**Coinrule Site**\n"
                f"{DISCORD_EMOJI} [website](https://coinrule.com/)\n"
                f"{DISCORD_EMOJI} [platform](https://web.coinrule.com/)\n\n"
                "**Coinrule Socials**\n"
                f"{DISCORD_EMOJI} [twitter](https://x.com/CoinRuleHQ)\n"
                f"{DISCORD_EMOJI} [youtube](https://www.youtube.com/@Coinrule)\n"
                f"{DISCORD_EMOJI} [linkedin](https://www.linkedin.com/company/coinrule)\n"
                f"{DISCORD_EMOJI} [facebook](https://web.facebook.com/CoinruleHQ/)\n"
                f"{DISCORD_EMOJI} [instagram](https://www.instagram.com/coinrulehq/)\n"
                f"{DISCORD_EMOJI} [tiktok](https://www.tiktok.com/@coinrulehq)\n\n"
                "**Other Platforms**\n"
                f"{DISCORD_EMOJI} [tradingview](https://www.tradingview.com/u/Coinrule/)\n"
                f"{DISCORD_EMOJI} [coinmarketcap](https://coinmarketcap.com/community/profile/CoinruleHQ/)"
            )
        )
        embed.set_thumbnail(url=ICON_URL)
        embed.set_image(url=CUSTOM_BANNER_URL)
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            logging.error("Interaction expired before response could be sent (Official Links button).")
        except Exception as e:
            logging.error(f"Failed to send Official Links embed: {e}")

    @discord.ui.button(label="Resources", style=discord.ButtonStyle.secondary, row=0, custom_id="welcome_resources")
    async def resources(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Resources",
            description=(
                "**Help & Support**\n"
                f"{DISCORD_EMOJI} [help centre](https://help.coinrule.com/)\n"
                f"{DISCORD_EMOJI} [knowledgebase](https://coinrule.com/help/)\n"
                f"{DISCORD_EMOJI} [faq](https://help.coinrule.com/categories/573935-frequently-asked-questions)\n"
                f"{DISCORD_EMOJI} [technical faq](https://help.coinrule.com/categories/980014-technical-faq)\n\n"
                "**Getting Started**\n"
                f"{DISCORD_EMOJI} [get started](https://coinrule.com/help/faq-get-started-with-coinrule/)\n"
                f"{DISCORD_EMOJI} [templates](https://help.coinrule.com/categories/574672-template-rules)\n\n"
                "**Markets & Features**\n"
                f"{DISCORD_EMOJI} [stocks](https://help.coinrule.com/categories/935654-automated-trading-for-stocks)\n"
                f"{DISCORD_EMOJI} [leverage](https://help.coinrule.com/categories/190493-trading-with-leverage-on-coinrule)\n\n"
                "**Updates**\n"
                f"{DISCORD_EMOJI} [blog](https://coinrule.com/blog/)"
            )
        )
        embed.set_thumbnail(url=ICON_URL)
        embed.set_image(url=CUSTOM_BANNER_URL)
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            logging.error("Interaction expired before response could be sent (Resources button).")
        except Exception as e:
            logging.error(f"Failed to send Resources embed: {e}")

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.secondary, row=0, custom_id="welcome_rules")
    async def rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        rules_text = """**1. No advertisement**

Don't advertise your discord server (plainly posting an invite counts). Don't advertise your social media. Don't tell people to message you to get a link. Don't tell people you are looking for staff members. Violating this is an easy way to get a permanent ban.

**2. No harassment**

Don't go out of your way to annoy someone. If you act weird towards someone, and they tell you to stop it, you should do so.

**3. Be respectful**

We are all people here, and we don't expect you to write a formal letter for every message, however being disrespectful won't be accepted.

**4. Don't attempt to evade punishments**

This includes alts or messaging other people to say something on your behalf, or anything else that allows you to get past your punishment. This is another easy way to get a permanent ban.

**6. Don't cause drama**

If you have a personal conflict with someone, talk it out in DMs. If someone broke a rule, you are free to message a moderator about it.

**7. Don't challenge mod actions**

If you think a moderator is being unjust, you can ask them on their reasoning, but you shouldn't cause drama or be disrespectful. If you are sure they are being unreasonable, you can message a superior staff member about it, but don't just start screaming in the chat or in DMs.

**8. Use common sense**

Just because it isn't in the rules does not mean you are free to do it. If you are unsure if something is allowed, message a moderator. If you are told to stop doing something, stop it.

**9. Follow ToS**

This includes our own ToS and Discord's ToS and any other applicable document.

```
Moderators reserve the right to take action on any behavior deemed disruptive, even if not explicitly listed here.
```
"""
        embed = discord.Embed(
            title="Community Guidelines & Discord Rules",
            description=rules_text
        )
        embed.set_thumbnail(url=ICON_URL)
        embed.set_image(url=BANNER_URL)
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            logging.error("Interaction expired before response could be sent (Rules button).")
        except Exception as e:
            logging.error(f"Failed to send Rules embed: {e}")

async def post_welcome_message():
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        try:
            last_message = None
            async for message in channel.history(limit=1):
                last_message = message
            if last_message and last_message.author == bot.user:
                await last_message.delete()
                logging.info("Previous main embed deleted successfully.")
            else:
                logging.info("No previous main embed to delete or last message not sent by bot.")
        except Exception as e:
            logging.warning(f"Could not delete previous message: {e}")

        embed = discord.Embed(
            title="Coinrule",
            description=(
                "> Automate Trading 24/7\n"
                "> 300+ Strategies, Infinite Potential\n\n"
                "> Automations for the top 10+\n"
                "> Popular Exchanges/Chains\n\n"
                "> Military-grade\n"
                "> Security & Encryption"
            ),
        )
        embed.set_thumbnail(url=ICON_URL)
        embed.set_image(url=BANNER_URL)
        try:
            await channel.send(embed=embed, view=WelcomeView())
            logging.info("New main embed posted successfully.")
        except Exception as e:
            logging.error(f"Failed to post welcome embed: {e}")
    else:
        logging.warning("Welcome channel not found.")

async def update_member_count():
    await bot.wait_until_ready()
    previous_count = None
    while not bot.is_closed():
        try:
            guild = bot.get_guild(GUILD_ID)
            channel = bot.get_channel(MEMBER_COUNT_CHANNEL_ID)
            logging.info(f"[MemberCount] Guild: {guild} (ID: {GUILD_ID})")
            logging.info(f"[MemberCount] Channel: {channel} (ID: {MEMBER_COUNT_CHANNEL_ID})")
            if channel:
                logging.info(f"[MemberCount] Channel type: {type(channel)}")
                perms = channel.permissions_for(guild.me)
                logging.info(f"[MemberCount] Bot permissions in channel: {perms}")
            if guild and channel and isinstance(channel, discord.VoiceChannel):
                member_count = sum(1 for m in guild.members if not m.bot)
                logging.info(f"[MemberCount] Calculated member count: {member_count}")
                if previous_count is None or previous_count != member_count:
                    await channel.edit(name=f"👤・Members: {member_count}")
                    logging.info(
                        f"[MemberCount] Updated channel name to: 👤・Members: {member_count} | Previous: {previous_count} | New: {member_count}"
                    )
                    previous_count = member_count
                else:
                    logging.info(f"[MemberCount] No change in member count ({member_count}), not updating channel name.")
            else:
                logging.warning("[MemberCount] Guild or member count channel not found or not a voice channel.")
        except Exception as e:
            logging.warning(f"[MemberCount] Failed to update member count: {e}")
        await asyncio.sleep(600)  # Update every 10 minutes

async def update_bot_count():
    await bot.wait_until_ready()
    previous_count = None
    while not bot.is_closed():
        try:
            guild = bot.get_guild(GUILD_ID)
            channel = bot.get_channel(BOT_COUNT_CHANNEL_ID)
            logging.info(f"[BotCount] Guild: {guild} (ID: {GUILD_ID})")
            logging.info(f"[BotCount] Channel: {channel} (ID: {BOT_COUNT_CHANNEL_ID})")
            if channel:
                logging.info(f"[BotCount] Channel type: {type(channel)}")
                perms = channel.permissions_for(guild.me)
                logging.info(f"[BotCount] Bot permissions in channel: {perms}")
            if guild and channel and isinstance(channel, discord.VoiceChannel):
                bot_count = sum(1 for m in guild.members if m.bot)
                logging.info(f"[BotCount] Calculated bot count: {bot_count}")
                if previous_count is None or previous_count != bot_count:
                    await channel.edit(name=f"🤖・Bots: {bot_count}")
                    logging.info(
                        f"[BotCount] Updated channel name to: 🤖・Bots: {bot_count} | Previous: {previous_count} | New: {bot_count}"
                    )
                    previous_count = bot_count
                else:
                    logging.info(f"[BotCount] No change in bot count ({bot_count}), not updating channel name.")
            else:
                logging.warning("[BotCount] Guild or bot count channel not found or not a voice channel.")
        except Exception as e:
            logging.warning(f"[BotCount] Failed to update bot count: {e}")
        await asyncio.sleep(600)  # Update every 10 minutes

@bot.event
async def on_ready():
    logging.info(f"Bot is online as {bot.user}")
    # Register persistent views so button interactions always work after restart
    bot.add_view(WelcomeView())
    await post_welcome_message()
    # Immediate update on startup
    bot.loop.create_task(update_member_count())
    bot.loop.create_task(update_bot_count())

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)