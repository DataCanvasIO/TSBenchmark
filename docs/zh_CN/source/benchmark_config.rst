===========================
Benchmark配置文件参考
===========================

tsbenchmark 提供了命令行工具 ``tsb`` 命令管理Benchmark。 可以使用yaml格式的配置文件定义benchmark，并使用tsb命令运行：

.. code-block:: shell

    $ tsb run --config <benchmark_config_file>


配置样例
===========


LocalBenchmark
---------------

.. code-block:: yaml

    name: 'benchmark_example_local'
    desc: 'a local benchmark example'

    kind: local  # 单机模式

    players:
      - players/hyperts_dl_player

    datasets:
      task_ids:
        - 512754

    random_states: [ 23163, 5318, 9527 ]

    venv:
      conda:
        home: /opt/miniconda3  # 配置本机conda安装位置


RemoteSSHBenchmark
-------------------

.. code-block:: yaml

    name: 'benchmark_example_local'
    desc: 'a remote benchmark example'

    kind: remote  # 远程并行模式

    players:
      - players/hyperts_dl_player

    datasets:
      task_ids:
        - 512754

    random_states: [ 23163, 5318, 9527 ]

    machines:
      - connection: # 配置远程SSH机器连接方式
            hostname: host1
            username: hyperctl
            password: hyperctl
        environments: # 配置远程SSH机器conda安装位置
          TSB_CONDA_HOME: /opt/miniconda3


配置项参考
==========

BaseBenchmarkConfig
--------------------

Benchmark有两个实现：

- LocalBenchmark: 单机模式运行的Benchmark，专用配置见 `LocalBenchmarkConfig`_
- RemoteSSHBenchmark: 基于SSH协议并行运行的Benchmark, 专用配置见 `RemoteSSHBenchmarkConfig`_

这部分配置是这两个实现的通用的。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - name
      - ``str``, required
      - benchmark的名称，支持使用数字、大小写字母、下划线、中划线。

    * - desc
      - ``str``, optional
      - Benchmark描述。

    * - kind
      - ``str``, required
      - Benchmark的类型，可选 ``local`` 和 ``remote`` ，分别对应 ``LocalBenchmark`` 和 ``LocalBenchmark`` 的Benchmar实现。

    * - benchmarks_working_dir
      - ``str``, optional
      - 用于存放Benchmark运行产生的文件; 默认为 ``～/tsbenchmark_working_dir``，

        将会以Benchmark的name为名称为每个Benchmark在此目录下创建子目录。

    * - players
      - ``list[str]``,  required
      - Benchmark使用到的Player的本地目录地址。如果是 ``RemoteSSHBenchmark`` 这些目录将会被上传到远程机器使用。

    * - constraints
      - `ConstraintsConfig`_,  required
      - 运行Benchmark的约束条件。

    * - tasks
      - `TaskFilterConfig`_,  optional
      - 设置参与Benchmark的任务。

    * - random_states
      - ``list[int]``,  optional
      - Benchmark任务使用的随机数，默认为 ``[9527]`` 。

        Benchmark运行时会让Player使用不同的随机数运行同一个任务，这样可以降低实验的随机性。


.. Note::

    当一个Benchmark重复运行时，之前运行结束（失败或者成功状态）的任务会被跳过不再运行。
    如需重新运行Benchmark中已经结束的任务，可以删除该任务的状态文件,任务的状态文件在：

    - 任务成功的状态文件：``{benchmarks_working_dir}/{benchmark_name}/batch/{job_name}.succeed``
    - 任务失败的状态文件：``{benchmarks_working_dir}/{benchmark_name}/batch/{job_name}.failed``

    若要实现一次Benchmark基于上一次Benchmark运行时跳过已经结束的任务， 需要确保这两次运行的Benchmark的 ``benchmarks_working_dir`` 和 ``name`` 属性一致。


TaskFilterConfig
--------------------

使用所有的任务运行Benchmark将消耗很多资源和时间，因此可以使用过滤条件指定哪些任务用来运行Benchmark。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - task_types
      - ``list[str]``, optional
      - 按任务类型筛选，默认为使用所有类型的任务。可选的值有 ``univariate-forecast``, ``multivariate-forecast``。

    * - datasets_sizes
      - ``list[str]``, optional
      - 按数据集的大小筛选, 默认选择所有大小类型的数据集文件; 可选 ``small``, ``large``。

    * - task_ids
      - ``list[int]``, optional
      - 指定任务的id。

    * - dataset_ids
      - ``list[int]``, optional
      - 指定数据集的id。

.. Note::

   过滤条件可以指定一个或者多个, 多个筛选条件之间的是"与"的关系，如果没有设置筛选条件将使用所有任务。


ConstraintsConfig
--------------------

运行Benchmark可以设定一些约束条件。比如设置Player中的算法搜索的次数、评价指标等。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - task
      - `TaskConstraintsConfig`_
      - 对任务的约束条件。


TaskConstraintsConfig
----------------------

任务的约束参数在Player中可以接受到，player中的算法需要使用这些参数运行任务。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - max_trials
      - ``int``, optional
      - 最大搜索次数，默认是10。

    * - reward_metric
      - ``str``, optional
      - 设置调参的评价指标，默认是 ``rmse``。


LocalBenchmarkConfig
--------------------

单机模式运行的Benchmark特有的配置，这种模式下训练任务都将在当前机器上进行，配置样例见 `LocalBenchmark`_ 。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - venv
      - `LocalVenvConfig`_
      - 配置当前机器上的虚拟环境管理器信息。


LocalVenvConfig
--------------------

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - conda
      - `LocalCondaConfig`_
      - 配置Conda虚拟环境管理器的信息。


LocalCondaConfig
--------------------

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - home
      - ``str``, optional
      - conda的安装目录, 如果在Benchmark中用到的player有使用conda虚拟环境的，需要配置conda的安装目录。

        Benchmark在运行的时候可以使用这个conda创建虚拟环境。


RemoteSSHBenchmarkConfig
------------------------

基于SSH协议并行运行的Benchmark特有的配置，这种模式以利用多台机器加快Benchmark的运行进度。它将任务通过SSH协议分发的远程节点，这要求远程运行任务的节点需要运行SSH服务，并且提供连接帐号。
如果运行的player中有使用到conda创建虚拟环境的，还需要在远程机器中安装好conda。配置样例见 `RemoteSSHBenchmark`_ 。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - machines
      - list[`RemoteMachineConfig`_ ], required
      - 远程机器的的链接信息和配置信息,  Benchmark会将训练任务分发到这些节点上。


RemoteMachineConfig
--------------------

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - connection
      - `SHHConnectionConfig`_, required
      - 远程机器的的链接信息。

    * - environments
      - ``dict``, optional
      - 远程机器的环境信息。如果运行的Player有使用conda虚拟环境的，需要通过键 ``TSB_CONDA_HOME`` 配置conda的安装目录，例如：

        .. code-block:: yaml

            machines:
              - connection:
                    hostname: host1
                    username: hyperctl
                    password: hyperctl
                environments:
                  TSB_CONDA_HOME: /opt/miniconda3  # 配置conda的安装目录


SHHConnectionConfig
--------------------

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - hostname
      - ``hostname``, required
      - 远程机器的ip地址或者主机名。

    * - username
      - ``username``, required
      - 远程机器的用户名。

    * - password
      - ``password``, required
      - 远程机器的连接密码。

