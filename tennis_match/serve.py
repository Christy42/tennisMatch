from random import randint


def serve_balance(serve_aggression, serve, strength, mobility):
    balance = max(round(serve_aggression * 3 + serve / 15.0 + strength / 12.0 + randint(-15, +20) -
                        mobility / 8.0, 2), 0)
    return -balance


def serve_in(serve_aggression, serve):
    base = (100 - min(serve_aggression, 5) * 7.0 - 16.0 * max((serve_aggression - 5), 0)) / 100.0

    modification = 3.0 * float(serve) * float(serve_aggression * 10) / (100.0 * 100.0 * 4.0)
    return min(base + modification, 1.0 - serve_aggression * 0.01 * (1 - serve * 0.005))


def ace(serve_aggression, serve, strength, mobility, shot_selection):
    base_hit = strength * serve_aggression * serve_aggression / (1000.0 * 100.0)
    accuracy_boost = base_hit + (1 - base_hit) * (serve / 1500.0 + shot_selection / 2400.0)
    mobility_def = accuracy_boost * (100 - mobility * (10 - serve_aggression) / 18.0) / 100.0
    return mobility_def
