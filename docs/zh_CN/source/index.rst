欢迎使用 TSBenchmark
=====================

TSBenchmark: 一个面向时间序列预测自动机器学习算法的分布式Benchmark框架
#######################################################################

TSBenchmark 同时支持Time Series特性与AutoML特性。时间序列预测算法，支持单变量预测与多变量预测，同时支持协变量benchmark。
运行过程中，支持最优参数组合采集，为AutoML框架的分析提供支撑。

框架支持分布式运行模式，具备高效的跑评分效率。框架集成了Hypernets的内的轻量级分布式调度框架,python或者conda环境下均可运行。
推荐使用conda作为环境管理，以支持不同时序算法的环境隔离。


内容:
------

..  toctree::
    :maxdepth: 2

    基本概念<concepts.md>
    快速开始<quickstart.md>
    配置文件<config_file_references.rst>
    API 参考<api_docs/modules.rst>
    Release Notes<release_note.rst>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


DataCanvas
-----------
TSBenchmark is an open source project created by `DataCanvas <https://www.datacanvas.com>`_ .
