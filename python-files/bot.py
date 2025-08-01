import discord
import a2s
import datetime
import asyncio
import os
import json
import logging
import sqlite3
import requests
import re
from discord.ext import commands
from dotenv import load_dotenv
from collections import defaultdict
from tabulate import tabulate

# Try to import arma3query, fallback if not available
try:
    import arma3query
    ARMA3_QUERY_AVAILABLE = True
except ImportError:
    ARMA3_QUERY_AVAILABLE = False
    logging.warning("arma3query not available. Install with: pip install arma3query")

# Set up logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot_runtime.log'), logging.StreamHandler()]
)

# Load configuration from .env file with defaults
load_dotenv()
CONFIG = {
    'REFRESH_INTERVAL': int(os.getenv('REFRESH_INTERVAL', 10)),
    'API_KEY': os.getenv('API_KEY'),
    'CHANNEL_ID': int(os.getenv('CHANNEL_ID')),
    'SERVERS': json.loads(os.getenv('SERVERS', '[]')),
    'QUERY_TIMEOUT': int(os.getenv('QUERY_TIMEOUT', 5)),
    'DATABASE_FILE': os.getenv('DATABASE_FILE', 'bot_data.db'),
    'MAX_RETRIES': int(os.getenv('MAX_RETRIES', 3)),
    'CUSTOM_TITLE': os.getenv('CUSTOM_TITLE', 'Server Status'),
    'CUSTOM_TEXT': os.getenv('CUSTOM_TEXT', '**DM an admin to join our servers!**'),
    'LEADERBOARD_TITLE': os.getenv('LEADERBOARD_TITLE', 'Player Leaderboard'),
    'LEADERBOARD_SIZE': int(os.getenv('LEADERBOARD_SIZE', 10)),
    'STATUS_COLOR': int(os.getenv('STATUS_COLOR', '0x1A529A'), 16),
    'LEADERBOARD_COLOR': int(os.getenv('LEADERBOARD_COLOR', '0xFFD700'), 16),
    'FOOTER_ICON': os.getenv('FOOTER_ICON', 'https://example.com/icon.jpg'),
    'KILL_UPDATE_INTERVAL': int(os.getenv('KILL_UPDATE_INTERVAL', 300)),
    'MISSION_SYNC_DELAY': int(os.getenv('MISSION_SYNC_DELAY', 300)),  # Max time to wait for mission sync (5 mins)
    'MONTHLY_RESET_DAY': int(os.getenv('MONTHLY_RESET_DAY', 3))  # Day of month for leaderboard reset
}

# Configure Discord bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def init_db():
    """Set up SQLite database with tables for messages and leaderboards."""
    conn = sqlite3.connect(CONFIG['DATABASE_FILE'])
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        message_id TEXT,
        channel_id TEXT,
        type TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        player_name TEXT PRIMARY KEY,
        kills INTEGER,
        time_played INTEGER,
        last_seen TEXT,
        last_kill_update TEXT,
        current_session_kills INTEGER,
        last_session_time INTEGER
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS monthly_leaderboard (
        player_name TEXT PRIMARY KEY,
        kills INTEGER,
        time_played INTEGER,
        month TEXT
    )''')
    
    # Check if we need to migrate from minutes to seconds
    cursor.execute("PRAGMA table_info(leaderboard)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add migration flag column if it doesn't exist
    if 'migrated_to_seconds' not in columns:
        cursor.execute("ALTER TABLE leaderboard ADD COLUMN migrated_to_seconds INTEGER DEFAULT 0")
        
        # Migrate existing data from minutes to seconds
        cursor.execute("SELECT player_name, time_played, migrated_to_seconds FROM leaderboard")
        players_to_migrate = cursor.fetchall()
        
        for player_name, time_played, migrated in players_to_migrate:
            if migrated == 0 and time_played > 0:
                # Convert from minutes to seconds (multiply by 60)
                new_time_seconds = time_played * 60
                cursor.execute("UPDATE leaderboard SET time_played = ?, migrated_to_seconds = 1 WHERE player_name = ?", 
                             (new_time_seconds, player_name))
                logging.info(f"Migrated {player_name}: {time_played} mins -> {new_time_seconds} seconds")
        
        # Also migrate monthly leaderboard
        cursor.execute("ALTER TABLE monthly_leaderboard ADD COLUMN migrated_to_seconds INTEGER DEFAULT 0")
        cursor.execute("SELECT player_name, time_played, migrated_to_seconds FROM monthly_leaderboard")
        monthly_to_migrate = cursor.fetchall()
        
        for player_name, time_played, migrated in monthly_to_migrate:
            if migrated == 0 and time_played > 0:
                # Convert from minutes to seconds (multiply by 60)
                new_time_seconds = time_played * 60
                cursor.execute("UPDATE monthly_leaderboard SET time_played = ?, migrated_to_seconds = 1 WHERE player_name = ?", 
                             (new_time_seconds, player_name))
                logging.info(f"Migrated monthly {player_name}: {time_played} mins -> {new_time_seconds} seconds")
        
        logging.info("Completed migration from minutes to seconds storage")
    
    conn.commit()
    conn.close()

init_db()

class DataManager:
    @staticmethod
    def save_message(message_id, channel_id, message_type):
        with sqlite3.connect(CONFIG['DATABASE_FILE']) as conn:
            conn.execute('INSERT OR REPLACE INTO messages (message_id, channel_id, type) VALUES (?, ?, ?)',
                        (message_id, channel_id, message_type))
    
    @staticmethod
    def get_message(message_type):
        with sqlite3.connect(CONFIG['DATABASE_FILE']) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT message_id, channel_id FROM messages WHERE type = ?', (message_type,))
            return cursor.fetchone()
    
    @staticmethod
    def save_leaderboard(player_stats, monthly_stats):
        with sqlite3.connect(CONFIG['DATABASE_FILE']) as conn:
            conn.executemany('''INSERT OR REPLACE INTO leaderboard 
                (player_name, kills, time_played, last_seen, last_kill_update, current_session_kills, last_session_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                [(name, stats.kills, stats.time_played, stats.last_seen.isoformat(),
                  stats.last_kill_update.isoformat() if stats.last_kill_update else None,
                  stats.current_session_kills, stats.last_session_time) 
                 for name, stats in player_stats.items()])
            
            # Use current month period starting from MONTHLY_RESET_DAY
            now = datetime.datetime.now()
            if now.day >= CONFIG['MONTHLY_RESET_DAY']:
                current_period = f"{now.year}-{now.month:02d}"
            else:
                # If before reset day, use previous month
                prev_month = now.replace(day=1) - datetime.timedelta(days=1)
                current_period = f"{prev_month.year}-{prev_month.month:02d}"
                
            conn.executemany('''INSERT OR REPLACE INTO monthly_leaderboard 
                (player_name, kills, time_played, month)
                VALUES (?, ?, ?, ?)''',
                [(name, stats.kills, stats.time_played, current_period) 
                 for name, stats in monthly_stats.items()])
    
    @staticmethod
    def load_leaderboard():
        with sqlite3.connect(CONFIG['DATABASE_FILE']) as conn:
            cursor = conn.cursor()
            # Check if last_session_time column exists, if not add it
            cursor.execute("PRAGMA table_info(leaderboard)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'last_session_time' not in columns:
                cursor.execute("ALTER TABLE leaderboard ADD COLUMN last_session_time INTEGER DEFAULT 0")
                conn.commit()
            
            # Only load players seen since the MONTHLY_RESET_DAY of current month
            now = datetime.datetime.now()
            current_month_reset_day = datetime.datetime(now.year, now.month, CONFIG['MONTHLY_RESET_DAY'])
            
            cursor.execute('''SELECT player_name, kills, time_played, last_seen, 
                            last_kill_update, current_session_kills, last_session_time FROM leaderboard
                            WHERE last_seen >= ?''', (current_month_reset_day.isoformat(),))
            player_stats = {
                row[0]: PlayerStats(row[1], row[2], 
                                  datetime.datetime.fromisoformat(row[3]),
                                  datetime.datetime.fromisoformat(row[4]) if row[4] else None,
                                  row[5], row[6] if len(row) > 6 else 0)
                for row in cursor.fetchall()
            }
            
            # Use current month period starting from MONTHLY_RESET_DAY
            if now.day >= CONFIG['MONTHLY_RESET_DAY']:
                current_period = f"{now.year}-{now.month:02d}"
            else:
                # If before reset day, use previous month
                prev_month = now.replace(day=1) - datetime.timedelta(days=1)
                current_period = f"{prev_month.year}-{prev_month.month:02d}"
                
            cursor.execute('SELECT player_name, kills, time_played FROM monthly_leaderboard WHERE month = ?', 
                         (current_period,))
            monthly_stats = {
                row[0]: PlayerStats(row[1], row[2]) 
                for row in cursor.fetchall()
            }
            return player_stats, monthly_stats

def format_time_readable(seconds):
    """Convert seconds to readable format like '43m 2s', '1hr 30mins', '2 days 1.6hrs'."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:  # Less than 1 hour
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{minutes}m"
    elif seconds < 86400:  # Less than 1 day
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}hr {remaining_minutes}mins"
        else:
            return f"{hours}hr"
    else:  # 1 day or more
        days = seconds // 86400
        remaining_hours = (seconds % 86400) / 3600
        if remaining_hours >= 1:
            return f"{days} days {remaining_hours:.1f}hrs"
        else:
            return f"{days} days"

class PlayerStats:
    def __init__(self, kills=0, time_played=0, last_seen=None, last_kill_update=None, current_session_kills=0, last_session_time=0):
        self.kills = kills
        self.time_played = time_played  # Store in seconds now
        self.last_seen = last_seen or datetime.datetime.now()
        self.last_kill_update = last_kill_update
        self.current_session_kills = current_session_kills
        self.last_session_time = last_session_time  # Track last known session time to detect resets

class PresetServerManager:
    def __init__(self):
        self.preset_servers = {}
        self.last_preset_update = datetime.datetime.min
        
    async def fetch_preset_servers(self):
        """Fetch preset server configuration from GitHub."""
        now = datetime.datetime.now()
        if (now - self.last_preset_update).total_seconds() < 3600:  # Cache for 1 hour
            return
            
        try:
            response = await asyncio.to_thread(
                requests.get,
                "https://raw.githubusercontent.com/jishnukarri/CAC-Config/master/servers.json",
                timeout=10
            )
            if response.status_code == 200:
                self.preset_servers = response.json()
                self.last_preset_update = now
                logging.info(f"Updated preset server configuration: {len(self.preset_servers)} servers")
            else:
                logging.error(f"Failed to fetch preset servers: HTTP {response.status_code}")
                
        except Exception as e:
            logging.error(f"Failed to fetch preset server config: {str(e)}")
    
    def get_preset_server_info(self, server_name):
        """Get preset server info by name."""
        return self.preset_servers.get(server_name)
    
    def get_all_preset_servers(self):
        """Get all preset servers."""
        return self.preset_servers

class ServerMonitor:
    def __init__(self):
        self.status_message = None
        self.leaderboard_message = None
        self.server_data = {}
        self.arma_server_data = {}  # Cache for Arma 3 server mod data
        self.last_arma_update = {}  # Track last mod list update per server
        self.player_stats, self.monthly_leaderboard = DataManager.load_leaderboard()
        self.last_reset = datetime.datetime.now()
        self.preset_manager = PresetServerManager()

    async def query_server(self, address):
        """Query a game server with retry logic."""
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                info = await asyncio.wait_for(a2s.ainfo(address), timeout=CONFIG['QUERY_TIMEOUT'])
                players = await asyncio.wait_for(a2s.aplayers(address), timeout=CONFIG['QUERY_TIMEOUT'])
                return info, players, round(info.ping * 1000)
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {address}: {str(e)}")
                await asyncio.sleep(1)
        return None, [], None

    async def update_all_servers(self):
        """Update all servers in parallel and handle leaderboard reset."""
        # Fetch preset server configuration
        await self.preset_manager.fetch_preset_servers()
        
        # Update servers from environment config
        tasks = [self.update_single_server(server['ip'], server['port']) for server in CONFIG['SERVERS']]
        await asyncio.gather(*tasks)
        self.check_monthly_reset()
        DataManager.save_leaderboard(self.player_stats, self.monthly_leaderboard)

    async def update_single_server(self, ip, port):
        address = (ip, port)
        try:
            info, players, ping = await self.query_server(address)
            if info:
                # Ensure players is a list
                if players is None:
                    players = []
                # Ensure ping is a number
                if ping is None:
                    ping = 0
                    
                self.server_data[address] = (info, players, ping)
                self.update_player_stats(players)
                
                # Check if this is an Arma 3 server and query mods every 20 minutes
                if self.is_arma3_server(info):
                    await self.update_arma3_server_data(address)
            else:
                # Remove offline servers from server_data to prevent stale data
                if address in self.server_data:
                    del self.server_data[address]
        except Exception as e:
            logging.error(f"Error updating server {ip}:{port}: {str(e)}")
            # Remove problematic servers from server_data
            if address in self.server_data:
                del self.server_data[address]

    def is_arma3_server(self, info):
        """Check if server is Arma 3 based on game info."""
        return (hasattr(info, 'game') and 'arma' in info.game.lower()) or \
               (hasattr(info, 'folder') and 'arma' in info.folder.lower()) or \
               (hasattr(info, 'keywords') and info.keywords and any(
                   keyword in info.keywords.lower() for keyword in ['arma', 'altis', 'malden', 'tanoa']))

    async def update_arma3_server_data(self, address):
        """Update Arma 3 server mod data every 20 minutes."""
        now = datetime.datetime.now()
        last_update = self.last_arma_update.get(address, datetime.datetime.min)
        
        # Update every 20 minutes (1200 seconds)
        if (now - last_update).total_seconds() >= 1200:
            if ARMA3_QUERY_AVAILABLE:
                try:
                    rules = await asyncio.wait_for(
                        asyncio.to_thread(arma3query.arma3rules, address),
                        timeout=CONFIG['QUERY_TIMEOUT']
                    )
                    self.arma_server_data[address] = rules
                    self.last_arma_update[address] = now
                    logging.info(f"Updated Arma 3 mod data for {address}: {len(rules.mods)} mods, {len(rules.cdlc)} CDLCs")
                except Exception as e:
                    logging.error(f"Failed to query Arma 3 rules for {address}: {str(e)}")
            else:
                logging.warning(f"Cannot query Arma 3 mods for {address} - arma3query not available")

    def update_player_stats(self, players):
        """Update player kill counts and time played using delta tracking to prevent double-counting."""
        if not players or not hasattr(players, '__iter__'):
            return  # Skip if players is None or not iterable
            
        now = datetime.datetime.now()
        
        for player in players:
            if not player or not hasattr(player, 'name') or not player.name:
                continue
                
            try:
                current_kills = getattr(player, 'score', 0) or 0
                current_time_seconds = int(getattr(player, 'duration', 0) or 0)  # Current session time in seconds
                
                # Debug logging for time conversion
                logging.debug(f"{player.name}: Raw time={current_time_seconds}s")
                
                # Get or create player stats
                stats = self.player_stats.get(player.name, PlayerStats())
                monthly_stats = self.monthly_leaderboard.get(player.name, PlayerStats())
                
                # Detect server restart or player rejoin scenarios
                server_reset_detected = False
                player_rejoined = False
                
                # Server reset: current time is 0 but we had previous session data
                if current_time_seconds == 0 and stats.last_session_time > 0:
                    server_reset_detected = True
                    logging.info(f"Server reset detected for {player.name} (time reset to 0)")
                
                # Player rejoined: time went backwards significantly
                elif current_time_seconds < stats.last_session_time and (stats.last_session_time - current_time_seconds) > 2:
                    player_rejoined = True
                    logging.info(f"Player rejoin detected for {player.name} (time: {stats.last_session_time} -> {current_time_seconds})")
                
                # Handle resets and rejoins
                if server_reset_detected or player_rejoined:
                    # Reset tracking values but keep accumulated leaderboard stats
                    stats.current_session_kills = 0
                    stats.last_session_time = 0
                    stats.last_kill_update = None
                    logging.info(f"Reset session tracking for {player.name}")
                
                # Only update if enough time has passed since last kill update
                should_update_kills = (
                    not stats.last_kill_update or 
                    (now - stats.last_kill_update).total_seconds() >= CONFIG['KILL_UPDATE_INTERVAL']
                )
                
                if should_update_kills:
                    # Calculate deltas
                    kills_delta = 0
                    time_delta = 0
                    
                    if server_reset_detected or player_rejoined:
                        # Fresh start after reset/rejoin - don't add any deltas, just reset tracking
                        kills_delta = 0
                        time_delta = 0
                        logging.info(f"{player.name}: Reset detected - resetting tracking without adding to totals")
                    else:
                        # Normal delta calculation
                        kills_delta = max(0, current_kills - stats.current_session_kills)
                        time_delta = max(0, current_time_seconds - stats.last_session_time)
                    
                    # Only add to leaderboard if time has actually progressed
                    # This prevents adding kills when mission hasn't updated yet
                    if time_delta > 0:
                        stats.kills += kills_delta
                        stats.time_played += time_delta
                        monthly_stats.kills += kills_delta
                        monthly_stats.time_played += time_delta
                        
                        if kills_delta > 0:
                            logging.info(f"{player.name}: +{kills_delta} kills, +{format_time_readable(time_delta)} (Total: {stats.kills} kills, {format_time_readable(stats.time_played)})")
                    elif kills_delta > 0 and time_delta == 0:
                        # Kills increased but time didn't - likely mission delay or data inconsistency
                        logging.warning(f"{player.name}: Kills increased (+{kills_delta}) but time didn't (+{time_delta}) - skipping update (mission sync delay?)")
                    
                    # Update tracking values
                    stats.current_session_kills = current_kills
                    stats.last_session_time = current_time_seconds
                    stats.last_kill_update = now
                
                # Always update last seen
                stats.last_seen = now
                
                # Save back to collections
                self.player_stats[player.name] = stats
                self.monthly_leaderboard[player.name] = monthly_stats
                
            except Exception as e:
                logging.error(f"Error updating stats for player {getattr(player, 'name', 'Unknown')}: {str(e)}")
                continue

    def parse_location_from_gametags(self, keywords):
        """Parse location from Arma 3 game tags (c parameter for lat/long)."""
        if not keywords:
            return "Unknown"
        
        try:
            # Look for location data (c parameter: c<long>-<lat>)
            location_match = re.search(r'c(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)', keywords)
            if location_match:
                longitude = float(location_match.group(1))
                latitude = float(location_match.group(2))
                
                # Use a simple geocoding approach to determine country/region
                # This is a basic implementation - you could enhance with a proper geocoding service
                location_name = self.get_location_from_coordinates(latitude, longitude)
                return location_name
            
            # Fallback: look for country code (o parameter)
            country_match = re.search(r'o([A-Z]{2})', keywords)
            if country_match:
                country_code = country_match.group(1)
                country_names = {
                    'US': 'United States', 'GB': 'United Kingdom', 'DE': 'Germany',
                    'FR': 'France', 'NL': 'Netherlands', 'CA': 'Canada',
                    'AU': 'Australia', 'SE': 'Sweden', 'NO': 'Norway',
                    'DK': 'Denmark', 'FI': 'Finland', 'PL': 'Poland',
                    'CZ': 'Czech Republic', 'RU': 'Russia', 'JP': 'Japan'
                }
                return country_names.get(country_code, country_code)
            
        except Exception as e:
            logging.warning(f"Error parsing location from tags '{keywords}': {str(e)}")
        
        return "Unknown"
    
    def get_location_from_coordinates(self, latitude, longitude):
        """Get location name from latitude and longitude coordinates."""
        try:
            # Basic geographic regions based on lat/long
            # This is a simplified approach - for production you'd use a proper geocoding API
            
            # Europe
            if 35 <= latitude <= 70 and -10 <= longitude <= 40:
                if 49 <= latitude <= 62 and -8 <= longitude <= 2:
                    return "United Kingdom"
                elif 47 <= latitude <= 55 and 5 <= longitude <= 15:
                    return "Germany"
                elif 42 <= latitude <= 51 and -5 <= longitude <= 10:
                    return "France"
                elif 50 <= latitude <= 54 and 3 <= longitude <= 7:
                    return "Netherlands"
                elif 55 <= latitude <= 69 and 10 <= longitude <= 25:
                    return "Sweden"
                elif 58 <= latitude <= 71 and 4 <= longitude <= 31:
                    return "Norway"
                else:
                    return "Europe"
            
            # North America
            elif 25 <= latitude <= 72 and -168 <= longitude <= -52:
                if 25 <= latitude <= 49 and -125 <= longitude <= -66:
                    return "United States"
                elif 42 <= latitude <= 72 and -142 <= longitude <= -52:
                    return "Canada"
                else:
                    return "North America"
            
            # Asia-Pacific
            elif -50 <= latitude <= 70 and 95 <= longitude <= 180:
                if -44 <= latitude <= -10 and 112 <= longitude <= 154:
                    return "Australia"
                elif 30 <= latitude <= 46 and 129 <= longitude <= 146:
                    return "Japan"
                else:
                    return "Asia-Pacific"
            
            # Default fallback
            return f"Lat: {latitude:.1f}, Long: {longitude:.1f}"
            
        except Exception as e:
            logging.warning(f"Error determining location from coordinates {latitude}, {longitude}: {str(e)}")
            return f"Lat: {latitude:.1f}, Long: {longitude:.1f}"

    def format_server_status(self):
        embed = discord.Embed(title="CAC Server Status", color=CONFIG['STATUS_COLOR'])
        embed.add_field(name=CONFIG['CUSTOM_TITLE'], value=CONFIG['CUSTOM_TEXT'], inline=False)
        
        # Display servers in the same order as SERVERS config
        servers_to_display = []
        
        for server_config in CONFIG['SERVERS']:
            server_ip = server_config['ip']
            server_port = server_config['port']
            address = (server_ip, server_port)  # Query port is game port + 1
            
            if address in self.server_data:
                server_data = self.server_data[address]
                if server_data and len(server_data) >= 3:
                    info, players, ping = server_data
                    servers_to_display.append((info, players, ping))
        
        # Display servers in order
        if servers_to_display:
            for idx, (info, players, ping) in enumerate(servers_to_display):
                try:
                    # Use simple numbering instead of emojis
                    server_number = f"{idx + 1}."
                    
                    # Safely handle players list
                    if players and hasattr(players, '__iter__'):
                        player_table = tabulate(
                            [[p.name, p.score] for p in players if p and hasattr(p, 'name') and p.name],
                            headers=["Player", "Kills"],
                            tablefmt="presto"
                        )
                    else:
                        player_table = "No players online"
                    
                    if not player_table.strip():
                        player_table = "No players online"
                    
                    # Safely get server info
                    server_name = getattr(info, 'server_name', 'Unknown Server') if info else 'Unknown Server'
                    player_count = getattr(info, 'player_count', 0) if info else 0
                    max_players = getattr(info, 'max_players', 0) if info else 0
                    map_name = getattr(info, 'map_name', 'Unknown') if info else 'Unknown'
                    game_name = getattr(info, 'game', 'Unknown Game') if info else 'Unknown Game'
                    
                    # Get server state and location from keywords
                    server_state_parts = []
                    keywords = getattr(info, 'keywords', '') if info else ''
                    
                    # Parse server state from keywords (s parameter)
                    if keywords:
                        # Look for server state (s parameter)
                        state_match = re.search(r's(\d+)', keywords)
                        if state_match:
                            state_code = state_match.group(1)
                            state_names = {
                                '0': 'NONE',
                                '1': 'SELECTING MISSION',
                                '2': 'EDITING MISSION', 
                                '3': 'ASSIGNING ROLES',
                                '4': 'SENDING MISSION',
                                '5': 'LOADING GAME',
                                '6': 'BRIEFING',
                                '7': 'PLAYING',
                                '8': 'DEBRIEFING',
                                '9': 'MISSION ABORTED'
                            }
                            server_state = state_names.get(state_code, f'STATE {state_code}')
                        else:
                            server_state = 'UNKNOWN'
                    else:
                        server_state = 'UNKNOWN'
                    
                    # Parse location from game tags
                    location = self.parse_location_from_gametags(keywords)
                    
                    embed.add_field(
                        name=f"{server_number} {server_name} ({player_count}/{max_players})",
                        value=f"**Map:** {map_name}\n**Status:** {server_state}\n```\n{player_table}\n```",
                        inline=False
                    )
                except Exception as e:
                    logging.error(f"Error formatting server {info}: {str(e)}")
                    continue
        else:
            # Show message when no servers are online
            embed.add_field(
                name="No Servers Online",
                value="All servers are currently offline or unreachable.",
                inline=False
            )
        
        # Add mod command notice
        embed.add_field(
            name="Need Mods?", 
            value="Use `/server` to get download links for server mods!\nUse `/cdlc` to get Arma 3 Creator DLC downloads!", 
            inline=False
        )
        
        embed.set_footer(text='\u200b', icon_url=CONFIG['FOOTER_ICON'])
        embed.timestamp = datetime.datetime.now()
        return embed

    def format_leaderboard(self):
        leaderboard = sorted(
            self.player_stats.items(),
            key=lambda x: (x[1].kills, x[1].time_played),
            reverse=True
        )[:CONFIG['LEADERBOARD_SIZE']]

        embed = discord.Embed(title=CONFIG['LEADERBOARD_TITLE'], color=CONFIG['LEADERBOARD_COLOR'])
        for rank, (name, stats) in enumerate(leaderboard, 1):
            embed.add_field(
                name=f"{rank}. {name}",
                value=f"**Kills:** {stats.kills} | **Time Played:** {format_time_readable(stats.time_played)}",
                inline=False
            )
        embed.set_footer(text='\u200b', icon_url=CONFIG['FOOTER_ICON'])
        embed.timestamp = datetime.datetime.now()
        return embed

    def get_rank_emoji(self, rank):
        # Simplified without emojis
        return str(rank)

    def check_monthly_reset(self):
        """Reset monthly leaderboard data that's older than the MONTHLY_RESET_DAY of current month."""
        now = datetime.datetime.now()
        current_month_reset_day = datetime.datetime(now.year, now.month, CONFIG['MONTHLY_RESET_DAY'])
        
        # Remove any data that's older than the MONTHLY_RESET_DAY of current month
        players_to_remove = []
        for player_name, stats in self.monthly_leaderboard.items():
            if stats.last_seen < current_month_reset_day:
                players_to_remove.append(player_name)
        
        for player_name in players_to_remove:
            del self.monthly_leaderboard[player_name]
            
        if players_to_remove:
            logging.info(f"Removed {len(players_to_remove)} players with data older than {current_month_reset_day.strftime('%Y-%m-%d')}")
        
        # Also clean up the main leaderboard - only keep players seen since the MONTHLY_RESET_DAY
        main_players_to_remove = []
        for player_name, stats in self.player_stats.items():
            if stats.last_seen < current_month_reset_day:
                main_players_to_remove.append(player_name)
        
        for player_name in main_players_to_remove:
            del self.player_stats[player_name]
            
        if main_players_to_remove:
            logging.info(f"Removed {len(main_players_to_remove)} players from main leaderboard with data older than {current_month_reset_day.strftime('%Y-%m-%d')}")

monitor = ServerMonitor()

class ModListGenerator:
    def __init__(self):
        self.steam_mods = {}
        self.content_links = {}
        self.last_config_update = datetime.datetime.min
        
    async def fetch_config_data(self):
        """Fetch mod IDs and download links from GitHub."""
        now = datetime.datetime.now()
        if (now - self.last_config_update).total_seconds() < 3600:  # Cache for 1 hour
            return
            
        try:
            # Fetch steam mod IDs
            steam_response = await asyncio.to_thread(
                requests.get,
                "https://raw.githubusercontent.com/jishnukarri/CAC-Config/master/steam.json",
                timeout=10
            )
            if steam_response.status_code == 200:
                self.steam_mods = steam_response.json()
                
            # Fetch download links
            content_response = await asyncio.to_thread(
                requests.get,
                "https://raw.githubusercontent.com/jishnukarri/CAC-Config/master/content.json",
                timeout=10
            )
            if content_response.status_code == 200:
                self.content_links = content_response.json()
                
            self.last_config_update = now
            logging.info("Updated mod configuration from GitHub")
            
        except Exception as e:
            logging.error(f"Failed to fetch mod config: {str(e)}")
    
    def get_mod_name_from_steam_id(self, steam_id):
        """Get mod folder name from steam workshop ID."""
        for mod_name, mod_id in self.steam_mods.get('mods', {}).items():
            if str(mod_id) == str(steam_id):
                return mod_name
        return None
    
    def normalize_mod_name(self, mod_name):
        """Normalize mod name for lookup (handle @ prefix differences)."""
        # Remove @ prefix if present
        clean_name = mod_name.replace('@', '')
        
        # Check if mod exists in content with @ prefix
        if f"@{clean_name}" in self.content_links.get('mods', {}):
            return f"@{clean_name}"
        
        # Check if mod exists without @ prefix
        if clean_name in self.content_links.get('mods', {}):
            return clean_name
            
        # Return original if not found
        return mod_name
    
    def get_download_link(self, mod_name):
        """Get download link for a mod."""
        # First try to normalize the mod name
        normalized_name = self.normalize_mod_name(mod_name)
        
        links = self.content_links.get('mods', {}).get(normalized_name)
        if isinstance(links, list):
            return links  # Multiple links
        elif isinstance(links, str):
            return [links]  # Single link
        return None
    
    async def generate_preset_server_mod_list(self, server_name, preset_info):
        """Generate a formatted mod list for a preset server."""
        await self.fetch_config_data()
        
        # Build the message
        message_parts = []
        
        # Header
        message_parts.append(f"**{server_name}**\n")
        
        # Server info
        arma_info = self.content_links.get('arma', {})
        arma_version = arma_info.get('version', 'v2.20.152984')
        
        message_parts.append(f"Server version: **{arma_version}**")
        message_parts.append(f"Required game version: **{arma_version}**\n")
        
        # Separator
        message_parts.append("-" * 164 + "\n")
        
        # Location - get from preset server config if available
        if preset_info and 'country' in preset_info:
            location = preset_info['country']
        else:
            location = "Unknown"
        
        message_parts.append(f"Location: {location}\n")
        
        message_parts.append("-" * 164 + "\n")
        
        # Warnings
        message_parts.append("**>>>STEAM MUST BE RUNNING!<<<**")
        message_parts.append("**>>>BATTLEYE DISABLED!<<<**\n")
        
        message_parts.append("-" * 164 + "\n")
        
        # Prerequisites
        message_parts.append("**Prerequisites:**")
        message_parts.append("Visual C++ Redistributable Runtimes All-in-One")
        message_parts.append("<https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/>\n")
        
        arma_link = arma_info.get('link', 'https://tinyurl.com/33taw7ds')
        
        message_parts.append(f"**Arma 3 {arma_version}**")
        message_parts.append("(Without CDLC's)")
        message_parts.append(f"Download link: <{arma_link}>")
        message_parts.append("(Yes, you need all 9!)\n")
        
        # Check for CDLCs in mod list
        preset_mods = preset_info.get('mods', [])
        cdlc_mods = [mod for mod in preset_mods if mod in ['rf', 'ws', 'spe', 'gm', 'vn', 'csla']]
        
        if cdlc_mods:
            cdlc_names = {
                'rf': 'Reaction Forces',
                'ws': 'Western Sahara',
                'spe': 'Spearhead 1944',
                'gm': 'Global Mobilization',
                'vn': 'S.O.G. Prairie Fire',
                'csla': 'CSLA Iron Curtain'
            }
            
            for cdlc in cdlc_mods:
                cdlc_name = cdlc_names.get(cdlc, cdlc.upper())
                cdlc_info = self.content_links.get('dlc', {}).get(cdlc)
                if cdlc_info:
                    message_parts.append(f"**{cdlc_name}**")
                    message_parts.append(f"Download: <{cdlc_info.get('link', 'N/A')}>")
                    if cdlc_info.get('pwd'):
                        message_parts.append(f"Password: {cdlc_info['pwd']}")
                    message_parts.append("")
        
        # Required mods - only show if there are mods beyond CDLCs
        regular_mods = [mod for mod in preset_mods if mod not in cdlc_mods]
        
        if regular_mods:
            message_parts.append("**Mods needed:**\n")
            
            for mod_name in regular_mods:
                # Get download links using normalized name lookup
                links = self.get_download_link(mod_name)
                if links:
                    # Special handling for ACE
                    if mod_name.lower() in ["@ace", "ace"]:
                        message_parts.append("**ACE Medical & Advanced Combat Environment**")
                        for link in links:
                            message_parts.append(f"Download: <{link}>")
                        message_parts.append("(ace_nouniformrestrictions mod is in @ace\\optionals\\@ace_nouniformrestrictions")
                        message_parts.append("(just move or copy it to Mods folder))\n")
                    else:
                        # Get better display names
                        display_name = self.get_mod_display_name(mod_name)
                        
                        if len(links) == 1:
                            message_parts.append(f"**{display_name}:** <{links[0]}>\n")
                        else:
                            message_parts.append(f"**{display_name}**")
                            for link in links:
                                message_parts.append(f"Download: <{link}>")
                            message_parts.append("")
                else:
                    # Mod not found in download links
                    display_name = self.get_mod_display_name(mod_name)
                    message_parts.append(f"**{display_name}** - Download link not available\n")
        
        # Optional mods
        message_parts.append("\n**Optional mods:**\n")
        optionals = self.content_links.get('optionals', {})
        for mod_name, link in optionals.items():
            display_name = self.get_mod_display_name(mod_name)
            if isinstance(link, list):
                message_parts.append(f"**{display_name}**")
                for l in link:
                    message_parts.append(f"Download: <{l}>")
                message_parts.append("")
            else:
                message_parts.append(f"**{display_name}:** <{link}>\n")
        
        return "\n".join(message_parts)
    
    def get_mod_display_name(self, mod_name):
        """Get a properly formatted display name for a mod."""
        # Just return the mod name as-is from the configuration
        return mod_name
    
    async def generate_server_mod_list(self, server_address):
        """Generate a formatted mod list for a server."""
        if server_address not in monitor.arma_server_data:
            return "No Arma 3 mod data available for this server."
            
        await self.fetch_config_data()
        
        rules = monitor.arma_server_data[server_address]
        server_info = monitor.server_data[server_address][0]
        
        # Build the message
        message_parts = []
        
        # Header
        message_parts.append(f"**{server_info.server_name}**\n")
        message_parts.append(f"Server version: {getattr(server_info, 'version', 'Unknown')}")
        message_parts.append(f"Required game version: {getattr(server_info, 'version', 'Unknown')}\n")
        
        # Separator
        message_parts.append("─" * 100 + "\n")
        
        # Location info (from game tags if available)
        location = self.parse_location_from_tags(getattr(server_info, 'keywords', ''))
        message_parts.append(f"**Location:** {location}\n")
        
        message_parts.append("─" * 100 + "\n")
        
        # Warnings
        battleye_status = self.parse_battleye_from_tags(getattr(server_info, 'keywords', ''))
        message_parts.append("**>>>STEAM MUST BE RUNNING!<<<**")
        message_parts.append(f"**>>>BATTLEYE {battleye_status}!<<<**\n")
        
        message_parts.append("─" * 100 + "\n")
        
        # Prerequisites
        message_parts.append("**Prerequisites:**\n")
        message_parts.append("Visual C++ Redistributable Runtimes All-in-One")
        message_parts.append("<https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/>\n")
        
        arma_info = self.content_links.get('arma', {})
        arma_version = arma_info.get('version', 'v2.20.152984')
        arma_link = arma_info.get('link', 'https://tinyurl.com/33taw7ds')
        
        message_parts.append(f"Arma 3 {arma_version}")
        message_parts.append("(Without CDLC's)")
        message_parts.append(f"Download link: <{arma_link}>")
        message_parts.append("(Yes, you need all 9!)\n")
        
        # CDLCs if any
        if rules.cdlc:
            message_parts.append("**CDLCs needed:**\n")
            for cdlc in rules.cdlc:
                cdlc_info = self.get_cdlc_info(cdlc)
                if cdlc_info:
                    message_parts.append(f"{cdlc_info['description']}")
                    message_parts.append(f"Download: <{cdlc_info['link']}>")
                    message_parts.append(f"Password: {cdlc_info.get('pwd', 'N/A')}\n")
        
        # Required mods
        message_parts.append("**Mods needed:**\n")
        message_parts.append("(Potential mod list, to check exact mods you need for current session use Mod Checker in CAC Launcher settings)\n")
        
        found_mods = []
        for mod in rules.mods:
            mod_name = None
            if isinstance(mod.workshop_id, int):
                mod_name = self.get_mod_name_from_steam_id(mod.workshop_id)
            
            if mod_name:
                links = self.get_download_link(mod_name)
                if links:
                    found_mods.append((mod_name, mod.name, links))
                    
                    # Special handling for ACE
                    if mod_name == "@ace":
                        message_parts.append(f"**{mod.name}**")
                        for link in links:
                            message_parts.append(f"Download: <{link}>")
                        message_parts.append("(ace_nouniformrestrictions mod is in @ace\\optionals\\@ace_nouniformrestrictions")
                        message_parts.append("(just move or copy it to Mods folder))\n")
                    else:
                        message_parts.append(f"**{mod.name}**")
                        for link in links:
                            message_parts.append(f"Download: <{link}>")
                        message_parts.append("")
        
        # Optional mods
        message_parts.append("\n**Optional mods:**\n")
        optionals = self.content_links.get('optionals', {})
        for mod_name, link in optionals.items():
            display_name = mod_name.replace('@', '').replace('_', ' ')
            if isinstance(link, list):
                message_parts.append(f"**{display_name}:**")
                for l in link:
                    message_parts.append(f"  <{l}>")
            else:
                message_parts.append(f"**{display_name}:** <{link}>")
        
        return "\n".join(message_parts)
    
    def parse_location_from_tags(self, keywords):
        """Parse location from Arma 3 game tags."""
        if not keywords:
            return "Unknown"
        
        # Look for country code in keywords (format: oXX where XX is country code)
        import re
        country_match = re.search(r'o([A-Z]{2})', keywords)
        if country_match:
            return country_match.group(1)
        
        return "Unknown"
    
    def parse_battleye_from_tags(self, keywords):
        """Parse BattlEye status from Arma 3 game tags."""
        if not keywords:
            return "UNKNOWN"
        
        # Look for BattlEye flag (bt = true, bf = false)
        if 'bt,' in keywords:
            return "ENABLED"
        elif 'bf,' in keywords:
            return "DISABLED"
        
        return "UNKNOWN"
    
    def get_cdlc_info(self, cdlc_name):
        """Get CDLC download info."""
        cdlc_map = {
            'reaction forces': 'rf',
            'western sahara': 'ws', 
            'spearhead 1944': 'spe',
            'global mobilization': 'gm',
            's.o.g. prairie fire': 'vn',
            'csla iron curtain': 'csla'
        }
        
        cdlc_key = cdlc_map.get(cdlc_name.lower())
        if cdlc_key:
            return self.content_links.get('dlc', {}).get(cdlc_key)
        return None

mod_generator = ModListGenerator()

@bot.tree.command(name="server", description="Get mod list and download links for configured servers")
@discord.app_commands.describe(server="Choose which server to get mods for")
async def server_command(interaction: discord.Interaction, server: str = None):
    """Generate mod lists for servers from GitHub configuration."""
    await interaction.response.defer(ephemeral=True)
    
    # Ensure preset servers are loaded
    await monitor.preset_manager.fetch_preset_servers()
    
    # Get all servers from GitHub servers.json
    preset_servers = monitor.preset_manager.get_all_preset_servers()
    
    if not preset_servers:
        await interaction.followup.send("No servers configured in GitHub config.", ephemeral=True)
        return
    
    # Convert to list for easier indexing
    available_servers = list(preset_servers.items())
    
    # If no server specified, show options
    if server is None:
        options_text = "**Available Servers:**\n\n"
        for i, (server_name, preset_info) in enumerate(available_servers, 1):
            address = preset_info.get('address', 'TBA')
            port = preset_info.get('port', '?')
            
            # Check if server is currently online by matching with monitored servers
            is_online = False
            if address != 'TBA':
                # Check primary address
                for monitored_address, server_data in monitor.server_data.items():
                    if not server_data or len(server_data) < 3:
                        continue
                    server_ip, server_port = monitored_address
                    
                    # Match IP and check if port matches (query port = preset port + 1)
                    if server_ip == address and server_port == port + 1:
                        is_online = True
                        break
                
                # Special case: also check 192.168.0.22 for theghost.ddns.net
                if not is_online and address == "theghost.ddns.net":
                    for monitored_address, server_data in monitor.server_data.items():
                        if not server_data or len(server_data) < 3:
                            continue
                        server_ip, server_port = monitored_address
                        
                        # Check fallback IP with same port logic
                        if server_ip == "192.168.0.22" and server_port == port + 1:
                            is_online = True
                            break
            
            status = "🟢 ONLINE" if is_online else "🔴 OFFLINE"
            password_text = " [Password Protected]" if preset_info.get('password') else ""
            mod_count = len(preset_info.get('mods', []))
            
            options_text += f"**{i}.** {server_name}{password_text}\n"
            options_text += f"   Status: {status}\n"
            options_text += f"   Mods: {mod_count} required\n\n"
        
        options_text += "Please use `/server <number>` to get mod list for a specific server.\n"
        options_text += "Example: `/server 1` for the first server."
        
        await interaction.followup.send(options_text, ephemeral=True)
        return
    
    # Parse server selection
    try:
        server_index = int(server) - 1
        if server_index < 0 or server_index >= len(available_servers):
            await interaction.followup.send(f"Invalid server number. Please use 1-{len(available_servers)}.", ephemeral=True)
            return
        
        selected_name, preset_info = available_servers[server_index]
        
    except ValueError:
        await interaction.followup.send("Please provide a valid server number.", ephemeral=True)
        return
    
    try:
        # Generate mod list from preset data
        mod_list = await mod_generator.generate_preset_server_mod_list(selected_name, preset_info)
        
        # Always send as DM
        try:
            dm_channel = await interaction.user.create_dm()
            
            # Split into chunks of 1900 characters to stay well under 2000 limit
            max_chunk_size = 1900
            chunks = []
            
            if len(mod_list) > max_chunk_size:
                # Split by lines first to avoid breaking formatting
                lines = mod_list.split('\n')
                current_chunk = ""
                
                for line in lines:
                    # Check if adding this line would exceed the limit
                    if len(current_chunk) + len(line) + 1 > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = line
                        else:
                            # Line itself is too long, split it
                            chunks.append(line[:max_chunk_size])
                            current_chunk = line[max_chunk_size:]
                    else:
                        if current_chunk:
                            current_chunk += "\n" + line
                        else:
                            current_chunk = line
                
                if current_chunk:
                    chunks.append(current_chunk)
            else:
                chunks = [mod_list]
            
            # Send each chunk
            for i, chunk in enumerate(chunks):
                if len(chunks) > 1:
                    header = f"**{selected_name} - Mod List (Part {i+1}/{len(chunks)})**\n\n"
                else:
                    header = f"**{selected_name} - Mod List**\n\n"
                
                # Make sure header + chunk doesn't exceed limit
                message_content = header + chunk
                if len(message_content) > 2000:
                    # If still too long, send without code blocks
                    await dm_channel.send(header + chunk[:2000-len(header)-10] + "...\n*(truncated)*")
                else:
                    await dm_channel.send(message_content)
                
                # Small delay between messages
                if i < len(chunks) - 1:
                    await asyncio.sleep(0.5)
            
            # Check if server is online for status message
            address = preset_info.get('address', 'TBA')
            port = preset_info.get('port', 0)
            is_online = False
            if address != 'TBA':
                # Check primary address
                for monitored_address, server_data in monitor.server_data.items():
                    if not server_data or len(server_data) < 3:
                        continue
                    server_ip, server_port = monitored_address
                    if server_ip == address and server_port == port + 1:
                        is_online = True
                        break
                
                # Special case: also check 192.168.0.22 for theghost.ddns.net
                if not is_online and address == "theghost.ddns.net":
                    for monitored_address, server_data in monitor.server_data.items():
                        if not server_data or len(server_data) < 3:
                            continue
                        server_ip, server_port = monitored_address
                        if server_ip == "192.168.0.22" and server_port == port + 1:
                            is_online = True
                            break
            
            status_text = "🟢 ONLINE" if is_online else "🔴 OFFLINE"
            await interaction.followup.send(f"Mod list for **{selected_name}** ({status_text}) sent to your DMs!", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("Cannot send DM. Please enable DMs from server members and try again.", ephemeral=True)
        except Exception as dm_error:
            logging.error(f"Error sending DM: {str(dm_error)}")
            await interaction.followup.send(f"Error sending DM: {str(dm_error)}", ephemeral=True)
            
    except Exception as e:
        logging.error(f"Error generating server mod list: {str(e)}")
        await interaction.followup.send(f"Error generating mod list: {str(e)}", ephemeral=True)

# Autocomplete for server selection
@server_command.autocomplete('server')
async def server_autocomplete(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    """Provide autocomplete options for server selection."""
    # Ensure preset servers are loaded
    await monitor.preset_manager.fetch_preset_servers()
    
    preset_servers = monitor.preset_manager.get_all_preset_servers()
    available_servers = list(preset_servers.items())
    
    choices = []
    for i, (server_name, preset_info) in enumerate(available_servers):
        if len(choices) >= 25:  # Discord limit
            break
            
        # Check if server is online
        address = preset_info.get('address', 'TBA')
        port = preset_info.get('port', 0)
        is_online = False
        
        if address != 'TBA':
            # Check primary address
            for monitored_address, server_data in monitor.server_data.items():
                if not server_data or len(server_data) < 3:
                    continue
                server_ip, server_port = monitored_address
                if server_ip == address and server_port == port + 1:
                    is_online = True
                    break
            
            # Special case: also check 192.168.0.22 for theghost.ddns.net
            if not is_online and address == "theghost.ddns.net":
                for monitored_address, server_data in monitor.server_data.items():
                    if not server_data or len(server_data) < 3:
                        continue
                    server_ip, server_port = monitored_address
                    if server_ip == "192.168.0.22" and server_port == port + 1:
                        is_online = True
                        break
        
        status = "🟢" if is_online else "🔴"
        password_text = " [PW]" if preset_info.get('password') else ""
        display_name = f"{status} {server_name}{password_text}"
        
        if len(display_name) > 80:  # Discord choice name limit
            display_name = display_name[:77] + "..."
        choices.append(discord.app_commands.Choice(name=f"{i+1}. {display_name}", value=str(i+1)))
    
    return choices

@bot.tree.command(name="cdlc", description="Get download links and info for Arma 3 Creator DLCs")
@discord.app_commands.describe(dlc="Choose which CDLC to get info for (optional)")
async def cdlc_command(interaction: discord.Interaction, dlc: str = None):
    """Show information about Arma 3 Creator DLCs with download links."""
    await interaction.response.defer(ephemeral=True)
    
    # Ensure mod config is loaded
    await mod_generator.fetch_config_data()
    
    dlc_data = mod_generator.content_links.get('dlc', {})
    
    if not dlc_data:
        await interaction.followup.send("No CDLC data available. Please try again later.", ephemeral=True)
        return
    
    # If no specific DLC requested, show all available
    if dlc is None:
        message_parts = []
        message_parts.append("**Arma 3 Creator DLCs Available:**\n")
        
        for i, (dlc_key, dlc_info) in enumerate(dlc_data.items(), 1):
            description = dlc_info.get('description', dlc_key.upper())
            message_parts.append(f"**{i}.** {description}")
        
        message_parts.append("\nUse `/cdlc <number>` to get download info for a specific CDLC.")
        message_parts.append("Example: `/cdlc 1` for the first DLC.")
        
        await interaction.followup.send("\n".join(message_parts), ephemeral=True)
        return
    
    # Parse DLC selection
    try:
        dlc_index = int(dlc) - 1
        dlc_keys = list(dlc_data.keys())
        
        if dlc_index < 0 or dlc_index >= len(dlc_keys):
            await interaction.followup.send(f"Invalid DLC number. Please use 1-{len(dlc_keys)}.", ephemeral=True)
            return
        
        selected_key = dlc_keys[dlc_index]
        selected_dlc = dlc_data[selected_key]
        
    except ValueError:
        await interaction.followup.send("Please provide a valid DLC number.", ephemeral=True)
        return
    
    # Generate DLC info message
    try:
        message_parts = []
        
        # Header
        description = selected_dlc.get('description', selected_key.upper())
        message_parts.append(f"**Arma 3 Creator DLC: {description}**\n")
        
        # Download info
        download_link = selected_dlc.get('link', 'N/A')
        password = selected_dlc.get('pwd', 'N/A')
        
        message_parts.append(f"**Download:** <{download_link}>")
        if password != 'N/A':
            message_parts.append(f"**Password:** {password}\n")
        else:
            message_parts.append("")
        
        # Installation instructions
        message_parts.append("**Installation:**")
        message_parts.append("1. Download the DLC file")
        message_parts.append("2. Navigate to your Arma 3 installation folder")
        message_parts.append("3. Select and extract the downloaded file using 7zip")
        message_parts.append("4. Use 'Extract here' option in 7zip")
        message_parts.append("5. Launch Arma 3 and the DLC should be available\n")
        
        # Additional notes
        message_parts.append("**Notes:**")
        message_parts.append("• Make sure Arma 3 is closed during installation")
        message_parts.append("• Creator DLCs add new maps, vehicles, and equipment")
        message_parts.append("• Some servers may require specific DLCs to join")
        message_parts.append("• Check server mod lists to see which DLCs are needed")
        
        full_message = "\n".join(message_parts)
        
        # Send as DM to avoid clutter
        try:
            dm_channel = await interaction.user.create_dm()
            
            # Split message if too long
            if len(full_message) > 1900:
                # Split into chunks
                chunks = []
                lines = full_message.split('\n')
                current_chunk = ""
                
                for line in lines:
                    if len(current_chunk) + len(line) + 1 > 1900:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = line
                        else:
                            chunks.append(line[:1900])
                            current_chunk = line[1900:]
                    else:
                        if current_chunk:
                            current_chunk += "\n" + line
                        else:
                            current_chunk = line
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Send each chunk
                for i, chunk in enumerate(chunks):
                    if len(chunks) > 1:
                        header = f"📦 **{description} - Info (Part {i+1}/{len(chunks)})**\n\n"
                    else:
                        header = f"📦 **{description} - DLC Info**\n\n"
                    
                    await dm_channel.send(header + chunk)
                    
                    if i < len(chunks) - 1:
                        await asyncio.sleep(0.5)
            else:
                await dm_channel.send(f"📦 **{description} - DLC Info**\n\n{full_message}")
            
            await interaction.followup.send(f"📨 DLC info for **{description}** sent to your DMs!", ephemeral=True)
            
        except discord.Forbidden:
            # If DM fails, send in channel but truncate if needed
            if len(full_message) > 1900:
                truncated = full_message[:1850] + "...\n*(Message truncated - enable DMs for full info)*"
                await interaction.followup.send(f"📦 **{description} - DLC Info**\n\n{truncated}", ephemeral=True)
            else:
                await interaction.followup.send(f"**{description} - DLC Info**\n\n{full_message}", ephemeral=True)
        except Exception as dm_error:
            logging.error(f"Error sending DLC info DM: {str(dm_error)}")
            await interaction.followup.send(f"Error sending DM: {str(dm_error)}", ephemeral=True)
            
    except Exception as e:
        logging.error(f"Error generating DLC info: {str(e)}")
        await interaction.followup.send(f"Error generating DLC info: {str(e)}", ephemeral=True)

# Autocomplete for CDLC selection
@cdlc_command.autocomplete('dlc')
async def cdlc_autocomplete(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    """Provide autocomplete options for CDLC selection."""
    # Ensure mod config is loaded
    await mod_generator.fetch_config_data()
    
    dlc_data = mod_generator.content_links.get('dlc', {})
    
    choices = []
    for i, (dlc_key, dlc_info) in enumerate(dlc_data.items()):
        if len(choices) >= 25:  # Discord limit
            break
        description = dlc_info.get('description', dlc_key.upper())
        if len(description) > 80:  # Discord choice name limit
            description = description[:77] + "..."
        choices.append(discord.app_commands.Choice(name=f"{i+1}. {description}", value=str(i+1)))
    
    return choices

@bot.command(name='reset_player')
async def reset_player_stats(ctx, player_name: str, reset_type: str = "session"):
    """Reset a specific player's stats (admin only).
    
    Usage: 
    !reset_player <name> session - Reset only session tracking
    !reset_player <name> total - Reset all accumulated stats
    !reset_player <name> all - Reset everything including monthly
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Admin permissions required.")
        return
    
    if player_name not in monitor.player_stats:
        await ctx.send(f"Player **{player_name}** not found in leaderboard.")
        return
    
    stats = monitor.player_stats[player_name]
    
    if reset_type.lower() == "session":
        # Reset only session tracking
        stats.current_session_kills = 0
        stats.last_session_time = 0
        stats.last_kill_update = None
        await ctx.send(f"Reset session tracking for **{player_name}**")
        logging.info(f"Manual session reset for {player_name} by {ctx.author}")
        
    elif reset_type.lower() == "total":
        # Reset accumulated stats but keep monthly
        old_kills = stats.kills
        old_time = stats.time_played
        stats.kills = 0
        stats.time_played = 0
        stats.current_session_kills = 0
        stats.last_session_time = 0
        stats.last_kill_update = None
        await ctx.send(f"Reset total stats for **{player_name}** (was {old_kills} kills, {format_time_readable(old_time)})")
        logging.info(f"Manual total reset for {player_name} by {ctx.author} - was {old_kills} kills, {format_time_readable(old_time)}")
        
    elif reset_type.lower() == "all":
        # Reset everything including monthly
        old_kills = stats.kills
        old_time = stats.time_played
        stats.kills = 0
        stats.time_played = 0
        stats.current_session_kills = 0
        stats.last_session_time = 0
        stats.last_kill_update = None
        
        # Also reset monthly if exists
        if player_name in monitor.monthly_leaderboard:
            monthly_stats = monitor.monthly_leaderboard[player_name]
            monthly_stats.kills = 0
            monthly_stats.time_played = 0
        
        await ctx.send(f"Reset ALL stats for **{player_name}** (was {old_kills} kills, {format_time_readable(old_time)})")
        logging.info(f"Manual complete reset for {player_name} by {ctx.author} - was {old_kills} kills, {format_time_readable(old_time)}")
        
    else:
        await ctx.send("Invalid reset type. Use: `session`, `total`, or `all`")
        return
    
    # Save changes to database
    DataManager.save_leaderboard(monitor.player_stats, monitor.monthly_leaderboard)

@bot.command(name='leaderboard_info')
async def leaderboard_info(ctx, player_name: str = None):
    """Show detailed leaderboard info for a player (admin only)."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Admin permissions required.")
        return
    
    if player_name:
        if player_name in monitor.player_stats:
            stats = monitor.player_stats[player_name]
            embed = discord.Embed(title=f"Stats for {player_name}", color=0x00ff00)
            embed.add_field(name="Total Kills", value=stats.kills, inline=True)
            embed.add_field(name="Total Time", value=format_time_readable(stats.time_played), inline=True)
            embed.add_field(name="Current Session Kills", value=stats.current_session_kills, inline=True)
            embed.add_field(name="Last Session Time", value=format_time_readable(stats.last_session_time), inline=True)
            embed.add_field(name="Last Seen", value=stats.last_seen.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            if stats.last_kill_update:
                embed.add_field(name="Last Kill Update", value=stats.last_kill_update.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Player **{player_name}** not found.")
    else:
        total_players = len(monitor.player_stats)
        total_kills = sum(stats.kills for stats in monitor.player_stats.values())
        total_time = sum(stats.time_played for stats in monitor.player_stats.values())
        
        embed = discord.Embed(title="Leaderboard Summary", color=0x00ff00)
        embed.add_field(name="Total Players", value=total_players, inline=True)
        embed.add_field(name="Total Kills", value=total_kills, inline=True)
        embed.add_field(name="Total Time", value=format_time_readable(total_time), inline=True)
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    """Initialize bot by clearing old messages and starting update loop."""
    logging.info(f'Logged in as {bot.user}')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")
    
    channel = bot.get_channel(CONFIG['CHANNEL_ID'])
    
    async for message in channel.history(limit=100):
        if message.author == bot.user:
            await message.delete()
            logging.info(f"Deleted old bot message: {message.id}")
    
    # IMPORTANT: Leaderboard message first, then server status
    monitor.leaderboard_message = await channel.send("Updating leaderboard...")
    DataManager.save_message(monitor.leaderboard_message.id, CONFIG['CHANNEL_ID'], 'leaderboard')
    
    monitor.status_message = await channel.send("Updating server status...")
    DataManager.save_message(monitor.status_message.id, CONFIG['CHANNEL_ID'], 'status')
    
    bot.loop.create_task(status_update_loop())

async def status_update_loop():
    """Continuously update server data and Discord messages."""
    while True:
        try:
            # Update server data
            try:
                await monitor.update_all_servers()
            except Exception as e:
                logging.error(f"Error updating server data: {str(e)}")
            
            # Update leaderboard message
            try:
                if monitor.leaderboard_message:
                    await monitor.leaderboard_message.edit(content="", embed=monitor.format_leaderboard())
            except Exception as e:
                logging.error(f"Error updating leaderboard message: {str(e)}")
            
            # Update status message
            try:
                if monitor.status_message:
                    await monitor.status_message.edit(content="", embed=monitor.format_server_status())
            except Exception as e:
                logging.error(f"Error updating status message: {str(e)}")
                
        except Exception as e:
            logging.error(f"Unexpected error in update loop: {str(e)}")
        
        await asyncio.sleep(CONFIG['REFRESH_INTERVAL'])

if __name__ == "__main__":
    try:
        bot.run(CONFIG['API_KEY'])
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
