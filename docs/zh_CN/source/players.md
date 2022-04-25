
Env config example :

```

env:
  kind: conda
  requirements: requirements_txt
  requirements_txt:
    python_version: 3.8
    file: requirements.txt

---
env:
  kind: conda
  requirements: conda_yaml
  conda_yaml:
    file: requirements.txt

---

env:
  kind: custom_python
  requirements: conda_yaml
  conda_yaml:
    file: requirements.txt
```