import os
import sys
from webdriver_manager.chrome import ChromeDriverManager as ChromeDriverManager_
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# ------------------- Headless Chrome Setup -------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless")                 # Run without GUI
options.add_argument("--no-sandbox")               # Needed for hosting providers
options.add_argument("--disable-dev-shm-usage")    # Solve limited /dev/shm space
options.add_argument("--disable-gpu")              # Optional
options.add_argument("--window-size=1920,1080")    # Virtual window size

# Optional: specify Chrome binary if your host has it installed
# options.binary_location = "/usr/bin/google-chrome"

# Initialize WebDriver using ChromeDriverManager
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager_().install()),
    options=options
)



# ---- Original script contents appended ----


import discord
from discord.ext import commands
import json
import os
import asyncio
import re
import random
import string
from datetime import datetime
import time
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as ChromeDriverManager_
# Corrected import for ChromeDriverManager
from PIL import Image
import base64
import platform
import psutil
import pkg_resources

def setup_config():
    """Create config.json with all necessary settings"""
    config = {
        "bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE",
        "new_password": "NewSecurePassword123!",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "max_recovery_attempts": 3,
        "wait_time_seconds": 30,
        "admin_users": [],
        "microsoft_recovery_url": "https://account.live.com/password/recover",
        "temp_mail_url": "https://temp-mail.org/en/",
        "email_check_interval": 30,
        "max_wait_minutes": 10,
        "debug_mode": True,
        "chrome_headless": False,
        "screenshot_quality": 85,
        "page_load_timeout": 30,
        "element_wait_timeout": 20,
        "super_admin_id": 1383641747913183256,
        "authorized_users": [],
        "database_file": "auth_database.json"
    }

    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("Created config.json - Please configure your bot token and settings")

    return config

def load_config():
    """Load configuration from config.json"""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    else:
        return setup_config()

def load_auth_database():
    """Load authorization database"""
    db_file = config.get('database_file', 'auth_database.json')
    if os.path.exists(db_file):
        with open(db_file, 'r') as f:
            return json.load(f)
    else:
        # Initialize with super admin
        db = {
            "authorized_users": [config.get('super_admin_id', 1383641747913183256)],
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
        save_auth_database(db)
        return db

def save_auth_database(db):
    """Save authorization database"""
    db_file = config.get('database_file', 'auth_database.json')
    db['last_updated'] = datetime.utcnow().isoformat()
    with open(db_file, 'w') as f:
        json.dump(db, f, indent=2)

def is_authorized(user_id):
    """Check if user is authorized"""
    db = load_auth_database()
    return user_id in db.get('authorized_users', [])

def is_super_admin(user_id):
    """Check if user is super admin"""
    return user_id == config.get('super_admin_id', 1383641747913183256)

config = load_config()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

class ChromeManager: # Renamed from ChromeDriverManager to avoid confusion
    """Manages Chrome WebDriver instance"""

    def __init__(self):
        self.driver = None
        self.setup_chrome_options()

    def setup_chrome_options(self):
        """Setup Chrome options for automation"""
        self.chrome_options = Options()

        if config.get('chrome_headless', False):
            self.chrome_options.add_argument('--headless')

        # Security and automation options
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent
        self.chrome_options.add_argument(f'--user-agent={config["user_agent"]}')

        # Window size
        self.chrome_options.add_argument('--window-size=1920,1080')

        # Disable notifications and popups
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

    def start_driver(self):
        """Start Chrome WebDriver"""
        try:
            # Use the imported ChromeDriverManager_
            service = Service(ChromeDriverManager_().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)

            # Set timeouts
            self.driver.set_page_load_timeout(config.get('page_load_timeout', 30))
            self.driver.implicitly_wait(5)

            # Execute script to hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return True
        except Exception as e:
            print(f"Failed to start Chrome driver: {e}")
            return False

    def take_screenshot(self, filename=None):
        """Take screenshot and return as bytes"""
        try:
            if not self.driver:
                return None

            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()

            # Optimize image size
            image = Image.open(io.BytesIO(screenshot))

            # Resize if too large
            max_width, max_height = 1920, 1080
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save as bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True, quality=config.get('screenshot_quality', 85))
            img_bytes.seek(0)

            return img_bytes.getvalue()

        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    def quit_driver(self):
        """Quit Chrome WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

class TempMailHandler:
    """Handles temporary email creation and management"""

    def __init__(self, chrome_manager):
        self.chrome_manager = chrome_manager
        self.driver = None
        self.temp_email = None

    def setup_driver(self):
        """Setup WebDriver"""
        self.driver = self.chrome_manager.driver

    async def create_temp_email(self, ctx):
        """Create temporary email using temp-mail.org"""
        try:
            temp_mail_url = config.get('temp_mail_url', 'https://temp-mail.org/en/')
            self.driver.get(temp_mail_url)

            await asyncio.sleep(3)

            # Get the generated email
            email_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "mail"))
            )

            self.temp_email = email_element.get_attribute('value')

            await ctx.send(f"📧 Created temporary email: `{self.temp_email}`")

            return self.temp_email

        except Exception as e:
            await ctx.send(f"❌ Failed to create temporary email: {str(e)}")
            return None

class MicrosoftPasswordRecovery:
    """Handles Microsoft account password recovery with Chrome automation"""

    def __init__(self, chrome_manager):
        self.chrome_manager = chrome_manager
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Setup WebDriver and wait object"""
        self.driver = self.chrome_manager.driver
        self.wait = WebDriverWait(self.driver, config.get('element_wait_timeout', 20))

    async def send_screenshot(self, ctx, title, description=""):
        """Send screenshot to Discord"""
        try:
            screenshot_bytes = self.chrome_manager.take_screenshot()
            if screenshot_bytes:
                file = discord.File(
                    io.BytesIO(screenshot_bytes),
                    filename=f"screenshot_{int(time.time())}.png"
                )

                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=0x0099ff,
                    timestamp=datetime.utcnow()
                )

                embed.set_image(url=f"attachment://screenshot_{int(time.time())}.png")

                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(f"📷 **{title}** - Screenshot failed to capture")
        except Exception as e:
            await ctx.send(f"❌ Screenshot error: {str(e)}")

    async def navigate_to_recovery_page(self, ctx):
        """Navigate to Microsoft recovery page"""
        try:
            recovery_url = config['microsoft_recovery_url']
            self.driver.get(recovery_url)

            await asyncio.sleep(3)
            await self.send_screenshot(ctx, "🌐 Microsoft Recovery Page", "Navigated to password recovery page")

            return True

        except Exception as e:
            await ctx.send(f"❌ Failed to navigate to recovery page: {str(e)}")
            return False

    async def complete_recovery_process(self, ctx, email, old_password, new_password):
        """Complete the full recovery process"""
        try:
            # Navigate to recovery page
            if not await self.navigate_to_recovery_page(ctx):
                return False

            # Fill email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            email_input.clear()
            email_input.send_keys(email)

            await self.send_screenshot(ctx, "📧 Email Entered", f"Entered email: {email}")

            # Continue with recovery process...
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
            )
            next_button.click()

            await asyncio.sleep(3)
            await self.send_screenshot(ctx, "✅ Recovery Initiated", "Recovery process started")

            return True

        except Exception as e:
            await ctx.send(f"❌ Recovery process failed: {str(e)}")
            return False

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Password Recovery Bot with authorization system is ready!')

@bot.command(name='auth')
async def auth_user(ctx, user_mention: str = None):
    """Authorize a user to use the bot"""
    if not is_super_admin(ctx.author.id):
        await ctx.send("❌ Only the super admin can authorize users.")
        return

    if not user_mention:
        await ctx.send("❌ Please mention a user to authorize. Example: `$auth @username`")
        return

    try:
        # Extract user ID from mention
        user_id = int(re.findall(r'\d+', user_mention)[0])

        db = load_auth_database()

        if user_id not in db['authorized_users']:
            db['authorized_users'].append(user_id)
            save_auth_database(db)

            user = bot.get_user(user_id)
            username = user.name if user else f"User ID: {user_id}"

            embed = discord.Embed(
                title="✅ User Authorized",
                description=f"User {username} has been authorized to use the bot.",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ User is already authorized.")

    except (ValueError, IndexError):
        await ctx.send("❌ Invalid user mention. Please use @username format.")
    except Exception as e:
        await ctx.send(f"❌ Error authorizing user: {str(e)}")

@bot.command(name='unauth')
async def unauth_user(ctx, user_mention: str = None):
    """Unauthorize a user (only super admin can do this)"""
    if not is_super_admin(ctx.author.id):
        await ctx.send("❌ Only the super admin can unauthorize users.")
        return

    if not user_mention:
        await ctx.send("❌ Please mention a user to unauthorize. Example: `$unauth @username`")
        return

    try:
        user_id = int(re.findall(r'\d+', user_mention)[0])

        # Cannot unauth super admin
        if user_id == config.get('super_admin_id'):
            await ctx.send("❌ Cannot unauthorize the super admin.")
            return

        db = load_auth_database()

        if user_id in db['authorized_users']:
            db['authorized_users'].remove(user_id)
            save_auth_database(db)

            user = bot.get_user(user_id)
            username = user.name if user else f"User ID: {user_id}"

            embed = discord.Embed(
                title="❌ User Unauthorized",
                description=f"User {username} has been removed from authorization.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ User is not authorized.")

    except (ValueError, IndexError):
        await ctx.send("❌ Invalid user mention. Please use @username format.")
    except Exception as e:
        await ctx.send(f"❌ Error unauthorizing user: {str(e)}")

@bot.command(name='list')
async def list_authorized(ctx):
    """List all authorized users"""
    if not is_authorized(ctx.author.id):
        await ctx.send("❌ You are not authorized to use this bot.")
        return

    try:
        db = load_auth_database()
        authorized_users = db.get('authorized_users', [])

        embed = discord.Embed(
            title="👥 Authorized Users",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )

        if authorized_users:
            user_list = []
            for user_id in authorized_users:
                user = bot.get_user(user_id)
                if user:
                    status = "🔹 Super Admin" if user_id == config.get('super_admin_id') else "🔸 Authorized"
                    user_list.append(f"{status} {user.name} (`{user_id}`)")
                else:
                    status = "🔹 Super Admin" if user_id == config.get('super_admin_id') else "🔸 Authorized"
                    user_list.append(f"{status} Unknown User (`{user_id}`)")

            embed.description = "\n".join(user_list)
        else:
            embed.description = "No authorized users found."

        embed.add_field(
            name="📊 Statistics",
            value=f"Total Authorized: {len(authorized_users)}",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error listing users: {str(e)}")

@bot.command(name='status')
async def bot_status(ctx):
    """Show bot status information"""
    try:
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )

        # Bot info
        embed.add_field(
            name="🏷️ Bot Information",
            value=f"**Name:** {bot.user.name}\n**ID:** {bot.user.id}\n**Guilds:** {len(bot.guilds)}\n**Users:** {len(bot.users)}",
            inline=True
        )

        # System info
        embed.add_field(
            name="💻 System Information",
            value=f"**Platform:** {platform.system()}\n**Python:** {platform.python_version()}\n**Discord.py:** {discord.__version__}",
            inline=True
        )

        # Authorization info
        db = load_auth_database()
        embed.add_field(
            name="🔐 Authorization",
            value=f"**Authorized Users:** {len(db.get('authorized_users', []))}\n**Super Admin:** <@{config.get('super_admin_id')}>",
            inline=True
        )

        # Configuration
        embed.add_field(
            name="⚙️ Configuration",
            value=f"**Debug Mode:** {config.get('debug_mode', False)}\n**Headless Chrome:** {config.get('chrome_headless', False)}\n**Max Attempts:** {config.get('max_recovery_attempts', 3)}",
            inline=False
        )

        embed.set_footer(text="Password Recovery Bot")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error getting status: {str(e)}")

@bot.command(name='stats')
async def bot_stats(ctx):
    """Show system stats and package information"""
    try:
        embed = discord.Embed(
            title="📊 System Statistics",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )

        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        embed.add_field(
            name="🖥️ System Resources",
            value=f"**CPU Usage:** {cpu_percent}%\n**Memory Usage:** {memory.percent}%\n**Available Memory:** {memory.available // (1024**3)} GB",
            inline=True
        )

        # Package versions
        key_packages = ['discord.py', 'selenium', 'pillow', 'webdriver-manager']
        package_info = []

        for package in key_packages:
            try:
                version = pkg_resources.get_distribution(package).version
                package_info.append(f"✅ {package}: {version}")
            except pkg_resources.DistributionNotFound:
                package_info.append(f"❌ {package}: Not installed")

        embed.add_field(
            name="📦 Key Packages",
            value="\n".join(package_info),
            inline=True
        )

        # Check Chrome driver
        try:
            # Use the corrected ChromeDriverManager_
            chrome_manager_instance = ChromeDriverManager_()
            # Attempt to install or get the driver path to check availability
            driver_path = chrome_manager_instance.install()
            chrome_status = "✅ Available" if driver_path else "❌ Error during installation check"
        except Exception as e:
            chrome_status = f"❌ Not available ({e})"

        embed.add_field(
            name="🌐 WebDriver Status",
            value=f"**Chrome Driver:** {chrome_status}",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error getting stats: {str(e)}")

@bot.command(name='ping')
async def ping(ctx):
    """Show bot latency"""
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=0x00ff00 if latency < 100 else 0xffa500 if latency < 200 else 0xff0000,
        timestamp=datetime.utcnow()
    )

    await ctx.send(embed=embed)

@bot.command(name='passchange')
async def password_change(ctx, account_info: str = None, new_password: str = None):
    """
    Initiate Microsoft account password recovery
    Usage: $passchange email:oldpassword newpassword
    """
    if not is_authorized(ctx.author.id):
        await ctx.send("❌ You are not authorized to use this bot. Contact an admin for access.")
        return

    if not account_info or ':' not in account_info or not new_password:
        embed = discord.Embed(
            title="❌ Invalid Format",
            description="Please provide the correct format:\n\n`$passchange email:oldpassword newpassword`\n\nExample: `$passchange john@outlook.com:myoldpass MyNewPassword123!`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    # Parse email and old password
    try:
        email, old_password = account_info.split(':', 1)
        email = email.strip()
        old_password = old_password.strip()
        new_password = new_password.strip()
    except ValueError:
        await ctx.send("❌ Invalid format. Use: `$passchange email:oldpassword newpassword`")
        return

    if not email or '@' not in email:
        await ctx.send("❌ Please provide a valid email address.")
        return

    # Create initial embed
    embed = discord.Embed(
        title="🔄 Microsoft Account Recovery Started",
        description=f"Starting automated recovery for: `{email}`\nNew password will be set to: `{new_password}`",
        color=0x0099ff,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="🤖 Method",
        value="Chrome WebDriver + temp-mail.org",
        inline=False
    )

    await ctx.send(embed=embed)

    # Initialize automation
    chrome_manager = ChromeManager() # Use the renamed class
    temp_mail_handler = TempMailHandler(chrome_manager)
    recovery_handler = MicrosoftPasswordRecovery(chrome_manager)

    try:
        # Start Chrome Driver
        await ctx.send("🚀 **Step 1:** Starting Chrome WebDriver...")

        if not chrome_manager.start_driver():
            await ctx.send("❌ Failed to start Chrome WebDriver.")
            return

        temp_mail_handler.setup_driver()
        recovery_handler.setup_driver()

        # Create temporary email
        await ctx.send("📧 **Step 2:** Creating temporary email...")
        temp_email = await temp_mail_handler.create_temp_email(ctx)

        if not temp_email:
            return

        # Start recovery process
        await ctx.send("🔐 **Step 3:** Starting password recovery...")

        success = await recovery_handler.complete_recovery_process(ctx, email, old_password, new_password)

        # Final status
        final_embed = discord.Embed(
            title="🏁 Recovery Process Complete",
            timestamp=datetime.utcnow()
        )

        if success:
            final_embed.color = 0x00ff00
            final_embed.description = f"✅ Recovery initiated for `{email}`!\n\nTemporary email: `{temp_email}`\nNew password: `{new_password}`"
        else:
            final_embed.color = 0xff0000
            final_embed.description = f"❌ Recovery failed for `{email}`."

        await ctx.send(embed=final_embed)

    except Exception as e:
        await ctx.send(f"❌ Unexpected error: {str(e)}")

    finally:
        await ctx.send("ℹ️ Chrome browser left open for manual review.")

@bot.command(name='info') # Renamed command from 'help' to 'info'
async def info_command(ctx): # Renamed function to match command
    """Display info information"""
    embed = discord.Embed(
        title="🔧 Password Recovery Bot Info", # Updated embed title
        description="Automated Microsoft account password recovery with authorization system",
        color=0x0099ff
    )

    embed.add_field(
        name="🔐 Authentication Commands",
        value="`$auth @user` - Authorize user (Super Admin only)\n`$unauth @user` - Remove authorization (Super Admin only)\n`$list` - List authorized users",
        inline=False
    )

    embed.add_field(
        name="📋 Main Commands",
        value="`$passchange email:oldpass newpass` - Start password recovery\n`$status` - Show bot status\n`$stats` - Show system statistics\n`$ping` - Show bot latency",
        inline=False
    )

    embed.add_field(
        name="🤖 Features",
        value="• Chrome WebDriver automation\n• temp-mail.org integration\n• User authorization system\n• Screenshot monitoring\n• Real-time progress updates",
        inline=False
    )

    embed.add_field(
        name="⚠️ Authorization",
        value="Only authorized users can use password recovery commands. Contact the super admin for access.",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Use `$info` for usage information.") # Updated help command reference
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `$info` to see available commands.") # Updated help command reference
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

if __name__ == "__main__":
    # Setup configuration
    setup_config()

    # Load bot token
    bot_token = config.get('bot_token')

    if bot_token == "YOUR_DISCORD_BOT_TOKEN_HERE" or not bot_token:
        print("❌ Please set your Discord bot token in config.json")
        print("1. Open config.json")
        print("2. Replace 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual bot token")
        print("3. Run the bot again")
    else:
        try:
            bot.run(bot_token)
        except discord.errors.LoginFailure:
            print("❌ Invalid bot token. Please check your config.json")
        except Exception as e:
            print(f"❌ Bot error: {e}")