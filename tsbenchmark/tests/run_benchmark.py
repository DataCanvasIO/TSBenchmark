import tsbenchmark.tasks
from tsbenchmark.benchmark import LocalBenchmark
from tsbenchmark.tests.players import load_test_player


def main():

    player = load_test_player("plain_player")

    task_config = tsbenchmark.tasks.get_task_config(512754)

    lb = LocalBenchmark(name='local-benchmark-example', desc='a local benchmark', players=[player],
                        random_states=[8086], ts_tasks_config=[task_config])

    lb.run()


if __name__ == '__main__':
    main()
