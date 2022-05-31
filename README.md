# TSBenchmark
[![Python Versions](https://img.shields.io/pypi/pyversions/hypergbm.svg)](https://pypi.org/project/hypergbm)
[![Downloads](https://pepy.tech/badge/hypergbm)](https://pepy.tech/project/hypergbm)
[![PyPI Version](https://img.shields.io/pypi/v/hypergbm.svg)](https://pypi.org/project/hypergbm)

[中文](README_zh_CN.md)

## What is TSBenchmark
TSBenchmark is a distributed benchmark framework specified for time series forecasting tasks using automated machine learning (AutoML) algorithms.

## Overview
TSBenchmark supports both time series and AutoML characteristics.

As for time series forecasting, it supports univariate forecasting, multivariate forecasting, as well as covariate benchmark.
During operation, it collects the information of optimal parameter combinations, performance indicators and other key parameters, supporting the analysis and evaluation of the AutoML framework.

This benchmark framework supports distributed operation mode and shows high scores in efficiency ranking.
It integrates the lightweight distributed scheduling framework in hypernets and can be executed in both Python and CONDA virtual environments.
For the purpose of environment isolation, it is recommended to use CONDA as the environment manager to support different algorithms.

## Installation

### Pip

Basically, use 'pip' command to install tsbenchmark:
```bash
pip install tsbechmark
```

## Examples

### Define your player.
  - tsbenchmark.yaml:  the global Benchmark configuration
  - players 
    - am_navie_player: the specific algorithm directory.
    - exec.py: (Required), the algorithm to be tested.
    - player.yaml: (Required), metadata settings of the algorithm.

### [tsbenchmark.yaml](tsbenchmark/tests/benchmark.template.yaml) and [Examples](tsbenchmark/tests/benchmark_example_remote.yaml).

### exec.py 

Integrate the forecasting tasks for evaluation through API interface, including task reading, model training, prediction and evaluation.

```python
import tsbenchmark as tsb

task = tsb.api.get_task()
# Navie model see also players/plain_navie_player/exec.py
snavie = Navie().fit(task.get_train(), task.series_name)
df_forecast = snavie.predict(task.horizon)
tsb.api.send_report_data(task, df_forecast)
```

### player.yaml 

Use customized settings to specify the operating environment of the algorithm.
```yaml
env:
  venv:
    kind: custom_python
    config:
      py_executable: /usr/anaconda3/envs/tsb-hyperts/bin/python
```

For more examples, please refer to [Quick Start](https://tsbenchmark.readthedocs.io/en/latest/quickstart.html) and [Examples](https://tsbenchmark.readthedocs.io/en/latest/examples.html).

### Run TSBenchmark with Command Line Tools
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

* [Overview](https://tsbenchmark.readthedocs.io/en/latest/index.html)
* [Concepts](https://tsbenchmark.readthedocs.io/en/latest/concepts.html)
* [Quick Start](https://tsbenchmark.readthedocs.io/en/latest/quickstart.html)
* [Examples](https://tsbenchmark.readthedocs.io/en/latest/examples.html)
* [API Reference](https://tsbenchmark.readthedocs.io/en/latest/api_docs/modules.html)
* [Release Notes](https://tsbenchmark.readthedocs.io/en/latest/release_note.html)

## DataCanvas
TSBenchmark is an open source project created by [DataCanvas](https://www.datacanvas.com/).
