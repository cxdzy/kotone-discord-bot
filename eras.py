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
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa-hyerin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin%20aaa%20epic.png",
                    "Legendary": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin-AAA-legendary-preview.png"
                },
                "animated_images": {"Legendary": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin-AAA-legendary.gif"},
            },
            "KYY": {
                "name": "Yooyeon",
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20kyy%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa-yooyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yooyeon%20aaa%20epic.png",
                    "Legendary": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/yooyeon%20aaa%20L%20preview.png",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/yooyeon%20aaa%20l.gif"},
            },
            "KNK": {
                "name": "Nakyoung",
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20knk%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa-nakyoung-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/nakyoung%20aaa%20epic.png",
                    "Legendary": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/nakyoung%20aaa%20L%20preview.png",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/nakyoung%20aaa%20l.gif"},
            },
            "GYB": {
                "name": "Yubin",
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa%20gyb%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/aaa-yubin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yubin%20aaa%20epic.png",
                    "Legendary": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/yubin%20aaa%20L%20preview.png",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/yubin%20aaa%20l.gif"},
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
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-seoyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/seoyeon%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-seoyeon-402z-1782342601718.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "JHR": {
                "name": "Hyerin",
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20jhr%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-hyerin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin%20assemble%20epic.png",
                    "Legendary": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin-AAA-legendary-preview.png",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin-AAA-legendary.gif"},
            },
            "LJW": {
                "name": "Jiwoo",
                "full_name": "Lee Jiwoo",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20ljw%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-jiwoo-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/jiwoo%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-jiwoo-402z-1782343067344.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KCY": {
                "name": "Chaeyeon",
                "full_name": "Kim Chaeyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20kcy%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-chaeyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/chaeyeon%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-chaeyeon-402z-1782343868867.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KYY": {
                "name": "Yooyeon",
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20kyy%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-yooyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yooyeon%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-yooyeon-402z-1782344712343.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KSM": {
                "name": "Soomin",
                "full_name": "Kim Soomin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20ksm%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-soomin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/soomin%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-soomin-402z-1782339995617.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KNK": {
                "name": "Nakyoung",
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20knk%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-nakyoung-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/nakyoung%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-nakyoung-402z-1782340614290.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "GYB": {
                "name": "Yubin",
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20gyb%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-yubin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yubin%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-yubin-402z-1782344112134.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KAE": {
                "name": "Kaede",
                "full_name": "Yamada Kaede",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20kae%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-kaede-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kaede%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-kaede-402z-1782343301941.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "SDH": {
                "name": "Dahyun",
                "full_name": "Seo Dahyun",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble%20sdh%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble-dahyun-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/dahyun%20assemble%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/ever01-dahyun-402z-1782342791953.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
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
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre-seoyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20seoyeon%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-seoyeon-402z-1782342482866.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "LJW": {
                "name": "Jiwoo",
                "full_name": "Lee Jiwoo",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20ljw%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre-jiwoo-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20jiwoo%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/cream02-jiwoo-402z-1782339924657.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KCY": {
                "name": "Chaeyeon",
                "full_name": "Kim Chaeyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20kcy%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre-chaeyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20chaeyeon%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/atom02-chaeyeon-402z-1782344412320.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KSM": {
                "name": "Soomin",
                "full_name": "Kim Soomin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20ksm%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre-soomin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kre%20soomin%20epic.png",
                    "Legendary": "https://media.objekt.top/collection-images/front/binary02-soomin-402z-1782344378764.webp",
                    "Mythic": "https://media.discordapp.net/attachments/1335162578246041680/1559917581484302366/5bb48508-dd83-4c61-a0ed-8029bcff3cd6.png?ex=6ad0d1f5&is=6acf8075&hm=f8c6e26aae76d7531d714cdad1f2472a2544294532b97352d25ac0959fe1946a&=&format=webp&quality=lossless"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
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
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-seoyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/seoyeon%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "JHR": {
                "name": "Hyerin",
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20HYERIN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-hyerin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hyerin%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "LJW": {
                "name": "Jiwoo",
                "full_name": "Lee Jiwoo",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20JIWOO.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-jiwoo-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/jiwoo%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KCY": {
                "name": "Chaeyeon",
                "full_name": "Kim Chaeyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20CHAEYEON.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-chaeyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/chaeyeon%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KYY": {
                "name": "Yooyeon",
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20YOOYEON.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-yooyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yooyeon%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KSM": {
                "name": "Soomin",
                "full_name": "Kim Soomin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SOOMIN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-soomin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/soomin%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KNK": {
                "name": "Nakyoung",
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20NAKYOUNG.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-nakyoung-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/nakyoung%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "GYB": {
                "name": "Yubin",
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20YUBIN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-yubin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yubin%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KAE": {
                "name": "Kaede",
                "full_name": "Yamada Kaede",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20KAEDE.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-kaede-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kaede%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "SDH": {
                "name": "Dahyun",
                "full_name": "Seo Dahyun",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20DAHYUN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-dahyun-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/dahyun%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KTN": {
                "name": "Kotone",
                "full_name": "Kamimoto Kotone",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20KOTONE.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-kotone-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/kotone%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KYJ": {
                "name": "Yeonji",
                "full_name": "Kwak Yeonji",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20YEONJI.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-yeonji-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/yeonji%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "HST": {
                "name": "Nien",
                "full_name": "Hsu Nien Tzu",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20NIEN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-nien-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/nien%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "PSH": {
                "name": "Sohyun",
                "full_name": "Park Sohyun",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SOHYUN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-sohyun-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/sohyun%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "ZXY": {
                "name": "Xinyu",
                "full_name": "Zhou Xinyu",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20XINYU.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-xinyu-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/xinyu%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KMY": {
                "name": "Mayu",
                "full_name": "Koma Mayu",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20MAYU.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-mayu-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/mayu%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "LYN": {
                "name": "Lynn",
                "full_name": "Kawakami Lynn",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20LYNN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-lynn-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/lynn%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "JBN": {
                "name": "Joobin",
                "full_name": "Joo Bin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20JOOBIN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-joobin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/joobin%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "JHY": {
                "name": "Hayeon",
                "full_name": "Jeong Hayeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20HAYEON.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-hayeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/hayeon%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "SHI": {
                "name": "Shion",
                "full_name": "Park Shion",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SHION.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-shion-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/shion%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "KCW": {
                "name": "Chaewon",
                "full_name": "Kim Chaewon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20CHAEWON.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-chaewon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/chaewon%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "SUL": {
                "name": "Sullin",
                "full_name": "Pirada Bunraksa",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SULLIN.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-sullin-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/sullin%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "SEO": {
                "name": "Seoah",
                "full_name": "Jeong Haerin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20SEOAH.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-seoah-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/seoah%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            },
            "JSH": {
                "name": "Jiyeon",
                "full_name": "Ji Suhyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/ASSEMBLE24%20JIYEON.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/assemble24-jiyeon-r.png",
                    "Epic": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/jiyeon%20assemble24%20epic.png",
                    "Legendary": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&",
                    "Mythic": "https://cdn.discordapp.com/attachments/1335162578246041680/1559959802896060516/4d9fba29-2611-4e3e-a12a-b38d9d16b12b.png?ex=6ad0f947&is=6acfa7c7&hm=ed65212f4b455c4361159a4a85c2d7e232979e8fae5b20e60de481e407910832&"
                },
                "animated_images": {"Legendary": "https://www.example.com/gifexample"},
            }
        }
    },
    "VV": {
        "name": "VV",
        "members": {
            "JHR": {
                "name": "Hyerin",
                "full_name": "Jeong Hyerin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20hyerin%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20hyerin%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20hyerin%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "KYY": {
                "name": "Yooyeon",
                "full_name": "Kim Yooyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20yooyeon%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20yooyeon%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20yooyeon%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "KNK": {
                "name": "Nakyoung",
                "full_name": "Kim Nakyoung",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20nakyoung%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20nakyoung%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20nakyoung%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "GYB": {
                "name": "Yubin",
                "full_name": "Gong Yubin",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20yubin%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20yubin%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20yubin%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "KAE": {
                "name": "Kaede",
                "full_name": "Yamada Kaede",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20kaede%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20kaede%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20kaede%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "KTN": {
                "name": "Kotone",
                "full_name": "Kamimoto Kotone",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20kotone%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20kotone%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20kotone%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "KYJ": {
                "name": "Yeonji",
                "full_name": "Kwak Yeonji",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20yeonji%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20yeonji%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20yeonji%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "HST": {
                "name": "Nien",
                "full_name": "Hsu Nien Tzu",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20nien%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20nien%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20nien%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "PSH": {
                "name": "Sohyun",
                "full_name": "Park Sohyun",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20sohyun%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20sohyun%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20sohyun%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "ZXY": {
                "name": "Xinyu",
                "full_name": "Zhou Xinyu",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20xinyu%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20xinyu%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20xinyu%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "LYN": {
                "name": "Lynn",
                "full_name": "Kawakami Lynn",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20lynn%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20lynn%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20lynn%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
            "JSH": {
                "name": "Jiyeon",
                "full_name": "Ji Suhyeon",
                "images": {
                    "Common": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20jiyeon%20c.png",
                    "Rare": "https://gejzwuqlkaggzdmbgdsd.supabase.co/storage/v1/object/public/kotone%20bot/vv%20jiyeon%20r.png",
                    "Epic": "https://pub-6b36c51f5c9a4d9c884ee896543879d9.r2.dev/vv%20jiyeon%20e.png",
                    "Legendary": "https://example.com/example.jpg",
                    "Mythic": "https://example.com/example.jpg",
                },
                "animated_images": {},
            },
        },
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
    "VV": (
        "VV",
        "Visionary Vision",
        "Hit The Floor",
        "HTF",
        "Perfomante",
    ),
}
ERA_ALIAS_LOOKUP = {
    normalize_era_alias(alias): era
    for era, aliases in ERA_ALIASES.items()
    for alias in aliases
}
