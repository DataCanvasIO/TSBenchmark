## 概念

**Dataset**  

`Dataset`是供`Player`跑benchmark时使用的数据和元数据, 通过`TsTask`对象的get_train和get_test方法可以获取。

初次运行时，框架自动从云端下载数据集。已下载成功的数据集会统一保存到缓存目录，后续运行时会使用缓存数据。数据缓存目录地址可以在
`benchmark.yaml`中指定。


**Task**  

`Task`是`Benchmark`的评测的一个原子任务。其主要供`Player`中使用，用户可以通过tsbenchmark.api的get_task和get_local_task获取。

`Task`包含几部分信息
- 数据，包括训练数据和测试数据
- 元数据，包括任务类型、数据形状、horizon、时间序列字段列表、协变量字段列表等
- 训练参数，包括random_state、reward_metric、max_trials等`Benchmark`参数


**Benchmark**  

`Benchmark`通过使一组`Player`分别运行一组相同的`Task`，并将运行的结果汇总成一个`Report`。 
在Report中包含这些`Player`运行任务消耗的时间、评估指标得分等信息。

目前有两个Benchmark的实现，分别是： 
- LocalBenchmark: 在本地运行的Benchmark
- RemoteSSHBenchmark: 通过SSH协议将训练任务分发到远程机器运行的Benchmark，

**Player**  

Player用来运行Task。它会包含一个python运行环境和一个python脚本文件。在python脚本中，可以调用tsbenchmark
提供的api获取Task，训练模型，评估模型和上传运行数据。

**Environment** 

Player的python运行环境。可以是自定义python环境，也可以是由conda管理的虚拟python环境。可以使用`requirement.txt`或者conda导出的yaml文件定义虚拟环境。
如果是使用conda管理的虚拟环境，需要安装好[conda](https://docs.conda.io)，并在Benchmark的配置文件中设置conda的安装目录。 Benchmark运行时会使用conda创建虚拟python环境并用此环境运行player的`exec.py`。

**Report**  

`Report`是供`Benchmark`的最终成果，收集`Player`的反馈结果信息，并生成对比分析报告。
报告支持不同`Player`间的对比报告横向对比，也支持同`Player`跑不同的Benchmark之间的对比纵向对比。

报告包含预测结果归档和Performance对比，其中的Performance包含smape, mae, rmse和mape的常见评价指标.
