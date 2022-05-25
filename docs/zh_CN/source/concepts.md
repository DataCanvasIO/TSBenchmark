## 概念

**Dataset**
// TODO

**Task**
// TODO

**Benchmark**

`Benchmark`通过使一组`Player`分别运行一组相同的`Task`，并将运行的结果汇总成一个`Report`。
`Report`中这些`Player`在运行时间、评估指标得分等方面的差异。

TSBenchmark目前有两个Benchmark的实现： 
- LocalBenchmark: 在本地运行Benchmark
- RemoteSSHBenchmark: 通过SSH协议将训练任务在远程运行的Benchmark

**Player**

Player用来运行Task。它会包含一个python运行环境和一个python脚本文件。在python脚本中，可以调用tsbenchmark
提供的api获取Task，训练模型，评估模型和上传运行数据。

**Environment**

Player的运行环境。可以是自定义python环境，也可以是由conda管理的虚拟python环境。可以使用`requirement.txt`或者conda导出的yaml文件定义虚拟环境。


**Report**

// TODO


