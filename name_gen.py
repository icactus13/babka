import csv
import random


class Letter:
    """
    Класс для описания буквы алфавита.
    """
    def __init__(self, lower, upper, is_vowel, is_consonant, is_upperchar):
        self.lower = lower
        self.upper = upper
        self.is_vowel = is_vowel
        self.is_consonant = is_consonant
        self.is_upperchar = is_upperchar


class NameGenerator:
    """
    Генератор имён на основе марковской цепи первого порядка.
    """
    def __init__(self, alph, prob_matrix, min_length=3, max_length=10):
        self.alphabet = alph
        self.letter_map = {letter.lower: letter for letter in alph}
        self.letter_map.update({letter.upper: letter for letter in alph})
        self.prob = self.normalize([row[:] for row in prob_matrix])
        self.min_length = min_length
        self.max_length = max_length

    @classmethod
    def from_csv(cls, alphabet_param, matrix_path, min_length=3, max_length=10):
        """From csv"""
        prob = []
        with open(matrix_path, newline='', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                prob.append([float(num) for num in row])
        return cls(alphabet_param, prob, min_length, max_length)

    @staticmethod
    def normalize(prob):
        """Normalize"""
        for s, row in enumerate(prob):
            total = sum(row)
            if total > 0:
                prob[s] = [p / total for p in row]
        return prob

    def pick_letter(self, prev_num):
        """Pick letter"""
        r = random.random()
        total = 0
        for j, letter in enumerate(self.alphabet):
            total += self.prob[prev_num][j]
            if r <= total or j == len(self.alphabet) - 1:
                return letter
        return self.alphabet[0]

    def get_letter(self, prev_num, need_consonant, need_vowel):
        """Get letter"""
        while True:
            letter = self.pick_letter(prev_num)
            if (need_consonant and letter.is_vowel) or (need_vowel and letter.is_consonant):
                continue
            return letter

    def make_name(self):
        """Make name"""
        name_length = random.randint(self.min_length, self.max_length)
        my_name = ""
        my_name_nums = []
        prev_vowel = False
        prev_consonant = False
        prev2_vowel = False
        prev2_consonant = False
        prev_num = 0
        for e in range(name_length):
            if e == 0:
                while True:
                    letter = random.choice(
                        [letter for letter in self.alphabet if letter.is_upperchar]
                    )
                    if letter.is_upperchar:
                        my_name += letter.upper
                        break
            else:
                letter = self.get_letter(prev_num, prev2_vowel, prev2_consonant)
                my_name += letter.lower
            prev2_vowel = (letter.is_vowel and prev_vowel)
            prev2_consonant = (letter.is_consonant and prev_consonant)
            prev_vowel = letter.is_vowel
            prev_consonant = letter.is_consonant
            prev_num = self.alphabet.index(letter)
            my_name_nums.append(prev_num)
        return my_name, my_name_nums

    def generate_name(self, gender=None):
        """
        Сгенерировать имя. Если gender='female', имя заканчивается на 'а', 'я' или 'и'.
        """
        while True:
            name, _ = self.make_name()
            if gender == 'female':
                if name[-1] in ('а', 'я', 'и'):
                    return name
            else:
                return name

    def train_on_name(self, name, good=True):
        """
        Усилить или ослабить вероятности переходов на основе пользовательской оценки.
        """
        factor = 1.01 if good else 0.99
        nums = []
        for c in name:
            for i, letter in enumerate(self.alphabet):
                if c == letter.lower or c == letter.upper:
                    nums.append(i)
                    break
        for i in range(len(nums) - 1):
            self.prob[nums[i]][nums[i + 1]] *= factor
        self.prob = self.normalize(self.prob)

    def save_matrix(self, path):
        """Save matrix"""
        with open(path, 'w', newline='', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in self.prob:
                writer.writerow(row)


class NameGenerator2ndOrder:
    """
    Генератор имён на основе марковской цепи второго порядка.
    """
    def __init__(
        self, _alphabet, prob_matrix, start_matrix, min_length=3, max_length=10, real_names=None
    ):
        self.alphabet = _alphabet
        self.letter_map = {letter.lower: letter for letter in _alphabet}
        self.letter_map.update({letter.upper: letter for letter in _alphabet})
        self.prob = self.normalize3d([[[p for p in row] for row in mat] for mat in prob_matrix])
        self.start_matrix = self.normalize(start_matrix)
        self.min_length = min_length
        self.max_length = max_length
        self.real_names = set(real_names) if real_names else set()

    @staticmethod
    def normalize(prob):
        """Normalize"""
        for s, row in enumerate(prob):
            total = sum(row)
            if total > 0:
                prob[s] = [p / total for p in row]
        return prob

    @staticmethod
    def normalize3d(prob):
        """Normalize 3d"""
        for i, mat in enumerate(prob):
            for j, row in enumerate(mat):
                total = sum(row)
                if total > 0:
                    prob[i][j] = [p / total for p in row]
        return prob

    @classmethod
    def from_csv(
        cls,
        alphabet_param,
        matrix_path,
        start_path,
        min_length=3,
        max_length=10,
        real_names_path=None
    ):
        """Get from csv"""
        # prob_matrix: [prev1][prev2][next]
        prob_matrix = []
        with open(matrix_path, newline='', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                # row: prev1,prev2,prob0,prob1,...probN
                prev1 = int(row[0])
                prev2 = int(row[1])
                probs = [float(x) for x in row[2:]]
                while len(prob_matrix) <= prev1:
                    prob_matrix.append([])
                while len(prob_matrix[prev1]) <= prev2:
                    prob_matrix[prev1].append([0.0 for _ in range(len(alphabet_param))])
                prob_matrix[prev1][prev2] = probs
        # start_matrix: [first][second]
        start_matrix = []
        with open(start_path, newline='', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                start_matrix.append([float(x) for x in row])
        # real names
        real_names = set()
        if real_names_path:
            with open(real_names_path, encoding='utf-8') as f:
                for line in f:
                    name = line.strip().split(';')[1] if ';' in line else line.strip()
                    if name:
                        real_names.add(name)
        return cls(alphabet_param, prob_matrix, start_matrix, min_length, max_length, real_names)

    def pick_start(self):
        """Pick start"""
        r = random.random()
        total = 0
        for i in range(len(self.alphabet)):
            for j in range(len(self.alphabet)):
                total += self.start_matrix[i][j]
        r *= total
        acc = 0
        for i in range(len(self.alphabet)):
            for j in range(len(self.alphabet)):
                acc += self.start_matrix[i][j]
                if r <= acc:
                    return i, j
        return 0, 1

    def pick_letter(self, prev1, prev2):
        """Pick letter"""
        r = random.random()
        total = 0
        for k in range(len(self.alphabet)):
            total += self.prob[prev1][prev2][k]
        r *= total
        acc = 0
        for k in range(len(self.alphabet)):
            acc += self.prob[prev1][prev2][k]
            if r <= acc:
                return k
        return 0

    def make_name(self):
        """Make name"""
        name_length = random.randint(self.min_length, self.max_length)
        name_nums = []
        i, j = self.pick_start()
        name_nums.append(i)
        name_nums.append(j)
        for _ in range(2, name_length):
            k = self.pick_letter(name_nums[-2], name_nums[-1])
            name_nums.append(k)
        name = self.alphabet[
            name_nums[0]
        ].upper + ''.join(self.alphabet[n].lower for n in name_nums[1:])
        return name, name_nums

    def generate_name(self, gender=None, max_attempts=20):
        """
        Сгенерировать реалистичное имя. Если возможно — совпадающее с настоящим.
        """
        best = None
        for _ in range(max_attempts):
            name, _ = self.make_name()
            if gender == 'female' and name[-1] not in ('а', 'я', 'и'):
                continue
            if self.real_names and name in self.real_names:
                return name  # Совпало с настоящим именем
            if not best or (self.real_names and name in self.real_names):
                best = name
        return best


# --- Описание алфавита и загрузка матрицы ---
alphabet = [
    Letter('а', 'А', True, False, True),
    Letter('б', 'Б', False, True, True),
    Letter('в', 'В', False, True, True),
    Letter('г', 'Г', False, True, True),
    Letter('д', 'Д', False, True, True),
    Letter('е', 'Е', True, False, True),
    Letter('ё', 'Ё', True, False, True),
    Letter('ж', 'Ж', False, True, True),
    Letter('з', 'З', False, True, True),
    Letter('и', 'И', True, False, True),
    Letter('й', 'Й', True, False, False),
    Letter('к', 'К', False, True, True),
    Letter('л', 'Л', False, True, True),
    Letter('м', 'М', False, True, True),
    Letter('н', 'Н', False, True, True),
    Letter('о', 'О', True, False, True),
    Letter('п', 'П', False, True, True),
    Letter('р', 'Р', False, True, True),
    Letter('с', 'С', False, True, True),
    Letter('т', 'Т', False, True, True),
    Letter('у', 'У', True, False, True),
    Letter('ф', 'Ф', False, True, True),
    Letter('х', 'Х', False, True, True),
    Letter('ц', 'Ц', False, True, True),
    Letter('ч', 'Ч', False, True, True),
    Letter('ш', 'Ш', False, True, True),
    Letter('щ', 'Щ', False, True, True),
    Letter('ъ', 'Ъ', False, True, False),
    Letter('ы', 'Ы', True, False, False),
    Letter('ь', 'Ь', False, True, False),
    Letter('э', 'Э', True, False, True),
    Letter('ю', 'Ю', True, False, True),
    Letter('я', 'Я', True, False, True)
]

MATRIX_PATH = './matrix.csv'
START_MATRIX_PATH = './start_matrix.csv'  # матрица начальных пар букв для 2-го порядка
ALLNAMES_PATH = './allnames.csv'

# Обычный генератор (1-й порядок)
gen = NameGenerator.from_csv(alphabet, MATRIX_PATH)


def get_name(gender, use_2nd_order=False):
    """
    Генерировать имя.
    Если use_2nd_order=True — использовать цепь второго порядка и фильтрацию по настоящим именам.
    """
    if use_2nd_order:
        # Для работы требуется подготовить start_matrix.csv и allnames.csv
        if not hasattr(get_name, 'gen2'):
            get_name.gen2 = NameGenerator2ndOrder.from_csv(
                alphabet, 'matrix_2nd.csv', START_MATRIX_PATH, real_names_path=ALLNAMES_PATH
            )
        return get_name.gen2.generate_name(gender)
    return gen.generate_name(gender)


def generate_2nd_order_matrices(alphabet_param, allnames_path, matrix_2nd_path, start_matrix_path):
    """
    Генерирует матрицу второго порядка (matrix_2nd.csv) и матрицу начальных пар (start_matrix.csv)
    по списку настоящих имён (allnames.csv).
    """
    n = len(alphabet_param)
    # Индексы букв
    letter_idx = {l.lower: i for i, l in enumerate(alphabet_param)}
    letter_idx.update({l.upper: i for i, l in enumerate(alphabet_param)})
    # Счётчики
    start_counts = [[0 for _ in range(n)] for _ in range(n)]
    counts = [[[0 for _ in range(n)] for _ in range(n)] for _ in range(n)]

    with open(allnames_path, encoding='utf-8') as f:
        for line in f:
            name = line.strip().split(';')[1] if ';' in line else line.strip()
            if len(name) < 3:
                continue
            nums = [letter_idx.get(c) for c in name]
            if len(nums) < 3:
                continue
            # Начальные пары
            idx0, idx1 = nums[0], nums[1]
            if idx0 is not None and idx1 is not None:
                start_counts[idx0][idx1] += 1
            # Основная матрица
            for i in range(2, len(nums)):
                idxa, idxb, idxc = nums[i-2], nums[i-1], nums[i]
                if idxa is not None and idxb is not None and idxc is not None:
                    counts[idxa][idxb][idxc] += 1
    # Нормализация и сохранение start_matrix.csv
    with open(start_matrix_path, 'w', newline='', encoding='UTF-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in start_counts:
            total = sum(row)
            if total > 0:
                writer.writerow([c/total for c in row])
            else:
                writer.writerow([0 for _ in row])
    # Сохранение matrix_2nd.csv
    with open(matrix_2nd_path, 'w', newline='', encoding='UTF-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(n):
            for j in range(n):
                total = sum(counts[i][j])
                if total > 0:
                    probs = [c/total for c in counts[i][j]]
                else:
                    probs = [0 for _ in range(n)]
                writer.writerow([i, j] + probs)


if __name__ == '__main__':
    import sys
    if '--gen2nd' in sys.argv:
        print('Генерирую матрицы второго порядка из allnames.csv...')
        generate_2nd_order_matrices(alphabet, ALLNAMES_PATH, 'matrix_2nd.csv', START_MATRIX_PATH)
        print('Готово: matrix_2nd.csv и start_matrix.csv созданы.')
        sys.exit(0)
    print('--- 1-й порядок ---')
    for _ in range(5):
        print('Ж:', gen.generate_name('female'))
        print('М:', gen.generate_name('male'))
    print('--- 2-й порядок + фильтрация ---')
    for _ in range(5):
        print('Ж:', get_name('female', use_2nd_order=True))
        print('М:', get_name('male', use_2nd_order=True))
