from tsbenchmark.benchmark import load_players, PlayerSpec, LocalBenchmark


def test_load_players():
    players = load_players(['plain_player'])
    assert len(players) == 1
    plain_player: PlayerSpec = players[0]
    assert plain_player.name == 'plain_player'
    env = plain_player.env
    assert env.kind == 'custom_python'
    assert env.custom_python['executable'] == '/usr/bin/python'


def test_run_benchmark():
    players = load_players(['plain_player'])
    lb = LocalBenchmark(name='name', desc='desc', players=players, constraints={})

    lb.run()

