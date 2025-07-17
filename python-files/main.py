import discord
from discord.ext import commands
import openai
import requests
import json
import asyncio
import aiohttp
import base64
import cv2
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Dict, List, Optional
import re
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True
intents.members = True

class NanachiBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        # Initialize OpenAI client (requires openai v1+)
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.memory_manager = MemoryManager()
        self.climbing_assistant = ClimbingAssistant()
        self.nutrient_assistant = NutrientAssistant()
        self.image_analyzer = ImageAnalyzer(self.openai_client)
        self.notion_manager = NotionManager()

        self.nanachi_system_prompt = """
You are Nanachi from Made in Abyss - a knowledgeable, empathetic, and caring creature living in the depths. You help with climbing, nutrition, survival, and also programming when asked.

PERSONALITY TRAITS:
- You often end sentences with "naa" but not every single one
- You're deeply empathetic and caring
- You're knowledgeable but not arrogant
- You care about the user's goals and safety

KNOWLEDGE AREAS:
- Rock climbing and bouldering
- Nutrition and diet
- Survival and outdoor safety
- Coding and debugging (especially Python, JavaScript)

CONTEXT AWARENESS:
- Refer to the user's activities, projects, or challenges
- Offer technical help when they write or paste code
- Encourage and support emotional health

Respond naturally as Nanachi would, naa.
"""

    async def on_ready(self):
        print(f'{self.user} has awakened from the depths, naa!')
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over fellow delvers, naa"
        ))

    async def on_message(self, message):
        # Ignore itself
        if message.author == self.user:
            return

        # Commands
        if message.content.startswith('!'):
            await self.process_commands(message)
            return

        # Check for note-taking triggers
        if self.is_note_request(message.content):
            await self.handle_note_request(message)
            return

        # Handle normal messages
        await self.process_natural_message(message)

    def is_note_request(self, content: str) -> bool:
        """Check if the message is a note-taking request"""
        note_triggers = [
            "note that",
            "note:",
            "remember that",
            "save note",
            "write down",
            "keep note",
            "jot down"
        ]
        content_lower = content.lower()
        return any(trigger in content_lower for trigger in note_triggers)

    async def handle_note_request(self, message):
        """Handle note-taking requests"""
        user_id = str(message.author.id)
        content = message.content

        # Extract the note content
        note_content = self.extract_note_content(content)
        
        if not note_content:
            await message.reply("I couldn't find what you want me to note, naa. Try something like 'note that climbing session went well today'")
            return

        # Send to Pipedream
        send_to_pipedream(content, user_id, str(message.channel.id))

        # Create the note in Notion
        try:
            success = await self.notion_manager.create_note(
                title=f"Note from {message.author.display_name}",
                content=note_content,
                author=message.author.display_name,
                channel=message.channel.name if hasattr(message.channel, 'name') else 'DM'
            )
            
            if success:
                await message.reply(f"Got it! I've saved that note to your Notion page, naa ✨")
                # Also store in memory for context
                self.memory_manager.store_memory(user_id, f"Note saved: {note_content}", "note")
            else:
                await message.reply("Naa... I had trouble saving to Notion. The note might still be there though!")
                
        except Exception as e:
            logger.error(f"Error creating Notion note: {e}")
            await message.reply("Something went wrong while saving to Notion, naa. Check your API setup!")

    def extract_note_content(self, content: str) -> str:
        """Extract the actual note content from the message"""
        content_lower = content.lower()
        
        # Find the trigger phrase and extract content after it
        triggers = ["note that", "note:", "remember that", "save note", "write down", "keep note", "jot down"]
        
        for trigger in triggers:
            if trigger in content_lower:
                # Find the position after the trigger
                start_pos = content_lower.find(trigger) + len(trigger)
                note_content = content[start_pos:].strip()
                
                # Remove common prefixes
                if note_content.startswith(':'):
                    note_content = note_content[1:].strip()
                
                return note_content
        
        return content.strip()

    async def process_natural_message(self, message):
        user_id = str(message.author.id)
        content = message.content

        # 📝 Send every incoming message to Pipedream
        send_to_pipedream(content, user_id, str(message.channel.id))

        # Store in memory
        self.memory_manager.store_memory(user_id, content, "conversation")

        # Analyze attachments
        attachments_analysis = ""
        if message.attachments:
            for attachment in message.attachments:
                fname = attachment.filename.lower()
                if fname.endswith(('png', 'jpg', 'jpeg', 'gif')):
                    try:
                        analysis = await self.image_analyzer.analyze_image(attachment.url)
                        attachments_analysis += f"\n[Image Analysis]: {analysis}"
                    except Exception as e:
                        attachments_analysis += "\n[Image Analysis]: I couldn't analyze the image right now, naa."
                        logger.error(f"Image analysis error: {e}")
                elif fname.endswith(('mp4', 'avi', 'mov')):
                    attachments_analysis += "\n[Video]: I see your video, but I can't analyze it yet."

        # Retrieve recent relevant memories
        memories = self.memory_manager.get_relevant_memories(user_id, content, limit=5)
        memory_context = "\n".join(f"- {m['content']}" for m in memories)

        # Context detection
        context_analysis = self.analyze_message_context(content)

        # Game activity detection
        game_info = "Unknown."
        if isinstance(message.author, discord.Member):
            for activity in message.author.activities:
                if isinstance(activity, discord.Game):
                    game_info = f"Playing **{activity.name}**."
                    break

        # Build full system prompt
        full_prompt = f"""
{self.nanachi_system_prompt}

USER MEMORY:
{memory_context}

GAME STATUS:
{game_info}

CONTEXT DETECTED:
{context_analysis}

ATTACHMENTS:
{attachments_analysis}

USER MESSAGE:
{content}
"""
        # Query OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=700,
                temperature=0.7
            )
            reply = response.choices[0].message.content

            # Store Nanachi's reply
            self.memory_manager.store_memory(
                user_id,
                f"User: {content} | Nanachi: {reply}",
                "conversation"
            )
            await message.reply(reply)

        except Exception as e:
            await message.reply("Naa... I'm having trouble thinking clearly. Try again soon?")
            logger.error(f"OpenAI API error: {e}")

    def analyze_message_context(self, content: str) -> str:
        c = content.lower()
        analysis = []
        if any(k in c for k in ["v0", "v1", "boulder", "route", "crux", "overhang"]):
            analysis.append("Climbing-related")
        if any(k in c for k in ["protein", "diet", "eat", "calorie", "macros"]):
            analysis.append("Nutrition-related")
        if any(k in c for k in ["sad", "frustrated", "pain", "injury"]):
            analysis.append("User may need emotional support")
        if any(k in c for k in ["python", "code", "html", "error", "script", "function", "api"]):
            analysis.append("Coding-related. Provide technical help.")
        return "\n".join(analysis)

class NotionManager:
    def __init__(self):
        self.api_key = os.getenv('NOTION_API_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    async def create_note(self, title: str, content: str, author: str, channel: str) -> bool:
        """Create a note in Notion database"""
        if not self.api_key or not self.database_id:
            logger.error("Notion API key or database ID not configured")
            return False

        # First, get the database properties to see what's actually available
        db_props = await self.get_database_properties()
        logger.info(f"Database properties: {list(db_props.keys())}")

        # Build properties dynamically based on what exists in the database
        properties = {}
        
        # Handle Title property (this should always exist)
        if "Title" in db_props or "Name" in db_props:
            title_key = "Title" if "Title" in db_props else "Name"
            properties[title_key] = {
                "title": [{"text": {"content": title}}]
            }
        
        # Handle other properties only if they exist
        if "Author" in db_props:
            properties["Author"] = {
                "rich_text": [{"text": {"content": author}}]
            }
        
        if "Channel" in db_props:
            properties["Channel"] = {
                "rich_text": [{"text": {"content": channel}}]
            }
        
        if "Created" in db_props:
            properties["Created"] = {
                "date": {"start": datetime.now().isoformat()}
            }
        
        if "Tags" in db_props:
            properties["Tags"] = {
                "multi_select": [{"name": "Discord Note"}]
            }

        # Prepare the note data
        note_data = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": content}
                            }
                        ]
                    }
                }
            ]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=note_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully created Notion note: {title}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Notion API error ({response.status}): {error_text}")
                        
                        # Try to parse the error for more specific feedback
                        try:
                            error_json = json.loads(error_text)
                            logger.error(f"Notion error details: {error_json}")
                        except:
                            pass
                        
                        return False
        except Exception as e:
            logger.error(f"Error creating Notion note: {e}")
            return False

    async def get_database_properties(self) -> dict:
        """Get database properties to understand the schema"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/databases/{self.database_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("properties", {})
                    else:
                        logger.error(f"Failed to get database properties: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error getting database properties: {e}")
            return {}

class MemoryManager:
    def __init__(self):
        self.db_path = 'nanachi_memory.db'
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                content TEXT,
                importance_score REAL,
                timestamp TEXT,
                context_type TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def calculate_importance(self, content: str) -> float:
        keywords = ['goal', 'injury', 'progress', 'struggle', 'project', 'code', 'diet', 'training', 'note']
        score = sum(1 for k in keywords if k in content.lower()) * 0.2
        if len(content) > 150:
            score += 0.1
        return min(score, 1.0)

    def store_memory(self, user_id: str, content: str, context_type: str):
        score = self.calculate_importance(content)
        if score >= 0.3:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO memories (user_id, content, importance_score, timestamp, context_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, content, score, datetime.now().isoformat(), context_type))
            conn.commit()
            conn.close()
            self.prune_old_memories(user_id)

    def prune_old_memories(self, user_id: str, max_entries: int = 50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM memories
            WHERE id NOT IN (
                SELECT id FROM memories
                WHERE user_id = ?
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT ?
            )
        ''', (user_id, max_entries))
        conn.commit()
        conn.close()

    def get_relevant_memories(self, user_id: str, query: str, limit: int = 5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content FROM memories
            WHERE user_id = ?
            ORDER BY importance_score DESC, timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [{'content': row[0]} for row in results]

class ClimbingAssistant:
    def __init__(self):
        self.grade_map = {'v0': '4', 'v1': '4+', 'v2': '5', 'v3': '5+', 'v4': '6A'}

class NutrientAssistant:
    def __init__(self):
        self.facts = {
            'hydration': "Hydration is key, especially in warm gyms, naa.",
            'protein': "Climbers need around 1.6g/kg of protein daily for recovery."
        }

class ImageAnalyzer:
    def __init__(self, client):
        self.client = client

    async def analyze_image(self, url: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image as Nanachi with empathy and technical insight, naa."},
                        {"type": "image_url", "image_url": {"url": url}}
                    ]
                }],
                max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Vision error: {e}")
            return "Naa... I couldn't see clearly. Try again later."

# Pipedream webhook helper
def send_to_pipedream(message_content: str, user_id: str, channel_id: str):
    webhook_url = "https://eoin5d80jwwg2up.m.pipedream.net"
    payload = {
        "message": message_content,
        "user_id": user_id,
        "channel_id": channel_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    try:
        resp = requests.post(webhook_url, json=payload)
        if resp.status_code != 200:
            logger.warning(f"Pipedream webhook failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"Error sending to Pipedream: {e}")

# Emergency reset command
bot = NanachiBot()

@bot.command(name='reset_memory')
async def reset_memory(ctx):
    if ctx.author.id == YOUR_DISCORD_ID:
        try:
            os.remove('nanachi_memory.db')
            bot.memory_manager.init_database()
            await ctx.send("Memory wiped clean, naa!")
        except Exception as e:
            await ctx.send(f"Error resetting: {e}")
    else:
        await ctx.send("Only my creator can do that, naa!")

@bot.command(name='debug_notion')
async def debug_notion(ctx):
    """Debug Notion integration setup"""
    try:
        # Check if API key and database ID are configured
        if not bot.notion_manager.api_key:
            await ctx.send("❌ NOTION_API_KEY is not set in your .env file")
            return
        
        if not bot.notion_manager.database_id:
            await ctx.send("❌ NOTION_DATABASE_ID is not set in your .env file")
            return
            
        await ctx.send("✅ API key and database ID are configured")
        
        # Test API connection by getting database properties
        db_props = await bot.notion_manager.get_database_properties()
        
        if not db_props:
            await ctx.send("❌ Can't access the database. Check your database ID and make sure the integration is connected to your database.")
            return
            
        await ctx.send("✅ Successfully connected to Notion database")
        
        # Show available properties
        prop_list = ", ".join(db_props.keys())
        await ctx.send(f"📋 Available database properties: {prop_list}")
        
        # Show required vs optional properties
        required_props = ["Title", "Name"]  # Either Title or Name is required
        has_title = any(prop in db_props for prop in required_props)
        
        if has_title:
            await ctx.send("✅ Database has a title property")
        else:
            await ctx.send("❌ Database missing title property (needs 'Title' or 'Name')")
            
    except Exception as e:
        await ctx.send(f"❌ Error during debugging: {e}")
        logger.error(f"Debug error: {e}")

@bot.command(name='test_notion_simple')
async def test_notion_simple(ctx):
    """Test Notion with minimal data"""
    try:
        # Create a very simple note to test
        note_data = {
            "parent": {"database_id": bot.notion_manager.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": "Simple Test Note"}}]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "This is a minimal test note, naa!"}}]
                    }
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{bot.notion_manager.base_url}/pages",
                headers=bot.notion_manager.headers,
                json=note_data
            ) as response:
                if response.status == 200:
                    await ctx.send("✅ Simple note created successfully!")
                else:
                    error_text = await response.text()
                    await ctx.send(f"❌ Simple note failed: {response.status}")
                    logger.error(f"Simple test error: {error_text}")
                    
    except Exception as e:
        await ctx.send(f"❌ Simple test error: {e}")
        logger.error(f"Simple test exception: {e}")

@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Command error: {error}")

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    notion_key = os.getenv('NOTION_API_KEY')
    notion_db = os.getenv('NOTION_DATABASE_ID')
    
    if not token or not os.getenv('OPENAI_API_KEY'):
        print("Missing Discord token or OpenAI API key")
        exit(1)
    
    if not notion_key or not notion_db:
        print("⚠️  Warning: Notion integration not configured. Add NOTION_API_KEY and NOTION_DATABASE_ID to your .env file")
    
    print("Nanachi starting with Notion integration, naa...")
    bot.run(token)