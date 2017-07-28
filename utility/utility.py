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


def add_lists(list_one, list_two):
    sum_list = []
    for i in range(len(list_one)):
        sum_list.append(list_one[i] + list_two[i])
    return sum_list


def arg_max(the_list):
    largest = max(the_list)
    for i in range(len(the_list)):
        if the_list[i] == largest:
            return i
