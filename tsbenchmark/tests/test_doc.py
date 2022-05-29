from tsbenchmark import api
from tsbenchmark import tasks
from sklearn.linear_model import LinearRegression as LR

def test_doc_api():
    print(help(api))

def test_doc_task():
    print(help(tasks))