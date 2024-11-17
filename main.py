# coding=utf-8
"""
Main module
"""

import sys
from time import sleep
from classes import Babka, Location, Stats
import helper
from menu import show_menu, print_title, intro, clear_screen
import functions as f
from db import get_babka_from_db, get_saves, save_babka


def load_game():
    """
    Load a saved babka from the database and return it as a Babka object.

    This function retrieves a list of saved babkas from the database,
    displays a menu to select one, and loads the selected babka's properties
    from the database. A Babka object is then created with the retrieved
    properties, including stats, and returned.

    Returns:
        Babka: The loaded Babka object with its properties populated from the database.
    """
    babky = get_saves()
    choose_babka = show_menu('Выбери бабку', babky)
    babka_props = get_babka_from_db(choose_babka)
    saved_babka = Babka(
        name=babka_props.get('name'),
        gender=babka_props.get('gender'),
        level=babka_props.get('level'),
        stats=Stats(
            hp=babka_props.get('hp'),
            strength=babka_props.get('strength'),
            dexterity=babka_props.get('dexterity'),
            luck=babka_props.get('luck'),
            damage=babka_props.get('damage'),
            defence=babka_props.get('defence'),
            exp=babka_props.get('exp')
        )
    )

    saved_babka.stats.hp = babka_props.get('hp')
    saved_babka.stats.strength = babka_props.get('strength')
    saved_babka.stats.dexterity = babka_props.get('dexterity')
    saved_babka.stats.luck = babka_props.get('luck')

    return saved_babka


def move_menu(babka, location):
    """
    Display the current location and allow the player to select a new location to move to.

    This function displays the current location and generates a menu of all available locations.
    The player's choice is retrieved from the menu and the babka is moved to the destination.
    The location is then updated and the new location is generated.
    If a weapon is spawned in the new location, the babka's weapon is updated.
    The function then waits for the player to press enter before continuing.

    Args:
        babka (Babka): The babka object being moved.
        location (Location): The location object being updated.
    """
    print('Текущая локация:')
    location.about()
    menu_choice = show_menu(
        "Меню перемещения", f.available_locations(babka.location, babka.location, names=True)
    )
    destination = f.available_locations(babka.location, babka.location)[menu_choice - 1]
    babka.move(destination)
    location.location_num = babka.location
    location.generate_location(babka.level)
    weapon = location.spawn_weapon(babka.level)
    if weapon:
        babka.get_new_weapon(weapon)
    input("Нажми enter для продолжения...")


def fight(victim, babka, location):
    """
    Engage in a fight between Babka and an NPC.

    This function initializes a fight scene where Babka and a selected
    NPC (victim) engage in combat. The fight continues until either
    participant's health points (HP) reach zero. The function displays
    relevant fight messages, handles attacks between Babka and the NPC,
    and updates experience points for Babka upon victory. If Babka loses,
    the game ends.

    Args:
        victim (NPC): The NPC object engaging in the fight.
        babka (Babka): The Babka object engaging in the fight.
        location (Location): The location object where the fight takes place.
    """
    victim.terpenie = -100
    victim.mood = 'Злой'
    victim.get_weapon()

    print_title(babka.name + ' vs ' + victim.name)
    f.print_message(
        f'{babka.name} HP: {babka.stats.hp} | {victim.name} HP: {victim.stats.hp}', msg_type='info'
    )

    if babka.weapon != '':
        f.print_message(
            f'{babka.name} оружие: {helper.babka_weapon[babka.weapon][0]} \
                | {victim.name} оружие: {helper.weapon[victim.weapon][0]}'
        )
    else:
        f.print_message(
            f'{babka.name} без оружия \
                | {victim.name} оружие: {helper.weapon[victim.weapon][0]}', msg_type='info'
        )

    print_title('Prepare to fight!')
    input("Нажми enter для продолжения...")

    while True:
        if babka.attack(victim):
            f.print_message(
                f'{victim.name}: Ну ты и падла, я умираю!.', msg_type='fight'
            )

            exp = f.calc_exp(babka.level, victim.level)
            babka.stats.exp += exp

            f.print_message(f'Бабка {babka.name} получает {exp} очков опыта.', msg_type='info')
            f.print_message(f'Теперь у нее {babka.stats.exp} очков опыта, так держать', msg_type='info')

            babka.smart_talk()

            break

        if victim.attack(babka):
            print('Ты сдох!')
            print('Игра окончена')
            sleep(3)
            sys.exit(0)

    # Удаление жертвы
    npc_to_del = None

    for k, v in location.npc.items():
        if v == victim:
            npc_to_del = k
            break

    location.npc.pop(npc_to_del)
    location.npc = {i: v for i, (_, v) in enumerate(location.npc.items(), start=1)}

    input("Нажми enter для продолжения...")


def interact_with_npc(victim, babka, location):
    """
    Simulates interaction between Babka and an NPC.

    This function handles user input for interacting with an NPC. The user can
    choose to either grumble at the NPC, spit at the NPC, attack the NPC, or
    leave the NPC alone. If the NPC's mood is 'Злой', the NPC will attack Babka
    and the game will enter a fight sequence. If the user chooses to attack the
    NPC, the game will also enter a fight sequence.

    Args:
        victim (NPC): The NPC object being interacted with.
        babka (Babka): The Babka object doing the interacting.
        location (Location): The location object representing where the interaction
            is taking place.
    """
    print('Твоя жертва:', victim.name)
    print('Настроение жертвы:', victim.mood)
    while True:
        if victim.mood == 'Злой':
            print(victim.name, '- Ну пизда тебе, старая!')
            babka.smart_talk()
            fight(victim, babka, location)
            break
        act = show_menu('Взаимодействие с жертвой', helper.npc_menu)
        victim.say()
        if act == 1:
            babka.talk(
                helper.grumble_phrases[f.randint(0, len(helper.grumble_phrases) - 1)]
            )
            victim.nervous(1)
        elif act == 2:
            print(f'Бабка {babka.name} смачно плюет в {victim.name}')
            victim.nervous(2)
        elif act == 3:
            print("Ты уверен что хочешь атаковать", victim.name, '?')
            if f.confirm(input('y/n?')):
                fight(victim, babka, location)
                break
        elif act == 4:
            break


def move_to_npc(npc, babka, location):
    """
    Simulates Babka moving to an NPC.

    This function displays a menu of NPCs currently at the location and allows
    the user to choose which one to move to. After choosing an NPC, the game
    enters an interaction sequence with the chosen NPC.

    Args:
        npc (dict): A dictionary of NPC objects with keys being the number of
            the NPC and values being the NPC object itself.
        babka (Babka): The Babka object performing the movement.
        location (Location): The location object representing where the NPCs
            are located.
    """
    clear_screen()
    print_title('К кому?')
    npc_list = [npc[i].name for i in npc]
    menu_action = show_menu('Выбери жертву', npc_list, back=1)
    if menu_action != 'x':
        victim = npc[menu_action]
        interact_with_npc(victim, babka, location)


def action_menu(babka, location):
    """
    Simulates Babka's action menu.

    This function displays a menu of actions that can be taken by Babka, such
    as looking at NPCs, moving to an NPC, relaxing on a bench, or getting a
    weapon from a weapon case.

    Args:
        babka (Babka): The Babka object performing the actions.
        location (Location): The location object representing where the NPCs
            are located.

    Returns:
        bool: True if the action menu is exited, False otherwise.
    """
    clear_screen()
    action = show_menu("Меню действия", helper.action_menu)
    npcs = location.get_npc()
    if action == 1:
        if npcs:
            for i in npcs.keys():
                print(f'NPC #{i}:')
                npcs[i].about()
                print(f'Настроение: {npcs[i].mood}\n')
        input("Нажми enter для продолжения...")
    elif action == 2:
        move_to_npc(npcs, babka, location)
    elif action == 3:
        bench_relax(babka)
    elif action == 4:
        get_weapon_menu(babka)
    else:
        return True


def bench_relax(babka):
    """
    Simulates Babka sitting on a bench and relaxing.

    This function displays a menu that allows Babka to choose whether to
    relax on the bench for a short or long time. Babka's health points are
    increased when relaxing on the bench. The menu is displayed in an
    infinite loop until Babka's health points reach their maximum value or
    Babka chooses to exit the menu.

    Args:
        babka (Babka): The Babka object that is relaxing.

    Returns:
        None
    """
    while True:
        clear_screen()
        relax = show_menu("На лавочке", helper.bench_menu, back=1)
        if relax in [1, 2]:
            increment = 10 if relax == 2 else 2
            babka.stats.hp = min(babka.stats.hp + increment, babka.maxhp)
            print(babka.name, ' hp: ', babka.stats.hp)
            message = 'Тошнит уже от этих семечек' if relax == 2 else 'Сколько ж сидеть то можно!'
            babka.talk(message)
            input("Нажми enter для продолжения...")
            if babka.stats.hp >= babka.maxhp:
                break
            sleep(1)
        elif relax == -1:
            break


def get_weapon_menu(babka):
    """
    Simulates Babka choosing a weapon from their inventory.

    This function displays a menu of the weapons in Babka's inventory and
    allows Babka to choose which one to equip. The chosen weapon is then
    assigned to the 'weapon' attribute of the Babka object.

    Args:
        babka (Babka): The Babka object choosing the weapon.
    """
    weapon_list = {}
    babka.about()
    for i in babka.inventory:
        weapon_list[i] = helper.babka_weapon[i]
    babka.weapon = babka.inventory[show_menu('Выбери оружие', weapon_list.values())-1]
    babka.calculate_stats()


def start_game(babka, location):
    """
    Simulates the main game loop.

    This function displays the main menu and allows the user to choose an
    action. The user can choose to view their stats, move to a new location,
    take an action, save the game, or exit the game.

    Args:
        babka (Babka): The Babka object performing the actions.
        location (Location): The location object representing where the NPCs
            are located.

    Returns:
        None
    """
    clear_screen()
    while True:
        if babka.stats.hp < babka.maxhp:
            babka.stats.hp += 1
        if babka.stats.exp >= (100 * babka.level):
            babka.levelup()
            input("Нажми enter для продолжения...")
            clear_screen()
        choose = show_menu("Главное меню", helper.main_menu)
        if choose == 1:
            babka.about()
            location.about()
            input("Нажми enter для продолжения...")
        elif choose == 2:
            move_menu(babka, location)
        elif choose == 3:
            action_menu(babka, location)
        elif choose == 4:
            save_babka(
                name=babka.name,
                level=babka.level,
                hp=babka.stats.hp,
                strength=babka.stats.strength,
                dexterity=babka.stats.dexterity,
                luck=babka.stats.luck,
                inventory=babka.inventory,
                damage=babka.stats.damage,
                defence=babka.stats.defence,
                exp=babka.stats.exp,
                location=babka.location,
                maxhp=babka.maxhp
            )
            f.print_message(f'Бабка {babka.name} была сохранена.')
        elif choose == 5:
            print('Ты уверен что хочешь выйти из игры?')
            if f.confirm(input('y/n? ')):
                print('Бабка была уничтожена!')
                print('Ты не смог спасти этот мир!')
                sys.exit(0)


def main():
    """
    Main function of the program.

    This function displays the intro message and then enters a loop where it
    displays the main menu and waits for user input. Depending on the user's
    choice, it starts a new game, loads a saved game, changes the name generation
    option, or exits the program.
    """
    intro()
    while True:
        clear_screen()
        menu = show_menu('Бабка 2.0', helper.start_menu)
        if menu == 1:
            clear_screen()
            babka = Babka(f.create_name())
            babka.about()
            print('\n\nТы просыпаешься в своей квартире. Воняет сыростью и плесенью.')
            print('Оглядываешь комнату, все на месте, все как всегда.')
            print('Поганое настроение... Что ж пора вставать.')
            input("Нажми enter для продолжения...")
            location = Location(babka.location)
            start_game(babka, location)
        elif menu == 2:
            clear_screen()
            print_title('Загрузить бабку')
            babka = load_game()
            babka.about()
            location = Location(babka.location)
            start_game(babka, location)
        elif menu == 3:
            clear_screen()
            opts = show_menu('Настройки', helper.name_gen_menu, back=1)
            if opts == 2:
                helper.options['gen_names'] = 'neuro'
            else:
                helper.options['gen_names'] = 'norm'
        else:
            clear_screen()
            print("Ты уверен что хочешь выйти из игры?")
            if f.confirm(input('y/n? ')):
                print('Ты не смог спасти этот мир!')
                sys.exit(0)
            else:
                print('Правильно, оставайся с нами')


if __name__ == '__main__':
    main()
