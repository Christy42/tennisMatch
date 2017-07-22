import random


def diff(elements):
    return abs(elements[0] - elements[1])


def divide_diff_by_int(dictionary, number):
    for first_tier in dictionary:
        for element in dictionary[first_tier]:
            dictionary[first_tier][element] /= float(number)

    return dictionary


def repeated_random(lower, upper, rolls):
    total = 0
    for _ in range(rolls):
        total += random.randint(lower, upper)

    return total / float(rolls)
