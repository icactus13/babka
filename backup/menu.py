from func import print_title, available_locations
from helper import locations


def show_menu(title, items):
    def print_menu():
        print_title(title)
        for idx, item in enumerate(items):
            print(idx + 1, item)
        print(80 * '-')

    loop = True
    int_choice = -1
    while loop:
        print_menu()
        choice = input('Сделай свой выбор: ')
        for i in range(1, len(items) + 1):
            if choice == i.__str__():
                int_choice = int(choice)
                loop = False
                break
        else:
            input("Неправильный выбор. Нажми энтер для продолжения...")
    return int_choice


def show_move_menu(cur_loc):
    def print_menu():
        print_title('Меню перемещения')
        print("Куда отправиться?")
        print('Текущая локация: ', locations[cur_loc])
        for i in available_locations(0, cur_loc):
            print(i, locations[i])
        print(80 * "-")
        print('x Вернуться в главное меню')

    loop = True
    int_choice = -1

    while loop:
        print_menu()
        choice = input("Выбирай: ")
        print('Ты выбрал: ', choice)
        for y in available_locations(0, cur_loc):
            if choice == y.__str__():
                int_choice = y
                loop = False
                break
            elif choice == 'x':
                loop = False
                break

        else:
            input("Неправильный выбор. Нажми энтер для продолжения...")
    return int_choice


def show_npc_menu(title, items):
    def print_menu():
        print_title(title)
        for idx, item in enumerate(items):
            print(idx + 1, item)
        print('x Вернуться в главное меню')
        print(80 * '-')

    loop = True
    int_choice = -1

    while loop:
        print_menu()
        choice = input('Сделай свой выбор: ')
        for i in range(1, len(items) + 1):
            if choice == i.__str__():
                int_choice = int(choice)
                loop = False
                break
            elif choice == 'x':
                loop = False
                break
        else:
            input("Неправильный выбор. Нажми энтер для продолжения...")
    return int_choice

