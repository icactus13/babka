"""
Class module
"""

from random import randint, choice
import helper
from name_gen import get_name
import functions as func
from typing import Optional


class Location:
    """
    A class representing a location.
    """
    def __init__(self, location_num: int, npc: Optional[dict] = None):
        """Initialize a new Location object.

        Args:
            name (str): The name of the location.
            description (str): The description of the location.
            npc (list, optional): A list of NPCs in the location. Defaults to None.
        """
        if npc is None:
            npc = {}
        self.location_num = location_num
        self.npc = npc

    def generate_location(self, level, babka_exp=0):
        """ Location generator

        Args:
            level (int): level
            location (int): Location number
            babka_exp (int): опыт бабки
        """
        npcs = {}
        info = []
        exp_bonus = babka_exp // 100
        # --- Новый блок: коэффициент сложности по расстоянию от дома ---
        distance = max(0, self.location_num - 1)  # Дом = 1, дальше — больше
        difficulty = 1 + distance * 0.25  # Чем дальше, тем сложнее (0.25 — шаг роста)
        if self.location_num != 1:
            num = 1
            for _ in range(1, randint(self.location_num, self.location_num + 5)):
                # Уровень NPC теперь зависит от расстояния
                npc_level = int(
                    (
                        randint(level - 2, level + 2) if level > 2 else level
                    ) * difficulty
                )
                npc_level = max(1, npc_level)
                npc_hp = int(randint(npc_level * 30, npc_level * 70) * difficulty) + exp_bonus * 10
                # --- Новый блок: диапазон оружия для NPC ---
                min_weapon = min(1 + distance, len(helper.weapon))
                max_weapon = min(
                    len(helper.weapon), int(len(helper.weapon) * (0.3 + 0.1 * distance))
                )
                if max_weapon < min_weapon:
                    max_weapon = min_weapon
                weapon_id = randint(min_weapon, max_weapon)
                mood = helper.mood[randint(1, 3)]
                # --- Модификатор характеристик по настроению ---
                if mood == 'Злой':
                    mood_coeff = 1.2
                elif mood == 'Добрый':
                    mood_coeff = 0.9
                else:
                    mood_coeff = 1.0
                npcs[num] = NPC(
                    name='NPC',
                    gender=choice(helper.gender),
                    level=int(npc_level * mood_coeff),
                    stats=Stats(
                        hp=int(npc_hp * mood_coeff),
                        strength=int(
                            randint(
                                npc_level + 1, npc_level + 3) * difficulty * mood_coeff
                            ) + exp_bonus,
                        dexterity=int(
                            randint(
                                npc_level + 1, npc_level + 3) * difficulty * mood_coeff
                            ),
                        luck=int(
                            randint(
                                npc_level + 1, npc_level + 3) * difficulty * mood_coeff
                            ),
                        damage=int(
                            randint(
                                npc_level + 1, npc_level + 3) * difficulty * mood_coeff
                            ) + exp_bonus,
                        defence=int(
                            randint(
                                npc_level + 1, npc_level + 3) * difficulty * mood_coeff
                            ) + exp_bonus,
                    ),
                    mood=mood,
                    location=self.location_num
                )
                # Назначаем оружие с учётом расстояния
                npcs[num].inventory = [weapon_id]
                npcs[num].weapon = weapon_id
                npcs[num].calculate_stats()
                info.append(
                    f'NPC #{num}: {npcs[num].name}\n'
                )
                num = num + 1
            self.npc = npcs
        else:
            info.append('Ты дома, тут никого нет.')
        return info

    def about(self) -> str:
        """Print the location's stats.

        This method prints the location's name and description.

        """
        return f"Текущая локация: {helper.locations[self.location_num][0]}"

    def get_npc(self) -> dict:
        """Return the list of NPCs in the current location.

        Returns:
            dict: A dictionary where NPC's name is the key and NPC object is the value.
        """
        return self.npc

    def spawn_weapon(self) -> int:
        """Spawn a new weapon on location.

        Args:
            level (int): The babka's level.

        Returns:
            int: The number of the spawned weapon, либо 0 если не сгенерировано.
        """
        # --- Новый блок: диапазон оружия по расстоянию ---
        distance = max(0, self.location_num - 1)
        min_weapon = min(1 + distance, len(helper.babka_weapon))
        max_weapon = min(
            len(helper.babka_weapon), int(len(helper.babka_weapon) * (0.3 + 0.1 * distance))
        )
        if max_weapon < min_weapon:
            max_weapon = min_weapon
        chance = randint(1, 1)  # 5 - babka.luck)
        if chance == 1:
            item = randint(min_weapon, max_weapon)
            return item
        return 0


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


class MessageHandler:
    """Handles formatted output of game messages."""
    def __init__(self, output_func=print):
        self.output_func = output_func

    def print_message(self, message, msg_type='info'):
        """Print a formatted message with a given type."""
        if msg_type == 'info':
            formatted_message = f"\033[94m[{msg_type.upper()}]\033[0m: {message}"
        elif msg_type == 'fight':
            formatted_message = f"\033[91m[{msg_type.upper()}]\033[0m: {message}"
        elif msg_type == 'system':
            formatted_message = f"\033[92m[{msg_type.upper()}]\033[0m: {message}"
        elif msg_type == 'talk':
            formatted_message = f'\n{message}\n'
        else:
            formatted_message = f"[{msg_type.upper()}]: {message}"
        self.output_func(formatted_message)


class Combat:
    """
    A class representing combat between two characters.
    """
    def __init__(self, handler):
        self.handler = handler

    def attack(self, attacker, victim):
        """Attack logic for combat."""
        self.handler.print_message(attacker.say(), msg_type='talk')
        self.handler.print_message(f'{attacker.name} атакует!', msg_type='fight')

        # --- Новое: уклонение ---
        evaded = func.calculate_evasion_chance(victim.stats.defence, victim.stats.luck)
        if evaded:
            self.handler.print_message(f'{victim.name} ловко уклонился от удара!', msg_type='fight')
            return False

        # --- Новое: критический удар ---
        is_crit = func.calculate_critical_hit(attacker.stats.luck)
        damage = func.calculate_attack_power(
            attacker.stats.strength,
            helper.weapon[attacker.weapon][1] if attacker.weapon else 1,
            attacker.stats.damage,
            victim.stats.defence,
            getattr(attacker, 'level', 1),
            getattr(victim, 'level', 1),
            crit=is_crit,
            evaded=False
        )

        if is_crit:
            self.handler.print_message(
                f'Критический удар! {attacker.name} наносит {damage} урона', msg_type='fight'
            )
        else:
            self.handler.print_message(
                f'{attacker.name} наносит {damage} урона', msg_type='fight'
            )
        victim.stats.hp -= damage
        victim.say()
        self.handler.print_message(
            f'{victim.name} HP: {victim.stats.hp}', msg_type='info'
        )
        return victim.stats.hp <= 0


class Human:
    """
    Базовый класс для всех персонажей (игрок и NPC).
    """
    def __init__(
        self,
        name,
        gender=None,
        level=1,
        location=1,
        stats=None,
        inventory=None,
        weapon=None,
        maxhp=100,
        mood='Нейтральный',
        patience=100
    ):
        self.name = name
        self.gender = gender
        self.level = level
        self.location = location if location is not None else 1
        self.stats = stats or Stats(
            hp=maxhp,
            strength=randint(level + 3, level + 7),
            dexterity=randint(level + 3, level + 7),
            luck=randint(level + 1, level + 3),
            damage=2,
            defence=2
        )
        self.inventory = inventory if inventory is not None else []
        self.weapon = weapon if weapon is not None else None
        self.maxhp = maxhp
        self.kills = 0
        self.mood = mood
        self.patience = patience

    def about(self):
        """Return basic information about the character."""
        return {
            'Имя': self.name,
            'Пол': 'мужской' if self.gender == 'male' else 'женский',
            'Уровень': self.level,
            'HP': self.stats.hp,
            'Сила': self.stats.strength,
            'Ловкость': self.stats.dexterity,
            'Удача': self.stats.luck,
            'Оружие': helper.babka_weapon[
                self.weapon
            ][0] if self.weapon in helper.babka_weapon else 'нет',
            'Наносимый урон': self.stats.damage,
            'Защита': self.stats.defence,
            'Опыт': self.stats.exp,
            'Инвентарь': [
                {
                    'Оружие': helper.babka_weapon[i][0],
                    'Урон': helper.babka_weapon[i][1],
                } for i in self.inventory if i in helper.babka_weapon
            ]
        }

    def move(self, destination):
        """Move character to destination"""
        if destination == self.location:
            return f"{self.name} уже находится в этой локации: {helper.locations[self.location][0]}"
        self.location = destination
        return f"{self.name} переместился в {helper.locations[destination][0]}"

    def calculate_stats(self):
        """Caclulate character stats"""
        if not self.weapon or self.weapon not in helper.babka_weapon:
            self.stats.damage = self.stats.strength
        else:
            self.stats.damage = self.stats.strength * helper.babka_weapon[self.weapon][1]
        self.stats.defence = int((self.stats.strength // 2) * (self.stats.dexterity // 1.5))

    def get_new_weapon(self, weapon):
        """ Get new weapon"""
        weapon_list = {
            w: helper.babka_weapon[w][0] for w in self.inventory if w in helper.babka_weapon
        }
        if helper.babka_weapon[weapon][0] in weapon_list.values():
            return 'Такая штука у тебя уже есть, эх..'
        self.inventory.append(weapon)
        return f'Теперь у тебя есть: {helper.babka_weapon[weapon][0]}'

    def get_weapon(self):
        """Get weapon"""
        if not self.weapon and self.inventory:
            self.weapon = self.inventory[0]
        self.calculate_stats()
        if self.weapon and self.weapon in helper.weapon:
            return f'{self.name} достает {helper.weapon[self.weapon][0]}'
        return None

    def hide_weapon(self):
        """Hide weapon"""
        if self.weapon:
            self.weapon = None
            self.calculate_stats()
        return None

    def say(self):
        """Say phrase"""
        return f'{self.name}: ...'


class Babka(Human):
    """
    Класс для игрока-бабки.
    """
    def __init__(self, name, gender="female", level=1, stats=None):
        super().__init__(
            name=name,
            gender=gender,
            level=level,
            location=1,
            stats=stats,
            inventory=[1],
            weapon=None,
            maxhp=110,
            mood='Нейтральный',
            patience=100
        )
        self.calculate_stats()

    def calculate_expirience(self, npc_level) -> int:
        """Caclulate expirience"""
        base_exp = 40
        diff = npc_level - self.level
        exp = int(base_exp * (1 + 0.5 * max(0, diff)))
        return max(10, exp)

    def add_experience(self, exp):
        """Add expirience"""
        self.stats.exp += exp
        # Порог для повышения уровня (например, 100 * текущий уровень)
        levelup_messages = []
        while self.stats.exp >= 100 * self.level:
            self.stats.exp -= 100 * self.level
            self.level += 1
            self.stats.strength += 2
            self.stats.dexterity += 1
            if self.level % 3 == 0 and self.stats.luck < 12:
                self.stats.luck += 1
            self.maxhp += 10
            self.stats.hp = self.maxhp
            levelup_messages.append(
                f'Бабка повысила уровень до {self.level}! Сила +2, Ловкость +1, Макс. HP +10' +
                (', Удача +1' if self.level % 3 == 0 else '')
            )
        self.calculate_stats()
        return levelup_messages

    def about(self):
        info = super().about()
        info['Тип'] = 'Бабка'
        return info

    def say(self):
        return f'{self.name}: {func.generate_phrase()}'

    def levelup(self):
        """Level up function"""
        self.level += 1
        self.maxhp = 10 + 100 * self.level
        self.stats.hp = self.maxhp
        self.stats.strength += 1
        self.stats.dexterity += 1
        if self.stats.luck < 10 and self.level % 5 == 0:
            self.stats.luck += 1
        self.calculate_stats()


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
        location=1
    ):
        """
        Initialize a new NPC object.

        Args:
            name (str): The name of the NPC. Defaults to 'NPC'.
            gender (str): The gender of the NPC. Defaults to None.
            level (int): The level of the NPC. Defaults to 1.
            stats (Stats): The stats of the NPC. Defaults to None.
            mood (str): The mood of the NPC. Defaults to 'Нейтральный'.
            location (int): The location of the NPC. Defaults to 1.
        """

        super().__init__(name, gender, level, location, stats)

        self.stats = stats or Stats(
            hp=100,
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
        self.location = location
        self.inventory.append(randint(1, len(helper.weapon)))
        self.weapon = None
        self.patience = 100
        self.calculate_stats()

    def about(self):
        """
        Return a dictionary containing basic information about the NPC.

        Returns:
            dict: A dictionary with the NPC's name and gender.
        """
        return {
            'Имя': self.name,
            'Пол': 'мужской' if self.gender == 'male' else 'женский',
        }

    def calculate_stats(self):
        """Calculate the NPC's combat stats.

        This method calculates the NPC's damage, defence, and hit points based on
        their current weapon, strength, dexterity, and level.

        Args:
            None

        Returns:
            None
        """

        if not self.weapon or self.weapon not in helper.weapon:
            self.damage = int(self.stats.strength) + 1
        else:
            self.damage = self.stats.strength + int(helper.weapon[self.weapon][1])

        self.defence = int((self.stats.strength / 2)) * int((self.stats.dexterity / 1.5))

    def gen_name(self, gender):
        """Generate a random name for an NPC based on gender.

        Args:
            gender (str): The gender of the NPC, either 'male' or 'female'.

        Returns:
            str: A random name for the NPC.
        """
        if helper.options.get('gen_names') == "neuro":
            return get_name(
                gender,
                use_2nd_order=True
            )
        return func.random_name(gender)

    def say(self):
        """Print a phrase spoken by the NPC.

        This method uses the `random` module to select a phrase from a list of
        phrases based on the NPC's current mood.

        Args:
            None

        Returns:
            str: A phrase spoken by the NPC.
        """
        phrases = {
            'Добрый': helper.happy_phrases,
            'Нейтральный': helper.neutral_phrases,
            'Злой': helper.angry_phrases
        }[self.mood]
        return f'{self.name}: {choice(phrases)}'

    def nervous(self, act):
        """
        Make the NPC nervous.

        If the NPC is not already in a 'Злой' mood, this method reduces the
        NPC's patience by a certain amount based on the 'act' argument. If the
        NPC's patience reaches 0, the NPC's mood is changed to the one above
        their current mood in the helper.mood dictionary.

        Args:
            act (int): The type of action that made the NPC nervous. A value of
                1 indicates a minor action, while any other value indicates a
                major action.

        Returns:
            str: A message indicating whether the NPC's mood changed.
        """
        if self.mood != 'Злой':
            if act == 1:
                self.patience -= 10
            else:
                self.patience -= 40
            if self.patience <= 0:
                self.patience = 100
                for k, m in helper.mood.items():
                    if m == self.mood:
                        self.mood = helper.mood[k - 1]
                return f'{self.name} изменил настроение на {self.mood}'
        return f'{self.name} не изменил настроение'

    def get_weapon(self):
        """
        Equip the NPC with a weapon from their inventory.

        If the NPC does not currently have a weapon equipped, this method assigns
        the first weapon from their inventory to the 'weapon' attribute and then
        recalculates the NPC's combat stats.

        Args:
            None

        Returns:
            None
        """
        if not self.weapon and self.inventory:
            self.weapon = self.inventory[0]
        self.calculate_stats()
        if self.weapon and self.weapon in helper.weapon:
            return f'{self.name} достает {helper.weapon[self.weapon][0]}'
        return None

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
            self.weapon = ''
            self.calculate_stats()
