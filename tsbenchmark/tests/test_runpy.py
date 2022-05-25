import sys
from pathlib import Path
import tempfile

from tsbenchmark.players import PythonEnv
from tsbenchmark.tests.test_benchmark import need_conda, get_conda_home
import subprocess
from hypernets.utils.common import generate_short_id

PWD = Path(__file__).parent


run_py_file_path = PWD.parent / "run_py.sh"


@need_conda
def test_conda_yaml_env():

    env_name = generate_short_id()
    conda_home = get_conda_home()
    conda_env_temp_yaml_path = PWD / "run_py" / "conda_yaml" / "env.yaml"

    # generate env file
    conda_env_yaml_path_fd, conda_env_yaml_file = tempfile.mkstemp(suffix=".yaml")
    with open(conda_env_temp_yaml_path, 'r') as f:
        env_content = f.read().replace("#ENV_NAME#", env_name)
    with open(conda_env_yaml_file, 'w') as f:
        print("env_content")
        print(env_content)
        f.write(env_content)

    print(f"generated env file path: {conda_env_yaml_file}")

    py_path = PWD / "run_py" / "conda_yaml" / "validate.py"
    command = f"/bin/bash -x {run_py_file_path} --venv-kind={PythonEnv.KIND_CONDA}" \
              f" --requirements-kind={PythonEnv.REQUIREMENTS_CONDA_YAML} " \
              f" --venv-name={env_name} --requirements-yaml-file={conda_env_yaml_file}" \
              f" --python-script={py_path.as_posix()}"
    print(command)
    status, output = subprocess.getstatusoutput(command)
    print("output")
    print(output)
    assert status == 0

    # assert python path
    assert (Path(conda_home) / "envs" / env_name / "bin" / "python").exists()


def test_custom_python():

    py_path = PWD / "run_py" / "conda_yaml" / "validate.py"
    command = f"/bin/bash -x {run_py_file_path} --venv-kind={PythonEnv.KIND_CUSTOM_PYTHON}" \
              f" --requirements-kind={PythonEnv.REQUIREMENTS_CONDA_YAML} " \
              f" --custom-py-executable={sys.executable}" \
              f" --python-script={py_path.as_posix()}"
    print(command)
    status, output = subprocess.getstatusoutput(command)
    print("output")
    print(output)
    assert status == 0


@need_conda
def test_conda_requirement_txt():
    py_path = PWD / "run_py" / "requirement_txt" / "validate.py"

    requirement_txt_path = PWD / "run_py" / "requirement_txt" / "requirements.txt"
    venv_name = generate_short_id()

    command = f"/bin/bash -x {run_py_file_path} --venv-kind={PythonEnv.KIND_CONDA}" \
              f" --requirements-kind={PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT} " \
              f" --venv-name={venv_name} " \
              f" --requirements-txt-file={requirement_txt_path.as_posix()} " \
              f" --requirements-txt-py-version=3.7" \
              f" --python-script={py_path.as_posix()}"
    print(command)
    status, output = subprocess.getstatusoutput(command)
    print("output")
    print(output)
    assert status == 0
    # assert python path
    conda_home = get_conda_home()
    assert (Path(conda_home) / "envs" / venv_name / "bin" / "python").exists()
