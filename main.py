# coding=utf-8
from menu import print_title, show_menu
import helper
import func
from random import randint
import sys

npc = {}
location_npc = []


def move(babka, current_location, destination):
    """ Move to another location

    Args:
        babka (class): Your babka
        current_location (int): Current location number
        destination (int): Location number where we are going

    Returns:
        none
    """
    global npc
    if destination == -1:
        print('Текущая локация:', helper.locations[current_location][0])
    else:
        print('Бабка', babka.name, 'перемещается...')
        print('Текущая локация:', helper.locations[destination][0])
        npc = func.loc_gen(babka, destination)
        return destination


def who_on_location(loc_npc, location):
    """ Show NPC on current location

    Args:
        loc_npc ([type]): ?
        location (int): Current location number

    Returns:
        [type]: [description]
    """
    units = []
    # for y in [x for x in range(1, num) if loc_npc[x].location == location]:
    for y in [x for x in loc_npc if loc_npc[x].location == location]:
        units.append(y)
    return units


def fight(victim):
    """ Fight function

    Args:
        victim (int): NPC number
    """
    npc[victim].terpenie = -100
    npc[victim].mood = 'Злой'
    npc[victim].get_weapon()
    print_title(Babka.name + ' vs ' + npc[victim].name)
    print(Babka.name, 'HP: ', Babka.hp, '|', npc[victim].name, ' HP: ', npc[victim].hp)
    print(Babka.name, 'Оружие: ', helper.babka_weapon[Babka.weapon][0], '|', npc[victim].name, ' Оружие: ', helper.weapon[npc[victim].weapon][0])
    print_title('Prepare to fight!')
    input("Нажми enter для продолжения...")
    while npc[victim].hp != 0 or npc[victim].hp > 0:
        if Babka.hp <= 0:
            print('Ты сдох!')
            print('Игра окончена')
            func.sleep(3)
            exit(0)
        npc[victim].say()
        chance = randint(1, 15 - Babka.luck)
        print('Бабка', Babka.name, 'атакует!')
        damage = func.calc_damage(Babka.damage, npc[victim].defence, chance - 5)
        func.sleep(1)
        print('Бабка', Babka.name, 'наносит', damage, 'урона')
        npc[victim].hp = npc[victim].hp - damage
        print(npc[victim].name, 'HP: ', npc[victim].hp)
        npc[victim].say()
        func.sleep(0.5)
        if npc[victim].hp <= 0:
            break
        print(npc[victim].name, 'атакует!')
        damage = func.calc_damage(npc[victim].damage, Babka.defence)
        func.sleep(1)
        if chance == 1:
            print('Бабка', Babka.name, 'ловко уклонилась от удара')
        else:
            print(npc[victim].name, 'наносит ', damage, 'урона')
            Babka.hp = Babka.hp - damage
        print(Babka.name, 'HP:', Babka.hp)
        func.sleep(0.5)
    print(npc[victim].name, '- Ну ты и сука, я умираю, ааааааааааАААААааааа.')
    exp = func.calc_exp(Babka.level, npc[victim].level)
    npc.pop(victim)
    Babka.exp = Babka.exp + exp
    print('Бабка', Babka.name, 'получает', exp ,'очков опыта.')
    print('Теперь у нее', Babka.exp, 'очков опыта, так держать')
    Babka.smart_talk()
    input("Нажми enter для продолжения...")
    loop()


def move_to_npc(loc_npc):
    """ Go to the NPC at the current location

    Args:
        loc_npc (list?): NPC list
    """
    func.clear_screen()
    print_title('К кому?')
    npc_list = []
    for i in loc_npc:
        npc_list.append(npc[i].name)
    menu_action = show_menu('Выбери жертву', npc_list, back=1)
    loop1 = True
    while loop1:
        if menu_action == 'x':
            exit(0)
        else:
            act_npc(loc_npc[menu_action - 1])


def act_npc(victim):
    """ Interaction with NPC

    Args:
        victim (int?): NPC number
    """
    print('Твоя жертва:', npc[victim].name)
    print('Настроение жертвы:', npc[victim].mood)
    npc_loop = True
    while npc_loop:
        if npc[victim].mood == 'Злой':
            print(npc[victim].name, '- Ну пизда тебе, старая!')
            Babka.smart_talk()
            npc_loop = False
            fight(victim)
        else:
            act_loop = True
            while act_loop:
                if npc[victim].mood == 'Злой':
                    act_loop = False
                act = show_menu('Взаимодействие с жертвой', helper.npc_menu)
                npc[victim].say()
                if act == 1:
                    Babka.talk(helper.grumble_phrases[func.randint(0, helper.grumble_phrases.__len__() - 1)])
                    npc[victim].nervous(1)
                elif act == 2:
                    print('Бабка', Babka.name, 'смачно плюет в', npc[victim].name)
                    npc[victim].nervous(2)
                elif act == 3:
                    print("Ты уверен что хочешь атаковать", npc[victim].name, '?')
                    if func.confirm(input('y/n? ')):
                        act_loop = False
                        npc_loop = False
                        fight(victim)
                elif act == 4:
                    act_loop = False
                    pass


def show_npc(loc_npc):
    """ Print list of NPC

    Args:
        loc_npc (list?): NPC list
    """
    func.clear_screen()
    print('В текущей локации находятся:')
    for i in loc_npc:
        print('NPC ', i)
        print(npc[i].about())
        print('Настроение:', npc[i].mood, '\n')
    input("Нажми enter для продолжения...")


def bench_relax():
    """ Relax on bench
    """
    relaxing = True
    hp = 10 * Babka.level
    while relaxing:
        relax = show_menu("На лавочке", helper.bench_menu, back=1)
        if relax == 1:
            Babka.hp += 2
            print(Babka.name, ' hp: ', Babka.hp)
            if Babka.hp - hp >= 10:
                Babka.talk('Сколько ж сидеть то можно!')
                relaxing = False
        elif relax == 2:
            Babka.hp += 10
            print(Babka.name, ' hp: ', Babka.hp)
            if Babka.hp - hp >= 20:
                Babka.talk('Тошнит уже от этих семечек')
                relaxing = False
        elif relax == -1:
            relaxing = False


def get_weapon_menu(babka):
    """ Show weapon menu

    Args:
        babka (class): Your babka
    """
    weapon_list = {}
    for i in babka.inventory:
        weapon_list[i] = helper.babka_weapon[i]
    babka.weapon = babka.inventory[show_menu('Выбери оружие', weapon_list.values())-1]
    babka.calculate_stats()


def action_menu():
    """ Show action menu

    Returns:
        True, if no action is selected
        Call the appropriate function for the action
    """
    #func.clear_screen()
    action = show_menu("Меню действия", helper.action_menu)
    if action == 1:
        show_npc(who_on_location(npc, Babka.location))
    elif action == 2:
        move_to_npc(who_on_location(npc, Babka.location))
    elif action == 3:
        bench_relax()
    elif action == 4:
        get_weapon_menu(Babka)
    else:
        return True


def move_menu():
    """ Show move menu
    """
    print('Текущая локация:', helper.locations[Babka.location][0])
    menu_choice = show_menu("Меню перемещения", func.available_locations(Babka.location, Babka.location, names=True))
    destination = func.available_locations(Babka.location, Babka.location)[menu_choice - 1]
    Babka.location = move(Babka, Babka.location, destination)
    func.spawn_weapon(Babka)
    input("Нажми enter для продолжения...")


def loop():
    """ Main loop

    Returns:
        something
    """
    func.clear_screen()
    Babka.hp = Babka.hp + 1
    if Babka.exp >= (100 * Babka.level) * 2:
        Babka.levelup()
        print('Бабка', Babka.name, 'достигла нового уровня:', Babka.level, '!')
    choose = show_menu("Главное меню", helper.main_menu)
    if choose == 1:
        Babka.about()
        input("Нажми enter для продолжения...")
    elif choose == 2:
        move_menu()
    elif choose == 3:
        action_menu()
    elif choose == 4:
        Babka.grumble()
    elif choose == 5:
        func.save_babka(Babka)
        print('Бабка', Babka.name, 'была сохранена.')
        input("Нажми enter для продолжения...")
    elif choose == 6:
        print("Ты уверен что хочешь выйти из игры?")
        if func.confirm(input('y/n? ')):
            print('Бабка была уничтожена!')
            print('Ты не смог спасти этот мир!')
            func.sleep(2)
            exit(0)
        else:
            return loop()
    return loop()


if __name__ == "__main__":
    try:
        func.intro()
        start_menu = True
        while start_menu:
            """ Main menu loop
            """
            func.create_table()
            menu = show_menu('Бабка 2.0', helper.start_menu)
            if menu == 1:
                Babka = func.Babka(func.create_name())
                print('Бабка', Babka.name, 'создана.')
                print('-' * 80)
                Babka.about()
                input("Нажми enter для продолжения...")
                #func.sleep(1)
                print('\n\nТы просыпаешься в своей квартире. Воняет сыростью и плесенью.')
                print('Оглядываешь комнату, все на месте, все как всегда.')
                print('Поганое настроение... Что ж пора вставать.')
                input("Нажми enter для продолжения...")
                start_menu = False
                loop()
            elif menu == 2:
                func.clear_screen()
                choose_babka = show_menu(
                    'Загрузка бабки', func.load_babkas(), back=1)
                if choose_babka != -1:
                    Babka = func.load_babka(choose_babka)
                    print('Бабка ', Babka.name, 'загружена.')
                    print('-' * 80)
                    Babka.about()
                    input("Нажми enter для продолжения...")
                    start_menu = False
                    loop()
            elif menu == 3:
                opts = show_menu('Настройки', helper.name_gen_menu, back=1)
                if opts == 2:
                    func.gen_names = 'neuro'
                else:
                    func.gen_names = 'norm'
            else:
                print("Ты уверен что хочешь выйти из игры?")
                if func.confirm(input('y/n? ')):
                    print('Ты не смог спасти этот мир!')
                    start_menu = False
                    exit(0)
                else:
                    print('Правильно, оставайся с нами')
    except KeyboardInterrupt:
        sys.exit()
