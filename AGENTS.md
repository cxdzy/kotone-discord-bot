# AGENTS.md

Guide for AI coding assistants working on this repo. Read this first and open only the files a task needs. Do not scan the whole repo.

## What this is

A Discord bot (Python, discord.py 2.7.1) for a tripleS card collecting game. Players drop, merge, trade, train and perform cards with slash commands. Data lives in SQLite (`kpop_cards.db`). The bot runs in Docker on a server and on a developer's Windows PC.

- Libraries are pinned in `requirements.txt` (discord.py 2.7.1, Pillow 12.3.0, python-dotenv 1.2.4).
- Local Python is 3.10, the server runs 3.12. Write code that works on both.
- The only environment variable the code reads is `DISCORD_TOKEN` (in `bot.py`). Locally it comes from `.env`. On the server `compose.yml` passes it with `env_file`.

## Layout

| Path | What is in it |
|---|---|
| `bot.py` | Short entry file (about 55 lines). Loads `.env`, imports `kotone.client`, `kotone.events` and `features`, then runs the bot. Also holds the Windows single-instance lock. Do not add logic here. |
| `kotone/client.py` | Bot client (`bot`), `slash_command` decorator, command registries |
| `kotone/config.py` | Shared constants: rarities, spin limits, member lists, minigames |
| `kotone/db.py` | `get_db`, `init_db` and the table migrations |
| `kotone/cooldowns.py` | Cooldowns and the reminder loop |
| `kotone/shop.py` | Shop items, boosters, daily streak |
| `kotone/game.py` | Card generation, spin, merge, targets |
| `kotone/images.py` | Card images, collages, drop embeds |
| `kotone/views.py` | Buttons, menus, help, and the collection embed builders (large file, open only if the task is about views) |
| `kotone/events.py` | `on_ready`, `on_message`, error handler |
| `features/*.py` | Slash commands: binder, cards, economy, market, training, trivia, fun_utility |
| `features/__init__.py` | Imports every features file. It sets the command registration order. |
| `eras.py` | Card data and image links (large data file, search it, do not read it whole) |
| `triples_trivia.json` | Trivia questions |
| `Start Bot.bat`, `.env.example` | Windows start script, and the list of required environment variable names |
| `ci/smoke_test.py`, `.github/workflows/ci.yml` | CI checks |
| `Dockerfile`, `compose.yml`, `.dockerignore` | Server hosting. Do not change without asking. |

## Where new code goes

| Task | Put it in |
|---|---|
| New slash command | `features/`. A new file must also be added to the import line in `features/__init__.py`, which sets command order. |
| New constant | `kotone/config.py` if several modules use it. Otherwise next to the code that uses it (for example `SHOP_ITEMS` in `kotone/shop.py`). |
| New database table or column | `kotone/db.py`, inside `init_db` |
| Game logic | `kotone/game.py` |
| Button or menu | `kotone/views.py` |
| Image code | `kotone/images.py` |
| New card or era | `eras.py` |

## Code rules

- Use explicit imports. Never use `from x import *`.
- Imports flow one way. `client`, `config`, `db` and `images` import nothing else from `kotone/`. `cooldowns` uses `client` and `db`. `shop` uses `cooldowns` and `db`. `game` uses `config`, `cooldowns`, `db` and `shop`. `views` uses `client`, `config`, `cooldowns`, `db`, `game` and `images`. `events` uses `client`, `cooldowns` and `db`. Nothing in `kotone/` may import `bot` or `features`.
- Commands are registered with the `slash_command` decorator from `kotone/client.py`. Each alias is a separate top-level command, and the binder group counts once (its subcommands do not). The bot has 50 commands today, and CI fails if the count drops.
- Shared state: there is one client (`bot` in `kotone/client.py`) and two shared registries (`SLASH_COMMANDS`, `SLASH_COMMAND_ALIASES`). `features/binder.py` adds its group to `SLASH_COMMANDS` by hand. The reminder loop starts in `on_ready` (`kotone/events.py`).
- Keep `load_dotenv()` in `bot.py`. It searches for `.env` starting from the folder of the file that calls it.
- Keep the existing line endings (CRLF) and style. Do not reformat or reorder code you were not asked to change.
- Do not move or rename code unless the task is a restructure.
- Open data files with a path built from `Path(__file__)`, never a bare file name. The live bot runs from `/app/data`, not from the code folder.
- Do not create a top-level folder named `data`. `.dockerignore` excludes `data/`, `*.db` files and `Start Bot.bat` from the server image.

## Database rules

- The database path is the relative name `kpop_cards.db`, resolved from the working directory. On the server that is the `/app/data` volume, and the container runs as a non-root user (UID 10001).
- Importing `kotone.db` runs `init_db()` and creates `kpop_cards.db` (plus `-wal` and `-shm` files) in the current folder. Run scripts and tests from a temporary folder.
- Tables are created with `CREATE TABLE IF NOT EXISTS`. Adding a column to an existing table needs a guarded `ALTER TABLE` (check `PRAGMA table_info` first), so a second start does not crash.
- Never use `DROP TABLE` or a `DELETE` without a `WHERE`. Tell the owner about any schema change in the pull request, because the live database needs the same change.
- Never read, print, commit or delete a `.db` file.

## Images

- Card images must be hosted on the project's Supabase bucket (`kotone bot`).
- Never use `file:///`, `C:\`, `example.com`, or Discord links (`cdn.discordapp.com`, `media.discordapp.net`). Discord links expire.
- `get_card_image` ignores `example.com` placeholders for animated images. Do not remove that check.
- Existing data does not follow these rules yet. `eras.py` still has 65 expired Discord links and 61 `example.com` placeholders (at the time of writing), and `get_card_image` falls back to an `example.com` URL for unknown cards. `kotone/events.py` also has hard-coded Discord, Tenor and Klipy links. Replace links when you touch a card. Do not copy them.

## Run and test locally

1. Create `.env` with `DISCORD_TOKEN=` set to a test bot token. Never use the live token.
2. `python -m pip install -r requirements.txt`
3. Start with `Start Bot.bat` or `python bot.py`. It should print "Synced 50 slash commands".
4. Check changed `.py` files with `python -m py_compile <file>`.

## Git rules

- Never push to `feature/daeyeyo`. Work on a new branch from the latest `feature/daeyeyo` of `daeyeyo/kotone-discord-bot` (`origin` in the owner's clone, `upstream` in a fork) and open a pull request into it.
- Never create or push tags. Tags starting with `v` trigger a production deploy.
- Never commit `.env`, any `.db` file, or a token. Stage exact file names, not `git add .`.
- Never force push, `reset --hard`, `clean` or `rebase`.
- Commit message: a short first line starting with a verb, then `Database: yes/no`, `New library: yes/no`, `Commands changed: yes/no`, `Tested: how`.
- Pull requests need a short description: what changed, any database change, any new library with its exact version, how it was tested.

## CI

Every pull request runs on Python 3.10 and 3.12: install libraries, compile, ruff, and a smoke test that imports the bot and counts the slash commands. Ruff only checks real errors (syntax and undefined names), so unused imports and style problems are not caught. A red check means do not merge. CI does not run commands, so test changed commands in Discord.

## Saving tokens

- Open `bot.py` only to change startup. Almost all logic is in `kotone/` and `features/`.
- Search `eras.py` with grep for a member code or era. Do not read it in full.
- Read only the one `kotone/` file or `features/` file the task touches.
- Do not rewrite or summarise large files that the task does not need.
