from pathlib import Path

from tsbenchmark.players import load_player


PWD = Path(__file__).parent


def load_test_player(name):
    player = load_player((PWD / name).as_posix())
    return player
