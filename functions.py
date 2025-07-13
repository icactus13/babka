"""
Functions
"""
from random import randint, uniform
import markovify
from db import save_babka
import helper
# from name_gen import get_name


def create_name(name=None):
    """
    Create Babka's name
    if no name is specified, the function will generate a random name.

    Args:
        name (string, optional): Babka's name

    Returns:
        string: Generated Babka's name
    """
    if not name:
        if helper.options.get('gen_names') == "neuro":
            name = helper.markov_gen.generate(gender='female')
        else:
            name = random_name('female')
    return name


def random_name(gender: str) -> str:
    """Random name function

    Args:
        gender (str): Gender, either 'female' or 'male'

    Returns:
        str: Random name
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

    This function takes a Babka object and saves its properties to the database.

    Args:
        babka (Babka): Babka to save
    """
    # Call the save_babka function from the db module to save the babka to the database
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
    # Возвращаем строку для вывода в окно событий
    return f'Бабка {babka.name} успешно сохранена!'


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


def calculate_attack_power(
    strength: int,
    weapon_damage: int,
    base_damage: int,
    victim_defence: int,
    attacker_level: int = 1,
    victim_level: int = 1,
    crit: bool = False,
    evaded: bool = False
) -> float:
    """
    Улучшенный расчет урона с учетом силы, оружия, уровня, защиты, крита, уклонения и рандомизации.
    """
    if evaded:
        return 0
    # Базовый урон
    attack = base_damage + strength * 2 + weapon_damage + attacker_level
    # Рандомизация ±10%
    attack *= uniform(0.9, 1.1)
    # Критический удар
    if crit:
        attack *= 2
    # Процентная защита
    defence_percent = min(0.7, (victim_defence + victim_level) / 200)  # максимум 70%
    attack = attack * (1 - defence_percent)
    # Минимальный урон
    if attack < 1:
        attack = 1
    return int(attack)


def calculate_defence(
    dexterity: int,
    base_defence: int,
    armor_defence: int = 0,
    level: int = 1
) -> int:
    """
    Улучшенный расчет защиты: базовая + ловкость + броня + бонус от уровня.
    """
    defence = base_defence + dexterity + armor_defence + level // 2
    return defence


def calculate_critical_hit(luck: int) -> bool:
    """
    Крит: 5% + 4% за каждую удачу, максимум 60%.
    """
    critical_chance = 5 + luck * 4
    if critical_chance > 60:
        critical_chance = 60
    roll = randint(1, 100)
    return roll <= critical_chance


def calculate_evasion_chance(defence: int, luck: int) -> bool:
    """
    Уклонение: 1% за каждые 2 защиты + 2% за удачу, максимум 60%.
    """
    evasion_chance = (defence // 2) + luck * 2
    if evasion_chance > 60:
        evasion_chance = 60
    roll = randint(1, 100)
    return roll <= evasion_chance
