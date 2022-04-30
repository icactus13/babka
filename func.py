import helper
import menu
from time import sleep
from sys import exit
from random import randint, choice
import threading
import markovify
from name_gen import get_name
import sqlite3


gen_names = 'norm'


def clear_screen():
    """This function clears the screen
    """
    print(50 * '\n')


def insert_db(query, var=""):
    """This function adds an entry to the database

    Args:
        query (string): Database query
        var (str, optional): [description]. Defaults to "".
    """
    conn = sqlite3.connect('saves.db')
    cur = conn.cursor()
    cur.execute(query, var)
    conn.commit()


def select_db(query):
    """Return rows from DB

    Args:
        query (string): Database query

    Returns:
        [list]: rows from DB
    """
    conn = sqlite3.connect('saves.db')
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


def create_table():
    """ Create table
    """
    insert_db("""CREATE TABLE IF NOT EXISTS babkas(
                    userid INT PRIMARY KEY,
                    name TEXT,
                    level INT,
                    hp INT,
                    strength INT,
                    dexterity INT,
                    luck INT,
                    tired INT,
                    inventory BLOB,
                    damage INT,
                    defence INT,
                    exp INT,
                    location INT,
                    maxhp INT);
                    """)


def save_babka(babka):
    """[summary]

    Args:
        babka (class?): Current babka
    """
    try:
        check = select_db(
            "Select * from babkas Where name = '" + babka.name + "';")
    except:
        print("DAMN, GOD, YOU CRASHED THE GAME!")
    else:
        inv = '-'
        for i in babka.inventory:
            inv += str(i) + '-'
        if len(check) == 0:
            result = select_db("Select * from babkas;")
            save = (len(result)+1, babka.name, babka.level, babka.hp, babka.strength, babka.dexterity, babka.luck,
                    babka.tired, inv, babka.damage, babka.defence, babka.exp, babka.location, babka.maxhp)
            insert_db(
                'INSERT INTO babkas VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', save)
        else:
            update_save = (babka.level, babka.hp, babka.strength, babka.dexterity, babka.luck,
                           babka.tired, inv, babka.damage, babka.defence, babka.exp, babka.location, babka.maxhp, check[0][0])
            insert_db("UPDATE babkas SET level=?, hp=?, strength=?, dexterity=?, \
                       luck=?, tired=?, inventory=?, damage=?, defence=?, exp=?, \
                       location=?, maxhp=? where userid = ?", update_save)


def load_babkas():
    """[summary]

    Returns:
        [list]: List of saved babkas
    """
    result = select_db("Select * from babkas;")
    names = []
    for name in result:
        names.append(name[1])
    return names


def load_babka(babka_number):
    """[summary]

    Args:
        babka_number (int): Babka number from the database

    Returns:
        class: Babka
    """
    params = select_db(
        "Select * from babkas Where userid = " + str(babka_number) + ";")
    inv = []
    for i in params[0][8]:
        if i != '-':
            inv.append(int(i))
    babka = Babka(params[0][1],
                  "female",
                  params[0][2],
                  params[0][3],
                  params[0][4],
                  params[0][5],
                  params[0][6],
                  params[0][7],
                  inv,
                  params[0][9],
                  params[0][10],
                  params[0][11],
                  params[0][12],
                  params[0][13])
    return babka


def intro():
    """ Show intro
    """
    clear_screen()
    print('\n' * 10)
    print("Babka 2.0")
    print("=" * 5, "The chosen", "=" * 5)
    print('\nLoading', end="", flush=True)
    loading(3)
    clear_screen()


def is_digit(string):
    """ checks if a variable is a number

    Args:
        string (string): variable being checked

    Returns:
        bool: 
    """
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def is_string(string):
    """ checks if a variable is a string

    Args:
        string (string): variable being checked

    Returns:
        bool: True or false
    """
    if isinstance(string, str):
        return True
    else:
        return False


def create_name():
    """Create Babka's name
    if no name is specified, the function will generate a random name.

    Returns:
        string: Generated Babka's name
    """
    menu.print_title('Создание бабки')
    print('Если имя не будет введено, то будет сгенерировано случайное имя.')
    name = input('Введи имя: ')
    if not name:
        print('Хорошо, я сгенерирую рандомное имя для бабки...')
        if gen_names == "neuro":
            name = get_name('female')
        else:
            name = random_name('female')
        print('Имя бабки: ', name)
        return name
    elif is_string(name):
        print("Хорошо!")
        return name


def random_name(gender):
    """ Random name function

    Args:
        gender (string): Gender

    Returns:
        string: Random name
    """
    name = ''
    if gender == 'female':
        num = helper.female_names.__len__()
        name = helper.female_names[randint(0, num - 1)]
    elif gender == 'male':
        num = helper.male_names.__len__()
        name = helper.male_names[randint(0, num - 1)]
    return name


def confirm(answer):
    """Yes/no function

    Args:
        answer (string): Your answer

    Returns:
        bool:
    """
    if is_string(answer):
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            return confirm
    else:
        return confirm


# def calculate(one: int, two: int, three: int):
#     """ I forgot what this function is

#     Args:
#         one (int): first number
#         two (int): second number
#         three (int): third number

#     Returns:
#         int: fourth number
#     """
#     point = (abs(one + two + three / 2)).__int__()
#     return point


def calc_damage(att, dfn, luck=0):
    """Calculate damage

    Args:
        att (int): Attack points
        dfn (int): defence point
        luck (int): lucky points, default 0

    Returns:
        int: Damage points
    """
    return abs(att - att * (dfn / 100).__int__() + luck)

def calc_exp(babka_level, npc_level):
    """ Calculate gained experience 

    Args:
        babka_level (int): Babka level
        npc_level (int): NPC level

    Returns:
        int: Gained expirience
    """
    return round(100 * (10 + npc_level - babka_level)/(7 + babka_level))


def available_locations(loc1, loc2, names=False):
    """ Return list of available locations

    Args:
        loc1 (int): Current location
        loc2 (int): ?
        names (bool, optional): return the name of the location, not its number. Defaults to False.

    Returns:
        string: Location name or nubmer
    """
    if names:
        return [helper.locations[i][0] for i in helper.locations if i != loc1 if i != loc2]
    else:
        return [helper.locations[i][1] for i in helper.locations if i != loc1 if i != loc2]


def moving(cur_loc, loc, time):
    """ Move to location

    Args:
        cur_loc (int): Current location
        loc (int): Destination
        time (int): travel time 

    Returns:
        [type]: I forgot
    """
    if cur_loc > loc:
        for i in range(0, 2 * (cur_loc - loc)):
            print('.', end="", flush=True)
            sleep(time)
        print('')
        return 2 * (cur_loc - loc)
    else:
        for i in range(0, 2 * (loc - cur_loc)):
            print('.', end="", flush=True)
            sleep(time)
        print('')
        return 2 * (loc - cur_loc)


def loading(num):
    """ the function of simulating the loading of the game,
        such as such a cool and large game, like this,
        it takes even a long time to load

    Args:
        num (int): some number
    """
    for i in range(0, 2 * num):
        print('.', end="", flush=True)
        sleep(i / 10)
    print('')


def create_npc(loc, gender, level, mood):
    """ Create NPC

    Args:
        loc (int): Location
        gender (string): gender
        level (int): NPC level
        mood (int): NPC mood

    Returns:
        class: NPC
    """
    if gen_names == "neuro":
        name = get_name(gender)
    else:
        name = random_name(gender)
    return NPC(name, gender, level, loc, mood)


def phrase_gen():
    """ Generate funny phrases with markov chain

    Returns:
        String: Babka's phrase
    """
    with open('./markov.json') as f:
        text = f.read()
    text_model_a = markovify.Text.from_json(text)
    return text_model_a.make_short_sentence(50)


def spawn_weapon(babka):
    """ Spawn new weapon on location

    Args:
        babka (class): Your babka

    Returns:
        nothing if the weapon drop chance is not equal to 1
        Call get_new_weapon func if drop chance equal 1
    """
    chance = randint(1, 1)#5 - babka.luck)
    weapons = len(helper.babka_weapon)
    if chance == 1:
        if babka.location + babka.level >= weapons:
            random_num = weapons
        else:
            random_num = babka.location + babka.level
        item = randint(1, random_num)
        print('Ого, вот это да, ', helper.babka_weapon[item], "!")
        get_new_weapon(babka, item)
    else:
        return False


def get_new_weapon(babka, weapon):
    """ Add new weapon in Babka's inventory

    Args:
        babka (class): Your Babka
        weapon (int): Spawned weapon
    """
    weapon_list = {}
    for i in babka.inventory:
        weapon_list[i] = helper.babka_weapon[i][0]
    if helper.babka_weapon[weapon][0] in weapon_list.values():
        print('Такая штука у тебя уже есть, эх..')
    else:
        babka.inventory.append(weapon)


def loc_gen(babka, location):
    """ Location generator

    Args:
        babka (class): Your Babka
        location (int): Location number

    Returns:
        [dict]: NPC list
    """
    num = 1
    npc = {}
    for y in range(1, randint(location, location + 5)):
        if babka.level <= 2:
            npc[num] = create_npc(location, choice(helper.gender),
                                  randint(babka.level, babka.level + 2),
                                  helper.mood[randint(1, 3)])
        else:
            npc[num] = create_npc(location, choice(helper.gender),
                                  randint(babka.level - 2, babka.level + 2),
                                  helper.mood[randint(1, 3)])
        loading(1)
        print('NPC #', num, ': ', npc[num].name, ' успешно создан.')
        num = num + 1
        sleep(0.2)
        print('[OK]')
    return npc


class Human:  # Класс "Человек"
    def __init__(self, name, 
                 gender=None, 
                 level=1, 
                 location=''):
        self.name = name
        self.gender = gender
        self.location = location
        self.level = level

    def talk(self, phrase):
        print(self.name, "-", phrase)


class Babka(Human):  # Подкласс "Бабка"
    def __init__(self, name, 
                 gender="female",
                 level=1,
                 hp=10,
                 strength=randint(3, 7),
                 dexterity=randint(3, 7),
                 luck=randint(3, 7),
                 tired=0,
                 inventory = [],
                 damage=None,
                 defence=None,
                 exp=0,
                 location=1,
                 maxhp=20):
        super().__init__(name, gender, level, location)
        self.level = level
        self.hp = hp
        self.strength = strength
        self.dexterity = dexterity
        self.luck = luck
        self.tired = tired
        self.weapon = ''
        self.damage = damage
        self.defence = defence
        self.exp = exp
        self.location = location
        self.inventory = inventory
        self.maxhp = maxhp
        self.grumble_mode = 'off'
        #self.inventory.append(1)
        self.calculate_stats()

    def calculate_stats(self):
        if self.weapon == '':
            self.damage = self.strength + 1
        else:
            self.damage = self.strength + \
                int(helper.babka_weapon[self.weapon][1])
        self.defence = (self.strength / 2).__int__() * self.dexterity

    def about(self):
        pol = ''
        if self.gender == 'male':
            pol = 'муж.'
        elif self.gender == 'female':
            pol = 'жен.'
        print("Имя:", self.name)
        print("Пол:", pol)
        print('Уровень:', self.level)
        print('HP:', self.hp)
        print('Сила:', self.strength)
        print('Ловкость:', self.dexterity)
        print('Удача:', self.luck)
        print('Усталость:', self.tired)
        if self.weapon == '':
            print('Оружие: нет')
        else:
            print('Оружие:', helper.babka_weapon[self.weapon])
        print('Наносимый урон:', self.damage)
        print('Защита:', self.defence)
        # print("Всего денег: ", self.money, "p")
        print("Опыт:", self.exp)
        print('Инвентарь:')
        for i in self.inventory:
            print('-', helper.babka_weapon[i][0],
                  '- урон:', helper.babka_weapon[i][1])
        print('Текущая локация:', helper.locations[self.location][1])
        print('-' * 80)

    def grumble(self):  # Режим ворчания
        if self.grumble_mode == 'off':
            self.grumble_mode = 'on'
        elif self.grumble_mode == 'on':
            self.grumble_mode = 'off'
        phrases = helper.grumble_phrases.__len__()

        def loop():
            while self.grumble_mode == "on":
                sleep(5)
                print(self.name, ": ",
                      helper.grumble_phrases[randint(0, phrases - 1)])

        thread = threading.Thread(target=loop)
        if self.grumble_mode == 'on':
            print("--Режим ворчания включен--")
            thread.daemon = True
            thread.start()
        elif self.grumble_mode == 'off':
            print("--Режим ворчания выключен--")
            thread.daemon = False

    def smart_talk(self):
        print(self.name, "-", phrase_gen())

    def levelup(self):
        self.level = self.level + 1
        self.maxhp = 10 + 10 * self.level
        self.hp = self.maxhp
        self.strength = self.strength + 1
        self.dexterity = self.dexterity + 1
        if self.luck < 10:
            if self.level % 5 == 0:
                self.luck = self.luck + 1
        self.calculate_stats()
        print('Бабка', self.name, 'достигла нового уровня:', self.level, '!')
        self.about()


class NPC(Human):  # Подкласс НПЦ
    def __init__(self,
                name,
                gender,
                level,
                location,
                mood,
                strength=randint(3, 7),
                dexterity=randint(3, 7),
                ):
        super().__init__(name, gender, level, location)
        self.strength = strength
        self.dexterity = dexterity
        self.inventory = []
        self.mood = mood
        self.location = location
        self.inventory.append(randint(1, helper.weapon.__len__()))
        self.weapon = ''
        self.terpenie = 100
        self.calculate_stats()
        
    def about(self):  # Показать информацию об объекте класса
        pol = ''
        if self.gender == 'male':
            pol = 'муж.'
        elif self.gender == 'female':
            pol = 'жен.'
        print("Информация:")
        print("Имя:", self.name)
        print("Пол:", pol)
        print('Уровень:', self.level)
        print('HP:', self.hp)
    
    def calculate_stats(self):
        if self.weapon == '':
            self.damage = int(self.strength) + 1
        else:
            self.damage = self.strength + int(helper.weapon[self.weapon][1])
        self.defence = (self.strength / 2).__int__() * \
            (self.dexterity / 1.5).__int__()
        self.hp = 10 * self.level
        
    def get_weapon(self):
        if self.weapon == '':
            print(self.name, 'достает', helper.weapon[self.inventory[0]][0])
            self.weapon = self.inventory[0]
        else:
            print(self.name, 'крепко сжимает в руке',
                  helper.weapon[self.weapon][0][0])
        self.calculate_stats()

    def hide_weapon(self):
        if self.weapon != '':
            print(self.name, 'убирает', helper.weapon[self.inventory[0]][0])
            self.weapon = ''
            self.calculate_stats()

    def nervous(self, kak):
        if self.mood != 'Злой':
            if kak == 1:
                print(self.name, 'м?')
                self.terpenie = self.terpenie - 10
                print('Терпение', self.name, ': ', self.terpenie)
            else:
                print(self.name, 'эй!')
                self.terpenie = self.terpenie - 40
                print('Терпение', self.name, ': ', self.terpenie)
            if self.terpenie <= 0:
                self.terpenie = 100
                for k, m in helper.mood.items():
                    if m == self.mood:
                        self.mood = helper.mood[k - 1]
                print(self.name, 'изменил настроение на', self.mood)

    def say(self):
        if self.mood == 'Добрый':
            self.talk(helper.happy_phrases[randint(
                0, helper.happy_phrases.__len__() - 1)])
        elif self.mood == 'Нейтральный':
            self.talk(helper.neutral_phrases[randint(
                0, helper.neutral_phrases.__len__() - 1)])
        else:
            self.talk(helper.angry_phrases[randint(
                0, helper.angry_phrases.__len__() - 1)])
            # self.talk(phrase_gen())
