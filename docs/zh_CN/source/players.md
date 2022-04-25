
Env config example :

```
env:
  kind: custom_python
  custom_python:
    executable: python
```


```
env:
  kind: requirements_txt
    requirements_txt:
        file: requirements.txt
        python_version: 3.8
```


```
env:
  kind: conda_yaml
  conda_yaml:
    file: env.yaml
```