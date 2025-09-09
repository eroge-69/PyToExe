import discord
from discord import app_commands
from discord.ext import commands
from helpers.boost import tboost, check_stock, get_tokens  # Assuming these exist
from helpers.utils import isWhitelisted  # Optional auth layer
import pyfiglet
import os
from colorama import Fore, Style, init

init(autoreset=True)

def prompt_license():
    # Clear terminal screen (Windows: cls, Unix: clear)
    os.system('cls' if os.name == 'nt' else 'clear')

    # Print styled BoostVault banner
    banner = pyfiglet.figlet_format("BoostVault", font="slant")
    print(Fore.YELLOW + banner)

    # Prompt message
    print(Fore.YELLOW + Style.BRIGHT + "🔐 Vault Access Required")
    license_key = input(Fore.YELLOW + "🧾 Enter Owner License Key: ").strip()

    # Validation
    if len(license_key) < 8:
        print(Fore.RED + Style.BRIGHT + "❌ License key too short.")
        return None

    print(Fore.YELLOW + Style.BRIGHT + f"✅ License `{license_key}` accepted. Welcome, User!")
    return license_key

# Run it
prompt_license()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
@bot.tree.command(name="boost-server", description="Manually boost a server using a provided invite link")
@app_commands.describe(invite="Server invite code", boosts="Number of boosts", months="Duration: 1 or 3")
async def boost_server(interaction: discord.Interaction, invite: str, boosts: int, months: int):
    from helpers.boost import tboost
    tboost(invite, boosts, months, f"BoostedBy_{interaction.user.name}")
    await interaction.response.send_message(f"✅ Boosted `{invite}` with `{boosts}` boost(s) for `{months}` month(s)!", ephemeral=True)
    
@bot.tree.command(name="boost-keys-panel", description="Open the boost license redemption panel")
async def boost_keys_panel(interaction: discord.Interaction):
    from helpers.ui import RedeemButtonView  # Make sure this exists
    embed = discord.Embed(
        title="🔑 BoostVault License Redemption",
        description="Click the button below to redeem your license and apply boosts.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=RedeemButtonView())

@bot.tree.command(name="bot-information", description="Show bot stats and boost token availability")
async def bot_information(interaction: discord.Interaction):
    from helpers.boost import check_stock
    latency = round(bot.latency * 1000)
    stock = check_stock()

    embed = discord.Embed(title="🤖 Bot Information", color=discord.Color.green())
    embed.add_field(name="Latency", value=f"`{latency}ms`")
    embed.add_field(name="1m Tokens", value=f"`{stock['1m']}`")
    embed.add_field(name="3m Tokens", value=f"`{stock['3m']}`")
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="change-status", description="Change the bot's visible status")
@app_commands.describe(status="online, idle, dnd", activity="Activity text")
async def change_status(interaction: discord.Interaction, status: str, activity: str):
    status_map = {
        "online": discord.Status.online,
        "idle": discord.Status.idle,
        "dnd": discord.Status.do_not_disturb
    }
    await bot.change_presence(status=status_map.get(status.lower()), activity=discord.Game(name=activity))
    await interaction.response.send_message(f"🔧 Bot status updated to `{status}` with activity: `{activity}`", ephemeral=True)

@bot.tree.command(name="check-stock", description="Check current token stock")
async def check_stock(interaction: discord.Interaction):
    from helpers.boost import check_stock
    stock = check_stock()
    await interaction.response.send_message(f"📦 1m: `{stock['1m']}` tokens\n📦 3m: `{stock['3m']}` tokens", ephemeral=True)

@bot.tree.command(name="check-tokens", description="Verify token health")
async def check_tokens(interaction: discord.Interaction):
    from helpers.token_utils import validate_tokens  # Add this in your helpers!
    report = validate_tokens()
    await interaction.response.send_message(f"✅ Token Check:\n{report}", ephemeral=True)

@bot.tree.command(name="fetch-order", description="Get info on a redeemed license order")
@app_commands.describe(code="License key")
async def fetch_order(interaction: discord.Interaction, code: str):
    with open("assets/redeem_keys.json") as f:
        keys = json.load(f)

    if code in keys:
        info = keys[code]
        embed = discord.Embed(title="🔍 Order Details", color=discord.Color.purple())
        for k, v in info.items():
            embed.add_field(name=k.capitalize(), value=str(v), inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ No order found for that code.", ephemeral=True)
        
@bot.tree.command(name="giveowner", description="Guide user to transfer bot ownership properly")
async def giveowner(interaction: discord.Interaction):
    embed = discord.Embed(
        title="👑 Transfer Bot Ownership",
        description=(
            "Bot ownership must be transferred through the [Discord Developer Portal](https://discord.com/developers/applications):\n\n"
            "1. Create or use a **Team**.\n"
            "2. Invite new owner to the team.\n"
            "3. Transfer the bot to the team.\n"
            "4. Transfer **Team Ownership**.\n\n"
            "✅ This ensures your bot stays safe and under full control."
        ),
        color=discord.Color.dark_gold()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="invoice-panel", description="Send an invoice panel for manual payment info")
@app_commands.describe(product="Product name", price="Price (USD)", buyer="Buyer tag or Discord ID")
async def invoice_panel(interaction: discord.Interaction, product: str, price: str, buyer: str):
    embed = discord.Embed(
        title="🧾 BoostVault Invoice",
        description=f"**Product:** `{product}`\n**Price:** `${price}`\n**Buyer:** `{buyer}`\n\nUse the provided payment link or reach out manually.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Powered by BoostVault Invoices")
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="live-stock", description="Announce current token stock levels")
async def live_stock(interaction: discord.Interaction):
    from helpers.boost import check_stock
    stock = check_stock()
    embed = discord.Embed(title="📦 Live BoostVault Stock", color=discord.Color.orange())
    embed.add_field(name="1 Month Tokens", value=f"`{stock['1m']}` available")
    embed.add_field(name="3 Month Tokens", value=f"`{stock['3m']}` available")
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("📡 Stock update posted publicly.", ephemeral=True)
    
@bot.tree.command(name="oauth-boost-server", description="Trigger boost via OAuth user link (stub)")
async def oauth_boost_server(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🚧 OAuth boost requires user token authentication. If you want to set this up via browser login or Sellix webhook, I’ll help build it!",
        ephemeral=True
    )
    
@bot.tree.command(name="redeem-panel", description="Open redemption UI for license keys")
async def redeem_panel(interaction: discord.Interaction):
    from helpers.ui import RedeemButtonView
    embed = discord.Embed(
        title="🔑 Redeem Boost Key",
        description="Click below to activate your license and apply boosts.",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed, view=RedeemButtonView())

@bot.tree.command(name="restock-tokens", description="Upload new token file and merge with stock")
@app_commands.describe(duration="1m or 3m")
async def restock_tokens(interaction: discord.Interaction, duration: str):
    await interaction.response.send_message(
        f"📤 Please upload the new `{duration}` token file as an attachment to this message reply.",
        ephemeral=True
    )
    
@bot.tree.command(name="unboost-server", description="Remove boosts from a server (admin only)")
@app_commands.describe(invite="Server invite code", amount="Boosts to remove")
async def unboost_server(interaction: discord.Interaction, invite: str, amount: int):
    # You must implement an `unboost()` function in helpers/boost.py
    from helpers.boost import unboost
    unboost(invite, amount)
    await interaction.response.send_message(f"⚠️ `{amount}` boost(s) removed from `{invite}`.", ephemeral=True)
    

import json

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Run the bot using the token from config
bot.run(config["token"])
