import sqlite3
from contextlib import contextmanager


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
        
        # Per-card skill points and training history
        c.execute('''CREATE TABLE IF NOT EXISTS card_skill_points
                     (card_serial TEXT PRIMARY KEY,
                      skill TEXT NOT NULL,
                      points INTEGER NOT NULL,
                      training_sessions INTEGER NOT NULL DEFAULT 0,
                      performances INTEGER NOT NULL DEFAULT 0,
                      last_trained REAL,
                      FOREIGN KEY(card_serial) REFERENCES cards(serial))''')

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
