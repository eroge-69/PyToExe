import discord
from discord.ext import commands, tasks
from discord.http import Route
import time, random

DISBOARD_ID   = 302050872383242240
CHANNEL_ID    = 123456789012345678  # ← set your bump channel ID here
BUMP_INTERVAL = 2 * 60 * 60         # 2 hours

class AutoBump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.next_bump = time.time()
        self.bump_loop.start()

    def cog_unload(self):
        self.bump_loop.cancel()

    async def fetchSlashCommand(self, channel: discord.TextChannel, app_id: int, name: str):
        data = await self.bot.http.request(
            Route("GET", f"/applications/{app_id}/guilds/{channel.guild.id}/commands")
        )
        for cmd in data:
            if cmd["name"] == name:
                return cmd
        return None

    async def execSlashCommand(self, channel: discord.TextChannel, cmd_data: dict):
        payload = {
            "type": 2,
            "application_id": str(cmd_data["application_id"]),
            "guild_id": str(channel.guild.id),
            "channel_id": str(channel.id),
            "session_id": self.bot.ws.session_id,
            "data": {"id": cmd_data["id"], "name": cmd_data["name"], "options": []}
        }
        await self.bot.http.request(Route("POST", "/interactions"), json=payload)

    @tasks.loop(seconds=30)
    async def bump_loop(self):
        now = time.time()
        if now < self.next_bump:
            return
        try:
            channel  = await self.bot.fetch_channel(CHANNEL_ID)
            cmd_data = await self.fetchSlashCommand(channel, DISBOARD_ID, "bump")
            if cmd_data:
                await self.execSlashCommand(channel, cmd_data)
                self.next_bump = now + BUMP_INTERVAL + random.randint(120, 300)
        except:
            self.next_bump = now + 60

    @commands.command(name="bump")
    async def manual_bump(self, ctx, action: str = None):
        """!bump now | start | stop"""
        await ctx.message.delete()
        action = (action or "").lower()

        if action == "now":
            try:
                channel  = await self.bot.fetch_channel(CHANNEL_ID)
                cmd_data = await self.fetchSlashCommand(channel, DISBOARD_ID, "bump")
                if cmd_data:
                    await self.execSlashCommand(channel, cmd_data)
                    self.next_bump = time.time() + BUMP_INTERVAL
                    await ctx.send("✅ Bumped now", delete_after=5)
                else:
                    await ctx.send("❌ Slash command not found", delete_after=5)
            except:
                await ctx.send("❌ Manual bump failed", delete_after=5)

        elif action == "stop":
            self.bump_loop.stop()
            await ctx.send("⚠️ Auto-bump stopped", delete_after=5)

        elif action == "start":
            if not self.bump_loop.is_running():
                self.bump_loop.start()
            await ctx.send("✅ Auto-bump started", delete_after=5)

        else:
            await ctx.send("Usage: `!bump now` | `!bump start` | `!bump stop`", delete_after=8)

def setup(bot):
    bot.add_cog(AutoBump(bot))

