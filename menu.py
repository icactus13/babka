from func import print_title


def show_menu(title, items, text1=0, text2=0, back=0):  # выводит меню, параметр back=1 рисует кнопку назад
    def print_menu():
        print_title(title)
        if text1 != 0:
            print(text1)
        if text2 != 0:
            print(text2)
        for idx, item in enumerate(items):
            print(idx + 1, item)
        if back == 1:
            print('x Вернуться назад')
        print(80 * '-')

    loop = True
    int_choice = -1
    while loop:
        print_menu()
        choice = input('Сделай свой выбор: \n')
        for i in range(1, len(items) + 1):
            if choice == i.__str__():
                int_choice = int(choice)
                loop = False
                break
            elif choice == 'x':
                int_choice = -1
                loop = False
                break
        else:
            input("Неправильный выбор. Нажми энтер для продолжения...\n")
    return int_choice
