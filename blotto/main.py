from blotto.strats import csv_spawn, random_spawn, dumb_spawn, random_breed
from blotto.constants import N_PLAYERS, N_CASTLES
from blotto.game import Game


def run():
    game = Game(csv_spawn, random_breed, cull_ratio=5)
    for i in range(2000):
        if i % 100 == 0:
            print(i)
        game.play_all()
        game.cull_and_spawn()
    return game


def run_to_maturity():
    game = Game(csv_spawn, random_breed, cull_ratio=5)
    while not meta_is_mature(game.meta()):
        print('iterating...')
        for i in range(100):
            game.play_all()
            game.cull_and_spawn()
    return game



def meta_is_mature(meta):
    return all(meta[i] < meta[i + 1] for i in range(N_CASTLES - 1))


if __name__ == '__main__':
    print(run())
