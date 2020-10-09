# adsapi
An exercise in creating an API for ads

# Swagger Editor
View the `openapi.yaml` in [Swagger Editor](https://editor.swagger.io/?url=https://macken.dafnet.se/david/openapi.yaml#)

# Usage
Tested on Lubuntu 18.04

```
git clone https://github.com/dafvid/adsapi.git
cd adsapi
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install wheel
.venv/bin/python setup.py install (maybe you need to do this twice)
.venv/bin/python run.py (edit run.py to change port)
```
