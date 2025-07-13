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
from version import GAME_VERSION

# Размеры окон (можно подстроить под размер терминала)
STATS_WIDTH = 50
STATS_HEIGHT = 13  # увеличено для корректного отображения всех строк
LOCINFO_HEIGHT = 10  # высота окна информации о локации и NPC
INV_HEIGHT = 15  # высота окна инвентаря
NPC_STATS_HEIGHT = 15  # высота окна статистики NPC
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
    h, w = win.getmaxyx()
    # Цветная рамка
    win.attron(curses.color_pair(10))
    win.box()
    win.attroff(curses.color_pair(10))
    # Заголовок
    title = 'Статистика'
    win.attron(curses.color_pair(10) | curses.A_BOLD)
    win.addstr(0, (w - len(title)) // 2, title[:w-2])
    win.attroff(curses.color_pair(10) | curses.A_BOLD)
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
    h, w = win.getmaxyx()
    win.attron(curses.color_pair(11))
    win.box()
    win.attroff(curses.color_pair(11))
    title = 'Локация'
    win.attron(curses.color_pair(11) | curses.A_BOLD)
    win.addstr(0, (w - len(title)) // 2, title[:w-2])
    win.attroff(curses.color_pair(11) | curses.A_BOLD)
    win.addstr(1, 2, f'Локация: {helper.locations[location.location_num][0]}'[:w-4])
    win.addstr(2, 2, 'NPC на локации:'[:w-4])
    npcs = location.get_npc() or {}
    y = 3
    for npc in npcs.values():
        if y >= h-1:
            break
        # Добавляем пол NPC
        gender_str = (
            'муж.' if getattr(npc, 'gender', None) == 'male'
            else 'жен.' if getattr(npc, 'gender', None) == 'female' else '—'
        )
        # Показывать настроение только если revealed_mood
        if getattr(npc, 'revealed_mood', False):
            line = f'- {npc.name} ({gender_str}, {npc.mood})'
        else:
            line = f'- {npc.name} ({gender_str})'
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
    """Draws the main event window with color support."""
    win.clear()
    h, w = win.getmaxyx()
    win.attron(curses.color_pair(10))
    win.box()
    win.attroff(curses.color_pair(10))
    title = 'События'
    win.attron(curses.color_pair(10) | curses.A_BOLD)
    win.addstr(0, (w - len(title)) // 2, title[:w-2])
    win.attroff(curses.color_pair(10) | curses.A_BOLD)
    visible_lines = lines[-(h-2):] if len(lines) > (h-2) else lines
    y = 1
    for line, msg_type in visible_lines:
        if msg_type == "action":
            color = curses.color_pair(1)
        elif msg_type == "talk":
            color = curses.color_pair(2)
        elif msg_type == "info":
            color = curses.color_pair(3)
        else:
            color = curses.A_NORMAL
        for subline in wrap_text(str(line), max(1, w-4)):
            if y >= h-1:
                break
            win.addstr(y, 2, subline, color)
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
    h, w = win.getmaxyx()
    win.attron(curses.color_pair(10))
    win.box()
    win.attroff(curses.color_pair(10))
    title = 'Инвентарь'
    win.attron(curses.color_pair(10) | curses.A_BOLD)
    win.addstr(0, (w - len(title)) // 2, title[:w-2])
    win.attroff(curses.color_pair(10) | curses.A_BOLD)
    win.addstr(1, 2, 'Инвентарь:'[:w-4])
    y = 2
    for item in babka.inventory:
        marker = '>' if babka.weapon == item else ' '
        name, dmg = helper.babka_weapon.get(item, ['?', 0])
        line = f'{marker} {name} (урон: {dmg})'
        try:
            safe_line = str(line)
            safe_line = safe_line.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
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
    h, w = win.getmaxyx()
    win.attron(curses.color_pair(11))
    win.box()
    win.attroff(curses.color_pair(11))
    title = 'NPC'
    win.attron(curses.color_pair(11) | curses.A_BOLD)
    win.addstr(0, (w - len(title)) // 2, title[:w-2])
    win.attroff(curses.color_pair(11) | curses.A_BOLD)
    # Добавляем строку с полом после имени
    gender_str = (
        'мужской' if getattr(npc, 'gender', None) == 'male'
        else 'женский' if getattr(npc, 'gender', None) == 'female' else '—'
    )
    stats_lines = [
        f'NPC: {npc.name}',
        f'Пол: {gender_str}',
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


def curses_menu(win, title, items, babka, main_lines=None, main_win=None):
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
        if 0 <= key < 256:
            process_cheat_code(babka, chr(key), main_lines, main_win)
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


def curses_menu_in_menuwin(menu_win, title, items, babka, main_lines=None, main_win=None):
    """Displays a menu in a given window and returns the selected index or -1 for ESC."""
    h, w = menu_win.getmaxyx()
    pos = 0
    menu_win.keypad(True)
    # Словарь иконок для разных меню
    icon_map = {
        'Главное меню': ['🚶', '⚡', '🎒', '💾', '🍵', '🚪'],
        'Действие с': ['⚔️', '💬', '🚶'],
        'Выбери NPC': ['👤'] * len(items),
        'Выбери оружие': ['🔪'] * len(items),
        'Куда идем?': ['🚶'] * len(items),
        'Инвентарь': ['🎒'] * len(items),
    }
    # Определяем иконки для текущего меню
    icons = icon_map.get(title, ['•'] * len(items))
    if len(icons) < len(items):
        icons += ['•'] * (len(items) - len(icons))
    while True:
        menu_win.clear()
        # Цветная рамка
        menu_win.attron(curses.color_pair(10))
        menu_win.box()
        menu_win.attroff(curses.color_pair(10))
        # Цветной заголовок
        menu_win.attron(curses.color_pair(10) | curses.A_BOLD)
        menu_win.addstr(1, max(2, (w - len(title)) // 2), title[:w-4])
        menu_win.attroff(curses.color_pair(10) | curses.A_BOLD)
        y = 3
        for idx, item in enumerate(items):
            if y >= h-2:
                break
            marker = '>' if idx == pos else ' '
            icon = icons[idx] if idx < len(icons) else '•'
            lines = wrap_menu_item(
                f'{marker} {icon} {item}', max(1, w-4)
            )
            for i, line in enumerate(lines):
                if y >= h-2:
                    break
                prefix = '  ' if i > 0 else ''
                if idx == pos:
                    menu_win.attron(curses.color_pair(2) | curses.A_BOLD)
                    menu_win.addstr(y, 2, prefix + line)
                    menu_win.attroff(curses.color_pair(2) | curses.A_BOLD)
                else:
                    menu_win.attron(curses.color_pair(3))
                    menu_win.addstr(y, 2, prefix + line)
                    menu_win.attroff(curses.color_pair(3))
                y += 1
        # Цветная подсказка
        menu_win.attron(curses.color_pair(1))
        menu_win.addstr(
            h-2, 2, '↑/↓ — выбор, Enter — подтвердить, ESC — назад'[:w-4]
        )
        menu_win.attroff(curses.color_pair(1))
        menu_win.refresh()
        key = menu_win.getch()
        if 0 <= key < 256:
            process_cheat_code(babka, chr(key), main_lines, main_win)
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
        """Appends a message to the battle lines with type."""
        self.battle_lines.append((message, msg_type))

    def pop_battle_lines(self):
        """Returns and clears the battle lines."""
        lines = self.battle_lines[:]
        self.battle_lines.clear()
        return lines


def print_event_lines(main_win, main_lines, new_lines):
    """Prints event lines with a delay. new_lines: list of (text, type) or just text."""
    for entry in new_lines:
        if isinstance(entry, tuple):
            main_lines.append(entry)
        else:
            main_lines.append((entry, "info"))
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
    print_event_lines(main_win, main_lines, [(f'Бой: {babka.name} vs {npc.name}!', 'action')])
    while True:
        print_event_lines(main_win, main_lines, [(f'{babka.say()}', 'talk')])
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
                [(npc.say(), 'talk'), (f'{npc.name}: Ну ты и падла, я умираю!', 'action')]
            )
            exp = babka.calculate_expirience(npc.level)
            babka.add_experience(exp)
            max_exp = 100 * babka.level
            print_event_lines(
                main_win, main_lines,
                [
                    (f'Бабка {babka.name} получает {exp} опыта.', 'info'),
                    (f'Теперь у нее {babka.stats.exp} из {max_exp} опыта.', 'info')
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
        print_event_lines(main_win, main_lines, [(npc.say(), 'talk')])
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
                [(npc.say(), 'talk'), ('Ты сдох! Игра окончена.', 'action')]
            )
            insult = random.choice(helper.INSULT_PHRASES)
            print_event_lines(main_win, main_lines, [(insult, 'action')])
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


def process_cheat_code(babka, char, main_lines=None, main_win=None):
    if not hasattr(babka, 'cheat_buffer'):
        babka.cheat_buffer = ''
    if not hasattr(babka, 'godmode'):
        babka.godmode = False
    if not hasattr(babka, 'inventory'):
        babka.inventory = []
    if char:
        babka.cheat_buffer += char.lower()
        babka.cheat_buffer = babka.cheat_buffer[-6:]
        if 'iddqd' in babka.cheat_buffer:
            babka.godmode = True
            if main_lines is not None:
                main_lines.append(('Чит-режим: Бабка теперь бессмертна! (IDDQD)', 'info'))
                if main_win is not None:
                    draw_main(main_win, main_lines)
                    main_win.refresh()
            babka.cheat_buffer = ''
        elif 'idkfa' in babka.cheat_buffer:
            import helper
            babka.inventory = list(helper.babka_weapon.keys())
            if main_lines is not None:
                main_lines.append(('Чит-режим: Выдано всё оружие! (IDKFA)', 'info'))
                if main_win is not None:
                    draw_main(main_win, main_lines)
                    main_win.refresh()
            babka.cheat_buffer = ''


def curses_menu_game_loop(stdscr, babka):
    """Main game loop for the curses interface."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)      # действия (атака, защита)
    curses.init_pair(2, curses.COLOR_GREEN, -1)    # разговоры
    curses.init_pair(3, curses.COLOR_CYAN, -1)     # информация
    curses.init_pair(4, curses.COLOR_GREEN, -1)  # ярко-зеленый для имен (если поддерживается)
    curses.init_pair(10, curses.COLOR_CYAN, -1)    # рамка/заголовок
    curses.init_pair(11, curses.COLOR_MAGENTA, -1)  # альтернативная рамка/заголовок
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
    npc_stats_win = curses.newwin(
        NPC_STATS_HEIGHT, STATS_WIDTH, STATS_HEIGHT + LOCINFO_HEIGHT, 0
    )
    main_win = curses.newwin(max_y, max_x - STATS_WIDTH - MENU_WIDTH, 0, STATS_WIDTH)
    menu_win = curses.newwin(max_y - INV_HEIGHT, MENU_WIDTH, 0, max_x - MENU_WIDTH)
    inv_win = curses.newwin(INV_HEIGHT, MENU_WIDTH, max_y - INV_HEIGHT, max_x - MENU_WIDTH)
    main_lines = [(f"Добро пожаловать в Babka {GAME_VERSION}!", "info")]
    location = Location(babka.location)
    running = True
    if not hasattr(babka, 'godmode'):
        babka.godmode = False
    while running:
        draw_stats(stats_win, babka, location)
        draw_locinfo(locinfo_win, location)
        draw_main(main_win, main_lines)
        draw_inventory(inv_win, babka)
        main_lines.append(('Выбери дальнейшее действие', 'info'))
        draw_main(main_win, main_lines)
        main_win.refresh()
        stats_win.refresh()
        locinfo_win.refresh()
        menu_win.refresh()
        inv_win.refresh()
        menu_items = [
            'Переместиться',
            'Действие',
            'Инвентарь',
            'Сохранить бабку',
            'Сесть на лавочку и погрызть семечки',
            'Выход',
        ]
        choice = curses_menu_in_menuwin(menu_win, 'Главное меню', menu_items, babka, main_lines, main_win)
        if choice == 0:
            loc_names = [
                name[0] for loc_id, name in helper.locations.items() if loc_id != babka.location
            ]
            loc_ids = [loc_id for loc_id in helper.locations if loc_id != babka.location]
            loc_choice = curses_menu_in_menuwin(menu_win, 'Куда идем?', loc_names, babka, main_lines, main_win)
            if loc_choice >= 0:
                new_loc = loc_ids[loc_choice]
                main_lines.append((f'Бабка переместилась в {helper.locations[new_loc][0]}', 'info'))
                babka.location = new_loc
                location = Location(new_loc)
                location.generate_location(babka.level, babka.stats.exp)
                if random.random() < 0.9:
                    weapon = location.spawn_weapon()
                    if weapon and weapon not in babka.inventory:
                        babka.inventory.append(weapon)
                        main_lines.append((f'Бабка нашла оружие: {helper.babka_weapon[weapon][0]}!', 'info'))
                    elif weapon:
                        main_lines.append(
                            (f'Бабка нашла {helper.babka_weapon[weapon][0]}, но оно уже есть в инвентаре.', 'info')
                        )
        elif choice == 1:
            npcs = location.get_npc() or {}
            if npcs:
                npc_names = []
                for npc in npcs.values():
                    if getattr(npc, "revealed_mood", False):
                        mood_str = npc.mood if getattr(npc, "revealed_mood", False) else "Нейтральный"
                        name_str = f'{npc.name} ({mood_str})'
                    else:
                        if getattr(npc, 'gender', None) == 'male':
                            gender_str = ' (муж.)'
                        elif getattr(npc, 'gender', None) == 'female':
                            gender_str = ' (жен.)'
                        else:
                            gender_str = ''
                        name_str = f'{npc.name}{gender_str}'
                    npc_names.append(name_str)
                npc_choice = curses_menu_in_menuwin(menu_win, 'Выбери NPC', npc_names, babka, main_lines, main_win)
                if npc_choice >= 0:
                    npc = list(npcs.values())[npc_choice]
                    npc_actions = ['Атаковать', 'Поговорить', 'Уйти']
                    act_choice = curses_menu_in_menuwin(
                        menu_win, f'Действие с {npc.name}', npc_actions, babka, main_lines, main_win
                    )
                    if act_choice == 0:
                        main_lines.append((f'Бабка атакует {npc.name}!', 'action'))
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
                                main_lines.append((f'Бабка: {sad_phrase}', 'talk'))
                                babka.location = 1
                                babka.stats.hp = babka.maxhp
                                main_lines.append((
                                    'Бабка отправилась домой и полностью восстановила здоровье.',
                                    'info'))
                                location = Location(1)
                                if npc_stats_win:
                                    npc_stats_win.clear()
                                    npc_stats_win.box()
                                    npc_stats_win.refresh()
                    elif act_choice == 1:
                        main_lines.append((f'Бабка говорит с {npc.name}: "{f.generate_phrase()}"', 'talk'))
                        npc.revealed_mood = True
                        main_lines.append((npc.say(), 'talk'))
                        npc_info = [
                            (f'NPC: {npc.name}', 'talk'),
                            (f'Уровень: {npc.level}', 'info'),
                            (f'HP: {npc.stats.hp}', 'info'),
                            (f'Сила: {npc.stats.strength}', 'info'),
                            (f'Ловкость: {npc.stats.dexterity}', 'info'),
                            (f'Удача: {npc.stats.luck}', 'info'),
                            (f'Урон: {npc.stats.damage}', 'info'),
                            (f'Защита: {npc.stats.defence}', 'info'),
                            (f'Оружие: {helper.babka_weapon.get(npc.weapon, ["нет"])[0]}', 'info'),
                            (f'Настроение: {npc.mood}', 'info'),
                        ]
                        main_lines.extend(npc_info)
                        draw_npc_stats(npc_stats_win, npc)
                        npc_stats_win.refresh()
                    elif act_choice in (2, -1):
                        main_lines.append((f'Бабка оставила {npc.name} в покое.', 'info'))
            else:
                main_lines.append(('Здесь никого нет.', 'info'))
        elif choice == 2:
            inv_items = [helper.babka_weapon.get(i, ['?'])[0] for i in babka.inventory]
            inv_choice = curses_menu_in_menuwin(menu_win, 'Выбери оружие', inv_items, babka, main_lines, main_win)
            if inv_choice >= 0:
                babka.weapon = babka.inventory[inv_choice]
                babka.calculate_stats()
                main_lines.append((f'Выбрано оружие: {helper.babka_weapon.get(babka.weapon, ["?"])[0]}', 'info'))
        elif choice == 3:
            msg = f.save_game(babka)
            main_lines.append((msg, 'info'))
        elif choice == 4:
            babka.stats.hp = babka.maxhp
            main_lines.append(('Бабка села на лавочку и погрызла семечки. Здоровье полностью восстановлено!', 'info'))
        elif choice in (5, -1):
            running = False
        time.sleep(0.05)
        stdscr.nodelay(True)
        try:
            key = stdscr.getch()
            if key != -1 and 0 <= key < 256:
                process_cheat_code(babka, chr(key))
        except Exception:
            pass
        stdscr.nodelay(False)


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
