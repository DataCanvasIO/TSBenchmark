## 快速开始

使用pip安装tsbenchmark:
```
pip install tsbenchmark
```

以使用[prophet]()训练为例子定一个player，创建目录`prophet_player`，并在该目录创建`player.yaml`文件:
```yaml
env:
  venv:
    kind: conda  # 使用conda创建虚拟环境
  requirements:
    kind: conda_yaml  # 使用的conda 的yaml文件定义虚拟环境
    config:
      file_name: env.yaml 

tasks:  # 声明该player 仅支持单变量预测的任务
  - univariate-forecast
```

在目录`prophet_player`中创建`env.yaml` 文件，这个文件用来使用[conda]()创建虚拟环境，在player运行时使用。
```yaml
name: tsb_prophet_player
channels:
  - defaults
  - conda-forge
dependencies:
  - prophet
  - pip:
      - tsbenchmark
```

在目录`prophet_player`中创建`exec.py` 文件用来使用prophet训练任务：
```python
from prophet import Prophet

import tsbenchmark as tsb
import tsbenchmark.api


def main():
    task = tsb.api.get_task()
    print(task)
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=365)
    report_data = {'reward': 0.7}
    tsb.api.report_task(report_data=report_data)

if __name__ == "__main__":
    main()
```


由于player的运行环境需要使用使用[conda](https://docs.conda.io)创建，请先安装conda到`/opt/miniconda3`。

然后在当前目录创建Benchmark配置文件`benchmark.yaml`:
```yaml
name: 'benchmark_example'
desc: 'local benchmark run prophet'

kind: local

players:
  - ./prophet_player

datasets:
  filter:
    tasks:
      - univariate-forecast
    data_sizes:
      - small

random_states: [ 23163 ]

constraints:
  task:
    reward_metric: rmse

venv:
  conda:
    home: /opt/miniconda3
```

当前目录的结构应该为：
```
.
├── benchmark.yaml
└── prophet_player
    ├── env.yaml
    ├── exec.yaml
    └── player.yaml
```

运行该benchmark:
```shell
$ tsb run --config ./benchmark.yaml
```
运行结束后可以去`./report` 目录查看生成的测试报告。
