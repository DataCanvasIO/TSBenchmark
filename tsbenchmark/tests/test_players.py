from tsbenchmark.benchmark import load_players, Player, LocalBenchmark
from tsbenchmark.players import load_player, PythonEnv
from pathlib import Path

HERE = Path(__file__).parent


class TestLoadPlayer:

    def assert_palin_player(self, plain_player):
        assert plain_player.name == 'plain_player'
        env = plain_player.env
        assert env.venv_kind == 'custom_python'

    def test_load_builtin_players(self):
        players = load_players(['plain_player'])
        assert len(players) == 1
        plain_player: Player = players[0]
        self.assert_palin_player(plain_player)

    def test_load_external_custom_python_player(self):
        plain_player_dir = (HERE / "players" / "plain_player_custom_python").as_posix()
        plain_player = load_player(plain_player_dir)

        assert plain_player.name == 'plain_player_custom_python'
        env = plain_player.env
        assert env.venv_kind == 'custom_python'

    def test_load_external_reqs_txt_player(self):
        plain_player_dir = (HERE / "players" / "plain_player_requirements_txt").as_posix()
        plain_player = load_player(plain_player_dir)

        assert plain_player.name == 'plain_player_requirements_txt'
        env = plain_player.env

        assert env.venv_kind == PythonEnv.KIND_CONDA
        assert env.reqs_kind == PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT
        assert env.requirements.py_version == "3.8"
