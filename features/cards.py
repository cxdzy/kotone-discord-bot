from bot import *

@slash_command(name='drop')
async def drop(ctx):
    """Drop 3 random cards for claiming."""
    user_id = ctx.author.id

    # Check drop cooldown
    is_on_cooldown, remaining = check_cooldown(user_id, 'drop', 600)
    if is_on_cooldown:
        await ctx.reply(
            f"You're on cooldown! Please wait {remaining} seconds before using drop again."
        )
        return

    try:
        drop_booster_active = has_active_drop_booster(user_id)
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT extra_drop_slots FROM user_item_effects WHERE user_id=?",
                (user_id,),
            )
            extra_slot_row = c.fetchone()
        extra_slot_available = bool(extra_slot_row and extra_slot_row[0] > 0)

        # Generate one additional card when an activated extra slot is ready.
        cards = generate_unique_cards(
            4 if extra_slot_available else 3,
            target=get_user_target(user_id),
            rarity_boost=drop_booster_active,
        )

        # Store generated cards, consume a queued slot, and start cooldown atomically.
        with get_db() as conn:
            c = conn.cursor()
            c.execute("BEGIN IMMEDIATE")
            now = time.time()
            c.execute(
                '''SELECT expires_at FROM cooldowns
                   WHERE user_id=? AND cooldown_type='drop' ''',
                (user_id,),
            )
            existing_cooldown = c.fetchone()
            if existing_cooldown and existing_cooldown[0] > now:
                remaining = int(existing_cooldown[0] - now)
                await ctx.reply(
                    f"You're on cooldown! Please wait {remaining} seconds before using drop again."
                )
                return

            c.execute(
                "SELECT extra_drop_slots FROM user_item_effects WHERE user_id=?",
                (user_id,),
            )
            current_slot_row = c.fetchone()
            extra_slot_used = bool(
                current_slot_row
                and current_slot_row[0] > 0
                and extra_slot_available
                and len(cards) == 4
            )
            cards_to_drop = cards if extra_slot_used else cards[:3]
            if extra_slot_used:
                c.execute(
                    '''UPDATE user_item_effects
                       SET extra_drop_slots=extra_drop_slots-1
                       WHERE user_id=? AND extra_drop_slots>0''',
                    (user_id,),
                )
                if c.rowcount != 1:
                    raise RuntimeError("The extra drop slot changed before the drop.")

            for card in cards_to_drop:
                c.execute('''INSERT INTO cards
                            (serial, member_code, era, rarity, owner_id, obtained_at)
                            VALUES (?, ?, ?, ?, NULL, NULL)''',
                          (card['serial'], card['member_code'], card['era'], card['rarity']))
            drop_expires_at = now + 600
            c.execute(
                '''INSERT OR REPLACE INTO cooldowns
                   (user_id, cooldown_type, expires_at) VALUES (?, 'drop', ?)''',
                (user_id, drop_expires_at),
            )
            schedule_cooldown_reminder(
                c,
                user_id,
                'drop',
                drop_expires_at,
            )
        cards = cards_to_drop

        embed = create_drop_embed(
            "🎉 Card Drop! 🎉",
            (
                f"{ctx.author.mention} has 30 seconds to claim one card first."
                + (
                    "\n🍀 Your Drop Luck Booster is active!"
                    if drop_booster_active
                    else ""
                )
            ),
            cards,
        )
        drop_image = await create_drop_embed_image(cards)

        # Create view with buttons for dropper
        view = View(timeout=30)
        view.dropper_id = user_id
        view.dropper_claimed = False
        view.drop_cards = cards
        view.refresh_lock = asyncio.Lock()

        for i, card in enumerate(cards, 1):
            button = ClaimButton(label=f"Claim Card {i}", card_serial=card['serial'])
            view.add_item(button)

        # Send message with buttons
        drop_msg = await ctx.send(embed=embed, file=drop_image, view=view)

        async def update_countdown():
            for seconds_remaining in range(25, -1, -5):
                await asyncio.sleep(5)
                if view.is_finished():
                    return
                async with view.refresh_lock:
                    countdown_embed = drop_msg.embeds[0].copy()
                    countdown_embed.description = (
                        f"{ctx.author.mention} has {seconds_remaining} seconds left to claim one card first."
                    )
                    await drop_msg.edit(
                        embed=countdown_embed,
                        attachments=drop_msg.attachments,
                        view=view,
                    )

        countdown_task = asyncio.create_task(update_countdown())
        await view.wait()
        countdown_task.cancel()

        for child in view.children:
            child.disabled = True
        if view.dropper_claimed:
            await drop_msg.delete()
        else:
            description = "The first-claim window expired. The remaining cards are open to everyone."
            async with view.refresh_lock:
                embed = drop_msg.embeds[0].copy()
                embed.description = description
                await drop_msg.edit(
                    embed=embed,
                    attachments=drop_msg.attachments,
                    view=view,
                )

        # Check which cards are still available
        with get_db() as conn:
            c = conn.cursor()
            available_cards = []

            for card in cards:
                c.execute('''SELECT owner_id FROM cards WHERE serial=?''',
                         (card['serial'],))
                result = c.fetchone()

                if result and result[0] is None:
                    available_cards.append(card)

        if available_cards:
            embed2 = create_drop_embed(
                "🎉 Remaining Cards! 🎉",
                "Everyone can now claim the remaining cards!",
                available_cards,
            )
            remaining_image = await create_drop_embed_image(available_cards)

            # Create view with buttons for everyone
            public_view = View(timeout=30)
            public_view.drop_cards = available_cards
            public_view.refresh_lock = asyncio.Lock()
            public_view.message_replaced = False
            public_view.dropper_id = None
            public_view.original_drop_message = (
                None if view.dropper_claimed else drop_msg
            )

            for index, card in enumerate(available_cards, 1):
                button = ClaimButton(
                    label=f"Claim Card {index}",
                    card_serial=card['serial']
                )
                public_view.add_item(button)

            public_msg = await ctx.send(
                embed=embed2,
                file=remaining_image,
                view=public_view,
            )

            # Wait for the public claim period
            await public_view.wait()

            # Disable all buttons after timeout
            for child in public_view.children:
                child.disabled = True

            if not public_view.message_replaced:
                await public_msg.edit(view=public_view)

        await ctx.send("Card drop event has ended!")

    except Exception as e:
        print(f"Error in drop command: {e}")
        await ctx.reply("An error occurred while dropping cards. Please try again.")


@slash_command(name='spin')
async def spin(ctx, serial: str = ""):
    """Preview the odds and confirm wagering an owned card on a spin.

    Confirming consumes the wager. Each spin has one explosion among 16 buttons,
    and up to five spins are allowed per local day.
    """
    serial = serial.strip()
    if not serial:
        await ctx.reply(
            "Choose one of your owned card serials with `/spin serial`. "
            "Your wagered card is consumed."
        )
        return
    if len(serial) > 50:
        await ctx.reply("Invalid serial number.")
        return

    today = datetime.date.today().isoformat()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT member_code, era, rarity
                   FROM cards WHERE serial=? AND owner_id=?''',
                (serial, ctx.author.id),
            )
            card_row = cursor.fetchone()
            if card_row is None:
                await ctx.reply("You don't own a card with that serial.")
                return
            member_code, era, rarity = card_row
            if rarity not in SPIN_REWARD_COUNTS:
                await ctx.reply(
                    "That card has an unsupported rarity and can't be spun."
                )
                return
            cursor.execute(
                "SELECT 1 FROM market_listings WHERE card_serial=?",
                (serial,),
            )
            if cursor.fetchone():
                await ctx.reply(
                    "Unlist that card from the market before using it for a spin."
                )
                return
            cursor.execute(
                "SELECT spin_date, spins FROM spin_usage WHERE user_id=?",
                (ctx.author.id,),
            )
            usage_row = cursor.fetchone()
            spins_used = (
                usage_row[1]
                if usage_row and usage_row[0] == today
                else 0
            )
            if spins_used >= SPIN_DAILY_LIMIT:
                await ctx.reply(
                    f"You've used all **{SPIN_DAILY_LIMIT} spins** for today. "
                    "Your limit resets at local midnight."
                )
                return
            member = ERAS[era]["members"][member_code]
            wagered_card = {
                "serial": serial,
                "member_code": member_code,
                "era": era,
                "rarity": rarity,
                "name": member["name"],
                "full_name": member["full_name"],
            }
    except sqlite3.Error as error:
        print(f"Database error while preparing spin for {ctx.author.id}: {error}")
        await ctx.reply("Spin odds couldn't be checked due to a database error.")
        return
    except KeyError as error:
        print(f"Could not prepare spin for {ctx.author.id}: {error}")
        await ctx.reply("That card's details couldn't be loaded for a spin.")
        return

    view = SpinConfirmationView(
        ctx,
        wagered_card,
        SPIN_DAILY_LIMIT - spins_used - 1,
    )
    view.message = await ctx.reply(
        embed=view.get_embed(),
        view=view,
    )


@slash_command(name='merge')
async def merge_cards(ctx, *, card_serials: str = ""):
    """Confirm a merge of selected owned cards into the next rarity."""
    serials = card_serials.replace(",", " ").split()
    if len(serials) not in {9, 10} or len(set(serials)) != len(serials):
        await ctx.reply(
            "Provide 10 different serials, or 9 after activating a Merge Discount Token. Example: "
            "`/merge` with the card serials separated by spaces."
        )
        return

    try:
        with get_db() as conn:
            selected_rarity, selected_cards = get_merge_selection(
                conn.cursor(),
                ctx.author.id,
                serials,
            )
    except ValueError as error:
        await ctx.reply(str(error))
        return
    except sqlite3.Error as error:
        print(f"Database error while checking merge cards: {error}")
        await ctx.reply("The merge couldn't be started due to a database error.")
        return

    next_rarity = MERGE_UPGRADES[selected_rarity]
    serial_count = len(serials)
    token_note = (
        " Your activated Merge Discount Token will be consumed."
        if serial_count == 9
        else ""
    )
    confirmation_embed = discord.Embed(
        title="Confirm Card Merge",
        description=(
            f"Merge these {serial_count} **{selected_rarity}** cards into 1 random "
            f"**{next_rarity}** card? This will permanently consume the cards below."
            f"{token_note}"
        ),
        color=0xff6b8b,
    )
    card_list = []
    for serial, member_code, era, rarity, _ in selected_cards:
        member_name = ERAS[era]["members"][member_code]["full_name"]
        card_list.append(
            f"• `{serial}` — {member_name} ({ERAS[era]['name']}, {rarity})"
        )
    confirmation_embed.add_field(
        name="Cards to consume",
        value="\n".join(card_list),
        inline=False,
    )

    view = MergeConfirmationView(ctx.author.id, serials)
    view.message = await ctx.reply(embed=confirmation_embed, view=view)


@slash_command(name='collection')
async def collection(ctx, *, query: str = ""):
    """Show your owned cards for one era, with rarity filters."""
    parts = query.strip().split()
    if not parts:
        await ctx.reply(
            "Choose an era, optionally with a rarity. Example: "
            "`/collection` with `ASSEMBLE rare`."
        )
        return

    rarity_lookup = {rarity.casefold(): rarity for rarity in RARITIES}
    selected_rarities = [
        rarity_lookup[part.casefold()]
        for part in parts
        if part.casefold() in rarity_lookup
    ]
    if len(selected_rarities) > 1:
        await ctx.reply("Choose only one rarity for your collection.")
        return
    rarity = selected_rarities[0] if selected_rarities else "Common"
    era_parts = [
        part for part in parts if part.casefold() not in rarity_lookup
    ]
    era = ERA_ALIAS_LOOKUP.get(normalize_era_alias(" ".join(era_parts)))
    if era is None or era not in ERAS:
        available_eras = ", ".join(
            f"{ERAS[era_key]['name']} ({aliases[1]})"
            for era_key, aliases in ERA_ALIASES.items()
        )
        await ctx.reply(
            f"I couldn't identify that era. Available eras: {available_eras}."
        )
        return

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                '''SELECT member_code, rarity FROM cards
                   WHERE owner_id=? AND era=?''',
                (ctx.author.id, era),
            )
            owned_by_rarity = {name: set() for name in RARITIES}
            for member_code, card_rarity in c.fetchall():
                if card_rarity in owned_by_rarity:
                    owned_by_rarity[card_rarity].add(member_code)

        view = CollectionView(
            ctx.author,
            era,
            owned_by_rarity,
            rarity,
        )
        embed = create_collection_embed(
            ctx.author,
            era,
            rarity,
            len(owned_by_rarity[rarity]),
            len(ERAS[era]["members"]),
            1,
            view.total_pages,
        )
        image = await create_collection_embed_image(
            era,
            rarity,
            owned_by_rarity[rarity],
        )
        view.message = await ctx.reply(
            embed=embed,
            file=image,
            view=view,
        )
    except sqlite3.Error as error:
        print(f"Database error while loading collection: {error}")
        await ctx.reply("An error occurred while loading your collection.")
    except Exception as error:
        print(f"Error while creating collection: {error}")
        await ctx.reply("An error occurred while creating your collection.")


@slash_command(name='inventory', aliases=('inv',))
async def inventory(ctx, user: discord.Member = None, *, query: str = ""):
    """View and filter your card inventory or another user's."""
    user = user or ctx.author
    query = query.strip()
    search_terms = query.casefold().replace(',', ' ').split()
    user_id = user.id

    try:
        with get_db() as conn:
            c = conn.cursor()

            # Get user's cards
            c.execute('''SELECT serial, member_code, era, rarity, obtained_at
                         FROM cards
                         WHERE owner_id=?
                         ORDER BY obtained_at DESC''', (user_id,))
            cards = c.fetchall()

        if search_terms:
            filtered_cards = []
            for card in cards:
                _, member_code, era, rarity, _ = card
                member_data = ERAS.get(era, {}).get('members', {}).get(member_code, {})
                s_number = (
                    S_ORDER.index(member_code) + 1
                    if member_code in S_ORDER
                    else None
                )
                search_text = ' '.join((
                    member_code,
                    f"s{s_number}" if s_number is not None else "",
                    era,
                    rarity,
                    member_data.get('name', ''),
                    member_data.get('full_name', ''),
                )).casefold()
                if all(term in search_text for term in search_terms):
                    filtered_cards.append(card)
            cards = filtered_cards

        if not cards:
            if search_terms:
                await ctx.reply(
                    f"No cards in {user.display_name}'s inventory match `{query}`."
                )
                return
            await ctx.reply(f"{user.display_name} doesn't have any cards yet!")
            return

        # Create paginated view
        view = InventoryView(cards, user.display_name, ctx)
        embed = view.get_embed()

        await ctx.reply(embed=embed, view=view)

    except Exception as e:
        print(f"Error in inventory command: {e}")
        await ctx.reply("An error occurred while fetching inventory. Please try again.")


@slash_command(name='view')
async def view_card(ctx, serial: str):
    """View detailed information about a specific card."""
    # Basic input validation
    if len(serial) > 50:
        await ctx.reply("Invalid serial number!")
        return

    try:
        with get_db() as conn:
            c = conn.cursor()

            # Get card details
            c.execute('''SELECT member_code, era, rarity, owner_id, obtained_at
                         FROM cards
                         WHERE serial=?''', (serial,))

            card = c.fetchone()

        if not card:
            await ctx.reply("Card not found!")
            return

        member_code, era, rarity, owner_id, obtained_at = card

        # Get owner username
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE user_id=?", (owner_id,))
            owner = c.fetchone()

        owner_name = owner[0] if owner else "Unknown"
        owner_user = ctx.guild.get_member(owner_id) if ctx.guild and owner_id else None
        if owner_user is None and owner_id:
            owner_user = ctx.bot.get_user(owner_id)
        if owner_user is None and owner_id:
            try:
                owner_user = await ctx.bot.fetch_user(owner_id)
            except discord.HTTPException as e:
                print(f"Could not fetch card owner {owner_id}: {e}")

        # Get card info
        try:
            full_name = ERAS[era]['members'][member_code]['full_name']
            era_name = ERAS[era]['name']
            image_url = get_card_image(era, member_code, rarity)
        except KeyError:
            await ctx.reply("Card data corrupted!")
            return

        # Create embed
        embed = discord.Embed(
            description=f"**{full_name}**",
            color=0xff6b8b
        )
        embed.set_author(
            name=serial,
            icon_url=owner_user.display_avatar.url if owner_user else None,
        )

        # Set the card image
        embed.set_image(url=image_url)

        embed.add_field(name="Rarity", value=rarity, inline=True)
        embed.add_field(name="Era", value=era_name, inline=True)
        embed.add_field(name="Owner", value=owner_name, inline=True)
        embed.add_field(
            name="Obtained",
            value=obtained_at[:10] if obtained_at else "Unknown",
            inline=True
        )

        # Set color based on rarity
        rarity_colors = {
            "Common": 0x808080,     # Gray
            "Rare": 0x0070FF,       # Blue
            "Epic": 0x800080,       # Purple
            "Legendary": 0xFFD700,  # Gold
            "Mythic": 0xFF4FD8      # Pink
        }
        embed.color = rarity_colors.get(rarity, 0xff6b8b)

        await ctx.reply(embed=embed)

    except Exception as e:
        print(f"Error in view command: {e}")
        await ctx.reply("An error occurred while viewing the card. Please try again.")


@slash_command(name='give', aliases=('gift', 'send'))
async def give_card(ctx, recipient: discord.Member, serial: str):
    """Give a card to another user."""
    # Validation
    if ctx.author.id == recipient.id:
        await ctx.reply("You can't give a card to yourself!")
        return

    if len(serial) > 50:
        await ctx.reply("Invalid serial number!")
        return

    if recipient.bot:
        await ctx.reply("You can't give cards to bots!")
        return

    try:
        with get_db() as conn:
            c = conn.cursor()

            # Check if the card exists and belongs to the sender
            c.execute('''SELECT owner_id, member_code, era, rarity
                        FROM cards WHERE serial=?''', (serial,))
            card = c.fetchone()

            if not card:
                await ctx.reply("Card not found!")
                return

            if card[0] != ctx.author.id:
                await ctx.reply("You don't own this card!")
                return

            # Check if recipient exists in users table, if not create them
            c.execute("SELECT user_id FROM users WHERE user_id=?", (recipient.id,))
            recipient_exists = c.fetchone()

            if not recipient_exists:
                c.execute('''INSERT INTO users (user_id, username)
                            VALUES (?, ?)''',
                          (recipient.id, str(recipient)))

            # Transfer the card
            c.execute('''UPDATE cards
                        SET owner_id=?, obtained_at=?
                        WHERE serial=?''',
                      (recipient.id, str(datetime.datetime.now()), serial))

        # Get card details for message
        member_code, era, rarity = card[1], card[2], card[3]
        try:
            member_name = ERAS[era]['members'][member_code]['name']
            card_desc = f"{rarity} {member_name}"
        except KeyError:
            card_desc = serial

        await ctx.reply(
            f"{ctx.author.mention} has given **{card_desc}** ({serial}) to {recipient.mention}!"
        )

    except Exception as e:
        print(f"Error in give command: {e}")
        await ctx.reply("An error occurred while transferring the card. Please try again.")


@slash_command(name='target')
async def target_command(ctx, *, query: str = ""):
    """Set or clear the member/rarity/era you want to target."""
    query = query.strip()
    if query.casefold() in {"clear", "off", "none"}:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM user_targets WHERE user_id=?", (ctx.author.id,))
        await ctx.reply("Your card target has been cleared.")
        return

    if not query:
        current_target = get_user_target(ctx.author.id)
        if current_target:
            await ctx.reply(
                f"Your current target is **{format_target(current_target)}**. "
                "Use `/target` with `clear` to remove it."
            )
        else:
            await ctx.reply(
                "Set a target with `/target` and a member, optionally adding a rarity "
                "and/or era (for example, `rare jiwoo`)."
            )
        return

    tokens = query.casefold().split()
    rarity = next(
        (name for name in RARITIES if name.casefold() in tokens),
        None,
    )
    era = next(
        (
            era_code for era_code, era_data in ERAS.items()
            if era_code.casefold() in tokens
            or era_data["name"].casefold() in tokens
        ),
        None,
    )
    member_query = " ".join(
        token for token in tokens
        if token not in {
            *(name.casefold() for name in RARITIES),
            *(era_code.casefold() for era_code in ERAS),
            *(era_data["name"].casefold() for era_data in ERAS.values()),
        }
    ).strip()
    normalized_member_query = " ".join(member_query.split())

    matching_members = {
        (era_code, member_code)
        for era_code, era_data in ERAS.items()
        for member_code, member_data in era_data["members"].items()
        if (era is None or era_code == era)
        and normalized_member_query in {
            member_code.casefold(),
            member_data["name"].casefold(),
            member_data["full_name"].casefold(),
        }
    }

    member_codes = {member_code for _, member_code in matching_members}
    if not normalized_member_query or not member_codes:
        await ctx.reply(
            "I couldn't find that member. Try their short name, full name, or member code."
        )
        return
    if len(member_codes) > 1:
        await ctx.reply(
            "That name matches multiple members. Please use a more specific name or member code."
        )
        return

    member_code = next(iter(member_codes))
    target = {"era": era, "member_code": member_code, "rarity": rarity}
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (ctx.author.id, str(ctx.author)),
        )
        c.execute(
            '''INSERT OR REPLACE INTO user_targets
               (user_id, era, member_code, rarity)
               VALUES (?, ?, ?, ?)''',
            (ctx.author.id, era, member_code, rarity),
        )

    await ctx.reply(
        f"Your card target is now **{format_target(target)}**. "
        "It gets a small +5 percentage-point chance on generated cards."
    )


@slash_command(name='bias')
async def bias_command(ctx, *, query: str = ""):
    """Set or clear the members shown as your profile biases."""
    query = query.strip()
    if not query:
        await ctx.reply(
            "Set your biases with `/bias` and `set jiwoo seoyeon yooyeon`, "
            "or clear them with `/bias` and `clear`."
        )
        return

    action, _, names = query.partition(" ")
    if action.casefold() in {"clear", "off", "none"}:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM user_biases WHERE user_id=?", (ctx.author.id,))
        await ctx.reply("Your profile biases have been cleared.")
        return

    if action.casefold() != "set" or not names.strip():
        await ctx.reply(
            "Use `/bias` with `set <member names>` or `clear`."
        )
        return

    try:
        bias_codes = parse_biases(names)
    except ValueError as error:
        await ctx.reply(str(error))
        return

    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (ctx.author.id, str(ctx.author)),
        )
        c.execute("DELETE FROM user_biases WHERE user_id=?", (ctx.author.id,))
        c.executemany(
            "INSERT INTO user_biases (user_id, member_code) VALUES (?, ?)",
            ((ctx.author.id, member_code) for member_code in bias_codes),
        )

    display_names = [S_MEMBERS[code]["name"] for code in bias_codes]
    await ctx.reply(
        "Your profile biases have been set! **"
        + ", ".join(display_names)
        + "**"
    )
