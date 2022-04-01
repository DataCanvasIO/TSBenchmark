import tsbenchmark as tsb
import tsbenchmark.api


def main():
  task = tsb.api.get_task()
  dataset = task.dataset

  print(task)
  print(dataset)

  tsb.api.report_result()


if __name__ == "__main__":
    main()
