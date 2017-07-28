from random import randint
from math import log
import os


from utility import shift_bit_length


def create_groups(numbers, seeded_players):
    total = shift_bit_length(numbers)
    seeded_players = shift_bit_length(seeded_players)
    group = []
    list_remaining = list(range(1, total + 1))
    for i in range(1, seeded_players + 1):
        group.append([i])
        list_remaining.remove(i)
    last_group = 0
    for i in range(numbers + 1, total + 1):
        group[last_group].append(i)
        last_group = (last_group + 1) % seeded_players
        list_remaining.remove(i)

    for i in range(seeded_players):
        while len(group[i]) < int(total / seeded_players):
            next_player = list_remaining[randint(0, len(list_remaining) - 1)]
            list_remaining.remove(next_player)
            group[i].append(next_player)
    sorting = [group[0], group[1]]
    group = group[2:]

    for i in range(2, int(log(seeded_players, 2)) + 1):
        next_group = 2 ** i - max(2 ** (i - 1), 2)
        safety = sorting + [[]] * len(sorting)
        for k in range(len(sorting)):
            safety[2 * k] = sorting[k]
            if k > 0:
                safety[2 * k - 1] = []
        sorting = safety
        picked = []
        for j in range(next_group):
            picking = randint(0, next_group - 1)
            while picking in picked:
                picking = randint(0, next_group - 1)
            picked.append(picking)
            sorting[j * 2 - 1] = group[picking]
        group = group[next_group:]
    return sorting


def create_schedule(numbers, seeded_players, start_date=1):
    sorting = create_groups(numbers, seeded_players)
    final = []
    for i in range(len(sorting)):
        final += sorting[i]
    sub_set = final[int(len(final) / 2):]
    sub_set = sub_set[::-1]
    final = final[:int(len(final) / 2)] + sub_set
    days = [(start_date + x * 2) % 7 for x in range(int(log(numbers, 2)))]
    if days[len(days) - 1] == 6 or days[len(days) - 1] == 1:
        days[len(days) - 1] = 0
    # TODO: Write these details to a file?
    return final, days


def run_competition(numbers, seeded_players, qualification_rounds=None, start_date=1):
    schedule = create_schedule(numbers, seeded_players)
    # TODO: Change this to read this information from a file.
    # TODO: Should not run each round in quick succession but stagger them out.
    qualification_rounds = numbers if qualification_rounds is None else qualification_rounds
    players_left = schedule
    print(players_left)
    rounds_played = 0

    while len(players_left) > 1 and rounds_played < qualification_rounds:
        rounds_played += 1
        next_round = []
        for i in range(int(len(players_left) / 2)):
            score_one = randint(0, 100) + players_left[2 * i] + 200 * (players_left[2 * i] > numbers)
            score_two = randint(0, 100) + players_left[2 * i + 1] + 200 * (players_left[2 * i + 1] > numbers)
            print("{}: {} Vs {} :{}".format(players_left[2 * i], score_one, score_two, players_left[2 * i + 1]))
            if score_one < score_two:
                next_round.append(players_left[2 * i])
            else:
                next_round.append(players_left[2 * i + 1])
        players_left = next_round
        print("")
        print(players_left)
    print(players_left)
    return players_left

run_competition(24, 8, 4)
