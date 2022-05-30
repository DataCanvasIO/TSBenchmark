## Benchmark Examples

TSBenchmark provides the command `tsb` to control every benchmark. The example below shows how to use `tsb` to run a benchmark configured by a `.yaml` file: 
```shell
$ tsb run --config <benchmark_config_file>
```

### Run Benchmark in Local Mode

Local mode means executing tasks in the local machine by setting the argument `kind` as `local`.

```yaml
name: 'benchmark_example_local' # name of benchmark
desc: 'a local benchmark example'

kind: local  # local mode

players:  # define the directory of the player
  - players/hyperts_dl_player

random_states: [ 23163,5318,9527,33179 ] # multiple runs with different random states

```

### Configure the Conda Installation Directory in Local Mode

When using the conda virtual environment, it needs to configure the conda installation directory. By setting the argument `venv.conda.home` to the directory `/opt/miniconda3`,
the benchmark will locate the directory and install the virtual environment accordingly. 
```shell
name: 'benchmark_example_local' # name of benchmark
desc: 'a local benchmark example'

kind: local  # local mode

players: 
  - players/hyperts_dl_player

datasets: 
  tasks_id:
    - 512754

random_states: [ 23163,5318,9527,33179 ]

venv:
  conda:
    home: /opt/miniconda3  # define the conda installation directory
```

### Select tasks

User could set different filtering conditions to select desired tasks. Benchmark provides the three types of conditions and each condition has multiple options.
- `datasets.filter.tasks`: select one or more task types, default (empty) means all types
- `datasets.filter.data_sizes`: select one or more data size types (small/large), default (empty) means all types 
- `datasets.filter.tasks_id`: define the task identifications

An example of tasks selection：

```yaml
name: 'benchmark_example_local'
desc: 'a local benchmark example'

kind: local

players: 
  - players/hyperts_dl_player

datasets:
  filter:
    tasks:  # select two task types: univariate-forecast，multivariate-forecast
      - univariate-forecast
      - multivariate-forecast
    data_sizes:  # select small-size dataset
      - small
    tasks_id:  # define task id
      - 512754

random_states: [ 23163, 5318,9527,33179 ]
```

### Configure Constraints 

Benchmark could set some constraints like the trial times of algorithm searching (`max_trials`), evaluation indicator definition (`reward_metric`) and so on.
```yaml
name: 'benchmark_example_local'
desc: 'a local benchmark example'

kind: local

players: 
  - players/hyperts_dl_player

random_states: [ 23163,5318,9527,33179 ]

constraints:  # configure the constraints
  task:  
    max_trials: 10  
    reward_metric: rmse  
```


### Multiple Runs with Defined Random States
TSBenchmark could set player to run the same task with multiple defined random states, which could help to reduce the randomness and evaluate the stability of algorithms. 
The random states and its number could be set by the argument `random_states` and `n_random_states`. See example below：
```yaml
name: 'benchmark_example_local'
desc: 'a local benchmark example'

kind: local

players: 
  - players/hyperts_dl_player

random_states: [ 23163,5318,9527,33179 ]  # the task runs 4 times with these 4 random states.

```

### Run Benchmark in Remote (Multi-machine) Mode

Running benchmark in remote/multi-machine mode could speed up the execution process.  
It requires TSBenchmark assign tasks to multiple notes by SSH protocol. First, set the argument `kind` as `remote` and then configure the argument `machines` with remote connection information. 
If the player requires virtual operating environment, the remote machine needs to install conda and specify the conda installation directory.

 ```yaml
name: 'benchmark_example_remote'
desc: 'a remote benchmark example'

kind: remote

players:
  - players/hyperts_dl_player

random_states: [ 23163,5318,9527,33179 ] 

machines:  # remote machine, SSH 
  - connection:  # remote machine information
        hostname: host1  
        username: hyperctl  
        password: hyperctl  
    environments:
      TSB_CONDA_HOME: /opt/miniconda3  # specify the conda installation directory
 ```


### Rerun Benchmark

When rerunning a benchmark, the previous executed tasks (either failed or successful) will be skipped.
The state files of both failed and successful tasks are shown below. To rerun executed tasks, user could delete the corresponding state files.
- State file of successful task：`{working_dir}/batches/{benchmark_name}/{job_name}.succeed`
- State file of failed state：`{working_dir}/batches/{benchmark_name}/{job_name}.failed`

The output data and state information of an executed benchmark will be written under the directory `working_dir`. 
If executing a benchmark that is continuous of another, make sure the configurations of `working_dir` and `name` of the two benchmarks are consistent：
```yaml
name: 'benchmark_example_local' # name of benchmark 
desc: 'a local benchmark example'

kind: local 

working_dir: ～/tsbenchmark_working_dir/benchmark_example_local  # the directory of Benchmark which store the output files; default(empty) dir `～/tsbenchmark_working_dir`

players: 
  - players/hyperts_dl_player

```
