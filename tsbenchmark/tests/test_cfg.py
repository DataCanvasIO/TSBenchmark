import asyncio
from pathlib import Path

from tsbenchmark.benchmark import LocalBenchmark, RemoteSSHBenchmark
from tsbenchmark.cfg import load_benchmark, CopyCfgCallback

PWD = Path(__file__).parent


class TestLoadBenchmark:

    def assert_benchmark(self, benchmark):
        assert benchmark.desc == "hyperts V0.1.0 release benchmark on 20220321"
        assert len(benchmark.random_states) == 5
        assert benchmark.conda_home == "~/miniconda3/"
        batch_app_init_kwargs = benchmark.batch_app_init_kwargs

        assert batch_app_init_kwargs['scheduler_interval'] == 1
        assert batch_app_init_kwargs['scheduler_exit_on_finish'] == True

        assert batch_app_init_kwargs['server_port'] == 8060
        assert batch_app_init_kwargs['server_host'] == "localhost"
        assert benchmark.task_constraints == {"max_trials": 10, "reward_metric": "rmse"}
        assert benchmark.working_dir == "/tmp/tsbenchmark-hyperctl"
        assert benchmark.conda_home == "~/miniconda3/"

        assert set([p.name for p in benchmark.players]) == {'hyperts_dl_player', 'plain_player_requirements_txt'}
        assert len(benchmark.ts_tasks_config) > 0

        assert isinstance(benchmark.callbacks[0], CopyCfgCallback)

    def test_load_local(self):
        local_benchmark_example = PWD / "benchmark_example_local.yaml"
        benchmark = load_benchmark(local_benchmark_example.as_posix())
        assert benchmark.name == "benchmark_example_local"
        assert isinstance(benchmark, LocalBenchmark)
        self.assert_benchmark(benchmark)

    def test_load_remote(self):
        local_benchmark_example = PWD / "benchmark_example_remote.yaml"
        benchmark = load_benchmark(local_benchmark_example.as_posix())
        assert benchmark.name == "benchmark_example_remote"
        assert isinstance(benchmark, RemoteSSHBenchmark)
        assert len(benchmark.machines) > 0
        self.assert_benchmark(benchmark)


class TestCopyCfgCallback:

    @classmethod
    def setup_class(cls):
        pass

    def test_run_local(self):
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())

        local_benchmark_example = PWD / "benchmark_local_no_report.yaml"
        benchmark = load_benchmark(local_benchmark_example.as_posix())
        assert benchmark.name == "benchmark_example_local_no_report"
        assert isinstance(benchmark, LocalBenchmark)
        benchmark.run()

        # assert copied file exists
        assert (Path(benchmark.working_dir) / "benchmark_local_no_report.yaml").exists()

        # assert random states file exits and content is right
        random_states_path = Path(benchmark.working_dir) / "random_states"
        assert random_states_path.exists()
        from hypernets.hyperctl.utils import load_json
        assert set(load_json(random_states_path)) == set(benchmark.random_states)

        # assert max_trials and random_state is in benchmark tasks
        bm_tasks = benchmark.tasks()
        assert set([bt.ts_task.random_state for bt in bm_tasks]) == {23163, 23164}
        assert set([bt.ts_task.max_trials for bt in bm_tasks]) == {10}

    @classmethod
    def teardown_class(cls):
        asyncio.get_event_loop().stop()  # release res
        asyncio.get_event_loop().close()
