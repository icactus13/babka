def print_title(men_title):
    """Show pretty menu title

    Args:
        men_title (string): Menu title
    """
    print(80 * '=')
    title_len = len(men_title)
    titled = (((80 - title_len) // 2) - 1)
    if title_len % 2 == 1:
        print('-' * titled, men_title, '-' * (titled + 1))

    else:
        print('-' * titled, men_title, '-' * titled)
    print(80 * '=')


def show_menu(title, items, text1='0', text2='0', back=''):
    """ Show menu
    
    Args:
        title (string): Title text
        items (list): Menu items
        text1 (str, optional): Text after title. Defaults to 0.
        text2 (str, optional): Text after text after title. Defaults to 0.
        back (int, optional): Show back button. Defaults to 0.
        
    Return:
        int: menu choice
    """
    def print_menu():
        """ Function in function???
        """
        print_title(title)
        if text1 != '0':
            print(text1)
        if text2 != '0':
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
        if choice == 'x' and len(items) == 0:
            int_choice = -1
            loop = False
            break
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
