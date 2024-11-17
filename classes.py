"""
Class module
"""

import random
from time import sleep
from random import randint, choice
import helper
from name_gen import get_name
import functions as func


class Location:
    """
    A class representing a location.
    """
    def __init__(self, location_num: int, npc: dict = None):
        """Initialize a new Location object.

        Args:
            name (str): The name of the location.
            description (str): The description of the location.
            npc (list, optional): A list of NPCs in the location. Defaults to None.
        """
        self.location_num = location_num
        self.npc = npc

    def generate_location(self, level):
        """ Location generator

        Args:
            level (int): level
            location (int): Location number
        """
        npcs = {}
        if self.location_num != 1:
            num = 1
            for _ in range(1, randint(self.location_num, self.location_num + 5)):
                npc_level = randint(level - 2, level + 2) if level > 2 else level
                npcs[num] = NPC(
                    name='NPC',
                    gender=choice(helper.gender),
                    level=npc_level,
                    stats=Stats(
                        hp=10,
                        strength=randint(npc_level + 1, npc_level + 3),
                        dexterity=randint(npc_level + 1, npc_level + 3),
                        luck=randint(npc_level + 1, npc_level + 3),
                        damage=randint(npc_level + 1, npc_level + 3),
                        defence=randint(npc_level + 1, npc_level + 3),
                    ),
                    mood=helper.mood[randint(1, 3)],
                    location=self.location_num
                )
                func.print_message(
                    f'NPC #{num}: {npcs[num].name} успешно создан.', msg_type='system'
                )
                num = num + 1
                sleep(0.2)
            self.npc = npcs
        else:
            print('Ты дома, тут никого нет.')

    def about(self):
        """Print the location's stats.

        This method prints the location's name and description.

        """
        print(f"Текущая локация: {helper.locations[self.location_num][0]}")

    def get_npc(self) -> dict:
        """Return the list of NPCs in the current location.

        Returns:
            dict: A dictionary where NPC's name is the key and NPC object is the value.
        """
        return self.npc

    def spawn_weapon(self, level):
        """Spawn a new weapon on location.

        Args:
            level (int): The babka's level.

        Returns:
            int: The number of the spawned weapon.
        """
        chance = randint(1, 1)  # 5 - babka.luck)
        weapons = len(helper.babka_weapon)
        if chance == 1:
            if self.location_num + level >= weapons:
                random_num = weapons
            else:
                random_num = self.location_num + level
            item = randint(1, random_num)
            print(f'Ого, вот это да, смотри что валяется: {helper.babka_weapon[item][0]}!')
            return item


class Stats:
    """
    A class representing the statistics of a human.
    """
    def __init__(
        self,
        hp: int,
        strength: int,
        dexterity: int,
        luck: int,
        damage: int = 0,
        defence: int = 0,
        exp: int = 0
    ):
        """Initialize a new Stats object.

        Args:
            hp (int): The health points of the human.
            strength (int): The strength of the human.
            dexterity (int): The dexterity of the human.
            luck (int): The luck of the human.
        """
        self.hp = hp
        self.strength = strength
        self.dexterity = dexterity
        self.luck = luck
        self.damage = damage
        self.defence = defence
        self.exp = exp


class Human:
    """
    A class representing a human being.
    """
    def __init__(self, name, gender=None, level=1, location=None, stats=None):
        """Initialize a new Human object.

        Args:
            name (str): The name of the human.
            gender (str, optional): The gender of the human. Defaults to None.
            level (int, optional): The level of the human. Defaults to 1.
            location (str, optional): The location of the human. Defaults to an empty string.
            stats (Stats, optional): The statistics of the human. Defaults to None.
        """
        self.name = name
        self.gender = gender
        self.location = location
        self.level = level
        self.stats = stats or Stats(
            hp=10,
            strength=randint(self.level + 3, self.level + 7),
            dexterity=randint(self.level + 3, self.level + 7),
            luck=randint(self.level + 1, self.level + 3),
            damage=2,
            defence=2
        )

    def talk(self, phrase):
        """Print a phrase as if it was said by the human.

        Args:
            phrase (str): The phrase to be printed.
        """
        print(f'{self.name}: {phrase}')


class Babka(Human):
    """
    A class representing a babka.

    This class inherits from the Human class.
    """
    def __init__(
        self,
        name,
        gender="female",
        level=1,
        stats=None,
    ):
        """Initialize a new Babka object.

        Args:
            name (str): The name of the babka.
            gender (str, optional): The gender of the babka. Defaults to "female".
            level (int, optional): The level of the babka. Defaults to 1.
            stats (Stats, optional): The statistics of the babka. Defaults to None.
        """
        super().__init__(name, gender, level, location=None, stats=stats)
        self.level = level
        self.location = 1
        self.stats = stats or Stats(
            hp=10,
            strength=randint(self.level + 3, self.level + 7),
            dexterity=randint(self.level + 3, self.level + 7),
            luck=randint(self.level + 1, self.level + 3),
            damage=2,
            defence=2
        )
        self.weapon = None
        self.maxhp = 20
        self.inventory = [1]
        self.calculate_stats()

    def calculate_stats(self):
        """
        Calculate the human's stats based on their characteristics and level.
        """
        if not self.weapon:
            self.stats.damage = self.stats.strength + 1
        else:
            self.stats.damage = self.stats.strength + helper.babka_weapon[self.weapon][1]
        self.stats.defence = int((self.stats.strength // 2) * (self.stats.dexterity // 1.5))
        self.stats.hp = self.level * 10

    def about(self):
        """Print the babka's stats.

        This method prints the babka's name, gender, level, hit points, strength,
        dexterity, luck, weapon, damage, defence, experience, current location,
        and inventory.
        """

        print(
            f"Имя: {self.name}\n"
            f"Пол: {'мужской' if self.gender == 'male' else 'женский'}\n"
            f"Уровень: {self.level}\n"
            f"HP: {self.stats.hp}\n"
            f"Сила: {self.stats.strength}\n"
            f"Ловкость: {self.stats.dexterity}\n"
            f"Удача: {self.stats.luck}\n"
            f"Оружие: {helper.babka_weapon.get(self.weapon, ['нет', 0])[0]}\n"
            f"Наносимый урон: {self.stats.damage}\n"
            f"Защита: {self.stats.defence}\n"
            f"Опыт: {self.stats.exp}\n"
            f"Текущая локация: {helper.locations[self.location][1]}"
        )
        print("Инвентарь:")
        for i in self.inventory:
            print(f"- Оружие: {helper.babka_weapon[i][0]}")
            print(f"  Урон: {helper.babka_weapon[i][1]}")
        print('-' * 80)

    def smart_talk(self):
        """
        Print a randomly generated phrase spoken by the babka.

        This method uses the `generate_phrase` function to create a random phrase
        and prints it with the babka's name as the speaker.

        Returns:
            None
        """
        print(f'{self.name}: {func.generate_phrase()}')

    def levelup(self):
        """
        Level up the babka by increasing its attributes.

        This method increments the babka's level, updates maximum and current
        health points, increases strength and dexterity, and potentially
        increments luck every 5 levels if it is below 10. It then recalculates
        the babka's stats and prints the updated information.

        Returns:
            None
        """

        self.level += 1
        self.maxhp = 10 + 10 * self.level
        self.stats.hp = self.maxhp
        self.stats.strength += 1
        self.stats.dexterity += 1
        if self.stats.luck < 10 and self.level % 5 == 0:
            self.stats.luck += 1
        self.calculate_stats()
        print(f'Бабка {self.name} достигла нового уровня: {self.level}!')
        self.about()

    def move(self, destination):
        """ Move to another location

        Args:
            current_location (int): Current location number
            destination (int): Location number where we are going

        """

        if destination == self.location:
            print('Текущая локация:', helper.locations[self.location][0])
            print('Бабка уже находится в этой локации.')
        else:
            print(f'Бабка {self.name} перемещается...')

            if self.location > destination:

                for _ in range(0, 2 * (self.location - destination)):
                    print('.', end="", flush=True)
                    sleep(0.2)
                print('')

            for _ in range(0, 2 * (destination - self.location)):
                print('.', end="", flush=True)
                sleep(0.2)

            print('')
            print('Текущая локация:', helper.locations[destination][0])

            self.location = destination

    def get_new_weapon(self, weapon):
        """ Add new weapon in Babka's inventory

        Args:
            babka (class): Your Babka
            weapon (int): Spawned weapon
        """

        weapon_list = {}

        for w in self.inventory:
            weapon_list[w] = helper.babka_weapon[w][0]

        if helper.babka_weapon[weapon][0] in weapon_list.values():
            print('Такая штука у тебя уже есть, эх..')
        else:
            self.inventory.append(weapon)
            print('Теперь у тебя есть:', helper.babka_weapon[weapon][0])

    def attack(self, victim):
        chance = randint(1, self.stats.luck)
        func.print_message(f'Бабка {self.name} атакует!', msg_type='fight')
        sleep(1)
        crit = random.random()
        damage = func.calc_damage(self.stats.damage, victim.stats.defence, abs(chance - 5))
        if crit < 0.1 + self.stats.luck * 0.01:
            damage *= 2
            func.print_message(f'Бабка {self.name} лютует и наносит {damage} урона', msg_type='fight')
        else:
            func.print_message(f'Бабка {self.name} наносит {damage} урона', msg_type='fight')
        victim.stats.hp -= damage
        func.print_message(f'{victim.name} HP: {victim.stats.hp}', msg_type='info')
        victim.say()
        sleep(1)
        return victim.stats.hp <= 0


class NPC(Human):
    """
    A class representing a non-player character (NPC).
    """

    def __init__(
        self,
        name='NPC',
        gender=None,
        level=1,
        stats=None,
        mood='Нейтральный',
        location=None
    ):
        """
        Initialize a new NPC object.

        Args:
            name (str): The name of the NPC. Defaults to 'NPC'.
            gender (str): The gender of the NPC. Defaults to None.
            level (int): The level of the NPC. Defaults to 1.
            stats (Stats): The stats of the NPC. Defaults to None.
            mood (str): The mood of the NPC. Defaults to 'Нейтральный'.
            location (str): The location of the NPC. Defaults to None.
        """

        super().__init__(name, gender, level, location=location, stats=stats)

        self.stats = stats or Stats(
            hp=10,
            strength=randint(self.level + 3, self.level + 7),
            dexterity=randint(self.level + 3, self.level + 7),
            luck=randint(self.level + 1, self.level + 3),
            damage=2,
            defence=2,
            exp=0
        )

        self.name = self.gen_name(gender)
        self.inventory = []
        self.mood = mood
        self.location = None
        self.inventory.append(randint(1, len(helper.weapon)))
        self.weapon = ''
        self.patience = 100
        self.calculate_stats()

    def about(self):
        """Print the NPC's stats.

        This method prints the NPC's name, gender, level, and hit points.

        """

        print(
            f"Имя: {self.name}\n"
            f"Пол: {'мужской' if self.gender == 'male' else 'женский'}\n"
            f"Уровень: {self.level}\n"
            f"HP: {self.stats.hp}"
        )

    def calculate_stats(self):
        """Calculate the NPC's combat stats.

        This method calculates the NPC's damage, defence, and hit points based on
        their current weapon, strength, dexterity, and level.

        Args:
            None

        Returns:
            None
        """

        if self.weapon == '':
            self.damage = int(self.stats.strength) + 1
        else:
            self.damage = self.stats.strength + int(helper.weapon[self.weapon][1])

        self.defence = int((self.stats.strength / 2)) * \
            int((self.stats.dexterity / 1.5))
        self.stats.hp = 10 * self.level

    def gen_name(self, gender):
        """Generate a random name for an NPC based on gender.

        Args:
            gender (str): The gender of the NPC, either 'male' or 'female'.

        Returns:
            str: A random name for the NPC.
        """
        if helper.options.get('gen_names') == "neuro":
            return get_name(gender)
        return func.random_name(gender)

    def say(self):
        """Make the NPC say a random phrase based on their mood.

        Args:
            None

        Returns:
            None
        """
        phrases = {
            'Добрый': helper.happy_phrases,
            'Нейтральный': helper.neutral_phrases,
            'Злой': helper.angry_phrases
        }[self.mood]
        self.talk(choice(phrases))

    def nervous(self, kak):
        """Change NPC's mood if they are not already angry.

        If kak is 1, the NPC loses 10 patience. If kak is not 1, the NPC
        loses 40 patience. If the NPC's patience reaches 0, their mood is
        changed to the previous mood in the helper.mood dictionary.

        Args:
            kak (int): 1 if the NPC loses 10 patience, any other value if
                the NPC loses 40 patience.

        Returns:
            None
        """
        if self.mood != 'Злой':
            if kak == 1:
                print(self.name, 'м?')
                self.patience = self.patience - 10
                print('Терпение', self.name, ': ', self.patience)
            else:
                print(self.name, 'эй!')
                self.patience = self.patience - 40
                print('Терпение', self.name, ': ', self.patience)
            if self.patience <= 0:
                self.patience = 100
                for k, m in helper.mood.items():
                    if m == self.mood:
                        self.mood = helper.mood[k - 1]
                print(self.name, 'изменил настроение на', self.mood)

    def get_weapon(self):
        """Make the NPC draw a weapon from their inventory.

        If the NPC has no weapon equipped, they draw the first one in their
        inventory. If they already have a weapon equipped, they hold it
        tightly and ready themselves for battle.

        Args:
            None

        Returns:
            None
        """
        if self.weapon == '':
            print(self.name, 'достает', helper.weapon[self.inventory[0]][0])
            self.weapon = self.inventory[0]
        else:
            print(
                self.name, 'крепко сжимает в руке', helper.weapon[self.weapon][0][0]
            )
        self.calculate_stats()

    def hide_weapon(self):
        """Make the NPC hide their weapon.

        If the NPC has a weapon equipped, they put it away and remove it from
        their inventory. If they don't have a weapon equipped, this method does
        nothing.

        Args:
            None

        Returns:
            None
        """
        if self.weapon != '':
            print(self.name, 'убирает', helper.weapon[self.inventory[0]][0])
            self.weapon = ''
            self.calculate_stats()

    def attack(self, babka):
        func.print_message(f'{self.name} атакует!', msg_type='fight')
        sleep(1)
        damage = func.calc_damage(self.stats.damage, babka.stats.defence)
        chance = randint(1, 15 - babka.stats.luck)
        if chance == 1:
            func.print_message(f'Бабка {babka.name} ловко уклонилась от удара', msg_type='fight')
        else:
            func.print_message(f'{self.name} наносит {damage} урона', msg_type='fight')
            babka.stats.hp -= damage
        func.print_message(f'{babka.name} HP: {babka.stats.hp}', msg_type='info')
        sleep(1)
        return babka.stats.hp <= 0
