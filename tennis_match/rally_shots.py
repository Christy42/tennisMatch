import random
import yaml


def shot_selection_effect(shot_skill, balance):
    if balance > -50 and random.random() < shot_skill / 800.0:
        return round(shot_skill / 5.0, 2)
    return 0


def applying_aggression(aggression, balance):
    with open("aggression.yaml", "r") as agg_file:
        table = yaml.safe_load(agg_file)
    section = ""
    for element in table["balance"]:
        if balance <= table["balance"][element]:
            section = element
            break

    number = random.random()
    cdf = 0
    for agg in table["probs"][aggression]:
        cdf += table["probs"][aggression][agg]
        if number < cdf:
            return agg + table["values"][section]
    print("ERROR, elements of table do not sum to 1")
    return random.randint(1, 10)


def rally_shot(skill, aggression, balance, shot_selection, mobility):
    shot_factor = 0.7 + balance / 500.0 + 6 * skill / 10000.0 + 3 * skill * mobility / 1000000.0 \
                  + (shot_selection * (10 - aggression / 2)) / 25000.0
    # print(shot_factor)
    shot_factor -= max((aggression - (skill + mobility / 3.0) / 27.0), 1.0) / 20.0 * (1 - shot_factor)
    shot_factor -= max((aggression - (skill + mobility / 3.0) / 27.0), 1.0) / 20.0 * (1 - shot_factor)
    # print(shot_factor)
    # print("X")
    return random.random() < shot_factor or random.random() * 1.5 < shot_factor


def rally(players, initial_balance, next_hit):
    shot_in = True
    player = next_hit
    count = 0
    balance = initial_balance
    eff_mobility = [players[0]["mobility"], players[1]["mobility"]]
    old_balance = balance
    balance_eff = 0
    while shot_in:
        agg = applying_aggression(players[player]["aggression"], balance)
        shot_in = rally_shot(players[player]["accuracy"], agg, balance, players[player]["shot selection"],
                             eff_mobility[player])
        if shot_in:
            old_balance = balance
            balance_eff = balance_change(players[player]["accuracy"], agg, balance, eff_mobility[(player + 1) % 2],
                                         players[player]["strength"]) + \
                shot_selection_effect(players[player]["shot selection"], agg)
            balance += balance_eff
        balance *= -1
        eff_mobility[player] = players[player]["mobility"] - 3 * agg
        balance = round(min(max(balance, -100.0), 100.0), 2)
        player = (player + 1) % 2

        count += 1
        # if count > 1:
        # print("{}:  {}:  {}".format(balance, old_balance, balance_eff))
    # print(next_hit)
    # print("End rally")
    return {"winner": player, "rally": count, "end_balance": balance}


def balance_change(skill, aggression, balance, mobility, strength):
    random_eff = random.randint(-20, 15)
    if balance > 0:
        return - balance / 5 + aggression * 1.9 * strength / 100 + strength / 20.0 + skill / 25.0\
               - max(min(mobility / 4.0, aggression * 1.5 + random_eff + skill / 19.0), 0) + random_eff
    else:
        return - balance / 2 * (balance > -50) + aggression * 1.9 * strength / 100 + strength / 20.0 + skill / 25.0\
               - max(min(mobility / 4.0, aggression * 1.5 + random_eff + skill / 19.0), 0) + random_eff
