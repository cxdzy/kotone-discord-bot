from eras import ERAS


RARITIES = {
    "Common": 100000,
    "Rare": 44203,
    "Epic": 580,
    "Legendary": 10,
    "Mythic": 1,
}
SPIN_DAILY_LIMIT = 5
SPIN_REWARD_COUNTS = {
    "Common": {
        "Common": 8,
        "Rare": 4,
        "Epic": 2,
        "Legendary": 1,
        "Mythic": 0,
    },
    "Rare": {
        "Common": 6,
        "Rare": 4,
        "Epic": 3,
        "Legendary": 2,
        "Mythic": 0,
    },
    "Epic": {
        "Common": 5,
        "Rare": 4,
        "Epic": 3,
        "Legendary": 2,
        "Mythic": 1,
    },
    "Legendary": {
        "Common": 3,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 3,
        "Mythic": 2,
    },
    "Mythic": {
        "Common": 2,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 4,
        "Mythic": 2,
    },
}
SPIN_BOMB_SLOTS = 1
SPIN_BOARD_SIZE = 16

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
    (
        "tripleS Trivia",
        "Answer tripleS trivia questions to earn COMO.",
        "/trivia",
    ),
)
