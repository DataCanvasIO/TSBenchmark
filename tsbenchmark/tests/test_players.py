import sys

from tsbenchmark.benchmark import Player
from tsbenchmark.players import PythonEnv
from pathlib import Path

from tsbenchmark.tests.players import load_test_player

HERE = Path(__file__).parent


class TestLoadPlayer:

    def assert_palin_player(self, plain_player):
        assert plain_player.name == 'plain_player'
        env = plain_player.env
        assert env.venv_kind == 'custom_python'

    def test_load_builtin_players(self):
        plain_player = load_test_player('plain_player')
        self.assert_palin_player(plain_player)

    def test_load_external_custom_python_player(self):
        plain_player = load_test_player("plain_player_custom_python")

        assert plain_player.name == 'plain_player_custom_python'
        env = plain_player.env
        assert env.venv_kind == 'custom_python'

    def test_load_plain_player_univariate(self):
        player = load_test_player("plain_player_univariate")
        assert player.name == 'plain_player_univariate'
        env = player.env
        assert env.venv_kind == 'custom_python'
        assert env.venv.py_executable == sys.executable
        assert set(player.tasks) == {"univariate-forecast"}

    def test_load_external_reqs_txt_player(self):
        plain_player = load_test_player("plain_player_requirements_txt")

        assert plain_player.name == 'plain_player_requirements_txt'
        env = plain_player.env

        assert env.venv.name == "plain_player_requirements_txt"
        assert env.venv_kind == PythonEnv.KIND_CONDA
        assert env.reqs_kind == PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT
        assert env.requirements.py_version == "3.8"

    def test_load_conda_yaml_player(self):
        plain_player = load_test_player("plain_player_conda_yaml")

        assert plain_player.name == 'plain_player_conda_yaml'
        env = plain_player.env

        assert env.venv.name == "plain_player_conda_yaml"
        assert env.venv_kind == PythonEnv.KIND_CONDA
        assert env.reqs_kind == PythonEnv.REQUIREMENTS_CONDA_YAML
        assert env.requirements.file_name == "env.yaml"

    def test_load_non_random_player(self):
        player = load_test_player("non_random_player_univariate")

        assert player.name == 'non_random_player_univariate'
        env = player.env
        assert env.venv_kind == PythonEnv.KIND_CUSTOM_PYTHON

        assert player.random is False
