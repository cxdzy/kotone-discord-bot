import discord
from discord.ext import commands, tasks
import random
import sqlite3
import datetime
import asyncio
import time
import os
import re
import ctypes
from io import BytesIO
from urllib.error import URLError
from urllib.request import Request, urlopen
from discord.ui import Button, View
from contextlib import contextmanager
from PIL import Image, ImageDraw, ImageOps
from dotenv import load_dotenv

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

def get_command_prefix(_bot, message):
    prefix = message.content[:2]
    if prefix.casefold() == "k!":
        return prefix
    return "k!"


bot = commands.Bot(
    command_prefix=get_command_prefix,
    case_insensitive=True,
    intents=intents,
)

# Remove the default help command so we can define our own
bot.remove_command('help')

# Card data with eras
ERAS = {
    "AAA": {
        "name": "AAA",
        "members": {
            "JHR": {
                "name": "Hyerin", 
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/atom01-hyerin-118a-1782341464062.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/atom01-hyerin-117a-1782342024353.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/atom01-hyerin-219z-1782343785301.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-hyerin-402z-1782339683194.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KYY": {
                "name": "Yooyeon", 
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/atom01-yooyeon-119a-1782342128777.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/atom01-yooyeon-120a-1782340883272.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/atom01-yooyeon-218z-1782344300718.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-yooyeon-402z-1782343607356.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KNK": {
                "name": "Nakyoung", 
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/atom01-nakyoung-119a-1782343380082.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/atom01-nakyoung-117a-1782343380083.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/atom01-nakyoung-216z-1782340366108.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-nakyoung-402z-1782340422614.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "GYB": {
                "name": "Yubin", 
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/atom01-yubin-117a-1782342429572.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/atom01-yubin-118a-1782339636430.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/atom01-yubin-217z-1782345000648.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-yubin-402z-1782340307577.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            }
        }
    },
    "ASSEMBLE": {
        "name": "ASSEMBLE",
        "members": {
            "YSY": {
                "name": "Seoyeon", 
                "full_name": "Yoon Seoyeon",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-seoyeon-108z-1782344857688.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-seoyeon-313z-1782340962654.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-seoyeon-202z-1782344513651.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-seoyeon-402z-1782342601718.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "JHR": {
                "name": "Hyerin", 
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-hyerin-106z-1782339886639.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-hyerin-301z-1782339829211.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-hyerin-202z-1782344549210.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/divine01-hyerin-401a-1782343961924.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "LJW": {
                "name": "Jiwoo", 
                "full_name": "Lee Jiwoo",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-jiwoo-105a-1782341318096.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-jiwoo-305z-1782340536939.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-jiwoo-208a-1782339895359.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-jiwoo-402z-1782343067344.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KCY": {
                "name": "Chaeyeon", 
                "full_name": "Kim Chaeyeon",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-chaeyeon-107z-1782342745204.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-chaeyeon-305z-1782344865148.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-chaeyeon-202z-1782343768187.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-chaeyeon-402z-1782343868867.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KYY": {
                "name": "Yooyeon", 
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-yooyeon-102z-1782343175557.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-yooyeon-303z-1782341626035.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-yooyeon-202z-1782342170245.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-yooyeon-402z-1782344712343.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KSM": {
                "name": "Soomin", 
                "full_name": "Kim Soomin",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-soomin-108a-1782342418981.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-soomin-303z-1782342106452.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-soomin-208a-1782344993571.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-soomin-402z-1782339995617.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KNK": {
                "name": "Nakyoung", 
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-nakyoung-106z-1782341561799.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-nakyoung-302z-1782341859551.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-nakyoung-201z-1782343906331.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-nakyoung-402z-1782340614290.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "GYB": {
                "name": "Yubin", 
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-yubin-106z-1782343427617.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-yubin-302z-1782341541747.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-yubin-208a-1782344214005.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-yubin-402z-1782344112134.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KAE": {
                "name": "Kaede", 
                "full_name": "Yamada Kaede",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-kaede-108z-1782344646240.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-kaede-301z-1782340993833.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-kaede-207a-1782340565556.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-kaede-402z-1782343301941.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "SDH": {
                "name": "Dahyun", 
                "full_name": "Seo Dahyun",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-dahyun-104z-1782341722068.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-dahyun-302z-1782341712869.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-dahyun-201z-1782339676521.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-dahyun-402z-1782342791953.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            }
        }
    },
    "KRE": {
        "name": "KRE",
        "members": {
            "YSY": {
                "name": "Seoyeon",
                "full_name": "Yoon Seoyeon",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-seoyeon-326z-1782343585590.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-seoyeon-325z-1782340561853.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-seoyeon-211a-1782344947239.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-seoyeon-402z-1782342482866.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "LJW": {
                "name": "Jiwoo",
                "full_name": "Lee Jiwoo",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-jiwoo-323z-1782342139066.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-jiwoo-319z-1782343394143.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-jiwoo-212a-1782342913644.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/cream02-jiwoo-402z-1782339924657.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KCY": {
                "name": "Chaeyeon",
                "full_name": "Kim Chaeyeon",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-chaeyeon-324z-1782341561799.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-chaeyeon-320z-1782339457965.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-chaeyeon-211a-1782339389690.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-chaeyeon-402z-1782344412320.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            },
            "KSM": {
                "name": "Soomin",
                "full_name": "Kim Soomin",
                "images": {
                    "Common": "https://media.objekt.top/collection-images/front/binary01-soomin-324z-1782340706008.webp",
                    "Rare": "https://media.objekt.top/collection-images/front/binary01-soomin-319z-1782340812953.webp",
                    "Epic": "https://media.objekt.top/collection-images/front/binary01-soomin-213a-1782343683921.webp",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-soomin-402z-1782344378764.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                }
            }
        }
    },
    "ASSEMBLE24": {
        "name": "ASSEMBLE24",
        "members": {
            "YSY": {
                "name": "Seoyeon",
                "full_name": "Yoon Seoyeon",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "JHR": {
                "name": "Hyerin",
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "LJW": {
                "name": "Jiwoo",
                "full_name": "Lee Jiwoo",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KCY": {
                "name": "Chaeyeon",
                "full_name": "Kim Chaeyeon",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KYY": {
                "name": "Yooyeon",
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KSM": {
                "name": "Soomin",
                "full_name": "Kim Soomin",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KNK": {
                "name": "Nakyoung",
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "GYB": {
                "name": "Yubin",
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KAE": {
                "name": "Kaede",
                "full_name": "Yamada Kaede",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "SDH": {
                "name": "Dahyun",
                "full_name": "Seo Dahyun",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KTN": {
                "name": "Kotone",
                "full_name": "Kamimoto Kotone",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KYJ": {
                "name": "Yeonji",
                "full_name": "Kwak Yeonji",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "HST": {
                "name": "Nien",
                "full_name": "Hsu Nien Tzu",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "PSH": {
                "name": "Sohyun",
                "full_name": "Park Sohyun",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "ZXY": {
                "name": "Xinyu",
                "full_name": "Zhou Xinyu",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KMY": {
                "name": "Mayu",
                "full_name": "Koma Mayu",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "LYN": {
                "name": "Lynn",
                "full_name": "Kawakami Lynn",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "JBN": {
                "name": "Joobin",
                "full_name": "Joo Bin",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "JHY": {
                "name": "Hayeon",
                "full_name": "Jeong Hayeon",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "SHI": {
                "name": "Shion",
                "full_name": "Park Shion",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "KCW": {
                "name": "Chaewon",
                "full_name": "Kim Chaewon",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "SUL": {
                "name": "Sullin",
                "full_name": "Pirada Bunraksa",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "SEO": {
                "name": "Seoah",
                "full_name": "Jeong Haerin",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            },
            "JSH": {
                "name": "Jiyeon",
                "full_name": "Ji Suhyeon",
                "images": {
                    "Common": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            }
        }
    }
}

RARITIES = {
    "Common": 100000,
    "Rare": 44203,
    "Epic": 580,
    "Legendary": 10,
    "Mythic": 1,
}

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
    ("Minigame 1", "Minigame 1 description"),
    ("Minigame 2", "Minigame 2 description"),
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
        
        # Check if era column exists, if not add it (for migration)
        c.execute("PRAGMA table_info(cards)")
        columns = [column[1] for column in c.fetchall()]
        if 'era' not in columns:
            c.execute("ALTER TABLE cards ADD COLUMN era TEXT")
            c.execute("UPDATE cards SET era = 'AAA' WHERE era IS NULL")

init_db()

# Cooldown management functions
COOLDOWN_REMINDER_TYPES = {
    "daily": ("Daily", "k!daily"),
    "weekly": ("Weekly", "k!weekly"),
    "drop": ("Drop", "k!drop"),
    "claim": ("Claim", None),
}

def schedule_cooldown_reminder(cursor, user_id, cooldown_type, expires_at):
    cursor.execute(
        '''UPDATE cooldown_reminders SET expires_at=?
           WHERE user_id=? AND cooldown_type=? AND enabled=1''',
        (expires_at, user_id, cooldown_type),
    )

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
        "description": "Reset your active k!drop cooldown.",
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
        "description": "Use to add one card to your next k!drop.",
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
            raise ValueError("You don't have a COMO balance yet. Use `k!daily` first.")
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
            raise ValueError(f"You don't have a **{item['name']}** in `k!items`.")

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
                    "Activated an **Extra Drop Slot** for your next `k!drop`"
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
def get_card_image(era, member_code, rarity):
    try:
        images = ERAS[era]["members"][member_code]["images"]
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
            image = ImageOps.fit(
                image,
                (card_width, card_height),
                method=Image.Resampling.LANCZOS,
            )
            canvas.paste(image, (x, 0))
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
    if era == "ASSEMBLE24":
        start = page * COLLECTION_MEMBERS_PER_PAGE
        members = members[start:start + COLLECTION_MEMBERS_PER_PAGE]
    card_width, card_height = 170, 238
    label_height = 34
    gap = 10
    columns = min(6 if era == "ASSEMBLE24" else 5, len(members))
    rows = (len(members) + columns - 1) // columns
    canvas_width = columns * card_width + (columns - 1) * gap
    canvas_height = rows * (card_height + label_height) + (rows - 1) * gap
    canvas = Image.new("RGB", (canvas_width, canvas_height), (35, 35, 45))
    draw = ImageDraw.Draw(canvas)

    for index, (member_code, member_data) in enumerate(members):
        column = index % columns
        row = index // columns
        x = column * (card_width + gap)
        y = row * (card_height + label_height + gap)
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
            image = ImageOps.fit(
                image,
                (card_width, card_height),
                method=Image.Resampling.LANCZOS,
            )
        except (URLError, OSError, ValueError, Image.DecompressionBombError) as error:
            print(f"Could not load collection image for {member_code}: {error}")
            image = Image.new("RGB", (card_width, card_height), (65, 65, 75))
            ImageDraw.Draw(image).text(
                (12, card_height // 2),
                "Image unavailable",
                fill="white",
            )

        if member_code not in owned_member_codes:
            muted = ImageOps.grayscale(image).convert("RGB")
            overlay = Image.new("RGB", muted.size, (25, 25, 30))
            image = Image.blend(muted, overlay, 0.62)

        canvas.paste(image, (x, y))
        draw.text(
            (x + 4, y + card_height + 5),
            member_data["name"],
            fill=(245, 245, 250),
        )

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
                                SET owner_id=?, obtained_at=? 
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
                        claimed_embed.set_image(url=get_card_image(era, member_code, rarity))
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
class InventoryView(View):
    def __init__(self, cards, user_display_name, ctx):
        super().__init__(timeout=180)  # 3 minute timeout
        self.cards = cards
        self.user_display_name = user_display_name
        self.ctx = ctx
        self.current_page = 0
        self.items_per_page = 5
        self.total_pages = (len(cards) + self.items_per_page - 1) // self.items_per_page
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        # Disable/enable buttons based on current page
        self.children[0].disabled = self.current_page == 0  # Previous button
        self.children[1].disabled = self.current_page >= self.total_pages - 1  # Next button
    
    def get_embed(self):
        embed = discord.Embed(
            title=f"{self.user_display_name}'s Inventory",
            description=f"Page {self.current_page + 1}/{self.total_pages} • Total Cards: {len(self.cards)}",
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
        end_idx = min((self.current_page + 1) * self.items_per_page, len(self.cards))
        
        for i in range(start_idx, end_idx):
            serial, member_code, era, rarity, obtained_at = self.cards[i]
            
            try:
                member_name = ERAS[era]['members'][member_code]['name']
                era_name = ERAS[era]['name']
            except KeyError:
                member_name = "Unknown"
                era_name = "Unknown"
            
            embed.add_field(
                name=f"{serial}",
                value=f"Member: {member_name}\nEra: {era_name}\nRarity: {rarity}\nObtained: {obtained_at[:10] if obtained_at else 'Unknown'}",
                inline=False
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

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    if not cooldown_reminder_loop.is_running():
        cooldown_reminder_loop.start()

@bot.command(name='8ball')
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
    await ctx.reply(f'{random.choice(responses)}')

@bot.command(name='choose')
async def choose(ctx, *, options):
    """Choose between multiple options (separate with 'or')."""
    if ' or ' not in options:
        await ctx.reply("Please provide options separated by 'or' (e.g., k!choose pizza or burger or pasta)")
        return
    
    choices = [option.strip() for option in options.split(' or ')]
    if len(choices) < 2:
        await ctx.reply("Please provide at least two options separated by 'or'")
        return
    
    await ctx.reply(f"{random.choice(choices)}!")

@bot.group(name='minigame', invoke_without_command=True)
async def minigame(ctx):
    """Show the available minigames."""
    embed = discord.Embed(
        title="🎮 Minigames",
        description="Play a minigame with `k!minigame play <number>`.",
        color=0xff6b8b,
    )
    for number, (name, description) in enumerate(MINIGAMES, 1):
        embed.add_field(
            name=f"{number}. {name}",
            value=f"- {description}",
            inline=False,
        )
    await ctx.reply(embed=embed)

@minigame.command(name='play')
async def minigame_play(ctx, number: int):
    """Select a minigame by its number."""
    if number < 1 or number > len(MINIGAMES):
        await ctx.reply(
            f"Choose a minigame number from 1 to {len(MINIGAMES)}. "
            "Use `k!minigame` to see the list."
        )
        return

    name = MINIGAMES[number - 1][0]
    await ctx.reply(f"**{name}** isn't available yet. Check back later!")

@bot.command(name='daily')
async def daily(ctx):
    """Claim your daily COMO reward (24h cooldown)."""
    user_id = ctx.author.id
    username = str(ctx.author)
    today = datetime.datetime.now().date()

    # Retry up to 3 times if database is locked
    daily_card = generate_card(target=get_user_target(user_id))
    for attempt in range(3):
        try:
            with get_db() as conn:
                c = conn.cursor()
                # Acquire write lock immediately
                c.execute("BEGIN IMMEDIATE")

                # --- Check cooldown ---
                current_time = time.time()
                c.execute('''SELECT expires_at FROM cooldowns 
                             WHERE user_id=? AND cooldown_type=?''',
                          (user_id, 'daily'))
                row = c.fetchone()
                if row:
                    remaining = int(row[0] - current_time)
                    if remaining > 0:
                        # Still on cooldown
                        hours = remaining // 3600
                        minutes = (remaining % 3600) // 60
                        seconds = remaining % 60
                        await ctx.reply(
                            f"You've already claimed your daily COMO today! "
                            f"You can claim again in **{hours}h {minutes}m {seconds}s**."
                        )
                        return
                    else:
                        # Expired cooldown – delete it
                        c.execute('''DELETE FROM cooldowns 
                                     WHERE user_id=? AND cooldown_type=?''',
                                  (user_id, 'daily'))

                # --- Process daily claim ---
                # Check if user exists
                c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
                user = c.fetchone()

                if user:
                    last_daily = datetime.datetime.strptime(user[3], '%Y-%m-%d').date() if user[3] else None
                    current_streak = user[2]
                    current_como = user[4]
                    new_streak, streak_shield_used = advance_daily_streak(
                        c,
                        user_id,
                        last_daily,
                        today,
                        current_streak,
                    )

                    # Calculate reward
                    base_reward = random.randint(100, 200)
                    if new_streak >= 5:
                        reward = base_reward * 2
                        bonus_msg = " (2x streak bonus applied!)"
                    else:
                        reward = base_reward
                        bonus_msg = ""
                    if streak_shield_used:
                        bonus_msg += " (Streak Shield used!)"

                    new_como = current_como + reward

                    # Update user record
                    c.execute('''UPDATE users 
                                 SET username=?, daily_streak=?, last_daily=?, como=? 
                                 WHERE user_id=?''',
                              (username, new_streak, str(today), new_como, user_id))
                else:
                    # New user
                    reward = random.randint(100, 200)
                    new_streak = 1
                    new_como = reward
                    bonus_msg = ""
                    c.execute('''INSERT INTO users 
                                 (user_id, username, daily_streak, last_daily, como) 
                                 VALUES (?, ?, ?, ?, ?)''',
                              (user_id, username, new_streak, str(today), new_como))

                # Set 24h cooldown
                c.execute(
                    "INSERT INTO cards (serial, member_code, era, rarity, owner_id, obtained_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (daily_card['serial'], daily_card['member_code'], daily_card['era'], daily_card['rarity'], user_id, str(datetime.datetime.now())),
                )
                expires_at = time.time() + 86400
                c.execute('''INSERT OR REPLACE INTO cooldowns 
                             (user_id, cooldown_type, expires_at) 
                             VALUES (?, ?, ?)''',
                          (user_id, 'daily', expires_at))
                schedule_cooldown_reminder(
                    c,
                    user_id,
                    'daily',
                    expires_at,
                )

                # Commit everything
                conn.commit()

                await ctx.reply(
                    f"You've received **{reward} COMO**!{bonus_msg}\n"
                    f"Daily card: **{daily_card['rarity']} {daily_card['name']}** ({daily_card['serial']})\n"
                    f"Current streak: **{new_streak}** days\n"
                    f"Total COMO: **{new_como}**"
                )
                return  # Success – exit the retry loop

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                await asyncio.sleep(0.5 * (attempt + 1))  # backoff
                continue
            else:
                # Re-raise if it's not a lock error or we exhausted retries
                raise
        except Exception as e:
            print(f"Error in daily command: {e}")
            await ctx.reply("An error occurred. Please try again later.")
            return

@bot.command(name='balance', aliases=['como', 'bal'])
async def balance(ctx, user: discord.Member = None):
    """Check COMO balance for yourself or another user."""
    user = user or ctx.author
    user_id = user.id
    
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT como FROM users WHERE user_id=?", (user_id,))
            result = c.fetchone()
            
            if result:
                como = result[0]
                await ctx.reply(f"{user.display_name} has {como} COMO")
            else:
                if user.id == ctx.author.id:
                    await ctx.reply("You don't have a COMO balance yet. Use `k!daily` to get started!")
                else:
                    await ctx.reply(f"{user.display_name} doesn't have a COMO balance yet.")
    except Exception as e:
        print(f"Error in balance command: {e}")
        await ctx.reply("An error occurred. Please try again later.")

@bot.command(name='shop')
async def shop(ctx, *, query: str = ""):
    """View shop items or purchase an item with COMO."""
    parts = query.strip().split(maxsplit=1)
    if not parts:
        embed = discord.Embed(
            title="🛍️ Kotone Shop",
            description=(
                "Items go into your item inventory. View them with `k!items` "
                "and activate them with `k!use <item>`."
            ),
            color=0xff6b8b,
        )
        embed.add_field(
            name="🍀 Drop Luck Booster — 600 COMO",
            value=(
                "Boosts Rare, Epic, Legendary, and Mythic drop weights for 1 hour when used. "
                "Using another while active extends its duration.\n"
                "`k!shop buy booster`"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎴 Drop Cooldown Reset — 200 COMO",
            value="Use while `k!drop` is on cooldown to reset it.\n`k!shop buy drop`",
            inline=False,
        )
        embed.add_field(
            name="🔀 Merge Discount Token — 1,200 COMO",
            value=(
                "Activate it to merge 9 same-rarity cards instead of 10. "
                "It is consumed only when the merge is confirmed.\n"
                "`k!shop buy merge` then `k!use merge`"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛡️ Streak Shield — 800 COMO",
            value=(
                "Activate it to automatically protect your streak after missing "
                "exactly one day. It is consumed only when needed.\n"
                "`k!shop buy shield` then `k!use shield`"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎴 Extra Drop Slot — 400 COMO",
            value=(
                "Activate it to add one card to your next successful `k!drop`.\n"
                "`k!shop buy extra_drop` then `k!use extra_drop`"
            ),
            inline=False,
        )
        try:
            with get_db() as conn:
                c = conn.cursor()
                c.execute("SELECT como FROM users WHERE user_id=?", (ctx.author.id,))
                balance_row = c.fetchone()
                c.execute(
                    "SELECT expires_at FROM user_drop_boosters WHERE user_id=?",
                    (ctx.author.id,),
                )
                booster_row = c.fetchone()
            balance_amount = balance_row[0] if balance_row else 0
            embed.set_footer(text=f"Your balance: {balance_amount} COMO")
            if booster_row and booster_row[0] > time.time():
                remaining = max(0, int(booster_row[0] - time.time()))
                minutes, seconds = divmod(remaining, 60)
                embed.add_field(
                    name="Active booster",
                    value=f"{minutes}m {seconds}s remaining",
                    inline=False,
                )
            await ctx.reply(embed=embed)
        except sqlite3.Error as error:
            print(f"Database error while viewing shop: {error}")
            await ctx.reply("The shop couldn't be loaded due to a database error.")
        return

    action = parts[0].casefold()
    item_name = parts[1] if len(parts) > 1 else ""
    if action != "buy" or not item_name:
        await ctx.reply(
            "Use `k!shop` to view items or `k!shop buy <item>` to purchase one."
        )
        return
    item_key = SHOP_ITEM_ALIASES.get(item_name.strip().casefold().replace(" ", "_"))
    if item_key is None:
        await ctx.reply(
            "Unknown shop item. Use `k!shop` to see available items."
        )
        return

    try:
        new_balance = purchase_shop_item(ctx.author.id, item_key)
        await ctx.reply(
            f"Bought **{SHOP_ITEMS[item_key]['name']}** for "
            f"**{SHOP_ITEMS[item_key]['price']} COMO**. It's now in `k!items`. "
            f"Your balance is **{new_balance} COMO**."
        )
    except ValueError as error:
        await ctx.reply(str(error))
    except sqlite3.Error as error:
        print(f"Database error while purchasing shop item: {error}")
        await ctx.reply("The purchase couldn't be completed due to a database error.")

@bot.command(name='items')
async def items(ctx):
    """Show the items in your consumable inventory."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                '''SELECT item_key, quantity FROM user_items
                   WHERE user_id=? AND quantity>0 ORDER BY item_key''',
                (ctx.author.id,),
            )
            inventory = c.fetchall()
            c.execute(
                "SELECT expires_at FROM user_drop_boosters WHERE user_id=?",
                (ctx.author.id,),
            )
            booster = c.fetchone()
            c.execute(
                '''SELECT merge_discounts, streak_shields, extra_drop_slots
                   FROM user_item_effects WHERE user_id=?''',
                (ctx.author.id,),
            )
            active_effects = c.fetchone()

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Items",
            color=0xff6b8b,
        )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url,
        )
        if inventory:
            for item_key, quantity in inventory:
                item = SHOP_ITEMS.get(item_key)
                if item is not None:
                    embed.add_field(
                        name=item["name"],
                        value=f"Quantity: **{quantity}**\nUse: `k!use {item_key}`",
                        inline=False,
                    )
        elif (
            (not active_effects or not any(active_effects))
            and not (booster and booster[0] > time.time())
        ):
            embed.description = "You don't have any items yet. Visit `k!shop` to buy some."
        else:
            embed.description = "Your item inventory is empty; activated effects are listed below."

        if booster and booster[0] > time.time():
            remaining = max(0, int(booster[0] - time.time()))
            minutes, seconds = divmod(remaining, 60)
            embed.add_field(
                name="Active Drop Luck Booster",
                value=f"{minutes}m {seconds}s remaining",
                inline=False,
            )
        if active_effects:
            effect_labels = (
                ("Merge Discounts Ready", active_effects[0]),
                ("Streak Shields Armed", active_effects[1]),
                ("Extra Drop Slots Ready", active_effects[2]),
            )
            for label, quantity in effect_labels:
                if quantity:
                    embed.add_field(
                        name=label,
                        value=f"**{quantity}** ready",
                        inline=False,
                    )
        await ctx.reply(embed=embed)
    except sqlite3.Error as error:
        print(f"Database error while viewing items: {error}")
        await ctx.reply("Your items couldn't be loaded due to a database error.")

@bot.command(name='use')
async def use_item(ctx, *, item_name: str = ""):
    """Consume an item from your item inventory."""
    item_key = SHOP_ITEM_ALIASES.get(
        item_name.strip().casefold().replace(" ", "_")
    )
    if item_key is None:
        await ctx.reply(
            "Choose an item to use: `k!use booster`, `k!use drop`, "
            "`k!use merge`, `k!use shield`, or `k!use extra_drop`."
        )
        return

    try:
        confirmation = use_shop_item(ctx.author.id, item_key)
        await ctx.reply(f"{confirmation}.")
    except ValueError as error:
        await ctx.reply(str(error))
    except sqlite3.Error as error:
        print(f"Database error while using shop item: {error}")
        await ctx.reply("The item couldn't be used due to a database error.")
    except RuntimeError as error:
        print(f"Shop item use failed: {error}")
        await ctx.reply("The item couldn't be used. Please try again.")

@bot.command(name='drop')
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
                    await drop_msg.edit(embed=countdown_embed, view=view)

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
                await drop_msg.edit(embed=embed, view=view)
        
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
                "You need to activate a Merge Discount Token with `k!use merge` "
                "before merging 9 cards."
            )

    placeholders = ",".join("?" for _ in serials)
    cursor.execute(
        f'''SELECT serial, member_code, era, rarity, owner_id
            FROM cards WHERE serial IN ({placeholders})''',
        serials,
    )
    cards_by_serial = {row[0]: row for row in cursor.fetchall()}
    if len(cards_by_serial) != required_count:
        raise ValueError("One or more of those card serials could not be found.")

    selected_cards = [cards_by_serial[serial] for serial in serials]
    if any(card[4] != user_id for card in selected_cards):
        raise ValueError("You can only merge cards that you own.")

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
            url=get_card_image(era, member_code, rarity)
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

@bot.command(name='merge')
async def merge_cards(ctx, *, card_serials: str = ""):
    """Confirm a merge of selected owned cards into the next rarity."""
    serials = card_serials.replace(",", " ").split()
    if len(serials) not in {9, 10} or len(set(serials)) != len(serials):
        await ctx.reply(
            "Provide 10 different serials, or 9 after activating a Merge Discount Token. Example: "
            "`k!merge LJW-XXXXX KYY-XXXXX KAE-XXXXX ...`."
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

def normalize_era_alias(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())

ERA_ALIASES = {
    "ASSEMBLE": (
        "ASSEMBLE",
        "RISING",
    ),
    "ASSEMBLE24": (
        "ASSEMBLE24",
        "ASSEMBLE 24",
        "GND",
        "Girls Never Die",
        "S1-S24",
        "S1 to S24",
    ),
    "AAA": (
        "AAA",
        "Generation",
        "acid angel asia",
        "acid angel of asia",
        "asid angel of asia",
        "asid angel asia",
    ),
    "KRE": (
        "KRE",
        "Krystal Eyes",
        "+(KR)ystal Eyes",
        "Cherry Talk",
    ),
}
ERA_ALIAS_LOOKUP = {
    normalize_era_alias(alias): era
    for era, aliases in ERA_ALIASES.items()
    for alias in aliases
}

def create_collection_embed(
    user,
    era,
    rarity,
    owned_count,
    total_count,
    page=1,
    total_pages=1,
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
    def __init__(self, user, era, owned_by_rarity, default_rarity):
        super().__init__(timeout=180)
        self.user = user
        self.era = era
        self.owned_by_rarity = owned_by_rarity
        self.message = None
        self.selected_rarity = default_rarity
        self.current_page = 0
        self.total_pages = (
            (
                len(ERAS[era]["members"])
                + COLLECTION_MEMBERS_PER_PAGE
                - 1
            ) // COLLECTION_MEMBERS_PER_PAGE
            if era == "ASSEMBLE24"
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

@bot.command(name='collection')
async def collection(ctx, *, query: str = ""):
    """Show your owned cards for one era, with rarity filters."""
    parts = query.strip().split()
    if not parts:
        await ctx.reply(
            "Choose an era, optionally with a rarity. Example: "
            "`k!collection ASSEMBLE rare`."
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

@bot.command(name='inventory', aliases=['inv'])
async def inventory(ctx, *, query: str = ""):
    """View and filter your card inventory or another user's."""
    user = ctx.author
    query = query.strip()
    catalog_terms = {rarity.casefold() for rarity in RARITIES}
    catalog_terms.update(f"s{number}" for number in range(1, len(S_ORDER) + 1))
    for era_code, era_data in ERAS.items():
        catalog_terms.add(era_code.casefold())
        catalog_terms.add(era_data['name'].casefold())
        for member_code, member_data in era_data['members'].items():
            catalog_terms.add(member_code.casefold())
            for value in (member_data['name'], member_data['full_name']):
                catalog_terms.update(
                    value.casefold().replace('(', ' ').replace(')', ' ').split()
                )

    if ctx.message.mentions:
        user = ctx.message.mentions[0]
        for mentioned_user in ctx.message.mentions:
            query = query.replace(mentioned_user.mention, ' ')
            query = query.replace(f'<@{mentioned_user.id}>', ' ')
            query = query.replace(f'<@!{mentioned_user.id}>', ' ')
        query = query.strip()
    elif query and not all(
        term.casefold() in catalog_terms for term in query.replace(',', ' ').split()
    ):
        try:
            user = await commands.MemberConverter().convert(ctx, query)
            query = ''
        except commands.MemberNotFound:
            pass

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

@bot.command(name='view')
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

@bot.command(name='give', aliases=['gift', 'send'])
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

@bot.command(name='target')
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
                "Use `k!target clear` to remove it."
            )
        else:
            await ctx.reply(
                "Set a target with `k!target <member>`, optionally adding a rarity "
                "and/or era (for example, `k!target rare jiwoo`)."
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

@bot.command(name='bias')
async def bias_command(ctx, *, query: str = ""):
    """Set or clear the members shown as your profile biases."""
    query = query.strip()
    if not query:
        await ctx.reply(
            "Set your biases with `k!bias set jiwoo seoyeon yooyeon`, "
            "or clear them with `k!bias clear`."
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
            "Use `k!bias set <member names>` or `k!bias clear`."
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

@bot.command(name='profile')
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

@bot.command(name='bio')
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
        await ctx.reply("Use `k!bio set <your bio>` or `k!bio clear`.")
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

@bot.command(name='stats')
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

@bot.command(name='cooldown', aliases=['cd'])
async def cooldown(ctx):
    """Show the time remaining on your cooldowns."""
    cooldown_labels = {
        'daily': '📅 Daily',
        'weekly': '🗓️ Weekly',
        'drop': '🎴 Drop',
        'claim': '🙋 Claim',
    }
    now = time.time()

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

        embed = discord.Embed(title="Cooldowns", color=0xff6b8b)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        cooldown_types = list(cooldown_labels)
        cooldown_types.extend(sorted(
            set(active_cooldowns) - set(cooldown_labels)
        ))

        for cooldown_type in cooldown_types:
            expires_at = active_cooldowns.get(cooldown_type)
            if expires_at is None:
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

@bot.command(name='remind', aliases=['reminder', 'reminders'])
async def cooldown_reminders(ctx, *, options: str = ""):
    """Choose which cooldown resets should be sent to you by DM."""
    parts = options.casefold().split()
    if parts:
        if parts[0] != "all" and parts[0] not in COOLDOWN_REMINDER_TYPES:
            await ctx.reply(
                "Choose `daily`, `weekly`, `drop`, `claim`, or `all`."
            )
            return
        if len(parts) > 2 or (len(parts) == 2 and parts[1] not in {"on", "off"}):
            await ctx.reply(
                "Use `k!remind <daily|weekly|drop|claim|all> [on|off]`."
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
            "Use `k!remind daily` to enable one, "
            "`k!remind drop off` to disable one, or `k!remind all on/off`."
        )

@bot.command(name='help')
async def help_command(ctx):
    """Display help information about bot commands."""
    embed = discord.Embed(
        title="🦭 Kotone Bot Commands",
        description="Here are all the available commands:",
        color=0xff6b8b
    )
    
    embed.add_field(
        name="💰 Economy",
        value=(
            "`k!daily` - Claim daily COMO (streak bonuses!)\n"
            "`k!weekly` - Claim weekly COMO and a random card\n"
            "`k!cooldown` or `k!cd` - Check your active cooldowns\n"
            "`k!remind` or `k!reminder` - Choose cooldown reset DM reminders\n"
            "`k!balance` or `k!como` - Check your COMO balance\n"
            "`k!shop` - View items; `k!shop buy <item>` - Buy an item\n"
            "`k!items` - View your items; `k!use <item>` - Use an item from your inventory\n"
            "`k!transfer <@user> <amount>` - Send COMO to another user"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎴 Cards",
        value=(
            "`k!drop` - Drop 3 random cards (10min cooldown)\n"
            "`k!inventory` or `k!inv` - View your cards\n"
            "`k!view <serial>` - View detailed card info\n"
            "`k!merge <10 serials>` - Merge 10 owned cards; use a Merge Discount Token for 9\n"
            "`k!collection <era> [rarity]` - View your era collection; rarity can come before or after the era\n"
            "`k!give <@user> <serial>` - Give a card to someone\n"
            "`k!target <member>` - Set or change your single card target; `k!target clear` removes it\n"
            "`k!bias set <names or S numbers>` - Set multiple profile biases in S order; `k!bias clear` removes them\n"
            "`k!bio set <text>` - Set your profile bio; `k!bio clear` removes it\n"
            "`k!profile [@user]` - View a player profile\n"
            "`k!stats` - View your collection statistics"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🏪 Market",
        value=(
            "`k!market` - View cards for sale\n"
            "`k!mylistings` or `k!mymarket` - View only your market listings\n"
            "`k!list <serial> <price>` - List a card for sale\n"
            "`k!unlist <serial>` - Remove your listing\n"
            "`k!buy <serial>` - Buy a card from the market"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎮 Fun",
        value=(
            "`k!afk [reason]` - Set your AFK status; it clears when you speak again\n"
            "`k!minigame` - View minigames; `k!minigame play <number>` - Select a minigame\n"
            "`k!8ball <question>` - Ask the magic 8-ball\n"
            "`k!choose <option> or <option>` - Choose between options\n"
            "`k!rob` - Try to rob someone (just for fun!)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📝 Notes",
        value=(
            "• Claim cooldown: 5 minutes\n"
            "• Drop cooldown: 10 minutes\n"
            "• Daily streak bonus at 5+ days: 2x COMO\n"
            "• Dropper gets first claim on their drops"
        ),
        inline=False
    )
    
    await ctx.reply(embed=embed)

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

@bot.command(name='afk')
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

@bot.command(name='weekly')
async def weekly(ctx):
    """Claim your weekly COMO and random card reward (7-day cooldown)."""
    user_id = ctx.author.id
    username = str(ctx.author)
    weekly_card = generate_card(target=get_user_target(user_id))

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("BEGIN IMMEDIATE")

            c.execute('''SELECT expires_at FROM cooldowns
                         WHERE user_id=? AND cooldown_type=?''',
                      (user_id, 'weekly'))
            cooldown = c.fetchone()
            if cooldown:
                remaining = int(cooldown[0] - time.time())
                if remaining > 0:
                    days = remaining // 86400
                    hours = (remaining % 86400) // 3600
                    await ctx.reply(
                        f"You've already claimed your weekly reward! "
                        f"You can claim again in **{days}d {hours}h**."
                    )
                    return
                c.execute('''DELETE FROM cooldowns
                             WHERE user_id=? AND cooldown_type=?''',
                          (user_id, 'weekly'))

            # Get or create user
            c.execute("SELECT como FROM users WHERE user_id=?", (user_id,))
            user = c.fetchone()
            if user:
                current_como = user[0]
            else:
                # Create new user with 0 COMO
                c.execute('''INSERT INTO users (user_id, username, daily_streak, last_daily, como)
                             VALUES (?, ?, 0, NULL, 0)''',
                          (user_id, username))
                current_como = 0

            # Reward: 500-1000 COMO (more than daily)
            reward = random.randint(500, 1000)
            new_como = current_como + reward

            # Update balance
            c.execute("UPDATE users SET como=? WHERE user_id=?", (new_como, user_id))

            c.execute(
                '''INSERT INTO cards
                   (serial, member_code, era, rarity, owner_id, obtained_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    weekly_card['serial'],
                    weekly_card['member_code'],
                    weekly_card['era'],
                    weekly_card['rarity'],
                    user_id,
                    str(datetime.datetime.now()),
                ),
            )

            # Set 7-day cooldown
            expires_at = time.time() + 604800
            c.execute("INSERT OR REPLACE INTO cooldowns (user_id, cooldown_type, expires_at) VALUES (?, ?, ?)", (user_id, 'weekly', expires_at))
            schedule_cooldown_reminder(
                c,
                user_id,
                'weekly',
                expires_at,
            )

            conn.commit()

        await ctx.reply(
            f"You've received your weekly reward of **{reward} COMO**! "
            f"Total COMO: **{new_como}**\n"
            f"Weekly card: **{weekly_card['rarity']} {weekly_card['name']}** "
            f"({weekly_card['serial']})"
        )

    except Exception as e:
        print(f"Error in weekly command: {e}")
        await ctx.reply("An error occurred. Please try again later.")

@bot.command(name='market', aliases=['listing', 'mylistings', 'mylisting', 'mymarket'])
async def market(ctx):
    """View all market listings, or only your own with k!mylistings."""
    own_listings_only = ctx.invoked_with in ('mylistings', 'mylisting', 'mymarket')

    try:
        with get_db() as conn:
            c = conn.cursor()
            query = '''SELECT m.card_serial, m.price, m.seller_id, m.listed_at,
                              c.member_code, c.era, c.rarity
                       FROM market_listings m
                       JOIN cards c ON m.card_serial = c.serial'''
            if own_listings_only:
                query += " WHERE m.seller_id=?"
            query += " ORDER BY m.listed_at DESC"
            params = (ctx.author.id,) if own_listings_only else ()
            c.execute(query, params)
            listings = c.fetchall()

        if not listings:
            if own_listings_only:
                await ctx.reply("You don't have any cards listed on the market.")
                return
            await ctx.reply("The market is empty. List a card with `k!list <serial> <price>`!")
            return

        # Create paginated view (reuse InventoryView-like structure)
        # We'll make a simple view with page buttons
        class MarketView(View):
            def __init__(self, listings, ctx):
                super().__init__(timeout=120)
                self.listings = listings
                self.ctx = ctx
                self.current_page = 0
                self.items_per_page = 5
                self.total_pages = (len(listings) + self.items_per_page - 1) // self.items_per_page
                self.update_buttons()

            def update_buttons(self):
                self.children[0].disabled = self.current_page == 0
                self.children[1].disabled = self.current_page >= self.total_pages - 1

            def get_embed(self):
                embed = discord.Embed(
                    title=(
                        "🏪 Your Market Listings"
                        if self.ctx.invoked_with in ('mylistings', 'mylisting', 'mymarket')
                        else "🏪 Market Listings"
                    ),
                    description=f"Page {self.current_page + 1}/{self.total_pages} • Total: {len(self.listings)} cards",
                    color=0x00ff00
                )
                start = self.current_page * self.items_per_page
                end = min(start + self.items_per_page, len(self.listings))
                for i in range(start, end):
                    serial, price, seller_id, listed_at, member_code, era, rarity = self.listings[i]
                    try:
                        member_name = ERAS[era]['members'][member_code]['name']
                        era_name = ERAS[era]['name']
                    except KeyError:
                        member_name = "Unknown"
                        era_name = "Unknown"
                    # Get seller name
                    with get_db() as conn2:
                        c2 = conn2.cursor()
                        c2.execute("SELECT username FROM users WHERE user_id=?", (seller_id,))
                        seller_row = c2.fetchone()
                        seller_name = seller_row[0] if seller_row else "Unknown"
                    embed.add_field(
                        name=f"{serial} - {member_name}",
                        value=f"Era: {era_name} • Rarity: {rarity}\nPrice: **{price} COMO** • Seller: {seller_name}",
                        inline=False
                    )
                return embed

            @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary)
            async def prev_button(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != self.ctx.author.id:
                    await interaction.response.send_message("This is not your market view!", ephemeral=True)
                    return
                self.current_page -= 1
                self.update_buttons()
                await interaction.response.edit_message(embed=self.get_embed(), view=self)

            @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
            async def next_button(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != self.ctx.author.id:
                    await interaction.response.send_message("This is not your market view!", ephemeral=True)
                    return
                self.current_page += 1
                self.update_buttons()
                await interaction.response.edit_message(embed=self.get_embed(), view=self)

        view = MarketView(listings, ctx)
        embed = view.get_embed()
        await ctx.reply(embed=embed, view=view)

    except Exception as e:
        print(f"Error in market command: {e}")
        await ctx.reply("An error occurred while fetching the market.")

@bot.command(name='list')
async def list_card(ctx, serial: str, price: int):
    """List a card for sale at a given price (COMO)."""
    if price <= 0:
        await ctx.reply("Price must be a positive integer!")
        return

    user_id = ctx.author.id

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("BEGIN IMMEDIATE")

            # 1. Verify the card exists and belongs to the user
            c.execute('''SELECT owner_id FROM cards WHERE serial=?''', (serial,))
            row = c.fetchone()
            if not row:
                await ctx.reply("Card not found!")
                return
            if row[0] != user_id:
                await ctx.reply("You don't own this card!")
                return

            # 2. Check if already listed
            c.execute('''SELECT 1 FROM market_listings WHERE card_serial=?''', (serial,))
            if c.fetchone():
                await ctx.reply("This card is already on the market!")
                return

            # 3. Insert listing
            listed_at = str(datetime.datetime.now())
            c.execute('''INSERT INTO market_listings (card_serial, seller_id, price, listed_at)
                         VALUES (?, ?, ?, ?)''',
                      (serial, user_id, price, listed_at))

            conn.commit()

        await ctx.reply(f"✅ Your card **{serial}** has been listed for **{price} COMO**!")

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            await ctx.reply("The market is busy, please try again in a moment.")
        else:
            raise
    except Exception as e:
        print(f"Error in list command: {e}")
        await ctx.reply("An error occurred while listing the card.")

@bot.command(name='unlist')
async def unlist_card(ctx, serial: str):
    """Remove your card from the market."""
    user_id = ctx.author.id

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("BEGIN IMMEDIATE")

            # Check listing exists and belongs to user
            c.execute('''SELECT seller_id FROM market_listings WHERE card_serial=?''', (serial,))
            row = c.fetchone()
            if not row:
                await ctx.reply("This card is not listed on the market.")
                return
            if row[0] != user_id:
                await ctx.reply("You didn't list this card!")
                return

            # Delete listing
            c.execute('''DELETE FROM market_listings WHERE card_serial=?''', (serial,))
            conn.commit()

        await ctx.reply(f"✅ Your listing for **{serial}** has been removed.")

    except Exception as e:
        print(f"Error in unlist command: {e}")
        await ctx.reply("An error occurred while removing the listing.")

@bot.command(name='buy')
async def buy_card(ctx, serial: str):
    """Buy a card from the market using COMO."""
    buyer_id = ctx.author.id

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("BEGIN IMMEDIATE")

            # 1. Get listing details
            c.execute('''SELECT seller_id, price FROM market_listings WHERE card_serial=?''', (serial,))
            listing = c.fetchone()
            if not listing:
                await ctx.reply("This card is not listed for sale.")
                return
            seller_id, price = listing

            if seller_id == buyer_id:
                await ctx.reply("You already own this card – you can't buy your own listing!")
                return

            # 2. Get buyer's balance
            c.execute("SELECT como FROM users WHERE user_id=?", (buyer_id,))
            buyer_row = c.fetchone()
            buyer_balance = buyer_row[0] if buyer_row else 0
            if buyer_balance < price:
                await ctx.reply(f"Insufficient COMO! You have {buyer_balance}, but the card costs {price}.")
                return

            # 3. Get seller's balance
            c.execute("SELECT como FROM users WHERE user_id=?", (seller_id,))
            seller_row = c.fetchone()
            seller_balance = seller_row[0] if seller_row else 0

            # 4. Verify card still owned by seller (defensive)
            c.execute("SELECT owner_id FROM cards WHERE serial=?", (serial,))
            card_owner = c.fetchone()
            if not card_owner or card_owner[0] != seller_id:
                await ctx.reply("The seller no longer owns this card. Listing removed.")
                c.execute("DELETE FROM market_listings WHERE card_serial=?", (serial,))
                conn.commit()
                return

            # 5. Perform transaction
            new_buyer_balance = buyer_balance - price
            new_seller_balance = seller_balance + price

            # Update balances
            c.execute("UPDATE users SET como=? WHERE user_id=?", (new_buyer_balance, buyer_id))
            c.execute("UPDATE users SET como=? WHERE user_id=?", (new_seller_balance, seller_id))

            # Transfer card ownership
            c.execute('''UPDATE cards SET owner_id=?, obtained_at=? 
                         WHERE serial=?''',
                      (buyer_id, str(datetime.datetime.now()), serial))

            # Remove listing
            c.execute("DELETE FROM market_listings WHERE card_serial=?", (serial,))

            conn.commit()

        # Get card name for response
        try:
            with get_db() as conn2:
                c2 = conn2.cursor()
                c2.execute("SELECT member_code, era, rarity FROM cards WHERE serial=?", (serial,))
                card_data = c2.fetchone()
                if card_data:
                    member_code, era, rarity = card_data
                    member_name = ERAS[era]['members'][member_code]['name']
                    card_desc = f"{rarity} {member_name}"
                else:
                    card_desc = serial
        except:
            card_desc = serial

        await ctx.reply(
            f"✅ Purchase successful! {ctx.author.mention} bought **{card_desc}** ({serial}) "
            f"for **{price} COMO** from <@{seller_id}>."
        )

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            await ctx.reply("The market is busy, please try again in a moment.")
        else:
            raise
    except Exception as e:
        print(f"Error in buy command: {e}")
        await ctx.reply("An error occurred while processing the purchase.")

# -------------------- NEW COMMANDS --------------------

@bot.command(name='rob')
async def rob(ctx, user: discord.Member = None):
    """Funny easter egg: no robbing allowed!"""
    responses = [
        "Hey you are not allowed to rob!",
        "No robbing please :(",
        "Don't rob!!",
        "We don't do that here :((",
        "Robbing is illegal! 🚨",
        "You can't steal COMO! Be nice!",
        "I'm calling the police! 👮",
        "Nice try! But no.",
        "That's not how we do things here.",
        "Please don't rob, it's not cool."
    ]
    if user:
        await ctx.reply(f"{random.choice(responses)} (and don't bother {user.display_name} either!)")
    else:
        await ctx.reply(random.choice(responses))

@bot.command(name='transfer')
async def transfer(ctx, recipient: discord.Member, amount: int):
    """Transfer COMO to another user."""
    sender_id = ctx.author.id
    recipient_id = recipient.id

    if sender_id == recipient_id:
        await ctx.reply("You can't transfer COMO to yourself!")
        return

    if amount <= 0:
        await ctx.reply("Amount must be a positive integer!")
        return

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("BEGIN IMMEDIATE")

            # Get sender's balance
            c.execute("SELECT como FROM users WHERE user_id=?", (sender_id,))
            sender_row = c.fetchone()
            if not sender_row:
                await ctx.reply("You don't have any COMO yet. Use `k!daily` to get some!")
                return
            sender_balance = sender_row[0]
            if sender_balance < amount:
                await ctx.reply(f"You don't have enough COMO! You have {sender_balance}.")
                return

            # Get recipient's balance (or create if not exists)
            c.execute("SELECT como FROM users WHERE user_id=?", (recipient_id,))
            recipient_row = c.fetchone()
            if recipient_row:
                recipient_balance = recipient_row[0]
            else:
                # Create user with 0 COMO
                c.execute('''INSERT INTO users (user_id, username, daily_streak, last_daily, como)
                             VALUES (?, ?, 0, NULL, 0)''',
                          (recipient_id, str(recipient)))
                recipient_balance = 0

            # Update balances
            new_sender = sender_balance - amount
            new_recipient = recipient_balance + amount
            c.execute("UPDATE users SET como=? WHERE user_id=?", (new_sender, sender_id))
            c.execute("UPDATE users SET como=? WHERE user_id=?", (new_recipient, recipient_id))

            conn.commit()

        await ctx.reply(f"✅ Successfully transferred **{amount} COMO** to {recipient.mention}!")

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            await ctx.reply("The system is busy, please try again in a moment.")
        else:
            raise
    except Exception as e:
        print(f"Error in transfer command: {e}")
        await ctx.reply("An error occurred while processing the transfer.")

# -------------------------------------------------------

@bot.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == bot.user:
        return

    afk_responses = []
    if message.guild is not None:
        message_parts = message.content.split(maxsplit=1)
        is_afk_command = bool(
            message_parts and message_parts[0].casefold() == "k!afk"
        )
        mentioned_users = {
            user.id: user
            for user in message.mentions
            if user.id != message.author.id and not user.bot
        }
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                if not is_afk_command:
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

    # Process commands after checking for greetings
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("Invalid argument provided. Please check your command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    else:
        print(f"Error in command {ctx.command}: {error}")
        await ctx.reply("An unexpected error occurred. Please try again later.")

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