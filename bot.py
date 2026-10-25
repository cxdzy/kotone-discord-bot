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

# Bot setup
intents = discord.Intents.default()
intents.message_content = True


class KotoneBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced {len(self.tree.get_commands())} slash commands")

bot = KotoneBot()
SLASH_COMMANDS = {}
SLASH_COMMAND_ALIASES = {}


class SlashContext:
    def __init__(self, interaction, invoked_with, members):
        self.interaction = interaction
        self.author = interaction.user
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.bot = interaction.client
        self.invoked_with = invoked_with
        self.message = SimpleNamespace(mentions=members)

    async def reply(self, content=None, **kwargs):
        kwargs.pop("mention_author", None)
        return await self.interaction.followup.send(
            content=content,
            wait=True,
            **kwargs,
        )

    async def send(self, content=None, **kwargs):
        return await self.reply(content, **kwargs)


def slash_command(
    name=None,
    *,
    aliases=(),
    group=None,
    autocomplete=None,
    descriptions=None,
):
    def decorator(callback):
        callback_signature = inspect.signature(callback)
        option_parameters = []
        for parameter in list(callback_signature.parameters.values())[1:]:
            annotation = parameter.annotation
            if annotation is inspect.Parameter.empty:
                annotation = str
            option_parameters.append(
                parameter.replace(
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=annotation,
                )
            )

        async def invoke(interaction, **options):
            await interaction.response.defer(thinking=True)
            members = [
                value
                for value in options.values()
                if isinstance(value, discord.Member)
            ]
            context = SlashContext(
                interaction,
                interaction.data.get("name", command_name),
                members,
            )
            await callback(context, **options)

        command_name = name or callback.__name__
        command_description = (callback.__doc__ or "Run this command.").strip()
        command_description = command_description.splitlines()[0][:100]
        parameters = [
            inspect.Parameter(
                "interaction",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=discord.Interaction,
            ),
            *option_parameters,
        ]
        invoke.__signature__ = inspect.Signature(parameters)
        invoke.__annotations__ = {
            parameter.name: parameter.annotation for parameter in parameters
        }
        if descriptions:
            invoke.__discord_app_commands_param_description__ = descriptions
        if autocomplete:
            app_commands.autocomplete(**autocomplete)(invoke)

        for registered_name in (command_name, *aliases):
            SLASH_COMMAND_ALIASES[registered_name] = tuple(
                alias
                for alias in (command_name, *aliases)
                if alias != registered_name
            )
            command = app_commands.Command(
                name=registered_name,
                description=command_description,
                callback=invoke,
            )
            if group is None:
                bot.tree.add_command(command)
            else:
                group.add_command(command)
            command_key = (
                f"{group.name} {registered_name}"
                if group is not None
                else registered_name
            )
            SLASH_COMMANDS[command_key] = command
        return callback

    return decorator

RARITIES = {
    "Common": 100000,
    "Rare": 44203,
    "Epic": 580,
    "Legendary": 10,
    "Mythic": 1,
}
SPIN_DAILY_LIMIT = 5
SPIN_REWARD_COUNTS = {
    "Common": {
        "Common": 8,
        "Rare": 4,
        "Epic": 2,
        "Legendary": 1,
        "Mythic": 0,
    },
    "Rare": {
        "Common": 6,
        "Rare": 4,
        "Epic": 3,
        "Legendary": 2,
        "Mythic": 0,
    },
    "Epic": {
        "Common": 5,
        "Rare": 4,
        "Epic": 3,
        "Legendary": 2,
        "Mythic": 1,
    },
    "Legendary": {
        "Common": 3,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 3,
        "Mythic": 2,
    },
    "Mythic": {
        "Common": 2,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 4,
        "Mythic": 2,
    },
}
SPIN_BOMB_SLOTS = 1
SPIN_BOARD_SIZE = 16

S_ORDER = (
    "YSY", "JHR", "LJW", "KCY", "KYY", "KSM", "KNK", "GYB", "KAE", "SDH",
    "KTN", "KYJ", "HST", "PSH", "ZXY", "KMY", "LYN", "JBN", "JHY", "SHI",
    "KCW", "SUL", "SEO", "JSH",
)
S_MEMBERS = {
    code: ERAS["ASSEMBLE"]["members"][code]
    for code in S_ORDER[:10]
}
S_MEMBERS.update({
    "KTN": {"name": "Kotone", "full_name": "Kamimoto Kotone"},
    "KYJ": {"name": "Yeonji", "full_name": "Kwak Yeonji"},
    "HST": {"name": "Nien", "full_name": "Hsu Nien Tzu"},
    "PSH": {"name": "Sohyun", "full_name": "Park Sohyun"},
    "ZXY": {"name": "Xinyu", "full_name": "Zhou Xinyu"},
    "KMY": {"name": "Mayu", "full_name": "Koma Mayu"},
    "LYN": {"name": "Lynn", "full_name": "Kawakami Lynn"},
    "JBN": {"name": "Joobin", "full_name": "Joo Bin"},
    "JHY": {"name": "Hayeon", "full_name": "Jeong Hayeon"},
    "SHI": {"name": "Shion", "full_name": "Park Shion"},
    "KCW": {"name": "Chaewon", "full_name": "Kim Chaewon"},
    "SUL": {"name": "Sullin", "full_name": "Pirada Bunraksa"},
    "SEO": {"name": "Seoah", "full_name": "Jeong Haerin"},
    "JSH": {"name": "Jiyeon", "full_name": "Ji Suhyeon"},
})
MINIGAMES = (
    (
        "tripleS Trivia",
        "Answer tripleS trivia questions to earn COMO.",
        "/trivia",
    ),
)

# Database context manager for safer connections
@contextmanager
def get_db():
    conn = sqlite3.connect('kpop_cards.db', timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Database setup
def init_db():
    with get_db() as conn:
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY, 
                      username TEXT, 
                      daily_streak INTEGER DEFAULT 0,
                      last_daily TEXT,
                      como INTEGER DEFAULT 0)''')
        
        # Cards table
        c.execute('''CREATE TABLE IF NOT EXISTS cards
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      serial TEXT UNIQUE,
                      member_code TEXT,
                      era TEXT,
                      rarity TEXT,
                      owner_id INTEGER,
                      obtained_at TEXT,
                      in_binder INTEGER NOT NULL DEFAULT 0,
                      FOREIGN KEY(owner_id) REFERENCES users(user_id))''')
        
        # Cooldowns table
        c.execute('''CREATE TABLE IF NOT EXISTS cooldowns
                     (user_id INTEGER,
                      cooldown_type TEXT,
                      expires_at REAL,
                      PRIMARY KEY(user_id, cooldown_type))''')
        c.execute('''CREATE TABLE IF NOT EXISTS cooldown_reminders
                     (user_id INTEGER NOT NULL,
                      cooldown_type TEXT NOT NULL,
                      enabled INTEGER NOT NULL DEFAULT 0,
                      expires_at REAL,
                      PRIMARY KEY(user_id, cooldown_type))''')
        c.execute('''CREATE TABLE IF NOT EXISTS spin_usage
                     (user_id INTEGER PRIMARY KEY,
                      spin_date TEXT NOT NULL,
                      spins INTEGER NOT NULL DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS guild_afk
                     (guild_id INTEGER NOT NULL,
                      user_id INTEGER NOT NULL,
                      reason TEXT NOT NULL,
                      since REAL NOT NULL,
                      PRIMARY KEY(guild_id, user_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_drop_boosters
                     (user_id INTEGER PRIMARY KEY,
                      expires_at REAL NOT NULL,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_items
                     (user_id INTEGER NOT NULL,
                      item_key TEXT NOT NULL,
                      quantity INTEGER NOT NULL DEFAULT 0,
                      PRIMARY KEY(user_id, item_key),
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_item_effects
                     (user_id INTEGER PRIMARY KEY,
                      merge_discounts INTEGER NOT NULL DEFAULT 0,
                      streak_shields INTEGER NOT NULL DEFAULT 0,
                      extra_drop_slots INTEGER NOT NULL DEFAULT 0,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS user_targets
                     (user_id INTEGER PRIMARY KEY,
                      era TEXT,
                      member_code TEXT NOT NULL,
                      rarity TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS trivia_seen
                     (user_id INTEGER NOT NULL,
                      question_id TEXT NOT NULL,
                      difficulty TEXT NOT NULL,
                      seen_at TEXT NOT NULL,
                      PRIMARY KEY (user_id, question_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_biases
                     (user_id INTEGER NOT NULL,
                      member_code TEXT NOT NULL,
                      PRIMARY KEY(user_id, member_code),
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_bios
                     (user_id INTEGER PRIMARY KEY,
                      bio TEXT NOT NULL,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        
        # --- NEW: Market listings table ---
        c.execute('''CREATE TABLE IF NOT EXISTS market_listings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      card_serial TEXT UNIQUE NOT NULL,
                      seller_id INTEGER NOT NULL,
                      price INTEGER NOT NULL,
                      listed_at TEXT NOT NULL,
                      FOREIGN KEY(card_serial) REFERENCES cards(serial),
                      FOREIGN KEY(seller_id) REFERENCES users(user_id))''')
        
        # Create indexes for better performance
        c.execute('''CREATE INDEX IF NOT EXISTS idx_cards_owner 
                     ON cards(owner_id)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_cards_serial 
                     ON cards(serial)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_cooldowns_expires 
                     ON cooldowns(expires_at)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_market_seller 
                     ON market_listings(seller_id)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_trivia_seen_user
                     ON trivia_seen(user_id, difficulty)''')
        
        # Check if columns exist, if not add them (for migration)
        c.execute("PRAGMA table_info(cards)")
        columns = [column[1] for column in c.fetchall()]
        if 'era' not in columns:
            c.execute("ALTER TABLE cards ADD COLUMN era TEXT")
            c.execute("UPDATE cards SET era = 'AAA' WHERE era IS NULL")
        if 'in_binder' not in columns:
            c.execute(
                "ALTER TABLE cards ADD COLUMN in_binder "
                "INTEGER NOT NULL DEFAULT 0"
            )
        c.execute('''CREATE INDEX IF NOT EXISTS idx_cards_binder
                     ON cards(owner_id, in_binder)''')

init_db()

# Cooldown management functions
COOLDOWN_REMINDER_TYPES = {
    "daily": ("Daily", "/daily"),
    "weekly": ("Weekly", "/weekly"),
    "drop": ("Drop", "/drop"),
    "spin": ("Spin", "/spin serial"),
    "claim": ("Claim", None),
    "trivia": ("Trivia", "/trivia"),
}

def schedule_cooldown_reminder(cursor, user_id, cooldown_type, expires_at):
    cursor.execute(
        '''UPDATE cooldown_reminders SET expires_at=?
           WHERE user_id=? AND cooldown_type=? AND enabled=1''',
        (expires_at, user_id, cooldown_type),
    )


def next_local_midnight_timestamp(day=None):
    current_day = (
        datetime.date.fromisoformat(day)
        if day is not None
        else datetime.date.today()
    )
    tomorrow = current_day + datetime.timedelta(days=1)
    return datetime.datetime.combine(tomorrow, datetime.time.min).timestamp()


@tasks.loop(seconds=30)
async def cooldown_reminder_loop():
    now = time.time()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT user_id, cooldown_type, expires_at
                   FROM cooldown_reminders
                   WHERE enabled=1 AND expires_at IS NOT NULL AND expires_at<=?''',
                (now,),
            )
            due_reminders = cursor.fetchall()
    except sqlite3.Error as error:
        print(f"Database error while checking cooldown reminders: {error}")
        return

    for index, (user_id, cooldown_type, expires_at) in enumerate(due_reminders):
        if index:
            await asyncio.sleep(1)

        cooldown_label, command_hint = COOLDOWN_REMINDER_TYPES.get(
            cooldown_type,
            (cooldown_type.replace("_", " ").title(), cooldown_type),
        )
        try:
            user = bot.get_user(user_id) or await bot.fetch_user(user_id)
            reminder_message = f"Your **{cooldown_label}** cooldown has reset."
            if command_hint:
                reminder_message += f" You can use `{command_hint}` again."
            else:
                reminder_message += " You can claim a card again."
            await user.send(
                reminder_message
            )
        except discord.HTTPException as error:
            print(
                f"Could not send {cooldown_type} cooldown reminder "
                f"to user {user_id}: {error}"
            )
            if error.status == 429:
                try:
                    with get_db() as conn:
                        conn.execute(
                            '''UPDATE cooldown_reminders SET expires_at=?
                               WHERE user_id=? AND cooldown_type=? AND expires_at=?''',
                            (time.time() + 60, user_id, cooldown_type, expires_at),
                        )
                except sqlite3.Error as database_error:
                    print(
                        f"Database error while deferring rate-limited "
                        f"{cooldown_type} reminder for user {user_id}: "
                        f"{database_error}"
                    )
                return

        try:
            with get_db() as conn:
                conn.execute(
                    '''UPDATE cooldown_reminders SET expires_at=NULL
                       WHERE user_id=? AND cooldown_type=? AND expires_at=?''',
                    (user_id, cooldown_type, expires_at),
                )
        except sqlite3.Error as error:
            print(
                f"Database error while clearing {cooldown_type} cooldown "
                f"reminder for user {user_id}: {error}"
            )

def check_cooldown(user_id: int, cooldown_type: str, duration: int) -> tuple[bool, int]:
    """
    Check if user is on cooldown.
    Returns (is_on_cooldown, remaining_seconds)
    """
    current_time = time.time()
    
    with get_db() as conn:
        c = conn.cursor()
        
        # Clean up expired cooldowns
        c.execute("DELETE FROM cooldowns WHERE expires_at < ?", (current_time,))
        
        # Check if user has active cooldown
        c.execute('''SELECT expires_at FROM cooldowns 
                     WHERE user_id=? AND cooldown_type=?''', 
                  (user_id, cooldown_type))
        result = c.fetchone()
        
        if result:
            remaining = int(result[0] - current_time)
            if remaining > 0:
                return True, remaining
            else:
                # Cooldown expired, remove it
                c.execute('''DELETE FROM cooldowns 
                            WHERE user_id=? AND cooldown_type=?''',
                         (user_id, cooldown_type))
                return False, 0
        
        return False, 0

def set_cooldown(user_id: int, cooldown_type: str, duration: int):
    """Set a cooldown for a user."""
    expires_at = time.time() + duration
    
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO cooldowns 
                     (user_id, cooldown_type, expires_at) 
                     VALUES (?, ?, ?)''',
                  (user_id, cooldown_type, expires_at))
        schedule_cooldown_reminder(
            c,
            user_id,
            cooldown_type,
            expires_at,
        )

DROP_BOOSTER_DURATION = 3600
DROP_BOOSTER_RARITY_MULTIPLIER = 1.5
SHOP_ITEMS = {
    "drop_booster": {
        "name": "Drop Luck Booster",
        "price": 600,
        "description": "Boosts Rare, Epic, Legendary, and Mythic drop weights for 1 hour.",
    },
    "drop_reset": {
        "name": "Drop Cooldown Reset",
        "price": 200,
        "description": "Reset your active /drop cooldown.",
    },
    "merge_discount": {
        "name": "Merge Discount Token",
        "price": 1200,
        "description": "Use for one merge that consumes 9 cards instead of 10.",
    },
    "streak_shield": {
        "name": "Streak Shield",
        "price": 800,
        "description": "Use to protect your streak from one missed day.",
    },
    "extra_drop_slot": {
        "name": "Extra Drop Slot",
        "price": 400,
        "description": "Use to add one card to your next /drop.",
    },
}
SHOP_ITEM_ALIASES = {
    "booster": "drop_booster",
    "luck_booster": "drop_booster",
    "drop_booster": "drop_booster",
    "drop_luck_booster": "drop_booster",
    "drop": "drop_reset",
    "drop_reset": "drop_reset",
    "drop_cooldown_reset": "drop_reset",
    "merge": "merge_discount",
    "merge_discount": "merge_discount",
    "merge_discount_token": "merge_discount",
    "shield": "streak_shield",
    "streak_shield": "streak_shield",
    "extra_drop": "extra_drop_slot",
    "extra_drop_slot": "extra_drop_slot",
    "drop_slot": "extra_drop_slot",
}

def purchase_shop_item(user_id, item_key):
    item = SHOP_ITEMS[item_key]
    with get_db() as conn:
        c = conn.cursor()
        c.execute("BEGIN IMMEDIATE")
        c.execute("SELECT como FROM users WHERE user_id=?", (user_id,))
        user = c.fetchone()
        if user is None:
            raise ValueError("You don't have a COMO balance yet. Use `/daily` first.")
        if user[0] < item["price"]:
            raise ValueError(
                f"You need {item['price']} COMO to buy the {item['name']}."
            )
        c.execute(
            "UPDATE users SET como=como-? WHERE user_id=?",
            (item["price"], user_id),
        )
        c.execute(
            '''INSERT INTO user_items (user_id, item_key, quantity)
               VALUES (?, ?, 1)
               ON CONFLICT(user_id, item_key)
               DO UPDATE SET quantity=quantity+1''',
            (user_id, item_key),
        )

    return user[0] - item["price"]

def use_shop_item(user_id, item_key):
    item = SHOP_ITEMS[item_key]
    now = time.time()
    with get_db() as conn:
        c = conn.cursor()
        c.execute("BEGIN IMMEDIATE")
        c.execute(
            "SELECT quantity FROM user_items WHERE user_id=? AND item_key=?",
            (user_id, item_key),
        )
        inventory_item = c.fetchone()
        if inventory_item is None or inventory_item[0] <= 0:
            raise ValueError(f"You don't have a **{item['name']}** in `/items`.")

        if item_key == "drop_reset":
            cooldown_type = "drop"
            c.execute(
                '''SELECT expires_at FROM cooldowns
                   WHERE user_id=? AND cooldown_type=?''',
                (user_id, cooldown_type),
            )
            cooldown = c.fetchone()
            if cooldown is None or cooldown[0] <= now:
                raise ValueError("You don't have an active drop cooldown to reset.")
            c.execute(
                "DELETE FROM cooldowns WHERE user_id=? AND cooldown_type=?",
                (user_id, cooldown_type),
            )
            schedule_cooldown_reminder(
                c,
                user_id,
                cooldown_type,
                now,
            )
            confirmation = f"Used a **{item['name']}** and reset your drop cooldown"
        elif item_key == "drop_booster":
            c.execute(
                "SELECT expires_at FROM user_drop_boosters WHERE user_id=?",
                (user_id,),
            )
            booster = c.fetchone()
            booster_expires = max(now, booster[0]) if booster else now
            c.execute(
                '''INSERT OR REPLACE INTO user_drop_boosters (user_id, expires_at)
                   VALUES (?, ?)''',
                (user_id, booster_expires + DROP_BOOSTER_DURATION),
            )
            confirmation = "Used a **Drop Luck Booster**"
        else:
            effect_columns = {
                "merge_discount": "merge_discounts",
                "streak_shield": "streak_shields",
                "extra_drop_slot": "extra_drop_slots",
            }
            effect_column = effect_columns[item_key]
            c.execute(
                f'''INSERT INTO user_item_effects (user_id, {effect_column})
                    VALUES (?, 1)
                    ON CONFLICT(user_id)
                    DO UPDATE SET {effect_column}={effect_column}+1''',
                (user_id,),
            )
            confirmations = {
                "merge_discount": (
                    "Activated a **Merge Discount Token**. "
                    "Your next merge can use 9 cards"
                ),
                "streak_shield": (
                    "Activated a **Streak Shield**. It will automatically protect "
                    "your streak after one missed day"
                ),
                "extra_drop_slot": (
                    "Activated an **Extra Drop Slot** for your next `/drop`"
                ),
            }
            confirmation = confirmations[item_key]

        c.execute(
            '''UPDATE user_items SET quantity=quantity-1
               WHERE user_id=? AND item_key=? AND quantity>0''',
            (user_id, item_key),
        )
        if c.rowcount != 1:
            raise RuntimeError("The item inventory changed while using the item.")

    return confirmation

def has_active_drop_booster(user_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT expires_at FROM user_drop_boosters WHERE user_id=?",
            (user_id,),
        )
        result = c.fetchone()
    return result is not None and result[0] > time.time()

def advance_daily_streak(cursor, user_id, last_daily, today, current_streak):
    if last_daily == today:
        return current_streak, False
    if last_daily == today - datetime.timedelta(days=1):
        return current_streak + 1, False
    if last_daily == today - datetime.timedelta(days=2):
        cursor.execute(
            '''SELECT streak_shields FROM user_item_effects
               WHERE user_id=?''',
            (user_id,),
        )
        shield_row = cursor.fetchone()
        if shield_row and shield_row[0] > 0:
            cursor.execute(
                '''UPDATE user_item_effects
                   SET streak_shields=streak_shields-1
                   WHERE user_id=? AND streak_shields>0''',
                (user_id,),
            )
            if cursor.rowcount == 1:
                return current_streak + 1, True
    return 1, False

# Generate a random card with guaranteed uniqueness
def get_user_target(user_id):
    """Return the user's target preference, if one is set."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT era, member_code, rarity FROM user_targets WHERE user_id=?",
            (user_id,),
        )
        result = c.fetchone()
    if result:
        return {"era": result[0], "member_code": result[1], "rarity": result[2]}
    return None

def generate_card(
    max_attempts=100,
    target=None,
    forced_rarity=None,
    connection=None,
    rarity_boost=False,
):
    """Generate a unique card, optionally targeted or restricted to one rarity."""
    for attempt in range(max_attempts):
        candidates = []
        for rarity, rarity_weight in RARITIES.items():
            if forced_rarity and rarity != forced_rarity:
                continue
            for era, era_data in ERAS.items():
                member_weight = 1 / len(ERAS) / len(era_data["members"])
                for member_code in era_data["members"]:
                    candidates.append((
                        rarity,
                        era,
                        member_code,
                        rarity_weight / sum(RARITIES.values()) * member_weight,
                    ))

        weights = [candidate[3] for candidate in candidates]
        if rarity_boost:
            weights = [
                weight * (
                    DROP_BOOSTER_RARITY_MULTIPLIER
                    if candidate[0] != "Common"
                    else 1
                )
                for candidate, weight in zip(candidates, weights)
            ]
            total_weight = sum(weights)
            weights = [weight / total_weight for weight in weights]
        if target:
            target_indices = [
                index for index, (rarity, era, member_code, _) in enumerate(candidates)
                if member_code == target["member_code"]
                and (target["era"] is None or era == target["era"])
                and (target["rarity"] is None or rarity == target["rarity"])
            ]
            if target_indices:
                target_probability = sum(weights[index] for index in target_indices)
                if target.get("rarity") == "Mythic":
                    # A Mythic target must not increase the overall Mythic drop rate.
                    other_indices = [
                        index for index, candidate in enumerate(candidates)
                        if candidate[0] == "Mythic" and index not in target_indices
                    ]
                    other_probability = sum(weights[index] for index in other_indices)
                    rarity_probability = target_probability + other_probability
                    boosted_probability = min(
                        target_probability + rarity_probability * 0.01,
                        rarity_probability,
                    )
                    remaining_probability = rarity_probability - boosted_probability
                else:
                    boosted_probability = min(target_probability + 0.01, 1.0)
                    other_indices = [
                        index for index in range(len(weights))
                        if index not in target_indices
                    ]
                    other_probability = 1 - target_probability
                    remaining_probability = 1 - boosted_probability
                target_scale = boosted_probability / target_probability
                other_scale = (
                    remaining_probability / other_probability
                    if other_probability else 0
                )
                for index in target_indices:
                    weights[index] *= target_scale
                for index in other_indices:
                    weights[index] *= other_scale

        rarity, era, member_code = random.choices(
            [
                (candidate[0], candidate[1], candidate[2])
                for candidate in candidates
            ],
            weights=weights,
            k=1,
        )[0]
        
        # Generate serial
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        random_part = ''.join(random.choices(chars, k=5))
        serial = f"{member_code}-{random_part}"
        
        # Check if serial already exists
        if connection is None:
            with get_db() as conn:
                c = conn.cursor()
                c.execute("SELECT serial FROM cards WHERE serial=?", (serial,))
                serial_exists = c.fetchone()
        else:
            c = connection.cursor()
            c.execute("SELECT serial FROM cards WHERE serial=?", (serial,))
            serial_exists = c.fetchone()

        if not serial_exists:
            # Serial is unique
            return {
                "serial": serial,
                "member_code": member_code,
                "era": era,
                "name": ERAS[era]["members"][member_code]["name"],
                "full_name": ERAS[era]["members"][member_code]["full_name"],
                "rarity": rarity
            }
    
    # If we somehow can't generate unique serial after max_attempts
    raise RuntimeError("Failed to generate unique card serial")

# Generate multiple unique cards
def generate_unique_cards(count=3, target=None, rarity_boost=False):
    """Generate unique cards, optionally applying a small target bonus."""
    cards = []
    generated_serials = set()
    
    for _ in range(count):
        max_attempts = 100
        for attempt in range(max_attempts):
            card = generate_card(target=target, rarity_boost=rarity_boost)
            if card['serial'] not in generated_serials:
                cards.append(card)
                generated_serials.add(card['serial'])
                break
            
            if attempt == max_attempts - 1:
                raise Exception("Failed to generate unique cards")
    
    return cards

# Get image URL for a card
def get_card_image(era, member_code, rarity, animated=False):
    try:
        member = ERAS[era]["members"][member_code]
        images = member["images"]
        if animated:
            animated_image = member.get("animated_images", {}).get(rarity)
            if animated_image and "example.com" not in animated_image:
                return animated_image
        if rarity == "Mythic" and rarity not in images:
            return images["Legendary"]
        return images[rarity]
    except KeyError:
        return "https://example.com/default_card.jpg"

DROP_CARD_IMAGE_FILENAME = "drop_cards.jpg"

def create_card_image_file(cards):
    """Create a one-row image collage from cards' remote images."""
    card_width, card_height = 240, 340
    gap = 12
    canvas = Image.new(
        "RGB",
        (len(cards) * card_width + max(0, len(cards) - 1) * gap, card_height),
        (35, 35, 45),
    )

    for index, card in enumerate(cards):
        x = index * (card_width + gap)
        try:
            request = Request(
                get_card_image(card["era"], card["member_code"], card["rarity"]),
                headers={"User-Agent": "KotoneBot/1.0"},
            )
            with urlopen(request, timeout=10) as response:
                image_data = response.read(10 * 1024 * 1024 + 1)
            if len(image_data) > 10 * 1024 * 1024:
                raise ValueError("image exceeds the 10 MiB download limit")
            image = Image.open(BytesIO(image_data)).convert("RGB")
            image = ImageOps.contain(
                image,
                (card_width, card_height),
                method=Image.Resampling.LANCZOS,
            )
            canvas.paste(
                image,
                (
                    x + (card_width - image.width) // 2,
                    (card_height - image.height) // 2,
                ),
            )
        except (URLError, OSError, ValueError, Image.DecompressionBombError) as error:
            print(f"Could not load image for card {card['serial']}: {error}")
            draw = ImageDraw.Draw(canvas)
            draw.rectangle(
                (x, 0, x + card_width - 1, card_height - 1),
                fill=(55, 55, 70),
            )
            draw.text((x + 12, card_height // 2), "Card image unavailable", fill="white")

    image_buffer = BytesIO()
    canvas.save(image_buffer, format="JPEG", quality=90)
    image_buffer.seek(0)
    return discord.File(image_buffer, filename=DROP_CARD_IMAGE_FILENAME)

async def create_drop_embed_image(cards):
    return await asyncio.to_thread(create_card_image_file, cards)

COLLECTION_IMAGE_FILENAME = "collection.jpg"
COLLECTION_MEMBERS_PER_PAGE = 12

def create_collection_image_file(era, rarity, owned_member_codes, page=0):
    """Create a rarity-specific era collection collage with missing cards dimmed."""
    members = list(ERAS[era]["members"].items())
    if era in {"ASSEMBLE24", "VV"}:
        start = page * COLLECTION_MEMBERS_PER_PAGE
        members = members[start:start + COLLECTION_MEMBERS_PER_PAGE]
    card_width, card_height = 194, 300
    gap = 10
    columns = min(6 if era in {"ASSEMBLE24", "VV"} else 5, len(members))
    rows = (len(members) + columns - 1) // columns
    canvas_width = columns * card_width + (columns - 1) * gap
    canvas_height = rows * card_height + (rows - 1) * gap
    canvas = Image.new("RGB", (canvas_width, canvas_height), (35, 35, 45))

    def load_member_image(member):
        member_code, _ = member
        try:
            request = Request(
                get_card_image(era, member_code, rarity),
                headers={"User-Agent": "KotoneBot/1.0"},
            )
            with urlopen(request, timeout=10) as response:
                image_data = response.read(10 * 1024 * 1024 + 1)
            if len(image_data) > 10 * 1024 * 1024:
                raise ValueError("image exceeds the 10 MiB download limit")
            image = Image.open(BytesIO(image_data)).convert("RGB")
            image = ImageOps.contain(
                image,
                (card_width, card_height),
                method=Image.Resampling.LANCZOS,
            )
            card_image = Image.new(
                "RGB",
                (card_width, card_height),
                (35, 35, 45),
            )
            card_image.paste(
                image,
                (
                    (card_width - image.width) // 2,
                    (card_height - image.height) // 2,
                ),
            )
            return card_image, None
        except (URLError, OSError, ValueError, Image.DecompressionBombError) as error:
            return None, error

    worker_count = min(6, len(members))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        image_results = executor.map(load_member_image, members)
        for index, ((member_code, _), (card_image, error)) in enumerate(
            zip(members, image_results)
        ):
            column = index % columns
            row = index // columns
            x = column * (card_width + gap)
            y = row * (card_height + gap)
            if error:
                print(
                    f"Could not load collection image for {member_code}: {error}"
                )
                card_image = Image.new(
                    "RGB",
                    (card_width, card_height),
                    (65, 65, 75),
                )
                ImageDraw.Draw(card_image).text(
                    (12, card_height // 2),
                    "Image unavailable",
                    fill="white",
                )

            if member_code not in owned_member_codes:
                muted = ImageOps.grayscale(card_image).convert("RGB")
                overlay = Image.new("RGB", muted.size, (25, 25, 30))
                card_image = Image.blend(muted, overlay, 0.62)

            canvas.paste(card_image, (x, y))

    image_buffer = BytesIO()
    canvas.save(image_buffer, format="JPEG", quality=88)
    image_buffer.seek(0)
    return discord.File(image_buffer, filename=COLLECTION_IMAGE_FILENAME)

async def create_collection_embed_image(era, rarity, owned_member_codes, page=0):
    return await asyncio.to_thread(
        create_collection_image_file,
        era,
        rarity,
        owned_member_codes,
        page,
    )

def create_drop_embed(title, description, cards, show_full_name=False):
    embed = discord.Embed(title=title, description=description, color=0xff6b8b)
    for index, card in enumerate(cards, 1):
        era_name = ERAS[card["era"]]["name"]
        member_name = (
            card["full_name"] if show_full_name else card["name"]
        )
        embed.add_field(
            name=f"Card {index}",
            value=(
                f"Rarity: {card['rarity']}\n"
                f"Member: {member_name}\n"
                f"Era: {era_name}"
            ),
            inline=True,
        )
    if cards:
        embed.set_image(url=f"attachment://{DROP_CARD_IMAGE_FILENAME}")
    return embed

async def replace_remaining_drop_message(message, view):
    async with view.refresh_lock:
        if view.message_replaced:
            return

        with get_db() as conn:
            c = conn.cursor()
            available_cards = []
            for card in view.drop_cards:
                c.execute(
                    "SELECT 1 FROM cards WHERE serial=? AND owner_id IS NULL",
                    (card["serial"],),
                )
                if c.fetchone():
                    available_cards.append(card)

        view.drop_cards = available_cards
        view.message_replaced = True
        new_message = None
        if available_cards:
            embed = create_drop_embed(
                "🎉 Remaining Cards! 🎉",
                "Everyone can now claim the remaining cards!",
                available_cards,
            )
            remaining_image = await create_drop_embed_image(available_cards)
            next_view = View(timeout=30)
            next_view.drop_cards = available_cards
            next_view.refresh_lock = asyncio.Lock()
            next_view.message_replaced = False
            next_view.dropper_id = None

            for index, card in enumerate(available_cards, 1):
                next_view.add_item(
                    ClaimButton(
                        label=f"Claim Card {index}",
                        card_serial=card["serial"],
                    )
                )

            new_message = await message.channel.send(
                embed=embed,
                file=remaining_image,
                view=next_view,
            )

        await message.delete()
        original_message = getattr(view, "original_drop_message", None)
        if original_message is not None:
            await original_message.delete()
            view.original_drop_message = None

        return new_message

# Button for card claiming with race condition protection
class ClaimButton(Button):
    def __init__(self, label, card_serial, style=discord.ButtonStyle.primary):
        super().__init__(label=label, style=style)
        self.card_serial = card_serial
    
    async def callback(self, interaction):
        user_id = interaction.user.id

        dropper_id = getattr(self.view, "dropper_id", None)
        if dropper_id is not None and not self.view.dropper_claimed and user_id != dropper_id:
            await interaction.response.send_message(
                "Only the person who started this drop can claim first.",
                ephemeral=True
            )
            return
        
        # Check claim cooldown
        is_on_cooldown, remaining = check_cooldown(user_id, 'claim', 300)
        if is_on_cooldown:
            await interaction.response.send_message(
                f"You're on cooldown! Please wait {remaining} seconds before claiming another card.",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        claim_completed = False
        try:
            # Use database transaction with exclusive lock to prevent race conditions
            with get_db() as conn:
                c = conn.cursor()
                
                # Start exclusive transaction
                c.execute("BEGIN EXCLUSIVE")
                
                # Check if card is still available (owner_id is NULL)
                c.execute('''SELECT owner_id FROM cards 
                            WHERE serial=? AND owner_id IS NULL''', 
                         (self.card_serial,))
                card = c.fetchone()
                
                if card is not None:
                    # Card is available, claim it
                    c.execute('''UPDATE cards 
                                SET owner_id=?, obtained_at=?, in_binder=0
                                WHERE serial=? AND owner_id IS NULL''',
                             (user_id, str(datetime.datetime.now()), self.card_serial))
                    
                    if c.rowcount > 0:
                        # Successfully claimed
                        c.execute('''SELECT member_code, era, rarity 
                                    FROM cards WHERE serial=?''', 
                                 (self.card_serial,))
                        card_details = c.fetchone()
                        
                        # Commit the transaction
                        conn.commit()
                        claim_completed = True
                        
                        # Set claim cooldown
                        set_cooldown(user_id, 'claim', 300)

                        member_code, era, rarity = card_details
                        claimed_card = {
                            "serial": self.card_serial,
                            "member_code": member_code,
                            "era": era,
                            "rarity": rarity,
                            "name": ERAS[era]["members"][member_code]["name"],
                            "full_name": ERAS[era]["members"][member_code]["full_name"],
                        }
                        claimed_embed = create_drop_embed(
                            "🎉 Card Claimed!",
                            f"{interaction.user.mention} claimed **{rarity} "
                            f"{claimed_card['name']}** ({self.card_serial}).",
                            [claimed_card],
                            show_full_name=True,
                        )
                        claimed_embed.set_image(
                            url=get_card_image(
                                era,
                                member_code,
                                rarity,
                                animated=True,
                            )
                        )
                        await interaction.followup.send(
                            embed=claimed_embed,
                        )
                        
                        self.disabled = True
                        if dropper_id == user_id:
                            self.view.dropper_claimed = True
                            self.view.stop()
                        for child in self.view.children:
                            if dropper_id == user_id:
                                child.disabled = True
                        if dropper_id is None:
                            await replace_remaining_drop_message(
                                interaction.message,
                                self.view,
                            )
                        
                        return
                
                # Card was already claimed
                await interaction.followup.send(
                    "This card has already been claimed!", 
                    ephemeral=True
                )
                
        except sqlite3.Error as e:
            print(f"Database error during claim: {e}")
            await interaction.followup.send(
                "An error occurred while claiming the card. Please try again.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error during claim: {e}")
            await interaction.followup.send(
                (
                    "Your card was claimed, but the drop display could not be updated."
                    if claim_completed
                    else "An error occurred while claiming the card. Please try again."
                ),
                ephemeral=True
            )

# Pagination for inventory
def build_spin_outcomes(wager_rarity):
    reward_counts = SPIN_REWARD_COUNTS[wager_rarity]
    outcomes = [
        rarity
        for rarity, count in reward_counts.items()
        for _ in range(count)
    ]
    outcomes.extend([None] * SPIN_BOMB_SLOTS)
    if len(outcomes) != SPIN_BOARD_SIZE:
        raise RuntimeError(
            f"Spin outcomes must fill exactly {SPIN_BOARD_SIZE} buttons."
        )
    random.shuffle(outcomes)
    return outcomes


class SpinChoiceButton(Button):
    def __init__(self, position):
        super().__init__(
            label="?",
            style=discord.ButtonStyle.secondary,
            row=position // 4,
        )
        self.slot_index = position

    async def callback(self, interaction):
        await self.view.choose(interaction, self.slot_index)


class SpinView(View):
    def __init__(self, ctx, wagered_card, outcomes, spins_remaining):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.wagered_card = wagered_card
        self.outcomes = outcomes
        self.spins_remaining = spins_remaining
        self.resolved = False
        self.lock = asyncio.Lock()
        self.message = None

        for position in range(SPIN_BOARD_SIZE):
            self.add_item(SpinChoiceButton(position))

    def get_embed(self, state="pending"):
        if state == "pending":
            reward_counts = SPIN_REWARD_COUNTS[self.wagered_card["rarity"]]
            rarity_odds = " • ".join(
                f"{rarity}: {reward_counts[rarity]}/{SPIN_BOARD_SIZE}"
                for rarity in RARITIES
            )
            description = (
                f"Wagered: **{self.wagered_card['rarity']} "
                f"{self.wagered_card['name']}** "
                f"(`{self.wagered_card['serial']}`) — consumed\n"
                f"Choose one hidden button. An explosion wins nothing; otherwise, "
                f"you get a new card matching the revealed rarity.\n"
                f"This board expires in 3 minutes; the wager is already consumed.\n"
                f"💥 Explosion: {SPIN_BOMB_SLOTS}/{SPIN_BOARD_SIZE}\n"
                f"{rarity_odds}\n"
                f"Spins remaining today: **{self.spins_remaining}**"
            )
            title = "🎰 Card Spin"
        else:
            description = (
                "The cards are spinning... Will you win a new card, "
                "or hit an explosion? ✨"
            )
            title = "🎰 The spin is in motion..."
        return discord.Embed(title=title, description=description, color=0xff6b8b)

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Only the person who started this spin can choose a button.",
                ephemeral=True,
            )
            return False
        return True

    async def choose(self, interaction, position):
        await interaction.response.defer()
        async with self.lock:
            if self.resolved:
                await interaction.followup.send(
                    "This spin has already ended.", ephemeral=True
                )
                return
            self.resolved = True
            result = self.outcomes[position]
            reward_card = None

            if result is not None:
                try:
                    with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute("BEGIN IMMEDIATE")
                        reward_card = generate_card(
                            forced_rarity=result,
                            connection=conn,
                        )
                        cursor.execute(
                            '''INSERT INTO cards
                               (serial, member_code, era, rarity, owner_id, obtained_at)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (
                                reward_card["serial"],
                                reward_card["member_code"],
                                reward_card["era"],
                                reward_card["rarity"],
                                self.ctx.author.id,
                                str(datetime.datetime.now()),
                            ),
                        )
                except sqlite3.Error as error:
                    self.resolved = False
                    print(f"Database error while awarding spin card: {error}")
                    await interaction.followup.send(
                        "Your spin reward couldn't be saved. Please choose a button again.",
                        ephemeral=True,
                    )
                    return
                except RuntimeError as error:
                    self.resolved = False
                    print(f"Could not generate spin reward: {error}")
                    await interaction.followup.send(
                        "Your spin reward couldn't be generated. Please choose a button again.",
                        ephemeral=True,
                    )
                    return

            for button in self.children:
                button.disabled = True
            selected_button = self.children[position]
            selected_button.label = "..."
            await interaction.message.edit(
                embed=self.get_embed("spinning"),
                view=self,
            )
            await asyncio.sleep(2)
            if result is None:
                result_embed = discord.Embed(
                    title="💥 Oh no! Your spin exploded!",
                    description=(
                        "That was the unlucky spot! Your wagered card "
                        f"(`{self.wagered_card['serial']}`) is gone, "
                        "and you didn't win a new card. Better luck next time!"
                    ),
                    color=0xff6b8b,
                )
            else:
                result_embed = create_drop_embed(
                    "🎉 Card Spin Successful!",
                    (
                        f"{self.ctx.author.mention} won a **{result} "
                        f"{reward_card['name']}** ({reward_card['serial']})!\n"
                        f"Wagered card `{self.wagered_card['serial']}` was consumed."
                    ),
                    [reward_card],
                    show_full_name=True,
                )
                result_embed.set_image(
                    url=get_card_image(
                        reward_card["era"],
                        reward_card["member_code"],
                        reward_card["rarity"],
                        animated=True,
                    )
                )
            for index, button in enumerate(self.children):
                outcome = self.outcomes[index]
                button.label = "💥" if outcome is None else outcome
                button.style = discord.ButtonStyle.secondary
            selected_button.style = (
                discord.ButtonStyle.danger
                if result is None
                else discord.ButtonStyle.success
            )
            await interaction.message.edit(embed=result_embed, view=self)

    async def on_timeout(self):
        async with self.lock:
            if self.resolved:
                return
            self.resolved = True
            for button in self.children:
                button.disabled = True
            if self.message is not None:
                embed = self.get_embed()
                embed.description += (
                    "\n\n⌛ Spin expired. The wagered card was consumed."
                )
                await self.message.edit(embed=embed, view=self)


def start_card_spin(user_id, serial):
    today = datetime.date.today().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            '''SELECT member_code, era, rarity, in_binder
               FROM cards WHERE serial=? AND owner_id=?''',
            (serial, user_id),
        )
        card_row = cursor.fetchone()
        if card_row is None:
            raise ValueError("You don't own a card with that serial anymore.")
        member_code, era, rarity, in_binder = card_row
        if in_binder:
            raise ValueError(
                "That card is in your binder. Remove it with "
                "`/binder remove` before spinning."
            )
        if rarity not in SPIN_REWARD_COUNTS:
            raise ValueError("That card has an unsupported rarity and can't be spun.")

        cursor.execute(
            "SELECT 1 FROM market_listings WHERE card_serial=?",
            (serial,),
        )
        if cursor.fetchone():
            raise ValueError(
                "Unlist that card from the market before using it for a spin."
            )

        cursor.execute(
            "SELECT spin_date, spins FROM spin_usage WHERE user_id=?",
            (user_id,),
        )
        usage_row = cursor.fetchone()
        spins_used = (
            usage_row[1]
            if usage_row and usage_row[0] == today
            else 0
        )
        if spins_used >= SPIN_DAILY_LIMIT:
            raise ValueError(
                f"You've used all **{SPIN_DAILY_LIMIT} spins** for today. "
                "Your limit resets at local midnight."
            )

        member = ERAS[era]["members"][member_code]
        wagered_card = {
            "serial": serial,
            "member_code": member_code,
            "era": era,
            "rarity": rarity,
            "name": member["name"],
            "full_name": member["full_name"],
        }
        outcomes = build_spin_outcomes(rarity)
        cursor.execute(
            "DELETE FROM cards WHERE serial=? AND owner_id=?",
            (serial, user_id),
        )
        if cursor.rowcount != 1:
            raise RuntimeError("The wagered card changed before the spin started.")

        spins_used += 1
        cursor.execute(
            '''INSERT INTO spin_usage (user_id, spin_date, spins)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   spin_date=excluded.spin_date,
                   spins=excluded.spins''',
            (user_id, today, spins_used),
        )
        if spins_used == SPIN_DAILY_LIMIT:
            reset_at = next_local_midnight_timestamp(today)
            cursor.execute(
                '''INSERT OR REPLACE INTO cooldowns
                   (user_id, cooldown_type, expires_at)
                   VALUES (?, 'spin', ?)''',
                (user_id, reset_at),
            )
            schedule_cooldown_reminder(
                cursor,
                user_id,
                "spin",
                reset_at,
            )

    return wagered_card, outcomes, SPIN_DAILY_LIMIT - spins_used


class SpinConfirmationView(View):
    def __init__(self, ctx, wagered_card, spins_remaining):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.wagered_card = wagered_card
        self.spins_remaining = spins_remaining
        self.resolved = False
        self.lock = asyncio.Lock()
        self.message = None

    def get_embed(self):
        rarity = self.wagered_card["rarity"]
        reward_counts = SPIN_REWARD_COUNTS[rarity]
        odds = "\n".join(
            f"**{reward_rarity}:** {count}/{SPIN_BOARD_SIZE} "
            f"({count / SPIN_BOARD_SIZE * 100:g}%)"
            for reward_rarity, count in reward_counts.items()
        )
        explosion_chance = SPIN_BOMB_SLOTS / SPIN_BOARD_SIZE * 100
        embed = discord.Embed(
            title="Confirm Card Spin",
            description=(
                f"Are you sure you want to spin "
                f"**{rarity} {self.wagered_card['name']}** "
                f"(`{self.wagered_card['serial']}`)?\n"
                "Confirming permanently consumes this card, even if you hit "
                "the explosion or the spin board expires.\n\n"
                f"**Reward chances for a {rarity} wager:**\n{odds}\n"
                f"**Explosion (no reward):** "
                f"{SPIN_BOMB_SLOTS}/{SPIN_BOARD_SIZE} ({explosion_chance:g}%)\n\n"
                f"You'll have 3 minutes to choose from the 4×4 board. "
                f"Spins remaining today after this: **{self.spins_remaining}**."
            ),
            color=0xff6b8b,
        )
        embed.set_thumbnail(
            url=get_card_image(
                self.wagered_card["era"],
                self.wagered_card["member_code"],
                rarity,
            )
        )
        return embed

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Only the person who started this spin can confirm it.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Confirm Spin", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction, button):
        await interaction.response.defer()
        async with self.lock:
            if self.resolved:
                await interaction.followup.send(
                    "This spin confirmation has already ended.",
                    ephemeral=True,
                )
                return
            self.resolved = True
            await interaction.message.edit(
                content="Preparing your spin... ✨",
                embed=None,
                view=None,
            )
            await asyncio.sleep(1.5)
            try:
                wagered_card, outcomes, spins_remaining = start_card_spin(
                    self.ctx.author.id,
                    self.wagered_card["serial"],
                )
            except ValueError as error:
                await interaction.followup.send(str(error))
                self.stop()
                return
            except sqlite3.Error as error:
                print(f"Database error while confirming spin: {error}")
                await interaction.followup.send(
                    "The spin couldn't be started due to a database error. "
                    "Your card was not consumed."
                )
                self.stop()
                return
            except (KeyError, RuntimeError) as error:
                print(f"Could not start confirmed spin: {error}")
                await interaction.followup.send(
                    "The spin couldn't be started. Your card was not consumed."
                )
                self.stop()
                return

            spin_view = SpinView(
                self.ctx,
                wagered_card,
                outcomes,
                spins_remaining,
            )
            spin_view.message = await interaction.message.edit(
                content=None,
                embed=spin_view.get_embed(),
                view=spin_view,
            )
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction, button):
        await interaction.response.defer()
        async with self.lock:
            if self.resolved:
                await interaction.followup.send(
                    "This spin confirmation has already ended.",
                    ephemeral=True,
                )
                return
            self.resolved = True
            await interaction.message.edit(
                content="Spin cancelled. Your card was not consumed.",
                embed=None,
                view=None,
            )
            self.stop()

    async def on_timeout(self):
        if self.resolved:
            return
        self.resolved = True
        for button in self.children:
            button.disabled = True
        if self.message is not None:
            await self.message.edit(
                content="Spin confirmation expired. Your card was not consumed.",
                embed=None,
                view=self,
            )


class InventoryView(View):
    def __init__(
        self,
        cards,
        user_display_name,
        ctx,
        selected_member_codes=None,
        filter_labels=None,
    ):
        super().__init__(timeout=180)  # 3 minute timeout
        self.cards = cards
        self.user_display_name = user_display_name
        self.ctx = ctx
        self.selected_member_codes = set(selected_member_codes or ())
        self.filter_labels = filter_labels or []
        self.current_page = 0
        self.items_per_page = 5
        member_select = InventoryMemberSelect(self)
        if member_select.options:
            self.add_item(member_select)
        self.update_buttons()

    def get_filtered_cards(self):
        if not self.selected_member_codes:
            return self.cards
        return [
            card for card in self.cards
            if card[1] in self.selected_member_codes
        ]

    def update_buttons(self):
        filtered_cards = self.get_filtered_cards()
        self.total_pages = max(
            1,
            (len(filtered_cards) + self.items_per_page - 1)
            // self.items_per_page,
        )
        for child in self.children:
            if isinstance(child, Button) and child.label == "◀ Previous":
                child.disabled = self.current_page == 0
            elif isinstance(child, Button) and child.label == "Next ▶":
                child.disabled = self.current_page >= self.total_pages - 1

    def get_embed(self):
        filtered_cards = self.get_filtered_cards()
        filter_labels = list(self.filter_labels)
        if self.selected_member_codes:
            member_names = [
                S_MEMBERS[member_code]["name"]
                for member_code in S_ORDER
                if member_code in self.selected_member_codes
            ]
            filter_labels.append("members " + ", ".join(member_names))
        filter_description = (
            " • Filters: " + ", ".join(filter_labels)
            if filter_labels
            else ""
        )
        embed = discord.Embed(
            title=f"{self.user_display_name}'s Inventory",
            description=(
                f"Page {self.current_page + 1}/{self.total_pages} • "
                f"Total Cards: {len(filtered_cards)}{filter_description}"
            ),
            color=0xff6b8b
        )
        inventory_owner = self.ctx.author
        if self.ctx.message.mentions:
            inventory_owner = self.ctx.message.mentions[0]
        embed.set_author(
            name=self.user_display_name,
            icon_url=inventory_owner.display_avatar.url,
        )
        
        start_idx = self.current_page * self.items_per_page
        end_idx = min(
            (self.current_page + 1) * self.items_per_page,
            len(filtered_cards),
        )
        
        for i in range(start_idx, end_idx):
            serial, member_code, era, rarity, obtained_at, in_binder = (
                filtered_cards[i]
            )
            
            try:
                member_name = ERAS[era]['members'][member_code]['name']
                era_name = ERAS[era]['name']
            except KeyError:
                member_name = "Unknown"
                era_name = "Unknown"
            
            embed.add_field(
                name=f"{'📌 ' if in_binder else ''}{serial}",
                value=(
                    f"Member: {member_name}\nEra: {era_name}\n"
                    f"Rarity: {rarity}\n"
                    f"Binder: {'Protected' if in_binder else 'No'}\n"
                    f"Obtained: {obtained_at[:10] if obtained_at else 'Unknown'}"
                ),
                inline=False
            )

        if not filtered_cards:
            embed.add_field(
                name="No matching cards",
                value="You don't have cards matching the selected filters.",
                inline=False,
            )

        return embed
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return
        
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return
        
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)


class InventoryMemberSelect(discord.ui.Select):
    def __init__(self, inventory_view):
        self.inventory_view = inventory_view
        selected_codes = inventory_view.selected_member_codes
        options = [
            discord.SelectOption(
                label=member_data["name"],
                value=member_code,
                default=member_code in selected_codes,
            )
            for member_code, member_data in S_MEMBERS.items()
        ]
        super().__init__(
            placeholder="Filter by one or more members",
            min_values=0,
            max_values=len(options),
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.inventory_view.ctx.author.id:
            await interaction.response.send_message(
                "Only the person who opened this inventory can change its filters.",
                ephemeral=True,
            )
            return

        self.inventory_view.selected_member_codes = set(self.values)
        for option in self.options:
            option.default = option.value in self.inventory_view.selected_member_codes
        self.inventory_view.current_page = 0
        self.inventory_view.update_buttons()
        await interaction.response.edit_message(
            embed=self.inventory_view.get_embed(),
            view=self.inventory_view,
        )

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














MERGE_UPGRADES = {
    "Common": "Rare",
    "Rare": "Epic",
    "Epic": "Legendary",
}

def get_merge_selection(cursor, user_id, serials):
    required_count = len(serials)
    if required_count not in {9, 10}:
        raise ValueError("A merge requires 10 cards, or 9 with an activated Merge Discount Token.")
    if required_count == 9:
        cursor.execute(
            '''SELECT merge_discounts FROM user_item_effects
               WHERE user_id=?''',
            (user_id,),
        )
        discount = cursor.fetchone()
        if discount is None or discount[0] <= 0:
            raise ValueError(
                "You need to activate a Merge Discount Token with `/use` and `merge` "
                "before merging 9 cards."
            )

    placeholders = ",".join("?" for _ in serials)
    cursor.execute(
        f'''SELECT serial, member_code, era, rarity, owner_id, in_binder
            FROM cards WHERE serial IN ({placeholders})''',
        serials,
    )
    cards_by_serial = {row[0]: row for row in cursor.fetchall()}
    if len(cards_by_serial) != required_count:
        raise ValueError("One or more of those card serials could not be found.")

    selected_cards = [cards_by_serial[serial] for serial in serials]
    if any(card[4] != user_id for card in selected_cards):
        raise ValueError("You can only merge cards that you own.")
    binder_serials = [card[0] for card in selected_cards if card[5]]
    if binder_serials:
        raise ValueError(
            "Remove these cards from your binder before merging: "
            + ", ".join(f"`{serial}`" for serial in binder_serials)
        )

    selected_rarity = selected_cards[0][3]
    if any(card[3] != selected_rarity for card in selected_cards):
        raise ValueError(f"All {required_count} cards must have the same rarity.")
    if selected_rarity not in MERGE_UPGRADES:
        raise ValueError(
            f"{selected_rarity} cards cannot be merged into a higher rarity."
        )

    cursor.execute(
        f'''SELECT card_serial FROM market_listings
            WHERE card_serial IN ({placeholders})''',
        serials,
    )
    listed_serials = [row[0] for row in cursor.fetchall()]
    if listed_serials:
        raise ValueError(
            "Unlist these cards before merging them: "
            + ", ".join(f"`{serial}`" for serial in listed_serials)
        )

    return selected_rarity, selected_cards

def merge_owned_cards(user_id, serials):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        selected_rarity, _ = get_merge_selection(cursor, user_id, serials)
        if len(serials) == 9:
            cursor.execute(
                '''UPDATE user_item_effects
                   SET merge_discounts=merge_discounts-1
                   WHERE user_id=? AND merge_discounts>0''',
                (user_id,),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("The Merge Discount Token is no longer available.")
        merged_card = generate_card(
            forced_rarity=MERGE_UPGRADES[selected_rarity],
            connection=conn,
        )
        delete_placeholders = ",".join("?" for _ in serials)
        cursor.execute(
            f'''DELETE FROM cards
                WHERE owner_id=? AND serial IN ({delete_placeholders})''',
            [user_id, *serials],
        )
        if cursor.rowcount != len(serials):
            raise RuntimeError("The selected cards changed during the merge.")

        cursor.execute(
            '''INSERT INTO cards
               (serial, member_code, era, rarity, owner_id, obtained_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                merged_card["serial"],
                merged_card["member_code"],
                merged_card["era"],
                merged_card["rarity"],
                user_id,
                str(datetime.datetime.now()),
            ),
        )

    return merged_card

class MergeConfirmationView(View):
    def __init__(self, user_id, serials):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.serials = serials
        self.message = None

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Only the person who started this merge can confirm it.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message is not None:
            await self.message.edit(
                content="Merge confirmation expired. No cards were changed.",
                embed=None,
                view=self,
            )

    @discord.ui.button(label="Confirm Merge", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction, button):
        await interaction.response.edit_message(
            content="Merging...",
            embed=None,
            view=None,
        )
        await asyncio.sleep(3)
        try:
            merged_card = merge_owned_cards(self.user_id, self.serials)
        except ValueError as error:
            await interaction.followup.send(str(error))
            self.stop()
            return
        except sqlite3.Error as error:
            print(f"Database error during card merge: {error}")
            await interaction.followup.send(
                "The merge couldn't be completed due to a database error."
            )
            self.stop()
            return
        except RuntimeError as error:
            print(f"Card merge failed: {error}")
            await interaction.followup.send(
                "The merge couldn't be completed. Please try again."
            )
            self.stop()
            return

        rarity = merged_card["rarity"]
        era = merged_card["era"]
        member_code = merged_card["member_code"]
        result_embed = create_drop_embed(
            "🎉 Card Merged!",
            (
                f"Congratulations, {interaction.user.mention}! You earned "
                f"**{rarity} {merged_card['name']}** "
                f"({merged_card['serial']})."
            ),
            [merged_card],
            show_full_name=True,
        )
        result_embed.set_image(
            url=get_card_image(
                era,
                member_code,
                rarity,
                animated=True,
            )
        )
        await interaction.followup.send(embed=result_embed)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction, button):
        await interaction.response.edit_message(
            content="Merge cancelled. No cards were changed.",
            embed=None,
            view=None,
        )
        self.stop()





def create_collection_embed(
    user,
    era,
    rarity,
    owned_count,
    total_count,
    page=1,
    total_pages=1,
    spare_count=0,
):
    embed = discord.Embed(
        description=(
            f"**{user.name}'s {ERAS[era]['name']} ({rarity}) Collection**"
        ),
        color=0xff6b8b,
    )
    embed.set_author(
        name="Collection",
        icon_url=user.display_avatar.url,
    )
    page_status = (
        f"Page {page}/{total_pages} • "
        if total_pages > 1
        else ""
    )
    embed.description = (
        f"{page_status}{owned_count}/{total_count} Cards\n\n"
        f"**{user.name}'s {ERAS[era]['name']} ({rarity}) Collection:**"
    )
    if owned_count == total_count:
        footer = "Yay, you have collected all cards!"
    else:
        footer = (
            f"You are missing {total_count - owned_count} cards. "
            "Keep playing!"
        )
    if spare_count:
        embed.add_field(
            name="Duplicates",
            value=(
                f"You have **{spare_count} spare {rarity} "
                f"{'card' if spare_count == 1 else 'cards'}**. "
                f"Use `/dupes era:{era} rarity:{rarity}` to view their "
                "serials."
            ),
            inline=False,
        )
    embed.set_footer(text=footer)
    embed.set_image(url=f"attachment://{COLLECTION_IMAGE_FILENAME}")
    return embed

class CollectionRarityButton(Button):
    def __init__(self, rarity, selected=False):
        super().__init__(
            label=rarity,
            style=(
                discord.ButtonStyle.success
                if selected
                else discord.ButtonStyle.secondary
            ),
        )
        self.rarity = rarity

    async def callback(self, interaction):
        await self.view.show_rarity(interaction, self.rarity)


class CollectionPageButton(Button):
    def __init__(self, label, page_delta):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            row=1,
        )
        self.page_delta = page_delta

    async def callback(self, interaction):
        await self.view.show_page(
            interaction,
            self.view.current_page + self.page_delta,
        )


class CollectionView(View):
    def __init__(
        self,
        user,
        era,
        owned_by_rarity,
        default_rarity,
        spare_by_rarity=None,
    ):
        super().__init__(timeout=180)
        self.user = user
        self.era = era
        self.owned_by_rarity = owned_by_rarity
        self.spare_by_rarity = spare_by_rarity or {}
        self.message = None
        self.selected_rarity = default_rarity
        self.current_page = 0
        self.total_pages = (
            (
                len(ERAS[era]["members"])
                + COLLECTION_MEMBERS_PER_PAGE
                - 1
            ) // COLLECTION_MEMBERS_PER_PAGE
            if era in {"ASSEMBLE24", "VV"}
            else 1
        )
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        for rarity in RARITIES:
            self.add_item(
                CollectionRarityButton(
                    rarity,
                    selected=rarity == self.selected_rarity,
                )
            )
        if self.total_pages > 1:
            previous_button = CollectionPageButton("◀ Previous", -1)
            previous_button.disabled = self.current_page == 0
            self.add_item(previous_button)

            next_button = CollectionPageButton("Next ▶", 1)
            next_button.disabled = self.current_page >= self.total_pages - 1
            self.add_item(next_button)

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "Only the person who opened this collection can change its rarity.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message is not None:
            await self.message.edit(view=self)

    async def show_rarity(self, interaction, rarity):
        self.selected_rarity = rarity
        await self.update_collection(interaction)

    async def show_page(self, interaction, page):
        if not 0 <= page < self.total_pages:
            await interaction.response.defer()
            return
        self.current_page = page
        await self.update_collection(interaction)

    async def update_collection(self, interaction):
        await interaction.response.defer()
        try:
            owned_codes = self.owned_by_rarity[self.selected_rarity]
            image = await create_collection_embed_image(
                self.era,
                self.selected_rarity,
                owned_codes,
                self.current_page,
            )
            embed = create_collection_embed(
                self.user,
                self.era,
                self.selected_rarity,
                len(owned_codes),
                len(ERAS[self.era]["members"]),
                self.current_page + 1,
                self.total_pages,
                self.spare_by_rarity.get(self.selected_rarity, 0),
            )
            self.update_buttons()
            await interaction.edit_original_response(
                embed=embed,
                attachments=[image],
                view=self,
            )
        except Exception as error:
            print(f"Error while updating collection rarity: {error}")
            await interaction.followup.send(
                "An error occurred while updating your collection.",
                ephemeral=True,
            )






def format_target(target):
    member_data = ERAS.get(target["era"], {}).get("members", {}).get(
        target["member_code"]
    )
    if member_data is None:
        member_data = next(
            (
                era_data["members"][target["member_code"]]
                for era_data in ERAS.values()
                if target["member_code"] in era_data["members"]
            ),
            None,
        )
    if member_data is None:
        return "Unknown member"

    parts = []
    if target["rarity"]:
        parts.append(target["rarity"])
    parts.append(member_data["full_name"])
    if target["era"]:
        parts.append(ERAS[target["era"]]["name"])
    else:
        parts.append("any era")
    return " ".join(parts)

def parse_biases(query):
    """Resolve bias names, short names, and member codes in the supplied order."""
    aliases = {}
    for index, member_code in enumerate(S_ORDER, start=1):
        member_data = S_MEMBERS[member_code]
        for alias in (
            member_code,
            f"s{index}",
            member_data["name"],
            member_data["full_name"],
        ):
            normalized_alias = alias.casefold().split()
            aliases[tuple(normalized_alias)] = member_code

    tokens = query.casefold().replace(",", " ").split()
    matched_codes = []
    position = 0
    while position < len(tokens):
        matches = [
            (alias_tokens, member_code)
            for alias_tokens, member_code in aliases.items()
            if tokens[position:position + len(alias_tokens)] == list(alias_tokens)
        ]
        if not matches:
            raise ValueError(f"Couldn't identify bias name starting with `{tokens[position]}`.")

        alias_tokens, member_code = max(matches, key=lambda match: len(match[0]))
        matched_codes.append(member_code)
        position += len(alias_tokens)

    return sorted(set(matched_codes), key=S_ORDER.index)







HELP_CATEGORIES = (
    ("💰 Economy", ("daily", "weekly", "balance", "shop", "items", "use", "transfer")),
    (
        "🎴 Cards",
        (
            "drop", "spin", "inventory", "view", "merge", "collection", "dupes",
            "binder", "give", "target", "bias", "bio", "profile", "stats",
        ),
    ),
    ("🏪 Market", ("market", "list", "unlist", "buy")),
    (
        "🎮 Fun & utility",
        (
            "help", "cooldown", "remind", "afk", "minigame", "trivia",
            "8ball", "choose", "rob",
        ),
    ),
)


class HelpView(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page == len(HELP_CATEGORIES) - 1

    def get_embed(self):
        category_name, command_names = HELP_CATEGORIES[self.current_page]
        command_list = []
        for command_name in command_names:
            command = SLASH_COMMANDS.get(command_name)
            if command is None:
                continue
            description = command.description or "No description available."
            if isinstance(command, app_commands.Group):
                command_list.extend(
                    f"`/{command.name} {subcommand.name}` — "
                    f"{subcommand.description or description}"
                    for subcommand in command.commands
                )
            else:
                aliases = SLASH_COMMAND_ALIASES.get(command.name, ())
                alias_text = (
                    f" (aliases: {', '.join(f'/{alias}' for alias in aliases)})"
                    if aliases
                    else ""
                )
                command_list.append(
                    f"`/{command.name}`{alias_text} — {description}"
                )

        embed = discord.Embed(
            title=f"🦭 Commands • {category_name}",
            description="Use `/help` with a command name to view its details.",
            color=0xff6b8b,
        )
        embed.add_field(
            name="Available commands",
            value="\n".join(command_list) or "No commands available.",
            inline=False,
        )
        embed.set_footer(
            text=f"Page {self.current_page + 1}/{len(HELP_CATEGORIES)}"
        )
        return embed

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "This is not your help menu!", ephemeral=True
            )
            return
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "This is not your help menu!", ephemeral=True
            )
            return
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)



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