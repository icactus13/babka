import menu
import helper
import func
from random import choice

num_npc = 1
npc = {}


def move(loc):
    if loc == -1:
        print('Текущая локация: ', helper.locations[Babka.location])
    else:
        print('Бабка ', Babka.name, 'перемещается...')
        tired = func.moving(Babka.location, loc, 1 - Babka.endurance/100)
        Babka.tired = tired - tired * abs(Babka.endurance/100)
        Babka.location = loc
        print('Текущая локация: ', helper.locations[Babka.location])
        print('В данной локации находятся: ')
        for y in [x for x in range(1, num_npc) if npc[x].location == Babka.location]:
            print(npc[y].name, '-', npc[y].mood)
        input("Нажми enter для продолжения...")


def fight(victim):
    npc[victim].get_weapon()
    func.print_title(Babka.name + ' vs ' + npc[victim].name)
    print(Babka.name, 'HP: ', Babka.hp, '|', npc[victim].name, ' HP: ', npc[victim].hp)
    print(Babka.name, 'Оружие: ', Babka.weapon, '|', npc[victim].name, ' Оружие: ', npc[victim].weapon)
    func.print_title('Prepare to fight!')
    input("Нажми enter для продолжения...")
    while npc[victim].hp != 0 or npc[victim].hp > 0:
        if Babka.hp <= 0:
            print('Ты сдох!')
            print('Игра окончена')
            func.sleep(3)
            exit(0)
        npc[victim].say()
        print('Бабка ', Babka.name, ' атакует!')
        damage = func.calc_damage(Babka.damage, npc[victim].defence)
        func.sleep(1)
        print('Бабка ', Babka.name, ' наносит ', damage, 'урона')
        npc[victim].hp = npc[victim].hp - damage
        print(npc[victim].name, 'HP: ', npc[victim].hp)
        npc[victim].say()
        func.sleep(0.5)
        if npc[victim].hp <= 0:
            break
        print(npc[victim].name, ' атакует!')
        damage = func.calc_damage(npc[victim].damage, Babka.defence)
        func.sleep(1)
        print(npc[victim].name, ' наносит ', damage, 'урона')
        Babka.hp = Babka.hp - damage
        print(Babka.name, 'HP: ', Babka.hp)
        func.sleep(0.5)
    print(npc[victim].name, ': Ну ты и сука, я умираю, ааааааааааАААААааааа.')
    Babka.exp = Babka.exp + 100
    print('Бабка ', Babka.name, ' получает 100 очков опыта.')
    print('Теперь у нее ', Babka.exp, ' очков опыта, так держать')
    loop()


def act2():
    npcs = []
    func.print_title('К кому?')
    for y in [x for x in range(1, num_npc) if npc[x].location == Babka.location]:
        npcs.append(npc[y].name + ' - ' + npc[y].mood)
    menu_action = menu.show_npc_menu('Выбери жертву', npcs)
    loop1 = True
    while loop1:
        if menu_action == 'x':
            exit(0)
        else:
            act_npc(menu_action)


def act_npc(victim):
    print('Твоя жертва: ', npc[victim].name)
    print('Настроение жертвы: ', npc[victim].mood)
    npc_loop = True
    while npc_loop:
        if npc[victim].mood == 'Злой':
            print(npc[victim].name, ': Ну пизда тебе, старая!')
            npc_loop = False
            fight(victim)
        else:
            act_loop = True
            while act_loop:
                if npc[victim].mood == 'Злой':
                    act_loop = False
                act = menu.show_menu('Взаимодействие с жертвой', helper.npc_menu)
                npc[victim].say()
                if act == 1:
                    Babka.talk(helper.grumble_phrases[func.randint(0, helper.grumble_phrases.__len__() - 1)])
                    npc[victim].nervous(1)
                elif act == 2:
                    print('Бабка ', Babka.name, 'смачно плюет в ', npc[victim].name)
                    npc[victim].nervous(2)
                elif act == 3:
                    print("Ты уверен что хочешь атаковать ", npc[victim].name, '?')
                    if func.confirm(input('y/n? ')):
                        act_loop = False
                        npc_loop = False
                        fight(victim)
                elif act == 4:
                    act_loop = False
                    pass


def action(act):
    if act == 1:
        act2()
    elif act == 2:
        print('Не реализовано!')
    elif act == 3:
        Babka.get_weapon()
    else:
        return True


def loop():
    choose = menu.show_menu("Главное меню", helper.main_menu)
    if choose == 1:
        func.print_title("Информация")
        Babka.about()
        input("Нажми enter для продолжения...")
    elif choose == 2:
        move(menu.show_move_menu(Babka.location))
    elif choose == 3:
        action(menu.show_menu('Меню действия', helper.action_menu))
    elif choose == 4:
        Babka.grumble()
    elif choose == 5:
        print("Ты уверен что хочешь выйти из игры?")
        if func.confirm(input('y/n? ')):
            print('Бабка была уничтожена!')
            print('Ты не смог спасти этот мир!')
            func.sleep(2)
            exit(0)
        else:
            return loop()
    return loop()


print('\n'*10)
print("Babka 2.0")
print("=" * 5, "The chosen", "=" * 5)
print('\nLoading', end="", flush=True)
func.loading(3)
intro = True
while intro:
    if menu.show_menu('Бабка 2.0', helper.start_menu) == 1:
        intro = False
        Babka = func.Babka(func.create_name())
        print('Бабка ', Babka.name, ' создана.')
        print('-' * 80)
        Babka.about()
        input("Нажми enter для продолжения...")
        print('Заселение локаций...')
        func.sleep(1)
        for i in func.available_locations(1, 2):
            func.print_title(helper.locations[i])
            for num in range(1, func.randint(i, i + 5)):
                if Babka.level <= 2:
                    npc[num_npc] = func.create_npc(i, choice(helper.gender),
                                                   func.randint(Babka.level, Babka.level + 2),
                                                   helper.mood[func.randint(1, 3)])
                else:
                    npc[num_npc] = func.create_npc(i, choice(helper.gender),
                                                   func.randint(Babka.level - 2, Babka.level + 2),
                                                   helper.mood[func.randint(1, 3)])
                #func.loading(1)
                print('NPC #', num_npc, ': ', npc[num_npc].name, ' успешно создан.')
                num_npc = num_npc + 1
        print('\n\nТы просыпаешься в своей квартире. Воняет сыростью и плесенью.')
        print('Оглядываешь комнату, все на месте, все как всегда.')
        print('Поганое настроение... Что ж пора вставать.')
        func.sleep(1)
        loop()

    else:
        print("Ты уверен что хочешь выйти из игры?")
        if func.confirm(input('y/n? ')):
            print('Ты не смог спасти этот мир!')
            intro = False
            exit(0)
        else:
            print('Правильно, оставайся с нами')
