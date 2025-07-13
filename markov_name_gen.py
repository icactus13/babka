import random
from collections import defaultdict
import csv
import re


def load_names_from_csv(path):
    """
    Загружает имена и пол из csv-файла (разделитель ;).
    Возвращает два списка: male_names, female_names
    """
    male_names = []
    female_names = []
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) < 3:
                continue
            name = row[1].strip()
            gender = row[2].strip().lower()
            # Фильтруем только имена из букв, длина >= 3
            if not re.match(r'^[А-Яа-яA-Za-z-]{3,}$', name):
                continue
            if gender in ('м', 'm', 'male', 'муж', 'мужской'):
                male_names.append(name)
            elif gender in ('ж', 'f', 'female', 'жен', 'женский'):
                female_names.append(name)
    return male_names, female_names


class MarkovNameGenerator:
    def __init__(self, names, n=2):
        """
        names: список строк-имён для обучения
        n: размер n-граммы (2 — биграммы, 3 — триграммы)
        """
        self.n = n
        self.model = defaultdict(list)
        self.starts = []
        for name in names:
            name = name.strip()
            if len(name) < n:
                continue
            self.starts.append(name[:n])
            for i in range(len(name) - n):
                key = name[i:i+n]
                next_char = name[i+n]
                self.model[key].append(next_char)
            # Добавим специальный символ конца
            self.model[name[-n:]].append(None)

    def generate(self, min_len=4, max_len=8):
        key = random.choice(self.starts)
        result = key
        while len(result) < max_len:
            next_chars = self.model.get(key)
            if not next_chars:
                break
            next_char = random.choice(next_chars)
            if next_char is None:
                if len(result) >= min_len:
                    break
                else:
                    # Принудительно продолжаем, если имя слишком короткое
                    key = random.choice(self.starts)
                    result += key
                    continue
            result += next_char
            key = result[-self.n:]
        return result.capitalize()


class GenderedMarkovNameGenerator:
    def __init__(self, male_names, female_names, n=2):
        self.male_gen = MarkovNameGenerator(male_names, n)
        self.female_gen = MarkovNameGenerator(female_names, n)

    def generate(self, gender=None, min_len=4, max_len=8):
        if gender in ('ж', 'f', 'female', 'жен', 'женский'):
            return self.female_gen.generate(min_len, max_len)
        elif gender in ('м', 'm', 'male', 'муж', 'мужской'):
            return self.male_gen.generate(min_len, max_len)
        else:
            # Если не указан пол — случайно
            if random.random() < 0.5:
                return self.male_gen.generate(min_len, max_len)
            else:
                return self.female_gen.generate(min_len, max_len)


if __name__ == "__main__":
    # Пример использования: загрузить имена из csv и сгенерировать мужские и женские имена
    male_names, female_names = load_names_from_csv('allnames.csv')
    gen = GenderedMarkovNameGenerator(male_names, female_names, n=2)
    print('Мужские имена:')
    for _ in range(5):
        print(gen.generate(gender='m'))
    print('Женские имена:')
    for _ in range(5):
        print(gen.generate(gender='f'))
