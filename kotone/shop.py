import datetime
import time
from kotone.cooldowns import (
    schedule_cooldown_reminder,
)
from kotone.db import (
    get_db,
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
