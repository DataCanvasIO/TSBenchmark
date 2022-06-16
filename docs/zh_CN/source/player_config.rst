===========================
Player配置文件参考
===========================

Player通常会包含一个yaml格式的描述文件 ``player.yaml`` 和一个python脚本 ``exec.py``，一个player的目录结构看起来像是：

.. code-block:: yaml

    .
    ├── exec.py
    └── player.yaml


- ``exec.py`` 脚本来借助tsbenchmark提供的api完成读取任务、训练任务、和评估指标，api用法参考 :doc:`/api_docs/modules` 。
- ``player.yaml`` 用来描述player的配置信息。


定义player例子请参考 :doc:`/quickstart`，在TSBenchmark中也已经将一些算法封装成Player，参考 `Player列表 <https://github.com/DataCanvasIO/TSBenchmark/tree/main/players>`_ 。


配置样例
=========

自定义python环境
-------------------

.. code-block:: yaml

    name: hyperts_player
    env:
      kind: custom_python  # 使用自定义python环境
      py_executable: /usr/bin/python


conda管理conda格式依赖文件
--------------------------

.. code-block:: yaml

    name: hyperts_player
    env:
      kind: conda  # 使用conda创建虚拟环境
      requirements:
        kind: conda_yaml # 使用conda 格式的依赖
        file_name: env.yaml


conda管理pip格式依赖文件
--------------------------------

.. code-block:: yaml

    name: hyperts_player
    env:
      kind: conda  # 使用conda创建虚拟环境
      requirements:
        kind: requirements_txt # 使用pip格式的依赖定义文件
        file_name: requirements.txt
        py_version: 3.8

    tasks:  # 仅支持单变量预测的任务
      - univariate-forecast

    random: true  #  使用随机数


配置项参考
==========

PlayerConfig
------------

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - name
      - ``str``, optional
      - player的名称，如果为空将使用player所在的文件夹名。

    * - env
      - `EnvConfig`_, required
      - 运行环境配置。

    * - tasks
      - ``list[str]``, optional
      - player支持的任务类型，默认为空，如果为空表示支持所有任务类型。

        Benchmark运行时只会给Player分配它能支持的类型的任务;

        可选的值有 ``univariate-forecast``, ``multivariate-forecast``。

    * - random
      - ``boolean``,  optional
      - player是否接受随机数，默认为 ``true``。

        如果接受随机数，Benchmark运行时会对每个任务使用不同的随机数跑多次减少随机因素带来的影响。

        如果不接受则仅运行任务一次。



EnvConfig
---------


是下列对象的一种：

- `CustomPythonEnvConfig`_
- `CondaEnvConfig`_


CustomPythonEnvConfig
---------------------

使用已经创建好的python环境运行player。这种情况下benchmark运行时候不会再为player创建虚拟环境，而是使用指定的python环境运行。


.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - kind
      - ``"custom_python"``
      -

    * - py_executable
      - ``str``, optional
      - python的可执行文件路径，默认为当前进程使用的python。


CondaEnvConfig
--------------

定义使用 `conda <https://docs.conda.io/en/latest/>`_ 管理的虚拟环境。Benchmark运行时候会使用已经配置好的conda创建虚拟环境并运行player。


.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - kind
      - ``"conda"``
      -

    * - name
      - ``str``, optional
      - conda虚拟环境的名称。
        如果为空, 当 ``env.requirements.kind=requirements_txt`` 时使用player的name;

        当 ``env.requirements.kind=conda_yaml`` 时使用conda环境的yaml文件中的名称。

    * - requirements
      - `RequirementsConfig`_
      - 定义虚拟环境的依赖包。

.. Note::

   如果运行时根据虚拟环境的名称检查到虚拟环境已经存在则会跳过环境创建并使用当前存在的环境运行player。


RequirementsConfig
------------------

是下列对象的一种：

- `RequirementsTxtConfig`_
- `CondaYamlConfig`_


RequirementsTxtConfig
---------------------

player可以使用 `pip的依赖文件格式 <https://pip.pypa.io/en/stable/reference/requirements-file-format/>`_ (requirement.txt)声明所需要的依赖库, 一个 ``requirement.txt`` 文件看起来像：

.. code-block:: text

    tsbenchmark
    numpy >=0.1

benchmark运行时候会使用conda创建虚拟环境并使用 `pip <https://pip.pypa.io/en/stable/>`_ 安装依赖。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - kind
      - ``"requirements_txt"``
      -
    * - py_version
      - ``str``, optional
      - 虚拟环境的python版本，如果为空将使用当前进程使用的python版本。

    * - file_name
      - ``str``, optional
      - pip依赖文件的名称，默认为 ``requirements.txt``, 此文件存放在player目录中。

        由于player运行时候需要使用tsbenchmark，请在该文件中添加tsbenchmark。


CondaYamlConfig
---------------

conda 可以将虚拟环境导出成yaml文件，参考 `Sharing an environment <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment>`_ 。导出的文件看起来像：

.. code-block:: yaml

    name: plain_player_conda_yaml
    channels:
      - defaults
    dependencies:
      - pip
      - pip:
          - tsbenchmark

导出的yaml文件可以用来定义player的虚拟python环境，Benchmark运行时候会使用此文件创建虚拟环境并用来运行Player。

.. list-table::
    :widths: 10 10 80
    :header-rows: 1

    * - Field Name
      - Type
      - Description

    * - kind
      - ``"conda_yaml"``
      -

    * - file_name
      - ``str``, optional
      - conda虚拟环境导出的yaml文件，默认为 ``env.yaml``, 此文件存放在player目录中。

        此文件中通常已经包含虚拟环境的名称，不必再通过 ``env.name`` 配置虚拟环境的名称；
