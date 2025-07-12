# coding=utf-8
"""
Main module
"""

import locale
import curses
from curses_menu import curses_menu_game_loop
from classes import Babka
import functions as f
import helper
import db


def curses_input_name(stdscr):
    """Prompt the user for Babka's name using curses input."""
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, 'Введите имя бабки (или оставьте пустым для случайного): ')
    stdscr.refresh()
    encoding = locale.getpreferredencoding()
    name = stdscr.getstr(3, 2, 30).decode(encoding, errors='replace').strip()
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
    """Display the load game menu and return the loaded Babka object or None."""
    saves = db.get_saves()
    if not saves:
        stdscr.clear()
        stdscr.addstr(2, 2, 'Нет сохранённых бабок. Нажмите любую клавишу...')
        stdscr.refresh()
        stdscr.getch()
        return None
    stdscr.clear()
    stdscr.addstr(2, 2, 'Выберите сохранение:')
    for i, name in enumerate(saves):
        stdscr.addstr(4 + i, 4, f'{i+1}. {name}')
    stdscr.addstr(4 + len(saves), 2, 'Введите номер и нажмите Enter: ')
    stdscr.refresh()
    while True:
        try:
            choice = int(stdscr.getstr(4 + len(saves), 32, 2).decode('utf-8').strip())
            if 1 <= choice <= len(saves):
                break
        except (ValueError, UnicodeDecodeError):
            pass
        stdscr.addstr(5 + len(saves), 2, 'Ошибка ввода. Попробуйте снова.')
        stdscr.refresh()
    babka_data = db.get_babka_from_db(choice)
    if not babka_data:
        stdscr.clear()
        stdscr.addstr(2, 2, 'Ошибка загрузки сохранения. Нажмите любую клавишу...')
        stdscr.refresh()
        stdscr.getch()
        return None
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


def curses_main_menu(stdscr):
    """Display the main menu and return the selected option index."""
    menu = [
        'Начать игру',
        'Опции',
        'Загрузить игру',
        'Выход',
    ]
    pos = 0
    stdscr.keypad(True)
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, 'Babka 2.0 — Главное меню')
        for i, item in enumerate(menu):
            marker = '>' if i == pos else ' '
            stdscr.addstr(3 + i, 4, f'{marker} {item}')
        stdscr.addstr(8, 2, '↑/↓ — выбор, Enter — подтвердить')
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord('k'), ord('K')]:
            pos = (pos - 1) % len(menu)
        elif key in [curses.KEY_DOWN, ord('j'), ord('J')]:
            pos = (pos + 1) % len(menu)
        elif key in [curses.KEY_ENTER, 10, 13]:
            return pos


def main():
    """Main entry point for the Babka RPG game."""
    db.init_db()

    def pre_game(stdscr):
        """Handle the pre-game menu and return a Babka object."""
        while True:
            choice = curses_main_menu(stdscr)
            if choice == 0:  # Начать игру
                name = curses_input_name(stdscr)
                return Babka(f.create_name(name))
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
