class TSBenchmarkMGR:

    def __init__(self, server_host="localhost",
                 server_port=8060,
                 scheduler_exit_on_finish=False,
                 scheduler_interval=5000,
                 backend_type='local',
                 backend_conf=None,
                 version=None,
                 **kwargs):
        pass



    def get_benchmark(kind):
        players = load_players(['plain_player'])
        #
        lb = LocalBenchmark(name='name', desc='desc',
                            players=players, tasks=[], constraints={}, backend_type="", backend_conf="")

        return lb
