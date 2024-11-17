"""
Functions
"""
from random import randint
import markovify
from db import save_babka
import helper
from menu import print_title
from name_gen import get_name


def print_message(message: str, msg_type='info') -> None:
    """
    Print a message with some formatting.

    Args:
        message (str): The message to print.
        type (str): The type of message (info, fight, system).
    """
    if msg_type == 'info':
        print(f"\033[94m{message}\033[0m")
    elif msg_type == 'fight':
        print(f"\033[91m{message}\033[0m")
    else:
        print(f"\033[92m[SYSTEM EVENT] {message}\033[0m")


def confirm(answer):
    """Yes/no function

    Args:
        answer (string): Your answer

    Returns:
        bool:
    """
    return answer.lower() == 'y' if isinstance(answer, str) else confirm(answer)


def available_locations(loc1, loc2, names=False):
    """ Return list of available locations

    Args:
        loc1 (int): Current location
        loc2 (int): ?
        names (bool, optional): return the name of the location, not its number. Defaults to False.

    Returns:
        string: Location name or nubmer
    """
    locs = [i for i in helper.locations if i not in (loc1, loc2)]
    if names:
        return [helper.locations[i][0] for i in locs]
    return [helper.locations[i][1] for i in locs]


def create_name():
    """Create Babka's name
    if no name is specified, the function will generate a random name.

    Returns:
        string: Generated Babka's name
    """
    print_title('Создание бабки')
    print('Если имя не будет введено, то будет сгенерировано случайное имя.')
    name = input('Введи имя: ')
    if not name:
        print('Хорошо, я сгенерирую рандомное имя для бабки...')
        if helper.options.get('gen_names') == "neuro":
            name = get_name('female')
        else:
            name = random_name('female')
        print('Имя бабки: ', name)
    if type(name) is str:
        print("Хорошо!")
    return name


def calc_damage(att, dfn, luck=0):
    """Calculate damage

    Args:
        att (int): Attack points
        dfn (int): defence point
        luck (int): lucky points, default 0

    Returns:
        int: Damage points
    """
    return abs(att - att * int((dfn / 100)) + luck)


def calc_exp(babka_level, npc_level):
    """Calculate experience gained from NPC

    Args:
        babka_level (int): Babka level
        npc_level (int): NPC level

    Returns:
        int: Experience gained
    """
    return round(100 * (10 + npc_level - babka_level)/(7 + babka_level))


def random_name(gender):
    """ Random name function

    Args:
        gender (string): Gender

    Returns:
        string: Random name
    """
    name = ''
    if gender == 'female':
        num = len(helper.female_names)
        name = helper.female_names[randint(0, num - 1)]
    elif gender == 'male':
        num = len(helper.male_names)
        name = helper.male_names[randint(0, num - 1)]
    return name


def save_game(babka):
    """
    Save babka to the database

    Args:
        babka (Babka): Babka to save
    """
    save_babka(
        name=babka.name,
        level=babka.level,
        hp=babka.stats.hp,
        strength=babka.stats.strength,
        dexterity=babka.stats.dexterity,
        luck=babka.luck,
        inventory=babka.inventory,
        damage=babka.damage,
        defence=babka.defence,
        exp=babka.exp,
        location=babka.location,
        maxhp=babka.maxhp
    )
    print_message(f'Бабка {babka.name} успешно сохранена.', msg_type='system')


def generate_phrase():
    """
    Generate a random phrase using the Markov chain model from markov.json.

    Returns:
        str: A random phrase of length up to 50 characters.
    """
    with open('./markov.json', encoding='utf-8') as f:
        text = f.read()
    text_model_a = markovify.Text.from_json(text)
    return text_model_a.make_short_sentence(50)
