"""
Curses-based interface for Babka RPG.
"""
import curses
import time
import random
import textwrap
from classes import Location, Combat
import helper
import functions as f

# Размеры окон (можно подстроить под размер терминала)
STATS_WIDTH = 50
STATS_HEIGHT = 13  # увеличено для корректного отображения всех строк
LOCINFO_HEIGHT = 10  # высота окна информации о локации и NPC
INV_HEIGHT = 10  # высота окна инвентаря
NPC_STATS_HEIGHT = 7  # высота окна статистики NPC
MENU_HEIGHT = 7  # Высота окна меню
MENU_WIDTH = 50  # ширина меню справа

# --- Окна ---


def wrap_text(text, width):
    """Разбивает строку на несколько по ширине width."""
    return textwrap.wrap(text, width)


def wrap_menu_item(text, width):
    """Разбивает пункт меню на несколько строк по ширине width."""
    return textwrap.wrap(text, width)


def draw_stats(win, babka, location):
    """Draws the stats window for Babka."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    stats_lines = [
        f'Имя: {babka.name}',
        f'Уровень: {babka.level}',
        f'HP: {babka.stats.hp}/{babka.maxhp}',
        f'Сила: {babka.stats.strength}',
        f'Ловкость: {babka.stats.dexterity}',
        f'Удача: {babka.stats.luck}',
        f'Урон: {babka.stats.damage}',
        f'Защита: {babka.stats.defence}',
        f'Опыт: {babka.stats.exp} / {100 * babka.level}',
        f'Оружие: {helper.babka_weapon.get(babka.weapon, ["нет"])[0]}',
        f'Локация: {helper.locations[babka.location][0]}',
        'Инвентарь:'
    ]
    for item in babka.inventory:
        name, dmg = helper.babka_weapon.get(item, ['?', 0])
        stats_lines.append(f'- {name} (урон: {dmg})')
    y = 1
    for line in stats_lines:
        try:
            safe_line = str(line)
            safe_line = safe_line.encode(
                'utf-8', errors='replace'
            ).decode('utf-8', errors='replace')
        except Exception:  # pylint: disable=broad-except
            safe_line = '?'
        for subline in wrap_text(safe_line, max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline)
            y += 1
    win.refresh()


def draw_locinfo(win, location):
    """Draws the location info window."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    win.addstr(1, 2, f'Локация: {helper.locations[location.location_num][0]}'[:w-4])
    win.addstr(2, 2, 'NPC на локации:'[:w-4])
    npcs = location.get_npc() or {}
    y = 3
    for npc in npcs.values():
        if y >= h-1:
            break
        line = f'- {npc.name} ({npc.mood})'
        try:
            safe_line = str(line)
            safe_line = safe_line.encode(
                'utf-8', errors='replace'
            ).decode('utf-8', errors='replace')
        except Exception:  # pylint: disable=broad-except
            safe_line = '?'
        for subline in wrap_text(safe_line, max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline)
            y += 1
    win.refresh()


def draw_main(win, lines):
    """Draws the main event window."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    visible_lines = lines[-(h-2):] if len(lines) > (h-2) else lines
    y = 1
    for line in visible_lines:
        try:
            safe_line = str(line)
            safe_line = safe_line.encode(
                'utf-8', errors='replace'
            ).decode('utf-8', errors='replace')
        except Exception:  # pylint: disable=broad-except
            safe_line = '?'
        for subline in wrap_text(safe_line, max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline)
            y += 1
    win.refresh()


def draw_dialog(win, dialog_lines):
    """Draws the dialog window."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    y = 1
    for line in dialog_lines[-(h-2):]:
        try:
            safe_line = str(line)
            safe_line = safe_line.encode(
                'utf-8', errors='replace'
                ).decode('utf-8', errors='replace')
        except Exception:  # pylint: disable=broad-except
            safe_line = '?'
        for subline in wrap_text(safe_line, max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline)
            y += 1
    win.refresh()


def draw_inventory(win, babka):
    """Draws the inventory window."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    win.addstr(1, 2, 'Инвентарь:'[:w-4])
    y = 2
    for item in babka.inventory:
        marker = '>' if babka.weapon == item else ' '
        name, dmg = helper.babka_weapon.get(item, ['?', 0])
        line = f'{marker} {name} (урон: {dmg})'
        try:
            safe_line = str(line)
            safe_line = safe_line.encode(
                'utf-8', errors='replace'
            ).decode('utf-8', errors='replace')
        except Exception:  # pylint: disable=broad-except
            safe_line = '?'
        for subline in wrap_text(safe_line, max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline)
            y += 1
    win.refresh()


def draw_npc_stats(win, npc):
    """Draws the NPC stats window."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    stats_lines = [
        f'NPC: {npc.name}',
        f'Уровень: {npc.level}',
        f'HP: {npc.stats.hp}',
        f'Сила: {npc.stats.strength}',
        f'Урон: {npc.stats.damage}',
        f'Защита: {npc.stats.defence}',
        f'Настроение: '
        f'{npc.mood if getattr(npc, "revealed_mood", False) else "Нейтральный"}',
    ]
    y = 1
    for line in stats_lines:
        try:
            safe_line = str(line)
            safe_line = safe_line.encode(
                'utf-8', errors='replace'
            ).decode('utf-8', errors='replace')
        except Exception:  # pylint: disable=broad-except
            safe_line = '?'
        for subline in wrap_text(safe_line, max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline)
            y += 1
    win.refresh()


def curses_menu(win, title, items):
    """Displays a menu and returns the selected index or -1 for ESC."""
    win.clear()
    win.box()
    h, w = win.getmaxyx()
    win.addstr(1, 2, title[:w-4])
    pos = 0
    win.keypad(True)
    while True:
        y = 3
        for idx, item in enumerate(items):
            marker = '>' if idx == pos else ' '
            lines = wrap_menu_item(f'{marker} {item}', max(1, w-4))
            for i, line in enumerate(lines):
                if y >= h-2:
                    break
                prefix = '  ' if i > 0 else ''
                win.addstr(y, 2, prefix + line)
                y += 1
        win.addstr(h-2, 2, '↑/↓ — выбор, Enter — подтвердить, ESC — назад'[:w-4])
        win.refresh()
        key = win.getch()
        if key == curses.KEY_UP:
            pos = (pos - 1) % len(items)
        elif key == curses.KEY_DOWN:
            pos = (pos + 1) % len(items)
        elif key in (ord('k'), ord('K')):
            pos = (pos - 1) % len(items)
        elif key in (ord('j'), ord('J')):
            pos = (pos + 1) % len(items)
        elif key in (curses.KEY_ENTER, 10, 13):
            return pos
        elif key == 27:
            return -1


def curses_menu_in_menuwin(menu_win, title, items):
    """Displays a menu in a given window and returns the selected index or -1 for ESC."""
    h, w = menu_win.getmaxyx()
    pos = 0
    menu_win.keypad(True)
    while True:
        menu_win.clear()
        menu_win.box()
        menu_win.addstr(1, 2, title[:w-4])
        y = 3
        for idx, item in enumerate(items):
            if y >= h-2:
                break
            marker = '>' if idx == pos else ' '
            lines = wrap_menu_item(f'{marker} {item}', max(1, w-4))
            for i, line in enumerate(lines):
                if y >= h-2:
                    break
                prefix = '  ' if i > 0 else ''
                menu_win.addstr(y, 2, prefix + line)
                y += 1
        menu_win.addstr(h-2, 2, '↑/↓ — выбор, Enter — подтвердить, ESC — назад'[:w-4])
        menu_win.refresh()
        key = menu_win.getch()
        if key == curses.KEY_UP:
            pos = (pos - 1) % len(items)
        elif key == curses.KEY_DOWN:
            pos = (pos + 1) % len(items)
        elif key in (ord('k'), ord('K')):
            pos = (pos - 1) % len(items)
        elif key in (ord('j'), ord('J')):
            pos = (pos + 1) % len(items)
        elif key in (curses.KEY_ENTER, 10, 13):
            return pos
        elif key == 27:
            return -1


class CursesMessageHandler:
    """Handles messages for curses combat output."""
    def __init__(self, main_lines):
        self.main_lines = main_lines
        self.battle_lines = []

    def print_message(self, message, msg_type='info'):
        """Appends a message to the battle lines."""
        del msg_type  # unused
        self.battle_lines.append(message)

    def pop_battle_lines(self):
        """Returns and clears the battle lines."""
        lines = self.battle_lines[:]
        self.battle_lines.clear()
        return lines


def print_event_lines(main_win, main_lines, new_lines):
    """Prints event lines with a delay."""
    for line in new_lines:
        main_lines.append(line)
        draw_main(main_win, main_lines)
        main_win.refresh()
        time.sleep(0.3)


def fight_curses(
    main_lines: list,
    dialog_lines: list,
    babka,
    npc,
    stats_win,
    locinfo_win,
    main_win,
    dialog_win,
    inv_win,
    location,
    npc_stats_win=None
) -> None:
    """
    Handles the turn-based combat UI for a fight between the player (babka) and an NPC.

    Args:
        main_lines (list): The main output lines for the UI.
        dialog_lines (list): The dialog output lines (unused).
        babka: The player character object.
        npc: The NPC character object.
        stats_win: The curses window for displaying player stats.
        locinfo_win: The curses window for displaying location info.
        main_win: The main curses window for output.
        dialog_win: The curses window for dialog (unused).
        inv_win: The curses window for inventory display.
        location: The current location object.
        npc_stats_win: (Optional) The curses window for displaying NPC stats.
    Returns:
        None
    """
    """Handles the turn-based combat UI."""
    del dialog_lines, dialog_win  # unused
    handler = CursesMessageHandler(main_lines)
    combat = Combat(handler)
    print_event_lines(main_win, main_lines, [f'Бой: {babka.name} vs {npc.name}!'])
    while True:
        print_event_lines(main_win, main_lines, [f'{babka.say()}'])
        draw_stats(stats_win, babka, location)
        draw_locinfo(locinfo_win, location)
        draw_main(main_win, main_lines)
        draw_inventory(inv_win, babka)
        if npc_stats_win:
            draw_npc_stats(npc_stats_win, npc)
        main_win.refresh()
        stats_win.refresh()
        locinfo_win.refresh()
        inv_win.refresh()
        if npc_stats_win:
            npc_stats_win.refresh()
        time.sleep(0.3)
        if combat.attack(babka, npc):
            print_event_lines(main_win, main_lines, handler.pop_battle_lines())
            print_event_lines(
                main_win, main_lines,
                [npc.say(), f'{npc.name}: Ну ты и падла, я умираю!']
            )
            exp = babka.calculate_expirience(npc.level)
            babka.add_experience(exp)
            max_exp = 100 * babka.level
            print_event_lines(
                main_win, main_lines,
                [
                    f'Бабка {babka.name} получает {exp} опыта.',
                    f'Теперь у нее {babka.stats.exp} из {max_exp} опыта.'
                ]
            )
            draw_stats(stats_win, babka, location)
            draw_locinfo(locinfo_win, location)
            draw_main(main_win, main_lines)
            draw_inventory(inv_win, babka)
            if npc_stats_win:
                draw_npc_stats(npc_stats_win, npc)
            main_win.refresh()
            stats_win.refresh()
            locinfo_win.refresh()
            inv_win.refresh()
            if npc_stats_win:
                npc_stats_win.refresh()
            time.sleep(0.3)
            break
        print_event_lines(main_win, main_lines, handler.pop_battle_lines())
        print_event_lines(main_win, main_lines, [npc.say()])
        draw_stats(stats_win, babka, location)
        draw_locinfo(locinfo_win, location)
        draw_main(main_win, main_lines)
        draw_inventory(inv_win, babka)
        if npc_stats_win:
            draw_npc_stats(npc_stats_win, npc)
        main_win.refresh()
        stats_win.refresh()
        locinfo_win.refresh()
        inv_win.refresh()
        if npc_stats_win:
            npc_stats_win.refresh()
        time.sleep(0.3)
        if combat.attack(npc, babka):
            print_event_lines(main_win, main_lines, handler.pop_battle_lines())
            print_event_lines(
                main_win, main_lines,
                [npc.say(), 'Ты сдох! Игра окончена.']
            )
            insult = random.choice(helper.INSULT_PHRASES)
            print_event_lines(main_win, main_lines, [insult])
            draw_stats(stats_win, babka, location)
            draw_locinfo(locinfo_win, location)
            draw_main(main_win, main_lines)
            draw_inventory(inv_win, babka)
            if npc_stats_win:
                draw_npc_stats(npc_stats_win, npc)
            main_win.refresh()
            stats_win.refresh()
            locinfo_win.refresh()
            inv_win.refresh()
            if npc_stats_win:
                npc_stats_win.refresh()
            time.sleep(0.3)
            raise RuntimeError('GAME_OVER_RETURN_TO_MENU')
        print_event_lines(main_win, main_lines, handler.pop_battle_lines())


def curses_menu_game_loop(stdscr, babka):
    """Main game loop for the curses interface."""
    curses.curs_set(0)
    stdscr.clear()
    min_width = 80
    min_height = 24
    max_y, max_x = stdscr.getmaxyx()
    if max_x < min_width or max_y < min_height:
        stdscr.clear()
        stdscr.addstr(
            0, 0, f"Терминал слишком маленький! Нужно хотя бы {min_width}x{min_height}."[:max_x-1]
        )
        stdscr.addstr(1, 0, f"Сейчас: {max_x}x{max_y}"[:max_x-1])
        stdscr.addstr(3, 0, "Растяните окно терминала и перезапустите игру."[:max_x-1])
        stdscr.addstr(5, 0, "Нажмите любую клавишу для выхода..."[:max_x-1])
        stdscr.refresh()
        stdscr.getch()
        return
    stats_win = curses.newwin(STATS_HEIGHT, STATS_WIDTH, 0, 0)
    locinfo_win = curses.newwin(LOCINFO_HEIGHT, STATS_WIDTH, STATS_HEIGHT, 0)
    inv_win = curses.newwin(INV_HEIGHT, STATS_WIDTH, STATS_HEIGHT + LOCINFO_HEIGHT, 0)
    npc_stats_win = curses.newwin(
        NPC_STATS_HEIGHT, STATS_WIDTH, STATS_HEIGHT + LOCINFO_HEIGHT + INV_HEIGHT, 0
    )
    main_win = curses.newwin(max_y, max_x - STATS_WIDTH - MENU_WIDTH, 0, STATS_WIDTH)
    menu_win = curses.newwin(max_y, MENU_WIDTH, 0, max_x - MENU_WIDTH)
    main_lines = ["Добро пожаловать в Babka 2.0!"]
    location = Location(babka.location)
    running = True
    while running:
        draw_stats(stats_win, babka, location)
        draw_locinfo(locinfo_win, location)
        draw_inventory(inv_win, babka)
        draw_main(main_win, main_lines)
        main_lines.append('Выбери дальнейшее действие')
        draw_main(main_win, main_lines)
        main_win.refresh()
        menu_items = [
            'Переместиться',
            'Действие',
            'Инвентарь',
            'Сохранить бабку',
            'Сесть на лавочку и погрызть семечки',
            'Выход',
        ]
        choice = curses_menu_in_menuwin(menu_win, 'Главное меню', menu_items)
        if choice == 0:
            loc_names = [
                name[0] for loc_id, name in helper.locations.items() if loc_id != babka.location
            ]
            loc_ids = [loc_id for loc_id in helper.locations if loc_id != babka.location]
            loc_choice = curses_menu_in_menuwin(menu_win, 'Куда идем?', loc_names)
            if loc_choice >= 0:
                new_loc = loc_ids[loc_choice]
                main_lines.append(f'Бабка переместилась в {helper.locations[new_loc][0]}')
                babka.location = new_loc
                location = Location(new_loc)
                location.generate_location(babka.level, babka.stats.exp)
                if random.random() < 0.9:
                    weapon = location.spawn_weapon()
                    if weapon and weapon not in babka.inventory:
                        babka.inventory.append(weapon)
                        main_lines.append(f'Бабка нашла оружие: {helper.babka_weapon[weapon][0]}!')
                    elif weapon:
                        main_lines.append(
                            f'Бабка нашла {helper.babka_weapon[weapon][0]}, '
                            'но оно уже есть в инвентаре.'
                        )
        elif choice == 1:
            npcs = location.get_npc() or {}
            if npcs:
                npc_names = [
                    f'{npc.name} (Нейтральный)'
                    if not getattr(npc, 'revealed_mood', False)
                    else f'{npc.name} ({npc.mood})'
                    for npc in npcs.values()
                ]
                npc_choice = curses_menu_in_menuwin(menu_win, 'Выбери NPC', npc_names)
                if npc_choice >= 0:
                    npc = list(npcs.values())[npc_choice]
                    npc_actions = ['Атаковать', 'Поговорить', 'Уйти']
                    act_choice = curses_menu_in_menuwin(
                        menu_win, f'Действие с {npc.name}', npc_actions
                        )
                    if act_choice == 0:
                        main_lines.append(f'Бабка атакует {npc.name}!')
                        npc.revealed_mood = True
                        fight_curses(
                            main_lines,
                            main_lines,
                            babka,
                            npc,
                            stats_win,
                            locinfo_win,
                            main_win,
                            main_win,
                            inv_win,
                            location,
                            npc_stats_win
                        )
                        if npc.stats.hp <= 0:
                            npc_key = list(location.npc.keys())[npc_choice]
                            del location.npc[npc_key]
                            if not location.npc:
                                sad_phrase = random.choice(helper.SAD_PHRASES)
                                main_lines.append(f'Бабка: {sad_phrase}')
                                babka.location = 1
                                babka.stats.hp = babka.maxhp
                                main_lines.append(
                                    'Бабка отправилась домой и полностью восстановила здоровье.'
                                )
                                location = Location(1)
                                if npc_stats_win:
                                    npc_stats_win.clear()
                                    npc_stats_win.box()
                                    npc_stats_win.refresh()
                    elif act_choice == 1:
                        main_lines.append(f'Бабка говорит с {npc.name}: "{f.generate_phrase()}"')
                        npc.revealed_mood = True
                        main_lines.append(npc.say())
                        npc_info = [
                            f'NPC: {npc.name}',
                            f'Уровень: {npc.level}',
                            f'HP: {npc.stats.hp}',
                            f'Сила: {npc.stats.strength}',
                            f'Ловкость: {npc.stats.dexterity}',
                            f'Удача: {npc.stats.luck}',
                            f'Урон: {npc.stats.damage}',
                            f'Защита: {npc.stats.defence}',
                            f'Оружие: {helper.babka_weapon.get(npc.weapon, ["нет"])[0]}',
                            f'Настроение: {npc.mood}',
                        ]
                        main_lines.extend(npc_info)
                        draw_npc_stats(npc_stats_win, npc)
                        npc_stats_win.refresh()
                    elif act_choice in (2, -1):
                        main_lines.append(f'Бабка оставила {npc.name} в покое.')
            else:
                main_lines.append('Здесь никого нет.')
        elif choice == 2:
            inv_items = [helper.babka_weapon.get(i, ['?'])[0] for i in babka.inventory]
            inv_choice = curses_menu_in_menuwin(menu_win, 'Выбери оружие', inv_items)
            if inv_choice >= 0:
                babka.weapon = babka.inventory[inv_choice]
                babka.calculate_stats()
                main_lines.append(f'Выбрано оружие: {helper.babka_weapon.get(babka.weapon, ["?"])[0]}')
        elif choice == 3:
            msg = f.save_game(babka)
            main_lines.append(msg)
        elif choice == 4:
            babka.stats.hp = babka.maxhp
            main_lines.append('Бабка села на лавочку и погрызла семечки. Здоровье полностью восстановлено!')
        elif choice in (5, -1):
            running = False
        time.sleep(0.05)


class Dummy:
    """Dummy class for standalone run."""
    name = 'Бабка'
    level = 1
    stats = type('Stats', (), {'hp': 100, 'exp': 0})()
    maxhp = 110
    location = 1
    weapon = 1
    inventory = [1, 2, 3]


if __name__ == "__main__":
    curses.wrapper(curses_menu_game_loop, Dummy())
