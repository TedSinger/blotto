from blotto.game import numba_play
from blotto.main import run
import numpy


def testPlayDraw():
    s = numpy.array([100, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    assert numba_play(s, s) == 0


def testPlayVictory():
    loser = numpy.array([100, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    winner = numpy.array([99, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    assert numba_play(winner, loser) == 1
    assert numba_play(loser, winner) == -1


def testCloseGame():
    winner = numpy.array([1, 2, 3, 4, 5, 6, 79, 0, 0, 0])  # 28 points
    loser = numpy.array([0, 0, 0, 0, 0, 0, 0, 8, 9, 83])  # 27 points
    assert numba_play(winner, loser) == 1


def profile():
    import cProfile
    import pstats
    out = '/dev/shm/cProfile.out'
    cProfile.run('run()', filename=out)
    p = pstats.Stats(out)
    p.sort_stats('cumulative').print_stats(50)
