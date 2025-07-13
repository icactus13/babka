# coding=utf-8
"""
Main module
"""

import locale
import curses
from curses_menu import curses_menu_game_loop
from classes import Babka, Stats
import functions as f
import helper
import db
from version import GAME_VERSION


def curses_input_name(stdscr):
    """Красивый ввод имени бабки в рамке с цветами."""
    curses.echo()
    stdscr.clear()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)    # заголовок
    curses.init_pair(2, curses.COLOR_WHITE, -1)   # обычный текст
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # поле ввода
    h, w = stdscr.getmaxyx()
    win_width = 50
    win_height = 8
    win_y = max(0, h // 2 - win_height // 2)
    win_x = max(0, w // 2 - win_width // 2)
    # Рисуем рамку
    for i in range(win_width):
        stdscr.addch(win_y, win_x + i, curses.ACS_HLINE, curses.color_pair(1))
        stdscr.addch(win_y + win_height - 1, win_x + i, curses.ACS_HLINE, curses.color_pair(1))
    for i in range(win_height):
        stdscr.addch(win_y + i, win_x, curses.ACS_VLINE, curses.color_pair(1))
        stdscr.addch(win_y + i, win_x + win_width - 1, curses.ACS_VLINE, curses.color_pair(1))
    stdscr.addch(win_y, win_x, curses.ACS_ULCORNER, curses.color_pair(1))
    stdscr.addch(win_y, win_x + win_width - 1, curses.ACS_URCORNER, curses.color_pair(1))
    stdscr.addch(win_y + win_height - 1, win_x, curses.ACS_LLCORNER, curses.color_pair(1))
    stdscr.addch(win_y + win_height - 1, win_x + win_width - 1, curses.ACS_LRCORNER, curses.color_pair(1))
    # Заголовок
    title = 'Ввод имени бабки'
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(win_y + 1, win_x + (win_width - len(title)) // 2, title)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    # Подсказка (разбить на две строки)
    hint1 = 'Введите имя бабки (или оставьте пустым'
    hint2 = 'для случайного):'
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(win_y + 2, win_x + 2, hint1[:win_width-4])
    stdscr.addstr(win_y + 3, win_x + 2, hint2[:win_width-4])
    stdscr.attroff(curses.color_pair(2))
    # Поле для ввода
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(win_y + 5, win_x + 4, '> ')
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()
    encoding = locale.getpreferredencoding()
    name = stdscr.getstr(win_y + 5, win_x + 6, 30).decode(encoding, errors='replace').strip()
    curses.noecho()
    return name


def curses_options_menu(stdscr):
    """Display and handle the NPC name generation options menu."""
    options = ['Обычные имена NPC', 'Генерация имен NPC (цепи Маркова)']
    stdscr.clear()
    stdscr.addstr(2, 2, 'Выберите способ генерации имен NPC:')
    for i, opt in enumerate(options):
        stdscr.addstr(4 + i, 4, f'{i+1}. {opt}')
    stdscr.addstr(7, 2, 'Введите номер и нажмите Enter: ')
    stdscr.refresh()
    while True:
        try:
            choice = int(stdscr.getstr(7, 32, 2).decode('utf-8').strip())
            if choice in (1, 2):
                break
        except (ValueError, UnicodeDecodeError):
            pass
        stdscr.addstr(8, 2, 'Ошибка ввода. Попробуйте снова.')
        stdscr.refresh()
    helper.options['gen_names'] = 'norm' if choice == 1 else 'neuro'


def curses_load_menu(stdscr):
    """Красивое меню загрузки игры с рамкой, цветами и ascii-артом."""
    ascii_art = [
        r"   .-''''-.   ",
        r"  /        \  ",
        r"  | (o)  (o) | ",
        r"  |   .__.   | ",
        r"  | (_____)  | ",
        r"  \        /  ",
        r"   '-.__.-'   "
    ]
    pos = 0
    while True:
        saves = db.get_saves()
        if not saves:
            stdscr.clear()
            stdscr.addstr(2, 2, 'Нет сохранённых бабок. Нажмите любую клавишу...')
            stdscr.refresh()
            stdscr.getch()
            return None
        menu = [f'{i+1}. {name}' for i, name in enumerate(saves)] + ['Удалить сохранение', 'Назад']
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        win_width = 40
        win_height = 10 + len(ascii_art) + len(menu)
        win_y = max(0, h // 2 - win_height // 2)
        win_x = max(0, w // 2 - win_width // 2)
        # Рисуем рамку
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_WHITE, -1)
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)
        for i in range(win_width):
            stdscr.addch(win_y, win_x + i, curses.ACS_HLINE, curses.color_pair(4))
            stdscr.addch(win_y + win_height - 1, win_x + i, curses.ACS_HLINE, curses.color_pair(4))
        for i in range(win_height):
            stdscr.addch(win_y + i, win_x, curses.ACS_VLINE, curses.color_pair(4))
            stdscr.addch(win_y + i, win_x + win_width - 1, curses.ACS_VLINE, curses.color_pair(4))
        stdscr.addch(win_y, win_x, curses.ACS_ULCORNER, curses.color_pair(4))
        stdscr.addch(win_y, win_x + win_width - 1, curses.ACS_URCORNER, curses.color_pair(4))
        stdscr.addch(win_y + win_height - 1, win_x, curses.ACS_LLCORNER, curses.color_pair(4))
        stdscr.addch(win_y + win_height - 1, win_x + win_width - 1, curses.ACS_LRCORNER, curses.color_pair(4))
        # ASCII-арт
        for i, art_line in enumerate(ascii_art):
            stdscr.attron(curses.color_pair(3))
            x_art = win_x + (win_width - len(art_line)) // 2
            y_art = win_y + 1 + i
            stdscr.addstr(y_art, x_art, art_line)
            stdscr.attroff(curses.color_pair(3))
        # Заголовок
        title = 'Загрузка игры'
        y_title = win_y + 1 + len(ascii_art)
        x_title = win_x + (win_width - len(title)) // 2
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(y_title, x_title, title)
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        # Меню
        for i, item in enumerate(menu):
            y = win_y + 3 + len(ascii_art) + i
            x = win_x + 4
            if i == pos:
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                marker = '>'
            else:
                stdscr.attron(curses.color_pair(3))
                marker = ' '
            stdscr.addstr(y, x, f'{marker} {item}')
            if i == pos:
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.attroff(curses.color_pair(3))
        # Подсказка
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(win_y + win_height - 2, win_x + 2, '↑/↓ — выбор, Enter — подтвердить, ESC — назад')
        stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord('k'), ord('K')]:
            pos = (pos - 1) % len(menu)
        elif key in [curses.KEY_DOWN, ord('j'), ord('J')]:
            pos = (pos + 1) % len(menu)
        elif key in [curses.KEY_ENTER, 10, 13]:
            if pos < len(saves):
                babka_data = db.get_babka_from_db(pos + 1)
                if not babka_data:
                    stdscr.clear()
                    stdscr.addstr(2, 2, 'Ошибка загрузки сохранения. Нажмите любую клавишу...')
                    stdscr.refresh()
                    stdscr.getch()
                    continue
                babka = Babka(
                    name=babka_data['name'],
                    stats=None
                )
                babka.level = babka_data['level']
                babka.inventory = babka_data['inventory']
                babka.stats.hp = babka_data['hp']
                babka.stats.strength = babka_data['strength']
                babka.stats.dexterity = babka_data['dexterity']
                babka.stats.luck = babka_data['luck']
                babka.stats.damage = babka_data['damage']
                babka.stats.defence = babka_data['defence']
                babka.stats.exp = babka_data['exp']
                babka.location = babka_data['location']
                babka.maxhp = babka_data['maxhp']
                return babka
            elif pos == len(saves):  # Удалить сохранение
                # Переход в режим удаления
                del_pos = 0
                while True:
                    stdscr.clear()
                    # Рисуем ту же рамку и ascii-арт
                    for i in range(win_width):
                        stdscr.addch(win_y, win_x + i, curses.ACS_HLINE, curses.color_pair(4))
                        stdscr.addch(win_y + win_height - 1, win_x + i, curses.ACS_HLINE, curses.color_pair(4))
                    for i in range(win_height):
                        stdscr.addch(win_y + i, win_x, curses.ACS_VLINE, curses.color_pair(4))
                        stdscr.addch(win_y + i, win_x + win_width - 1, curses.ACS_VLINE, curses.color_pair(4))
                    stdscr.addch(win_y, win_x, curses.ACS_ULCORNER, curses.color_pair(4))
                    stdscr.addch(win_y, win_x + win_width - 1, curses.ACS_URCORNER, curses.color_pair(4))
                    stdscr.addch(win_y + win_height - 1, win_x, curses.ACS_LLCORNER, curses.color_pair(4))
                    stdscr.addch(
                        win_y + win_height - 1, win_x + win_width - 1, curses.ACS_LRCORNER, curses.color_pair(4)
                    )
                    for i, art_line in enumerate(ascii_art):
                        stdscr.attron(curses.color_pair(3))
                        stdscr.addstr(win_y + 1 + i, win_x + (win_width - len(art_line)) // 2, art_line)
                        stdscr.attroff(curses.color_pair(3))
                    # Заголовок для режима удаления
                    del_title = 'Удалить сохранение'
                    y_del_title = win_y + 1 + len(ascii_art)
                    x_del_title = win_x + (win_width - len(del_title)) // 2
                    stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                    stdscr.addstr(y_del_title, x_del_title, del_title)
                    stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                    # Список сохранений для удаления
                    for i, name in enumerate(saves):
                        y_del_menu = win_y + 3 + len(ascii_art) + i
                        x_del_menu = win_x + 4
                        if i == del_pos:
                            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                            marker = '>'
                        else:
                            stdscr.attron(curses.color_pair(3))
                            marker = ' '
                        stdscr.addstr(y_del_menu, x_del_menu, f'{marker} {i+1}. {name}')
                        if i == del_pos:
                            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
                        else:
                            stdscr.attroff(curses.color_pair(3))
                    stdscr.attron(curses.color_pair(1))
                    hint = '↑/↓ — выбрать, Enter — удалить, ESC — назад'
                    stdscr.addstr(win_y + win_height - 2, win_x + 2, hint)
                    stdscr.attroff(curses.color_pair(1))
                    stdscr.refresh()
                    key2 = stdscr.getch()
                    # Вместо Delete теперь удаление по Enter
                    if key2 in [curses.KEY_UP, ord('k'), ord('K')]:
                        del_pos = (del_pos - 1) % len(saves)
                    elif key2 in [curses.KEY_DOWN, ord('j'), ord('J')]:
                        del_pos = (del_pos + 1) % len(saves)
                    elif key2 in [curses.KEY_ENTER, 10, 13]:
                        idx_to_delete = del_pos + 1
                        db.delete_babka_by_id(idx_to_delete)
                        saves = db.get_saves()
                        if not saves:
                            return None  # Сразу выйти в главное меню
                        if del_pos >= len(saves):
                            del_pos = max(0, len(saves) - 1)
                        continue
                    elif key2 == 27:
                        break
                continue
            elif pos == len(saves) + 1:  # Назад
                return None
        elif key == 27:
            return None


def curses_main_menu(stdscr):
    """Красивое главное меню с ASCII-артом, цветами и рамкой, без отдельного окна."""
    menu = [
        'Начать игру',
        'Опции',
        'Загрузить игру',
        'Выход',
    ]
    ascii_art = [
        r"   .-''''-.   ",
        r"  /        \  ",
        r"  | (o)  (o) | ",
        r"  |   .__.   | ",
        r"  | (_____)  | ",
        r"  \        /  ",
        r"   '-.__.-'   "
    ]
    pos = 0
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)    # версия
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # выбранный пункт
    curses.init_pair(3, curses.COLOR_WHITE, -1)   # обычный текст
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)  # рамка/заголовок
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        win_width = 40
        win_height = 10 + len(ascii_art)
        win_y = max(0, h // 2 - win_height // 2)
        win_x = max(0, w // 2 - win_width // 2)
        # Рисуем рамку вручную
        for i in range(win_width):
            stdscr.addch(win_y, win_x + i, curses.ACS_HLINE, curses.color_pair(4))
            stdscr.addch(win_y + win_height - 1, win_x + i, curses.ACS_HLINE, curses.color_pair(4))
        for i in range(win_height):
            stdscr.addch(win_y + i, win_x, curses.ACS_VLINE, curses.color_pair(4))
            stdscr.addch(win_y + i, win_x + win_width - 1, curses.ACS_VLINE, curses.color_pair(4))
        stdscr.addch(win_y, win_x, curses.ACS_ULCORNER, curses.color_pair(4))
        stdscr.addch(win_y, win_x + win_width - 1, curses.ACS_URCORNER, curses.color_pair(4))
        stdscr.addch(win_y + win_height - 1, win_x, curses.ACS_LLCORNER, curses.color_pair(4))
        stdscr.addch(win_y + win_height - 1, win_x + win_width - 1, curses.ACS_LRCORNER, curses.color_pair(4))
        # ASCII-арт
        for i, art_line in enumerate(ascii_art):
            stdscr.attron(curses.color_pair(3))
            x_art = win_x + (win_width - len(art_line)) // 2
            y_art = win_y + 1 + i
            stdscr.addstr(y_art, x_art, art_line)
            stdscr.attroff(curses.color_pair(3))
        # Заголовок
        title = f'Babka {GAME_VERSION}'
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(win_y + 1 + len(ascii_art), win_x + (win_width - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        # Меню
        for i, item in enumerate(menu):
            y_menu = win_y + 3 + len(ascii_art) + i
            x_menu = win_x + 4
            if i == pos:
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                marker = '>'
            else:
                stdscr.attron(curses.color_pair(3))
                marker = ' '
            stdscr.addstr(y_menu, x_menu, f'{marker} {item}')
            if i == pos:
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.attroff(curses.color_pair(3))
        # Подсказка
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(win_y + win_height - 2, win_x + 2, '↑/↓ — выбор, Enter — подтвердить')
        stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord('k'), ord('K')]:
            pos = (pos - 1) % len(menu)
        elif key in [curses.KEY_DOWN, ord('j'), ord('J')]:
            pos = (pos + 1) % len(menu)
        elif key in [curses.KEY_ENTER, 10, 13]:
            return pos


def curses_allocate_stats(stdscr):
    """Красивое распределение очков между характеристиками в рамке с цветами."""
    stats = {
        'Сила': 1,
        'Ловкость': 1,
        'Удача': 1,
        'Защита': 1,
    }
    stat_keys = list(stats.keys())
    points = 5
    pos = 0
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)    # заголовок
    curses.init_pair(2, curses.COLOR_WHITE, -1)   # обычный текст
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # выбранная характеристика
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        win_width = 50
        win_height = 13
        win_y = max(0, h // 2 - win_height // 2)
        win_x = max(0, w // 2 - win_width // 2)
        # Рамка
        for i in range(win_width):
            stdscr.addch(win_y, win_x + i, curses.ACS_HLINE, curses.color_pair(1))
            stdscr.addch(win_y + win_height - 1, win_x + i, curses.ACS_HLINE, curses.color_pair(1))
        for i in range(win_height):
            stdscr.addch(win_y + i, win_x, curses.ACS_VLINE, curses.color_pair(1))
            stdscr.addch(win_y + i, win_x + win_width - 1, curses.ACS_VLINE, curses.color_pair(1))
        stdscr.addch(win_y, win_x, curses.ACS_ULCORNER, curses.color_pair(1))
        stdscr.addch(win_y, win_x + win_width - 1, curses.ACS_URCORNER, curses.color_pair(1))
        stdscr.addch(win_y + win_height - 1, win_x, curses.ACS_LLCORNER, curses.color_pair(1))
        stdscr.addch(win_y + win_height - 1, win_x + win_width - 1, curses.ACS_LRCORNER, curses.color_pair(1))
        # Заголовок
        title = 'Распределение характеристик'
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(win_y + 1, win_x + (win_width - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        # Список характеристик
        for i, key in enumerate(stat_keys):
            y = win_y + 3 + i
            x = win_x + 4
            if i == pos:
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                marker = '>'
            else:
                stdscr.attron(curses.color_pair(2))
                marker = ' '
            stdscr.addstr(y, x, f'{marker} {key}: {stats[key]}')
            if i == pos:
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            else:
                stdscr.attroff(curses.color_pair(2))
        # Осталось очков
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(win_y + 9, win_x + 4, f'Осталось очков: {points}'[:win_width-8])
        # Подсказка (разбить на две строки)
        hint1 = '↑/↓ — выбрать, → — добавить, ← — убрать,'
        hint2 = 'Enter — подтвердить'
        stdscr.addstr(win_y + 10, win_x + 2, hint1[:win_width-4])
        stdscr.addstr(win_y + 11, win_x + 2, hint2[:win_width-4])
        stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord('k'), ord('K')]:
            pos = (pos - 1) % len(stat_keys)
        elif key in [curses.KEY_DOWN, ord('j'), ord('J')]:
            pos = (pos + 1) % len(stat_keys)
        elif key in [curses.KEY_RIGHT, ord('l'), ord('L')]:
            if points > 0:
                stats[stat_keys[pos]] += 1
                points -= 1
        elif key in [curses.KEY_LEFT, ord('h'), ord('H')]:
            if stats[stat_keys[pos]] > 1:
                stats[stat_keys[pos]] -= 1
                points += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            if points == 0:
                break
        elif key == 27:  # ESC
            if points == 0:
                break
    return stats


def main():
    """Main entry point for the Babka RPG game."""
    db.init_db()

    def pre_game(stdscr):
        """Handle the pre-game menu and return a Babka object."""
        while True:
            choice = curses_main_menu(stdscr)
            if choice == 0:  # Начать игру
                name = curses_input_name(stdscr)
                stats = curses_allocate_stats(stdscr)
                babka_stats = Stats(
                    hp=100,
                    strength=stats['Сила'],
                    dexterity=stats['Ловкость'],
                    luck=stats['Удача'],
                    damage=2,
                    defence=stats['Защита'],
                )
                babka = Babka(f.create_name(name), stats=babka_stats)
                # Приветственный текст с предысторией

                def show_intro(stdscr, babka):
                    intro = [
                        f'Babka {GAME_VERSION}',
                        '',
                        f'Сегодня бабка {babka.name} проснулась не в духе.',
                        'Всю ночь ей снились странные сны о том, как молодёжь шумит под окнами,',
                        'пенсия задерживается, а в магазине снова нет её любимых пряников.',
                        'В этот день она решила: хватит это терпеть! Пора навести порядок в этом дворе,',
                        'разобраться с наглыми соседями и показать всем, кто тут главный!',
                        '',
                        'Нажмите любую клавишу, чтобы начать приключение...'
                    ]
                    stdscr.clear()
                    h, w = stdscr.getmaxyx()
                    y = max(2, h // 2 - len(intro) // 2)
                    for line in intro:
                        stdscr.addstr(y, max(2, w // 2 - len(line) // 2), line)
                        y += 1
                    stdscr.refresh()
                    stdscr.getch()
                show_intro(stdscr, babka)
                return babka
            elif choice == 1:  # Опции
                curses_options_menu(stdscr)
            elif choice == 2:  # Загрузить игру
                babka = curses_load_menu(stdscr)
                if babka:
                    return babka
            elif choice == 3:  # Выход
                exit(0)
    while True:
        babka = curses.wrapper(pre_game)
        try:
            curses.wrapper(curses_menu_game_loop, babka)
        except KeyboardInterrupt:
            break  # Allow Ctrl+C to exit gracefully
        except Exception as e:
            if str(e) == 'GAME_OVER_RETURN_TO_MENU':
                continue  # Вернуться в главное меню
            raise  # Re-raise unexpected exceptions


if __name__ == "__main__":
    main()
