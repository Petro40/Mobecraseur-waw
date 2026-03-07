from __future__ import annotations

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
    "#..H.....F....#",
    "#.............#",
    "#.....####....#",
    "#.............#",
    "#...H......H..#",
    "#.............#",
    "#......T......#",
    "#.............#",
    "###############",
]

TILE_INFO = {
    "#": ("Mur", RED),
    ".": ("Sol", DIM),
    "B": ("Lit superpose", YELLOW),
    "G": ("Garde", RED),
    "I": ("Cachette", CYAN),
    "D": ("Porte de prison", CYAN),
    "H": ("Maison", YELLOW),
    "F": ("Fontaine", CYAN),
    "T": ("Place de la ville", GREEN),
}

ALIASES = {
    "z": "haut",
    "w": "haut",
    "haut": "haut",
    "up": "haut",
    "s": "bas",
    "bas": "bas",
    "down": "bas",
    "q": "gauche",
    "gauche": "gauche",
    "left": "gauche",
    "a": "attaquer",
    "d": "droite",
    "droite": "droite",
    "right": "droite",
    "aide": "aide",
    "help": "aide",
    "regarder": "regarder",
    "look": "regarder",
    "inv": "inventaire",
    "inventaire": "inventaire",
    "inventory": "inventaire",
    "stats": "stats",
    "fight": "fight",
    "f": "fuite",
    "run": "fuite",
    "fuir": "fuite",
    "fuite": "fuite",
    "equiper": "equip",
    "equiper": "equip",
    "equip": "equip",
    "attaquer": "attaquer",
    "attack": "attaquer",
    "continuer": "attaquer",
    "continue": "attaquer",
    "tour": "attaquer",
    "quitter": "quitter",
    "exit": "quitter",
}

MOVES = {
    "haut": (0, -1),
    "bas": (0, 1),
    "gauche": (-1, 0),
    "droite": (1, 0),
}

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
BAR_WIDTH = 20
RIPOSTE_DELAY = 0.5


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def build_state() -> dict:
    state = {
        "tiles": [],
        "player": [0, 0],
        "has_key": False,
        "inventory": [],
        "equipped_weapon": None,
        "hp": 20,
        "level": 1,
        "xp": 0,
        "running": True,
        "won": False,
        "message": "Bienvenue dans le bloc cellulaire. Fouille la prison et trouve la sortie.",
        "combat": None,
        "encounter": None,
        "show_inventory_panel": False,
        "guards_total": 0,
        "guards_defeated": 0,
        "key_guard_index": 1,
        "pending_enemy_attack": False,
    }
    load_area(state, "prison")
    return state


def load_area(state: dict, area: str) -> None:
    grid = PRISON_GRID if area == "prison" else CITY_GRID
    tiles = [list(row) for row in grid]
    player_x = 1
    player_y = 1

    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if tile == "@":
                player_x = x
                player_y = y
                tiles[y][x] = "."

    state["area"] = area
    state["tiles"] = tiles
    state["player"] = [player_x, player_y]
    state["combat"] = None
    state["encounter"] = None
    state["pending_enemy_attack"] = False

    if area == "prison":
        state["guards_total"] = sum(row.count("G") for row in tiles)
        state["guards_defeated"] = 0
        state["key_guard_index"] = random.randint(1, state["guards_total"])


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
            color("+---+", RED),
            color("| G |", RED),
            color("+---+", RED),
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
    if tile == "H":
        return [
            color("+---+", YELLOW),
            color("| H |", YELLOW),
            color("+---+", YELLOW),
        ]
    if tile == "F":
        return [
            color("+---+", CYAN),
            color("| F |", CYAN),
            color("+---+", CYAN),
        ]
    if tile == "T":
        return [
            color("+---+", GREEN),
            color("| T |", GREEN),
            color("+---+", GREEN),
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


def current_tile(state: dict) -> str:
    x, y = state["player"]
    return state["tiles"][y][x]


def nearby_text(state: dict) -> str:
    x, y = state["player"]
    here = current_tile(state)
    lines = []

    if here == ".":
        lines.append("Tu es sur une case vide.")
    elif here == "D":
        if state["area"] == "prison":
            lines.append("La grande porte de prison est juste devant toi.")
        else:
            lines.append("L'ancien portail de prison est derriere toi.")
    elif here == "G":
        lines.append("Un garde se tient devant toi. Tape 'fight' pour combattre ou pars de la case.")
    elif here == "B":
        lines.append("Un lit superpose grinche sous ton poids.")
    elif here == "I":
        lines.append("Une cachette improvisee est dissimulee dans le mur.")
    elif here == "H":
        lines.append("Une maison de ville borde la ruelle.")
    elif here == "F":
        lines.append("Une fontaine anime doucement la place.")
    elif here == "T":
        lines.append("Tu te tiens sur la place principale de la ville.")

    around = {
        "haut": (x, y - 1),
        "bas": (x, y + 1),
        "gauche": (x - 1, y),
        "droite": (x + 1, y),
    }

    for direction, (nx, ny) in around.items():
        tile = state["tiles"][ny][nx]
        name, _ = TILE_INFO.get(tile, ("Inconnu", DIM))
        if tile == "#":
            lines.append(f"{direction.capitalize()} : un mur bloque le passage.")
        elif tile == ".":
            lines.append(f"{direction.capitalize()} : une case libre.")
        else:
            lines.append(f"{direction.capitalize()} : {name}.")

    return "\n".join(lines)


def show_help() -> str:
    base = "Commandes : zqsd, haut/bas/gauche/droite, regarder, inv, stats, aide, quitter."
    combat = " Sur un garde, utilise fight pour lancer le combat. En combat, utilise a pour attaquer et f pour fuir."
    travel = " Sors de la prison par D pour atteindre la ville."
    return base + combat + travel


def xp_to_next_level(level: int) -> int:
    return 10 + (level - 1) * 5


def grant_xp(state: dict, amount: int) -> str:
    state["xp"] += amount
    messages = [f"Tu gagnes {amount} XP."]

    while state["xp"] >= xp_to_next_level(state["level"]):
        cost = xp_to_next_level(state["level"])
        state["xp"] -= cost
        state["level"] += 1
        state["hp"] = min(20, state["hp"] + 4)
        messages.append(f"Niveau {state['level']} atteint !")

    return " ".join(messages)


def show_inventory(state: dict) -> str:
    if not state["inventory"]:
        return "Inventaire : vide."
    return "Inventaire : " + ", ".join(state["inventory"])


def show_stats(state: dict) -> str:
    weapon = state["equipped_weapon"] or "aucune"
    damage = "5-8" if weapon == "lame artisanale" else "1-4"
    return (
        f"Stats - Vie: {state['hp']}/20, Niveau: {state['level']}, "
        f"XP: {state['xp']}/{xp_to_next_level(state['level'])}, Arme: {weapon}, Degats: {damage}."
    )


def inventory_panel(state: dict) -> str:
    lines = [color("INVENTAIRE", BOLD)]
    if not state["show_inventory_panel"]:
        lines.extend(["Tape 'inv' pour", "afficher le contenu."])
        return "\n".join(lines)

    if not state["inventory"]:
        lines.append("vide")
    else:
        for item in state["inventory"]:
            marker = " [equipe]" if state["equipped_weapon"] == item else ""
            lines.append(f"- {item}{marker}")

    if "lame artisanale" in state["inventory"]:
        lines.append("")
        lines.append("Commande :")
        lines.append("equip lame artisanale")
    return "\n".join(lines)


def side_panel(state: dict) -> str:
    return combat_panel(state) + "\n\n" + inventory_panel(state)


def equip_item(words: list[str], state: dict) -> str:
    if len(words) < 2:
        return "Precise quoi equiper."
    item = " ".join(words[1:])
    if item not in state["inventory"]:
        return f"Tu n'as pas '{item}' dans ton inventaire."
    if item != "lame artisanale":
        return f"Tu ne peux pas equiper '{item}'."
    state["equipped_weapon"] = item
    return "Tu equipes la lame artisanale."


def current_enemy_template() -> dict:
    return {
        "enemy_name": "Garde de ronde",
        "enemy_hp": 12,
        "enemy_max_hp": 12,
        "enemy_attack": 4,
        "has_key": False,
    }


def begin_combat(state: dict) -> None:
    if not state["encounter"]:
        state["encounter"] = current_enemy_template()
    state["combat"] = dict(state["encounter"])
    state["show_inventory_panel"] = False
    state["message"] = f"Le combat commence contre {state['combat']['enemy_name']} !"


def flee_combat(state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    if random.random() < 0.5:
        state["combat"] = None
        state["pending_enemy_attack"] = False
        state["encounter"] = dict(combat)
        state["message"] = "Tu parviens a fuir le combat."
        return

    state["message"] = "Ta fuite echoue."
    enemy_attack(state)


def end_combat(state: dict, victory: bool) -> None:
    x, y = state["player"]
    if victory:
        state["tiles"][y][x] = "."
        state["guards_defeated"] += 1
        if state["combat"]["has_key"] and not state["has_key"]:
            state["has_key"] = True
            state["inventory"].append("cle de cellule")
            state["message"] = "Le garde est neutralise. Tu recuperes sa cle de cellule. " + grant_xp(state, 8)
        else:
            state["message"] = "Le garde est neutralise. " + grant_xp(state, 8)
    state["combat"] = None
    state["encounter"] = None


def combat_status(state: dict) -> str:
    combat = state["combat"]
    if not combat:
        return ""
    return (
        f"Combat en cours contre {combat['enemy_name']} - "
        f"PV joueur: {state['hp']}/20 - PV ennemi: {combat['enemy_hp']}/{combat['enemy_max_hp']}"
    )


def combat_panel(state: dict) -> str:
    lines = [color("COMBAT", BOLD)]
    combat = state["combat"]

    if combat:
        enemy_bar = hp_bar(combat["enemy_hp"], combat["enemy_max_hp"])
        player_bar = hp_bar(state["hp"], 20)
        lines.extend(
            [
                f"Ennemi : {combat['enemy_name']}",
                f"PV ennemi : [{enemy_bar}]",
                f"          {combat['enemy_hp']}/{combat['enemy_max_hp']}",
                f"PV joueur : [{player_bar}]",
                f"          {state['hp']}/20",
                "",
            "Actions :",
            "- a",
            "- f",
            "",
            "a = attaquer puis",
            "riposte du garde.",
            "f = 1 chance",
            "sur 2.",
        ]
    )
        return "\n".join(lines)

    encounter = state["encounter"]
    if encounter:
        enemy_bar = hp_bar(encounter["enemy_hp"], encounter["enemy_max_hp"])
        key_note = "Oui" if encounter["has_key"] else "Non"
        lines.extend(
            [
                f"Adversaire : {encounter['enemy_name']}",
                f"PV : [{enemy_bar}]",
                f"     {encounter['enemy_hp']}/{encounter['enemy_max_hp']}",
                f"Degats : {encounter['enemy_attack']}",
                f"Possede la cle : {key_note}",
                "",
                "Actions :",
                "- fight ou f",
                "- bouger",
                "",
                "Tu peux fuir en",
                "quittant la case.",
            ]
        )
        return "\n".join(lines)

    if not combat:
        lines.append("Aucun combat en cours.")
        lines.append("")
        lines.append("Approche-toi d'un")
        lines.append("garde G pour")
        lines.append("declencher un duel.")
        return "\n".join(lines)

    return "\n".join(lines)


def enemy_attack(state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    damage = combat["enemy_attack"]

    state["hp"] -= damage

    if state["hp"] <= 0:
        state["hp"] = 0
        state["running"] = False
        state["message"] = "Le garde te terrasse. Fin de l'evasion."
        state["combat"] = None
        return

    state["message"] += f" Le garde riposte et t'inflige {damage} degats."


def player_auto_attack(state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    if state["equipped_weapon"] == "lame artisanale":
        damage = random.randint(5, 8)
    else:
        damage = random.randint(1, 4)
    combat["enemy_hp"] -= damage
    state["message"] = f"Tu frappes {combat['enemy_name']} et infliges {damage} degats."

    if combat["enemy_hp"] <= 0:
        end_combat(state, True)
        return

    state["pending_enemy_attack"] = True


def handle_combat(command: str, state: dict) -> None:
    combat = state["combat"]
    if not combat:
        return

    if command == "attaquer":
        player_auto_attack(state)
        return

    if command == "fuite":
        flee_combat(state)
        return

    if command == "aide":
        state["message"] = "En combat : a, f, aide, quitter."
        return

    if command == "regarder":
        state["message"] = combat_status(state)
        return

    state["message"] = "En combat, utilise : a ou f."


def interact_tile(state: dict) -> None:
    x, y = state["player"]
    tile = state["tiles"][y][x]

    state["encounter"] = None

    if tile == "I":
        state["tiles"][y][x] = "."
        state["inventory"].append("lame artisanale")
        state["message"] = "Tu trouves une lame artisanale et l'ajoutes a ton inventaire."
        return

    if tile == "G":
        state["encounter"] = current_enemy_template()
        next_guard_number = state["guards_defeated"] + 1
        state["encounter"]["has_key"] = next_guard_number == state["key_guard_index"]
        state["message"] = "Tu fais face a un garde de ronde. Tape 'fight' pour engager le combat."
        return

    if tile == "D":
        if state["area"] == "prison" and state["has_key"]:
            load_area(state, "ville")
            state["won"] = True
            state["message"] = "Tu franchis la porte de prison et debouches dans la ville."
        elif state["area"] == "prison":
            state["message"] = "La porte est verrouillee. Il te faut d'abord la cle."
        else:
            state["message"] = "Le portail de prison est maintenant derriere toi. La ville est devant toi."
        return

    if tile == "B":
        state["message"] = "Tu es devant un lit superpose rouille."
    elif tile == "H":
        state["message"] = "Tu passes devant une maison de ville aux volets fermes."
    elif tile == "F":
        state["message"] = "Tu t'arretes pres de la fontaine de la ville."
    elif tile == "T":
        state["message"] = "Tu rejoins la place centrale. Tu es enfin libre dans la ville."


def move_player(direction: str, state: dict) -> None:
    dx, dy = MOVES[direction]
    x, y = state["player"]
    nx, ny = x + dx, y + dy
    target = state["tiles"][ny][nx]

    if target == "#":
        state["message"] = "Impossible, un mur bloque cette case."
        return

    if state["combat"]:
        state["message"] = "Tu es en combat. Termine-le avant de bouger."
        return

    state["player"] = [nx, ny]
    state["message"] = f"Tu te deplaces d'une case vers le {direction}."
    interact_tile(state)


def render(state: dict) -> None:
    clear_screen()
    if state["area"] == "prison":
        title = "LA PRISON AUX CARREAUX"
        subtitle = "Fouille le bloc, recupere ton materiel et echappe-toi de la prison."
        legend = f"{color('@', CYAN)} joueur   {color('G', RED)} garde   {color('I', CYAN)} objet   {color('D', CYAN)} porte   {color('B', YELLOW)} lit   {color('###', RED)} mur"
    else:
        title = "LA VILLE"
        subtitle = "Tu as quitte la prison. Explore maintenant les rues de la ville."
        legend = f"{color('@', CYAN)} joueur   {color('H', YELLOW)} maison   {color('F', CYAN)} fontaine   {color('T', GREEN)} place   {color('D', CYAN)} portail   {color('###', RED)} mur"

    print(color(f"{BOLD}{title}{RESET}", MAGENTA))
    print(color(subtitle, DIM))
    print()
    print(merge_columns(render_grid(state), side_panel(state)))
    print()
    print(color("Legende :", BOLD))
    print(legend)
    print()
    print(color("Statut", BOLD))
    print(f"- Cle : {'oui' if state['has_key'] else 'non'}")
    print(f"- Vie : {state['hp']}/20")
    equipped = state["equipped_weapon"] or "aucune"
    print(f"- Arme equipee : {equipped}")
    print(f"- Niveau : {state['level']} ({state['xp']}/{xp_to_next_level(state['level'])} XP)")
    print(f"- Position : x={state['player'][0]}, y={state['player'][1]}")
    print(f"- Message : {state['message']}")
    if state["combat"]:
        print(f"- Combat : {combat_status(state)}")
    print()
    print(color("Autour de toi", BOLD))
    print(nearby_text(state))
    print()
    print(color("Commandes", BOLD))
    if state["combat"]:
        print("- a")
        print("- f")
        print("- regarder")
    elif state["encounter"]:
        print("- fight ou f")
        print("- zqsd ou haut/bas/gauche/droite")
        print("- inv")
        print("- stats")
        print("- equip lame artisanale")
    else:
        print("- zqsd ou haut/bas/gauche/droite")
        print("- regarder")
        print("- inv")
        print("- stats")
        print("- equip lame artisanale")
    print("- aide")
    print("- quitter")


def main() -> None:
    state = build_state()
    interact_tile(state)
    render(state)

    while state["running"]:
        try:
            raw = input(color("\n> ", BOLD)).strip().lower()
        except EOFError:
            print("\nA bientot !")
            break

        normalized_words = []

        if not raw:
            if state["combat"]:
                command = "attaquer"
            else:
                state["message"] = "Entre une commande pour bouger dans le bloc cellulaire."
                render(state)
                continue
        else:
            words = raw.split()
            normalized_words = [ALIASES.get(word, word) for word in words]
            command = normalized_words[0]

        if raw == "f":
            if state["combat"]:
                command = "fuite"
            elif state["encounter"]:
                command = "fight"

        if state["combat"] and command != "quitter":
            handle_combat(command, state)
            if state["pending_enemy_attack"]:
                render(state)
                time.sleep(RIPOSTE_DELAY)
                enemy_attack(state)
                state["pending_enemy_attack"] = False
                render(state)
                continue
        elif command == "fight":
            if state["encounter"]:
                begin_combat(state)
            else:
                state["message"] = "Il n'y a personne a combattre ici."
        elif command in MOVES:
            move_player(command, state)
        elif command == "regarder":
            state["show_inventory_panel"] = False
            state["message"] = "Tu observes le bloc et reperes les cases autour de toi."
        elif command == "inventaire":
            state["show_inventory_panel"] = True
            state["message"] = show_inventory(state)
        elif command == "stats":
            state["show_inventory_panel"] = False
            state["message"] = show_stats(state)
        elif command == "equip":
            state["show_inventory_panel"] = True
            state["message"] = equip_item(normalized_words, state)
        elif command == "aide":
            state["show_inventory_panel"] = False
            state["message"] = show_help()
        elif command == "quitter":
            print("A bientot !")
            break
        else:
            state["show_inventory_panel"] = False
            state["message"] = "Commande inconnue. Tape 'aide' pour voir les controles."

        render(state)


if __name__ == "__main__":
    if os.name == "nt":
        os.system("")
    main()
