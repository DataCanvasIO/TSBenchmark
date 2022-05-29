# TSBenchmark
[![Python Versions](https://img.shields.io/pypi/pyversions/hypergbm.svg)](https://pypi.org/project/hypergbm)
[![Downloads](https://pepy.tech/badge/hypergbm)](https://pepy.tech/project/hypergbm)
[![PyPI Version](https://img.shields.io/pypi/v/hypergbm.svg)](https://pypi.org/project/hypergbm)

[中文](README_zh_CN.md)

## What is TSBenchmark
Tsbenchmark is a distributed benchmark framework for time series forecasting (time series forecast) automatic machine learning (automl) algorithm.

## Overview
Tsbenchmark supports both the time series feature and the automl feature. The time series prediction algorithm supports univariate prediction, multivariate prediction, and covariate benchmark.
During operation, it supports the collection of optimal parameter combinations, providing support for the analysis of the automl framework.
The framework supports distributed operation mode and has efficient running scoring efficiency. The framework integrates the lightweight distributed scheduling framework in hypernets and can be run in Python or CONDA environments.
It is recommended to use CONDA as the environment management to support the environment isolation of different timing algorithms.

## Installation

### Pip

Basically, use the following 'pip' command to install tsbenchmark:
```bash
pip install tsbechmark
```

## Examples

### Develop your player.
  - tsbenchmark.yaml Benchmark global configuration
  - players 
    - am_navie_player: Algorithm specific directory.
    - exec.py: Required, Algorithm code to be tested.
    - player.yaml: Required, metadata settings of algorithm.

### [tsbenchmark.yaml](tsbenchmark/tests/benchmark.template.yaml) and [Examples](tsbenchmark/tests/benchmark_example_remote.yaml).

### exec.py 

Integrate the running code of the algorithm to be scored: obtain the task, train the model, predict and feed back the prediction results through the API interface.

```python
import tsbenchmark as tsb

task = tsb.api.get_task()
# Navie model see also players/plain_navie_player/exec.py
snavie = Navie().fit(task.get_train(), task.series_name)
df_forecast = snavie.predict(task.horizon)
tsb.api.send_report_data(task, df_forecast)
```

### player.yaml 

The personalized parameter setting of the algorithm can specify the running environment of the algorithm.
```yaml
env:
  venv:
    kind: custom_python
    config:
      py_executable: /usr/anaconda3/envs/tsb-hyperts/bin/python
```

For more usage examples, please refer to [Quick Start](https://tsbenchmark.readthedocs.io/zh_CN/latest/quickstart.html) and [Examples](https://tsbenchmark.readthedocs.io/zh_CN/latest/examples.html).

### Use TSBenchmark with Command line tools
```bash
tsb run --config benchmark_example_remote.yaml
```

```
tsb -h

usage: tsb [-h] [--log-level LOG_LEVEL] [-error] [-warn] [-info] [-debug]
           {run,compare} ...

tsb command is used to manage benchmarks

positional arguments:
  {run,compare}
    run                 run benchmark
    compare             compare benchmark reports

optional arguments:
  -h, --help            show this help message and exit

Console outputs:
  --log-level LOG_LEVEL
                        logging level, default is INFO
  -error                alias of "--log-level=ERROR"
  -warn                 alias of "--log-level=WARN"
  -info                 alias of "--log-level=INFO"
  -debug                alias of "--log-level=DEBUG"          
```

## DataSets reference
[data_desc](https://tsbenchmark.s3.amazonaws.com/datas/dataset_desc.csv)

## TSBenchmark related projects
* [Hypernets](https://github.com/DataCanvasIO/Hypernets): A general automated machine learning (AutoML) framework.
* [HyperGBM](https://github.com/DataCanvasIO/HyperGBM): A full pipeline AutoML tool integrated various GBM models.
* [HyperDT/DeepTables](https://github.com/DataCanvasIO/DeepTables): An AutoDL tool for tabular data.
* [HyperTS](https://github.com/DataCanvasIO/HyperTS): A full pipeline AutoML&AutoDL tool for time series datasets.
* [HyperKeras](https://github.com/DataCanvasIO/HyperKeras): An AutoDL tool for Neural Architecture Search and Hyperparameter Optimization on Tensorflow and Keras.
* [HyperBoard](https://github.com/DataCanvasIO/HyperBoard): A visualization tool for Hypernets.
* [Cooka](https://github.com/DataCanvasIO/Cooka): Lightweight interactive AutoML system.

## Documents

* [Overview](https://tsbenchmark.readthedocs.io/zh_CN/latest/index.html)
* [Concepts](https://tsbenchmark.readthedocs.io/zh_CN/latest/concepts.html)
* [Quick Start](https://tsbenchmark.readthedocs.io/zh_CN/latest/quickstart.html)
* [Examples](https://tsbenchmark.readthedocs.io/zh_CN/latest/examples.html)
* [API Reference](https://tsbenchmark.readthedocs.io/zh_CN/latest/api_docs/modules.html)
* [Release Notes](https://tsbenchmark.readthedocs.io/zh_CN/latest/release_note.html)

## DataCanvas
TSBenchmark is an open source project created by [DataCanvas](https://www.datacanvas.com/).
