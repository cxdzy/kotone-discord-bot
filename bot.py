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
































































import kotone.events
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