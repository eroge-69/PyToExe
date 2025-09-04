import asyncio
import logging
import traceback
from typing import Dict, Optional

import discord
from discord.utils import setup_logging


def print_banner() -> None:
    banner_text = "Rights _o9g"
    width = 80
    print("\n" + banner_text.center(width))
    print(("=" * len(banner_text)).center(width))


def prompt_inputs() -> tuple[str, int, int]:
    print("All inputs must be in English.")
    print("Use a Discord BOT token. User tokens are not supported and violate Discord TOS.")
    token = input("Enter your Discord bot token: ").strip()
    source_id_str = input("Enter the source server (guild) ID to copy FROM: ").strip()
    target_id_str = input("Enter the target server (guild) ID to copy INTO: ").strip()
    try:
        source_id = int(source_id_str)
        target_id = int(target_id_str)
    except ValueError:
        raise SystemExit("Guild IDs must be integers.")
    if not token:
        raise SystemExit("Token cannot be empty.")
    return token, source_id, target_id


async def copy_emojis(source: discord.Guild, target: discord.Guild) -> None:
    if not source.emojis:
        return
    print(f"Copying emojis ({len(source.emojis)} found)...")
    for emoji in source.emojis:
        try:
            if len(target.emojis) >= target.emoji_limit:
                print("- Emoji limit reached on target guild; skipping remaining emojis.")
                break
            try:
                image_bytes = await emoji.read()  # discord.py 2.3+
            except AttributeError:
                image_bytes = await emoji.url.read()  # fallback via Asset
            created = await target.create_custom_emoji(name=emoji.name, image=image_bytes)
            print(f"- Created emoji: :{created.name}:")
            await asyncio.sleep(0.5)
        except discord.Forbidden:
            print("- Missing permissions to create emojis in target guild; skipping emojis.")
            return
        except Exception as exc:
            print(f"- Failed to copy emoji {emoji.name}: {exc}")


def build_overwrites(
    source_channel: discord.abc.GuildChannel, role_map: Dict[int, discord.Role], target_guild: discord.Guild
) -> Dict[discord.abc.Snowflake, discord.PermissionOverwrite]:
    overwrites: Dict[discord.abc.Snowflake, discord.PermissionOverwrite] = {}
    for src_target, overwrite in source_channel.overwrites.items():
        try:
            if isinstance(src_target, discord.Role):
                if src_target.is_default():
                    overwrites[target_guild.default_role] = overwrite
                else:
                    mapped = role_map.get(src_target.id)
                    if mapped is not None:
                        overwrites[mapped] = overwrite
            # Member-specific overwrites are skipped intentionally
        except Exception:
            continue
    return overwrites


async def create_category(
    target: discord.Guild, source_category: discord.CategoryChannel, overwrites: Dict[discord.abc.Snowflake, discord.PermissionOverwrite]
) -> Optional[discord.CategoryChannel]:
    try:
        new_cat = await target.create_category(name=source_category.name, overwrites=overwrites)
        print(f"+ Category: {new_cat.name}")
        await asyncio.sleep(0.5)
        return new_cat
    except discord.Forbidden:
        print("- Missing permissions to create categories in target guild.")
    except Exception as exc:
        print(f"- Failed to create category {source_category.name}: {exc}")
    return None


async def create_text_channel(
    target: discord.Guild,
    source_channel: discord.TextChannel,
    category: Optional[discord.CategoryChannel],
    overwrites: Dict[discord.abc.Snowflake, discord.PermissionOverwrite],
) -> None:
    try:
        kwargs = {
            "name": source_channel.name,
            "topic": source_channel.topic,
            "nsfw": source_channel.nsfw,
            "slowmode_delay": source_channel.slowmode_delay,
            "category": category,
            "overwrites": overwrites,
        }
        new_ch = await target.create_text_channel(**kwargs)
        print(f"  - Text channel: #{new_ch.name}")
        await asyncio.sleep(0.5)
    except discord.Forbidden:
        print("  - Missing permissions to create text channels.")
    except Exception as exc:
        print(f"  - Failed to create text channel {source_channel.name}: {exc}")


async def create_voice_channel(
    target: discord.Guild,
    source_channel: discord.VoiceChannel,
    category: Optional[discord.CategoryChannel],
    overwrites: Dict[discord.abc.Snowflake, discord.PermissionOverwrite],
) -> None:
    try:
        bitrate = min(source_channel.bitrate or target.bitrate_limit, target.bitrate_limit)
        kwargs = {
            "name": source_channel.name,
            "user_limit": source_channel.user_limit,
            "bitrate": bitrate,
            "category": category,
            "overwrites": overwrites,
        }
        new_ch = await target.create_voice_channel(**kwargs)
        print(f"  - Voice channel: {new_ch.name}")
        await asyncio.sleep(0.5)
    except discord.Forbidden:
        print("  - Missing permissions to create voice channels.")
    except Exception as exc:
        print(f"  - Failed to create voice channel {source_channel.name}: {exc}")


async def wipe_guild(target: discord.Guild) -> None:
    print("Wiping target guild (channels, roles, emojis)...")
    # Delete channels (includes categories)
    for ch in sorted(target.channels, key=lambda c: getattr(c, "position", 0), reverse=True):
        try:
            await ch.delete(reason="Server clone wipe")
            print(f"- Deleted channel: {getattr(ch, 'name', str(ch.id))}")
            await asyncio.sleep(0.3)
        except Exception as exc:
            print(f"- Failed to delete channel {getattr(ch, 'name', str(ch.id))}: {exc}")

    # Delete emojis
    for e in list(target.emojis):
        try:
            await e.delete(reason="Server clone wipe")
            print(f"- Deleted emoji: :{e.name}:")
            await asyncio.sleep(0.3)
        except Exception as exc:
            print(f"- Failed to delete emoji {e.name}: {exc}")

    # Delete roles (cannot delete @everyone, managed roles, or roles >= bot top role)
    me = target.me
    top_position = me.top_role.position if me and me.top_role else 0
    for role in reversed(target.roles):
        try:
            if role.is_default() or role.managed:
                continue
            if role.position >= top_position:
                print(f"- Skipping role (above bot): {role.name}")
                continue
            await role.delete(reason="Server clone wipe")
            print(f"- Deleted role: {role.name}")
            await asyncio.sleep(0.3)
        except Exception as exc:
            print(f"- Failed to delete role {role.name}: {exc}")


async def copy_guild_profile(source: discord.Guild, target: discord.Guild) -> None:
    try:
        kwargs = {"name": source.name}
        try:
            if source.icon is not None:
                kwargs["icon"] = await source.icon.read()
        except Exception:
            pass
        try:
            if getattr(source, "banner", None) is not None:
                kwargs["banner"] = await source.banner.read()
        except Exception:
            pass
        await target.edit(**kwargs)
        print("Copied guild profile (name/icon/banner if available).")
    except discord.Forbidden:
        print("- Missing permissions to edit target guild profile (name/icon).")
    except Exception as exc:
        print(f"- Failed to edit target guild profile: {exc}")


async def copy_roles(source: discord.Guild, target: discord.Guild) -> Dict[int, discord.Role]:
    print("Copying roles...")
    role_map: Dict[int, discord.Role] = {}
    role_map[source.default_role.id] = target.default_role

    me = target.me
    top_position = me.top_role.position if me and me.top_role else 0

    # Create roles from bottom to top, skip managed and @everyone
    source_roles = [r for r in source.roles if not r.is_default() and not r.managed]
    source_roles.sort(key=lambda r: r.position)
    for src in source_roles:
        try:
            icon_bytes = None
            try:
                display_icon = getattr(src, "display_icon", None)
                if display_icon is not None:
                    icon_bytes = await display_icon.read()
            except Exception:
                icon_bytes = None
            new_role = await target.create_role(
                name=src.name,
                permissions=src.permissions,
                colour=src.colour,
                hoist=src.hoist,
                mentionable=src.mentionable,
                icon=icon_bytes if icon_bytes else None,
                reason="Server clone create role",
            )
            role_map[src.id] = new_role
            print(f"- Created role: {new_role.name}")
            await asyncio.sleep(0.5)
        except discord.Forbidden:
            print(f"- Missing permissions to create role: {src.name}")
        except Exception as exc:
            print(f"- Failed to create role {src.name}: {exc}")

    # Reorder roles as close as possible under bot's top role
    for src in sorted(source_roles, key=lambda r: r.position, reverse=False):
        new_role = role_map.get(src.id)
        if not new_role:
            continue
        try:
            desired = min(src.position, max(1, top_position - 1))
            await new_role.edit(position=desired, reason="Server clone role ordering")
            await asyncio.sleep(0.3)
        except Exception as exc:
            print(f"- Failed to set position for role {new_role.name}: {exc}")

    return role_map


async def clone_structure(source: discord.Guild, target: discord.Guild) -> None:
    print(f"Source: {source.name} ({source.id})")
    print(f"Target: {target.name} ({target.id})")

    await wipe_guild(target)
    await copy_guild_profile(source, target)
    role_map = await copy_roles(source, target)
    await copy_emojis(source, target)

    category_map: Dict[int, discord.CategoryChannel] = {}

    # Create uncategorized channels first
    print("Creating uncategorized channels...")
    for ch in sorted(source.channels, key=lambda c: getattr(c, "position", 0)):
        if ch.category is not None:
            continue
        if isinstance(ch, discord.TextChannel):
            overwrites = build_overwrites(ch, role_map, target)
            await create_text_channel(target, ch, None, overwrites)
        elif isinstance(ch, discord.VoiceChannel):
            overwrites = build_overwrites(ch, role_map, target)
            await create_voice_channel(target, ch, None, overwrites)

    # Create categories, then their channels
    print("Creating categories and their channels...")
    for cat in sorted(source.categories, key=lambda c: c.position):
        overwrites_cat = build_overwrites(cat, role_map, target)
        new_cat = await create_category(target, cat, overwrites_cat)
        if new_cat is None:
            continue
        category_map[cat.id] = new_cat
        # Channels inside this category
        text_channels = [c for c in cat.channels if isinstance(c, discord.TextChannel)]
        voice_channels = [c for c in cat.channels if isinstance(c, discord.VoiceChannel)]
        for t in sorted(text_channels, key=lambda c: c.position):
            overwrites = build_overwrites(t, role_map, target)
            await create_text_channel(target, t, new_cat, overwrites)
        for v in sorted(voice_channels, key=lambda c: c.position):
            overwrites = build_overwrites(v, role_map, target)
            await create_voice_channel(target, v, new_cat, overwrites)

    print("Done. Notes: Member-specific overwrites and some managed roles cannot be cloned.")


class ClonerClient(discord.Client):
    def __init__(self, source_id: int, target_id: int):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.emojis_and_stickers = True
        super().__init__(intents=intents)
        self.source_id = source_id
        self.target_id = target_id

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (id={self.user.id})")
        print("Guilds the bot can access:")
        for g in self.guilds:
            print(f"- {g.name} ({g.id})")
        if self.source_id == self.target_id:
            print("Error: Source and target guild IDs are the same. They must be different.")
            await self.close()
            return
        source = self.get_guild(self.source_id)
        target = self.get_guild(self.target_id)
        if source is None:
            print("Error: Bot is not a member of the SOURCE guild. Invite the bot there and try again.")
            await self.close()
            return
        if target is None:
            print("Error: Bot is not a member of the TARGET guild. Invite the bot there and try again.")
            await self.close()
            return
        try:
            print("Starting clone...")
            await clone_structure(source, target)
            print("Clone finished.")
        except Exception as exc:
            print(f"Unexpected error during clone: {exc}")
            traceback.print_exc()
        finally:
            await self.close()


def main() -> None:
    print_banner()
    setup_logging(level=logging.INFO)
    token, source_id, target_id = prompt_inputs()
    client = ClonerClient(source_id=source_id, target_id=target_id)
    try:
        client.run(token)
    except discord.LoginFailure:
        print("Invalid bot token. Please double-check and try again.")
    finally:
        try:
            input("\nPress Enter to exit...")
        except EOFError:
            pass


if __name__ == "__main__":
    main()


