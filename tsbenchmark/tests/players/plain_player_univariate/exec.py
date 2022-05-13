import tsbenchmark as tsb
import tsbenchmark.api


def main():
  task = tsb.api.get_task()
  print(task)
  report_data = {'reward': 0.7}
  tsb.api.report_task(report_data=report_data)


if __name__ == "__main__":
    main()
