import discord
from discord import app_commands
from discord.ext import tasks
import random
import sqlite3
import datetime
import asyncio
import inspect
import time
import os
import sys
import re
import ctypes
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from types import SimpleNamespace
from urllib.error import URLError
from urllib.request import Request, urlopen
from discord.ui import Button, View
from contextlib import contextmanager
from PIL import Image, ImageDraw, ImageOps
from dotenv import load_dotenv
from eras import ERA_ALIASES, ERA_ALIAS_LOOKUP, ERAS, normalize_era_alias

# Reuse this module when feature files import shared bot state during script startup.
sys.modules.setdefault("bot", sys.modules[__name__])

load_dotenv()

from kotone.client import bot


from kotone.db import get_db

from kotone.cooldowns import cooldown_reminder_loop
















@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name="Andless",
            type=discord.ActivityType.listening,
            details="YouTube",
            details_url="https://www.youtube.com/watch?v=uqJ6GDJSyfY",
            state="Spotify",
            state_url="https://open.spotify.com/track/54E6zLaoW4ofXKaXhLVu3G",
        ),
    )
    if not cooldown_reminder_loop.is_running():
        cooldown_reminder_loop.start()




































def format_afk_duration(elapsed_seconds):
    units = (
        (365 * 86400, "year"),
        (30 * 86400, "month"),
        (7 * 86400, "week"),
        (86400, "day"),
        (3600, "hour"),
        (60, "minute"),
        (1, "second"),
    )
    elapsed_seconds = max(1, int(elapsed_seconds))
    for unit_seconds, unit_name in units:
        if elapsed_seconds >= unit_seconds:
            count = elapsed_seconds // unit_seconds
            plural = "" if count == 1 else "s"
            return f"{count} {unit_name}{plural}"
    return "1 second"







# -------------------- NEW COMMANDS --------------------



# -------------------------------------------------------

@bot.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == bot.user:
        return

    afk_responses = []
    if message.guild is not None:
        mentioned_users = {
            user.id: user
            for user in message.mentions
            if user.id != message.author.id and not user.bot
        }
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT reason FROM guild_afk
                       WHERE guild_id=? AND user_id=?''',
                    (message.guild.id, message.author.id),
                )
                author_afk = cursor.fetchone()
                if author_afk:
                    cursor.execute(
                        "DELETE FROM guild_afk WHERE guild_id=? AND user_id=?",
                        (message.guild.id, message.author.id),
                    )
                    afk_responses.append(
                        f"Welcome back, **{message.author.display_name}**! "
                        "Your AFK status has been removed."
                    )

                if mentioned_users:
                    placeholders = ",".join("?" for _ in mentioned_users)
                    cursor.execute(
                        f'''SELECT user_id, reason, since FROM guild_afk
                            WHERE guild_id=? AND user_id IN ({placeholders})''',
                        (message.guild.id, *mentioned_users),
                    )
                    now = time.time()
                    for user_id, reason, since in cursor.fetchall():
                        mentioned_user = mentioned_users[user_id]
                        duration = format_afk_duration(now - since)
                        visible_reason = reason
                        if len(visible_reason) > 300:
                            visible_reason = visible_reason[:297] + "..."
                        afk_responses.append(
                            f"**{mentioned_user.display_name}** is AFK: "
                            f"{visible_reason} — {duration} ago."
                        )
        except sqlite3.Error as error:
            print(f"Database error while checking AFK statuses: {error}")
            afk_responses.append(
                "AFK statuses couldn't be checked due to a database error."
            )

    if afk_responses:
        response = []
        response_length = 0
        for afk_response in afk_responses:
            if response_length + len(afk_response) + 1 > 1900:
                response.append("More AFK statuses were omitted.")
                break
            response.append(afk_response)
            response_length += len(afk_response) + 1
        await message.reply(
            "\n".join(response),
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )
    
    # Only respond to direct greeting messages, not commands or quoted examples.
    greeting = message.content.strip()
    kotone_greeting = re.fullmatch(
        r"(?:hi|hello|hey)\s+(?:kotone|tone)[.!?]*",
        greeting,
        re.IGNORECASE,
    )
    kotone_goodnight = re.fullmatch(
        r"(?:good\s*night|night)\s+(?:kotone|tone)[.!?]*",
        greeting,
        re.IGNORECASE,
    )
    jiwoo_greeting = re.fullmatch(
        r"(?:hi|hello|hey)\s+jiwoo[.!?]*",
        greeting,
        re.IGNORECASE,
    )

    if kotone_goodnight:
        await message.reply("Good night! 💤")
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/"
            "1335162578246041680/1559482247713923092/"
            "SaveClip.App_723406788_18056502230752032_4643667593876559471_n.jpg"
        )

    elif kotone_greeting:
        await message.reply("Hi!")
        await message.channel.send("https://tenor.com/view/triples-kotone-kpop-s11-kamimoto-kotone-gif-1824783912790233912")

    if jiwoo_greeting:
        await message.reply("Hi!")
        # TODO: replace with a Jiwoo GIF link
        await message.channel.send("https://klipy.com/gifs/lee-jiwoo-jiwoo-triples")


@bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        message = (
            f"This command is on cooldown. Try again in "
            f"{error.retry_after:.1f} seconds."
        )
    else:
        print(f"Error in slash command: {error}")
        message = "An unexpected error occurred. Please try again later."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


# Load command modules so all slash commands are registered before the bot starts.
import features

# Run the bot with its token from the environment.
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set. Add it to your .env file.")

    instance_mutex = None
    if os.name == "nt":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = (
            ctypes.c_void_p,
            ctypes.c_bool,
            ctypes.c_wchar_p,
        )
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
        kernel32.CloseHandle.restype = ctypes.c_bool
        ctypes.set_last_error(0)
        instance_mutex = kernel32.CreateMutexW(
            None,
            False,
            "Local\\KotoneDiscordBot",
        )
        if not instance_mutex:
            raise ctypes.WinError(ctypes.get_last_error())
        if ctypes.get_last_error() == 183:
            kernel32.CloseHandle(instance_mutex)
            raise RuntimeError(
                "Another Kotone Discord bot instance is already running."
            )

    try:
        bot.run(token)
    except discord.LoginFailure:
        print("ERROR: Invalid bot token!")
        raise
    except Exception as e:
        print(f"ERROR: Failed to start bot: {e}")
        raise
    finally:
        if instance_mutex:
            kernel32.CloseHandle(instance_mutex)