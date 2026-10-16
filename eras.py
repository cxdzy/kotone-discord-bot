import re

# Card data with eras
ERAS = {
    "AAA": {
        "name": "AAA",
        "members": {
            "JHR": {
                "name": "Hyerin",
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20jhr%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20kyy%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20knk%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20gyb%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20ysy%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20jhr%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20ljw%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20kcy%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20kyy%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20ksm%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20knk%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20gyb%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20kae%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20sdh%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20ysy%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20ljw%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20kcy%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20ksm%20c.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SEOYEON.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20HYERIN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20JIWOO.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20CHAEYEON.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20YOOYEON.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SOOMIN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20NAKYOUNG.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20YUBIN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20KAEDE.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20DAHYUN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20KOTONE.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20YEONJI.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20NIEN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SOHYUN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20XINYU.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20MAYU.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20LYNN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20JOOBIN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20HAYEON.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SHION.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20CHAEWON.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SULLIN.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SEOAH.png",
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
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20JIYEON.png",
                    "Rare": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Epic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                }
            }
        }
    }
}


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
