"""Offline smoke test: import the bot and count the slash commands it registers.

Usage: python ci/smoke_test.py [repo_root]

repo_root defaults to the parent of this script's folder. The bot is only
imported: no login, no connection, no tree.sync. The token is a fake value.
Prints exactly one line to stdout: "COMMANDS: <n>". Exits non-zero on any
import error or when the count is 0 or less.
"""
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

# Do not write __pycache__ folders into the repo being tested.
sys.dont_write_bytecode = True
os.environ["DISCORD_TOKEN"] = "dummy-token-not-real"


def main():
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path(__file__).resolve().parent.parent

    start_dir = os.getcwd()
    tmp = tempfile.mkdtemp(prefix="smoke_")
    try:
        # init_db() creates kpop_cards.db in the current directory.
        os.chdir(tmp)
        sys.path.insert(0, str(root))
        import bot

        count = len(bot.bot.tree.get_commands())
        names = sorted(c.name for c in bot.bot.tree.get_commands())
        print("NAMES: " + ",".join(names), file=sys.stderr)
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        return 1
    finally:
        try:
            os.chdir(start_dir)
            shutil.rmtree(tmp, ignore_errors=True)
        except Exception:
            pass

    if count <= 0:
        print("no slash commands registered", file=sys.stderr)
        return 1
    print(f"COMMANDS: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
