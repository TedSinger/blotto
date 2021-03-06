import numba
import numpy

from blotto.strats import Strategy
from blotto.constants import N_CASTLES, N_PLAYERS


def numpy_play(left: Strategy, right: Strategy) -> int:
    battles = left > right
    numpy.sign(battles, out=battles)
    points = numpy.array(range(1, N_CASTLES + 1))
    numpy.multiply(battles, points, out=battles)
    score = battles.sum()
    return numpy.sign(score)


@numba.jit
def numba_play(left: Strategy, right: Strategy) -> int:
    # it's fast
    score = 0
    for i in range(N_CASTLES):
        if left[i] > right[i]:
            score += i + 1
        elif left[i] < right[i]:
            score -= i + 1
    return numpy.sign(score)


class Game(object):
    def __init__(self, spawn_func, breed_func, cull_ratio=5):
        self.spawn_func = spawn_func
        self.breed_func = breed_func
        self.cull_ratio = cull_ratio

        self.strats = [self.spawn_func() for i in range(N_PLAYERS)]
        self.generations = [0] * N_PLAYERS
        self.scores = [0] * N_PLAYERS
        self._played = False
        self.sorted_strat_indices = [0] * N_PLAYERS

    def reset_scores(self):
        self.scores = [0] * N_PLAYERS
        self.sorted_strat_indices = [0] * N_PLAYERS
        self._played = False

    def __repr__(self):
        self.play_all()
        lines = [f'{self.strats[stratIdx]}: {self.generations[stratIdx]:.2f}: {self.scores[stratIdx]/N_PLAYERS:.2f}' for
                 stratIdx in self.sorted_strat_indices]
        return '\n'.join(lines + ['strat                            gen   score', f'meta: {self.meta()}'])

    def meta(self):
        self.play_all()
        winners = self.sorted_strat_indices[N_PLAYERS // 2:]
        avg = numpy.zeros(N_CASTLES)
        for w in winners:
            avg += self.strats[w]
        avg /= (N_PLAYERS // 2)
        numpy.round(avg, decimals=1, out=avg)
        return avg

    def play_all(self):
        if not self._played:
            self._play_all()
            self._played = True

    def _play_all(self):
        triples = [(i, j, numba_play(self.strats[i], self.strats[j])) for i in range(N_PLAYERS) for j
                   in range(i + 1, N_PLAYERS)]
        for i, j, result in triples:
            self.scores[i] += result
            self.scores[j] -= result
        self.sorted_strat_indices = sorted(range(N_PLAYERS), key=self.scores.__getitem__)

    def cull_and_spawn(self):
        """
        The worst are replaced. Half of them are replaced by breeding the best survivors, half are replaced by new entries
        """
        for death_idx in range(N_PLAYERS // self.cull_ratio):
            if death_idx % 2:
                self.strats[self.sorted_strat_indices[death_idx]] = self.spawn_func()
                self.generations[self.sorted_strat_indices[death_idx]] = 0
            else:
                breeder_1 = self.sorted_strat_indices[N_PLAYERS - death_idx // 2 - 1]
                breeder_2 = self.sorted_strat_indices[
                    ((self.cull_ratio - 1) * N_PLAYERS) // self.cull_ratio + death_idx // 2]

                child = self.breed_func(self.strats[breeder_1], self.strats[breeder_2])
                self.strats[self.sorted_strat_indices[death_idx]] = child

                nextGen = 1 + (self.generations[breeder_1] + self.generations[breeder_2]) / 2
                self.generations[self.sorted_strat_indices[death_idx]] = nextGen

        self.reset_scores()
