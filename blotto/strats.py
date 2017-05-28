import random
import numpy
import pandas
from typing import Tuple

from blotto.constants import N_SOLDIERS, N_CASTLES

Strategy = numpy.ndarray


def dumb_spawn() -> Strategy:
    return numpy.array([100, 0, 0, 0, 0, 0, 0, 0, 0, 0])


def get_csv_strats():
    df = pandas.read_csv('data/538-castles.csv')
    return [numpy.array(row.tolist()) for _, row in df.iterrows()]


CSV_STRATS = get_csv_strats()


def csv_spawn() -> Strategy:
    return random.choice(CSV_STRATS)


def random_spawn() -> Strategy:
    strat = numpy.random.random(N_CASTLES)
    strat /= strat.sum()
    strat *= N_SOLDIERS
    numpy.round(strat, out=strat)  # some are rounded up!!
    strat = numpy.int64(strat)
    for i in range(10):
        diff = N_SOLDIERS - strat.sum()
        if diff >= 0:
            strat[i] += diff
            break
        elif strat[i] < -diff:
            strat[i] = 0
        else:
            strat[i] += diff
            break
    validate_strategy(strat)
    return strat


def breed(left: Strategy, leftGen: float, right: Strategy, rightGen: float) -> Tuple[Strategy, float]:
    """
    Start with no soldiers.
    Repeat until all soldiers consumed:
        Pick a castle at random
        If that castle has no soldiers, add enough to beat one parent
        Otherwise, add enough to beat both parents, and never choose that castle again
    """
    strat = numpy.zeros(N_CASTLES, dtype=numpy.int64)
    soldiers_spent = 0
    castle_choices = list(range(N_CASTLES)) * 2  # each castle can be chosen twice
    numpy.random.shuffle(castle_choices)
    mins = numpy.minimum(left, right)
    maxes = numpy.maximum(left, right)
    for castle in castle_choices:
        if strat[castle] == 0:
            soldiers = min(mins[castle] + 1, N_SOLDIERS - soldiers_spent)
            strat[castle] = soldiers
            soldiers_spent += soldiers
        else:
            soldiers_spent -= strat[castle]
            soldiers = min(maxes[castle] + 1, N_SOLDIERS - soldiers_spent)
            strat[castle] = soldiers
            soldiers_spent += soldiers
        if soldiers_spent == N_SOLDIERS:
            break
    validate_strategy(strat)
    return strat, 1 + (leftGen + rightGen) / 2


def validate_strategy(strat: Strategy):
    assert isinstance(strat, numpy.ndarray)
    assert strat.dtype == numpy.int64
    assert sum(strat) == N_SOLDIERS
    assert len(strat) == N_CASTLES
