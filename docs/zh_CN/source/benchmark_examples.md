## Benchmark示例

tsbenchmark 提供了命令行工具`tsb`命令管理Benchmark。
可以使用yaml格式的配置文件定义benchmark。使用tsb命令运行benchmark：

```shell
$ tsb run --config <benchmark_config_file>
```

### 单机模式运行的Benchmark
在单机模式下运行Benchmark，这种模式下训练任务都将在当前机器上进行。
将benchmark配置文件中的配置项`kind`设置为 `local` 使用单机模式：

```yaml
name: 'benchmark_example_local' # benchmark 的名称，建议仅使用数字、大小写字母、下划线、中划线。
desc: 'a local benchmark example'

kind: local  # 设定为单机模式

players:  # 指定运行benchmark的player目录
  - players/hyperts_dl_player

random_states: [23163, 5318, 9527] # 使用随机数跑多轮

```

### 单机模式设置conda安装目录

如果player有使用conda虚拟环境的，需要配置conda的安装目录，Benchmark在运行的时候可以使用指定的conda创建虚拟环境。
配置conda安装目录可以通过Benchmark配置文件中的配置项`venv.conda.home` 属性配置，以单机模式下将conda的安装目录配置到`/opt/miniconda3`为例：
```shell
name: 'benchmark_example_local' # benchmark 的名称，建议仅使用数字、大小写字母、下划线、中划线。
desc: 'a local benchmark example'

kind: local  # 设定为单机模式

players: 
  - players/hyperts_dl_player

datasets: 
  tasks_id:
    - 512754

random_states: [ 23163, 5318,9527,33179 ]

venv:
  conda:
    home: /opt/miniconda3  # 指定conda的安装目录
```

### 过滤数据集中的任务

可以对数据集中的任务设置过滤条件，可以指定一个或者多个条件。如果没有指定Benchmark将使用数据集中的所有任务，当前支持的筛选条件配置项：
- `datasets.filter.tasks`: 筛选任务类型，可以是1个多个，默认为空，代表选择所有任务类型
- `datasets.filter.data_sizes`: 筛选数据集的大小，可以是1个多个; 默认为空，代表选择所有大小类型的数据集文件; 可选 small, large
- `datasets.filter.tasks_id`: 指定任务的id
多个筛选条件之间的是"与"的关系。

筛选任务benchmark配置文件例子：

```yaml
name: 'benchmark_example_local'
desc: 'a local benchmark example'

kind: local

players: 
  - players/hyperts_dl_player

datasets:
  filter:
    tasks:  # 选择 univariate-forecast，multivariate-forecast 类型的任务
      - univariate-forecast
      - multivariate-forecast
    data_sizes:  # 选择文件大小为 small 的数据集
      - small
    tasks_id:  # 指定任务的id 
      - 512754

random_states: [ 23163, 5318,9527,33179 ]
```

### 配置约束条件

运行Benchmark可以设定一些约束条件。比如设置Player中的算法搜索的次数、评价指标等，以配置搜索次数(max_trials)和评价指标(reward_metric)为例：
```yaml
name: 'benchmark_example_local'
desc: 'a local benchmark example'

kind: local

players: 
  - players/hyperts_dl_player

random_states: [ 23163, 5318,9527,33179 ]

constraints:  
  task:  # 配置任务的运行约束条件
    max_trials: 10  # 设置最大搜索次数 
    reward_metric: rmse  # 设置 reward_metric
```


### 使用不同的随机数运行多轮
TSBenchmark可以让Player使用不同的随机数多次运行同一个任务，这样可以降低实验的随机性，并且评估Player中的算法的稳定性。
可以通过Benchmark的配置项`random_states`设置多个随机数。也可以使用配置项`n_random_states` 配置随机数的个数，由TSBenchmark 生成随机数，以使用`random_states` 配置随机数为例：
```yaml
name: 'benchmark_example_local'
desc: 'a local benchmark example'

kind: local

players: 
  - players/hyperts_dl_player

random_states: [ 23163, 5318,9527,33179 ]  # 配置4个随机数，每一个任务跑4轮

```

### 并行运行Benchmark

并行运行Benchmark可以利用多台机器加快Benchmark的运行进度。TSBenchmark可以将任务通过SSH协议分发的远程节点，这要求远程运行任务的节点需要运行SSH服务，并且提供链接帐号。
通过设置配置项`kind`为`remote`开启并行运行模式，然后需要通过配置项`machines` 添加远程机器的的链接信息和配置信息。如果运行的player中有使用到conda创建虚拟环境的，还需要在远程机器中安装好conda并配置conda的安装目录。
配置示例：

 ```yaml
name: 'benchmark_example_remote'
desc: 'a remote benchmark example'

kind: remote

players:
  - players/hyperts_dl_player

random_states: [ 23163, 5318,9527,33179 ] 

machines:  # 配置远程 SSH机器
  - connection:  # 配置机器的链接信息
        hostname: host1  # ip地址或者主机名
        username: hyperctl  # 用户名
        password: hyperctl  # 密码
    environments:
      TSB_CONDA_HOME: /opt/miniconda3  # 如果运行player使用使用conda创建虚拟环境，需要配置远程机器上conda的安装目录
 ```


### 重复运行Benchmark

当一个Benchmark重复运行时，之前运行结束（失败或者成功状态）的任务会被跳过不在运行。
如需重新运行Benchmark中的部分任务，可以删除该任务的状态文件。
任务成功的状态文件：`{working_dir}/batch/{job_name}.succeed`
任务失败的状态文件：`{working_dir}/batch/{job_name}.failed`

Benchmark运行时会将输出的数据、状态信息写入到`working_dir`中，若要一次Benchmark基于上一次Benchmark，需要确保这两次运行的Benchmark的`workking_dir`和`name`属性一致，配置示例：
```yaml
name: 'benchmark_example_local' # benchmark 的名称，建议仅使用数字、大小写字母、下划线、中划线。
desc: 'a local benchmark example'

kind: local 

working_dir: ～/tsbenchmark_working_dir/benchmark_example_local  # Benchmark 的工作目录，用于存放Benchmark运行产生的文件; 可以为空，默认为 `～/tsbenchmark_working_dir/{name}`

players: 
  - players/hyperts_dl_player

```
