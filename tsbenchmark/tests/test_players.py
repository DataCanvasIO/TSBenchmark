from tsbenchmark.benchmark import load_players, Player, LocalBenchmark
from tsbenchmark.players import load_player
from pathlib import Path
HERE = __file__


def assert_palin_player(plain_player):

    assert plain_player.name == 'plain_player'
    env = plain_player.env
    assert env.kind == 'custom_python'
    assert env.custom_python['executable'] == 'python'


def test_load_builtin_players():
    players = load_players(['plain_player'])
    assert len(players) == 1
    plain_player: Player = players[0]
    assert_palin_player(plain_player)


def test_load_external_players():
    plain_player_dir = (Path(HERE).parent.parent.parent / "players" / "plain_player").as_posix()
    plain_player = load_player(plain_player_dir)
    assert_palin_player(plain_player)
