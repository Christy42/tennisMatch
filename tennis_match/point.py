import random

from tennis_match import rally_shots, serve


def play_point(players, server, stats, returner=None):
    second_serve = False
    serve_aggression = players[server]["first serve aggression"]
    stats[server]["First Serve"] = 1 + stats[server].get("First Serve", 0)
    if not serve.serve_in(players[server]["first serve aggression"], players[server]["serve"]) > random.random():
        stats[server]["Second Serve"] = 1 + stats[server].get("Second Serve", 0)
        second_serve = True
        # Double Fault
        if not serve.serve_in(players[server]["second serve aggression"], players[server]["serve"]) > random.random():
            stats[server]["Double Fault"] = 1 + stats[server].get("Double Fault", 0)
            return {"winner": (server + 1) % 2, "stats": stats, "rally": 1}
        serve_aggression = players[server]["second serve aggression"]
    # Ace
    if serve.ace(serve_aggression, players[server]["serve"], players[server]["strength"],
                 players[(server + 1) % 2]["mobility"], players[server]["shot selection"]) > random.random():
        stats[server]["Ace"] = 1 + stats[server].get("Ace", 0)
        return {"winner": server, "stats": stats, "rally": 1}

    # Work out starting balance
    balance = serve.serve_balance(serve_aggression, players[server]["serve"],
                                  players[server]["strength"], players[(server + 1) % 2]["mobility"])
    balance -= rally_shots.shot_selection_effect(players[server]["shot selection"], 0)
    # Run through the rally itself
    result = rally_shots.rally(players, balance, (server + 1) % 2)
    serves_used = "Second" if second_serve else "First"
    won_serve = "Won" if result["winner"] == server else "Lost"
    stats[server][serves_used + " Serve " + won_serve] = 1 + stats[server].get(serves_used + " Serve " + won_serve, 0)
    return {"winner": result["winner"], "stats": stats, "rally": result["rally"] + 1}
