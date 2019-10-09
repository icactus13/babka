import helper
from time import sleep
from random import randint
import threading


def print_title(men_title):  # Рисует карсивый заголовок
    print(80 * '=')
    title_len = len(men_title)
    titled = (((80 - title_len) // 2) - 1)
    if title_len % 2 == 1:
        print('-' * titled, men_title, '-' * (titled + 1))

    else:
        print('-' * titled, men_title, '-' * titled)
    print(80 * '=')


def is_digit(string):  # Функция проверки является ли числом переменная
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def is_string(string):  # Функция проверки является ли строкой переменная
    if isinstance(string, str):
        return True
    else:
        return False


def create_name():  # Создание имени бабки, если имя не указано, то функция выберет случайное
    print_title('Создание бабки')
    print('Если имя не будет введено, то будет сгенерировано случайное имя.')
    name = input('Введи имя: ')
    if not name:
        print('Хорошо, я сгенерирую рандомное имя для бабки...')
        name = random_name('female')
        print('Имя бабки: ', name)
        return name
    elif is_string(name):
        print("Хорошо!")
        return name


def random_name(gender):  # Функция случайного выбора имени
    name = ''
    if gender == 'female':
        num = helper.female_names.__len__()
        name = helper.female_names[randint(0, num - 1)]
    elif gender == 'male':
        num = helper.male_names.__len__()
        name = helper.male_names[randint(0, num - 1)]
    return name


def confirm(answer):  # Функция да/нет
    if is_string(answer):
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            return confirm
    else:
        return confirm


def calculate(one, two, three):  # что это???
    point = (abs(one + two + three / 2)).__int__()
    return point


def calc_damage(att, dfn):
    return att - att * (dfn/100).__int__()


def available_locations(loc1, loc2):  # Список доступных локаций
    return [i for i in helper.locations if i != loc1 if i != loc2]


def moving(cur_loc, loc, time):  # Функция перемещения по локациям
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


def loading(num):  # Функция, имитирующая загрузку
    for i in range(0, 1 * num):
        print('.', end="", flush=True)
        sleep(1)
    print('')


def create_npc(loc, gender, level, mood):  # Создание нпц
    name = random_name(gender)
    return NPC(name, gender, loc, level, mood)


class Human:  # Класс "Человек"
    def __init__(self, name, gender, location, level):
        self.name = name
        self.gender = gender
        self.money = 0
        self.location = location
        self.level = level
        self.hp = 10
        '''Сила'''
        self.strength = randint(self.level, self.level+4) + self.level
        '''Ловкость'''
        self.dexterity = randint(self.level, self.level+4) + self.level
        '''Выносливость'''
        self.endurance = randint(self.level, self.level+4) + self.level
        '''Удача'''
        self.luck = randint(self.level, self.level+4)
        self.weapon = ('Пусто', 1)
        self.inventory = []
        self.damage = 0
        self.defence = 0
        self.calculate_stats()

    def about(self):  # Показать информацию об объекте класса
        pol = ''
        if self.gender == 'male':
            pol = 'муж.'
        elif self.gender == 'female':
            pol = 'жен.'
        print("Информация:")
        print("Имя: ", self.name)
        print("Пол: ", pol)
        print('Уровень: ', self.level)
        print('HP: ', self.hp)

    def talk(self, phrase):
        print(self.name, ": ", phrase)

    def calculate_stats(self):
        self.damage = self.strength + self.weapon[1]
        self.defence = (self.strength/2).__int__() * self.endurance
        self.hp = 10 * self.level

    def get_weapon(self):
        if self.weapon[0] == 'Пусто':
            print(self.name, 'достает ', self.inventory[0])
            self.weapon = self.inventory
        else:
            print(self.name, 'крепко сжимает в руке ', self.inventory[0])
        self.calculate_stats()

    def hide_weapon(self):
        if self.weapon != 'Пусто':
            print(self.name, 'убирает', self.weapon[0])
            self.weapon = ('Пусто', 1)
            self.calculate_stats()

    def levelup(self):
        self.strength = self.strength + 1
        self.dexterity = self.dexterity + 1
        self.endurance = self.endurance + 1


class Babka(Human):  # Подкласс "Бабка"
    def __init__(self, name, gender="female", location=1, level=1):
        super().__init__(name, gender, location, level)
        self.grumble_mode = 'off'
        self.money = 5000
        self.tired = 0
        self.inventory = helper.babka_weapon[1]
        self.exp = 0

    def about(self):
        pol = ''
        if self.gender == 'male':
            pol = 'муж.'
        elif self.gender == 'female':
            pol = 'жен.'
        print("Имя: ", self.name)
        print("Пол: ", pol)
        print('Уровень: ', self.level)
        print('HP: ', self.hp)
        print('Сила: ', self.strength)
        print('Ловкость: ', self.dexterity)
        print('Выносливость: ', self.endurance)
        print('Удача: ', self.luck)
        print('Усталость: ', self.tired)
        print('Оружие: ', self.weapon[0])
        print('Наносимый урон: ', self.damage)
        print('Защита: ', self.defence)
        print("Всего денег: ", self.money, "p")
        print('Инвентарь: ')
        for i in self.inventory:
            print(i)
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
                print(self.name, ": ", helper.grumble_phrases[randint(0, phrases - 1)])

        thread = threading.Thread(target=loop)
        if self.grumble_mode == 'on':
            print("--Режим ворчания включен--")
            thread.daemon = True
            thread.start()
        elif self.grumble_mode == 'off':
            print("--Режим ворчания выключен--")
            thread.daemon = False


class NPC(Human):  # Подкласс НПЦ
    def __init__(self, name, gender, location, level, mood):
        super().__init__(name, gender, location, level)
        self.mood = mood
        self.money = randint(10, 1000 * level)
        self.inventory = helper.weapon[randint(1, helper.weapon.__len__())]
        self.terpenie = 100

    def nervous(self, kak):
        if self.mood != 'Злой':
            if kak == 1:
                print(self.name, ' м?')
                self.terpenie = self.terpenie - 10
                print('Терпение ', self.name, ': ', self.terpenie)
            else:
                print(self.name, ' эй!')
                self.terpenie = self.terpenie - 40
                print('Терпение ', self.name, ': ', self.terpenie)
            if self.terpenie <= 0:
                self.terpenie = 100
                for k, m in helper.mood.items():
                    if m == self.mood:
                        self.mood = helper.mood[k - 1]
                print(self.name, ' изменил настроение на ', self.mood)

    def say(self):
        if self.mood == 'Добрый':
            self.talk(helper.happy_phrases[randint(0, helper.happy_phrases.__len__() - 1)])
        elif self.mood == 'Нейтральный':
            self.talk(helper.neutral_phrases[randint(0, helper.neutral_phrases.__len__() - 1)])
        else:
            self.talk(helper.angry_phrases[randint(0, helper.angry_phrases.__len__() - 1)])
