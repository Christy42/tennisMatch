def basic_comm_line(names, sets_previous, current_set, current_game, server):
    old_sets = ""
    for element in sets_previous:
        old_sets += " {} : {}, ".format(element[0], element[1])
    current_score = " {}".format(current_game[0]) + (u"\u25cf" if server == 0 else "") + \
                    " : {}".format(current_game[1]) + (u"\u25cf:" if server == 1 else ":")
    print("{} vs {}: ".format(names[0], names[1]) + old_sets + " {} : {} ".format(current_set[0], current_set[1]) +
          current_score)


def calc_game_score(score):
    for i in range(2):
        if str(score[i]) == "0":
            score[i] = "Love"
        elif str(score[i]) == "1":
            score[i] = "15"
        elif str(score[i]) == "2":
            score[i] = "30"
        elif str(score[i]) == "3":
            score[i] = "40"
        elif int(score[i]) >= 3 and score[0] == score[1]:
            score[i] = "D"
        elif int(score[i]) > 3 and score[i] > score[(i + 1) % 2]:
            score[i] = "A"
        elif int(score[i]) > 3 and score[i] < score[(i + 1) % 2]:
            score[i] = "-"
        else:
            print("Error in game score")


def calc_special_moment(max_sets, game_score, server, old_set_scores, current_set_score, cur_tie_break):
    game_point = 0
    break_point = 0
    if game_score[server] >= 3 and game_score[server] > game_score[(server + 1) % 2]:
        game_point = game_score[server] - game_score[(server + 1) % 2]
    elif game_score[(server + 1) % 2] >= 3 and game_score[(server + 1) % 2] > game_score[server]:
        break_point = game_score[(server + 1) % 2] - game_score[server]
    if game_point == break_point == 0:
        return ""
    set_point = False
    if max(current_set_score) >= 5 and max(current_set_score) > min(current_set_score):
        if (game_point and (current_set_score[server] > current_set_score[(server + 1) % 2])) or \
           (break_point and (current_set_score[server] < current_set_score[(server + 1) % 2])):
            set_point = True
    else:
        return str(abs(game_score[server] - game_score[(server + 1) % 2])) + (" break" if break_point else " game") + \
               " point"

