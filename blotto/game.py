import numba
import numpy
from typing import List

from blotto.strats import Strategy, breed
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
    def __init__(self, strats: List[Strategy], spawn_func):
        self.strats = strats
        self.scores = [0] * N_PLAYERS
        self.spawn_func = spawn_func
        self._played = False
        self.sorted_scores = [0] * N_PLAYERS

    def reset_scores(self):
        self.scores = [0] * N_PLAYERS
        self.sorted_scores = [0] * N_PLAYERS
        self._played = False

    def __repr__(self):
        self.play_all()
        pairs = zip(self.strats, self.scores)
        ordered_pairs = sorted(pairs, key=lambda both: both[1])
        strs = [f'{strat}: {score}' for strat, score in ordered_pairs]
        return '\n'.join(strs)

    def meta(self):
        self.play_all()
        winners = self.sorted_scores[N_PLAYERS // 2:]
        avg = numpy.zeros(N_CASTLES)
        for w in winners:
            avg += self.strats[w]
        avg /= (N_PLAYERS // 2)
        numpy.round(avg, decimals=1, out=avg)
        print(avg)
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
        self.sorted_scores = sorted(range(N_PLAYERS), key=self.scores.__getitem__)

    def cull_and_spawn(self):
        """
        The worst half are replaced. Half of them are replaced by breeding survivors, half are replaced by new entries
        """
        for death_idx in range(N_PLAYERS // 4):
            breeder_1 = self.sorted_scores[N_PLAYERS - death_idx - 1]
            breeder_2 = self.sorted_scores[N_PLAYERS // 2 + death_idx]
            child = breed(self.strats[breeder_1], self.strats[breeder_2])
            self.strats[self.sorted_scores[death_idx]] = child
        for death_idx in range(N_PLAYERS // 4, N_PLAYERS // 2):
            self.strats[self.sorted_scores[death_idx]] = self.spawn_func()
        self.reset_scores()
