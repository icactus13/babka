import csv
from random import *

global letter_count
letter_count = 0


class Letter():
    # Each Letter has a lowercase character, an uppercase character, and
    # identifiers as vowel or consonant.
    def __init__(self, lowerchar, upperchar, is_vowel, is_consonant, is_upperchar):
        global letter_count
        self.upperchar = upperchar
        self.lowerchar = lowerchar
        self.is_vowel = is_vowel
        self.is_consonant = is_consonant
        self.is_upperchar = is_upperchar
        self.num = letter_count
        letter_count += 1


def normalize(prob):
    global alphabet
    new_prob = prob
    for s in range(0, len(alphabet)):
        total = 0
        for j in range(0, len(alphabet)):
            total += prob[s][j]
        if total > 0:
            for j in range(0, len(alphabet)):
                new_prob[s][j] = prob[s][j] / total
    return new_prob


# Define the alphabet.
alphabet = [Letter('а', 'А', True, False, True),
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

# Read in probability matrix.
# prob[i][j] = probability that Letter j comes after Letter i
file_name = './matrix.csv'
prob = []
with open(file_name, newline='') as csvfile:
    prob_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in prob_reader:
        prob.append([])
        for num in row:
            prob[len(prob) - 1].append(float(num))

# Normalize the probability matrix.
prob = normalize(prob)


def uniform(x1, x2):
    # Generate a random floating-point number between x1 and x2.
    r = x1 + random() * (x2 - x1)
    return r


def rand_int(x1, x2):
    # Generate a random integer number between x1 and x2.
    r = int(int(x1) + random() * (int(x2) - int(x1)))
    return r


def make_name():
    # Determine name length.
    lmin = 3  # Minimum length.
    lmax = 10  # Maximum length.
    name_length = rand_int(lmin, lmax)

    # Initialize string.
    my_name = ""
    my_name_nums = []

    prev_vowel = False  # Was the previous Letter a vowel?
    prev_consonant = False  # Was the previous Letter a consonant?
    prev2_vowel = False  # Were the previous 2 Letters vowels?
    prev2_consonant = False  # Were the previous 2 Letters consonants?
    prev_num = 0
    # Generate Letters for name.
    for e in range(0, name_length):
        if e == 0:
            b = False
            while not b:
                a = alphabet[rand_int(0, 32)]
                if a.is_upperchar:
                    my_name = my_name + a.upperchar
                    b = True
        else:
            a = get_letter(prev_num, prev2_vowel, prev2_consonant)
            my_name = my_name + a.lowerchar
        prev2_vowel = (a.is_vowel and prev_vowel)
        prev2_consonant = (a.is_consonant and prev_consonant)
        prev_vowel = a.is_vowel
        prev_consonant = a.is_consonant
        prev_num = a.num
        my_name_nums.append(a.num)
    return [my_name, my_name_nums]


def get_letter(prev_num, need_consonant, need_vowel):
    global alphabet
    global prob
    # Generate a random Letter.
    done = False
    while not done:
        a = pick_letter(prev_num)
        if (need_consonant and a.is_vowel) or (need_vowel and a.is_consonant):
            done = False
        else:
            done = True
    return a


def pick_letter(num):
    r = random()
    total = 0
    for j in range(0, len(alphabet)):
        total += prob[num][j]
        if r <= total or j == len(alphabet):
            a = alphabet[j]
            return a
    return alphabet[0]


def gen_matrix():
    global prob
    prob = []
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            prob.append([])
            for num in row:
                prob[len(prob) - 1].append(float(num))

    # Read list of pre-generated names. Names should be stored one per line in file.

    with open('./allnames.csv', newline='', encoding='utf-8') as csvfile:
        name_reader = csv.reader(csvfile, delimiter=',', quotechar='|')  # Record file contents.
        for names in name_reader:  # Loop over names in list.
            name = names[0].split(';')[1]
            # Loop over letters in the current name.
            print(name)
            for i in range(0, len(name) - 1):
                letter1 = name[i]
                letter2 = name[i + 1]
                num1 = 0
                num2 = 0
                for i in range(0, len(alphabet)):
                    if letter1 == alphabet[i].lowerchar or letter1 == alphabet[i].upperchar:
                        num1 = alphabet[i].num
                    if letter2 == alphabet[i].lowerchar or letter2 == alphabet[i].upperchar:
                        num2 = alphabet[i].num
                # Add one to the number of times letter number i is followed by letter number i+1.
                prob[num1][num2] += 1

    # Normalize the probability matrix.
    prob = normalize(prob)
    # Write probability matrix to file. This file will be read by the name generator.
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(0, len(alphabet)):
            writer.writerow(prob[i])


def get_name(s):
    name = ''
    loop = True
    while loop:
        name2 = make_name()
        if s == 'female':
            if name2[0][-1] == 'а' or name2[0][-1] == 'я' or name2[0][-1] == 'и':
                name = name2[0]
                loop = False
        elif s == 'male':
            name = name2[0]
            loop = False
    return name


if __name__ == '__main__':
    for nu in range(0, 250):
        name1 = make_name()
        if name1[0][-1] == 'а' or name1[0][-1] == 'я' or name1[0][-1] == 'и':
            print(name1[0], ' -ж')
        else:
            print(name1[0], ' -м')
    print(get_name('male'))

# input_string = "Was this a good  name? y/n"
# good = input(input_string)
# if good == "y":
#     for i in range(0, len(name1[1]) - 1):
#         prob[name1[1][i]][name1[1][i + 1]] *= 1.01
# if good == "n":
#     for i in range(0, len(name1[1]) - 1):
#         prob[name1[1][i]][name1[1][i + 1]] *= 0.99
#
# prob = normalize(prob)
#
# with open(file_name, 'w', newline='') as csvfile:
#     prob_writer = csv.writer(csvfile, delimiter=',',
#                              quotechar='|', quoting=csv.QUOTE_MINIMAL)
#     for i in range(0, len(alphabet)):
#         prob_writer.writerow(prob[i])
#
