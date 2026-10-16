from bot import *

minigame_group = app_commands.Group(
    name="minigame",
    description="Browse and play minigames.",
)
bot.tree.add_command(minigame_group)
SLASH_COMMANDS["minigame"] = minigame_group

@slash_command(name='8ball')
async def eight_ball(ctx, *, question):
    """Ask the magic 8-ball a question."""
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
        "My reply is no.", "My sources say no.", "Outlook not so good.",
        "Very doubtful."
    ]
    await ctx.reply(
        f"🎱 **You asked:** {question}\n"
        f"**The 8-ball says:** {random.choice(responses)}"
    )


@slash_command(name='choose')
async def choose(ctx, *, options):
    """Choose between multiple options (separate with 'or')."""
    if ' or ' not in options:
        await ctx.reply("Please provide options separated by 'or' (e.g., `/choose` with `pizza or burger or pasta`).")
        return

    choices = [option.strip() for option in options.split(' or ')]
    if len(choices) < 2:
        await ctx.reply("Please provide at least two options separated by 'or'")
        return

    await ctx.reply(f"{random.choice(choices)}!")


@slash_command(name="list", group=minigame_group)
async def minigame(ctx):
    """Show the available minigames."""
    embed = discord.Embed(
        title="🎮 Minigames",
        description="Use `/minigame play` to choose a minigame.",
        color=0xff6b8b,
    )
    for number, (name, description) in enumerate(MINIGAMES, 1):
        embed.add_field(
            name=f"{number}. {name}",
            value=f"- {description}",
            inline=False,
        )
    await ctx.reply(embed=embed)


@slash_command(name="play", group=minigame_group)
async def minigame_play(ctx, number: int):
    """Select a minigame by its number."""
    if number < 1 or number > len(MINIGAMES):
        await ctx.reply(
            f"Choose a minigame number from 1 to {len(MINIGAMES)}. "
            "Use `/minigame list` to see the list."
        )
        return

    name = MINIGAMES[number - 1][0]
    await ctx.reply(f"**{name}** isn't available yet. Check back later!")


@slash_command(name='profile')
async def profile(ctx, user: discord.Member = None):
    """Show a player's card collection profile."""
    user = user or ctx.author
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM cards WHERE owner_id=?", (user.id,))
            card_count = c.fetchone()[0]
            c.execute(
                "SELECT como, daily_streak FROM users WHERE user_id=?",
                (user.id,),
            )
            user_row = c.fetchone()
            c.execute(
                "SELECT member_code FROM user_biases WHERE user_id=?",
                (user.id,),
            )
            bias_codes = {row[0] for row in c.fetchall()}
            c.execute(
                "SELECT bio FROM user_bios WHERE user_id=?",
                (user.id,),
            )
            bio_row = c.fetchone()

        target = get_user_target(user.id)
        embed = discord.Embed(
            title=f"{user.display_name}'s Profile",
            color=0xff6b8b,
        )
        embed.set_author(
            name=user.name,
            icon_url=user.display_avatar.url,
        )
        bias_names = ", ".join(
            S_MEMBERS[code]["name"]
            for code in S_ORDER if code in bias_codes
        ) or "None set"
        bio_text = bio_row[0] if bio_row else "No bio set."
        profile_lines = [
            f"📝 **Bio:**\n{bio_text}",
            "",
            "**Info:**",
            f"💰 **Balance:** {user_row[0] if user_row else 0}",
            f"🎴 **Cards:** {card_count}",
            f"🔥 **Streak:** {user_row[1] if user_row else 0} days",
            f"🎯 **Target:** {format_target(target) if target else 'None set'}",
            f"💖 **Bias:** {bias_names}",
        ]
        embed.description = "\n".join(profile_lines)
        await ctx.reply(embed=embed)
    except Exception as e:
        print(f"Error in profile command: {e}")
        await ctx.reply("An error occurred while fetching the profile.")


@slash_command(name='bio')
async def bio_command(ctx, *, query: str = ""):
    """Set or clear your profile bio."""
    action, _, bio = query.strip().partition(" ")
    if action.casefold() == "clear":
        with get_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM user_bios WHERE user_id=?", (ctx.author.id,))
        await ctx.reply("Your profile bio has been cleared.")
        return

    if action.casefold() != "set" or not bio.strip():
        await ctx.reply("Use `/bio` with `set <your bio>` or `clear`.")
        return

    bio = bio.strip()
    if len(bio) > 300:
        await ctx.reply("Your bio must be 300 characters or fewer.")
        return

    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (ctx.author.id, str(ctx.author)),
        )
        c.execute(
            '''INSERT OR REPLACE INTO user_bios (user_id, bio)
               VALUES (?, ?)''',
            (ctx.author.id, bio),
        )

    await ctx.reply("Your profile bio has been set!")


@slash_command(name='stats')
async def stats(ctx, user: discord.Member = None):
    """View statistics about your card collection."""
    user = user or ctx.author
    user_id = user.id

    try:
        with get_db() as conn:
            c = conn.cursor()

            # Get total cards
            c.execute('''SELECT COUNT(*) FROM cards WHERE owner_id=?''', (user_id,))
            total_cards = c.fetchone()[0]

            if total_cards == 0:
                await ctx.reply(f"{user.display_name} doesn't have any cards yet!")
                return

            # Get rarity breakdown
            c.execute('''SELECT rarity, COUNT(*) FROM cards
                        WHERE owner_id=? GROUP BY rarity''', (user_id,))
            rarity_counts = dict(c.fetchall())

            # Get era breakdown
            c.execute('''SELECT era, COUNT(*) FROM cards
                        WHERE owner_id=? GROUP BY era''', (user_id,))
            era_counts = dict(c.fetchall())

            # Get user info
            c.execute('''SELECT como, daily_streak FROM users WHERE user_id=?''', (user_id,))
            user_info = c.fetchone()
            como = user_info[0] if user_info else 0
            streak = user_info[1] if user_info else 0

        # Create embed
        embed = discord.Embed(
            title=f"📊 {user.display_name}'s Stats",
            color=0xff6b8b
        )

        embed.add_field(
            name="💎 Total Cards",
            value=str(total_cards),
            inline=True
        )
        embed.add_field(
            name="💰 COMO",
            value=str(como),
            inline=True
        )
        embed.add_field(
            name="🔥 Daily Streak",
            value=f"{streak} days",
            inline=True
        )

        # Rarity breakdown
        rarity_text = "\n".join([
            f"{rarity}: {rarity_counts.get(rarity, 0)}"
            for rarity in RARITIES
        ])
        embed.add_field(
            name="📈 Rarity Breakdown",
            value=rarity_text,
            inline=True
        )

        # Era breakdown
        era_text = "\n".join([
            f"{era}: {count}"
            for era, count in era_counts.items()
        ]) or "None"
        embed.add_field(
            name="🎭 Era Breakdown",
            value=era_text,
            inline=True
        )

        await ctx.reply(embed=embed)

    except Exception as e:
        print(f"Error in stats command: {e}")
        await ctx.reply("An error occurred while fetching stats. Please try again.")


@slash_command(name='cooldown', aliases=('cd',))
async def cooldown(ctx):
    """Show the time remaining on your cooldowns."""
    cooldown_labels = {
        'daily': '📅 Daily',
        'weekly': '🗓️ Weekly',
        'drop': '🎴 Drop',
        'spin': '🎰 Spin',
        'claim': '🙋 Claim',
    }
    now = time.time()
    today = datetime.date.today().isoformat()

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                '''SELECT cooldown_type, expires_at FROM cooldowns
                   WHERE user_id=? AND expires_at>?''',
                (ctx.author.id, now)
            )
            active_cooldowns = {
                cooldown_type: expires_at
                for cooldown_type, expires_at in c.fetchall()
            }
            c.execute(
                "SELECT spin_date, spins FROM spin_usage WHERE user_id=?",
                (ctx.author.id,),
            )
            spin_usage = c.fetchone()
            spins_used = (
                spin_usage[1]
                if spin_usage and spin_usage[0] == today
                else 0
            )

        embed = discord.Embed(title="Cooldowns", color=0xff6b8b)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        cooldown_types = list(cooldown_labels)
        cooldown_types.extend(sorted(
            set(active_cooldowns) - set(cooldown_labels)
        ))

        for cooldown_type in cooldown_types:
            expires_at = active_cooldowns.get(cooldown_type)
            if cooldown_type == "spin":
                if spins_used >= SPIN_DAILY_LIMIT:
                    reset_at = expires_at or next_local_midnight_timestamp(today)
                    remaining = max(0, int(reset_at - now))
                    days, remainder = divmod(remaining, 86400)
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
                    remaining_text = (
                        f"Limit reached ({spins_used}/{SPIN_DAILY_LIMIT}) "
                        f"• resets in {' '.join(parts)}"
                    )
                else:
                    remaining_text = (
                        f"{spins_used}/{SPIN_DAILY_LIMIT} used • "
                        f"{SPIN_DAILY_LIMIT - spins_used} left today"
                    )
            elif expires_at is None:
                remaining_text = "Ready ✅"
            else:
                remaining = max(0, int(expires_at - now))
                days, remainder = divmod(remaining, 86400)
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
                remaining_text = " ".join(parts)

            label = cooldown_labels.get(cooldown_type)
            if label is None:
                label = f"⏳ {cooldown_type.replace('_', ' ').title()}"
            embed.add_field(
                name=label,
                value=remaining_text,
                inline=False
            )

        await ctx.reply(embed=embed)
    except Exception as e:
        print(f"Error in cooldown command: {e}")
        await ctx.reply("An error occurred while checking your cooldowns.")


@slash_command(name='remind', aliases=('reminder', 'reminders'))
async def cooldown_reminders(ctx, *, options: str = ""):
    """Choose which cooldown resets should be sent to you by DM."""
    parts = options.casefold().split()
    if parts:
        if parts[0] != "all" and parts[0] not in COOLDOWN_REMINDER_TYPES:
            await ctx.reply(
                "Choose `daily`, `weekly`, `drop`, `spin`, `claim`, or `all`."
            )
            return
        if len(parts) > 2 or (len(parts) == 2 and parts[1] not in {"on", "off"}):
            await ctx.reply(
                "Use `/remind` with `<daily|weekly|drop|spin|claim|all> [on|off]`."
            )
            return
    now = time.time()

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                '''INSERT OR IGNORE INTO cooldown_reminders
                   (user_id, cooldown_type, enabled, expires_at)
                   VALUES (?, ?, 0, NULL)''',
                (
                    (ctx.author.id, cooldown_type)
                    for cooldown_type in COOLDOWN_REMINDER_TYPES
                ),
            )

            if parts:
                cooldown_type = parts[0]
                if cooldown_type == "all":
                    selected_types = list(COOLDOWN_REMINDER_TYPES)
                else:
                    selected_types = [cooldown_type]

                enabled = len(parts) == 1 or parts[1] == "on"
                for selected_type in selected_types:
                    expires_at = None
                    if enabled:
                        cursor.execute(
                            '''SELECT expires_at FROM cooldowns
                               WHERE user_id=? AND cooldown_type=? AND expires_at>?''',
                            (ctx.author.id, selected_type, now),
                        )
                        active_cooldown = cursor.fetchone()
                        if active_cooldown:
                            expires_at = active_cooldown[0]
                    cursor.execute(
                        '''UPDATE cooldown_reminders
                           SET enabled=?, expires_at=?
                           WHERE user_id=? AND cooldown_type=?''',
                        (
                            int(enabled),
                            expires_at,
                            ctx.author.id,
                            selected_type,
                        ),
                    )

            cursor.execute(
                '''SELECT cooldown_type, enabled FROM cooldown_reminders
                   WHERE user_id=?''',
                (ctx.author.id,),
            )
            settings = dict(cursor.fetchall())
    except sqlite3.Error as error:
        print(f"Database error while updating cooldown reminders: {error}")
        await ctx.reply("Your reminder settings couldn't be saved due to a database error.")
        return

    settings_text = "\n".join(
        f"**{label}:** {'On' if settings.get(cooldown_type, 0) else 'Off'}"
        for cooldown_type, (label, _) in COOLDOWN_REMINDER_TYPES.items()
    )
    if parts:
        changed_types = (
            list(COOLDOWN_REMINDER_TYPES)
            if parts[0] == "all"
            else [parts[0]]
        )
        state = "enabled" if len(parts) == 1 or parts[1] == "on" else "disabled"
        changed_labels = ", ".join(
            COOLDOWN_REMINDER_TYPES[cooldown_type][0]
            for cooldown_type in changed_types
        )
        await ctx.reply(
            f"{changed_labels} cooldown reminders {state}.\n\n{settings_text}"
        )
    else:
        await ctx.reply(
            "Cooldown reminder settings (sent by DM):\n"
            f"{settings_text}\n\n"
            "Use `/remind` with `daily` to enable one, "
            "`spin` to enable the daily spin reset reminder, "
            "or `all on/off`."
        )


@slash_command(name='help')
async def help_command(ctx, *, command_name: str = ""):
    """Show command categories or get usage details for a command."""
    command_name = command_name.strip()
    if command_name:
        command = SLASH_COMMANDS.get(command_name.casefold())
        if command is None:
            await ctx.reply(
                f"I couldn't find `/{command_name}`. Use `/help` "
                "to browse available commands."
            )
            return

        qualified_name = getattr(command, "qualified_name", command.name)
        usage = f"/{qualified_name}"
        for parameter in getattr(command, "parameters", ()):
            marker = "<" if parameter.required else "["
            closing_marker = ">" if parameter.required else "]"
            usage += f" {marker}{parameter.name}{closing_marker}"
        embed = discord.Embed(
            title=f"Help • /{qualified_name}",
            description=command.description or "No description available.",
            color=0xff6b8b,
        )
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        aliases = SLASH_COMMAND_ALIASES.get(command.name, ())
        if aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(f"`/{alias}`" for alias in aliases),
                inline=False,
            )
        if isinstance(command, app_commands.Group) and command.commands:
            subcommands = " • ".join(
                f"`/{command.name} {subcommand.name}`"
                for subcommand in command.commands
            )
            embed.add_field(name="Subcommands", value=subcommands, inline=False)
        await ctx.reply(embed=embed)
        return

    view = HelpView(ctx)
    await ctx.reply(embed=view.get_embed(), view=view)


@slash_command(name='afk')
async def afk(ctx, *, reason: str = "AFK"):
    """Set an AFK status that clears when you send another message."""
    if ctx.guild is None:
        await ctx.reply("AFK status can only be set in a server.")
        return

    reason = reason.strip() or "AFK"
    if len(reason) > 500:
        await ctx.reply("Your AFK reason must be 500 characters or fewer.")
        return

    try:
        with get_db() as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO guild_afk
                   (guild_id, user_id, reason, since)
                   VALUES (?, ?, ?, ?)''',
                (ctx.guild.id, ctx.author.id, reason, time.time()),
            )
    except sqlite3.Error as error:
        print(f"Database error while setting AFK status: {error}")
        await ctx.reply("Your AFK status couldn't be saved due to a database error.")
        return

    await ctx.reply(
        f"{ctx.author.display_name} is now AFK: {reason}",
        allowed_mentions=discord.AllowedMentions.none(),
    )
