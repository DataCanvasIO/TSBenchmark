## Concepts

**Dataset**

`Dataset` includes the data and metadate used in benchmark execution process. They can be obtained by the `get_train` and `get_test` functions of `TsTask` for training and testing tasks respectively. 

The benchmark framework will download the dataset from cloud for the first time and save them to a cache directory for future use. The cache directory could be configured in file `benchmark.yaml`.


**Task**

`Task` means the training or testing tasks in `Benchmark`. They are used in `Player`. Tasks can be obtained by the `get_task` and `get_local_task` of the `tsbenchmark.api`.

`Task` consists of the following information:
- data，include training data and testing data
- metadata，include task type, data structure, horizon, time series field list, covariate field list, etc.
- training parameters，include random_state、reward_metric、max_trials, etc.


**Player**

`Player` is to run tasks。A player contains a Python script file and an operating environment description file. 
The Python script file could call functions from TSBenchmark api to obtain the dataset, specified task, training model, evaluation methods and so on.


**Benchmark**

`Benchmark` makes the `Player` performing specified `Task` and integrates the results into one `Report`.
These results have differences in running time, evaluation scores, etc.

TSBenchmark currently supports two kinds of Benchmark implementation： 
- LocalBenchmark: running Benchmark in local mode
- RemoteSSHBenchmark: running benchmark in remote mode through SSH


**Environment**

The operating environment of player can be either custom Python environment or virtual Python environment which are defined by the `requirement.txt` or `.yaml` file exported by conda respectively.


**Report**

`Report` is the valuable output of the `Benchmark`, It collects the results from players and generates a comparison report, which contains the comparison results of both different players same benchmark and same player different benchmarks.

The results include the forecast results and the performance indicators, such as smape, mae, rmse, mape, etc.






