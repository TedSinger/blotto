from blotto.strats import csv_spawn, spawn, dumb_spawn
from blotto.constants import N_PLAYERS, N_CASTLES
from blotto.game import Game


def run():
    game = Game([csv_spawn() for i in range(N_PLAYERS)], spawn)
    for i in range(1000):
        game.play_all()
        game.cull_and_spawn()

    print(game.meta())
    print(game)


def run_to_maturity():
    game = Game([csv_spawn() for i in range(N_PLAYERS)], spawn)
    while not meta_is_mature(game.meta()):
        print('iterating')
        for i in range(100):
            game.play_all()
            game.cull_and_spawn()

    print(game.meta())
    print(game)


def meta_is_mature(meta):
    return all(meta[i] < meta[i + 1] for i in range(N_CASTLES - 1))


if __name__ == '__main__':
    run_to_maturity()
