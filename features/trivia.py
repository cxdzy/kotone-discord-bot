import asyncio
import datetime
import random
import sqlite3
import time
import discord
from kotone.client import (
    slash_command,
)
from kotone.cooldowns import (
    schedule_cooldown_reminder,
)
from kotone.db import (
    get_db,
)
import json
from pathlib import Path

TRIVIA_QUESTIONS_PATH = (
    Path(__file__).resolve().parent.parent / "triples_trivia.json"
)
DIFFICULTY_REWARDS = {"easy": 10, "medium": 20, "hard": 40}
SESSION_PLAN = (("easy", 2), ("medium", 2), ("hard", 1))
PERFECT_BONUS = 50
TRIVIA_COOLDOWN_SECONDS = 4 * 60 * 60
QUESTION_TIMEOUT_SECONDS = 15
FEEDBACK_SECONDS = 3
EMBED_COLOR = 0xff6b8b


def _load_trivia_questions():
    try:
        with TRIVIA_QUESTIONS_PATH.open(encoding="utf-8") as file:
            raw_questions = json.load(file)
    except FileNotFoundError:
        print(f"Trivia questions file not found: {TRIVIA_QUESTIONS_PATH}")
        return {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load trivia questions: {error}")
        return {}

    if not isinstance(raw_questions, list):
        print("Trivia questions file must contain a JSON list.")
        return {}

    pools = {difficulty: [] for difficulty in DIFFICULTY_REWARDS}
    seen_ids = set()
    for raw_question in raw_questions:
        if not isinstance(raw_question, dict):
            print("Skipping invalid trivia question: entry is not an object.")
            continue

        question_id = raw_question.get("id")
        difficulty = raw_question.get("difficulty")
        question = raw_question.get("question")
        choices = raw_question.get("choices")
        answer = raw_question.get("answer")
        if (
            not isinstance(question_id, str)
            or not question_id
            or question_id in seen_ids
            or difficulty not in DIFFICULTY_REWARDS
            or not isinstance(question, str)
            or not question.strip()
            or not isinstance(choices, list)
            or len(choices) != 4
            or not all(
                isinstance(choice, str) and choice.strip()
                for choice in choices
            )
            or not isinstance(answer, int)
            or isinstance(answer, bool)
            or answer < 0
            or answer >= len(choices)
        ):
            print(f"Skipping invalid trivia question: {question_id!r}")
            continue

        seen_ids.add(question_id)
        pools[difficulty].append(
            {
                "id": question_id,
                "difficulty": difficulty,
                "question": question.strip(),
                "choices": [choice.strip() for choice in choices],
                "answer": answer,
            }
        )

    missing_pools = [
        f"{difficulty} ({len(pools[difficulty])}/{required})"
        for difficulty, required in SESSION_PLAN
        if len(pools[difficulty]) < required
    ]
    if missing_pools:
        print(
            "Trivia question pools are too small: " + ", ".join(missing_pools)
        )
        return {}
    return pools


TRIVIA_QUESTIONS = _load_trivia_questions()
TRIVIA_READY = bool(TRIVIA_QUESTIONS)


class TriviaOnCooldown(Exception):
    def __init__(self, remaining_seconds):
        super().__init__("Trivia session is on cooldown.")
        self.remaining_seconds = remaining_seconds


class TriviaUnavailable(Exception):
    pass


def format_duration(seconds):
    days, remainder = divmod(max(0, int(seconds)), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def select_trivia_questions(cursor, user_id):
    selected = []
    for difficulty, required in SESSION_PLAN:
        pool = TRIVIA_QUESTIONS[difficulty]
        cursor.execute(
            '''SELECT question_id FROM trivia_seen
               WHERE user_id=? AND difficulty=?''',
            (user_id, difficulty),
        )
        seen_ids = {row[0] for row in cursor.fetchall()}
        chosen = [
            question
            for question in pool
            if question["id"] not in seen_ids
        ]
        if len(chosen) > required:
            chosen = random.sample(chosen, required)
        elif len(chosen) < required:
            chosen_ids = {question["id"] for question in chosen}
            fallback = [
                question
                for question in pool
                if question["id"] not in chosen_ids
            ]
            chosen.extend(
                random.sample(fallback, required - len(chosen))
            )
        random.shuffle(chosen)
        selected.extend(chosen)

    seen_at = datetime.datetime.now().isoformat(timespec="seconds")
    cursor.executemany(
        '''INSERT OR IGNORE INTO trivia_seen
           (user_id, question_id, difficulty, seen_at)
           VALUES (?, ?, ?, ?)''',
        [
            (user_id, question["id"], question["difficulty"], seen_at)
            for question in selected
        ],
    )

    for difficulty, _ in SESSION_PLAN:
        cursor.execute(
            '''SELECT COUNT(*) FROM trivia_seen
               WHERE user_id=? AND difficulty=?''',
            (user_id, difficulty),
        )
        seen_count = cursor.fetchone()[0]
        if seen_count >= len(TRIVIA_QUESTIONS[difficulty]):
            cursor.execute(
                '''DELETE FROM trivia_seen
                   WHERE user_id=? AND difficulty=?''',
                (user_id, difficulty),
            )

    return selected


def start_trivia_session(user_id, username):
    if not TRIVIA_READY:
        raise TriviaUnavailable("Trivia questions are not available.")

    now = time.time()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            '''SELECT expires_at FROM cooldowns
               WHERE user_id=? AND cooldown_type='trivia' ''',
            (user_id,),
        )
        cooldown = cursor.fetchone()
        if cooldown and cooldown[0] > now:
            raise TriviaOnCooldown(int(cooldown[0] - now))

        questions = select_trivia_questions(cursor, user_id)
        cursor.execute(
            '''INSERT OR IGNORE INTO users
               (user_id, username, daily_streak, last_daily, como)
               VALUES (?, ?, 0, NULL, 0)''',
            (user_id, username),
        )
        expires_at = now + TRIVIA_COOLDOWN_SECONDS
        cursor.execute(
            '''INSERT OR REPLACE INTO cooldowns
               (user_id, cooldown_type, expires_at)
               VALUES (?, 'trivia', ?)''',
            (user_id, expires_at),
        )
        schedule_cooldown_reminder(
            cursor,
            user_id,
            "trivia",
            expires_at,
        )
        conn.commit()

    return questions


def credit_trivia_reward(user_id, username, amount):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            '''INSERT OR IGNORE INTO users
               (user_id, username, daily_streak, last_daily, como)
               VALUES (?, ?, 0, NULL, 0)''',
            (user_id, username),
        )
        cursor.execute(
            '''UPDATE users SET username=?, como=como+?
               WHERE user_id=?''',
            (username, amount, user_id),
        )
        cursor.execute(
            "SELECT como FROM users WHERE user_id=?",
            (user_id,),
        )
        row = cursor.fetchone()
        new_balance = row[0] if row else amount
        conn.commit()

    return new_balance


def format_choices(choices):
    return "\n".join(
        f"**{letter}.** {choice}"
        for letter, choice in zip("ABCD", choices)
    )


def build_question_embed(question, number, total):
    difficulty = question["difficulty"]
    reward = DIFFICULTY_REWARDS[difficulty]
    embed = discord.Embed(
        title=f"🧠 tripleS Trivia • Question {number}/{total}",
        description=question["question"],
        color=EMBED_COLOR,
    )
    embed.add_field(
        name="Difficulty",
        value=difficulty.title(),
        inline=True,
    )
    embed.add_field(
        name="Reward",
        value=f"{reward} COMO",
        inline=True,
    )
    embed.add_field(
        name="Choices",
        value=format_choices(question["choices"]),
        inline=False,
    )
    embed.set_footer(
        text=(
            f"Select A, B, C, or D within "
            f"{QUESTION_TIMEOUT_SECONDS} seconds."
        )
    )
    return embed


def build_feedback_embed(record, number, total, score, earned):
    if record["timed_out"]:
        title = "⌛ Time's up!"
    elif record["correct"]:
        title = "✅ Correct!"
    else:
        title = "❌ Incorrect"

    question = record["question"]
    correct_letter = "ABCD"[question["answer"]]
    correct_choice = question["choices"][question["answer"]]
    embed = discord.Embed(
        title=title,
        description=question["question"],
        color=EMBED_COLOR,
    )
    embed.add_field(
        name="Correct answer",
        value=f"**{correct_letter}.** {correct_choice}",
        inline=False,
    )
    embed.add_field(
        name="Reward",
        value=(
            f"+{record['reward']} COMO"
            if record["reward"]
            else "0 COMO"
        ),
        inline=True,
    )
    embed.add_field(
        name="Score",
        value=f"{score}/{number}",
        inline=True,
    )
    embed.set_footer(
        text=f"Question {number}/{total} • Earned {earned} COMO so far"
    )
    return embed


def build_summary_embed(records, score, earned, bonus, new_balance, payout):
    total = len(records)
    embed = discord.Embed(
        title="🧠 tripleS Trivia • Session Complete",
        color=EMBED_COLOR,
    )
    embed.add_field(
        name="Score",
        value=f"{score}/{total}",
        inline=True,
    )
    embed.add_field(
        name="Question rewards",
        value=f"{earned} COMO",
        inline=True,
    )
    if bonus:
        embed.add_field(
            name="Perfect bonus",
            value=f"+{bonus} COMO",
            inline=True,
        )

    reward_lines = []
    for number, record in enumerate(records, 1):
        if record["correct"]:
            status = "✅"
        elif record["timed_out"]:
            status = "⌛"
        else:
            status = "❌"
        reward_text = (
            f"+{record['reward']} COMO"
            if record["reward"]
            else "0 COMO"
        )
        reward_lines.append(
            f"{number}. {record['question']['difficulty'].title()} — "
            f"{status} {reward_text}"
        )
    embed.add_field(
        name="Per-question rewards",
        value="\n".join(reward_lines) or "No questions answered.",
        inline=False,
    )
    embed.add_field(
        name="Total payout",
        value=f"{payout} COMO",
        inline=True,
    )
    embed.add_field(
        name="New balance",
        value=(
            f"{new_balance} COMO"
            if new_balance is not None
            else "Couldn't be updated"
        ),
        inline=True,
    )
    embed.set_footer(text=f"Session complete • {score}/{total} correct")
    return embed


async def send_ephemeral(interaction, content):
    try:
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral=True)
        else:
            await interaction.response.send_message(content, ephemeral=True)
    except (discord.HTTPException, discord.InteractionResponded, RuntimeError):
        pass


class TriviaQuestionView(discord.ui.View):
    def __init__(self, user_id, question_id):
        super().__init__(timeout=QUESTION_TIMEOUT_SECONDS)
        self.user_id = user_id
        self.answered = False
        self.result = asyncio.get_running_loop().create_future()

        for index, letter in enumerate("ABCD"):
            button = discord.ui.Button(
                label=letter,
                style=discord.ButtonStyle.primary,
                custom_id=f"trivia_{question_id}_{index}",
            )
            button.callback = self.make_callback(index)
            self.add_item(button)

    def make_callback(self, index):
        async def callback(interaction):
            if interaction.user.id != self.user_id:
                await send_ephemeral(interaction, "This isn't your game!")
                return
            if self.answered:
                await send_ephemeral(
                    interaction,
                    "This question has already ended.",
                )
                return

            self.answered = True
            for child in self.children:
                child.disabled = True

            try:
                await interaction.response.defer()
            except (
                discord.HTTPException,
                discord.InteractionResponded,
                RuntimeError,
            ):
                pass
            finally:
                if not self.result.done():
                    self.result.set_result(index)

        return callback

    async def on_timeout(self):
        if self.answered:
            return
        self.answered = True
        for child in self.children:
            child.disabled = True
        if not self.result.done():
            self.result.set_result(None)


class TriviaSession:
    def __init__(self, ctx, questions):
        self.ctx = ctx
        self.questions = questions
        self.records = []
        self.score = 0
        self.earned = 0
        self.message = None
        self.finalized = False

    async def play(self):
        total = len(self.questions)
        try:
            for number, question in enumerate(self.questions, 1):
                if not await self.ask_question(number, question, total):
                    break
        finally:
            await self.finish()

    async def ask_question(self, number, question, total):
        view = TriviaQuestionView(self.ctx.author.id, question["id"])
        embed = build_question_embed(question, number, total)
        try:
            if self.message is None:
                self.message = await self.ctx.reply(
                    embed=embed,
                    view=view,
                )
            else:
                await self.message.edit(embed=embed, view=view)
        except (discord.NotFound, discord.HTTPException) as error:
            print(f"Could not show trivia question: {error}")
            view.stop()
            return False

        answer = await view.result
        view.stop()
        timed_out = answer is None
        correct = not timed_out and answer == question["answer"]
        reward = (
            DIFFICULTY_REWARDS[question["difficulty"]]
            if correct
            else 0
        )
        if correct:
            self.score += 1
            self.earned += reward

        record = {
            "question": question,
            "correct": correct,
            "timed_out": timed_out,
            "reward": reward,
        }
        self.records.append(record)

        feedback = build_feedback_embed(
            record,
            number,
            total,
            self.score,
            self.earned,
        )
        try:
            await self.message.edit(embed=feedback, view=view)
        except (discord.NotFound, discord.HTTPException) as error:
            print(f"Could not show trivia feedback: {error}")
            self.message = None
            return False

        await asyncio.sleep(FEEDBACK_SECONDS)
        return True

    async def finish(self):
        if self.finalized:
            return
        self.finalized = True

        total = len(self.questions)
        bonus = PERFECT_BONUS if self.score == total else 0
        payout = self.earned + bonus
        new_balance = None

        try:
            new_balance = credit_trivia_reward(
                self.ctx.author.id,
                str(self.ctx.author),
                payout,
            )
        except sqlite3.Error as error:
            print(f"Could not credit trivia reward: {error}")

        embed = build_summary_embed(
            self.records,
            self.score,
            self.earned,
            bonus,
            new_balance,
            payout,
        )
        if self.message is not None:
            try:
                await self.message.edit(embed=embed, view=None)
                return
            except (discord.NotFound, discord.HTTPException) as error:
                print(f"Could not show trivia summary: {error}")
                self.message = None

        try:
            await self.ctx.reply(embed=embed)
        except (discord.NotFound, discord.HTTPException) as error:
            print(f"Could not send trivia summary: {error}")


@slash_command(name="trivia")
async def trivia(ctx):
    """Play a 5-question tripleS trivia session for COMO."""
    if not TRIVIA_READY:
        await ctx.reply(
            "Trivia isn't available right now. Please try again later."
        )
        return

    try:
        questions = start_trivia_session(
            ctx.author.id,
            str(ctx.author),
        )
    except TriviaOnCooldown as error:
        await ctx.reply(
            "You've already played a trivia session. "
            f"You can play again in "
            f"**{format_duration(error.remaining_seconds)}**."
        )
        return
    except TriviaUnavailable:
        await ctx.reply(
            "Trivia isn't available right now. Please try again later."
        )
        return
    except sqlite3.Error as error:
        print(f"Database error while starting trivia: {error}")
        await ctx.reply(
            "Trivia couldn't be started due to a database error."
        )
        return

    await TriviaSession(ctx, questions).play()
