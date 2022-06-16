import os
from pathlib import Path

from tsbenchmark import consts
from tsbenchmark.benchmark import LocalBenchmark, RemoteSSHBenchmark
from tsbenchmark.callbacks import ReporterCallback
from tsbenchmark.cfg import load_benchmark, CopyCfgCallback
import tempfile

from tsbenchmark.tests.test_benchmark import BaseBenchmarkTest, assert_local_bm_batch_succeed

PWD = Path(__file__).parent


class TestLoadBenchmark:

    def assert_benchmark(self, benchmark):
        assert benchmark.desc == "hyperts V0.1.0 release benchmark on 20220321"
        assert len(benchmark.random_states) == 5
        batch_app_init_kwargs = benchmark.batch_app_init_kwargs

        assert batch_app_init_kwargs['scheduler_interval'] == 1
        assert batch_app_init_kwargs['scheduler_exit_on_finish'] == True

        assert batch_app_init_kwargs['server_port'] == 8060
        assert batch_app_init_kwargs['server_host'] == "localhost"
        assert benchmark.task_constraints == {"max_trials": 10, "reward_metric": "rmse"}

        assert Path(benchmark.data_dir).name == benchmark.name

        assert set([p.name for p in benchmark.players]) == {'hyperts_dl_player', 'plain_player_requirements_txt'}
        assert len(benchmark.ts_tasks_config) > 0

        assert isinstance(benchmark.callbacks[0], CopyCfgCallback)

    def test_load_local(self):
        local_benchmark_example = PWD / "benchmark_example_local.yaml"
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-working-dir")
        benchmark = load_benchmark(local_benchmark_example.as_posix(), benchmarks_data_dir=batches_data_dir)
        assert benchmark.name == "benchmark_example_local"
        assert isinstance(benchmark, LocalBenchmark)
        self.assert_benchmark(benchmark)
        assert benchmark.conda_home == "~/miniconda3/"

        # assets tasks
        for task_config in benchmark.ts_tasks_config:
            assert task_config.task == 'univariate-forecast'
            assert task_config.data_size == 'small'

        report_callback: ReporterCallback = benchmark.callbacks[1]
        assert isinstance(report_callback, ReporterCallback)
        assert report_callback.reporter.benchmark_config['report.path'] == "/tmp/benchmark-output/hyperts"

    def test_default_report(self):
        local_benchmark_example = PWD / "benchmark_example_report.yaml"
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-working-dir")
        benchmark = load_benchmark(local_benchmark_example.as_posix(), benchmarks_data_dir=batches_data_dir)
        assert benchmark.name == "benchmark_example_local"
        assert isinstance(benchmark, LocalBenchmark)
        self.assert_benchmark(benchmark)
        assert benchmark.conda_home == "~/miniconda3/"

        assert benchmark.name == "benchmark_example_local"

        # assert report.enable is True
        report_callback: ReporterCallback = benchmark.callbacks[1]
        assert isinstance(report_callback, ReporterCallback)
        assert report_callback.reporter.benchmark_config['report.path'] == os.path.join(batches_data_dir, benchmark.name, "report")

    def test_load_remote(self):
        local_benchmark_example = PWD / "benchmark_example_remote.yaml"
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-working-dir")
        benchmark = load_benchmark(local_benchmark_example.as_posix(), benchmarks_data_dir=batches_data_dir)
        assert benchmark.name == "benchmark_example_remote"
        assert isinstance(benchmark, RemoteSSHBenchmark)
        assert len(benchmark.machines) > 0
        self.assert_benchmark(benchmark)


class TestCopyCfgCallback(BaseBenchmarkTest):

    @classmethod
    def setup_class(cls):
        super(TestCopyCfgCallback, cls).setup_class()
        local_benchmark_example = PWD / "benchmark_local_no_report.yaml"
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-working-dir")
        cls.benchmark = load_benchmark(local_benchmark_example.as_posix(), benchmarks_data_dir=batches_data_dir)

    def test_run_local(self):
        benchmark = self.benchmark
        assert benchmark.name == "benchmark_example_local_no_report"
        assert isinstance(benchmark, LocalBenchmark)
        benchmark.run()

        # assert copied file exists
        assert (Path(benchmark.data_dir) / "benchmark_local_no_report.yaml").exists()

        # assert random states file exits and content is right
        random_states_path = Path(benchmark.data_dir) / "random_states"
        assert random_states_path.exists()
        from hypernets.hyperctl.utils import load_json
        assert set(load_json(random_states_path)) == set(benchmark.random_states)

        # assert max_trials and random_state is in benchmark tasks
        bm_tasks = benchmark.tasks()
        assert set([bt.ts_task.random_state for bt in bm_tasks]) == {23163, 23164}
        assert set([bt.ts_task.max_trials for bt in bm_tasks]) == {10}


class TestUseDatasetsCachePath(BaseBenchmarkTest):

    @classmethod
    def setup_class(cls):
        super(TestUseDatasetsCachePath, cls).setup_class()
        template_benchmark_file = PWD / "benchmark_cache_path.yaml"
        cache_data_dir = tempfile.mkdtemp(prefix="benchmark-cache-dir")
        cls.cache_data_dir = cache_data_dir

        print("generate cache_data_dir: ")
        print(cache_data_dir)

        benchmark_file_fd, benchmark_file = tempfile.mkstemp(prefix="benchmark_cache_path", suffix=".yaml")
        os.close(benchmark_file_fd)

        with open(template_benchmark_file, 'r') as f:
            content = f.read().replace("#cache_path#", cache_data_dir)

        with open(benchmark_file, 'w') as f:
            f.write(content)

        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-working-dir")

        cls.benchmark = load_benchmark(benchmark_file, benchmarks_data_dir=batches_data_dir)

    def test_run_benchmark(self):
        benchmark = self.benchmark

        assert benchmark.name == "benchmark_cache_path"
        assert isinstance(benchmark, LocalBenchmark)
        benchmark.run()

        ts_task = benchmark.tasks()[0].ts_task
        assert os.getenv(consts.ENV_DATASETS_CACHE_PATH) == self.cache_data_dir
        assert ts_task.taskdata.taskdata_loader.data_path == self.cache_data_dir

        # job succeed
        assert_local_bm_batch_succeed(self.benchmark)
