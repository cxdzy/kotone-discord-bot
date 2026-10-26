import asyncio
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from urllib.error import URLError
from urllib.request import Request, urlopen
import discord
from PIL import Image, ImageDraw, ImageOps
from eras import ERAS


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
