import random
import math


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
    if type(the_list) == list:
        the_list = {i: the_list[i] for i in range(len(the_list))}
    largest = max(the_list.values())
    for i in the_list:
        if the_list[i] == largest:
            return i


def arg_min(the_list):
    if type(the_list) == list:
        the_list = {i: the_list[i] for i in range(len(the_list))}
    smallest = min(the_list.values())
    for i in the_list:
        if the_list[i] == smallest:
            return i


def shift_bit_length(x):
    return 1 << (x-1).bit_length()


def calc_time_diff(new_week, new_year, old_week, old_year):
    new_time = new_year * 52 + new_week
    old_time = old_year * 52 + old_week
    difference = new_time - old_time
    return difference


def max_x_from_dict(dictionary, x):
    big_dict = {}
    for element in dictionary:
        big_dict.update({element: dictionary[element][key]})
        if len(big_dict) > x:
            del big_dict[arg_min(big_dict)]
    return big_dict


def smallest_missing_in_list(list_of_numbers):
    if not list_of_numbers:
        return 0
    lowest_fail = len(list_of_numbers)
    partial = list_of_numbers
    highest_pass = -1
    half = int(len(list_of_numbers) / 2)
    while lowest_fail - highest_pass > 1 and partial:
        if list_of_numbers[half] == half:
            partial = partial[half:]
            highest_pass = half
            half += max(int(len(partial) / 2), 1)
        else:
            partial = partial[:half]
            lowest_fail = half
            half -= max(int(len(partial) / 2), 1)
    return lowest_fail


def add_dict(dict_1, dict_2):
    dict_new = {}
    for element in set(list(dict_1.keys()) + list(dict_2.keys())):
        dict_new[element] = dict_1.get(element, 0) + dict_2.get(element, 0)
    return dict_new
