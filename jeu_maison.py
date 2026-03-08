from __future__ import annotations

import json
from collections import Counter
import os
import random
import re
import time



RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BLUE = "\033[94m"

PRISON_GRID = [
    "###############",
    "#@..B.#.......#",
    "#....##...G...#",
    "#..I.#........#",
    "#.............#",
    "#...#######...#",
    "#....G..#.....#",
    "#.......#.....#",
    "#.......#.....#",
    "#...........D.#",
    "###############",
]

CITY_GRID = [
    "###############",
    "#.............#",
    "#..C.....A....#",
    "#.............#",
    "#.....####....#",
    "#.............#",
    "#...M......T..#",
    "#.............#",
    "#......S......#",
    "#.........O.D.#",
    "###############",
]

WORLD_WIDTH = 21
WORLD_HEIGHT = 13

CASTLE_GRID = [
    "#########",
    "#...K...#",
    "#.......#",
    "#...D...#",
    "#########",
]

ARMORER_GRID = [
    "#########",
    "#.......#",
    "#.......#",
    "#...D...#",
    "#########",
]

MERCHANT_GRID = [
    "#########",
    "#.......#",
    "#.......#",
    "#...D...#",
    "#########",
]

RITUAL_GRID = [
    "###########",
    "#....Y....#",
    "#.........#",
    "#....Z....#",
    "#.........#",
    "#....D....#",
    "###########",
]

SUMMON_ARENA_GRID = [
    "###########",
    "#.........#",
    "#.........#",
    "#....X....#",
    "#.........#",
    "#.........#",
    "###########",
]

TAVERN_GRID = [
    "#########",
    "#...Q...#",
    "#.......#",
    "#...D...#",
    "#########",
]

TILE_INFO = {
    "#": ("Wall", RED),
    ".": ("Floor", DIM),
    "B": ("Bunk bed", YELLOW),
    "G": ("Guard", MAGENTA),
    "I": ("Stash", CYAN),
    "D": ("Prison gate", CYAN),
    "C": ("Castle", WHITE),
    "A": ("Armorer", BLUE),
    "M": ("Merchant", YELLOW),
    "T": ("Tavern", MAGENTA),
    "S": ("City square", GREEN),
    "O": ("World gate", CYAN),
    "W": ("City", YELLOW),
    "V": ("Village", YELLOW),
    "F": ("Forest", GREEN),
    "H": ("Cave", BLUE),
    "U": ("Dungeon", RED),
    "X": ("Monster", RED),
    "L": ("Treasure chest", YELLOW),
    "w": ("Weapon counter", CYAN),
    "r": ("Armor counter", BLUE),
    "p": ("Potion counter", MAGENTA),
    "K": ("King", YELLOW),
    "Q": ("Quest patron", MAGENTA),
    "R": ("Ritual site", MAGENTA),
    "Y": ("Armor altar", BLUE),
    "Z": ("Weapon altar", RED),
}

AREA_META = {
    "prison": {"title": "PRISON", "place": "Prison of Ardri"},
    "city": {"title": "CITY OF ARDRI", "place": "Ardri"},
    "castle": {"title": "CASTLE", "place": "Castle of Ardri"},
    "armorer": {"title": "ARMORER", "place": "Armorer of Ardri"},
    "merchant": {"title": "MERCHANT", "place": "Merchant Stall"},
    "ritual": {"title": "RITUAL CIRCLE", "place": "Ritual Circle"},
    "summon_arena": {"title": "SUMMON ARENA", "place": "Summon Arena"},
    "tavern": {"title": "TAVERN", "place": "Tavern of Ardri"},
    "world": {"title": "WORLD MAP", "place": "The Wilds"},
    "village": {"title": "VILLAGE", "place": "Village"},
    "forest": {"title": "FOREST", "place": "Forest"},
    "cave": {"title": "CAVE", "place": "Cave"},
    "dungeon": {"title": "DUNGEON", "place": "Dungeon"},
}

CITY_NAMES = ["Jourda", "Velm", "Corven", "Eldhame", "Rith", "Norwyn"]
VILLAGE_NAMES = ["Willowfen", "Brindle", "Oakrest", "Fenmere", "Ashby"]
FOREST_NAMES = ["Whisperwood", "Blackpine", "Mossgrove", "Greenthorn"]
CAVE_NAMES = ["Old Man's Cave", "Hollow Fang", "Moon Hollow", "Stone Maw"]
DUNGEON_NAMES = ["Sunken Vault", "Iron Depths", "Grimhold", "Broken Crypt"]
KING_QUEST_LEVEL = 10
SUMMON_BOSS_LEVEL = 15

ITEM_DATA = {
    "shiv": {"kind": "weapon", "buy": 0, "sell": 10, "damage": (5, 8)},
    "iron sword": {"kind": "weapon", "buy": 30, "sell": 15, "damage": (7, 11)},
    "steel sword": {"kind": "weapon", "buy": 65, "sell": 33, "damage": (10, 14)},
    "war axe": {"kind": "weapon", "buy": 95, "sell": 48, "damage": (12, 17)},
    "leather armor": {"kind": "armor", "buy": 24, "sell": 12, "armor": 1},
    "chain armor": {"kind": "armor", "buy": 55, "sell": 28, "armor": 2},
    "scale armor": {"kind": "armor", "buy": 78, "sell": 39, "armor": 3},
    "royal mail": {"kind": "armor", "buy": 135, "sell": 68, "armor": 5},
    "small potion": {"kind": "potion", "buy": 10, "sell": 5, "heal": 12},
    "large potion": {"kind": "potion", "buy": 22, "sell": 11, "heal": 25},
    "greater potion": {"kind": "potion", "buy": 40, "sell": 20, "heal": 45},
    "sun tonic": {"kind": "potion", "buy": 70, "sell": 35, "heal": 80},
    "ember heart": {"kind": "reagent", "buy": 0, "sell": 18},
    "grave dust": {"kind": "reagent", "buy": 0, "sell": 16},
    "moon fang": {"kind": "reagent", "buy": 0, "sell": 22},
    "titan shard": {"kind": "reagent", "buy": 0, "sell": 26},
    "silver blade": {"kind": "weapon", "buy": 0, "sell": 60, "damage": (10, 15)},
    "king's blade": {"kind": "weapon", "buy": 0, "sell": 160, "damage": (18, 24)},
    "voidfang": {"kind": "weapon", "buy": 0, "sell": 320, "damage": (22, 28)},
    "warden plate": {"kind": "armor", "buy": 0, "sell": 75, "armor": 4},
    "ashen crown": {"kind": "armor", "buy": 0, "sell": 180, "armor": 7},
    "astral bulwark": {"kind": "armor", "buy": 0, "sell": 340, "armor": 10},
    "cell key": {"kind": "key", "buy": 0, "sell": 0},
}

DUNGEON_MONSTERS = [
    {"enemy_name": "Bone Warden", "enemy_hp": 22, "enemy_max_hp": 22, "enemy_attack": 7, "xp": 10, "money": 10, "drops": ["small potion", "large potion", "grave dust"]},
    {"enemy_name": "Cave Stalker", "enemy_hp": 24, "enemy_max_hp": 24, "enemy_attack": 8, "xp": 11, "money": 11, "drops": ["shiv", "small potion", "steel sword", "titan shard"]},
    {"enemy_name": "Ash Rat", "enemy_hp": 18, "enemy_max_hp": 18, "enemy_attack": 6, "xp": 8, "money": 8, "drops": ["large potion", "greater potion", "ember heart"]},
    {"enemy_name": "Grave Knight", "enemy_hp": 28, "enemy_max_hp": 28, "enemy_attack": 10, "xp": 14, "money": 16, "drops": ["chain armor", "scale armor", "greater potion", "grave dust"]},
]

FOREST_MONSTERS = [
    {"enemy_name": "Wild Boar", "enemy_hp": 12, "enemy_max_hp": 12, "enemy_attack": 4, "xp": 4, "money": 4, "drops": ["small potion", "ember heart"]},
    {"enemy_name": "Forest Wolf", "enemy_hp": 14, "enemy_max_hp": 14, "enemy_attack": 5, "xp": 5, "money": 5, "drops": ["shiv", "small potion", "moon fang"]},
    {"enemy_name": "Thorn Lynx", "enemy_hp": 17, "enemy_max_hp": 17, "enemy_attack": 6, "xp": 6, "money": 7, "drops": ["large potion", "leather armor", "moon fang"]},
]

CAVE_MONSTERS = [
    {"enemy_name": "Cave Fang", "enemy_hp": 18, "enemy_max_hp": 18, "enemy_attack": 6, "xp": 7, "money": 7, "drops": ["small potion", "leather armor", "greater potion", "ember heart"]},
    {"enemy_name": "Stone Crawler", "enemy_hp": 20, "enemy_max_hp": 20, "enemy_attack": 7, "xp": 8, "money": 8, "drops": ["iron sword", "large potion", "steel sword", "titan shard"]},
    {"enemy_name": "Tunnel Reaver", "enemy_hp": 24, "enemy_max_hp": 24, "enemy_attack": 9, "xp": 10, "money": 10, "drops": ["chain armor", "greater potion", "titan shard"]},
]

FINAL_BOSS = {
    "enemy_name": "Ashen Tyrant",
    "enemy_hp": 95,
    "enemy_max_hp": 95,
    "enemy_attack": 16,
    "xp": 80,
    "money": 180,
    "drops": ["ashen crown", "greater potion", "sun tonic"],
}

SUMMON_BOSSES = {
    "armor": {
        "enemy_name": "Astral Colossus",
        "enemy_hp": 105,
        "enemy_max_hp": 105,
        "enemy_attack": 18,
        "xp": 90,
        "money": 140,
        "drops": ["greater potion", "titan shard"],
        "requirements": {"ember heart": 2, "grave dust": 2, "titan shard": 1},
        "rare_drop": "astral bulwark",
        "altar_tile": "Y",
    },
    "weapon": {
        "enemy_name": "Void Seraph",
        "enemy_hp": 98,
        "enemy_max_hp": 98,
        "enemy_attack": 20,
        "xp": 90,
        "money": 140,
        "drops": ["sun tonic", "moon fang"],
        "requirements": {"moon fang": 2, "ember heart": 1, "titan shard": 2},
        "rare_drop": "voidfang",
        "altar_tile": "Z",
    },
}

TAVERN_QUESTS = [
    {
        "id": "forest_hunt",
        "title": "Tavern Hunt",
        "text": "A hunter wants 3 beasts cleared from the forests.",
        "target": "forest_kills",
        "required_level": 1,
        "goal": 3,
        "reward_money": 30,
        "reward_xp": 12,
        "reward_item": "large potion",
    },
    {
        "id": "cave_clear",
        "title": "Cave Contract",
        "text": "A miner pays for 3 monsters driven out of the caves.",
        "target": "cave_kills",
        "required_level": 1,
        "goal": 3,
        "reward_money": 55,
        "reward_xp": 18,
        "reward_item": "steel sword",
    },
    {
        "id": "deep_plunder",
        "title": "Delver's Wager",
        "text": "A delver offers a reward for opening 1 dungeon chest.",
        "target": "dungeon_chests",
        "required_level": 7,
        "goal": 1,
        "reward_money": 90,
        "reward_xp": 24,
        "reward_item": "scale armor",
    },
]

ALIASES = {
    "z": "up",
    "w": "up",
    "up": "up",
    "haut": "up",
    "s": "down",
    "down": "down",
    "bas": "down",
    "q": "left",
    "left": "left",
    "gauche": "left",
    "a": "attack",
    "e": "interact",
    "interagir": "interact",
    "interact": "interact",
    "d": "right",
    "right": "right",
    "droite": "right",
    "aide": "help",
    "help": "help",
    "regarder": "look",
    "look": "look",
    "inv": "inventory",
    "inventaire": "inventory",
    "inventory": "inventory",
    "m": "money",
    "money": "money",
    "stats": "stats",
    "reset": "reset",
    "use": "use",
    "buy": "buy",
    "sell": "sell",
    "fight": "fight",
    "f": "flee",
    "p": "potion",
    "potion": "potion",
    "run": "flee",
    "fuir": "flee",
    "fuite": "flee",
    "equiper": "equip",
    "equip": "equip",
    "unequip": "unequip",
    "attaquer": "attack",
    "attack": "attack",
    "continuer": "attack",
    "continue": "attack",
    "tour": "attack",
    "quitter": "quit",
    "exit": "quit",
    "quit": "quit",
    "cheat": "cheat",
}

MOVES = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
BAR_WIDTH = 20
RIPOSTE_DELAY = 0.5
GUARD_RESPAWN_DELAY = 20 * 60
SAVE_FILE = "savegame.json"
DEATH_COUNTDOWN_DELAY = 1


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def clone_grid(grid: list[str]) -> list[list[str]]:
    return [list(row) for row in grid]


def find_tile(grid: list[list[str]], target: str) -> tuple[int, int]:
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            if tile == target:
                return x, y
    return 1, 1


def find_all_tiles(grid: list[list[str]], target: str) -> list[tuple[int, int]]:
    positions = []
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            if tile == target:
                positions.append((x, y))
    return positions


def pos_key(x: int, y: int) -> str:
    return f"{x},{y}"


def generate_city_grid() -> list[list[str]]:
    width = 15
    height = 11
    grid = [["."] * width for _ in range(height)]

    for x in range(width):
        grid[0][x] = "#"
        grid[height - 1][x] = "#"
    for y in range(height):
        grid[y][0] = "#"
        grid[y][width - 1] = "#"

    grid[height - 2][width - 2] = "O"

    slots = [(2, 2), (5, 2), (9, 2), (3, 5), (8, 5), (11, 6), (6, 8)]
    random.shuffle(slots)
    buildings = ["C", "A", "M", "T", "S"]
    random.shuffle(buildings)
    count = random.randint(3, 5)

    for building, (x, y) in zip(buildings[:count], slots[:count]):
        grid[y][x] = building

    return grid


def generate_site_grid(kind: str) -> list[list[str]]:
    width = 11
    height = 7
    grid = [["."] * width for _ in range(height)]

    for x in range(width):
        grid[0][x] = "#"
        grid[height - 1][x] = "#"
    for y in range(height):
        grid[y][0] = "#"
        grid[y][width - 1] = "#"

    grid[height - 2][width // 2] = "D"

    obstacle_count = {"V": 3, "F": 4, "H": 4, "U": 5}.get(kind, 4)
    obstacle_tile = {"V": "B", "F": "B", "H": "B", "U": "#"}.get(kind, "#")

    placed = 0
    while placed < obstacle_count:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 3)
        if grid[y][x] == ".":
            grid[y][x] = obstacle_tile if obstacle_tile != "#" else "#"
            placed += 1

    if kind in {"F", "H", "U"}:
        monsters = {"F": random.randint(1, 2), "H": random.randint(2, 3), "U": random.randint(2, 4)}[kind]
        placed = 0
        while placed < monsters:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 3)
            if grid[y][x] == ".":
                grid[y][x] = "X"
                placed += 1

    if kind == "U":
        grid[1][width // 2] = "L"

    return grid


def generate_final_boss_room() -> list[list[str]]:
    grid = clone_grid([
        "###########",
        "#....L....#",
        "#.........#",
        "#....X....#",
        "#.........#",
        "#....D....#",
        "###########",
    ])
    return grid


def add_final_dungeon(world_tiles: list[list[str]], locations: dict[str, dict]) -> None:
    for location in locations.values():
        if location.get("final_dungeon"):
            return

    while True:
        x = random.randint(1, WORLD_WIDTH - 2)
        y = random.randint(1, WORLD_HEIGHT - 2)
        if world_tiles[y][x] == ".":
            world_tiles[y][x] = "U"
            locations[pos_key(x, y)] = {
                "tile": "U",
                "name": "Black Throne",
                "world_pos": [x, y],
                "level": 7,
                "rooms": [generate_site_grid("U") for _ in range(3)] + [generate_final_boss_room()],
                "room_index": 0,
                "chest_opened": False,
                "final_dungeon": True,
            }
            return


def add_ritual_site(world_tiles: list[list[str]], locations: dict[str, dict]) -> None:
    for location in locations.values():
        if location.get("ritual_site"):
            return

    while True:
        x = random.randint(1, WORLD_WIDTH - 2)
        y = random.randint(1, WORLD_HEIGHT - 2)
        if world_tiles[y][x] == ".":
            world_tiles[y][x] = "R"
            locations[pos_key(x, y)] = {
                "tile": "R",
                "name": "Ritual Circle",
                "world_pos": [x, y],
                "ritual_site": True,
            }
            return


def generate_world_data() -> tuple[list[list[str]], dict]:
    grid = generate_world_grid()
    locations: dict[str, dict] = {}

    ardri_pos = find_tile(grid, "W")
    locations[pos_key(*ardri_pos)] = {"tile": "W", "name": "Ardri", "city_id": "ardri"}

    used_city_names = set()
    city_index = 1
    for x, y in find_all_tiles(grid, "W"):
        key = pos_key(x, y)
        if key in locations:
            continue
        name = random.choice([n for n in CITY_NAMES if n not in used_city_names])
        used_city_names.add(name)
        locations[key] = {
            "tile": "W",
            "name": f"City of {name}",
            "city_id": f"city_{city_index}",
            "grid": generate_city_grid(),
            "world_pos": [x, y],
        }
        city_index += 1

    pools = {
        "V": VILLAGE_NAMES,
        "F": FOREST_NAMES,
        "H": CAVE_NAMES,
        "U": DUNGEON_NAMES,
    }

    for tile, names in pools.items():
        used = set()
        for x, y in find_all_tiles(grid, tile):
            available = [name for name in names if name not in used] or names
            name = random.choice(available)
            used.add(name)
            entry = {"tile": tile, "name": name, "world_pos": [x, y]}
            if tile == "U":
                level = random.randint(1, 5)
                entry["level"] = level
                room_count = random.randint(2 + level, 4 + level)
                entry["rooms"] = [generate_site_grid(tile) for _ in range(room_count)]
                for room in entry["rooms"][:-1]:
                    for yy, row in enumerate(room):
                        for xx, ch in enumerate(row):
                            if ch == "L":
                                room[yy][xx] = "."
                entry["room_index"] = 0
                entry["chest_opened"] = False
            else:
                entry["grid"] = generate_site_grid(tile)
            locations[pos_key(x, y)] = entry

    add_final_dungeon(grid, locations)
    add_ritual_site(grid, locations)

    return grid, locations


def final_dungeon_location(state: dict) -> dict | None:
    for location in state.get("world_locations", {}).values():
        if location.get("final_dungeon"):
            return location
    return None


def active_location(state: dict) -> dict | None:
    world_pos = state.get("active_world_pos")
    if not world_pos:
        return None
    return world_location_at(state, world_pos[0], world_pos[1])


def item_count(state: dict, item: str) -> int:
    return state.get("inventory", []).count(item)


def consume_items(state: dict, requirements: dict[str, int]) -> None:
    for item, amount in requirements.items():
        for _ in range(amount):
            state["inventory"].remove(item)


def requirement_text(requirements: dict[str, int]) -> str:
    return ", ".join(f"{amount}x {item}" for item, amount in requirements.items())


def can_pay_requirements(state: dict, requirements: dict[str, int]) -> bool:
    return all(item_count(state, item) >= amount for item, amount in requirements.items())


def summon_boss(state: dict, boss_key: str) -> str:
    data = SUMMON_BOSSES[boss_key]
    requirements = data["requirements"]
    if state.get("level", 1) < SUMMON_BOSS_LEVEL:
        return f"Ancient runes reject you. This altar only answers champions of level {SUMMON_BOSS_LEVEL} or higher."
    if not can_pay_requirements(state, requirements):
        return f"You need {requirement_text(requirements)} to summon {data['enemy_name']}."

    consume_items(state, requirements)
    boss = dict(data)
    boss["has_key"] = False
    boss["boss"] = True
    boss["summoned_boss"] = boss_key
    boss["loot_items"] = [item for item in boss.get("drops", []) if random.random() <= 0.65]
    if random.random() <= 0.10:
        boss["loot_items"].append(data["rare_drop"])
    arena = clone_grid(SUMMON_ARENA_GRID)
    state["summon_arena_tiles"] = arena
    state["summoned_boss"] = boss
    state["summoned_boss_key"] = boss_key
    add_loot_log(state, [f"Summon used -> {requirement_text(requirements)}"])
    load_area(state, "summon_arena")
    return f"{data['enemy_name']} answers the ritual. The offerings vanish and a battle gate opens before you."


def active_tavern_quest(state: dict) -> dict | None:
    for quest in state.get("tavern_quests", []):
        if quest.get("status") in {"active", "ready"}:
            return quest
    return None


def next_tavern_quest(state: dict) -> dict | None:
    for quest in state.get("tavern_quests", []):
        if quest.get("status") == "locked":
            return quest
    return None


def refresh_king_quest(state: dict) -> None:
    king_quest = state.setdefault("king_quest", {})
    if (
        king_quest.get("status") == "locked"
        and state.get("level", 1) >= KING_QUEST_LEVEL
        and all(
        quest.get("status") == "done" for quest in state.get("tavern_quests", [])
        )
    ):
        king_quest["status"] = "available"


def track_progress(state: dict, target: str, amount: int = 1) -> None:
    quest = active_tavern_quest(state)
    if not quest or quest.get("target") != target:
        return
    quest["progress"] = min(quest["goal"], quest.get("progress", 0) + amount)
    if quest["progress"] >= quest["goal"]:
        quest["status"] = "ready"


def grant_item(state: dict, item: str, quantity: int = 1) -> None:
    for _ in range(quantity):
        state["inventory"].append(item)
    if item == "cell key":
        state["has_key"] = True


def grant_all_items(state: dict) -> str:
    granted = []
    for item, data in ITEM_DATA.items():
        quantity = 100
        owned = state["inventory"].count(item)
        needed = max(0, quantity - owned)
        if needed:
            grant_item(state, item, needed)
            granted.append(f"{needed}x {item}")
    state["money"] = max(state.get("money", 0), 500)
    if not state.get("equipped_weapon"):
        state["equipped_weapon"] = "king's blade" if "king's blade" in state["inventory"] else "war axe"
    if not state.get("equipped_armor"):
        state["equipped_armor"] = "ashen crown" if "ashen crown" in state["inventory"] else "royal mail"
    add_loot_log(state, ["Cheat -> " + ", ".join(granted[:6]) + ("..." if len(granted) > 6 else "")])
    return "Cheat enabled: every item was added to your inventory and your purse was topped up."


def claim_tavern_reward(state: dict, quest: dict) -> str:
    rewards = []
    money = quest.get("reward_money", 0)
    xp = quest.get("reward_xp", 0)
    item = quest.get("reward_item")
    if money:
        state["money"] += money
        rewards.append(f"{money} crowns")
    if item:
        grant_item(state, item)
        rewards.append(item)
    if xp:
        rewards.append(f"{xp} XP")
    xp_text = grant_xp(state, xp) if xp else ""
    quest["status"] = "done"
    state["tavern_quests_completed"] = state.get("tavern_quests_completed", 0) + 1
    refresh_king_quest(state)
    add_loot_log(state, [f"{quest['title']} -> {', '.join(rewards)}"])
    return f"The tavern pays out for {quest['title']}: {', '.join(rewards)}. {xp_text}".strip()


def tavern_interaction(state: dict) -> str:
    quest = active_tavern_quest(state)
    if quest and quest.get("status") == "ready":
        return claim_tavern_reward(state, quest)
    if quest and quest.get("status") == "active":
        return f"A patron asks for more work: {quest['title']} ({quest['progress']}/{quest['goal']})."

    quest = next_tavern_quest(state)
    if not quest:
        return "The tavern patrons have nothing new for you right now."
    required_level = quest.get("required_level", 1)
    if state.get("level", 1) < required_level:
        return f"The patron lowers his voice: '{quest['title']}' is dangerous work. Come back when you reach level {required_level}."
    quest["status"] = "active"
    quest["progress"] = 0
    return f"A patron offers you {quest['title']}. {quest['text']} Reward: {quest['reward_money']} crowns, {quest['reward_xp']} XP, {quest['reward_item']}."


def king_interaction(state: dict) -> str:
    if state.get("active_city_id") != "ardri":
        return "This hall belongs to a lesser lord, not the King of Ardri."

    refresh_king_quest(state)
    king_quest = state.setdefault("king_quest", {})
    final_site = final_dungeon_location(state)
    if final_site:
        king_quest.setdefault("target_name", final_site["name"])
        king_quest.setdefault("target_pos", list(final_site["world_pos"]))

    status = king_quest.get("status", "locked")
    if status == "locked":
        if state.get("level", 1) < KING_QUEST_LEVEL:
            return f"The king studies you in silence. 'I need a proven champion, not a hopeful wanderer. Return at level {KING_QUEST_LEVEL}.'"
        return "The king will not trust you yet. Finish the tavern contracts first."
    if status == "available":
        if state.get("level", 1) < KING_QUEST_LEVEL:
            return f"The king folds his arms. 'My final order is for heroes of level {KING_QUEST_LEVEL} or higher.'"
        king_quest["status"] = "active"
        return f"The King of Ardri commands you to find {king_quest['target_name']} and slay the Ashen Tyrant within."
    if status == "active" and not king_quest.get("boss_defeated"):
        return f"The king says: 'Find {king_quest['target_name']} on the world map and end the Ashen Tyrant.'"
    if status == "active" and king_quest.get("boss_defeated"):
        king_quest["status"] = "done"
        state["won"] = True
        state["money"] += 250
        grant_item(state, "king's blade")
        xp_text = grant_xp(state, 120)
        add_loot_log(state, ["King's Reward -> 250 crowns, 1x king's blade, 120 XP"])
        return f"The king honors your victory with 250 crowns and the king's blade. {xp_text}"
    return "The throne room stands quiet."


def quest_panel(state: dict) -> str:
    lines = []
    tavern = active_tavern_quest(state)
    if tavern:
        lines.append(f"Tavern: {tavern['title']}")
        label = {
            "forest_kills": "forest kills",
            "cave_kills": "cave kills",
            "dungeon_chests": "dungeon chests",
        }.get(tavern["target"], tavern["target"])
        lines.append(f"{tavern['progress']}/{tavern['goal']} {label}")
    else:
        next_quest = next_tavern_quest(state)
        if next_quest:
            required_level = next_quest.get("required_level", 1)
            if state.get("level", 1) < required_level:
                lines.append(f"Tavern: {next_quest['title']} at Lv.{required_level}")
            else:
                lines.append(f"Tavern: ready for {next_quest['title']}")
        else:
            lines.append("Tavern: all contracts done")

    king_quest = state.get("king_quest", {})
    king_status = king_quest.get("status", "locked")
    if king_status == "locked":
        if state.get("level", 1) < KING_QUEST_LEVEL:
            lines.append(f"King: unlocks at Lv.{KING_QUEST_LEVEL}")
        else:
            lines.append("King: finish tavern contracts")
    elif king_status == "available":
        lines.append("King: return to Ardri castle")
    elif king_status == "active":
        boss_state = "slain" if king_quest.get("boss_defeated") else king_quest.get("target_name", "active")
        lines.append(f"King: {boss_state}")
    else:
        lines.append("King: realm saved")
    return panel_box("QUESTS", lines, width=98)


def ritual_panel(state: dict) -> str:
    if state.get("area") != "ritual":
        return panel_box("RITUALS", ["Visit the ritual circle", "to summon bosses."], width=98)

    lines = []
    for label, boss_key in (("Armor altar", "armor"), ("Weapon altar", "weapon")):
        data = SUMMON_BOSSES[boss_key]
        if state.get("level", 1) < SUMMON_BOSS_LEVEL:
            ready = f"need Lv.{SUMMON_BOSS_LEVEL}"
        else:
            ready = "ready" if can_pay_requirements(state, data["requirements"]) else "missing loot"
        lines.append(f"{label}: {data['enemy_name']} ({ready})")
        lines.append(requirement_text(data["requirements"]))
        lines.append(f"10% -> {data['rare_drop']}")
    return panel_box("RITUALS", lines, width=98)


def world_location_at(state: dict, x: int, y: int) -> dict | None:
    return state.get("world_locations", {}).get(pos_key(x, y))


def generate_world_grid() -> list[list[str]]:
    grid = [["."] * WORLD_WIDTH for _ in range(WORLD_HEIGHT)]

    for x in range(WORLD_WIDTH):
        grid[0][x] = "#"
        grid[WORLD_HEIGHT - 1][x] = "#"
    for y in range(WORLD_HEIGHT):
        grid[y][0] = "#"
        grid[y][WORLD_WIDTH - 1] = "#"

    grid[WORLD_HEIGHT // 2][2] = "W"

    def place(tile: str, count: int) -> None:
        placed = 0
        while placed < count:
            x = random.randint(1, WORLD_WIDTH - 2)
            y = random.randint(1, WORLD_HEIGHT - 2)
            if grid[y][x] == ".":
                grid[y][x] = tile
                placed += 1

    place("V", 4)
    place("F", 12)
    place("H", 5)
    place("U", 3)
    place("W", 2)

    return grid


def save_path() -> str:
    return os.path.join(os.path.dirname(__file__), SAVE_FILE)


def save_game(state: dict) -> None:
    state_to_save = dict(state)
    active_grid = state.get("current_grid") or state.get("area") or "prison"
    state_to_save["area"] = active_grid
    state_to_save["current_grid"] = active_grid
    with open(save_path(), "w", encoding="utf-8") as save_file:
        json.dump(state_to_save, save_file, indent=2)


def load_game() -> dict:
    state = build_state()
    path = save_path()

    if not os.path.exists(path):
        save_game(state)
        return state

    with open(path, "r", encoding="utf-8") as save_file:
        loaded = json.load(save_file)

    state.update(loaded)
    add_final_dungeon(state["world_tiles"], state["world_locations"])
    add_ritual_site(state["world_tiles"], state["world_locations"])
    state.setdefault(
        "tavern_quests",
        [dict(quest, status="locked", progress=0) for quest in TAVERN_QUESTS],
    )
    state.setdefault("tavern_quests_completed", 0)
    state.setdefault("king_quest", {"status": "locked", "boss_defeated": False})
    refresh_king_quest(state)

    active_area = loaded.get("current_grid") or loaded.get("area") or "prison"
    if active_area == "ville":
        active_area = "city"
    state["area"] = active_area
    state["current_grid"] = active_area

    if active_area == "city":
        state["tiles"] = set_active_city(state, loaded.get("active_city_id", "ardri"))
    elif active_area == "world":
        state["tiles"] = state["world_tiles"]
    elif active_area in {"castle", "armorer", "merchant", "ritual", "summon_arena", "tavern"}:
        state["tiles"] = state[f"{active_area}_tiles"]
    elif active_area in {"village", "forest", "cave", "dungeon", "ritual", "summon_arena"}:
        world_pos = loaded.get("active_world_pos") or state.get("active_world_pos")
        location = world_location_at(state, world_pos[0], world_pos[1]) if world_pos else None
        if active_area == "summon_arena":
            state["tiles"] = state.get("summon_arena_tiles") or clone_grid(SUMMON_ARENA_GRID)
        else:
            state["tiles"] = set_active_site(state, location) if location else state["world_tiles"]
    else:
        world_pos = loaded.get("active_world_pos")
        if active_area == "prison":
            state["tiles"] = state["prison_tiles"]
        elif world_pos:
            location = world_location_at(state, world_pos[0], world_pos[1])
            if location:
                state["tiles"] = set_active_site(state, location)
            else:
                state["tiles"] = state["prison_tiles"]
        else:
            state["tiles"] = state["prison_tiles"]

    max_y = len(state["tiles"]) - 1
    max_x = len(state["tiles"][0]) - 1
    px, py = state.get("player", [1, 1])
    if not (0 <= px <= max_x and 0 <= py <= max_y):
        state["player"] = [1, 1]

    if state["guard_respawn_at"] and time.time() >= state["guard_respawn_at"]:
        respawn_prison_guards(state)
        if state.get("area") == "prison":
            state["tiles"] = state["prison_tiles"]

    return state


def show_start_menu(message: str | None = None) -> None:
    clear_screen()
    print(color(f"{BOLD}PRISON OF ARDRI{RESET}", MAGENTA))
    print(color("You were imprisoned in the city of Ardri and robbed of your freedom.", DIM))
    print(color("Now your story begins beyond the bars, in a city filled with danger, secrets, and places worth exploring.", DIM))
    print()
    if message:
        print(color(message, CYAN))
        print()
    print(color("Press Enter to start", DIM))
    input()


def show_death_screen() -> None:
    clear_screen()
    print(color(f"{BOLD}YOU DIED{RESET}", RED))
    print(color("Darkness closes in...", DIM))
    print()
    for number in (3, 2, 1):
        print(color(str(number), MAGENTA))
        time.sleep(DEATH_COUNTDOWN_DELAY)


def reset_save() -> dict:
    state = build_state()
    save_game(state)
    return state


def build_state() -> dict:
    prison_tiles = clone_grid(PRISON_GRID)
    city_tiles = clone_grid(CITY_GRID)
    castle_tiles = clone_grid(CASTLE_GRID)
    armorer_tiles = clone_grid(ARMORER_GRID)
    merchant_tiles = clone_grid(MERCHANT_GRID)
    ritual_tiles = clone_grid(RITUAL_GRID)
    summon_arena_tiles = clone_grid(SUMMON_ARENA_GRID)
    tavern_tiles = clone_grid(TAVERN_GRID)
    world_tiles, world_locations = generate_world_data()
    state = {
        "tiles": prison_tiles,
        "player": [0, 0],
        "prison_tiles": prison_tiles,
        "city_tiles": city_tiles,
        "castle_tiles": castle_tiles,
        "armorer_tiles": armorer_tiles,
        "merchant_tiles": merchant_tiles,
        "ritual_tiles": ritual_tiles,
        "summon_arena_tiles": summon_arena_tiles,
        "tavern_tiles": tavern_tiles,
        "world_tiles": world_tiles,
        "world_locations": world_locations,
        "prison_door": find_tile(prison_tiles, "D"),
        "city_door": find_tile(city_tiles, "D"),
        "city_world_gate": find_tile(city_tiles, "O"),
        "city_tavern": find_tile(city_tiles, "T"),
        "city_castle": find_tile(city_tiles, "C"),
        "city_armorer": find_tile(city_tiles, "A"),
        "city_merchant": find_tile(city_tiles, "M"),
        "world_ardri": find_tile(world_tiles, "W"),
        "castle_door": find_tile(castle_tiles, "D"),
        "armorer_door": find_tile(armorer_tiles, "D"),
        "merchant_door": find_tile(merchant_tiles, "D"),
        "ritual_door": find_tile(ritual_tiles, "D"),
        "summon_arena_door": (5, 5),
        "tavern_door": find_tile(tavern_tiles, "D"),
        "active_city_id": "ardri",
        "active_city_name": "Ardri",
        "active_world_pos": list(find_tile(world_tiles, "W")),
        "active_site_name": None,
        "active_site_type": None,
        "active_city_entry": find_tile(city_tiles, "O"),
        "active_city_castle": find_tile(city_tiles, "C"),
        "active_city_armorer": find_tile(city_tiles, "A"),
        "active_city_merchant": find_tile(city_tiles, "M"),
        "active_city_tavern": find_tile(city_tiles, "T"),
        "guard_positions": find_all_tiles(prison_tiles, "G"),
        "guard_respawn_at": None,
        "has_key": False,
        "money": 0,
        "inventory": [],
        "equipped_weapon": None,
        "equipped_armor": None,
        "hp": 20,
        "max_hp": 20,
        "level": 1,
        "xp": 0,
        "damage_bonus": 0,
        "running": True,
        "won": False,
        "prison_escaped": False,
        "message": "You wake inside the Prison of Ardri, imprisoned and cut off from the city beyond the walls.",
        "current_grid": "prison",
        "combat": None,
        "encounter": None,
        "show_inventory_panel": False,
        "shop_context": None,
        "last_words": [],
        "show_shop_panel": False,
        "loot_log": [],
        "active_dungeon_level": 1,
        "active_dungeon_room": 0,
        "guards_total": len(find_all_tiles(prison_tiles, "G")),
        "guards_defeated": 0,
        "key_guard_index": random.randint(1, max(1, len(find_all_tiles(prison_tiles, "G")))),
        "pending_enemy_attack": False,
        "combat_origin_tile": None,
        "summoned_boss": None,
        "summoned_boss_key": None,
        "tavern_quests": [dict(quest, status="locked", progress=0) for quest in TAVERN_QUESTS],
        "tavern_quests_completed": 0,
        "king_quest": {"status": "locked", "boss_defeated": False},
    }
    if state["tavern_quests"]:
        state["tavern_quests"][0]["status"] = "locked"
    load_area(state, "prison")
    return state


def respawn_prison_guards(state: dict) -> None:
    for x, y in state["guard_positions"]:
        state["prison_tiles"][y][x] = "G"
    state["guards_defeated"] = 0
    state["guards_total"] = len(state["guard_positions"])
    state["key_guard_index"] = random.randint(1, max(1, state["guards_total"]))
    state["guard_respawn_at"] = None


def set_active_city(state: dict, city_id: str) -> list[list[str]]:
    if city_id == "ardri":
        tiles = state["city_tiles"]
        state["active_city_id"] = "ardri"
        state["active_city_name"] = "Ardri"
        state["active_world_pos"] = list(state["world_ardri"])
    else:
        city_data = next(
            location for location in state["world_locations"].values() if location.get("city_id") == city_id
        )
        tiles = city_data["grid"]
        state["active_city_id"] = city_id
        state["active_city_name"] = city_data["name"]
        state["active_world_pos"] = list(city_data["world_pos"])

    state["active_city_entry"] = find_tile(tiles, "O")
    state["active_city_castle"] = find_tile(tiles, "C")
    state["active_city_armorer"] = find_tile(tiles, "A")
    state["active_city_merchant"] = find_tile(tiles, "M")
    state["active_city_tavern"] = find_tile(tiles, "T")
    return tiles


def set_active_site(state: dict, location: dict) -> list[list[str]]:
    state["active_site_name"] = location["name"]
    state["active_site_type"] = location["tile"]
    if "world_pos" in location:
        state["active_world_pos"] = list(location["world_pos"])
    if location["tile"] == "U":
        rooms = location.setdefault("rooms", [generate_site_grid("U")])
        index = min(location.get("room_index", 0), len(rooms) - 1)
        location["room_index"] = index
        state["active_dungeon_level"] = location.get("level", 1)
        state["active_dungeon_room"] = index
        return rooms[index]
    if "grid" not in location:
        location["grid"] = generate_site_grid(location["tile"])
    return location["grid"]


def load_area(state: dict, area: str, spawn: str = "start") -> None:
    if area == "prison":
        if state["guard_respawn_at"] and time.time() >= state["guard_respawn_at"]:
            respawn_prison_guards(state)
        tiles = state["prison_tiles"]
        start_x, start_y = find_tile(tiles, "@")
        if tiles[start_y][start_x] == "@":
            tiles[start_y][start_x] = "."
        player_x, player_y = state["prison_door"] if spawn == "door" else (start_x, start_y)
    elif area == "city":
        tiles = set_active_city(state, state.get("active_city_id", "ardri"))
        if spawn == "door":
            player_x, player_y = state["city_door"]
        elif spawn == "tavern":
            player_x, player_y = state["active_city_tavern"]
        elif spawn == "world":
            player_x, player_y = state["active_city_entry"]
        else:
            player_x, player_y = (1, 1)
    elif area == "castle":
        tiles = clone_grid(CASTLE_GRID)
        state["castle_tiles"] = tiles
        player_x, player_y = state["castle_door"]
    elif area == "armorer":
        tiles = clone_grid(ARMORER_GRID)
        tiles[1][2] = "w"
        tiles[1][6] = "r"
        state["armorer_tiles"] = tiles
        player_x, player_y = state["armorer_door"]
    elif area == "merchant":
        tiles = clone_grid(MERCHANT_GRID)
        tiles[1][4] = "p"
        state["merchant_tiles"] = tiles
        player_x, player_y = state["merchant_door"]
    elif area == "ritual":
        tiles = clone_grid(RITUAL_GRID)
        state["ritual_tiles"] = tiles
        player_x, player_y = state["ritual_door"]
    elif area == "summon_arena":
        tiles = state.get("summon_arena_tiles") or clone_grid(SUMMON_ARENA_GRID)
        state["summon_arena_tiles"] = tiles
        player_x, player_y = state.get("summon_arena_door", (5, 5))
    else:
        if area == "tavern":
            tiles = clone_grid(TAVERN_GRID)
            state["tavern_tiles"] = tiles
            player_x, player_y = state["tavern_door"] if spawn != "tavern" else (4, 2)
        elif area == "world":
            tiles = state["world_tiles"]
            player_x, player_y = tuple(state.get("active_world_pos", state["world_ardri"]))
        elif area in {"village", "forest", "cave", "dungeon"}:
            location = world_location_at(state, state["active_world_pos"][0], state["active_world_pos"][1])
            tiles = set_active_site(state, location) if location else state["world_tiles"]
            player_x, player_y = find_tile(tiles, "D")
        else:
            location = world_location_at(state, state["active_world_pos"][0], state["active_world_pos"][1])
            tiles = set_active_site(state, location) if location else state["world_tiles"]
            player_x, player_y = find_tile(tiles, "D")

    state["area"] = area
    state["current_grid"] = area
    state["tiles"] = tiles
    state["player"] = [player_x, player_y]
    state["combat"] = None
    state["encounter"] = None
    state["pending_enemy_attack"] = False


def respawn_player(state: dict) -> None:
    state["hp"] = state["max_hp"]
    state["combat"] = None
    state["encounter"] = None
    state["pending_enemy_attack"] = False
    state["show_inventory_panel"] = False

    if state.get("prison_escaped"):
        state["active_city_id"] = "ardri"
        set_active_city(state, "ardri")
        load_area(state, "tavern", spawn="tavern")
        state["message"] = "You wake up inside Ardri's tavern, battered but alive."
    else:
        load_area(state, "prison")
        state["message"] = "You wake back up inside your prison cell."
    state["show_shop_panel"] = False


def return_to_city_entry(state: dict) -> None:
    if state["area"] == "castle":
        load_area(state, "city")
        state["player"] = list(state["active_city_castle"])
    elif state["area"] == "armorer":
        load_area(state, "city")
        state["player"] = list(state["active_city_armorer"])
    elif state["area"] == "merchant":
        load_area(state, "city")
        state["player"] = list(state["active_city_merchant"])
    elif state["area"] == "tavern":
        load_area(state, "city")
        state["player"] = list(state["active_city_tavern"])
    elif state["area"] == "summon_arena":
        load_area(state, "ritual")


def draw_cell(tile: str, has_player: bool) -> list[str]:
    if has_player:
        return [
            color("+---+", CYAN),
            color("| @ |", CYAN),
            color("+---+", CYAN),
        ]
    if tile == "#":
        return [
            color("+---+", RED),
            color("|###|", RED),
            color("+---+", RED),
        ]
    if tile == ".":
        return [
            "+---+",
            color("|   |", DIM),
            "+---+",
        ]
    if tile == "B":
        return [
            color("+---+", YELLOW),
            color("| B |", YELLOW),
            color("+---+", YELLOW),
        ]
    if tile == "G":
        return [
            color("+---+", MAGENTA),
            color("| G |", WHITE),
            color("+---+", MAGENTA),
        ]
    if tile == "I":
        return [
            color("+---+", CYAN),
            color("| I |", CYAN),
            color("+---+", CYAN),
        ]
    if tile == "D":
        return [
            color("+---+", CYAN),
            color("| D |", CYAN),
            color("+---+", CYAN),
        ]
    if tile == "C":
        return [
            color("+---+", YELLOW),
            color("| C |", YELLOW),
            color("+---+", YELLOW),
        ]
    if tile == "A":
        return [
            color("+---+", CYAN),
            color("| A |", CYAN),
            color("+---+", CYAN),
        ]
    if tile == "M":
        return [
            color("+---+", GREEN),
            color("| M |", GREEN),
            color("+---+", GREEN),
        ]
    if tile == "T":
        return [
            color("+---+", YELLOW),
            color("| T |", YELLOW),
            color("+---+", YELLOW),
        ]
    if tile == "O":
        return [
            color("+---+", CYAN),
            color("| O |", CYAN),
            color("+---+", CYAN),
        ]
    if tile == "H":
        return [
            color("+---+", BLUE),
            color("| H |", BLUE),
            color("+---+", BLUE),
        ]
    if tile == "W":
        return [
            color("+---+", YELLOW),
            color("| W |", YELLOW),
            color("+---+", YELLOW),
        ]
    if tile == "V":
        return [
            color("+---+", GREEN),
            color("| V |", GREEN),
            color("+---+", GREEN),
        ]
    if tile == "F":
        return [
            color("+---+", GREEN),
            color("| F |", GREEN),
            color("+---+", GREEN),
        ]
    if tile == "U":
        return [
            color("+---+", RED),
            color("| U |", RED),
            color("+---+", RED),
        ]
    if tile == "X":
        return [
            color("+---+", RED),
            color("| X |", WHITE),
            color("+---+", RED),
        ]
    if tile == "L":
        return [
            color("+---+", YELLOW),
            color("| L |", YELLOW),
            color("+---+", YELLOW),
        ]
    if tile in {"w", "r", "p"}:
        tint = {"w": WHITE, "r": BLUE, "p": MAGENTA}[tile]
        return [
            color("+---+", tint),
            color(f"| {tile.upper()} |", tint),
            color("+---+", tint),
        ]
    if tile == "S":
        return [
            color("+---+", GREEN),
            color("| S |", GREEN),
            color("+---+", GREEN),
        ]
    if tile in {"K", "Q"}:
        tint = YELLOW if tile == "K" else MAGENTA
        return [
            color("+---+", tint),
            color(f"| {tile} |", tint),
            color("+---+", tint),
        ]
    if tile == "R":
        return [
            color("+---+", MAGENTA),
            color("| R |", MAGENTA),
            color("+---+", MAGENTA),
        ]
    if tile in {"Y", "Z"}:
        tint = BLUE if tile == "Y" else RED
        return [
            color("+---+", tint),
            color(f"| {tile} |", tint),
            color("+---+", tint),
        ]
    return ["+---+", "| ? |", "+---+"]


def render_grid(state: dict) -> str:
    rows: list[str] = []
    player_x, player_y = state["player"]

    for y, row in enumerate(state["tiles"]):
        line_a: list[str] = []
        line_b: list[str] = []
        line_c: list[str] = []
        for x, tile in enumerate(row):
            a, b, c = draw_cell(tile, x == player_x and y == player_y)
            line_a.append(a)
            line_b.append(b)
            line_c.append(c)
        rows.extend(["".join(line_a), "".join(line_b), "".join(line_c)])
    return "\n".join(rows)


def merge_columns(left: str, right: str, gap: int = 4) -> str:
    left_lines = left.splitlines()
    right_lines = right.splitlines()
    height = max(len(left_lines), len(right_lines))
    left_width = max((visible_len(line) for line in left_lines), default=0)
    merged: list[str] = []

    for index in range(height):
        left_line = left_lines[index] if index < len(left_lines) else ""
        right_line = right_lines[index] if index < len(right_lines) else ""
        padding = max(0, left_width - visible_len(left_line))
        merged.append(left_line + (" " * padding) + (" " * gap) + right_line)

    return "\n".join(merged)


def visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def hp_bar(current: int, maximum: int, width: int = BAR_WIDTH) -> str:
    if maximum <= 0:
        return "-" * width
    filled = round((current / maximum) * width)
    filled = max(0, min(width, filled))
    return ("#" * filled) + ("-" * (width - filled))


def panel_box(title: str, lines: list[str], width: int = 28) -> str:
    inner = width - 2
    top = "+" + "-" * inner + "+"
    title_line = "|" + title.center(inner) + "|"
    body = []
    for line in lines:
        trimmed = line[:inner]
        body.append("|" + trimmed.ljust(inner) + "|")
    bottom = "+" + "-" * inner + "+"
    return "\n".join([top, title_line, *body, bottom])


def item_details(item: str) -> str:
    data = ITEM_DATA.get(item, {})
    details = []
    if data.get("kind") == "weapon":
        details.append(f"dmg {data['damage'][0]}-{data['damage'][1]}")
    elif data.get("kind") == "armor":
        details.append(f"def {data['armor']}")
    elif data.get("kind") == "potion":
        details.append(f"heal {data['heal']}")
    if data.get("buy", 0):
        details.append(f"buy {data['buy']}")
    if data.get("sell", 0):
        details.append(f"sell {data['sell']}")
    return ", ".join(details)


def resolve_shop_item(fragment_words: list[str], allowed_kind: str | None = None) -> str | None:
    fragment = " ".join(fragment_words).strip().lower()
    if not fragment:
        return None
    candidates = []
    for item, data in ITEM_DATA.items():
        if allowed_kind and data.get("kind") != allowed_kind:
            continue
        if data.get("buy", 0) <= 0 and allowed_kind:
            continue
        if item.startswith(fragment):
            candidates.append(item)
    if len(candidates) == 1:
        return candidates[0]
    exact = [item for item in candidates if item == fragment]
    if len(exact) == 1:
        return exact[0]
    return None


def current_tile(state: dict) -> str:
    x, y = state["player"]
    return state["tiles"][y][x]


def nearby_text(state: dict) -> str:
    x, y = state["player"]
    here = current_tile(state)
    lines = []

    if here == ".":
        lines.append("You are standing on an empty tile.")
    elif here == "D":
        if state["area"] == "prison":
            lines.append("The prison gate is right here. Use 'e' to interact.")
        elif state["area"] == "city":
            lines.append("The gate back to the Prison of Ardri is here. Use 'e' to interact.")
        else:
            lines.append("The exit is here. Use 'e' to go back outside.")
    elif here == "G":
        lines.append("A guard stands before you. Type 'fight' or step away.")
    elif here == "B":
        lines.append("A rusty bunk bed creaks under your weight.")
    elif here == "I":
        lines.append("A crude stash is hidden in the wall. Use 'e' to search it.")
    elif here == "C":
        lines.append("The great castle of Ardri towers above you.")
    elif here == "A":
        lines.append("An armorer's shop stands open for business.")
    elif here == "M":
        lines.append("A merchant watches the street from a busy stall.")
    elif here == "T":
        lines.append("A noisy tavern glows with warm light.")
    elif here == "S":
        lines.append("You stand in Ardri's central square.")
    elif here == "O":
        city_name = state.get("active_city_name", "Ardri") if state.get("area") == "city" else "the city"
        lines.append(f"A road leads out of {city_name}. Use 'e' to enter the world map.")
    elif here == "W":
        location = world_location_at(state, x, y)
        city_name = location["name"] if location else "a city"
        lines.append(f"{city_name} lies here. Use 'e' to enter.")
    elif here == "V":
        location = world_location_at(state, x, y)
        lines.append(f"Village: {location['name']}." if location else "A village rests here among the roads.")
    elif here == "F":
        location = world_location_at(state, x, y)
        lines.append(f"Forest: {location['name']}." if location else "Dense forest spreads across this region.")
    elif here == "H":
        location = world_location_at(state, x, y)
        lines.append(f"Cave: {location['name']}." if location else "A cave mouth opens into the earth here.")
    elif here == "U":
        location = world_location_at(state, x, y)
        if location:
            lines.append(f"Dungeon: {location['name']}.")
            lines.append(f"Level: {location.get('level', 1)} | Length: {len(location.get('rooms', []))} rooms.")
        else:
            lines.append("A dungeon entrance waits here in silence.")
    elif here == "X":
        lines.append("A monster lurks here. Type 'fight' or move away.")
    elif here == "w":
        lines.append("Weapon counter. Use 'e' to browse weapons.")
    elif here == "r":
        lines.append("Armor counter. Use 'e' to browse armor.")
    elif here == "p":
        lines.append("Potion counter. Use 'e' to browse potions.")
    elif here == "K":
        lines.append("The King of Ardri awaits. Use 'e' to speak.")
    elif here == "Q":
        lines.append("A quest patron is looking for help. Use 'e' to talk.")
    elif here == "R":
        lines.append("A ritual circle hums here. Use 'e' to enter.")
    elif here == "Y":
        lines.append("Armor altar. Offer monster loot and use 'e' to summon a boss.")
    elif here == "Z":
        lines.append("Weapon altar. Offer monster loot and use 'e' to summon a boss.")

    around = {
        "up": (x, y - 1),
        "down": (x, y + 1),
        "left": (x - 1, y),
        "right": (x + 1, y),
    }

    for direction, (nx, ny) in around.items():
        tile = state["tiles"][ny][nx]
        name, _ = TILE_INFO.get(tile, ("Unknown", DIM))
        if tile == "#":
            lines.append(f"{direction.capitalize()}: a wall blocks the way.")
        elif tile == ".":
            lines.append(f"{direction.capitalize()}: an open tile.")
        else:
            lines.append(f"{direction.capitalize()}: {name}.")

    return "\n".join(lines)


def show_help() -> str:
    base = "Commands: zqsd, up/down/left/right, look, inv, m, stats, use <potion> <qty>, buy <item>, sell <item>, equip <item>, unequip <weapon|armor|all>, cheat, reset, help, quit."
    combat = " On a guard tile, use fight to start combat. In combat, use a to attack and f to flee."
    travel = " Stand on a D gate tile and use e to interact. Ritual altars also use e."
    return base + combat + travel


def xp_to_next_level(level: int) -> int:
    return 10 + (level - 1) * 5


def grant_xp(state: dict, amount: int) -> str:
    state["xp"] += amount
    messages = [f"You gain {amount} XP."]
    level_ups = []

    while state["xp"] >= xp_to_next_level(state["level"]):
        cost = xp_to_next_level(state["level"])
        state["xp"] -= cost
        state["level"] += 1
        state["max_hp"] += 10
        state["hp"] = state["max_hp"]
        state["damage_bonus"] += 1
        text = f"LEVEL UP -> {state['level']} | Max HP +10 | Damage +1"
        messages.append(text)
        level_ups.append(text)

    if level_ups:
        state.setdefault("loot_log", []).extend(level_ups)

    return " ".join(messages)


def show_inventory(state: dict) -> str:
    return "You check your inventory."


def show_money(state: dict) -> str:
    return f"Money: {state['money']} crowns."


def weapon_range(state: dict) -> tuple[int, int]:
    weapon = state["equipped_weapon"]
    if weapon in ITEM_DATA and ITEM_DATA[weapon]["kind"] == "weapon":
        low, high = ITEM_DATA[weapon]["damage"]
    else:
        low, high = (1, 4)
    return low + state["damage_bonus"], high + state["damage_bonus"]


def armor_value(state: dict) -> int:
    armor = state.get("equipped_armor")
    if armor in ITEM_DATA and ITEM_DATA[armor]["kind"] == "armor":
        return ITEM_DATA[armor]["armor"]
    return 0


def consume_potion(state: dict, item_name: str, quantity: int = 1) -> str:
    if item_name not in ITEM_DATA or ITEM_DATA[item_name]["kind"] != "potion":
        return f"{item_name} is not a potion."
    if quantity <= 0:
        return "Quantity must be at least 1."
    owned = state["inventory"].count(item_name)
    if owned < quantity:
        return f"You only have {owned}x {item_name}."

    healed = 0
    for _ in range(quantity):
        state["inventory"].remove(item_name)
        healed += ITEM_DATA[item_name]["heal"]
    state["hp"] = min(state["max_hp"], state["hp"] + healed)
    return f"You use {quantity}x {item_name} and recover {healed} HP."


def quick_potion_use(state: dict) -> str:
    for potion in ("small potion", "large potion", "greater potion", "sun tonic"):
        if potion in state["inventory"]:
            return consume_potion(state, potion, 1)
    return "You have no potion to use."


def shop_lines(kind: str) -> list[str]:
    heading = {"weapon": "Weapons", "armor": "Armor", "potion": "Potions"}[kind]
    items = [
        (name, data)
        for name, data in ITEM_DATA.items()
        if data.get("kind") == kind and data.get("buy", 0) > 0
    ]
    lines = [heading]
    for index, (name, data) in enumerate(items, start=1):
        lines.append(f"{index}. {name}")
        lines.append(f"   {item_details(name)}")
    lines.extend(["", "buy <item>", "sell <item>"])
    return lines


def buy_item(state: dict, words: list[str]) -> str:
    if len(words) < 2:
        return "Specify what you want to buy."
    allowed_kind = state.get("shop_context")
    item = resolve_shop_item(words[1:], allowed_kind)
    if not item:
        return "That item name is ambiguous or unavailable here."
    data = ITEM_DATA.get(item)
    if not data or data.get("buy", 0) <= 0:
        return f"{item} is not for sale."
    allowed = {
        "weapon": state.get("shop_context") == "weapon",
        "armor": state.get("shop_context") == "armor",
        "potion": state.get("shop_context") == "potion",
    }
    if not allowed.get(data["kind"], False):
        return "You need to stand on the right counter to buy that item."
    if state["money"] < data["buy"]:
        return "You do not have enough crowns."
    state["money"] -= data["buy"]
    state["inventory"].append(item)
    return f"You buy 1x {item} for {data['buy']} crowns."


def sell_item(state: dict, words: list[str]) -> str:
    if len(words) < 2:
        return "Specify what you want to sell."
    item = " ".join(words[1:])
    if item not in state["inventory"]:
        return f"You do not have '{item}'."
    value = ITEM_DATA.get(item, {}).get("sell", 0)
    if value <= 0:
        return f"{item} cannot be sold."
    state["inventory"].remove(item)
    if state.get("equipped_weapon") == item:
        state["equipped_weapon"] = None
    if state.get("equipped_armor") == item:
        state["equipped_armor"] = None
    state["money"] += value
    return f"You sell 1x {item} for {value} crowns."


def show_stats(state: dict) -> str:
    weapon = state["equipped_weapon"] or "none"
    armor = state.get("equipped_armor") or "none"
    low, high = weapon_range(state)
    damage = f"{low}-{high}"
    return (
        f"Stats - HP: {state['hp']}/{state['max_hp']}, Level: {state['level']}, "
        f"XP: {state['xp']}/{xp_to_next_level(state['level'])}, Weapon: {weapon}, Armor: {armor}, Damage: {damage}, Defense: {armor_value(state)}."
    )


def add_loot_log(state: dict, entries: list[str]) -> None:
    if not entries:
        return
    state.setdefault("loot_log", []).extend(entries)


def inventory_panel(state: dict) -> str:
    lines: list[str] = []
    if not state["inventory"]:
        lines.append("empty")
    else:
        counts = Counter(state["inventory"])
        for item, qty in sorted(counts.items()):
            marker = ""
            if state["equipped_weapon"] == item or state.get("equipped_armor") == item:
                marker = " *"
            data = ITEM_DATA.get(item, {})
            details = []
            if data.get("kind") == "weapon":
                details.append(f"dmg {data['damage'][0]}-{data['damage'][1]}")
            elif data.get("kind") == "armor":
                details.append(f"def {data['armor']}")
            elif data.get("kind") == "potion":
                details.append(f"heal {data['heal']}")
            if data.get("sell", 0):
                details.append(f"sell {data['sell']}")
            suffix = f" ({', '.join(details)})" if details else ""
            lines.append(f"{qty}x {item}{marker}{suffix}")

    lines.append("")
    lines.append("equip <item>")
    lines.append("unequip <weapon|armor|all>")
    lines.append("use <potion> <qty>")
    return panel_box("INVENTORY", lines, width=48)


def shop_panel(state: dict) -> str:
    if not state.get("show_shop_panel"):
        return panel_box("SHOP", ["closed"], width=56)
    lines: list[str] = []
    if state["area"] == "merchant":
        lines.extend(shop_lines("potion"))
        return panel_box("SHOP", lines, width=56)
    if state["area"] == "armorer":
        lines.extend(shop_lines("weapon"))
        lines.append("")
        lines.extend(shop_lines("armor"))
        return panel_box("SHOP", lines, width=56)
    lines.append("No shop open.")
    return panel_box("SHOP", lines, width=56)


def side_panel(state: dict) -> str:
    lower = merge_columns(inventory_panel(state), shop_panel(state), gap=2)
    loot_lines = state.get("loot_log", [])[-5:] or ["No recent loot."]
    loot_box = panel_box("LOOT", loot_lines, width=98)
    return combat_panel(state) + "\n\n" + quest_panel(state) + "\n\n" + ritual_panel(state) + "\n\n" + loot_box + "\n\n" + lower


def equip_item(words: list[str], state: dict) -> str:
    if len(words) < 2:
        return "Specify what to equip."
    item = " ".join(words[1:])
    if item not in state["inventory"]:
        return f"You do not have '{item}' in your inventory."
    if item not in ITEM_DATA:
        return f"You cannot equip '{item}'."
    kind = ITEM_DATA[item]["kind"]
    if kind == "weapon":
        state["equipped_weapon"] = item
        return f"You equip {item}."
    if kind == "armor":
        state["equipped_armor"] = item
        return f"You equip {item}."
    return f"You cannot equip '{item}'."


def unequip_item(words: list[str], state: dict) -> str:
    if len(words) < 2:
        return "Specify what to unequip: weapon, armor, or all."
    target = " ".join(words[1:])

    if target == "weapon":
        if not state.get("equipped_weapon"):
            return "You do not have a weapon equipped."
        item = state["equipped_weapon"]
        state["equipped_weapon"] = None
        return f"You unequip {item}."

    if target == "armor":
        if not state.get("equipped_armor"):
            return "You do not have armor equipped."
        item = state["equipped_armor"]
        state["equipped_armor"] = None
        return f"You unequip {item}."

    if target == "all":
        removed = []
        if state.get("equipped_weapon"):
            removed.append(state["equipped_weapon"])
            state["equipped_weapon"] = None
        if state.get("equipped_armor"):
            removed.append(state["equipped_armor"])
            state["equipped_armor"] = None
        if not removed:
            return "You have nothing equipped."
        return "You unequip " + " and ".join(removed) + "."

    return "Use: unequip weapon, unequip armor, or unequip all."


def current_enemy_template(state: dict | None = None) -> dict:
    if state and state.get("area") == "dungeon":
        location = active_location(state)
        if location and location.get("final_dungeon"):
            last_room = location.get("room_index", 0) >= len(location.get("rooms", [])) - 1
            remaining = sum(ch == "X" for row in state.get("tiles", []) for ch in row)
            if last_room and remaining <= 1 and not state.get("king_quest", {}).get("boss_defeated"):
                monster = dict(FINAL_BOSS)
                monster["has_key"] = False
                monster["loot_items"] = list(monster.get("drops", []))
                monster["boss"] = True
                return monster
        monster = dict(random.choice(DUNGEON_MONSTERS))
        level = max(1, state.get("active_dungeon_level", 1))
        monster["enemy_name"] = f"{monster['enemy_name']} Lv.{level}"
        monster["enemy_hp"] += level * 4
        monster["enemy_max_hp"] = monster["enemy_hp"]
        monster["enemy_attack"] += level * 2
        monster["xp"] += level * 3
        monster["money"] += level * 6
        monster["has_key"] = False
        monster["loot_items"] = []
        for item in monster.get("drops", []):
            if random.random() <= 0.35:
                monster["loot_items"].append(item)
        return monster

    if state and state.get("area") == "forest":
        monster = dict(random.choice(FOREST_MONSTERS))
        monster["has_key"] = False
        monster["loot_items"] = [item for item in monster.get("drops", []) if random.random() <= 0.25]
        return monster

    if state and state.get("area") == "cave":
        monster = dict(random.choice(CAVE_MONSTERS))
        monster["has_key"] = False
        monster["loot_items"] = [item for item in monster.get("drops", []) if random.random() <= 0.3]
        return monster

    if state and state.get("area") == "ritual":
        return dict(state.get("encounter") or {})

    if state and state.get("area") == "summon_arena":
        if state.get("summoned_boss"):
            return dict(state["summoned_boss"])
        return {
            "enemy_name": "Summoned Horror",
            "enemy_hp": 1,
            "enemy_max_hp": 1,
            "enemy_attack": 1,
            "has_key": False,
            "xp": 0,
            "money": 0,
            "loot_items": [],
        }

    return {
        "enemy_name": "Patrol Guard",
        "enemy_hp": 12,
        "enemy_max_hp": 12,
        "enemy_attack": 4,
        "has_key": False,
        "xp": 4,
        "money": 0,
        "loot_items": [],
    }


def begin_combat(state: dict) -> None:
    if not state["encounter"]:
        state["encounter"] = current_enemy_template()
    state["combat"] = dict(state["encounter"])
    state["combat_origin_tile"] = current_tile(state)
    state["show_inventory_panel"] = False
    state["message"] = f"Combat starts against {state['combat']['enemy_name']}!"


def flee_combat(state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    if random.random() < 0.5:
        state["combat"] = None
        state["pending_enemy_attack"] = False
        state["encounter"] = dict(combat)
        state["message"] = "You manage to flee from combat."
        return

    state["message"] = "Your escape fails."
    enemy_attack(state)


def end_combat(state: dict, victory: bool) -> None:
    x, y = state["player"]
    if victory:
        origin_tile = state.get("combat_origin_tile", ".")
        state["tiles"][y][x] = origin_tile if origin_tile in {"Y", "Z"} else "."
        loot = []
        xp_gain = state["combat"].get("xp", 4)
        money_gain = state["combat"].get("money", 0)

        if state["area"] == "prison":
            state["guards_defeated"] += 1
            state["guard_respawn_at"] = time.time() + GUARD_RESPAWN_DELAY

        if state["combat"]["has_key"] and not state["has_key"]:
            state["has_key"] = True
            state["inventory"].append("cell key")
            loot.insert(0, "1x cell key")
        if state["area"] == "forest":
            track_progress(state, "forest_kills")
        elif state["area"] == "cave":
            track_progress(state, "cave_kills")
        for item in state["combat"].get("loot_items", []):
            state["inventory"].append(item)
            loot.append(f"1x {item}")
        if state["combat"].get("boss"):
            if state["combat"].get("summoned_boss"):
                state["summoned_boss"] = None
                state["summoned_boss_key"] = None
                door_x, door_y = state.get("summon_arena_door", (5, 5))
                state["tiles"][door_y][door_x] = "D"
                loot.append("arena unlocked")
            else:
                state.setdefault("king_quest", {})["boss_defeated"] = True
                loot.append("realm saved")
        if money_gain:
            state["money"] += money_gain
            loot.append(f"{money_gain}x crowns")
        loot.append(f"{xp_gain}x exp")
        xp_text = grant_xp(state, xp_gain)
        add_loot_log(state, [f"{state['combat']['enemy_name']} -> {', '.join(loot)}"])
        state["message"] = f"{state['combat']['enemy_name']} is defeated. Loot: " + ", ".join(loot) + ". " + xp_text
    state["combat"] = None
    state["encounter"] = None
    state["combat_origin_tile"] = None


def combat_status(state: dict) -> str:
    combat = state["combat"]
    if not combat:
        return ""
    return (
        f"Combat in progress against {combat['enemy_name']} - "
        f"Player HP: {state['hp']}/{state['max_hp']} - Enemy HP: {combat['enemy_hp']}/{combat['enemy_max_hp']}"
    )


def interact_current_tile(state: dict) -> str:
    tile = current_tile(state)

    if tile != "D":
        if tile == "I":
            state["tiles"][state["player"][1]][state["player"][0]] = "."
            state["inventory"].append("shiv")
            return "You pick up the shiv and add it to your inventory."
        if tile == "C":
            load_area(state, "castle")
            return "You enter the Castle of Ardri."
        if tile == "K":
            return king_interaction(state)
        if tile == "A":
            load_area(state, "armorer")
            return "You step into the armorer's shop."
        if tile == "M":
            load_area(state, "merchant")
            return "You step into the merchant's stall."
        if tile == "T":
            load_area(state, "tavern", spawn="tavern")
            return "You enter the tavern."
        if tile == "Q":
            return tavern_interaction(state)
        if tile == "Y":
            return summon_boss(state, "armor")
        if tile == "Z":
            return summon_boss(state, "weapon")
        if tile == "X" and state["area"] == "summon_arena":
            state["encounter"] = current_enemy_template(state)
            state["message"] = f"{state['encounter']['enemy_name']} waits in the arena. Type 'fight' to engage."
            return state["message"]
        if tile == "S":
            return "You take in the city square. Ardri feels alive around you."
        if tile == "O":
            load_area(state, "world")
            return "You leave Ardri behind and step into the wider world."
        if tile == "W":
            location = world_location_at(state, state["player"][0], state["player"][1])
            city_id = location.get("city_id", "ardri") if location else "ardri"
            city_name = location.get("name", "Ardri") if location else "Ardri"
            state["active_world_pos"] = [state["player"][0], state["player"][1]]
            state["active_city_id"] = city_id
            load_area(state, "city", spawn="world")
            return f"You arrive at the gates of {city_name}."
        if tile == "R":
            location = world_location_at(state, state["player"][0], state["player"][1])
            location_name = location["name"] if location else "the ritual circle"
            state["active_world_pos"] = [state["player"][0], state["player"][1]]
            load_area(state, "ritual")
            return f"You step into {location_name}, where old magic waits for offerings."
        if tile == "V":
            location = world_location_at(state, state["player"][0], state["player"][1])
            location_name = location["name"] if location else "a quiet village"
            state["active_world_pos"] = [state["player"][0], state["player"][1]]
            load_area(state, "village")
            return f"You arrive at {location_name}. Smoke rises from quiet cottages."
        if tile == "F":
            location = world_location_at(state, state["player"][0], state["player"][1])
            location_name = location["name"] if location else "the forest"
            state["active_world_pos"] = [state["player"][0], state["player"][1]]
            load_area(state, "forest")
            return f"You push into {location_name}. The trees close in around you."
        if tile == "H":
            location = world_location_at(state, state["player"][0], state["player"][1])
            location_name = location["name"] if location else "the cave mouth"
            state["active_world_pos"] = [state["player"][0], state["player"][1]]
            load_area(state, "cave")
            return f"You stand at {location_name}. Cold air drifts from within."
        if tile == "U":
            location = world_location_at(state, state["player"][0], state["player"][1])
            location_name = location["name"] if location else "the dungeon gate"
            state["active_world_pos"] = [state["player"][0], state["player"][1]]
            load_area(state, "dungeon")
            return f"You stand before {location_name}. Something ancient waits below."
        if tile == "L":
            remaining = sum(ch == "X" for row in state["tiles"] for ch in row)
            if remaining > 0:
                return "The chest is sealed. Defeat every monster in the dungeon first."
            rewards = []
            level = max(1, state.get("active_dungeon_level", 1))
            crowns = 35 + level * 20 + len(state.get("tiles", []))
            location = active_location(state)
            if location and location.get("final_dungeon"):
                crowns += 120
            state["money"] += crowns
            rewards.append(f"{crowns}x crowns")
            rare_pool = ["large potion", "greater potion", "silver blade", "warden plate", "ashen crown"]
            rare = random.choice(rare_pool)
            state["inventory"].append(rare)
            rewards.append(f"1x {rare}")
            state["tiles"][state["player"][1]][state["player"][0]] = "."
            track_progress(state, "dungeon_chests")
            add_loot_log(state, [f"Dungeon Chest -> {', '.join(rewards)}"])
            return "Dungeon chest opened: " + ", ".join(rewards) + "."
        if tile == "w":
            state["shop_context"] = "weapon"
            state["show_inventory_panel"] = True
            state["show_shop_panel"] = True
            return "Weapon counter open."
        if tile == "r":
            state["shop_context"] = "armor"
            state["show_inventory_panel"] = True
            state["show_shop_panel"] = True
            return "Armor counter open."
        if tile == "p":
            state["shop_context"] = "potion"
            state["show_inventory_panel"] = True
            state["show_shop_panel"] = True
            return "Potion counter open."
        if tile == "X":
            state["encounter"] = current_enemy_template(state)
            state["message"] = f"A {state['encounter']['enemy_name']} blocks your path. Type 'fight' to engage."
            return state["message"]
        return "There is nothing to interact with here."

    if state["area"] == "prison":
        if state["has_key"]:
            state["prison_escaped"] = True
            load_area(state, "city", spawn="door")
            state["won"] = True
            return "You step through the prison gate and emerge into the city."
        return "The gate is locked. You need the key first."

    if state["area"] == "city":
        if current_tile(state) == "D":
            load_area(state, "prison", spawn="door")
            return "You pass through the gate and return to the Prison of Ardri."
        if current_tile(state) == "O":
            load_area(state, "world")
            return f"You leave {state.get('active_city_name', 'the city')} and step onto the world map."
        return "There is nothing to interact with here."

    if state["area"] == "summon_arena":
        if current_tile(state) == "D":
            load_area(state, "ritual")
            return "You leave the summon arena and return to the ritual circle."
        return "Defeat the summoned boss before trying to leave this arena."

    if state["area"] in {"village", "forest", "cave", "dungeon", "ritual", "summon_arena"}:
        if state["area"] == "dungeon":
            location = world_location_at(state, state["active_world_pos"][0], state["active_world_pos"][1])
            if location and location.get("room_index", 0) < len(location.get("rooms", [])) - 1:
                remaining = sum(ch == "X" for row in state["tiles"] for ch in row)
                if remaining > 0:
                    return "The path forward is sealed. Defeat every monster in this room first."
                location["room_index"] += 1
                load_area(state, "dungeon")
                return f"You descend deeper into {location['name']} (room {location['room_index'] + 1}/{len(location['rooms'])})."
        load_area(state, "world")
        return "You return to the world map."

    return_to_city_entry(state)
    return "You step back out into Ardri."


def combat_panel(state: dict) -> str:
    lines = [color("COMBAT", BOLD)]
    combat = state["combat"]

    if combat:
        enemy_bar = hp_bar(combat["enemy_hp"], combat["enemy_max_hp"])
        player_bar = hp_bar(state["hp"], state["max_hp"])
        lines.extend(
            [
                f"Enemy: {combat['enemy_name']}",
                f"Enemy HP: [{enemy_bar}]",
                f"          {combat['enemy_hp']}/{combat['enemy_max_hp']}",
                f"Player HP: [{player_bar}]",
                f"          {state['hp']}/{state['max_hp']}",
                "",
            "Actions:",
            "- a",
            "- f",
            "- p",
            "",
            "a = attack, then",
            "the guard retaliates.",
            "f = 50% chance",
            "to flee.",
            "p = use potion",
        ]
    )
        return "\n".join(lines)

    encounter = state["encounter"]
    if encounter:
        enemy_bar = hp_bar(encounter["enemy_hp"], encounter["enemy_max_hp"])
        lines.extend(
            [
                f"Opponent: {encounter['enemy_name']}",
                f"HP: [{enemy_bar}]",
                f"     {encounter['enemy_hp']}/{encounter['enemy_max_hp']}",
                f"Damage: {encounter['enemy_attack']}",
                "",
                "Actions:",
                "- fight or f",
                "- move away",
                "",
                "You can avoid the",
                "fight by leaving.",
            ]
        )
        return "\n".join(lines)

    if not combat:
        lines.append("No combat in progress.")
        lines.append("")
        lines.append("Step onto a G")
        lines.append("guard tile to")
        lines.append("trigger a duel.")
        return "\n".join(lines)

    return "\n".join(lines)


def enemy_attack(state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    damage = max(1, combat["enemy_attack"] - armor_value(state))

    state["hp"] -= damage

    if state["hp"] <= 0:
        state["hp"] = 0
        show_death_screen()
        respawn_player(state)
        return

    state["message"] += f" The guard retaliates and deals {damage} damage."


def player_auto_attack(state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    low, high = weapon_range(state)
    damage = random.randint(low, high)
    combat["enemy_hp"] -= damage
    state["message"] = f"You strike {combat['enemy_name']} and deal {damage} damage."

    if combat["enemy_hp"] <= 0:
        end_combat(state, True)
        return

    state["pending_enemy_attack"] = True


def handle_combat(command: str, state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    if command == "attack":
        player_auto_attack(state)
        return

    if command == "flee":
        flee_combat(state)
        return

    if command == "potion":
        state["message"] = quick_potion_use(state)
        if state["combat"]:
            state["pending_enemy_attack"] = True
        return

    if command == "use":
        item = " ".join(state.get("last_words", [])[1:-1]) if len(state.get("last_words", [])) > 2 and state.get("last_words", [])[-1].isdigit() else " ".join(state.get("last_words", [])[1:])
        qty = int(state["last_words"][-1]) if len(state.get("last_words", [])) > 2 and state["last_words"][-1].isdigit() else 1
        state["message"] = consume_potion(state, item, qty)
        if state["combat"]:
            state["pending_enemy_attack"] = True
        return

    if command == "help":
        state["message"] = "In combat: a, f, p, help, quit."
        return

    if command == "look":
        state["message"] = combat_status(state)
        return

    state["message"] = "In combat, use: a, f, or p."


def interact_tile(state: dict) -> None:
    x, y = state["player"]
    tile = state["tiles"][y][x]

    state["encounter"] = None
    state["shop_context"] = None
    state["show_shop_panel"] = False

    if tile == "I":
        state["message"] = "You found a hidden stash. Press 'e' to take the shiv."
        return

    if tile == "G":
        state["encounter"] = current_enemy_template()
        next_guard_number = state["guards_defeated"] + 1
        state["encounter"]["has_key"] = next_guard_number == state["key_guard_index"]
        state["message"] = "You face a patrol guard. Type 'fight' to begin combat."
        return

    if tile == "X":
        state["encounter"] = current_enemy_template(state)
        state["message"] = f"A {state['encounter']['enemy_name']} prowls here. Type 'fight' to begin combat."
        return

    if tile == "L":
        state["message"] = "A dungeon chest waits here. Clear the dungeon and press 'e' to open it."
        return

    if tile == "R":
        state["message"] = "A ritual circle waits here. Press 'e' to enter."
        return

    if tile == "Y":
        state["message"] = "Armor altar: offer 2x ember heart, 2x grave dust, 1x titan shard."
        return

    if tile == "Z":
        state["message"] = "Weapon altar: offer 2x moon fang, 1x ember heart, 2x titan shard."
        return

    if tile == "X" and state["area"] == "summon_arena":
        state["encounter"] = current_enemy_template(state)
        state["message"] = f"{state['encounter']['enemy_name']} towers over the arena. Type 'fight' to begin combat."
        return

    if tile == "D":
        if state["area"] == "prison":
            state["message"] = "You are standing at the gate. Press 'e' to try opening it."
        else:
            state["message"] = "You are standing at the gate back to the Prison of Ardri. Press 'e' to interact."
        return

    if tile == "B":
        state["message"] = "You stand beside a rusty bunk bed."
    elif tile == "C":
        state["message"] = "You stand before the castle gates of Ardri."
    elif tile == "A":
        state["message"] = "You stop in front of the armorer's shop."
    elif tile == "M":
        state["message"] = "You stop by the merchant's stall."
    elif tile == "T":
        state["message"] = "You stand before the tavern entrance."
    elif tile == "S":
        state["message"] = "You reach Ardri's central square."
    elif tile == "K":
        state["message"] = "You stand before the King of Ardri."
    elif tile == "Q":
        state["message"] = "A patron waves you over with coin in hand."
    elif tile == "R":
        state["message"] = "The ritual circle waits for blood and relics."
    elif tile == "Y":
        state["message"] = "The armor altar is cold. Offer loot and press 'e' to summon."
    elif tile == "Z":
        state["message"] = "The weapon altar crackles. Offer loot and press 'e' to summon."
    elif tile == "X" and state["area"] == "summon_arena":
        state["message"] = "The summoned boss awaits in the arena center."


def move_player(direction: str, state: dict) -> None:
    dx, dy = MOVES[direction]
    x, y = state["player"]
    nx, ny = x + dx, y + dy
    target = state["tiles"][ny][nx]

    if target == "#":
        state["message"] = "You cannot move there. A wall blocks the tile."
        return

    if state["combat"]:
        state["message"] = "You are in combat. Finish it before moving."
        return

    state["player"] = [nx, ny]
    state["message"] = f"You move one tile to the {direction}."
    interact_tile(state)


def render(state: dict) -> None:
    clear_screen()
    if state["area"] == "prison":
        title = "PRISON"
        subtitle = "Search the block, gather what you need, and escape the prison."
        legend = f"{color('@', CYAN)} player   {color('G', MAGENTA)} guard   {color('I', CYAN)} item   {color('D', CYAN)} gate   {color('B', YELLOW)} bed   {color('###', RED)} wall"
    elif state["area"] == "city":
        title = "CITY OF ARDRI" if state.get("active_city_id") == "ardri" else state.get("active_city_name", "CITY")
        subtitle = "You have escaped the prison. Now explore the streets before you."
        legend = f"{color('@', CYAN)} player   {color('C', YELLOW)} castle   {color('A', CYAN)} armorer   {color('M', GREEN)} merchant   {color('T', YELLOW)} tavern   {color('S', GREEN)} square   {color('O', CYAN)} world exit   {color('D', CYAN)} gate   {color('###', RED)} wall"
    elif state["area"] == "world":
        title = "WORLD MAP"
        subtitle = "The lands beyond Ardri are different every time a new journey begins."
        legend = f"{color('@', CYAN)} player   {color('W', YELLOW)} city   {color('V', YELLOW)} village   {color('F', GREEN)} forest   {color('H', BLUE)} cave   {color('U', RED)} dungeon   {color('R', MAGENTA)} ritual   {color('###', RED)} border"
    elif state["area"] == "castle":
        title = AREA_META[state["area"]]["title"]
        subtitle = "Speak with the king and use D to leave the throne room."
        legend = f"{color('@', CYAN)} player   {color('K', YELLOW)} king   {color('D', CYAN)} exit   {color('###', RED)} wall"
    elif state["area"] == "ritual":
        title = AREA_META[state["area"]]["title"]
        subtitle = "Use monster loot at the altars to summon bosses. D returns to the world map."
        legend = f"{color('@', CYAN)} player   {color('Y', BLUE)} armor altar   {color('Z', RED)} weapon altar   {color('D', CYAN)} exit   {color('###', RED)} wall"
    elif state["area"] == "summon_arena":
        title = AREA_META[state["area"]]["title"]
        subtitle = "Face the summoned boss. A return door appears only after victory."
        legend = f"{color('@', CYAN)} player   {color('X', RED)} boss   {color('D', CYAN)} return door   {color('###', RED)} wall"
    elif state["area"] == "tavern":
        title = AREA_META[state["area"]]["title"]
        subtitle = "Meet patrons, pick up contracts, and use D to step back outside."
        legend = f"{color('@', CYAN)} player   {color('Q', MAGENTA)} patron   {color('D', CYAN)} exit   {color('###', RED)} wall"
    else:
        title = AREA_META[state["area"]]["title"]
        subtitle = "Explore the building interior and use D to step back outside."
        legend = f"{color('@', CYAN)} player   {color('D', CYAN)} exit   {color('###', RED)} wall"

    print(color(f"{BOLD}{title}{RESET}", MAGENTA))
    print(color("=" * len(title), MAGENTA))
    print(color(subtitle, DIM))
    print()
    print(merge_columns(render_grid(state), side_panel(state)))
    print()
    print(color("Legend:", BOLD))
    print(legend)
    print()
    print(color("Status", BOLD))
    if state["area"] == "city":
        place = state.get("active_city_name", "Ardri")
    elif state["area"] == "world":
        location = world_location_at(state, state["player"][0], state["player"][1])
        place = location["name"] if location else AREA_META["world"]["place"]
    elif state["area"] in {"village", "forest", "cave", "dungeon", "ritual"}:
        place = state.get("active_site_name") or AREA_META[state["area"]]["place"]
        if state["area"] == "dungeon":
            location = world_location_at(state, state["active_world_pos"][0], state["active_world_pos"][1])
            if location:
                place = f"{place} R{location.get('room_index', 0) + 1}/{len(location.get('rooms', []))}"
    else:
        place = AREA_META.get(state["area"], AREA_META["city"])["place"]
    print(f"- Place: {place}")
    if not state.get("prison_escaped"):
        print(f"- Key: {'yes' if state['has_key'] else 'no'}")
    print(f"- HP: {state['hp']}/{state['max_hp']}")
    equipped = state["equipped_weapon"] or "none"
    armor = state.get("equipped_armor") or "none"
    print(f"- Equipped weapon: {equipped}")
    print(f"- Equipped armor: {armor}")
    print(f"- Level: {state['level']} ({state['xp']}/{xp_to_next_level(state['level'])} XP)")
    print(f"- Position: x={state['player'][0]}, y={state['player'][1]}")
    print(f"- Message: {state['message']}")
    if state["combat"]:
        print(f"- Combat: {combat_status(state)}")


def main() -> None:
    menu_message = None
    while True:
        show_start_menu(menu_message)
        menu_message = None
        state = load_game()
        render(state)

        while state["running"]:
            try:
                raw = input(color("\n> ", BOLD)).strip().lower()
            except EOFError:
                print("\nSee you soon!")
                return

            normalized_words = []

            if not raw:
                if state["combat"]:
                    command = "attack"
                else:
                    state["message"] = "Enter a command to move through the area."
                    render(state)
                    continue
            else:
                words = raw.split()
                normalized_words = [ALIASES.get(word, word) for word in words]
                state["last_words"] = normalized_words
                command = normalized_words[0]

            if raw == "f":
                if state["combat"]:
                    command = "flee"
                elif state["encounter"]:
                    command = "fight"

            if state["combat"] and command != "quit":
                handle_combat(command, state)
                if state["pending_enemy_attack"]:
                    render(state)
                    time.sleep(RIPOSTE_DELAY)
                    enemy_attack(state)
                    state["pending_enemy_attack"] = False
                    save_game(state)
                    render(state)
                    continue
            elif command == "fight":
                if state["encounter"]:
                    begin_combat(state)
                else:
                    state["message"] = "There is no one here to fight."
            elif command in MOVES:
                move_player(command, state)
            elif command == "interact":
                state["show_inventory_panel"] = False
                state["message"] = interact_current_tile(state)
            elif command == "look":
                state["show_inventory_panel"] = False
                state["message"] = "You take a careful look around you."
            elif command == "inventory":
                state["message"] = show_inventory(state)
            elif command == "money":
                state["show_inventory_panel"] = False
                state["message"] = show_money(state)
            elif command == "stats":
                state["show_inventory_panel"] = False
                state["message"] = show_stats(state)
            elif command == "use":
                item = " ".join(normalized_words[1:-1]) if len(normalized_words) > 2 and normalized_words[-1].isdigit() else " ".join(normalized_words[1:])
                qty = int(normalized_words[-1]) if len(normalized_words) > 2 and normalized_words[-1].isdigit() else 1
                state["message"] = consume_potion(state, item, qty)
            elif command == "buy":
                state["show_inventory_panel"] = False
                state["message"] = buy_item(state, normalized_words)
            elif command == "sell":
                state["show_inventory_panel"] = False
                state["message"] = sell_item(state, normalized_words)
            elif command == "reset":
                reset_save()
                menu_message = "Save reset. Press Enter to begin a new game."
                break
            elif command == "equip":
                state["message"] = equip_item(normalized_words, state)
            elif command == "unequip":
                state["message"] = unequip_item(normalized_words, state)
            elif command == "cheat":
                state["message"] = grant_all_items(state)
            elif command == "help":
                state["show_inventory_panel"] = False
                state["message"] = show_help()
            elif command == "quit":
                save_game(state)
                print("See you soon!")
                return
            else:
                state["show_inventory_panel"] = False
                state["message"] = "Unknown command. Type 'help' to see the controls."

            save_game(state)
            render(state)


if __name__ == "__main__":
    if os.name == "nt":
        os.system("")
    main()
