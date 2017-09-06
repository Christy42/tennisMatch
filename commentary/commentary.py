def basic_comm_line(names, sets_previous, current_set, current_game, server):
    # TODO: Find out what happened for the last point, rally length, winner, how big of a turn around it was
    # TODO: Then use here in some sort of look up
    # TODO: Come up with a definition of winner, error.  Just a basic one that can be refined later on.
    pass


def calc_game_score(score):
    score_map = {0: "Love", 1: "15", 2: "30", 3: "40"}
    com_score = [score_map.get(int(score_map[i], i)) for i in score]
    if int(min(score)) >= 3:
        com_score = ["D", "D"] if score[0] == score[1] \
            else ["A" if score[0] > score[1] else "-", "A" if score[0] < score[1] else "-"]
    return com_score