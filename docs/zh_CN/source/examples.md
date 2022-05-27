## 使用示例

## 自定义Players示例

player 通常会包含一个描述文件`player.yaml`和一个python脚本`exec.py`，一个player的目录结构看起来想像是：
```shell
.
├── exec.py
└── player.yaml
```

- `exec.py`脚本来借助tsbenchmark提供的api完成读取任务、训练任务、和评估指标，api用法参考[tsbechmark api文档]()
- `player.yaml`用来描述player的python运行环境和其他配置信息。

完整定义player例子请参考[快速开始](quickstart.md)。

### 自定义运行环境Player

运行player的exec.py文件时可以指定使用已经安装好的python环境。这种情况下benchmark运行时候不会再为player创建虚拟环境，而是使用指定的python环境运行。
使用自定义的python环境需要将player的配置项`env.venv.kind`设置为`custon_python`，并通过`env.venv.config.py_executable` 设置python可执行文件路径。

player.yaml 配置示例：
```yaml
env:
  venv:
    kind: custom_python  # 设置python环境类型为自定义python环境 
  config:
    py_executable: /usr/bin/local/python  # 设置python可执行文件路径，如果为空将使用默认路径。

```

### 使用requirement.txt定义运行环境

player可以使用[pip的依赖文件格式requirement.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/)声明所需要的依赖库，benchmark运行时候会使用conda创建虚拟环境并使用[pip]()安装依赖。
如需要这种方式需要设置虚拟环境为`conda`，依赖声明的格式为`requirements_txt`，player.yaml 配置示例：
```yaml
env:
  venv:
    kind: conda  # 使用conda管理虚拟环境
    config:
      name: plain_player_requirements_txt  # 创建的conda虚拟环境的名称
  requirements:
    kind: requirements_txt  # 指定使用pip的依赖格式 `requirements.txt`
    config:
      py_version: 3.8  # 指定python版本
      file_name: requirements.txt  # 指定在player目录下的requirements文件的名称
```

配置项`env.requirements.config.file_name`的requirements.txt文件，该文件中指定了player虚拟python环境的依赖库:
```
tsbenchmark
numpy >=0.1 
```

### 使用 conda yaml 文件定义运行环境

conda 可以将虚拟环境导出成yaml文件，参考[Sharing an environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment
), 导出的yaml文件可以用用来定义player的虚拟python环境。 player.yaml 配置示例：
```yaml
env:
  venv:
    kind: conda  # 使用conda管理虚拟环境
  requirements:
    kind: conda_yaml  # 设置使用 conda_yaml 格式管理依赖库
    config:
      file_name: env.yaml  # 指定 conda yaml文件的文件名
```

注意: conda的yaml文件中已经包含虚拟环境的名称，不必再通过`env.venv.config.name`配置虚拟环境的名称。

配置项`env.requirements.config.file_name`的env.yaml文件，该文件中指定了player虚拟python环境的依赖库:
```yaml
name: plain_player_conda_yaml
channels:
  - defaults
dependencies:
  - pip
  - pip:
      - tsbenchmark
```

### 指定Player支持的任务类型

目前tsbenchmark集成的任务有单变量预测，多变量预测等。自定义的Player如果只只是其中一个或多个任务类型可以在player的配置文件中进行声明。
Benchmark运行时只会给Player分配它能支持的任务类型。可以在player配置文件中的`tasks`配置项指定它所支持的任务类型：

```yaml
env:
  venv:
    kind: custom_python
tasks:  # 指定player支持的任务类型
  - univariate-forecast  # 指定仅支持单变量任务，可选的值有: univariate-forecast, multivariate-forecast 

```

### 指定Player是否有随机性

如果训练算法有随机性，Benchmark运行时可以对每个任务分配不同的随机数跑多次来评估算法的稳定性和增加结果的准确性。
如果算法没有随机性，那么Benchmark仅运行Player一次即可。可以通过player的配置属性`random` 来设置player是否有随机性。以设置player没有随机性为例：
```yaml
env:
  venv:
    kind: custom_python
random:  false # 可选true 或者 false 指定player是否有随机性。默认值为true
```



## Benchmark示例

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