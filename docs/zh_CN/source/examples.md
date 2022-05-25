## 使用示例

## 自定义Players

player 通常会包含一个描述文件`player.yaml`和一个python脚本`exec.py`，一个player的目录结构看起来想像是：
```shell
.
├── exec.py
└── player.yaml
```

`exec.py`脚本来用读取任务、训练任务、和评估指标；`player.yaml`用来描述player的python运行环境和其他配置信息。

### 自定义运行环境Player

player.yaml
```yaml
env:
  venv:
    kind: custom_python
```

### 使用 requirement.txt 定义运行环境

player.yaml
```yaml
env:
  venv:
    kind: conda
    config:
      name: plain_player_requirements_txt
  requirements:
    kind: requirements_txt
    config:
      py_version: 3.8
      file_name: requirements.txt
```

requirements.txt:
```
tsbenchmark
numpy >=0.1
```

### 使用 conda yaml 文件定义运行环境
player.yaml
```yaml
env:
  venv:
    kind: conda
  requirements:
    kind: conda_yaml
    config:
      file_name: env.yaml

```

env.yaml
```yaml
name: plain_player_conda_yaml
channels:
  - defaults
dependencies:
  - pip
  - pip:
      - tsbenchmark
```

## Benchmark

### 在本机运行的Benchmark

```yaml
name: 'benchmark_example_local'
desc: 'hyperts V0.1.0 release benchmark on 20220321'

kind: local

players:
  - players/hyperts_dl_player
  - tsbenchmark/tests/players/plain_player_requirements_txt

datasets:
  filter:
    tasks:
      - univariate-forecast
    data_sizes:
      - small

random_states: [ 23163,4,5318,9527,33179 ]

constraints:
  task:
    max_trials: 10
    reward_metric: rmse

report:
  path: ~/benchmark-output/hyperts


batch_application_config:
  server_port: 8060
  server_host: localhost
  scheduler_interval: 1
  scheduler_exit_on_finish: True


venv:
  conda:
    home: ~/miniconda3/
```

### 过滤任务
### 配置约束条件
### 设置随机数
### 在远程运行的Benchmark
 ```yaml
name: 'benchmark_example_remote'
desc: 'hyperts V0.1.0 release benchmark on 20220321'

kind: remote

players:
  - players/hyperts_dl_player
  - tsbenchmark/tests/players/plain_player_requirements_txt

datasets:
  filter:
    tasks:
      - univariate-forecast
      - multivariate-forecast
    data_sizes:
      - small


n_random_states: 5

constraints:
  task:
    max_trials: 10
    reward_metric: rmse
  filter:
    tasks:
      - univariate-forecast
      - multivariate-forecast
    data_sizes:
      - small
report:
  path:  ~/benchmark-output/hyperts


batch_application_config:
  server_port: 8060
  server_host: localhost
  scheduler_interval: 1
  scheduler_exit_on_finish: True

working_dir: /tmp/tsbenchmark-hyperctl

machines:
  - connection:
        hostname: host1
        username: hyperctl
        password: hyperctl
    environments:
      TSB_CONDA_HOME: ~/miniconda3/
 ```