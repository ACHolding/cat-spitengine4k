"""AC Holdings • Partners in Time — single-file pygame RPG (files=off). Python 3.14+. Play / Reset.

DS-style PiT enemy sprites (goombas, toads, shroobs, etc.) built in-memory at runtime — files=off.
Maps sourced from Mario Wiki PiT locations:
https://www.mariowiki.com/Category:Mario_%26_Luigi:_Partners_in_Time_locations
"""
from __future__ import annotations

import random
import sys

import pygame

pygame.init()
WIDTH, HEIGHT = 1024, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AC Holdings • Partners in Time")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 36, bold=True)
small_font = pygame.font.SysFont("consolas", 22)
tiny_font = pygame.font.SysFont("consolas", 18)

AC_GREEN = (0, 255, 120)
GROK_PINK = (255, 100, 200)
TOAD_RED = (220, 30, 30)
MENU_BG = (10, 20, 40)
HUD_BG = (20, 30, 60)
BATTLE_BG = (15, 25, 50)
WHITE = (255, 255, 255)
GOLD = (255, 220, 0)

GRASS_PRESENT = (34, 139, 34)
PATH_PRESENT = (139, 90, 43)
WATER_PRESENT = (0, 105, 148)
GRASS_PAST = (115, 118, 63)
PATH_PAST = (90, 65, 40)
WATER_PAST = (210, 65, 15)
GRASS_FUTURE = (25, 20, 55)
PATH_FUTURE = (0, 220, 255)
WATER_FUTURE = (130, 0, 180)
HOUSE = (180, 120, 80)
ROOF = (120, 40, 40)

ERAS = ("PAST", "PRESENT", "FUTURE")
MAP_W, MAP_H = 48, 28

# Tile legend: .=grass =path ~=water !=lava %=yoob ^=forest H=house C=castle F=factory
#   @=warp  *=Cobalt shard  e=enemy  S=Shroom Shop  ?=NPC  :=baby pipe  B=boss door
PIT_PARTS = (
    "Intro story", "Overworld + time travel", "12+ Mario Wiki maps", "Turn-based battles",
    "Bros attacks (Shell/Drill/Trampoline)", "Items + Shroom Shop", "Cobalt Star quest",
    "Shard bosses", "Final boss (Elder Shroob)", "Map screen", "Party status", "NPC dialogue",
    "Baby pipes", "Play / Reset", "Victory / Game Over",
)

BROS_MOVES = (
    ("Green Shell", 18, 2),
    ("Red Shell", 22, 3),
    ("Baby Drill", 26, 4),
    ("Trampoline", 20, 3),
)

SHOP_STOCK = (
    ("Super Shroom", 15, "heal20"),
    ("Max Mushroom", 35, "healfull"),
    ("1-Up", 50, "revive"),
    ("Syrup Jar", 10, "bp3"),
)

BOSS_BY_ERA = {
    "PAST": ("Sunnycleft", 70, 14),
    "PRESENT": ("Swiggler", 85, 15),
    "FUTURE": ("Commander Shroob", 100, 16),
}
FINAL_BOSS = ("Elder Princess Shroob", 180, 20)

NPC_LINES: dict[str, list[str]] = {
    "Hollijolli Village": ["The Shroobs attacked our village!", "Baby partners can fit in small pipes (:)."],
    "Toadwood Forest": ["Toads are being drained here...", "Collect all Cobalt Star shards!"],
    "Shroom Shop": ["Welcome to Shroom Shop!", "Mushrooms heal. Syrup restores BP."],
    "Star Shrine": ["Three shards gathered?", "The Elder Shroob awaits beyond the B door."],
}


def _quick_map(name: str, wiki: str, mid: str, start: tuple[int, int], shop: bool = False) -> dict:
    rows = ["~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"] * MAP_H
    rows[1] = "~~~~~~....========....========....========....~~"
    rows[2] = "~~~~~~....=..=....=..=....=..=....=..=....~~~~.."
    rows[3] = f"~~~~~~....=..{mid}=..=....=..=....=..=....~~~~.."
    rows[4] = "~~~~~~....=..=....=.@=....=..=....=..=....~~~~.."
    rows[5] = "~~~~~~....====....====....====....====....~~~~.."
    rows[7] = "~~~~~~....eeee........eeee........eeee....~~~~.."
    if shop:
        rows[6] = "~~~~~~....SSSS........====........SSSS....~~~~.."
    return {"name": name, "wiki": wiki, "rows": rows, "start": start, "shard": None, "shop": shop}


def _extend_pit_locations() -> None:
    PIT_LOCATIONS["PRESENT"].extend([
        _quick_map("Toad Town", "Toad Town (Mario & Luigi: Partners in Time)", "??", (20, 3)),
        {"name": "Shroom Shop", "wiki": "Shroom Shop", "shop": True, "rows": [
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
            "~~~~~~....SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS....~~~~",
            "~~~~~~....S....========....========....S....~~~~",
            "~~~~~~....S....=..??..=....=..=....S....~~~~..",
            "~~~~~~....S....=......=....=.@.=....S....~~~~..",
            "~~~~~~....S....========....========....S....~~~~",
            "~~~~~~....SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS....~~~~",
        ] + ["~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"] * 10, "start": (22, 3), "shard": None},
        _quick_map("Star Hill", "Star Hill", "==", (18, 3)),
        _quick_map("Monty Mart", "Monty Mart", "HH", (16, 3), shop=True),
        _quick_map("Gritzy Caves", "Gritzy Caves", "!!", (14, 3)),
        _quick_map("Koopaseum", "Koopaseum", "CC", (20, 3)),
        _quick_map("Bowser's Castle", "Bowser's Castle (Mario & Luigi: Partners in Time)", "CC", (22, 3)),
    ])
    PIT_LOCATIONS["PAST"].extend([
        _quick_map("Gritzy Caves", "Gritzy Caves", "!!", (16, 3)),
        _quick_map("Koopaseum", "Koopaseum", "CC", (18, 3)),
        _quick_map("Gramma's Place", "Gramma's Place", "HH", (20, 3)),
        _quick_map("Peach's Dungeon", "Peach's Castle Dungeon", "CC", (22, 3)),
    ])
    PIT_LOCATIONS["FUTURE"].extend([
        _quick_map("Fawful's Bean 'n' Badge", "Fawful's Bean 'n' Badge", "FF", (18, 3), shop=True),
    ])


PIT_LOCATIONS: dict[str, list[dict]] = {
    "PRESENT": [
        {
            "name": "Hollijolli Village",
            "wiki": "Hollijolli Village",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~..........==========..........~~~~~~......",
                "~~~~~~..........=........=..........~~~~~~......",
                "~~~~~~....HH....=...**...=....HH....~~~~~~......",
                "~~~~~~....##....=...?...=....##....~~~~~~......",
                "~~~~~~..........====.@.====..........~~~~~~......",
                "~~~~~~..............................~~~~~~......",
                "~~~~~~....####................####....~~~~~~....",
                "~~~~~~....#..#....eeee....#..#....~~~~~~........",
                "~~~~~~....####................####....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~....HH........====........HH....~~~~~~~~..",
                "~~~~~~....##........=..=........##....~~~~~~~~..",
                "~~~~~~..............=..=..............~~~~~~~~..",
                "~~~~~~..............=..=..............~~~~~~~~..",
                "~~~~~~..............................~~~~~~~~~~~~",
            ],
            "start": (24, 8),
            "shard": (19, 3),
        },
        {
            "name": "Toadwood Forest",
            "wiki": "Toadwood Forest",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^~~....",
                "~~~~~~^^^....====....^^^^....====....^^^~~~~~~..",
                "~~~~~~^^^....=..=....^^^^....=..=....^^^~~~~~~..",
                "~~~~~~^^^....=..=....^^^^....=..=....^^^~~~~~~..",
                "~~~~~~...=====.@.=..........=..=..........~~~~..",
                "~~~~~~...=........eeee........eeee........~~~~..",
                "~~~~~~...=....^^^^^^^^^^^^^^^^....====....~~~~..",
                "~~~~~~...=....^^..........^^....=..=....~~~~..",
                "~~~~~~...=====..............====....~~~~~~......",
                "~~~~~~..........................................",
                "~~~~~~....^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....",
                "~~~~~~....^^....====....^^^^....====....^^....",
                "~~~~~~....^^....=..=....^^^^....=..=....^^....",
                "~~~~~~...........=..=...........=..=..........",
                "~~~~~~...........====...........====..........",
            ],
            "start": (10, 5),
            "shard": None,
        },
        {
            "name": "Peach's Castle",
            "wiki": "Peach's Castle (Mario & Luigi: Partners in Time)",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC~~~~..",
                "~~~~~~C....============================..C~~~~..",
                "~~~~~~C....=..........................=..C~~~~..",
                "~~~~~~C....=....HH........HH..........=..C~~~~..",
                "~~~~~~C....=....##....@...##..........=..C~~~~..",
                "~~~~~~C....=..........................=..C~~~~..",
                "~~~~~~C....=....eeee........eeee....=..C~~~~....",
                "~~~~~~C....=..........................=..C~~~~..",
                "~~~~~~C....============================..C~~~~..",
                "~~~~~~CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC~~~~..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
            ],
            "start": (24, 6),
            "shard": None,
        },
        {
            "name": "Gritzy Desert",
            "wiki": "Gritzy Desert",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~..........................................",
                "~~~~~~....====....====....====....====....~~~~..",
                "~~~~~~....=..=....=..=....=..=....=..=....~~~~..",
                "~~~~~~....=..=....=..=....=..=....=..=....~~~~..",
                "~~~~~~....=..=....=.@=....=..=....=..=....~~~~..",
                "~~~~~~....====....====....====....====....~~~~..",
                "~~~~~~..........................................",
                "~~~~~~....eeee........eeee........eeee....~~~~..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (20, 5),
            "shard": None,
        },
    ],
    "PAST": [
        {
            "name": "Yoob's Belly",
            "wiki": "Yoob's Belly",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%..",
                "~~~~~~%%....========....%%%%%%%%....====%%~~~~..",
                "~~~~~~%%....=......=....%%%%%%%%....=..=%%~~~~..",
                "~~~~~~%%....=..**..=....%%%%%%%%....=..=%%~~~~..",
                "~~~~~~%%....=......=....%%%%%%%%....=.@=%%~~~~..",
                "~~~~~~%%....========....%%%%%%%%....====%%~~~~..",
                "~~~~~~%%....%%%%%%%%....%%%%%%%%....%%%%%%~~~~..",
                "~~~~~~%%....%%%%eeee%%%%%%%%%%%%eeee%%%%%%~~~~..",
                "~~~~~~%%....%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%~~~~..",
                "~~~~~~%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (12, 4),
            "shard": (10, 3),
        },
        {
            "name": "Yoshi's Island",
            "wiki": "Yoshi's Island (Mario & Luigi: Partners in Time)",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~....~~~~....~~~~....~~~~....~~~~....~~~~..",
                "~~~~~~....=..=....=..=....=..=....=..=....~~~~..",
                "~~~~~~....=..=....=..=....=..=....=..=....~~~~..",
                "~~~~~~....=..=....=.@=....=..=....=..=....~~~~..",
                "~~~~~~....====....====....====....====....~~~~..",
                "~~~~~~..........................................",
                "~~~~~~....^^^^....^^^^....^^^^....^^^^....~~~~..",
                "~~~~~~....^^eeee^^....^^^^....eeee^^^^....~~~~..",
                "~~~~~~....^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....~~",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (10, 4),
            "shard": None,
        },
        {
            "name": "Thwomp Volcano",
            "wiki": "Thwomp Volcano",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!..",
                "~~~~~~!!....====....!!!!....====....!!!!!!~~~~..",
                "~~~~~~!!....=..=....!!!!....=..=....!!!!!!~~~~..",
                "~~~~~~!!....=..=....!!!!....=..=....!!!!!!~~~~..",
                "~~~~~~!!....=..=....!!@!!!!!..=....!!!!!!!~~~~..",
                "~~~~~~!!....====....!!!!....====....!!!!!!~~~~..",
                "~~~~~~!!....!!!!eeee!!!!eeee!!!!eeee!!!!!!~~~~..",
                "~~~~~~!!....!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!~~~~..",
                "~~~~~~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (14, 4),
            "shard": None,
        },
        {
            "name": "Vim Factory",
            "wiki": "Vim Factory",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF..",
                "~~~~~~FF....========....FFFFFFFF....====FF~~~~..",
                "~~~~~~FF....=......=....FFFFFFFF....=..=FF~~~~..",
                "~~~~~~FF....=......=....FFFFFFFF....=..=FF~~~~..",
                "~~~~~~FF....=......=....FFFF@FFF....=..=FF~~~~..",
                "~~~~~~FF....========....FFFFFFFF....====FF~~~~..",
                "~~~~~~FF....FFFFFFFFeeeeFFFFFFFFeeeeFFFF~~~~~~..",
                "~~~~~~FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (12, 4),
            "shard": None,
        },
    ],
    "FUTURE": [
        {
            "name": "Shroob Castle",
            "wiki": "Shroob Castle",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF..",
                "~~~~~~FF....============================..FF~~..",
                "~~~~~~FF....=..........................=..FF~~..",
                "~~~~~~FF....=....**....................=..FF~~..",
                "~~~~~~FF....=..........@...............=..FF~~..",
                "~~~~~~FF....=....eeee........eeee......=..FF~~..",
                "~~~~~~FF....=..........................=..FF~~..",
                "~~~~~~FF....============================..FF~~..",
                "~~~~~~FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (24, 5),
            "shard": (10, 3),
        },
        {
            "name": "Shroob Mother Ship",
            "wiki": "Shroob Mother Ship",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF..",
                "~~~~~~FF====....====....====....====....====FF..",
                "~~~~~~FF=..=....=..=....=..=....=..=....=..=FF..",
                "~~~~~~FF=..=....=..=....=.@=....=..=....=..=FF..",
                "~~~~~~FF====....====....====....====....====FF..",
                "~~~~~~FF....................................FF..",
                "~~~~~~FF....eeee........eeee........eeee....FF..",
                "~~~~~~FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (22, 4),
            "shard": None,
        },
        {
            "name": "Toad Town (Future)",
            "wiki": "Toad Town (Mario & Luigi: Partners in Time)",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~....FFFFFFFFFFFFFFFFFFFFFFFFFFFF....~~~~..",
                "~~~~~~....FF....====....========....FF....~~~~..",
                "~~~~~~....FF....=..=....=......=....FF....~~~~..",
                "~~~~~~....FF....=..=....=.@....=....FF....~~~~..",
                "~~~~~~....FF....=..=....=......=....FF....~~~~..",
                "~~~~~~....FF....====....========....FF....~~~~..",
                "~~~~~~....FF....eeee........eeee....FF....~~~~..",
                "~~~~~~....FFFFFFFFFFFFFFFFFFFFFFFFFFFF....~~~~..",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=................=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (20, 4),
            "shard": None,
        },
        {
            "name": "Star Shrine",
            "wiki": "Star Shrine",
            "rows": [
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "~~~~~~....********....********....********....~~",
                "~~~~~~....*....*....*....*....*....*....*....~~..",
                "~~~~~~....*....*....*....@....*....*....*....~~",
                "~~~~~~....*....*....*....B....*....*....*....~~",
                "~~~~~~....********....********....********....~~",
                "~~~~~~..........................................",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~....=..=....eeee........=..=....~~~~~~~~..",
                "~~~~~~....====................====....~~~~~~~~..",
                "~~~~~~..........................................",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..",
            ],
            "start": (22, 3),
            "shard": None,
        },
    ],
}

_extend_pit_locations()

def _pad_map_rows(rows: list[str]) -> list[list[str]]:
    grid: list[list[str]] = []
    for row in rows:
        line = row.ljust(MAP_W)[:MAP_W]
        grid.append(list(line))
    while len(grid) < MAP_H:
        grid.append(list("." * MAP_W))
    return grid[:MAP_H]


# --- DS-style procedural assets (files=off) ---------------------------------
DS_OUTLINE = (20, 12, 28)
DS_SKIN = (255, 200, 160)
DS_SKIN_SH = (220, 160, 120)
DS_BLUE = (40, 80, 220)
DS_RED = (220, 40, 40)
DS_SHROOB = (180, 60, 200)
DS_SHROOB_EYE = (255, 80, 80)
DS_GOOMBA = (160, 90, 40)
DS_GOOMBA_DK = (110, 55, 25)
DS_KOOPA = (60, 180, 60)
DS_KOOPA_SH = (40, 130, 40)

# PiT enemy sprite keys → procedural DS pixels (files=off, no imports)
PIT_ENEMY_SPRITES = (
    "goomba", "para_goomba", "toad", "toad_brigade", "koopa", "piranha",
    "hammer_bro", "boomerang_bro", "boo", "thwomp", "yoob_grub", "elasto_piranha",
    "shroob", "shrooboid", "shroob_dr", "shroob_commander", "shroob_empress",
    "swiggler", "sunnycleft",
)

OW_SPRITE_POOL: dict[str, list[str]] = {
    "PAST": ["yoob_grub", "elasto_piranha", "goomba", "koopa", "piranha"],
    "PRESENT": ["goomba", "para_goomba", "toad_brigade", "hammer_bro", "koopa", "toad"],
    "FUTURE": ["shroob", "shrooboid", "shroob_dr", "boo", "thwomp"],
}

BOSS_SPRITE_KEY: dict[str, str] = {
    "Sunnycleft": "sunnycleft",
    "Swiggler": "swiggler",
    "Commander Shroob": "shroob_commander",
    "Elder Princess Shroob": "shroob_empress",
}


def _px_sprite(lines: tuple[str, ...], pal: dict[str, tuple[int, int, int]], scale: int = 2) -> pygame.Surface:
    h, w = len(lines), max(len(r) for r in lines)
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y, row in enumerate(lines):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            c = pal.get(ch)
            if c:
                pygame.draw.rect(surf, c, (x * scale, y * scale, scale, scale))
    return surf


def _px_tile(base: tuple[int, int, int], detail: tuple[str, ...], pal: dict[str, tuple[int, int, int]], size: int = 32) -> pygame.Surface:
    surf = pygame.Surface((size, size))
    surf.fill(base)
    step = size // 16
    for y, row in enumerate(detail):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            c = pal.get(ch)
            if c:
                pygame.draw.rect(surf, c, (x * step, y * step, step, step))
    return surf


class DSAssets:
    _singleton: "DSAssets | None" = None

    def __init__(self) -> None:
        self.water_frame = 0
        self._tile_cache: dict[tuple[str, str, int], pygame.Surface] = {}
        k = DS_OUTLINE
        self.pal_bro = {
            ".": (0, 0, 0, 0), "k": k, "g": AC_GREEN, "G": (0, 200, 90),
            "r": DS_RED, "w": WHITE, "b": (40, 40, 40), "s": DS_SKIN, "S": DS_SKIN_SH,
            "y": GOLD, "B": DS_BLUE, "h": (160, 90, 50),
        }
        self.pal_baby = {
            ".": (0, 0, 0, 0), "k": k, "p": GROK_PINK, "P": (255, 150, 210),
            "t": TOAD_RED, "T": (255, 120, 120), "w": WHITE, "b": (40, 40, 40),
            "s": DS_SKIN, "S": DS_SKIN_SH, "c": (255, 220, 180),
        }
        self.pal_enemy = {
            ".": (0, 0, 0, 0), "k": k, "u": DS_SHROOB, "U": (140, 40, 160),
            "e": DS_SHROOB_EYE, "g": (120, 180, 40), "G": (80, 140, 30),
            "o": DS_GOOMBA, "O": DS_GOOMBA_DK, "f": (200, 150, 90),
            "m": DS_RED, "M": (180, 30, 30), "y": (255, 220, 60),
            "t": TOAD_RED, "T": (255, 120, 120), "c": (255, 220, 180),
            "s": DS_SKIN, "S": DS_SKIN_SH, "w": WHITE, "b": (30, 30, 30),
            "p": (50, 160, 60), "P": DS_KOOPA, "K": DS_KOOPA_SH,
            "h": (120, 80, 50), "B": (200, 200, 220), "n": (80, 80, 120),
            "i": (255, 180, 60), "a": (100, 200, 255),
        }
        self.enemy_sprites: dict[str, pygame.Surface] = {}
        self.pal_item = {
            ".": (0, 0, 0, 0), "k": k, "r": DS_RED, "w": WHITE,
            "g": (40, 200, 60), "G": (20, 140, 40), "y": GOLD, "b": DS_BLUE,
        }
        self._build_sprites()
        self._build_tiles()

    @classmethod
    def get(cls) -> "DSAssets":
        if cls._singleton is None:
            cls._singleton = DSAssets()
        return cls._singleton

    def _build_sprites(self) -> None:
        ac_lines = (
            "......kkkk......",
            ".....kGGGGk.....",
            "....kGGGGGGk....",
            "...kGGrrGGGk...",
            "...kGwwbbGGk...",
            "...kGwwbbGGk...",
            "...kGGGGGGGk...",
            "....kGGyyGGk....",
            ".....kGGGGk.....",
            "......kkkk......",
            "....kGGGGGGk....",
            "...kGGGGGGGGk...",
            "...kGGGGGGGGk...",
            "...khhGGGGhhk...",
            "...khhGGGGhhk...",
            "....kkkkkkkk....",
        )
        self.sprite_ac = _px_sprite(ac_lines, self.pal_bro, 2)

        grok_lines = (
            "....kkkkkk....",
            "...kPPPPPPk...",
            "...kPwwbbPpk..",
            "...kPwwbbPpk..",
            "...kPPPPPPPk..",
            "....kPPPPPk...",
            ".....kkkkk....",
            "...kPPPPPPPk..",
            "..kPPPPPPPPk..",
            "..kPPPPPPPPk..",
            "...kPPkkPPk...",
            "....kk..kk....",
        )
        self.sprite_grok = _px_sprite(grok_lines, self.pal_baby, 2)

        toad_lines = (
            "....kkkkkk....",
            "...kTTTTTTk...",
            "...kTwwbbTk...",
            "...kTwwbbTk...",
            "...kTTTTTTk...",
            "....kcccck....",
            "...kTTTTTTk...",
            "..kTTTTTTTTk..",
            "..kTTkkkkTTk..",
            "...kk....kk...",
        )
        self.sprite_toad = _px_sprite(toad_lines, self.pal_baby, 2)

        cat_lines = (
            "......kkkk......",
            ".....kGGGGk.....",
            "....kGGGGGGk....",
            "...kGGwwbbGGk...",
            "...kGGwwbbGGk...",
            "...kGGGGGGGGk...",
            "....kGGkkGGk....",
            "...kGGGGGGGGk...",
            "..kGGGGGGGGGGk..",
            "..kGGGGGGGGGGk..",
            "...kGG....GGk...",
            "...kGG....GGk...",
            "....kk....kk....",
        )
        self.sprite_cat = _px_sprite(cat_lines, self.pal_bro, 2)

        pe = self.pal_enemy
        defs: dict[str, tuple[tuple[str, ...], int]] = {
            "goomba": (
                ("....kkkk....", "..kooooook..", ".kowwbboook.", ".kooooooook.", "..kooooook..",
                 "...kkkkkk...", ".kfffffffk.", "kfffffffffk", ".kkk...kkk."), 3),
            "para_goomba": (
                ("..kwwwwk..", ".kwwyywwk.", "..kwwwwk..", "...kkkk...", "..koooook..",
                 ".kowwbboook.", ".kooooooook.", "..kooooook..", "...kkkkkk..", ".kfffffffk.",
                 "kfffffffffk", ".kkk...kkk."), 3),
            "toad": (
                ("....kkkkkk....", "...kTTTTTTk...", "...kTwwbbTk...", "...kTTTTTTk...",
                 "....kcccck....", "...kcccccck...", "..kcccccccck..", "..kcckkkkcck..",
                 "...kk....kk..."), 3),
            "toad_brigade": (
                ("....kkkkkk....", "...kMMMMMMk...", "...kMwwbbMk...", "...kMMMMMMk...",
                 "....kssssk....", "...kssssssk...", "..kssssssssk..", "..ksskkkkssk..",
                 "...kk....kk...", "..khhhhhk..", ".khhhhhhhhk."), 3),
            "koopa": (
                ("....kkkk....", "..kPPPPPPk..", ".kPwwbbPPk..", ".kPPPPPPPk..", "..kPPPPPk...",
                 "...kssssk...", "..kssssssk..", ".kssssssssk.", ".ksskkkkssk.", "..kk....kk.."), 3),
            "piranha": (
                ("....kkkk....", "...kggggk...", "..kggwwggk..", ".kggggggggk.", ".kggggggggk.",
                 "..kggggggk..", "...kggggk...", "..kgg..ggk..", "..kgg..ggk.."), 3),
            "hammer_bro": (
                ("...kkkkkk...", "..kmmmmmk..", ".kmmwwmmmk.", ".kmmmmmmmk.", "..kmmmmmk..",
                 "...kssssk...", "..kssssssk..", ".kssssssssk.", "..khhhhhk..", ".khhhhhhhhk.",
                 "...khhhk..."), 3),
            "boomerang_bro": (
                ("...kkkkkk...", "..kmmmmmk..", ".kmmwwmmmk.", ".kmmmmmmmk.", "..kmmmmmk..",
                 "...kssssk...", "..kiiiiik..", ".kiiiaaiik.", "..kiiiiik..", "...khhhk..."), 3),
            "boo": (
                ("....kkkkkk....", "...kBBBBBBk...", "..kBwwbbBBk..", ".kBBBBBBBBBk.", ".kBBBBBBBBBk.",
                 "..kBBBBBBBk..", "...kBnBnBk...", "...kBBBBBk...", "..kkk..kkk.."), 3),
            "thwomp": (
                ("..kkkkkkkk..", ".knnnnnnnnk.", ".knnwwbbnnk.", ".knnnnnnnnk.", ".knnnnnnnnk.",
                 ".knnnnnnnnk.", "..knnnnnnk..", "...knnnnk..."), 3),
            "yoob_grub": (
                ("...kkkk...", "..kooook..", ".kooGGook.", ".kooGGook.", ".kooooook.", "..kooook..",
                 "...kkkk...", "..kooook..", "..kooook.."), 3),
            "elasto_piranha": (
                ("..kggggk..", ".kggwwggk.", ".kggggggk.", ".kggggggk.", "..kggggk..",
                 "...kgggk...", "..kggggk..", ".kggggggk.", ".kggggggk.", "..kggggk.."), 3),
            "shroob": (
                ("...kkkkkk...", "..kUUUUUUk..", ".kUUeeUUUUk.", ".kUUeeUUUUk.", ".kUUUUUUUUk.",
                 "..kUUyyUUk..", "...kUUUUk...", "..kUUkkUUk..", ".kUU....UUk.", "..kk....kk.."), 3),
            "shrooboid": (
                ("....kkkkkk....", "...kUUUUUUk...", "..kUUeeUUk..", ".kUUeeeeUUk.", ".kUUUUUUUUk.",
                 "..kUUyyUUk..", "...kUUUUk...", "..kUUkkUUk..", ".kUU....UUk.", "..kk....kk.."), 3),
            "shroob_dr": (
                ("...kkkkkk...", "..kUUUUUUk..", ".kUUeeUUk..", ".kUUwwbbUUk.", ".kUUUUUUk..",
                 "..kwwwwk..", ".kwwiiwwk.", "..kwwwwk..", "..kUUUUk..", ".kUUkkUUk.", "..kk..kk.."), 3),
            "shroob_commander": (
                ("....kkkkkkkk....", "...kUUUUUUUUk...", "..kUUeeUUUUk..", ".kUUeeeeUUUUk.",
                 ".kUUUUUUUUUUk.", "..kUUyyUUyyk..", "...kUUUUUUk...", "..kUUkkkkUUk..",
                 ".kUU....UUk.", ".kUU....UUk.", "..kk....kk.."), 4),
            "shroob_empress": (
                ("......kkkkkk......", "....kUUUUUUk....", "...kUUeeUUUUk...", "..kUUeeeeUUUUk..",
                 "..kUUUUUUUUUUk..", "...kUUyyUUyyk...", "....kUUUUUUk....", "...kUUkkkkUUk...",
                 "..kUU....UUk..", "..kUU....UUk..", "...kk....kk...", ".kii....iik."), 4),
            "swiggler": (
                ("..kooooo..", ".kowwwoo.", ".kooooo.", "..kooooo..", ".kowwwoo.", ".kooooo.",
                 "..kooooo..", ".kowwwoo.", ".kooooo.", "..kooooo..", ".kowwwoo.", ".kooooo."), 3),
            "sunnycleft": (
                ("....kkkk....", "..kyyyyyyk..", ".kyywwyyyk.", ".kyyyyyyyyk.", "..kyyyyyyk..",
                 "...kooook...", "..kooGGook..", ".kooooooook.", "..kooook..", "...kkkk..."), 3),
        }
        for key, (lines, scale) in defs.items():
            self.enemy_sprites[key] = _px_sprite(lines, pe, scale)
        self.sprite_shroob = self.enemy_sprites["shroob"]
        self.sprite_grub = self.enemy_sprites["yoob_grub"]
        self.sprite_hammer = self.enemy_sprites["hammer_bro"]

        star_lines = (
            "....y....",
            "...yky...",
            "..ykkky..",
            ".ykkbky.",
            "ykkbbkky",
            ".ykkbky.",
            "..ykkky..",
            "...yky...",
            "....y....",
        )
        self.sprite_star = _px_sprite(star_lines, self.pal_item, 3)

        shroom_lines = (
            "...kkk...",
            "..krrrk..",
            ".krrrrrk.",
            ".krrrrrk.",
            "..kwwwk..",
            "...www...",
            "...www...",
        )
        self.sprite_shroom = _px_sprite(shroom_lines, self.pal_item, 3)

        shell_lines = (
            "...kkk...",
            "..kgggk..",
            ".kggGGgk.",
            ".kggGGgk.",
            "..kgggk..",
            "...kkk...",
        )
        self.sprite_shell = _px_sprite(shell_lines, self.pal_item, 3)

        hole_lines = (
            "...kkkk...",
            "..kBBBBk..",
            ".kBwwwwBk.",
            ".kBwyywBk.",
            ".kBwwwwBk.",
            "..kBBBBk..",
            "...kkkk...",
        )
        self.sprite_hole = _px_sprite(hole_lines, self.pal_item, 3)

        self.sprite_shadow = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.sprite_shadow, (0, 0, 0, 70), (0, 0, 28, 10))

    def _build_tiles(self) -> None:
        self._tile_detail = {
            ".": (
                "................",
                "..g.......g.....",
                "................",
                ".....g..........",
                "................",
                "..g.......g.....",
                "................",
                ".....g..........",
                "................",
                "..g.......g.....",
                "................",
                ".....g..........",
                "................",
                "..g.......g.....",
                "................",
                ".....g..........",
            ),
            "=": (
                "kkkkkkkkkkkkkkkk",
                "hhhhhhhhhhhhhhhh",
                "hhhhhhhhhhhhhhhh",
                "kkkkkkkkkkkkkkkk",
                "................",
                "................",
                "kkkkkkkkkkkkkkkk",
                "hhhhhhhhhhhhhhhh",
                "hhhhhhhhhhhhhhhh",
                "kkkkkkkkkkkkkkkk",
                "................",
                "................",
                "kkkkkkkkkkkkkkkk",
                "hhhhhhhhhhhhhhhh",
                "hhhhhhhhhhhhhhhh",
                "kkkkkkkkkkkkkkkk",
            ),
            "^": (
                ".......k........",
                "......kgk.......",
                ".....kgggk......",
                "....kgggggk.....",
                "...kgggggggk....",
                "..kgggggggggk...",
                ".kgggggggggggk..",
                "kgggggggggggggk.",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
            ),
            "~": (
                "....b.......b...",
                "................",
                ".......b........",
                "................",
                "....b.......b...",
                "................",
                ".......b........",
                "................",
                "....b.......b...",
                "................",
                ".......b........",
                "................",
                "....b.......b...",
                "................",
                ".......b........",
                "................",
            ),
            "H": (
                "....kkkk........",
                "...krrrrk.......",
                "..krrrrrrk......",
                "..kwwwwwwk......",
                "..kwwwwwwk......",
                "..krrrrrrk......",
                "...krrrrk.......",
                "....kkkk........",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
            ),
            "C": (
                "....kkkkkkkk....",
                "...kCCCCCCCCk...",
                "..kCCCCCCCCCCk..",
                "..kCC....CCk....",
                "..kCC....CCk....",
                "..kCCCCCCCCCCk..",
                "...kCCCCCCCCk...",
                "....kkkkkkkk....",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
            ),
            "S": (
                "....kkkk........",
                "...krrrrk.......",
                "..krrwwrrk......",
                "..krw..wrk......",
                "..krrwwrrk......",
                "...krrrrk.......",
                "....kkkk........",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
            ),
        }
        self._tile_pal = {
            "g": (50, 160, 50), "k": DS_OUTLINE, "h": (120, 75, 35),
            "b": (80, 180, 255), "r": DS_RED, "w": WHITE, "C": (200, 180, 150),
        }

    def tile(self, ch: str, era: str, frame: int = 0) -> pygame.Surface:
        key = (ch, era, frame % 2)
        if key in self._tile_cache:
            return self._tile_cache[key]
        colors = _tile_colors(era)
        base = colors.get(ch, colors["."])
        pal = dict(self._tile_pal)
        if era == "PAST":
            pal["g"] = (90, 100, 45)
            pal["h"] = (100, 65, 30)
            pal["b"] = (255, 140, 60)
        elif era == "FUTURE":
            pal["g"] = (35, 30, 70)
            pal["h"] = (0, 180, 200)
            pal["b"] = (160, 80, 255)
        if ch == "~" and frame % 2:
            pal["b"] = tuple(min(255, c + 35) for c in pal["b"])
        detail = self._tile_detail.get(ch, ("." * 16,) * 16)
        surf = _px_tile(base, detail, pal, 32)
        self._tile_cache[key] = surf
        return surf

    def tick(self) -> None:
        self.water_frame += 1

    def blit_sprite(
        self,
        surface: pygame.Surface,
        sprite: pygame.Surface,
        x: int,
        y: int,
        *,
        flip: bool = False,
        shadow: bool = True,
    ) -> None:
        img = pygame.transform.flip(sprite, flip, False) if flip else sprite
        if shadow:
            surface.blit(self.sprite_shadow, (x + img.get_width() // 2 - 14, y + img.get_height() - 6))
        surface.blit(img, (x, y))

    def sprite_for_key(self, key: str) -> pygame.Surface:
        return self.enemy_sprites.get(key, self.enemy_sprites["goomba"])

    def enemy_sprite(self, name: str, era: str, *, sprite_key: str | None = None) -> pygame.Surface:
        if sprite_key:
            return self.sprite_for_key(sprite_key)
        if key := BOSS_SPRITE_KEY.get(name):
            return self.sprite_for_key(key)
        n = name.lower()
        if "empress" in n or "elder" in n:
            return self.sprite_for_key("shroob_empress")
        if "commander" in n:
            return self.sprite_for_key("shroob_commander")
        if "swiggler" in n:
            return self.sprite_for_key("swiggler")
        if "sunnyc" in n:
            return self.sprite_for_key("sunnycleft")
        if "shroob" in n and "dr" in n:
            return self.sprite_for_key("shroob_dr")
        if "shrooboid" in n or "shroob" in n:
            return self.sprite_for_key("shroob")
        if "yoob" in n or "grub" in n:
            return self.sprite_for_key("yoob_grub")
        if "elasto" in n or "piranha" in n:
            return self.sprite_for_key("elasto_piranha" if "elasto" in n else "piranha")
        if "hammer" in n:
            return self.sprite_for_key("hammer_bro")
        if "boomerang" in n:
            return self.sprite_for_key("boomerang_bro")
        if "brigade" in n or "toad" in n:
            return self.sprite_for_key("toad_brigade" if "brigade" in n else "toad")
        if "koopa" in n:
            return self.sprite_for_key("koopa")
        if "para" in n and "goom" in n:
            return self.sprite_for_key("para_goomba")
        if "goom" in n:
            return self.sprite_for_key("goomba")
        if "boo" in n:
            return self.sprite_for_key("boo")
        if "thwomp" in n:
            return self.sprite_for_key("thwomp")
        pool = OW_SPRITE_POOL.get(era, ["goomba"])
        return self.sprite_for_key(pool[0])

    def partner_sprite(self, name: str) -> pygame.Surface:
        if name == "Grok":
            return self.sprite_grok
        if name == "Toad":
            return self.sprite_toad
        if name == "AC Cat":
            return self.sprite_cat
        return self.sprite_ac

    def draw_ds_panel(self, surface: pygame.Surface, rect: tuple[int, int, int, int], accent: tuple[int, int, int] = AC_GREEN) -> None:
        x, y, w, h = rect
        pygame.draw.rect(surface, (12, 18, 42), (x, y, w, h), border_radius=6)
        pygame.draw.rect(surface, (30, 45, 90), (x + 3, y + 3, w - 6, h - 6), border_radius=4)
        pygame.draw.rect(surface, accent, (x, y, w, h), 3, border_radius=6)
        for cx in range(x + 8, x + w - 8, 14):
            pygame.draw.rect(surface, (50, 70, 120), (cx, y + 5, 6, 3))
            pygame.draw.rect(surface, (50, 70, 120), (cx, y + h - 8, 6, 3))


def _tile_colors(era: str) -> dict[str, tuple[int, int, int]]:
    if era == "PAST":
        base = GRASS_PAST
        return {
            ".": base, "=": PATH_PAST, "~": WATER_PAST, "!": (220, 80, 20),
            "%": (180, 100, 60), "^": (60, 100, 40), "H": (130, 90, 60),
            "C": (140, 110, 90), "F": (90, 70, 50), "*": GOLD, "@": (255, 180, 60),
            "S": (180, 100, 80), "?": (255, 240, 150), ":": (100, 70, 50), "B": (140, 50, 30),
        }
    if era == "PRESENT":
        return {
            ".": GRASS_PRESENT, "=": PATH_PRESENT, "~": WATER_PRESENT,
            "!": (200, 100, 40), "%": (150, 130, 80), "^": (20, 100, 30),
            "H": HOUSE, "C": (200, 180, 160), "F": (120, 120, 130),
            "*": GOLD, "@": (255, 200, 80), "S": (200, 80, 120), "?": (255, 255, 100),
            ":": (80, 60, 40), "B": (160, 40, 40),
        }
    return {
        ".": GRASS_FUTURE, "=": PATH_FUTURE, "~": WATER_FUTURE,
        "!": (180, 40, 180), "%": (100, 50, 120), "^": (40, 30, 80),
        "H": (50, 60, 100), "C": (60, 40, 100), "F": (50, 50, 90),
        "*": GOLD, "@": (0, 255, 200), "S": (180, 60, 200), "?": (200, 200, 255),
        ":": (60, 40, 80), "B": (200, 50, 80),
    }


class Partner:
    def __init__(self, name: str, color: tuple[int, int, int], hp: int, atk: int, spd: int, role: str) -> None:
        self.name = name
        self.color = color
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.spd = spd
        self.role = role
        self.max_bp = 8
        self.bp = 4

    def alive(self) -> bool:
        return self.hp > 0

    def heal(self, amt: int) -> None:
        self.hp = min(self.max_hp, self.hp + amt)

    def restore_bp(self, amt: int) -> None:
        self.bp = min(self.max_bp, self.bp + amt)


class Enemy:
    def __init__(
        self,
        name: str,
        hp: int,
        atk: int,
        color: tuple[int, int, int],
        era: str,
        *,
        sprite_key: str = "goomba",
    ) -> None:
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.color = color
        self.era = era
        self.sprite_key = sprite_key

    def alive(self) -> bool:
        return self.hp > 0


def _enemy_table() -> dict[str, list[Enemy]]:
    return {
        "PAST": [
            Enemy("Yoob Grub", 28, 6, (160, 120, 40), "PAST", sprite_key="yoob_grub"),
            Enemy("Elasto-Piranha", 34, 8, (40, 180, 60), "PAST", sprite_key="elasto_piranha"),
            Enemy("Goomba", 26, 5, DS_GOOMBA, "PAST", sprite_key="goomba"),
            Enemy("Koopa", 32, 7, DS_KOOPA, "PAST", sprite_key="koopa"),
        ],
        "PRESENT": [
            Enemy("Goomba", 24, 5, DS_GOOMBA, "PRESENT", sprite_key="goomba"),
            Enemy("Para-Goomba", 28, 6, DS_GOOMBA_DK, "PRESENT", sprite_key="para_goomba"),
            Enemy("Toad Brigade", 30, 7, TOAD_RED, "PRESENT", sprite_key="toad_brigade"),
            Enemy("Hammer Bro", 40, 10, (180, 60, 30), "PRESENT", sprite_key="hammer_bro"),
            Enemy("Boomerang Bro", 36, 9, (200, 80, 40), "PRESENT", sprite_key="boomerang_bro"),
            Enemy("Koopa", 30, 7, DS_KOOPA, "PRESENT", sprite_key="koopa"),
        ],
        "FUTURE": [
            Enemy("Shrooboid", 36, 9, (180, 40, 200), "FUTURE", sprite_key="shrooboid"),
            Enemy("Dr. Shroob", 55, 12, (120, 0, 160), "FUTURE", sprite_key="shroob_dr"),
            Enemy("Shroob", 34, 8, DS_SHROOB, "FUTURE", sprite_key="shroob"),
            Enemy("Boo", 30, 7, (200, 200, 230), "FUTURE", sprite_key="boo"),
            Enemy("Thwomp", 45, 11, (90, 90, 120), "FUTURE", sprite_key="thwomp"),
        ],
    }


class GrokKitten:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, flip: bool = False) -> None:
        spr = DSAssets.get().sprite_grok
        gx = int(self.x - cam_x) - spr.get_width() // 2
        gy = int(self.y - cam_y) - spr.get_height() + 8
        DSAssets.get().blit_sprite(surface, spr, gx, gy, flip=flip)


class GrokToad:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, flip: bool = False) -> None:
        spr = DSAssets.get().sprite_toad
        tx = int(self.x - cam_x) - spr.get_width() // 2
        ty = int(self.y - cam_y) - spr.get_height() + 8
        DSAssets.get().blit_sprite(surface, spr, tx, ty, flip=flip)


class ACCat:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, flip: bool = False) -> None:
        spr = DSAssets.get().sprite_cat
        cx = int(self.x - cam_x) - spr.get_width() // 2
        cy = int(self.y - cam_y) - spr.get_height() + 8
        DSAssets.get().blit_sprite(surface, spr, cx, cy, flip=flip)


class OverworldEnemy:
    def __init__(self, x: int, y: int, era: str, loc_idx: int, sprite_key: str) -> None:
        self.x = x
        self.y = y
        self.era = era
        self.loc_idx = loc_idx
        self.sprite_key = sprite_key
        self.alive = True
        self.wobble = random.random() * 6.28

    def rect(self, tile: int) -> pygame.Rect:
        return pygame.Rect(self.x * tile + 4, self.y * tile + 4, tile - 8, tile - 8)


class ACOverworld:
    BLOCKED = "~"

    def __init__(self, party: list[Partner], coins: int, shards: set[str]) -> None:
        self.tile_size = 32
        self.map_width = MAP_W
        self.map_height = MAP_H
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.speed = 5
        self.party = party
        self.coins = coins
        self.shards = set(shards)
        self.current_era_index = 1
        self.time_phase = ERAS[self.current_era_index]
        self.location_index = 0
        self.grid = self._load_location_grid()
        self.ac_x = 0.0
        self.ac_y = 0.0
        self._place_at_start()
        self.grok = GrokKitten(self.ac_x - 55, self.ac_y + 5)
        self.toad = GrokToad(self.ac_x - 95, self.ac_y + 25)
        self.ac_cat = ACCat(self.ac_x + 70, self.ac_y - 15)
        self.enemies = self._spawn_enemies_all()
        self.message = ""
        self.message_timer = 0
        self.facing_left = False
        self.pending_battle_sprite: str | None = None

    def _locations(self) -> list[dict]:
        return PIT_LOCATIONS[self.time_phase]

    def _location(self) -> dict:
        return self._locations()[self.location_index]

    def _load_location_grid(self) -> list[list[str]]:
        return _pad_map_rows(self._location()["rows"])

    def _place_at_start(self) -> None:
        sx, sy = self._location()["start"]
        self.ac_x = sx * self.tile_size + self.tile_size // 2
        self.ac_y = sy * self.tile_size + self.tile_size // 2

    def _spawn_enemies_all(self) -> list[OverworldEnemy]:
        foes: list[OverworldEnemy] = []
        for era in ERAS:
            pool = OW_SPRITE_POOL[era]
            for idx, loc in enumerate(PIT_LOCATIONS[era]):
                grid = _pad_map_rows(loc["rows"])
                n = 0
                for y, row in enumerate(grid):
                    for x, ch in enumerate(row):
                        if ch == "e":
                            key = pool[(x + y + idx + n) % len(pool)]
                            foes.append(OverworldEnemy(x, y, era, idx, key))
                            n += 1
        return foes

    def travel_time(self) -> None:
        self.current_era_index = (self.current_era_index + 1) % len(ERAS)
        self.time_phase = ERAS[self.current_era_index]
        self.location_index = min(self.location_index, len(self._locations()) - 1)
        self.grid = self._load_location_grid()
        self._place_at_start()
        self.message = f"Time Hole → {self.time_phase}: {self._location()['name']}"
        self.message_timer = 150

    def next_location(self) -> None:
        self.location_index = (self.location_index + 1) % len(self._locations())
        self.grid = self._load_location_grid()
        self._place_at_start()
        self.message = f"→ {self._location()['name']}"
        self.message_timer = 120

    def area_name(self) -> str:
        return self._location()["name"]

    def _tile_at(self, tx: int, ty: int) -> str:
        if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
            return self.grid[ty][tx]
        return "~"

    def _walkable(self, ch: str) -> bool:
        return ch not in self.BLOCKED

    def _near_tile(self, tx: int, ty: int, want: str, radius: int = 1) -> bool:
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if self._tile_at(tx + dx, ty + dy) == want:
                    return True
        return False

    def update(self) -> str | None:
        keys = pygame.key.get_pressed()
        nx, ny = self.ac_x, self.ac_y
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            nx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            nx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ny -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ny += self.speed
        tx, ty = int(nx // self.tile_size), int(ny // self.tile_size)
        if self._walkable(self._tile_at(tx, ty)):
            if nx < self.ac_x:
                self.facing_left = True
            elif nx > self.ac_x:
                self.facing_left = False
            self.ac_x, self.ac_y = nx, ny

        tile = self._tile_at(int(self.ac_x // self.tile_size), int(self.ac_y // self.tile_size))
        if tile == "@":
            self.next_location()

        self.camera_x = self.ac_x - WIDTH // 2
        self.camera_y = self.ac_y - HEIGHT // 2
        self.grok.x += (self.ac_x - 55 - self.grok.x) * 0.18
        self.grok.y += (self.ac_y + 5 - self.grok.y) * 0.18
        self.toad.x += (self.ac_x - 95 - self.toad.x) * 0.12
        self.toad.y += (self.ac_y + 25 - self.toad.y) * 0.12
        self.ac_cat.x += (self.ac_x + 70 - self.ac_cat.x) * 0.15
        self.ac_cat.y += (self.ac_y - 15 - self.ac_cat.y) * 0.15

        if self.message_timer > 0:
            self.message_timer -= 1

        player_rect = pygame.Rect(int(self.ac_x) - 12, int(self.ac_y) - 12, 24, 24)
        for foe in self.enemies:
            if not foe.alive or foe.era != self.time_phase or foe.loc_idx != self.location_index:
                continue
            if player_rect.colliderect(foe.rect(self.tile_size)):
                foe.alive = False
                self.pending_battle_sprite = foe.sprite_key
                return "battle"

        return None

    def interact(self) -> str | None:
        ptx, pty = int(self.ac_x // self.tile_size), int(self.ac_y // self.tile_size)
        tile = self._tile_at(ptx, pty)
        loc = self._location()

        if tile == "S" or self._near_tile(ptx, pty, "S") or (loc.get("shop") and self._near_tile(ptx, pty, "S")):
            return "shop"

        if tile == "?" or self._near_tile(ptx, pty, "?"):
            return "dialogue"

        if tile == ":":
            self.coins += 5
            for p in self.party:
                if p.role == "baby":
                    p.atk += 1
            self.message = "Baby pipe! Bean power +1 ATK for babies."
            self.message_timer = 120
            return None

        if tile == "B" and loc["name"] == "Star Shrine" and len(self.shards) >= 3:
            return "final_boss"

        if self.time_phase not in self.shards:
            on_star = tile == "*"
            shard = loc.get("shard")
            on_shard = shard and abs(ptx - shard[0]) <= 1 and abs(pty - shard[1]) <= 1
            if on_star or on_shard:
                return f"boss:{self.time_phase}"

        return None

    def grant_shard(self, era: str) -> None:
        self.shards.add(era)
        self.coins += 25
        self.message = f"Cobalt Star shard ({era}) secured!"
        self.message_timer = 150

    def draw(self, surface: pygame.Surface) -> None:
        assets = DSAssets.get()
        assets.tick()
        ts = self.tile_size
        era = self.time_phase
        for y in range(MAP_H):
            for x in range(MAP_W):
                sx = x * ts - int(self.camera_x)
                sy = y * ts - int(self.camera_y)
                if not (-ts <= sx <= WIDTH and -ts <= sy <= HEIGHT):
                    continue
                ch = self.grid[y][x]
                draw_ch = "." if ch == "e" else ch
                if draw_ch in (".", "=", "^", "~", "H", "C", "S"):
                    surface.blit(assets.tile(draw_ch, era, assets.water_frame), (sx, sy))
                elif draw_ch in ("%", "!", "F"):
                    surface.blit(assets.tile(".", era), (sx, sy))
                    tint = _tile_colors(era).get(draw_ch, (100, 100, 100))
                    overlay = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    overlay.fill((*tint, 170))
                    surface.blit(overlay, (sx, sy))
                    pygame.draw.rect(surface, DS_OUTLINE, (sx + 4, sy + 4, ts - 8, ts - 8), 1)
                else:
                    surface.blit(assets.tile(".", era), (sx, sy))
                if ch == "*":
                    surface.blit(assets.sprite_star, (sx + 4, sy + 4))
                elif ch == "@":
                    surface.blit(assets.sprite_hole, (sx + 2, sy + 2))
                elif ch == "?":
                    pygame.draw.circle(surface, (255, 255, 100), (sx + 16, sy + 10), 9)
                    pygame.draw.circle(surface, DS_OUTLINE, (sx + 16, sy + 10), 9, 2)
                    surface.blit(tiny_font.render("?", True, DS_OUTLINE), (sx + 12, sy + 2))
                elif ch == "B":
                    pygame.draw.rect(surface, (200, 40, 40), (sx + 6, sy + 6, ts - 12, ts - 12), 3, border_radius=4)
                    surface.blit(tiny_font.render("B", True, WHITE), (sx + 12, sy + 8))
                elif ch == ":":
                    pygame.draw.rect(surface, (60, 40, 30), (sx + 12, sy + 4, 8, ts - 8))
                    pygame.draw.rect(surface, DS_OUTLINE, (sx + 10, sy + 2, 12, ts - 4), 2)

        for foe in self.enemies:
            if not foe.alive or foe.era != self.time_phase or foe.loc_idx != self.location_index:
                continue
            foe.wobble += 0.08
            r = foe.rect(ts)
            sx = r.x - int(self.camera_x)
            sy = r.y - int(self.camera_y) + int(4 * pygame.math.Vector2(1, 0).rotate(foe.wobble * 20).y)
            spr = assets.sprite_for_key(foe.sprite_key)
            assets.blit_sprite(surface, spr, sx - 4, sy - 18)

        flip = self.facing_left
        acx = int(self.ac_x - self.camera_x)
        acy = int(self.ac_y - self.camera_y)
        spr_ac = assets.sprite_ac
        assets.blit_sprite(surface, spr_ac, acx - spr_ac.get_width() // 2, acy - spr_ac.get_height() + 8, flip=flip)
        self.grok.draw(surface, self.camera_x, self.camera_y, flip=flip)
        self.toad.draw(surface, self.camera_x, self.camera_y, flip=flip)
        self.ac_cat.draw(surface, self.camera_x, self.camera_y, flip=flip)


class Battle:
    def __init__(
        self,
        party: list[Partner],
        era: str,
        coins: int,
        *,
        boss: tuple[str, int, int] | None = None,
        inventory: dict[str, int] | None = None,
        wild_sprite_key: str | None = None,
    ) -> None:
        self.party = party
        self.era = era
        self.inventory = inventory or {"shroom": 2, "max": 0, "1up": 0}
        if boss:
            name, hp, atk = boss
            bkey = BOSS_SPRITE_KEY.get(name, "shroob")
            self.enemies = [Enemy(name, hp, atk, (200, 50, 80), era, sprite_key=bkey)]
            self.is_boss = True
            self.log = [f"BOSS: {name}!"]
        else:
            pool = _enemy_table()[era]
            if wild_sprite_key:
                matches = [e for e in pool if e.sprite_key == wild_sprite_key]
                lead = matches[0] if matches else random.choice(pool)
            else:
                lead = random.choice(pool)
            self.enemies = [Enemy(lead.name, lead.max_hp, lead.atk, lead.color, era, sprite_key=lead.sprite_key)]
            if random.random() < 0.45:
                e2 = random.choice(pool)
                if e2.sprite_key != lead.sprite_key:
                    self.enemies.append(Enemy(e2.name, e2.max_hp, e2.atk, e2.color, era, sprite_key=e2.sprite_key))
            self.is_boss = False
            self.log = [f"Wild {self.enemies[0].name} appeared!"]
        self.coins = coins
        self.turn = "menu"
        self.menu_sel = 0
        self.menu_opts = ["Attack", "Bros Move", "Items", "Flee"]
        self.sub_sel = 0
        self.bros_pick: tuple[str, int, int] | None = None
        self.bros_timer = 0
        self.bros_window = 0
        self.pending_bros_dmg = 0
        self.flash = 0
        self.done = False
        self.won = False
        self.fled = False
        self.shard_reward: str | None = None

    def _alive_party(self) -> list[Partner]:
        return [p for p in self.party if p.alive()]

    def _alive_foes(self) -> list[Enemy]:
        return [e for e in self.enemies if e.alive()]

    def update_key(self, key: int) -> None:
        if self.done:
            return
        if self.turn == "bros":
            if key == pygame.K_SPACE and self.bros_window > 0:
                bonus = self.bros_pick[1] if self.bros_pick else 18
                self.pending_bros_dmg = bonus + 8
                self.log.append("Bros timing PERFECT! +damage")
            elif key == pygame.K_SPACE:
                self.pending_bros_dmg = (self.bros_pick[1] if self.bros_pick else 18) - 4
                self.log.append("Bros attack landed.")
            self._resolve_bros()
            return
        if self.turn == "bros_pick":
            if key == pygame.K_UP:
                self.sub_sel = (self.sub_sel - 1) % len(BROS_MOVES)
            elif key == pygame.K_DOWN:
                self.sub_sel = (self.sub_sel + 1) % len(BROS_MOVES)
            elif key == pygame.K_RETURN:
                move = BROS_MOVES[self.sub_sel]
                alive = self._alive_party()
                if not alive:
                    self.turn = "menu"
                    return
                lead = alive[0]
                if lead.bp < move[2]:
                    self.log.append("Not enough BP!")
                    self.turn = "menu"
                else:
                    lead.bp -= move[2]
                    self.bros_pick = move
                    self.turn = "bros"
                    self.bros_timer = 45
                    self.bros_window = 0
                    self.pending_bros_dmg = 0
                    self.log.append(f"{move[0]}! Press SPACE on the flash!")
            elif key == pygame.K_ESCAPE:
                self.turn = "menu"
            return
        if self.turn == "items":
            opts = self._item_opts()
            if key == pygame.K_UP:
                self.sub_sel = (self.sub_sel - 1) % max(1, len(opts))
            elif key == pygame.K_DOWN:
                self.sub_sel = (self.sub_sel + 1) % max(1, len(opts))
            elif key == pygame.K_RETURN and opts:
                self._use_item(opts[self.sub_sel])
            elif key == pygame.K_ESCAPE:
                self.turn = "menu"
            return
        if self.turn != "menu":
            return
        if key == pygame.K_UP:
            self.menu_sel = (self.menu_sel - 1) % len(self.menu_opts)
        elif key == pygame.K_DOWN:
            self.menu_sel = (self.menu_sel + 1) % len(self.menu_opts)
        elif key == pygame.K_RETURN:
            self._pick_action(self.menu_opts[self.menu_sel])

    def _item_opts(self) -> list[str]:
        opts: list[str] = []
        if self.inventory.get("shroom", 0):
            opts.append("Super Shroom")
        if self.inventory.get("max", 0):
            opts.append("Max Mushroom")
        if self.inventory.get("1up", 0):
            opts.append("1-Up")
        return opts

    def _use_item(self, name: str) -> None:
        if name == "Super Shroom" and self.inventory.get("shroom", 0):
            self.inventory["shroom"] -= 1
            for p in self.party:
                p.heal(20)
            self.log.append("Super Shroom! +20 HP all.")
            self._enemy_turn()
        elif name == "Max Mushroom" and self.inventory.get("max", 0):
            self.inventory["max"] -= 1
            for p in self.party:
                p.hp = p.max_hp
            self.log.append("Max Mushroom! Full heal.")
            self._enemy_turn()
        elif name == "1-Up" and self.inventory.get("1up", 0):
            self.inventory["1up"] -= 1
            for p in self.party:
                if not p.alive():
                    p.hp = p.max_hp // 2
            self.log.append("1-Up! Revived fallen partners.")
            self._enemy_turn()

    def tick(self) -> None:
        if self.bros_timer > 0:
            self.bros_timer -= 1
            if self.bros_timer == 15:
                self.bros_window = 12
            if self.bros_timer <= 0 and self.turn == "bros":
                self.pending_bros_dmg = 8
                self.log.append("Bros attack weak.")
                self._resolve_bros()
        if self.flash > 0:
            self.flash -= 1
        if not self._alive_party():
            self.done = True
            self.won = False
        elif not self._alive_foes():
            self.done = True
            self.won = True
            self.coins += 40 if self.is_boss else 15

    def _pick_action(self, action: str) -> None:
        foes = self._alive_foes()
        if not foes:
            return
        target = foes[0]
        if action == "Attack":
            dmg = sum(max(1, p.atk // 2) for p in self._alive_party()[:2])
            target.hp -= dmg
            self.log.append(f"Team attack → {dmg} dmg on {target.name}")
            self._enemy_turn()
        elif action == "Bros Move":
            self.turn = "bros_pick"
            self.sub_sel = 0
            self.bros_pick = None
        elif action == "Items":
            if not self._item_opts():
                self.log.append("No items!")
            else:
                self.turn = "items"
                self.sub_sel = 0
        elif action == "Flee":
            if random.random() < 0.55:
                self.done = True
                self.fled = True
                self.log.append("Got away safely!")
            else:
                self.log.append("Couldn't flee!")
                self._enemy_turn()

    def _resolve_bros(self) -> None:
        foes = self._alive_foes()
        if foes:
            foes[0].hp -= self.pending_bros_dmg
            self.log.append(f"Bros shell hit for {self.pending_bros_dmg}!")
        self.turn = "menu"
        self.bros_window = 0
        self._enemy_turn()

    def _enemy_turn(self) -> None:
        for foe in self._alive_foes():
            target = random.choice(self._alive_party())
            dmg = max(1, foe.atk - 2)
            target.hp -= dmg
            self.log.append(f"{foe.name} hits {target.name} for {dmg}")
            self.flash = 10
        if not self._alive_party():
            self.done = True
            self.won = False

    def draw(self, surface: pygame.Surface) -> None:
        assets = DSAssets.get()
        surface.fill(BATTLE_BG)
        for i in range(-HEIGHT, WIDTH + HEIGHT, 28):
            pygame.draw.line(surface, (22, 32, 58), (i, 0), (i - HEIGHT, HEIGHT), 14)
        pygame.draw.line(surface, DS_OUTLINE, (0, HEIGHT - 204), (WIDTH, HEIGHT - 204), 3)
        if self.flash > 0 and self.flash % 2 == 0:
            pygame.draw.rect(surface, (120, 30, 30), (0, 0, WIDTH, HEIGHT - 200), 5)

        assets.draw_ds_panel(surface, (0, HEIGHT - 200, WIDTH, 200))
        if self.is_boss:
            surface.blit(small_font.render("★ BOSS BATTLE ★", True, GOLD), (WIDTH // 2 - 90, 12))

        for i, p in enumerate(self.party):
            x = 24 + i * 245
            assets.draw_ds_panel(surface, (x, 28, 220, 118), p.color)
            spr = assets.partner_sprite(p.name)
            assets.blit_sprite(surface, spr, x + 10, 38, shadow=False)
            label = tiny_font.render(f"{p.name}", True, WHITE)
            surface.blit(label, (x + 72, 42))
            surface.blit(tiny_font.render(f"HP {p.hp}/{p.max_hp}  BP {p.bp}", True, (200, 220, 200)), (x + 72, 64))
            bar_w = int(130 * max(0, p.hp) / p.max_hp)
            pygame.draw.rect(surface, DS_OUTLINE, (x + 72, 88, 134, 16), 2, border_radius=3)
            pygame.draw.rect(surface, (30, 30, 30), (x + 74, 90, 130, 12), border_radius=2)
            pygame.draw.rect(surface, p.color, (x + 74, 90, bar_w, 12), border_radius=2)

        for i, e in enumerate(self.enemies):
            ex = WIDTH - 280 - i * 210
            spr = assets.enemy_sprite(e.name, e.era, sprite_key=e.sprite_key)
            mul = 2 if self.is_boss else 1
            big = pygame.transform.scale(spr, (spr.get_width() * mul, spr.get_height() * mul))
            assets.blit_sprite(surface, big, ex, 70)
            assets.draw_ds_panel(surface, (ex - 10, 200, big.get_width() + 20, 58), DS_SHROOB)
            surface.blit(small_font.render(e.name, True, WHITE), (ex, 210))
            surface.blit(tiny_font.render(f"HP {e.hp}/{e.max_hp}", True, (220, 200, 220)), (ex, 234))

        menu_x, menu_y = 24, HEIGHT - 188
        if self.turn == "menu":
            for i, opt in enumerate(self.menu_opts):
                col = AC_GREEN if i == self.menu_sel else (160, 180, 160)
                prefix = "▶ " if i == self.menu_sel else "  "
                surface.blit(small_font.render(prefix + opt, True, col), (menu_x, menu_y + i * 34))
        elif self.turn == "bros_pick":
            surface.blit(small_font.render("BROS MOVE", True, GOLD), (menu_x, menu_y - 28))
            for i, (name, dmg, cost) in enumerate(BROS_MOVES):
                col = AC_GREEN if i == self.sub_sel else (160, 180, 160)
                icon = assets.sprite_shell if "Shell" in name else assets.sprite_star
                surface.blit(icon, (menu_x, menu_y + i * 30))
                surface.blit(tiny_font.render(f"{name}  {dmg}dmg  {cost}BP", True, col), (menu_x + 36, menu_y + 4 + i * 30))
        elif self.turn == "items":
            surface.blit(small_font.render("ITEMS", True, GOLD), (menu_x, menu_y - 28))
            for i, opt in enumerate(self._item_opts()):
                col = AC_GREEN if i == self.sub_sel else (160, 180, 160)
                surface.blit(assets.sprite_shroom, (menu_x, menu_y + i * 30))
                surface.blit(tiny_font.render(opt, True, col), (menu_x + 36, menu_y + 4 + i * 30))
        elif self.turn == "bros":
            move = self.bros_pick[0] if self.bros_pick else "Bros"
            if self.bros_window > 0:
                pygame.draw.circle(surface, GOLD, (WIDTH // 2, HEIGHT - 130), 22)
                pygame.draw.circle(surface, WHITE, (WIDTH // 2, HEIGHT - 130), 14)
            msg = f"{move}: >>> PRESS SPACE <<<" if self.bros_window > 0 else f"{move}: Wait for flash..."
            surface.blit(font.render(msg, True, GOLD), (WIDTH // 2 - 240, HEIGHT - 120))

        assets.draw_ds_panel(surface, (380, HEIGHT - 188, WIDTH - 400, 168), (80, 120, 200))
        for i, line in enumerate(self.log[-5:]):
            surface.blit(tiny_font.render(line, True, (180, 220, 180)), (396, HEIGHT - 178 + i * 22))


def _new_party() -> list[Partner]:
    return [
        Partner("AC", AC_GREEN, 50, 12, 10, "lead"),
        Partner("Grok", GROK_PINK, 35, 8, 14, "baby"),
        Partner("Toad", TOAD_RED, 32, 7, 11, "baby"),
        Partner("AC Cat", (0, 200, 90), 42, 10, 9, "adult"),
    ]


INTRO_LINES = [
    "AC Holdings presents...",
    "Mario & Luigi: Partners in Time",
    "The Shroobs invade the Mushroom Kingdom!",
    "Baby AC, Grok, and Toad join adult AC Cat.",
    "Collect Cobalt Star shards across Past, Present, Future.",
    "Defeat bosses. Restore the timeline.",
    "Press ENTER to begin  •  P=Play  R=Reset",
]


class Game:
    def __init__(self) -> None:
        DSAssets.get()
        self.state = "menu"
        self.menu_selection = 0
        self.menu_options = ["Play", "Reset", "Help", "About", "Exit"]
        self.overworld: ACOverworld | None = None
        self.battle: Battle | None = None
        self.party = _new_party()
        self.coins = 12
        self.shards: set[str] = set()
        self.inventory = {"shroom": 2, "max": 0, "1up": 0}
        self.beans = 0
        self.final_boss_done = False
        self.sound_on = True
        self.help_scroll = 0
        self.paused = False
        self.intro_idx = 0
        self.shop_sel = 0
        self.dialogue_idx = 0
        self.dialogue_lines: list[str] = []
        self.pending_shard_era: str | None = None
        self.show_map = False
        self.show_party = False

    def reset_game(self) -> None:
        self.party = _new_party()
        self.coins = 12
        self.shards = set()
        self.inventory = {"shroom": 2, "max": 0, "1up": 0}
        self.beans = 0
        self.final_boss_done = False
        self.overworld = None
        self.battle = None
        self.state = "menu"
        self.paused = False
        self.intro_idx = 0
        self.show_map = False
        self.show_party = False
        self.pending_shard_era = None

    def start_play(self) -> None:
        self.party = _new_party()
        self.coins = 12
        self.shards = set()
        self.inventory = {"shroom": 2, "max": 0, "1up": 0}
        self.beans = 0
        self.final_boss_done = False
        self.overworld = ACOverworld(self.party, self.coins, self.shards)
        self.battle = None
        self.state = "intro"
        self.intro_idx = 0
        self.paused = False
        self.show_map = False
        self.show_party = False
        self.pending_shard_era = None

    def _start_battle(
        self,
        boss: tuple[str, int, int] | None = None,
        shard_era: str | None = None,
        wild_sprite_key: str | None = None,
    ) -> None:
        era = self.overworld.time_phase if self.overworld else "PRESENT"
        self.battle = Battle(
            self.party, era, self.coins,
            boss=boss, inventory=self.inventory, wild_sprite_key=wild_sprite_key,
        )
        self.battle.shard_reward = shard_era
        self.state = "battle"

    def _finish_battle(self) -> None:
        if not self.battle:
            return
        self.coins = self.battle.coins
        self.inventory = self.battle.inventory
        if self.battle.won and self.battle.shard_reward and self.overworld:
            self.overworld.grant_shard(self.battle.shard_reward)
            self.shards = set(self.overworld.shards)
        if (
            self.battle.won
            and self.battle.is_boss
            and self.battle.enemies
            and self.battle.enemies[0].name == FINAL_BOSS[0]
        ):
            self.final_boss_done = True
            self.state = "victory"
        else:
            self.state = "overworld"
        self.battle = None
        self.pending_shard_era = None

    def draw_menu(self) -> None:
        assets = DSAssets.get()
        screen.fill(MENU_BG)
        for i in range(60):
            pygame.draw.circle(screen, (30 + i % 5, 40 + i % 7, 70 + i % 9), ((i * 97) % WIDTH, (i * 53) % HEIGHT), 1)
        assets.draw_ds_panel(screen, (WIDTH // 2 - 340, 40, 680, 420))
        title = font.render("AC HOLDINGS", True, AC_GREEN)
        subtitle = font.render("PARTNERS IN TIME", True, (200, 255, 200))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 120))
        loc_count = sum(len(PIT_LOCATIONS[e]) for e in ERAS)
        tag = small_font.render(f"DS pixel assets  •  {loc_count} maps  •  files=off", True, (140, 180, 140))
        screen.blit(tag, (WIDTH // 2 - tag.get_width() // 2, 165))
        assets.blit_sprite(screen, assets.sprite_ac, WIDTH // 2 - 180, 200, shadow=False)
        assets.blit_sprite(screen, assets.sprite_grok, WIDTH // 2 - 60, 220, shadow=False)
        assets.blit_sprite(screen, assets.sprite_toad, WIDTH // 2 + 40, 220, shadow=False)
        assets.blit_sprite(screen, assets.sprite_cat, WIDTH // 2 + 120, 200, shadow=False)

        for i, option in enumerate(self.menu_options):
            color = AC_GREEN if i == self.menu_selection else (180, 200, 180)
            prefix = "▶ " if i == self.menu_selection else "  "
            screen.blit(font.render(prefix + option, True, color), (WIDTH // 2 - 100, 320 + i * 48))

        hint = small_font.render("↑↓ Select   ENTER Confirm   P=Play   R=Reset", True, (150, 200, 150))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 45))

    def draw_help(self) -> None:
        screen.fill(MENU_BG)
        lines = [
            "PARTNERS IN TIME — HELP",
            "",
            "OVERWORLD (Mario Wiki PiT locations)",
            "  WASD / Arrows — Move AC + partners",
            "  SPACE — Time Hole (Past → Present → Future)",
            "  TAB — Next location in current era",
            "  @ pads — Warp to next area in era",
            "  ENTER — Shop / NPC / shard / boss door",
            "  M — World map   I — Party status",
            "  ESC — Pause menu",
            "  P — Play (from title)   R — Reset run",
            "",
            "GAME PARTS",
            "  " + ", ".join(PIT_PARTS[:6]),
            "  " + ", ".join(PIT_PARTS[6:]),
            "",
            "QUEST",
            "  Cobalt Star shards: Hollijolli / Yoob's Belly / Shroob Castle",
            "  Beat era bosses, then Elder Shroob at Star Shrine (B door)",
            "",
            "BATTLE",
            "  Bros Move — Green/Red Shell, Baby Drill, Trampoline (BP cost)",
            "  Items — Super Shroom, Max Mushroom, 1-Up",
            "  Shroom Shop (S tiles) — buy supplies with coins",
            "",
            "Press ESC to return",
        ]
        for i, line in enumerate(lines):
            col = AC_GREEN if i == 0 else WHITE
            screen.blit(small_font.render(line, True, col), (80, 50 + i * 28))

    def draw_about(self) -> None:
        screen.fill(MENU_BG)
        lines = [
            "AC Holdings • Partners in Time",
            "CatSDK + Grok homage to Mario & Luigi: PiT",
            "Maps: mariowiki.com PiT locations category",
            "",
            "AC — lead brother",
            "Grok Kitten + Grok Toad — baby partners",
            "AC Cat — adult partner",
            "",
            "Travel time. Fight Shroobs. Save the timeline.",
            "Single file. No assets. Pure vibe.",
            "",
            "Press ESC to return",
        ]
        for i, line in enumerate(lines):
            screen.blit(small_font.render(line, True, AC_GREEN if i < 2 else (200, 220, 200)), (100, 80 + i * 32))

    def draw_intro(self) -> None:
        screen.fill((5, 10, 25))
        for i, line in enumerate(INTRO_LINES[: self.intro_idx + 1]):
            col = AC_GREEN if i == 0 else WHITE
            screen.blit(small_font.render(line, True, col), (80, 120 + i * 36))

    def draw_shop(self) -> None:
        assets = DSAssets.get()
        screen.fill((25, 15, 35))
        assets.draw_ds_panel(screen, (WIDTH // 2 - 360, 40, 720, HEIGHT - 80), (255, 140, 180))
        screen.blit(font.render("SHROOM SHOP", True, AC_GREEN), (WIDTH // 2 - 140, 60))
        screen.blit(assets.sprite_shroom, (WIDTH // 2 - 200, 55))
        screen.blit(small_font.render(f"Coins: {self.coins}", True, GOLD), (WIDTH // 2 + 40, 110))
        for i, (name, price, _) in enumerate(SHOP_STOCK):
            col = AC_GREEN if i == self.shop_sel else (180, 200, 180)
            owned = ""
            if price <= 15:
                owned = f"  x{self.inventory.get('shroom', 0)}"
            elif price <= 35:
                owned = f"  x{self.inventory.get('max', 0)}"
            else:
                owned = f"  x{self.inventory.get('1up', 0)}"
            y = 180 + i * 52
            assets.draw_ds_panel(screen, (100, y - 6, WIDTH - 200, 46), col if i == self.shop_sel else (60, 80, 120))
            screen.blit(assets.sprite_shroom, (120, y))
            screen.blit(small_font.render(f"{name}  ★{price}{owned}", True, col), (170, y + 8))
        screen.blit(tiny_font.render("ENTER buy   ESC leave", True, (150, 170, 150)), (WIDTH // 2 - 90, HEIGHT - 40))

    def buy_shop_item(self) -> None:
        name, price, effect = SHOP_STOCK[self.shop_sel]
        if self.coins < price:
            return
        self.coins -= price
        if effect == "heal20":
            self.inventory["shroom"] = self.inventory.get("shroom", 0) + 1
        elif effect == "healfull":
            self.inventory["max"] = self.inventory.get("max", 0) + 1
        elif effect == "revive":
            self.inventory["1up"] = self.inventory.get("1up", 0) + 1
        elif effect == "bp3":
            for p in self.party:
                p.restore_bp(3)

    def draw_dialogue(self) -> None:
        screen.fill((10, 15, 30))
        pygame.draw.rect(screen, HUD_BG, (60, HEIGHT // 2 - 100, WIDTH - 120, 200), border_radius=12)
        for i, line in enumerate(self.dialogue_lines[: self.dialogue_idx + 1]):
            screen.blit(small_font.render(line, True, WHITE), (90, HEIGHT // 2 - 70 + i * 32))
        screen.blit(tiny_font.render("ENTER continue   ESC close", True, (150, 170, 150)), (WIDTH // 2 - 120, HEIGHT // 2 + 120))

    def draw_map_overlay(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        screen.blit(font.render("WORLD MAP", True, AC_GREEN), (WIDTH // 2 - 100, 40))
        y = 100
        for era in ERAS:
            screen.blit(small_font.render(f"=== {era} ===", True, GOLD), (80, y))
            y += 32
            for loc in PIT_LOCATIONS[era]:
                mark = "★" if era in self.shards and loc.get("shard") else " "
                screen.blit(tiny_font.render(f"  {mark} {loc['name']}", True, WHITE), (100, y))
                y += 22
            y += 10
        screen.blit(tiny_font.render("M or ESC to close", True, (150, 170, 150)), (WIDTH // 2 - 70, HEIGHT - 30))

    def draw_party_overlay(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        screen.blit(font.render("PARTY STATUS", True, AC_GREEN), (WIDTH // 2 - 120, 50))
        for i, p in enumerate(self.party):
            y = 120 + i * 110
            pygame.draw.rect(screen, HUD_BG, (100, y, WIDTH - 200, 90), border_radius=8)
            screen.blit(small_font.render(f"{p.name} ({p.role})", True, p.color), (120, y + 12))
            screen.blit(tiny_font.render(f"HP {p.hp}/{p.max_hp}  ATK {p.atk}  SPD {p.spd}  BP {p.bp}/{p.max_bp}", True, WHITE), (120, y + 44))
        screen.blit(tiny_font.render(f"Beans: {self.beans}  Items: shroom×{self.inventory.get('shroom',0)} max×{self.inventory.get('max',0)}", True, GOLD), (120, HEIGHT - 60))
        screen.blit(tiny_font.render("I or ESC to close", True, (150, 170, 150)), (WIDTH // 2 - 70, HEIGHT - 30))

    def draw_pause(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        screen.blit(font.render("PAUSED", True, AC_GREEN), (WIDTH // 2 - 70, HEIGHT // 2 - 80))
        for i, opt in enumerate(["Resume", "Reset", "Title Menu"]):
            screen.blit(small_font.render(opt, True, WHITE), (WIDTH // 2 - 50, HEIGHT // 2 + i * 36))

    def draw_hud(self) -> None:
        if not self.overworld:
            return
        assets = DSAssets.get()
        assets.draw_ds_panel(screen, (0, 0, WIDTH, 62))
        ow = self.overworld
        screen.blit(assets.sprite_star, (12, 10))
        screen.blit(small_font.render(f"{ow.coins}", True, GOLD), (44, 14))
        screen.blit(small_font.render(ow.area_name(), True, WHITE), (120, 14))
        era_col = (255, 160, 80) if ow.time_phase == "PAST" else AC_GREEN if ow.time_phase == "PRESENT" else (120, 220, 255)
        screen.blit(small_font.render(f"ERA: {ow.time_phase}", True, era_col), (WIDTH // 2 - 60, 14))
        shards = "/".join(e[0] for e in ERAS if e in ow.shards) or "—"
        screen.blit(assets.sprite_star, (WIDTH - 310, 8))
        screen.blit(small_font.render(f"Cobalt {len(ow.shards)}/3 [{shards}]", True, GOLD), (WIDTH - 270, 14))
        if len(ow.shards) >= 3:
            screen.blit(tiny_font.render("→ Star Shrine B door", True, AC_GREEN), (WIDTH - 270, 36))
        for i, p in enumerate(ow.party):
            spr = assets.partner_sprite(p.name)
            screen.blit(pygame.transform.scale(spr, (20, 24)), (14 + i * 26, 36))
        hp_txt = "  ".join(f"{p.hp}" for p in ow.party)
        screen.blit(tiny_font.render(hp_txt, True, (180, 200, 180)), (130, 38))
        if ow.message_timer > 0:
            assets.draw_ds_panel(screen, (WIDTH // 2 - 220, HEIGHT - 88, 440, 36))
            screen.blit(small_font.render(ow.message, True, AC_GREEN), (WIDTH // 2 - 200, HEIGHT - 80))

    def draw_victory(self) -> None:
        screen.fill((10, 30, 20))
        screen.blit(font.render("TIMELINE RESTORED!", True, AC_GREEN), (WIDTH // 2 - 220, 200))
        screen.blit(small_font.render(f"Coins: {self.coins}  •  All Time Shards secured", True, WHITE), (WIDTH // 2 - 200, 280))
        screen.blit(small_font.render("ENTER = Play again   ESC = Title", True, (180, 200, 180)), (WIDTH // 2 - 180, 360))

    def draw_gameover(self) -> None:
        screen.fill((30, 10, 10))
        screen.blit(font.render("PARTNERS DOWN...", True, TOAD_RED), (WIDTH // 2 - 200, 220))
        screen.blit(small_font.render("ENTER = Reset   ESC = Title", True, (200, 180, 180)), (WIDTH // 2 - 140, 300))

    def run(self) -> None:
        running = True
        pause_sel = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    key = event.key

                    if key == pygame.K_p and self.state in ("menu", "intro"):
                        self.start_play()
                    if key == pygame.K_r and self.state in ("menu", "intro", "overworld", "shop", "dialogue", "victory", "gameover"):
                        self.reset_game()

                    if self.state == "menu":
                        if key == pygame.K_UP:
                            self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                        elif key == pygame.K_DOWN:
                            self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                        elif key == pygame.K_RETURN:
                            opt = self.menu_options[self.menu_selection]
                            if opt == "Play":
                                self.start_play()
                            elif opt == "Reset":
                                self.reset_game()
                            elif opt == "Help":
                                self.state = "help"
                            elif opt == "About":
                                self.state = "about"
                            elif opt == "Exit":
                                running = False

                    elif self.state == "help" and key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif self.state == "about" and key == pygame.K_ESCAPE:
                        self.state = "menu"

                    elif self.state == "victory":
                        if key == pygame.K_RETURN:
                            self.start_play()
                        elif key == pygame.K_ESCAPE:
                            self.reset_game()
                    elif self.state == "gameover":
                        if key == pygame.K_RETURN:
                            self.reset_game()
                            self.start_play()
                        elif key == pygame.K_ESCAPE:
                            self.reset_game()

                    elif self.state == "intro":
                        if key in (pygame.K_RETURN, pygame.K_SPACE):
                            if self.intro_idx < len(INTRO_LINES) - 1:
                                self.intro_idx += 1
                            else:
                                self.state = "overworld"
                        elif key == pygame.K_ESCAPE:
                            self.state = "overworld"

                    elif self.state == "shop":
                        if key == pygame.K_UP:
                            self.shop_sel = (self.shop_sel - 1) % len(SHOP_STOCK)
                        elif key == pygame.K_DOWN:
                            self.shop_sel = (self.shop_sel + 1) % len(SHOP_STOCK)
                        elif key == pygame.K_RETURN:
                            self.buy_shop_item()
                        elif key == pygame.K_ESCAPE:
                            self.state = "overworld"

                    elif self.state == "dialogue":
                        if key == pygame.K_RETURN:
                            if self.dialogue_idx < len(self.dialogue_lines) - 1:
                                self.dialogue_idx += 1
                            else:
                                self.state = "overworld"
                        elif key == pygame.K_ESCAPE:
                            self.state = "overworld"

                    elif self.state == "overworld":
                        if key == pygame.K_m:
                            self.show_map = not self.show_map
                        elif key == pygame.K_i:
                            self.show_party = not self.show_party
                        elif key == pygame.K_ESCAPE:
                            if self.show_map:
                                self.show_map = False
                            elif self.show_party:
                                self.show_party = False
                            else:
                                self.paused = not self.paused
                                pause_sel = 0
                        elif self.paused:
                            if key == pygame.K_UP:
                                pause_sel = (pause_sel - 1) % 3
                            elif key == pygame.K_DOWN:
                                pause_sel = (pause_sel + 1) % 3
                            elif key == pygame.K_RETURN:
                                if pause_sel == 0:
                                    self.paused = False
                                elif pause_sel == 1:
                                    self.start_play()
                                else:
                                    self.reset_game()
                        elif key == pygame.K_SPACE and self.overworld and not self.paused:
                            self.overworld.travel_time()
                        elif key == pygame.K_TAB and self.overworld and not self.paused:
                            self.overworld.next_location()
                        elif key == pygame.K_RETURN and self.overworld and not self.paused:
                            result = self.overworld.interact()
                            if result == "shop":
                                self.shop_sel = 0
                                self.state = "shop"
                            elif result == "dialogue":
                                area = self.overworld.area_name()
                                self.dialogue_lines = list(
                                    NPC_LINES.get(area, [f"Welcome to {area}!", "Press onward, partners!"])
                                )
                                if not self.dialogue_lines:
                                    self.dialogue_lines = ["..."]
                                self.dialogue_idx = 0
                                self.state = "dialogue"
                            elif result == "final_boss":
                                self._start_battle(boss=FINAL_BOSS)
                            elif result and result.startswith("boss:"):
                                era = result.split(":", 1)[1]
                                if era in BOSS_BY_ERA:
                                    self._start_battle(boss=BOSS_BY_ERA[era], shard_era=era)

                    elif self.state == "battle" and self.battle:
                        if key == pygame.K_ESCAPE and self.battle.done:
                            self._finish_battle()
                        elif key == pygame.K_RETURN and self.battle.done:
                            self._finish_battle()
                        else:
                            self.battle.update_key(key)

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "intro":
                self.draw_intro()
            elif self.state == "shop":
                self.draw_shop()
            elif self.state == "dialogue":
                self.draw_dialogue()
            elif self.state == "help":
                self.draw_help()
            elif self.state == "about":
                self.draw_about()
            elif self.state == "victory":
                self.draw_victory()
            elif self.state == "gameover":
                self.draw_gameover()
            elif self.state == "overworld" and self.overworld:
                if not self.paused:
                    result = self.overworld.update()
                    self.coins = self.overworld.coins
                    self.shards = set(self.overworld.shards)
                    if result == "battle":
                        wild_key = self.overworld.pending_battle_sprite
                        self.overworld.pending_battle_sprite = None
                        self._start_battle(wild_sprite_key=wild_key)
                    elif result == "victory":
                        self.state = "victory"
                if self.state == "overworld":
                    bg = (40, 30, 10) if self.overworld.time_phase == "PAST" else (10, 40, 15) if self.overworld.time_phase == "PRESENT" else (5, 5, 20)
                    screen.fill(bg)
                    self.overworld.draw(screen)
                    self.draw_hud()
                    if self.show_map:
                        self.draw_map_overlay()
                    if self.show_party:
                        self.draw_party_overlay()
                    if self.paused:
                        self.draw_pause()
            elif self.state == "battle" and self.battle:
                self.battle.tick()
                self.battle.draw(screen)
                if self.battle.done:
                    hint = "ENTER — continue"
                    screen.blit(tiny_font.render(hint, True, (150, 170, 150)), (WIDTH // 2 - 60, HEIGHT - 30))
                    if not self.battle.fled and not self.battle.won:
                        if not any(p.alive() for p in self.party):
                            self.state = "gameover"

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    if sys.version_info < (3, 14):
        print(f"Partners in Time: Python 3.14+ recommended (running {sys.version_info.major}.{sys.version_info.minor})")
    Game().run()
