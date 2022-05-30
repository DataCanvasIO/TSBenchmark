## Custom Player Examples

A player generally contains a Python script `exec.py` and a Python environment description file `player.yaml`. The directory structure of a player looks like below:
```shell
.
├── exec.py
└── player.yaml
```

- `exec.py` is used to read tasks, train tasks and evaluate indicators according to the API provided by TSBenchmark. 
For more information, please refer to the documentation [tsbechmark api]()
- `player.yaml` describes the player's Python operating environment and relevant configuration information 

A comprehensive example of how to define a player is described in [Quick start](quickstart.md). 
Besides, TSBenchmark have packaged some algorithms into players.  please refer to [Player list](https://github.com/DataCanvasIO/TSBenchmark/tree/main/players).


### Custom Player Operating Environment 

It's possible to run `exce.py` file in the user-defined Python environment. In this case, user needs to set the argument `env.venv.kind` as `custom_python`,
and put the Python executable file path after `env.venv.config.py_executable`.

`player.yaml` configuration example：
```yaml
env:
  venv:
    kind: custom_python  # set the environment as custom Python environment 
  config:
    py_executable: /usr/bin/local/python  # set the Python executive file path; otherwise use the default path
```

### Define Operating Environment with `requirement.txt`

Player could use the pip dependent file [requirement.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/) to define the operating environment, which states all dependent packages.
In this case, set the virtual environment as `conda` and set the dependency file format as `requirements_txt`. Then, benchmark will run in the virtual environment created by conda and install the dependent packages by pip.

`player.yaml` configuration example：
```yaml
env:
  venv:
    kind: conda  # use conda to manage the virtual environment
    config:
      name: plain_player_requirements_txt  # name of the virtual environment
  requirements:
    kind: requirements_txt  # define dependency file format as `requirements_txt`
    config:
      py_version: 3.8  # define python version
      file_name: requirements.txt  # file name 
```

The file `requirements.txt` contains the information of dependent packages in the Python virtual environment.
```
tsbenchmark
numpy >=0.1 
```

### Define Operating Environment with `.yaml` 

`conda` could export virtual environment to a `.yaml` file which can also be used to define the player's Python virtual environment. The export method is written in [Sharing an environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment
), 

`player.yaml` configuration example：
```yaml
env:
  venv:
    kind: conda  # use conda to manage the virtual environment
  requirements:
    kind: conda_yaml  # use conda_yaml to manage the dependency packages
    config:
      file_name: env.yaml  # conda yaml file name
```

NOTE: The virtual environment name has been included in the yaml file. Therefore, there is no need to define via `env.venv.config.name`.

`env.yaml` contains the information of dependent packages in the Python virtual environment.
```yaml
name: plain_player_conda_yaml
channels:
  - defaults
dependencies:
  - pip
  - pip:
      - tsbenchmark
```

### Define Task Types

`tsbenchmark` currently supports univariate and multivariate forecast tasks.  The custom player could define the task type via the argument `tasks`.

```yaml
env:
  venv:
    kind: custom_python
tasks:  # define the task type 
  - univariate-forecast  # options: univariate-forecast, multivariate-forecast 

```

### Define Randomness

If the algorithms have randomness, the benchmark is able to assign trial times to each task in order to improve the robustness and accuracy.
If the algorithms have no randomness, the benchmark will run only once. The example of setting randomness is shown below:
```yaml
env:
  venv:
    kind: custom_python
random:  false # default is true. false means the player has no randomness
```